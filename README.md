# Ready72 – AI-Powered Personalized Earthquake Preparedness Assistant

> *Preparedness should not be one-size-fits-all.*

Ready72 turns basic household information into a **personalized 72-hour earthquake preparedness plan** using generative AI.
Built for the Samsung Innovation Campus **SDG Generative AI Hackathon** (16–18 October 2026).

- **SDG:** SDG 11 – Sustainable Cities and Communities, **Target 11.5** (reduce the impact of disasters on people). Also relevant to SDG 13 (climate/disaster resilience).
- **Target user:** households in Türkiye (non-expert family members) who want a plan that fits *their* home, not a generic checklist.
- **Generative AI:** Google Gemini 2.5 Flash via the OpenRouter API (default; model name is configurable).

## What it does

The user enters: city and district, building type, floor, number of adults / elderly (65+) / children (by age group), mobility needs, pets, and existing emergency supplies.

Ready72 generates:

1. a household preparedness summary
2. priority actions
3. role assignments (one per household member)
4. a personalized emergency kit ("item — household-specific reason")
5. a five-phase first-72-hours action plan

The result can be ticked off in the app (kit checklist) and downloaded as a `.txt` file.

## How it works

```
Household form → Stage 1: household analysis (JSON) → Stage 2: plan (JSON, few-shot)
              → rule-based validation → (max. 1 repair call per stage) → final plan
```

| Technique | Where it is used |
|---|---|
| System prompt vs. task prompt | `SYSTEM_PROMPT` (always-on rules) and `TASK_ANALYSIS` / `TASK_PLAN` in `prompts_tr.py` |
| Step-by-step reasoning (chain) | Two-stage chain: analysis → plan; numbered steps inside each task prompt |
| Few-shot | Plan stage only: 3 example households + "do not copy" rule + code-level copy check |
| Structured output | Fixed JSON schema, parsed and validated in code |
| Negative prompting | "DO / DON'T" rules grouped by form, content, behavior |
| Prompt-injection defense | Priority order System > Task > Data; user data wrapped in `<kullanici_verisi>` tags and treated as data only |
| Validate → repair | `validate_analysis` / `validate_plan`; one repair attempt per stage with the problems fed back to the model |
| Response cache | Same input + settings → same plan (for stable demos and testing) |

The prompts are written in **Turkish**, because the target users are in Türkiye. The report, slides and video are in English.

### What the validators check
Required keys and item counts; five distinct time phases (fixed labels set in code); every household member has a role; no invented role labels; no phone numbers (including 112); a list of risky phrases (e.g. "completely safe", "use the elevator"); gas-valve advice only in the 1–15 min phase; no pet mentions when the household has no pet; no verbatim copying from few-shot examples.
Validation checks structure and selected rules. **It does not guarantee that every recommendation is correct or safe**; remaining issues are kept as internal warnings.

## Safety and ethics

The model is instructed **not** to produce: official assembly areas, evacuation routes, emergency phone numbers, building-safety judgments, local risk claims, earthquake predictions, or guarantees of safety. For official information, users are pointed to AFAD, e-Devlet and their municipality. The app displays: *"Ready72 supports earthquake preparedness planning and does not replace official emergency instructions or authorities."*
Special care is taken for vulnerable members: children are handled by age group (0–2 carried, 3–5 stay with an adult, 6–12 get simple tasks, 13–17 help adults), elderly and mobility-limited members get an evacuation plan built around them, and medication advice is limited to "keep a written list and a spare supply, ask your doctor".

## Run it locally

Requirements: Python 3.10+ and an [OpenRouter](https://openrouter.ai) API key.

```bash
git clone https://github.com/Hakanotaskin/Ready72-.git
cd Ready72-
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                                  # then put the submitted API key (The API key for evaluation was submitted separately via the submission form) (not stored in this repository).”
streamlit run app.py
```

Open the local URL that Streamlit prints (usually http://localhost:8501). You can also paste the API key into the sidebar instead of using `.env`.
**Never commit your `.env` file or API key.**

### Quick try (sample household)
City: İzmir · District: Karşıyaka · Building: Betonarme · Floor: 4 · 2 adults, 1 child (6–12), 1 elderly · Mobility: Yürüme Zorluğu · Pet: Kedi · Existing supplies: "su, el feneri" → click **"Bana Özel Planı Oluştur"**.

Sidebar switches let you turn the chain, the few-shot examples and the cache on/off to compare prompt variants (baseline single call vs. chain vs. chain + few-shot).

## Repository contents

| File | Purpose |
|---|---|
| `app.py` | Streamlit interface (form, result tabs, kit checklist, TXT export) |
| `plan_engine.py` | Generation flow: cache → analysis → plan → validation → repair |
| `prompts_tr.py` | All prompts (system, tasks, few-shot examples, baseline prompt) and validators |
| `Ready72_report.pdf` | 2-page project report |
| `.env.example` | Template for the API key |

## Limitations and future work

Ready72 does not yet retrieve verified local hazard data, official assembly areas, evacuation routes or real-time alerts. Future versions could integrate AFAD and municipality data, maps and accessibility-aware routing, and emergency drill simulations.

