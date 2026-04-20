"""
frontend/app.py
Clinical Review Summarizer — Clean Medical UI
Run: streamlit run frontend/app.py
"""

import streamlit as st
import requests
from datetime import datetime

API = "http://localhost:8000"

st.set_page_config(
    page_title="Clinical Review Summarizer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Merriweather:ital,wght@0,700;1,400&display=swap');

:root {
    --bg:           #F0F4F8;
    --surface:      #FFFFFF;
    --surface2:     #EBF2F7;
    --surface3:     #DDE8F0;
    --ink:          #0D2137;
    --ink2:         #2D4A62;
    --ink3:         #5B7A91;
    --ink4:         #8BA5B8;
    --blue:         #1565C0;
    --blue-light:   #E3EDF9;
    --teal:         #00796B;
    --teal-light:   #E0F2F0;
    --green:        #2E7D32;
    --green-light:  #E8F5E9;
    --amber:        #F57C00;
    --amber-light:  #FFF3E0;
    --red:          #C62828;
    --red-light:    #FFEBEE;
    --purple:       #6A1B9A;
    --border:       rgba(13,33,55,0.10);
    --border-em:    rgba(13,33,55,0.18);
    --shadow-sm:    0 1px 4px rgba(0,0,0,0.06), 0 0 0 0.5px rgba(0,0,0,0.06);
    --r:            12px;
    --r-sm:         8px;
    --r-pill:       100px;
}

html, body, [class*="css"], .stApp { background-color: var(--bg) !important; color: var(--ink) !important; font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, .stDeployButton { visibility: hidden; display: none !important; }
[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; }
.block-container { padding: 2rem 2.5rem 5rem !important; max-width: 1000px !important; margin: 0 auto !important; }

[data-testid="stSidebar"] { background: var(--ink) !important; border-right: 1px solid rgba(255,255,255,0.06) !important; }
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.80) !important; }
[data-testid="stSidebar"] .stMarkdown p { font-size: 12px !important; color: rgba(255,255,255,0.42) !important; }
[data-testid="stSidebar"] label { color: rgba(255,255,255,0.40) !important; font-size: 10px !important; font-family: 'IBM Plex Mono', monospace !important; letter-spacing: 1px !important; text-transform: uppercase !important; }
[data-testid="stSidebar"] [data-testid="stSlider"] * { accent-color: #4A90D9 !important; }

h1 { font-family: 'Merriweather', serif !important; font-size: 2.2rem !important; font-weight: 700 !important; color: var(--ink) !important; letter-spacing: -0.5px !important; line-height: 1.2 !important; margin-bottom: 4px !important; }
h1 em { color: var(--blue) !important; font-style: italic !important; font-weight: 400 !important; }

.stButton > button { background: var(--blue) !important; color: #fff !important; border: none !important; border-radius: var(--r) !important; font-family: 'Inter', sans-serif !important; font-size: 13px !important; font-weight: 600 !important; padding: 0.65rem 1.4rem !important; width: 100% !important; transition: all 0.15s ease !important; box-shadow: var(--shadow-sm) !important; }
.stButton > button:hover { background: #1976D2 !important; box-shadow: 0 4px 14px rgba(21,101,192,0.30) !important; transform: translateY(-1px) !important; }
.stButton > button:disabled { background: var(--surface3) !important; color: var(--ink4) !important; box-shadow: none !important; }

div.ex-btn .stButton > button { background: var(--surface) !important; border: 1px solid var(--border-em) !important; border-radius: var(--r-pill) !important; color: var(--ink3) !important; font-size: 12px !important; padding: 5px 14px !important; font-weight: 500 !important; box-shadow: none !important; }
div.ex-btn .stButton > button:hover { background: var(--teal-light) !important; border-color: var(--teal) !important; color: var(--teal) !important; transform: none !important; box-shadow: none !important; }

div.clear-btn .stButton > button { background: var(--surface) !important; color: var(--ink3) !important; border: 1.5px solid var(--border-em) !important; box-shadow: none !important; font-weight: 500 !important; }
div.clear-btn .stButton > button:hover { background: var(--surface2) !important; transform: none !important; box-shadow: none !important; }

div.sb-btn .stButton > button { background: rgba(21,101,192,0.15) !important; color: #90CAF9 !important; border: 1px solid rgba(21,101,192,0.30) !important; border-radius: var(--r-sm) !important; font-size: 12px !important; box-shadow: none !important; }
div.sb-btn .stButton > button:hover { background: rgba(21,101,192,0.25) !important; transform: none !important; box-shadow: none !important; }

[data-testid="stTextArea"] textarea { background: var(--surface) !important; border: 1.5px solid var(--border-em) !important; border-radius: var(--r) !important; color: var(--ink) !important; font-size: 14px !important; font-family: 'Inter', sans-serif !important; padding: 14px 16px !important; line-height: 1.7 !important; }
[data-testid="stTextArea"] textarea:focus { border-color: var(--blue) !important; box-shadow: 0 0 0 3px rgba(21,101,192,0.08) !important; }
[data-testid="stTextArea"] textarea::placeholder { color: var(--ink4) !important; }
[data-testid="stTextArea"] label { font-size: 10px !important; color: var(--ink4) !important; font-family: 'IBM Plex Mono', monospace !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; }

[data-testid="stRadio"] > div > div > label { background: var(--surface) !important; border: 1px solid var(--border-em) !important; border-radius: var(--r-pill) !important; padding: 5px 16px 5px 12px !important; font-size: 12px !important; color: var(--ink3) !important; cursor: pointer !important; display: inline-flex !important; align-items: center !important; gap: 5px !important; margin-bottom: 5px !important; font-weight: 500 !important; }
[data-testid="stRadio"] > div > div > label > div:first-child { display: none !important; }
[data-testid="stRadio"] > div > div > label:has(input:checked) { background: var(--blue) !important; border-color: var(--blue) !important; color: #fff !important; }

[data-testid="stSelectbox"] > div > div { background: var(--surface) !important; border: 1.5px solid var(--border-em) !important; border-radius: var(--r-sm) !important; color: var(--ink) !important; font-size: 13px !important; }
[data-testid="stFileUploader"] { background: var(--surface2) !important; border: 1.5px dashed var(--border-em) !important; border-radius: var(--r) !important; }
[data-testid="stFileUploader"] * { color: var(--ink3) !important; font-size: 12px !important; }
[data-testid="stFileUploader"] svg { fill: var(--teal) !important; }
[data-testid="stAlert"] { background: var(--surface) !important; border: 1px solid var(--border-em) !important; border-radius: var(--r) !important; font-size: 13px !important; }
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r); padding: 18px 20px; margin-bottom: 12px; box-shadow: var(--shadow-sm); }
.card-hero { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--blue); border-radius: 0 var(--r) var(--r) 0; padding: 20px 22px; margin-bottom: 14px; box-shadow: var(--shadow-sm); }

.section-divider { background: var(--surface); border: 1px solid var(--border); border-top: 3px solid var(--teal); border-radius: var(--r); padding: 14px 20px; margin: 32px 0 18px 0; box-shadow: var(--shadow-sm); display: flex; align-items: center; gap: 14px; }
.section-divider-icon { font-size: 24px; }
.section-divider-title { font-family: 'Merriweather', serif; font-size: 16px; font-weight: 700; color: var(--teal); }
.section-divider-sub { font-size: 11px; color: var(--ink4); font-family: 'IBM Plex Mono', monospace; margin-top: 3px; letter-spacing: 0.3px; }

.card-risk-low      { background: var(--green-light); border: 1px solid rgba(46,125,50,0.22);  border-radius: var(--r); padding: 16px 20px; margin-bottom: 14px; }
.card-risk-moderate { background: var(--amber-light); border: 1px solid rgba(245,124,0,0.22);  border-radius: var(--r); padding: 16px 20px; margin-bottom: 14px; }
.card-risk-high     { background: var(--red-light);   border: 1px solid rgba(198,40,40,0.22);  border-radius: var(--r); padding: 16px 20px; margin-bottom: 14px; }
.card-risk-unknown  { background: var(--surface2);    border: 1px solid var(--border);          border-radius: var(--r); padding: 16px 20px; margin-bottom: 14px; }
.card-risk-high .body { color: #7B1B1B; } .card-risk-moderate .body { color: #7A3E00; } .card-risk-low .body { color: #1B5E20; }

.tag { display: inline-flex; align-items: center; gap: 6px; font-size: 9px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; font-family: 'IBM Plex Mono', monospace; color: var(--blue); margin-bottom: 10px; }
.tag::before { content: ''; display: inline-block; width: 5px; height: 5px; border-radius: 50%; background: var(--blue); }
.tag.warn   { color: var(--amber); } .tag.warn::before   { background: var(--amber); }
.tag.green  { color: var(--teal);  } .tag.green::before  { background: var(--teal);  }
.tag.amber  { color: var(--amber); } .tag.amber::before  { background: var(--amber); }
.tag.purple { color: var(--purple);} .tag.purple::before { background: var(--purple);}
.tag.red    { color: var(--red);   } .tag.red::before    { background: var(--red);   }

.body  { font-size: 14px; color: var(--ink2); line-height: 1.85; }
.muted { font-size: 13px; color: var(--ink4); font-style: italic; }

.pills { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
.pill { font-size: 11px; padding: 4px 10px; border-radius: var(--r-pill); background: var(--surface2); border: 1px solid var(--border-em); color: var(--ink3); font-family: 'IBM Plex Mono', monospace; font-weight: 500; }
.pill.green { background: var(--green-light); border-color: rgba(46,125,50,0.25); color: var(--green); }
.pill.amber { background: var(--amber-light); border-color: rgba(245,124,0,0.25); color: var(--amber); }
.pill.red   { background: var(--red-light);   border-color: rgba(198,40,40,0.25); color: var(--red);   }
.pill.blue  { background: var(--blue-light);  border-color: rgba(21,101,192,0.20); color: var(--blue); }
.pill.teal  { background: var(--teal-light);  border-color: rgba(0,121,107,0.20); color: var(--teal); }
.chip { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; padding: 3px 10px; border-radius: var(--r-sm); background: var(--blue-light); border: 1px solid rgba(21,101,192,0.15); color: var(--blue); margin: 3px; font-family: 'IBM Plex Mono', monospace; }

.risk-badge { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; padding: 4px 10px; border-radius: var(--r-pill); font-family: 'IBM Plex Mono', monospace; display: inline-block; margin-bottom: 8px; }
.card-risk-high .risk-badge     { background: var(--red);   color: #fff; }
.card-risk-moderate .risk-badge { background: var(--amber); color: #fff; }
.card-risk-low .risk-badge      { background: var(--green); color: #fff; }
.card-risk-unknown .risk-badge  { background: var(--ink4);  color: #fff; }

.cond-row { background: var(--surface2); border: 1px solid var(--border); border-left: 3px solid var(--purple); border-radius: 0 var(--r-sm) var(--r-sm) 0; padding: 12px 14px; margin-bottom: 8px; }
.cond-name { font-size: 13px; font-weight: 600; color: var(--ink); }
.cond-meta { font-size: 10px; color: var(--purple); font-family: 'IBM Plex Mono', monospace; margin-top: 4px; }
.cond-ev   { font-size: 12px; color: var(--ink3); margin-top: 5px; line-height: 1.55; }

.test-row  { background: var(--surface2); border: 1px solid var(--border); border-left: 3px solid var(--teal); border-radius: 0 var(--r-sm) var(--r-sm) 0; padding: 12px 14px; margin-bottom: 8px; }
.test-name { font-size: 13px; font-weight: 600; color: var(--ink); }
.test-freq { font-size: 10px; color: var(--teal); font-family: 'IBM Plex Mono', monospace; margin-top: 3px; }
.test-why  { font-size: 12px; color: var(--ink3); margin-top: 5px; line-height: 1.5; }

.ls-row { padding: 9px 0; border-bottom: 1px solid var(--border); }
.ls-row:last-child { border-bottom: none; }
.ls-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1.2px; color: var(--ink4); font-family: 'IBM Plex Mono', monospace; margin-bottom: 3px; }
.ls-val   { font-size: 13px; color: var(--ink2); line-height: 1.6; }

.prec-item { display: flex; gap: 10px; align-items: flex-start; padding: 9px 0; border-bottom: 1px solid var(--border); }
.prec-item:last-child { border-bottom: none; }
.prec-num  { width: 22px; height: 22px; border-radius: 50%; background: var(--teal); color: #fff; font-size: 10px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px; font-family: 'IBM Plex Mono', monospace; }
.prec-text { font-size: 13px; color: var(--ink2); line-height: 1.6; }

.loader { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r); padding: 56px 24px; text-align: center; margin: 16px 0; box-shadow: var(--shadow-sm); }
.loader-bar { height: 3px; background: var(--surface2); border-radius: 2px; margin: 0 auto 32px; width: 200px; overflow: hidden; }
.loader-fill { height: 100%; width: 40%; background: linear-gradient(90deg, var(--blue), var(--teal)); border-radius: 2px; animation: loadbar 1.5s ease-in-out infinite alternate; }
@keyframes loadbar { from{margin-left:0%} to{margin-left:60%} }
.loader-t { font-family: 'Merriweather', serif; font-size: 20px; color: var(--ink); margin-bottom: 6px; font-weight: 700; }
.loader-s { font-size: 11px; color: var(--ink4); font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.5px; }
.loader-steps { display: flex; gap: 32px; margin-top: 28px; justify-content: center; }
.lstep { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.lstep-dot { width: 7px; height: 7px; border-radius: 50%; animation: pulse-dot 1.4s ease-in-out infinite; }
.lstep:nth-child(1) .lstep-dot { background: var(--blue);   animation-delay: 0.0s; }
.lstep:nth-child(2) .lstep-dot { background: var(--teal);   animation-delay: 0.2s; }
.lstep:nth-child(3) .lstep-dot { background: var(--purple); animation-delay: 0.4s; }
.lstep:nth-child(4) .lstep-dot { background: var(--amber);  animation-delay: 0.6s; }
@keyframes pulse-dot { 0%,100%{transform:scale(1);opacity:0.3} 50%{transform:scale(1.8);opacity:1} }
.lstep-lbl { font-size: 10px; color: var(--ink4); font-family: 'IBM Plex Mono', monospace; text-transform: uppercase; letter-spacing: 1.2px; }

.welcome { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r); padding: 52px 40px; text-align: center; margin-bottom: 20px; box-shadow: var(--shadow-sm); position: relative; overflow: hidden; }
.welcome::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, var(--blue), var(--teal)); }
.welcome-icon  { font-size: 48px; margin-bottom: 16px; }
.welcome-title { font-family: 'Merriweather', serif; font-size: 24px; font-weight: 700; color: var(--ink); margin-bottom: 12px; }
.welcome-sub   { font-size: 14px; color: var(--ink3); line-height: 1.9; max-width: 420px; margin: 0 auto; }

.scope-card { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--teal); border-radius: 0 var(--r) var(--r) 0; padding: 14px 18px; margin-bottom: 16px; box-shadow: var(--shadow-sm); }
.scope-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: var(--teal); font-family: 'IBM Plex Mono', monospace; margin-bottom: 6px; }
.scope-desc  { font-size: 13px; color: var(--ink3); line-height: 1.8; }

.subtitle-banner { background: var(--blue-light); border: 1px solid rgba(21,101,192,0.14); border-left: 3px solid var(--blue); border-radius: 0 var(--r) var(--r) 0; padding: 14px 20px; margin-bottom: 22px; font-size: 13px; color: var(--ink2); line-height: 1.9; }
.subtitle-banner strong { color: var(--blue); font-weight: 600; }

.disclaimer { background: var(--amber-light); border-left: 3px solid var(--amber); border-radius: 0 var(--r-sm) var(--r-sm) 0; padding: 12px 16px; font-size: 12px; color: #7A3E00; line-height: 1.7; margin-top: 14px; }

.hist { padding: 8px 10px; border-radius: 8px; cursor: pointer; margin-bottom: 2px; }
.hist:hover { background: rgba(255,255,255,0.06); }
.hist-q { font-size: 12px; color: rgba(255,255,255,0.75); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500; }
.hist-m { font-size: 10px; color: rgba(255,255,255,0.28); margin-top: 2px; font-family: 'IBM Plex Mono', monospace; }

.stat { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 14px 10px; text-align: center; }
.stat-n { font-size: 26px; font-weight: 700; color: #90CAF9; font-family: 'IBM Plex Mono', monospace; line-height: 1; }
.stat-l { font-size: 9px; color: rgba(255,255,255,0.28); text-transform: uppercase; letter-spacing: 2px; margin-top: 5px; font-family: 'IBM Plex Mono', monospace; }
</style>
""", unsafe_allow_html=True)


# ── API helpers ────────────────────────────────────────────────────────────────
def check_health():
    try:
        r = requests.get(f"{API}/health", timeout=3)
        return True, r.json().get("chromadb", {}).get("total_chunks", 0)
    except: return False, 0

def get_history():
    try:
        r = requests.get(f"{API}/history?limit=50", timeout=3)
        return r.json().get("history", [])
    except: return []

def get_known_sources(history):
    seen, out = set(), []
    for h in history:
        for s in h.get("sources_used", []):
            if s and s not in seen: seen.add(s); out.append(s)
    return out

def call_summarize(query, n_results, use_mmr, source_filter=None):
    payload = {"query": query, "n_results": n_results, "use_mmr": use_mmr}
    if source_filter: payload["source_filter"] = source_filter
    r = requests.post(f"{API}/summarize", json=payload, timeout=60)
    if not r.ok: raise Exception(r.json().get("detail", "Summarize API error"))
    return r.json()

def call_predict(query, n_results, use_mmr, source_filter=None):
    payload = {"query": query, "n_results": n_results, "use_mmr": use_mmr}
    if source_filter: payload["source_filter"] = source_filter
    r = requests.post(f"{API}/predict", json=payload, timeout=90)
    if not r.ok: raise Exception(r.json().get("detail", "Predict API error"))
    return r.json()

def upload_file(file):
    r = requests.post(f"{API}/upload", files={"file": (file.name, file.getvalue(), "application/octet-stream")}, timeout=60)
    if not r.ok: raise Exception(r.json().get("detail", "Upload failed"))
    return r.json()

def fmt_time(ts):
    try: return datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%H:%M")
    except: return ""

def risk_card_cls(lvl):
    return {"low": "card-risk-low", "moderate": "card-risk-moderate", "high": "card-risk-high"}.get(lvl.lower(), "card-risk-unknown")

def risk_pill_cls(lvl):
    return {"low": "pill green", "moderate": "pill amber", "high": "pill red"}.get(lvl.lower(), "pill")

def risk_icon(lvl):
    return {"low": "🟢", "moderate": "🟡", "high": "🔴"}.get(lvl.lower(), "⚪")


# ── Card renderer ──────────────────────────────────────────────────────────────
def render_card(tag_label, content, warn=False, green=False, pink=False):
    cls      = "tag warn" if warn else ("tag green" if green else ("tag purple" if pink else "tag"))
    is_empty = not content or "not mentioned" in content.lower() or "insufficient" in content.lower()
    body_cls = "muted" if is_empty else "body"
    text     = content if content else "Not mentioned in provided documents"
    st.markdown(f'<div class="card"><div class="{cls}">{tag_label}</div><div class="{body_cls}">{text}</div></div>', unsafe_allow_html=True)


# ── Prediction section ─────────────────────────────────────────────────────────
def render_prediction_section(p):
    lvl = p.get("risk_level", "unknown")

    st.markdown(
        f'<div class="{risk_card_cls(lvl)}">'
        f'<div class="risk-badge">{lvl.upper()} RISK</div>'
        f'<div class="tag amber">Overall Risk Profile</div>'
        f'<div class="body">{p.get("risk_summary","")}</div></div>',
        unsafe_allow_html=True,
    )

    conditions = p.get("predicted_conditions", [])
    st.markdown('<div class="card"><div class="tag purple">Predicted Future Conditions</div>', unsafe_allow_html=True)
    if conditions:
        for cond in conditions:
            st.markdown(
                f'<div class="cond-row">'
                f'<div class="cond-name">{cond.get("condition","")}</div>'
                f'<div class="cond-meta">Probability: {cond.get("probability","?")} &nbsp;&middot;&nbsp; '
                f'Horizon: {cond.get("time_horizon","?")} &nbsp;&middot;&nbsp; {cond.get("citation","")}</div>'
                f'<div class="cond-ev">{cond.get("supporting_evidence","")}</div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="muted">No specific conditions predicted from current data.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        precautions = p.get("precautions", [])
        st.markdown('<div class="card"><div class="tag green">Precautions</div>', unsafe_allow_html=True)
        if precautions:
            for i, prec in enumerate(precautions):
                st.markdown(f'<div class="prec-item"><div class="prec-num">{i+1}</div><div class="prec-text">{prec}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="muted">No precautions listed.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        ls    = p.get("lifestyle_changes", {})
        icons = {"diet": "🥗", "exercise": "🏃", "sleep": "😴", "habits": "🚭", "stress": "🧘"}
        st.markdown('<div class="card"><div class="tag green">Lifestyle Changes</div>', unsafe_allow_html=True)
        any_ls = False
        for key, icon in icons.items():
            val = ls.get(key, "").strip()
            if val and val.lower() != "insufficient data":
                any_ls = True
                # One st.markdown per row — avoids Streamlit HTML truncation bug
                st.markdown(f'<div class="ls-row"><div class="ls-label">{icon} {key}</div><div class="ls-val">{val}</div></div>', unsafe_allow_html=True)
        if not any_ls:
            st.markdown('<div class="muted">No lifestyle data available.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    tests = p.get("follow_up_tests", [])
    if tests:
        st.markdown('<div class="card"><div class="tag">Recommended Follow-up Tests</div>', unsafe_allow_html=True)
        for t in tests:
            st.markdown(
                f'<div class="test-row"><div class="test-name">🧪 {t.get("test","")}</div>'
                f'<div class="test-freq">Frequency: {t.get("frequency","As advised")}</div>'
                f'<div class="test-why">{t.get("reason","")}</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3: render_card("Clinical Reasoning", p.get("reasoning", ""))
    with col4: render_card("Data Gaps",          p.get("data_gaps", ""), warn=True)

    st.markdown(
        f'<div class="disclaimer">⚠ <strong>Medical Disclaimer:</strong> '
        f'{p.get("disclaimer","This is an AI-generated prediction for informational purposes only. Always consult a qualified healthcare professional.")}'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {"query": "", "summary": None, "prediction": None, "error": None, "last_uploaded": None}.items():
    if k not in st.session_state: st.session_state[k] = v


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 20px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
            <div style="width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,#1565C0,#00796B);display:flex;align-items:center;justify-content:center;font-size:16px;">🩺</div>
            <div>
                <div style="font-family:'Merriweather',serif;font-size:15px;font-weight:700;color:#FFFFFF;">ClinicalReview</div>
                <div style="font-size:9px;color:rgba(255,255,255,0.28);margin-top:2px;font-family:'IBM Plex Mono',monospace;letter-spacing:2px;text-transform:uppercase;">AI · RAG · Medical</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    online, chunks = check_health()
    history        = get_history()

    color = "#4CAF50" if online else "#EF5350"
    label = "API Online" if online else "API Offline"
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:7px;font-size:11px;font-family:\'IBM Plex Mono\',monospace;">'
        f'<div style="width:7px;height:7px;border-radius:50%;background:{color};animation:pulse 2s ease-in-out infinite;"></div>'
        f'<span style="color:{color};font-weight:600;">{label}</span></div>'
        f'<style>@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}</style>',
        unsafe_allow_html=True,
    )
    if not online:
        st.caption("Start backend first:")
        st.code("uvicorn backend.main:app --port 8000", language=None)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown(f'<div class="stat"><div class="stat-n">{chunks}</div><div class="stat-l">Chunks</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat"><div class="stat-n">{len(history)}</div><div class="stat-l">Queries</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:9px;font-weight:700;color:rgba(255,255,255,0.28);margin-bottom:10px;letter-spacing:2px;text-transform:uppercase;font-family:\'IBM Plex Mono\',monospace;">⚙ Retrieval Settings</div>', unsafe_allow_html=True)
    n_results = st.slider("Top-K chunks", 1, 15, 5)
    use_mmr   = st.checkbox("MMR Diversity Ranking", value=True)

    st.markdown("---")
    st.markdown('<div style="font-size:9px;font-weight:700;color:rgba(255,255,255,0.28);margin-bottom:10px;letter-spacing:2px;text-transform:uppercase;font-family:\'IBM Plex Mono\',monospace;">📄 Upload Document</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("File", type=["txt", "pdf", "docx"], label_visibility="collapsed")
    if uploaded:
        st.session_state["_pending_file"]      = uploaded.getvalue()
        st.session_state["_pending_file_name"] = uploaded.name
    if st.session_state.get("_pending_file"):
        st.markdown('<div class="sb-btn">', unsafe_allow_html=True)
        if st.button("➕  Ingest into ChromaDB", key="ingest_btn"):
            with st.spinner("Processing..."):
                try:
                    class _F:
                        def __init__(self, b, n): self._b = b; self.name = n
                        def getvalue(self): return self._b
                    res = upload_file(_F(st.session_state["_pending_file"], st.session_state["_pending_file_name"]))
                    st.session_state.last_uploaded = st.session_state["_pending_file_name"]
                    st.session_state.pop("_pending_file", None)
                    st.session_state.pop("_pending_file_name", None)
                    st.success(f"✅ {res.get('filename','?')} — {res.get('chunks_added','?')} chunks added")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:9px;font-weight:700;color:rgba(255,255,255,0.28);margin-bottom:10px;letter-spacing:2px;text-transform:uppercase;font-family:\'IBM Plex Mono\',monospace;">🕐 Recent Queries</div>', unsafe_allow_html=True)
    if not history:
        st.markdown('<div style="font-size:12px;color:rgba(255,255,255,0.22);font-style:italic;padding:4px 0;">No queries yet</div>', unsafe_allow_html=True)
    else:
        for h in history[:6]:
            q = h.get("query", "")
            st.markdown(
                f'<div class="hist"><div class="hist-q">📋 {q[:46]}{"..." if len(q)>46 else ""}</div>'
                f'<div class="hist-m">{fmt_time(h.get("timestamp",""))} · {h.get("num_chunks_used","?")} chunks</div></div>',
                unsafe_allow_html=True,
            )


# ── Main page ──────────────────────────────────────────────────────────────────
st.markdown('<h1>Clinical <em>Document AI</em></h1>', unsafe_allow_html=True)
st.markdown("""
<div class="subtitle-banner">
    🩺 <strong>Upload a clinical document, ask your question.</strong>
    Every query automatically gives you a full <strong>Summary</strong> AND a <strong>Risk Prediction with Precautions</strong> — both together in one click, no switching needed.
</div>
""", unsafe_allow_html=True)
st.markdown(
    '<div style="font-size:9px;color:var(--ink4);margin-bottom:24px;font-family:\'IBM Plex Mono\',monospace;letter-spacing:2px;text-transform:uppercase;">'
    'RAG · GROQ LLAMA 3.3 · CHROMADB · SENTENCE-TRANSFORMERS</div>',
    unsafe_allow_html=True,
)

# Example queries
EXAMPLES = ["What is the primary diagnosis?", "What medications were prescribed?", "Post-op recommendations?", "What comorbidities are present?"]
st.markdown('<div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--ink4);font-family:\'IBM Plex Mono\',monospace;margin-bottom:8px;">Try an example</div>', unsafe_allow_html=True)
ex_cols = st.columns(len(EXAMPLES))
for i, (col, ex) in enumerate(zip(ex_cols, EXAMPLES)):
    with col:
        st.markdown('<div class="ex-btn">', unsafe_allow_html=True)
        if st.button(ex, key=f"ex_{i}"):
            st.session_state.update({"query": ex, "summary": None, "prediction": None, "error": None})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Search scope
known_sources = get_known_sources(history)
if st.session_state.last_uploaded and st.session_state.last_uploaded not in known_sources:
    known_sources = [st.session_state.last_uploaded] + known_sources

st.markdown("""
<div class="scope-card">
    <div class="scope-label">📂 Search Scope</div>
    <div class="scope-desc">
        <strong style="color:var(--ink2);">🌐 All documents</strong> — search across everything indexed<br>
        <strong style="color:var(--ink2);">📄 One file</strong> — narrow to a specific patient document
    </div>
</div>
""", unsafe_allow_html=True)

fc1, fc2 = st.columns([1, 2])
with fc1:
    filter_mode = st.radio("scope", ["🌐 All", "📄 One file"], label_visibility="collapsed")
source_filter = None
with fc2:
    if filter_mode == "📄 One file":
        if known_sources:
            source_filter = st.selectbox("file", options=known_sources, label_visibility="collapsed")
        else:
            st.markdown('<div style="font-size:13px;color:var(--red);margin-top:8px;">No documents yet — upload one first.</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

query = st.text_area("Your question", value=st.session_state.query, placeholder="Ask about diagnosis, medications, risk factors, lab values, findings...", height=110)

bcol, ccol = st.columns([5, 1])
with bcol:
    submit = st.button("🔍  Analyze — Summarize & Predict Risks", disabled=not query.strip() or not online, use_container_width=True)
with ccol:
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("✕ Clear", use_container_width=True):
        st.session_state.update({"query": "", "summary": None, "prediction": None, "error": None})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── Run ────────────────────────────────────────────────────────────────────────
if submit and query.strip():
    st.session_state.update({"query": query, "summary": None, "prediction": None, "error": None})
    ph = st.empty()
    with ph:
        st.markdown("""
        <div class="loader">
            <div class="loader-bar"><div class="loader-fill"></div></div>
            <div class="loader-t">Analyzing clinical document...</div>
            <div class="loader-s">summarizing · predicting risks · generating precautions</div>
            <div class="loader-steps">
                <div class="lstep"><div class="lstep-dot"></div><div class="lstep-lbl">Embed</div></div>
                <div class="lstep"><div class="lstep-dot"></div><div class="lstep-lbl">Retrieve</div></div>
                <div class="lstep"><div class="lstep-dot"></div><div class="lstep-lbl">Summarize</div></div>
                <div class="lstep"><div class="lstep-dot"></div><div class="lstep-lbl">Predict</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    try:
        summary    = call_summarize(query, n_results, use_mmr, source_filter)
        prediction = call_predict(query, n_results, use_mmr, source_filter)
        st.session_state.summary    = summary
        st.session_state.prediction = prediction
        ph.empty()
        st.rerun()
    except Exception as e:
        st.session_state.error = str(e)
        ph.empty()
        st.rerun()


# ── Error ──────────────────────────────────────────────────────────────────────
if st.session_state.error:
    st.markdown(
        f'<div class="card" style="border-left:3px solid var(--red);border-radius:0 var(--r) var(--r) 0;">'
        f'<div class="tag red">Error</div><div class="body" style="color:var(--red);">{st.session_state.error}</div></div>',
        unsafe_allow_html=True,
    )

# ── Results ────────────────────────────────────────────────────────────────────
elif st.session_state.summary and st.session_state.prediction:
    r   = st.session_state.summary
    p   = st.session_state.prediction
    lvl = p.get("risk_level", "unknown")
    fp  = f'<span class="pill">{source_filter}</span>' if source_filter else '<span class="pill">All docs</span>'

    st.markdown(
        f'<div class="pills">'
        f'<span class="pill blue">{r.get("num_chunks_used", n_results)} chunks</span>'
        f'<span class="pill">{r.get("model","llama").split("-")[0]}</span>'
        f'<span class="{risk_pill_cls(lvl)}">{risk_icon(lvl)} {lvl.upper()} RISK</span>'
        f'{fp}</div>',
        unsafe_allow_html=True,
    )

    # ── SUMMARY SECTION ──
    st.markdown("""
    <div class="section-divider">
        <div class="section-divider-icon">📋</div>
        <div>
            <div class="section-divider-title">Clinical Summary</div>
            <div class="section-divider-sub">structured · cited · grounded in your document</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="card-hero"><div class="tag">Patient / Study Overview</div>'
        f'<div class="body" style="font-size:15px;">{r.get("overview") or "Not mentioned in provided documents"}</div></div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1: render_card("Key Findings",        r.get("key_findings"))
    with c2: render_card("Diagnosis",           r.get("diagnosis"))
    c3, c4 = st.columns(2)
    with c3: render_card("Recommendations",     r.get("recommendations"), green=True)
    with c4: render_card("Limitations & Risks", r.get("limitations"), warn=True)

    sources = r.get("sources_used", [])
    if sources:
        chips = "".join(f'<span class="chip">📄 {s}</span>' for s in sources if s)
        st.markdown(f'<div class="card"><div class="tag purple">Sources</div>{chips}</div>', unsafe_allow_html=True)

    # ── PREDICTION SECTION ──
    st.markdown("""
    <div class="section-divider">
        <div class="section-divider-icon">🔮</div>
        <div>
            <div class="section-divider-title">Risk Prediction & Precautions</div>
            <div class="section-divider-sub">AI-predicted future risks · precautions · lifestyle · follow-up tests</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    render_prediction_section(p)

# ── Welcome ────────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div class="welcome">
        <div class="welcome-icon">🩺</div>
        <div class="welcome-title">Clinical Document AI</div>
        <div class="welcome-sub">
            Upload a clinical document, type your question,<br>
            and get a full <strong>Summary</strong> + <strong>Risk Prediction with Precautions</strong> — both in one click.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    for col, (bg, color, ico, lbl, desc) in zip([col1, col2, col3], [
        ("#E3EDF9", "#1565C0", "🔍", "Retrieve",  "Semantic search across indexed clinical chunks using sentence-transformers and MMR re-ranking"),
        ("#E0F2F0", "#00796B", "📋", "Summarize", "Groq Llama 3.3 produces a structured summary with overview, findings, diagnosis, and recommendations"),
        ("#F3E5F5", "#6A1B9A", "🔮", "Predict",   "AI predicts future health risks with probabilities, precautions, lifestyle advice, and follow-up tests"),
    ]):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:28px 16px;">
                <div style="width:44px;height:44px;border-radius:11px;background:{bg};display:flex;align-items:center;justify-content:center;font-size:20px;margin:0 auto 14px;">{ico}</div>
                <div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;font-family:'IBM Plex Mono',monospace;color:{color};margin-bottom:8px;">{lbl}</div>
                <div style="font-size:12px;color:var(--ink4);line-height:1.8;">{desc}</div>
            </div>""", unsafe_allow_html=True)