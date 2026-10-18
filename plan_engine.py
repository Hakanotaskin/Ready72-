"""Ready72 plan motoru (Streamlit'ten bağımsız, test edilebilir).

Akış (kurstaki Draft → Validate → Finalize döngüsü):
  önbellek → (1) hane analizi [adım adım] → (2) plan taslağı → kod doğrulaması (kriter bazlı)
  → gerekirse 1 onarım çağrısı (finalize) → faz etiketi normalizasyonu. İnsan denetimi: kullanıcı resmî kaynaklarla doğrular.
"""
import copy
import hashlib
import json
from pathlib import Path

from prompts_tr import (
    PHASES, PROMPT_A_SYSTEM, PROMPT_VERSION, build_messages, build_user_prompt_baseline,
    normalize_phases, total_children, validate_analysis, validate_plan,
)

DEFAULT_MODEL = "google/gemini-2.5-flash"
DEFAULT_SEED = 42
DEFAULT_CACHE_DIR = Path(__file__).parent / ".plan_cache"


def make_client(api_key: str):
    from openai import OpenAI  
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)


def parse_json(content: str) -> dict:
    """Model cevabını güvenle JSON'a çevirir (```json bloklarını temizler)."""
    text = (content or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start: end + 1]
    return json.loads(text)


def _call(client, model, messages, temperature, seed, meta) -> str:
    kw = dict(model=model, messages=messages, temperature=temperature, top_p=1,
              response_format={"type": "json_object"})
    if seed is not None:
        kw["seed"] = seed
    meta["calls"] += 1
    try:
        # Sağlayıcı değişirse çıktı da değişir; fallback'i kapatmayı dene.
        r = client.chat.completions.create(**kw, extra_body={"provider": {"allow_fallbacks": False}})
    except Exception:
        r = client.chat.completions.create(**kw)
    return r.choices[0].message.content or ""


def _generate(client, model, messages, temperature, seed, validate, meta, repair=True):
    """JSON üret → doğrula → sorun varsa sorunları geri bildirerek BİR kez onar."""
    raw = _call(client, model, messages, temperature, seed, meta)
    try:
        obj = parse_json(raw)
        problems = validate(obj)
    except Exception as e:  # geçersiz JSON
        obj, problems = None, [f"Geçerli JSON değil: {e}"]
    if problems and repair:
        meta["repairs"] += 1
        fix = (
            "Önceki çıktında şu sorunlar var:\n- " + "\n- ".join(problems)
            + "\nYalnızca düzeltilmiş JSON'u ver; şemayı ve tüm kuralları koru."
        )
        raw2 = _call(client, model, messages + [
            {"role": "assistant", "content": raw}, {"role": "user", "content": fix}], temperature, seed, meta)
        try:
            obj2 = parse_json(raw2)
            p2 = validate(obj2)
            if obj is None or len(p2) <= len(problems):
                obj, problems = obj2, p2
        except Exception:
            pass
    return obj, problems


def _normalize_input(d: dict) -> dict:
    d = dict(d)
    d["children"] = total_children(d)
    return d


def _cache_key(d, model, temperature, seed, use_chain, fewshot) -> str:
    blob = json.dumps(
        {"d": d, "model": model, "t": temperature, "seed": seed, "chain": use_chain, "fs": fewshot, "v": PROMPT_VERSION},
        ensure_ascii=False, sort_keys=True,
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]


def generate_plan(user_data, api_key=None, model=DEFAULT_MODEL, temperature=0.2, seed=DEFAULT_SEED,
                  use_chain=True, use_cache=True, cache_dir=None, client=None, fewshot=True, repair=True) -> dict:
    """Dönen sözlük: plan, analysis, warnings (kalan doğrulama sorunları), meta."""
    d = _normalize_input(user_data)
    meta = {"calls": 0, "repairs": 0, "cached": False, "chain": use_chain, "fewshot": fewshot, "model": model,
            "temperature": temperature, "prompt_version": PROMPT_VERSION, "phase_labels_raw_ok": None}

    cdir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
    cfile = cdir / f"{_cache_key(d, model, temperature, seed, use_chain, fewshot)}.json"
    if use_cache and cfile.exists():
        try:
            hit = json.loads(cfile.read_text(encoding="utf-8"))
            hit["meta"] = {**hit.get("meta", {}), "cached": True}
            return hit
        except Exception:
            pass

    client = client or make_client(api_key)
    analysis, analysis_problems = None, []
    if use_chain:
        analysis, analysis_problems = _generate(
            client, model,
            build_messages("analysis", d), temperature, seed, lambda a: validate_analysis(a, d), meta, repair)
        if analysis_problems:  # analiz güvenilmezse zinciri bırak, tek çağrıya düş
            analysis = None

    plan, problems = _generate(
        client, model,
        build_messages("plan", d, analysis, fewshot), temperature, seed,
        lambda p: validate_plan(normalize_phases(copy.deepcopy(p)), d, check_copy=fewshot), meta, repair)
    if not isinstance(plan, dict):
        raise ValueError("Model geçerli bir plan üretemedi: " + "; ".join(problems))
    meta["phase_labels_raw_ok"] = [p.get("phase") for p in plan.get("first_72_hours", []) if isinstance(p, dict)] == PHASES
    normalize_phases(plan)

    warnings = list(problems)
    if use_chain and analysis is None:
        warnings.append("Analiz aşaması doğrulanamadı; plan tek çağrıyla üretildi.")
    result = {"plan": plan, "analysis": analysis, "warnings": warnings, "meta": meta}

    if use_cache and not problems:  # yalnızca temiz sonuçlar önbelleğe alınır
        try:
            cdir.mkdir(parents=True, exist_ok=True)
            cfile.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
    return result


def generate_baseline(user_data, api_key=None, model=DEFAULT_MODEL, temperature=0.2, seed=None, client=None) -> dict:
    """Prompt A (v1 baseline): tek çağrı, doğrulama/onarım yok. A/B/C deneyi için."""
    d = _normalize_input(user_data)
    meta = {"calls": 0, "repairs": 0, "cached": False, "chain": False, "fewshot": False, "model": model,
            "temperature": temperature, "prompt_version": "A-baseline"}
    client = client or make_client(api_key)
    raw = _call(client, model, [{"role": "system", "content": PROMPT_A_SYSTEM},
                                {"role": "user", "content": build_user_prompt_baseline(d)}],
                temperature, seed, meta)
    plan = parse_json(raw)
    meta["phase_labels_raw_ok"] = (
        [p.get("phase") for p in plan.get("first_72_hours", []) if isinstance(p, dict)] == PHASES
        if isinstance(plan, dict) else False)
    return {"plan": plan, "analysis": None, "warnings": [], "meta": meta}
