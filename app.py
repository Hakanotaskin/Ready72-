import os
import json
import html
import streamlit as st
from dotenv import load_dotenv

from plan_engine import generate_plan, DEFAULT_MODEL
from prompts_tr import CHILD_GROUPS  # YENİ EKLEDİM: çocuk yaş gruplarını prompta aktarmak için

load_dotenv()

# ==========================================
# SAYFA AYARLARI
# ==========================================
st.set_page_config(
    page_title="Ready72 - Kişisel Afet Rehberiniz",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# TASARIM (CSS)
# ==========================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #F4F7FB;
    --card: #FFFFFF;
    --ink: #1E293B;
    --muted: #64748B;
    --line: #E2E8F0;
    --primary: #0F9D8A;
    --primary-dark: #0B7A6B;
    --primary-soft: #E6F6F3;
    --accent: #F59E0B;
    --accent-soft: #FFF6E0;
    --danger-soft: #FEECEC;
    --blue-soft: #E8F1FE;
}

html, body, .stApp, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stApp { background: var(--bg) !important; color: var(--ink); }
header[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 1.5rem !important; max-width: 1150px; }

/* ---- Okunabilirlik: koyu temada bile yazılar görünsün ---- */
.stApp p, .stApp label, .stApp span, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    color: var(--ink);
}
div[data-testid="stWidgetLabel"] p {
    color: var(--ink) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}
:root, .stApp, section[data-testid="stSidebar"] { color-scheme: light !important; }

/* Tüm girdi katmanlarını açık renge zorla */
div[data-baseweb="select"] > div,
div[data-baseweb="input"],
div[data-baseweb="base-input"],
div[data-baseweb="textarea"],
div[data-testid="stNumberInput"] div[data-baseweb="input"],
div[data-testid="stNumberInput"] div[data-baseweb="base-input"],
div[data-testid="stTextInputRootElement"],
div[data-testid="stTextInputRootElement"] > div,
div[data-testid="stTextArea"] textarea {
    background-color: #F1F5F9 !important;
    border-radius: 12px !important;
    border-color: var(--line) !important;
}
input, textarea {
    background-color: transparent !important;
}
div[data-testid="stTextArea"] textarea { background-color: #F1F5F9 !important; }

/* Sayı kutusu +/- butonları */
button[data-testid="stNumberInputStepDown"],
button[data-testid="stNumberInputStepUp"] {
    background-color: #E2E8F0 !important;
    color: var(--ink) !important;
}
button[data-testid="stNumberInputStepDown"] svg,
button[data-testid="stNumberInputStepUp"] svg,
div[data-baseweb="select"] svg,
div[data-testid="stTextInputRootElement"] svg {
    fill: var(--ink) !important;
    color: var(--ink) !important;
}

/* Açılır liste (dropdown) menüsü */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
ul[data-testid="stSelectboxVirtualDropdown"],
div[data-baseweb="menu"],
div[data-baseweb="menu"] ul {
    background-color: #FFFFFF !important;
}
div[data-baseweb="popover"] li, div[data-baseweb="menu"] li,
div[data-baseweb="popover"] li * {
    background-color: #FFFFFF !important;
    color: var(--ink) !important;
}
div[data-baseweb="popover"] li:hover, div[data-baseweb="menu"] li:hover,
div[data-baseweb="popover"] li[aria-selected="true"] {
    background-color: var(--primary-soft) !important;
}

/* Seçim ve sayı kutularının TÜM iç katmanlarını aynı açık renge boya */
/* 1) Önce kutunun içindeki her şeyi şeffaf yap (etiketlere dokunma) */
div[data-baseweb="select"] > div *,
div[data-baseweb="input"] *,
div[data-baseweb="base-input"],
div[data-baseweb="textarea"] * {
    background-color: transparent !important;
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
}
/* 2) Sadece dış kutu aynı açık renkte olsun */
div[data-baseweb="select"] > div,
div[data-baseweb="input"],
div[data-baseweb="textarea"] {
    background-color: #F1F5F9 !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    overflow: hidden;
}
/* 3) Sayı kutusu +/- butonları kutuyla aynı renk, araya ince çizgi */
div[data-baseweb="input"] button,
button[data-testid="stNumberInputStepDown"],
button[data-testid="stNumberInputStepUp"] {
    background-color: transparent !important;
    border-left: 1px solid var(--line) !important;
}
div[data-baseweb="input"] button:hover { background-color: #E2E8F0 !important; }
/* 4) "Press Enter to submit form" ipucunu gizle */
div[data-testid="InputInstructions"],
div[data-testid="stForm"] [data-testid="InputInstructions"] {
    display: none !important;
}
/* 5) Etiketlerin arkasında renk kalmasın */
div[data-testid="stWidgetLabel"],
div[data-testid="stWidgetLabel"] * {
    background: transparent !important;
}
/* Seçili değer yazısı */
div[data-baseweb="select"] span,
div[data-baseweb="select"] input,
div[data-baseweb="select"] [value],
div[data-baseweb="select"] div[aria-live] {
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
}
div[data-baseweb="select"] *, input, textarea {
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
}
input::placeholder, textarea::placeholder {
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
}
div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="textarea"]:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(15,157,138,.15) !important;
}

/* ---- Yan panel ---- */
section[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid var(--line); }

/* ---- Hero ---- */
.hero {
    position: relative; overflow: hidden;
    background: linear-gradient(135deg, #0F9D8A 0%, #1B7FBF 100%);
    border-radius: 28px; padding: 40px 44px; margin-bottom: 18px;
    box-shadow: 0 18px 40px rgba(15,157,138,.25);
}
.hero::after {
    content: ""; position: absolute; right: -60px; top: -60px;
    width: 260px; height: 260px; border-radius: 50%;
    background: rgba(255,255,255,.10);
}
.hero::before {
    content: ""; position: absolute; right: 120px; bottom: -90px;
    width: 200px; height: 200px; border-radius: 50%;
    background: rgba(255,255,255,.08);
}
.hero .badge {
    display: inline-block; background: rgba(255,255,255,.18);
    color: #fff !important; padding: 6px 14px; border-radius: 999px;
    font-size: .8rem; font-weight: 600; margin-bottom: 14px;
}
.hero h1 {
    color: #fff !important; font-size: 2.3rem; font-weight: 800;
    margin: 0 0 10px 0; line-height: 1.2; position: relative; z-index: 1;
}
.hero p {
    color: rgba(255,255,255,.92) !important; font-size: 1.05rem;
    max-width: 640px; margin: 0; position: relative; z-index: 1;
}
.hero-steps { display: flex; gap: 12px; margin-top: 22px; flex-wrap: wrap; position: relative; z-index: 1; }
.hero-step {
    background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.25);
    color: #fff !important; padding: 8px 16px; border-radius: 14px;
    font-size: .85rem; font-weight: 600;
}

/* ---- Uyarı ---- */
.notice {
    display: flex; gap: 12px; align-items: flex-start;
    background: var(--accent-soft); border: 1px solid #FCE2A6;
    border-radius: 16px; padding: 14px 18px; margin-bottom: 22px;
    color: #7A5200 !important; font-size: .9rem;
}
.notice * { color: #7A5200 !important; }

/* ---- Form bölümleri ---- */
div[data-testid="stForm"] {
    background: var(--card); border: 1px solid var(--line);
    border-radius: 24px; padding: 28px 30px !important;
    box-shadow: 0 8px 30px rgba(30,41,59,.05);
}
.sec { display: flex; align-items: center; gap: 14px; margin: 6px 0 16px 0; }
.sec-num {
    width: 38px; height: 38px; border-radius: 12px; flex-shrink: 0;
    background: var(--primary-soft); color: var(--primary-dark) !important;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 1.05rem;
}
.sec-title { font-weight: 700; font-size: 1.15rem; color: var(--ink); }
.sec-sub { font-size: .85rem; color: var(--muted) !important; }
.divider { height: 1px; background: var(--line); margin: 22px 0; }

/* ---- Butonlar ---- */
div.stButton > button, div[data-testid="stFormSubmitButton"] > button, div.stDownloadButton > button {
    background: linear-gradient(135deg, #0F9D8A 0%, #0B7A6B 100%) !important;
    color: #fff !important; border: none !important; border-radius: 14px !important;
    padding: 14px 20px !important; font-weight: 700 !important; font-size: 1.05rem !important;
    box-shadow: 0 8px 20px rgba(15,157,138,.3);
    transition: transform .15s ease, box-shadow .15s ease;
}
div.stButton > button p, div[data-testid="stFormSubmitButton"] > button p, div.stDownloadButton > button p {
    color: #fff !important; font-weight: 700 !important;
}
div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover, div.stDownloadButton > button:hover {
    transform: translateY(-2px); box-shadow: 0 12px 26px rgba(15,157,138,.38);
}

/* ---- İstatistik kartları ---- */
.stat {
    background: var(--card); border: 1px solid var(--line); border-radius: 20px;
    padding: 18px 20px; box-shadow: 0 6px 18px rgba(30,41,59,.04); text-align: center;
}
.stat-ico { font-size: 1.6rem; }
.stat-val { font-size: 1.7rem; font-weight: 800; color: var(--primary-dark) !important; line-height: 1.2; }
.stat-lbl { font-size: .82rem; color: var(--muted) !important; font-weight: 500; }

/* ---- Sekmeler ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px; background: #fff; padding: 8px; border-radius: 18px;
    border: 1px solid var(--line); flex-wrap: wrap;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px; padding: 10px 18px; background: transparent;
    font-weight: 600; height: auto;
}
.stTabs [data-baseweb="tab"] p { color: var(--muted) !important; font-weight: 600; }
.stTabs [aria-selected="true"] { background: var(--primary-soft) !important; }
.stTabs [aria-selected="true"] p { color: var(--primary-dark) !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* ---- İçerik kartları ---- */
.summary-card {
    background: linear-gradient(135deg, #E8F1FE 0%, #E6F6F3 100%);
    border: 1px solid #CFE4F7; border-radius: 22px; padding: 26px 28px;
    line-height: 1.75; font-size: 1rem; color: var(--ink) !important; margin-top: 14px;
}
.action-card {
    display: flex; gap: 16px; align-items: flex-start;
    background: var(--card); border: 1px solid var(--line);
    border-left: 5px solid var(--accent);
    border-radius: 18px; padding: 18px 20px; margin-top: 12px;
    box-shadow: 0 4px 14px rgba(30,41,59,.04);
}
.action-num {
    width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
    background: var(--accent); color: #fff !important; font-weight: 800;
    display: flex; align-items: center; justify-content: center;
}
.action-text { font-weight: 600; line-height: 1.6; color: var(--ink) !important; }

.role-card {
    background: var(--card); border: 1px solid var(--line); border-radius: 20px;
    padding: 20px; margin-top: 12px; height: 100%;
    box-shadow: 0 4px 14px rgba(30,41,59,.04);
}
.role-top { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.role-avatar {
    width: 40px; height: 40px; border-radius: 12px; background: var(--blue-soft);
    display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
}
.role-title { font-weight: 700; color: var(--ink) !important; font-size: 1rem; }
.role-person {
    display: inline-block; background: var(--primary-soft); color: var(--primary-dark) !important;
    padding: 3px 12px; border-radius: 999px; font-size: .78rem; font-weight: 700;
}
.role-task { color: var(--muted) !important; font-size: .92rem; line-height: 1.6; }

.timeline { position: relative; margin-top: 16px; padding-left: 8px; }
.tl-item { display: flex; gap: 18px; position: relative; padding-bottom: 18px; }
.tl-item:not(:last-child)::before {
    content: ""; position: absolute; left: 15px; top: 34px; bottom: 0;
    width: 2px; background: #CBD5E1;
}
.tl-dot {
    width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0; z-index: 1;
    background: var(--primary); color: #fff !important; font-weight: 800; font-size: .85rem;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 0 5px var(--primary-soft);
}
.tl-body {
    background: var(--card); border: 1px solid var(--line); border-radius: 18px;
    padding: 16px 20px; flex: 1; box-shadow: 0 4px 14px rgba(30,41,59,.04);
}
.tl-phase { font-weight: 700; color: var(--primary-dark) !important; margin-bottom: 6px; }
.tl-action { color: var(--ink) !important; line-height: 1.65; font-size: .95rem; }

.sos {
    background: var(--danger-soft); border: 1px solid #F8CACA; color: #9B1C1C !important;
    border-radius: 16px; padding: 14px 18px; font-size: .92rem; margin-top: 22px;
}
.sos * { color: #9B1C1C !important; }

.footer { text-align: center; color: var(--muted) !important; font-size: .82rem; margin: 34px 0 10px 0; }

/* Streamlit checkbox */
div[data-testid="stCheckbox"] label p { color: var(--ink) !important; }
div[data-testid="stProgress"] > div > div > div > div { background-color: var(--primary) !important; }
</style>
""",
    unsafe_allow_html=True,
)

ILLER = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya",
    "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik",
    "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum",
    "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir",
    "Gaziantep", "Giresun", "Gümüşhane", "Hakkâri", "Hatay", "Iğdır", "Isparta", "İstanbul",
    "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kilis",
    "Kırıkkale", "Kırklareli", "Kırşehir", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa",
    "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize",
    "Sakarya", "Samsun", "Şanlıurfa", "Siirt", "Sinop", "Sivas", "Şırnak", "Tekirdağ",
    "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak",
]


# ==========================================
# YARDIMCI FONKSİYONLAR
# ==========================================
def esc(x) -> str:
    return html.escape(as_text(x))


def as_text(x) -> str:
    """AI bazen string yerine dict/list döndürebilir; hepsini düz metne çevir."""
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        return " – ".join(as_text(v) for v in x.values())
    if isinstance(x, (list, tuple)):
        return ", ".join(as_text(v) for v in x)
    return str(x)


def flatten_bag(items) -> list:
    """Çanta listesini düz bir string listesine çevirir."""
    out = []
    if isinstance(items, dict):
        for k, v in items.items():
            if isinstance(v, list):
                out.extend(f"{as_text(i)}" for i in v)
            else:
                out.append(f"{k}: {as_text(v)}")
    elif isinstance(items, list):
        for i in items:
            if isinstance(i, dict) and any(isinstance(v, list) for v in i.values()):
                for v in i.values():
                    if isinstance(v, list):
                        out.extend(as_text(x) for x in v)
            else:
                out.append(as_text(i))
    elif items:
        out.append(as_text(items))
    return [o for o in out if o.strip()]


def plan_to_text(plan: dict, data: dict) -> str:
    lines = ["READY72 – KİŞİSEL 72 SAATLİK AFET PLANI", "=" * 44, ""]
    lines.append(f"Konum: {data['district']}, {data['city']}")
    lines.append(f"Bina: {data['building_type']} | Kat: {data['floor_number']}")
    groups = ", ".join(f"{k} yaş: {n}" for k, n in (data.get("child_groups") or {}).items() if n)
    lines.append(
        f"Hane: {data['adults']} yetişkin, {data['children']} çocuk"
        + (f" ({groups})" if groups else "")
        + f", {data['elderly']} yaşlı\n"
    )
    lines += ["RİSK ÖZETİ", as_text(plan.get("household_risk_summary")), ""]
    lines.append("ÖNCELİKLİ ADIMLAR")
    for i, a in enumerate(plan.get("priority_actions", []), 1):
        lines.append(f"{i}. {as_text(a)}")
    lines += ["", "GÖREV DAĞILIMI"]
    for r in plan.get("role_assignments", []):
        if isinstance(r, dict):
            lines.append(f"- {r.get('role', '')} ({r.get('person', '')}): {r.get('task', '')}")
        else:
            lines.append(f"- {as_text(r)}")
    lines += ["", "ACİL DURUM ÇANTASI"]
    for b in flatten_bag(plan.get("emergency_bag", [])):
        lines.append(f"[ ] {b}")
    lines += ["", "İLK 72 SAAT"]
    for p in plan.get("first_72_hours", []):
        if isinstance(p, dict):
            lines.append(f"* {p.get('phase', '')}: {p.get('action', '')}")
        else:
            lines.append(f"* {as_text(p)}")
    lines += ["", "Not: Resmî toplanma alanları için e-Devlet / AFAD kanallarını kontrol edin. Acil durumda 112."]
    return "\n".join(lines)


# ==========================================
# SONUÇ EKRANI
# ==========================================
def render_plan(plan: dict, data: dict, extra: dict | None = None):
    extra = extra or {}
    actions = plan.get("priority_actions", []) or []
    roles = plan.get("role_assignments", []) or []
    bag = flatten_bag(plan.get("emergency_bag", []))
    phases = plan.get("first_72_hours", []) or []
    people = data["adults"] + data["children"] + data["elderly"]

    st.markdown(
        f"""
    <div style='margin:26px 0 10px 0'>
        <div style='font-size:1.5rem;font-weight:800;color:#1E293B'>🎉 Planınız hazır!</div>
        <div style='color:#64748B'>{esc(data['district'])}, {esc(data['city'])} için özel olarak hazırlandı.</div>
    </div>""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    for col, ico, val, lbl in [
        (c1, "👥", people, "Hane Sakini"),
        (c2, "⚡", len(actions), "Öncelikli Adım"),
        (c3, "🎒", len(bag), "Çanta Kalemi"),
        (c4, "⏳", len(phases), "Zaman Aşaması"),
    ]:
        col.markdown(
            f"<div class='stat'><div class='stat-ico'>{ico}</div>"
            f"<div class='stat-val'>{val}</div><div class='stat-lbl'>{lbl}</div></div>",
            unsafe_allow_html=True,
        )

    st.write("")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🏡 Risk Özeti", "⚡ Öncelikli Adımlar", "🤝 Görev Dağılımı", "🎒 Acil Durum Çantası", "⏳ İlk 72 Saat"]
    )

    with tab1:
        summary = as_text(plan.get("household_risk_summary")) or "Bilgi oluşturulamadı."
        st.markdown(
            f"<div class='summary-card'>{esc(summary).replace(chr(10), '<br>')}</div>",
            unsafe_allow_html=True,
        )

    with tab2:
        if not actions:
            st.info("Öncelikli adım oluşturulamadı.")
        for i, a in enumerate(actions, 1):
            st.markdown(
                f"<div class='action-card'><div class='action-num'>{i}</div>"
                f"<div class='action-text'>{esc(a)}</div></div>",
                unsafe_allow_html=True,
            )

    with tab3:
        if not roles:
            st.info("Özel bir görev ataması gerekmedi.")
        icons = ["🧭", "🎒", "💧", "🩹", "📻", "🐾", "👶", "🔦"]
        for row_start in range(0, len(roles), 2):
            cols = st.columns(2)
            for j, r in enumerate(roles[row_start : row_start + 2]):
                if not isinstance(r, dict):
                    r = {"role": "Görev", "person": "", "task": as_text(r)}
                ico = icons[(row_start + j) % len(icons)]
                person = (
                    f"<span class='role-person'>👤 {esc(r.get('person'))}</span>" if r.get("person") else ""
                )
                cols[j].markdown(
                    f"<div class='role-card'><div class='role-top'><div class='role-avatar'>{ico}</div>"
                    f"<div><div class='role-title'>{esc(r.get('role'))}</div>{person}</div></div>"
                    f"<div class='role-task'>{esc(r.get('task'))}</div></div>",
                    unsafe_allow_html=True,
                )

    with tab4:
        if not bag:
            st.info("Çanta listesi oluşturulamadı.")
        else:
            checked = sum(1 for i in range(len(bag)) if st.session_state.get(f"bag_{i}", False))
            st.markdown(f"**Hazırlık durumu:** {checked} / {len(bag)} malzeme tamam")
            st.progress(checked / len(bag))
            st.caption("Temin ettikçe işaretleyin – ilerlemeniz yukarıda görünür.")
            left, right = st.columns(2)
            half = (len(bag) + 1) // 2
            with left:
                for i in range(half):
                    st.checkbox(bag[i], key=f"bag_{i}")
            with right:
                for i in range(half, len(bag)):
                    st.checkbox(bag[i], key=f"bag_{i}")

    with tab5:
        if not phases:
            st.info("Zaman planı oluşturulamadı.")
        items = ""
        for i, p in enumerate(phases, 1):
            if not isinstance(p, dict):
                p = {"phase": f"Aşama {i}", "action": as_text(p)}
            items += (
                f"<div class='tl-item'><div class='tl-dot'>{i}</div><div class='tl-body'>"
                f"<div class='tl-phase'>📍 {esc(p.get('phase'))}</div>"
                f"<div class='tl-action'>{esc(p.get('action'))}</div></div></div>"
            )
        st.markdown(f"<div class='timeline'>{items}</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='sos'>🚨 <strong>Acil durumda 112</strong>'yi arayın. Resmî toplanma alanınızı "
        "<strong>e-Devlet</strong> veya <strong>AFAD</strong> üzerinden öğrenmeyi unutmayın.</div>",
        unsafe_allow_html=True,
    )

    st.write("")
    st.download_button(
        "📥 Planı İndir (.txt)",
        data=plan_to_text(plan, data),
        file_name="ready72_afet_plani.txt",
        mime="text/plain",
        use_container_width=True,
    )


# ==========================================
# YAN PANEL
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ Ayarlar")
    env_api_key = os.getenv("OPENROUTER_API_KEY", "")
    api_key = st.text_input("OpenRouter API Anahtarı", value=env_api_key, type="password")
    # YENİ EKLEDİM: v3 model/üretim ayarları
    selected_model = st.text_input("Model (OpenRouter)", value=DEFAULT_MODEL)
    temperature = st.slider(
        "Sıcaklık (temperature)", 0.0, 1.0, 0.2, 0.05,
        help="Düşük = daha tutarlı/tekrarlanabilir çıktı. Test için 0.0-0.3 önerilir.",
    )
    use_chain = st.checkbox("2 aşamalı analiz zinciri (chain)", value=True,
                            help="Önce hane analizi, sonra plan. Kapatırsan tek çağrıyla üretilir (karşılaştırma için).")
    use_fewshot = st.checkbox("Few-shot örnek (plan aşaması)", value=True,
                              help="Prompt C: 1 örnek eklenir (üslup/yapı tutarlılığı). Kapatırsan Prompt B (örneksiz).")
    use_cache = st.checkbox("Aynı girdi → aynı plan (önbellek)", value=True)
    st.markdown("---")
    st.markdown("🌱 **BM SKA 11.5**  \nSürdürülebilir Şehirler ve Topluluklar – Afet Dayanıklılığı")

# ==========================================
# ANA EKRAN
# ==========================================
st.markdown(
    """
<div class='hero'>
    <span class='badge'>🌍 BM SKA 11.5 · Afet Dayanıklılığı</span>
    <h1>🛡️ Ready72<br>Kişisel Afet ve Acil Durum Planınız</h1>
    <p>Sadece 1 dakikada, evinize ve ailenize özel 72 saatlik hazırlık rehberi oluşturun.</p>
    <div class='hero-steps'>
        <div class='hero-step'>① Bilgileri girin</div>
        <div class='hero-step'>② Planı oluşturun</div>
        <div class='hero-step'>③ İndirin &amp; paylaşın</div>
    </div>
</div>
<div class='notice'>
    <div>💡</div>
    <div><strong>Küçük bir hatırlatma:</strong> Bu plan yapay zekâ tarafından rehberlik amacıyla hazırlanır.
    Resmî toplanma alanlarınızı öğrenmek için lütfen e-Devlet veya AFAD kanallarını kontrol edin.</div>
</div>
""",
    unsafe_allow_html=True,
)


def section(num, title, sub):
    st.markdown(
        f"<div class='sec'><div class='sec-num'>{num}</div>"
        f"<div><div class='sec-title'>{title}</div><div class='sec-sub'>{sub}</div></div></div>",
        unsafe_allow_html=True,
    )


with st.form("household_form", border=False):
    section("1", "🏠 Ev ve Konum", "Bulunduğunuz yere göre riskleri belirleyeceğiz")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        city = st.selectbox("İl", ILLER, index=ILLER.index("İstanbul"))
    with col2:
        district = st.text_input("İlçe", placeholder="ör. Kadıköy")
    with col3:
        building_type = st.selectbox("Bina Tipi", ["Betonarme", "Yığma Bina", "Çelik / Ahşap", "Bilmiyorum"])
    with col4:
        floor_number = st.number_input("Bulunduğunuz Kat", min_value=-3, max_value=50, value=2)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    section("2", "👨‍👩‍👧‍👦 Ev Halkı", "Kimler için plan yapıyoruz?")
    col_a, col_c = st.columns(2)
    with col_a:
        adults = st.number_input("🧑 Yetişkin (18-64)", min_value=1, max_value=10, value=2)
    with col_c:
        elderly = st.number_input("🧓 Yaşlı (65+)", min_value=0, max_value=10, value=0)

    st.markdown("**🧒 Çocuklar (yaş gruplarına göre)**")
    kid_cols = st.columns(len(CHILD_GROUPS))
    child_groups = {}
    for col, (key, label) in zip(kid_cols, CHILD_GROUPS):
        with col:
            child_groups[key] = st.number_input(f"{label} ({key})", min_value=0, max_value=10, value=1 if key == "6-12" else 0)
    children = sum(child_groups.values())

    col_d, col_e = st.columns(2)
    with col_d:
        mobility_issue = st.selectbox(
            "♿ Hareket kısıtlılığı / özel gereksinim",
            ["Yok", "Tekerlekli Sandalye Kullanımı", "Yürüme Zorluğu", "Görme / İşitme Engeli"],
        )
    with col_e:
        has_pets = st.selectbox("🐾 Evcil hayvan", ["Yok", "Kedi", "Köpek", "Kuş / Diğer"])

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    section("3", "🎒 Mevcut Hazırlık", "Elinizde zaten neler var? (isteğe bağlı)")
    existing_supplies = st.text_area(
        "Mevcut acil durum malzemeleriniz",
        placeholder="ör. 2 litre su, el feneri, basit ilk yardım çantası, kedi maması...",
        height=100,
    )

    st.write("")
    submit_button = st.form_submit_button("✨ Bana Özel Planı Oluştur", use_container_width=True)

# ==========================================
# PLAN ÜRETİMİ
# ==========================================
if submit_button:
    if not api_key:
        st.error("🔑 Lütfen sol üstteki menüden (») OpenRouter API anahtarınızı girin.")
    elif not district.strip():
        st.warning("📍 Lütfen ilçe bilginizi yazın.")
    else:
        user_input_data = {
            "city": city,
            "district": district.strip(),
            "building_type": building_type,
            "floor_number": floor_number,
            "adults": adults,
            "children": children,
            "child_groups": child_groups,
            "elderly": elderly,
            "mobility_issue": mobility_issue,
            "has_pets": has_pets,
            "existing_supplies": existing_supplies.strip() or "Yok",
        }
        with st.spinner("Yapay zekâ evinizin koşullarını analiz ediyor, rehberiniz hazırlanıyor..."):
            try:
                # YENİ EKLEDİM: v3 plan motoru; analiz/doğrulama/onarım akışı
                result = generate_plan(
                    user_input_data, api_key=api_key, model=selected_model.strip() or DEFAULT_MODEL,
                    temperature=temperature, use_chain=use_chain, use_cache=use_cache, fewshot=use_fewshot,
                )
                plan = result["plan"]
                # Yeni plan geldiğinde eski çanta işaretlerini temizle
                for k in [k for k in st.session_state if str(k).startswith("bag_")]:
                    del st.session_state[k]
                st.session_state["plan"] = plan
                st.session_state["plan_input"] = user_input_data
                # YENİ EKLEDİM: ek tanılama bilgileri bellekte tutulur; istenmeyen paneller arayüzde gösterilmez
                st.session_state["plan_extra"] = {k: result[k] for k in ("warnings", "analysis", "meta")}
                st.balloons()
            except Exception as e:
                st.error(f"Plan oluşturulurken bir hata oluştu: {e}")

# Plan session_state'te saklanır: checkbox'a tıklayınca sonuç kaybolmaz
if "plan" in st.session_state:
    render_plan(st.session_state["plan"], st.session_state["plan_input"], st.session_state.get("plan_extra"))

st.markdown(
    "<div class='footer'>Ready72 · SDG Hackathon Prototipi · Streamlit &amp; Gemini (OpenRouter) ile hazırlandı</div>",
    unsafe_allow_html=True,
)