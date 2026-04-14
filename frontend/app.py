"""
frontend/app.py
Clinical Review Summarizer — Indigo + Cool Gray Theme
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&family=Sora:wght@300;400;600&display=swap');

/* ── Base ── */
html, body, [class*="css"], .stApp {
    background-color: #F7F7FB !important;
    color: #1A1740 !important;
    font-family: 'Inter', sans-serif !important;
}

#MainMenu, footer { visibility: hidden; }
.stDeployButton { display: none !important; }

[data-testid="stHeader"] {
    background: transparent !important;
    box-shadow: none !important;
}

.block-container {
    padding: 2.5rem 3rem 4rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #F0EFF9 !important;
    border-right: 1px solid #CECBF6 !important;
    min-width: 280px !important;
}
[data-testid="stSidebar"] * { color: #1A1740 !important; }
[data-testid="stSidebar"] .stMarkdown p {
    font-size: 13px !important;
    color: #7F77DD !important;
}

[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 0px !important;
    width: 0px !important;
    overflow: visible !important;
}

[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: #534AB7 !important;
    color: #EEEDFE !important;
    border: 3px solid #F7F7FB !important;
    border-radius: 50% !important;
    width: 42px !important;
    height: 42px !important;
    box-shadow: 0 4px 14px rgba(83,74,183,0.28) !important;
    z-index: 999999 !important;
    position: fixed !important;
    top: 18px !important;
    left: 12px !important;
}
[data-testid="collapsedControl"]:hover {
    background: #3C3489 !important;
    transform: scale(1.08) !important;
}

[data-testid="stSidebar"][aria-expanded="false"] .stMarkdown,
[data-testid="stSidebar"][aria-expanded="false"] p,
[data-testid="stSidebar"][aria-expanded="false"] h1,
[data-testid="stSidebar"][aria-expanded="false"] h2,
[data-testid="stSidebar"][aria-expanded="false"] h3,
[data-testid="stSidebar"][aria-expanded="false"] label,
[data-testid="stSidebar"][aria-expanded="false"] .stSlider,
[data-testid="stSidebar"][aria-expanded="false"] .stCheckbox,
[data-testid="stSidebar"][aria-expanded="false"] .stFileUploader,
[data-testid="stSidebar"][aria-expanded="false"] .stButton {
    display: none !important;
}

/* ── Sidebar logo ── */
.sb-logo-wrap {
    display: flex;
    align-items: center;
    gap: 11px;
    padding: 4px 0 12px;
}
.sb-logo-icon {
    width: 36px;
    height: 36px;
    background: #534AB7;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.sb-logo-icon svg {
    width: 18px;
    height: 18px;
    fill: none;
    stroke: #EEEDFE;
    stroke-width: 2px;
    stroke-linecap: round;
    stroke-linejoin: round;
}
.sb-logo-name {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #1A1740 !important;
    font-family: 'Sora', sans-serif !important;
    line-height: 1.2;
    letter-spacing: -0.2px;
}
.sb-logo-sub {
    font-size: 11px !important;
    color: #7F77DD !important;
    margin-top: 1px;
}

/* ── Headings ── */
h1 {
    font-family: 'Sora', sans-serif !important;
    font-size: 2.8rem !important;
    font-weight: 600 !important;
    color: #1A1740 !important;
    letter-spacing: -1px !important;
    line-height: 1.15 !important;
}
h1 span {
    color: #534AB7 !important;
    -webkit-text-fill-color: #534AB7 !important;
    font-style: normal !important;
}
h2, h3 {
    font-family: 'Sora', sans-serif !important;
    color: #1A1740 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    color: #1A1740 !important;
    font-size: 1rem !important;
}

/* ── Text area ── */
[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    border: 1px solid #CECBF6 !important;
    border-radius: 12px !important;
    color: #1A1740 !important;
    font-size: 16px !important;
    font-family: 'Inter', sans-serif !important;
    padding: 14px 16px !important;
    line-height: 1.65 !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #7F77DD !important;
    box-shadow: 0 0 0 3px rgba(127,119,221,0.14) !important;
}
[data-testid="stTextArea"] textarea::placeholder { color: #AFA9EC !important; }
[data-testid="stTextArea"] label {
    color: #534AB7 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── All buttons default ── */
.stButton > button {
    background: #534AB7 !important;
    color: #EEEDFE !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 0.65rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.18s ease !important;
    letter-spacing: 0.1px !important;
}
.stButton > button:hover {
    background: #3C3489 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:disabled {
    background: #D3D1C7 !important;
    color: #B4B2A9 !important;
}

/* ── Example query pill buttons ── */
div.ex-btn .stButton > button {
    background: transparent !important;
    border: 1px solid #CECBF6 !important;
    border-radius: 20px !important;
    color: #534AB7 !important;
    font-size: 12px !important;
    font-family: 'Inter', sans-serif !important;
    padding: 5px 13px !important;
    width: 100% !important;
    font-weight: 400 !important;
}
div.ex-btn .stButton > button:hover {
    background: #EEEDFE !important;
    border-color: #AFA9EC !important;
    color: #3C3489 !important;
    transform: none !important;
}

/* ── Slider ── */
[data-testid="stSlider"] label {
    color: #534AB7 !important;
    font-size: 13px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] div[role="progressbar"] {
    background: #7F77DD !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"],
[data-testid="stSlider"] [data-baseweb="slider"] div[data-baseweb="thumb"],
[data-testid="stSlider"] input[type="range"]::-webkit-slider-thumb,
[data-testid="stSlider"] input[type="range"]::-moz-range-thumb {
    background: #534AB7 !important;
    border-color: #534AB7 !important;
    background-color: #534AB7 !important;
}
[data-testid="stSlider"] * { accent-color: #534AB7 !important; }

/* ── Checkbox ── */
[data-testid="stCheckbox"] label {
    color: #534AB7 !important;
    font-size: 13px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stCheckbox"] [data-baseweb="checkbox"] span {
    background-color: #534AB7 !important;
    border-color: #534AB7 !important;
}

/* ── Radio → pill style ── */
[data-testid="stRadio"] label {
    color: #534AB7 !important;
    font-size: 13px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stRadio"] > div > div > label {
    background: #ffffff !important;
    border: 1px solid #CECBF6 !important;
    border-radius: 20px !important;
    padding: 5px 16px 5px 10px !important;
    font-size: 12px !important;
    color: #534AB7 !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    margin-bottom: 4px !important;
}
[data-testid="stRadio"] > div > div > label > div:first-child {
    display: none !important;
}
[data-testid="stRadio"] > div > div > label:has(input:checked) {
    background: #EEEDFE !important;
    border-color: #AFA9EC !important;
    color: #3C3489 !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] label {
    color: #534AB7 !important;
    font-size: 13px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border: 1px solid #CECBF6 !important;
    border-radius: 10px !important;
    color: #1A1740 !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 1px dashed #AFA9EC !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] svg { fill: #7F77DD !important; }
[data-testid="stFileUploader"] p   { color: #534AB7 !important; }

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: #EEEDFE !important;
    border: 1px solid #CECBF6 !important;
    border-radius: 10px !important;
    color: #1A1740 !important;
}

hr { border-color: #CECBF6 !important; }

/* ── Stat box ── */
.stat-box {
    background: #ffffff;
    border: 1px solid #CECBF6;
    border-radius: 10px;
    padding: 10px 12px;
    text-align: center;
}
.stat-num {
    font-size: 22px;
    font-weight: 600;
    color: #534AB7;
    font-family: 'JetBrains Mono', monospace;
}
.stat-lbl {
    font-size: 10px;
    color: #7F77DD;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-top: 2px;
}

/* ── Status ── */
.status-online  { color: #534AB7; font-size: 13px; font-family: 'JetBrains Mono', monospace; }
.status-offline { color: #A32D2D; font-size: 13px; font-family: 'JetBrains Mono', monospace; }

/* ── Section tags ── */
.section-tag {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
    color: #534AB7;
    margin-bottom: 8px;
}
.section-tag.warn { color: #A32D2D; }
.section-tag.src  { color: #7F77DD; }
.section-tag.info { color: #7F77DD; }

/* ── Cards ── */
.card {
    background: #ffffff;
    border: 1px solid #CECBF6;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 2px;
}
.card-hero {
    background: #EEEDFE;
    border: 1px solid #CECBF6;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 2px;
}
.card-accent {
    background: #F0EFF9;
    border: 1px solid #CECBF6;
    border-radius: 12px;
    padding: 14px 18px;
}
.card-filter {
    background: #ffffff;
    border: 1px solid #CECBF6;
    border-left: 3px solid #7F77DD;
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin-bottom: 4px;
}
.body-text { font-size: 15px; color: #1A1740; line-height: 1.7; }
.not-found { font-size: 14px; color: #AFA9EC; font-style: italic; }

/* ── Meta row ── */
.meta-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.meta-pill {
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 4px;
    background: #F0EFF9;
    border: 1px solid #CECBF6;
    color: #534AB7;
    font-family: 'JetBrains Mono', monospace;
}
.meta-pill.orange,
.meta-pill.teal {
    background: #EEEDFE;
    border-color: #AFA9EC;
    color: #3C3489;
}

/* ── Source chips ── */
.chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 4px;
    background: #F0EFF9;
    border: 1px solid #CECBF6;
    color: #534AB7;
    margin-right: 4px;
    margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace;
}
.chip::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #7F77DD;
    flex-shrink: 0;
}
.chip.active {
    background: #EEEDFE;
    border-color: #AFA9EC;
    color: #3C3489;
}

/* ── History ── */
.hist-item { padding: 8px 10px; border-radius: 8px; cursor: pointer; margin-bottom: 3px; }
.hist-item:hover { background: #ffffff; }
.hist-q { font-size: 12px; color: #1A1740; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.hist-t { font-size: 10px; color: #7F77DD; margin-top: 2px; font-family: 'JetBrains Mono', monospace; }

/* ── Loading ── */
.loading-overlay {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; padding: 48px 24px;
    background: #ffffff; border: 1px solid #CECBF6;
    border-radius: 16px; margin: 16px 0;
}
.loading-title { font-size: 16px; font-weight: 500; color: #1A1740; margin-top: 16px; font-family: 'Sora', sans-serif; }
.loading-sub   { font-size: 13px; color: #7F77DD; margin-top: 4px; }
.loading-steps { display: flex; gap: 24px; margin-top: 20px; }
.step          { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.step-dot      { width: 8px; height: 8px; border-radius: 50%; background: #CECBF6; }
.step.active .step-dot { background: #534AB7; }
.step-label    { font-size: 10px; color: #7F77DD; text-transform: uppercase; letter-spacing: 0.5px; font-family: 'JetBrains Mono', monospace; }
.pulse-ring {
    width: 40px; height: 40px; border-radius: 50%;
    border: 3px solid #CECBF6;
    border-top-color: #534AB7; border-right-color: #7F77DD;
    animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Welcome ── */
.welcome {
    background: #EEEDFE; border: 1px solid #CECBF6;
    border-radius: 16px; padding: 40px 32px; text-align: center;
}
.welcome-icon  { font-size: 40px; margin-bottom: 14px; }
.welcome-title { font-size: 20px; font-family: 'Sora', sans-serif; color: #1A1740; margin-bottom: 10px; font-weight: 600; }
.welcome-sub   { font-size: 14px; color: #7F77DD; line-height: 1.75; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def check_health():
    try:
        r = requests.get(f"{API}/health", timeout=3)
        d = r.json()
        return True, d.get("chromadb", {}).get("total_chunks", 0)
    except:
        return False, 0

def get_history():
    try:
        r = requests.get(f"{API}/history?limit=100", timeout=3)
        return r.json().get("history", [])
    except:
        return []

def get_known_sources(history):
    sources = set()
    for h in history:
        for s in h.get("sources_used", []):
            if s:
                sources.add(s)
    return sorted(list(sources))

def call_summarize(query, n_results, use_mmr, source_filter=None):
    payload = {"query": query, "n_results": n_results, "use_mmr": use_mmr}
    if source_filter:
        payload["source_filter"] = source_filter
    r = requests.post(f"{API}/summarize", json=payload, timeout=60)
    if not r.ok:
        raise Exception(r.json().get("detail", "API error"))
    return r.json()

def upload_file(file):
    r = requests.post(
        f"{API}/upload",
        files={"file": (file.name, file.getvalue(), "application/octet-stream")},
        timeout=60,
    )
    if not r.ok:
        raise Exception(r.json().get("detail", "Upload failed"))
    return r.json()

def fmt_time(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%H:%M")
    except:
        return ""

def render_section(tag, content, warn=False, src=False):
    tag_cls  = "section-tag warn" if warn else ("section-tag src" if src else "section-tag")
    is_empty = not content or "not mentioned" in content.lower()
    body_cls = "not-found" if is_empty else "body-text"
    text     = content if content else "Not mentioned in provided documents"
    st.markdown(f"""
    <div class="card">
        <div class="{tag_cls}">{tag}</div>
        <div class="{body_cls}">{text}</div>
    </div>""", unsafe_allow_html=True)

def render_loading():
    st.markdown("""
    <div class="loading-overlay">
        <div class="pulse-ring"></div>
        <div class="loading-title">Analyzing clinical documents</div>
        <div class="loading-sub">This may take a few seconds</div>
        <div class="loading-steps">
            <div class="step active"><div class="step-dot"></div><div class="step-label">Embed</div></div>
            <div class="step active"><div class="step-dot"></div><div class="step-label">Retrieve</div></div>
            <div class="step active"><div class="step-dot"></div><div class="step-label">Summarize</div></div>
            <div class="step active"><div class="step-dot"></div><div class="step-label">Cite</div></div>
        </div>
    </div>""", unsafe_allow_html=True)


EXAMPLES = [
    "What is the patient's primary diagnosis?",
    "What surgical procedure was performed?",
    "What medications were prescribed?",
    "What are the post-op recommendations?",
    "What comorbidities are present?",
]

# ── Session state ──────────────────────────────────────────────────────────────
if "query"         not in st.session_state: st.session_state.query         = ""
if "result"        not in st.session_state: st.session_state.result        = None
if "error"         not in st.session_state: st.session_state.error         = None
if "loading"       not in st.session_state: st.session_state.loading       = False
if "last_uploaded" not in st.session_state: st.session_state.last_uploaded = None

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:

    # Logo
    st.markdown("""
    <div class="sb-logo-wrap">
      <div class="sb-logo-icon">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <rect x="3" y="3" width="18" height="18" rx="4" stroke="#EEEDFE" stroke-width="1.5" fill="none"/>
          <path d="M12 8v8M8 12h8" stroke="#EEEDFE" stroke-width="2"/>
        </svg>
      </div>
      <div>
        <div class="sb-logo-name">ClinicalReview</div>
        <div class="sb-logo-sub">AI-powered medical summarization</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    online, chunks = check_health()
    history = get_history()

    if online:
        st.markdown('<div class="status-online">● API Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-offline">● API Offline — start backend first</div>', unsafe_allow_html=True)
        st.code("uvicorn backend.main:app --port 8000", language=None)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{chunks}</div><div class="stat-lbl">Chunks</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{len(history)}</div><div class="stat-lbl">Queries</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="font-size:13px;font-weight:600;color:#1A1740;margin-bottom:4px;">⚙ Retrieval Settings</p>', unsafe_allow_html=True)
    n_results = st.slider("Top-K chunks", 1, 15, 5)
    use_mmr   = st.checkbox("MMR Diversity Ranking", value=True)

    st.markdown("---")
    st.markdown('<p style="font-size:13px;font-weight:600;color:#1A1740;margin-bottom:4px;">📄 Upload Document</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload", type=["txt", "pdf", "docx"], label_visibility="collapsed")
    if uploaded:
        if st.button("➕  Ingest into ChromaDB"):
            with st.spinner("Processing…"):
                try:
                    res = upload_file(uploaded)
                    st.session_state.last_uploaded = uploaded.name
                    st.success(f"✅  {uploaded.name}\n{res.get('chunks_added','?')} chunks added · {res.get('doc_type','')}")
                except Exception as e:
                    st.error(str(e))

    st.markdown("---")
    st.markdown('<p style="font-size:13px;font-weight:600;color:#1A1740;margin-bottom:8px;">🕐 Recent Queries</p>', unsafe_allow_html=True)
    if not history:
        st.markdown('<div style="font-size:13px;color:#AFA9EC;font-style:italic;">No queries yet</div>', unsafe_allow_html=True)
    else:
        for h in history[:5]:
            q = h.get("query", "")
            chunks_used = h.get("num_chunks_used", "?")
            st.markdown(f"""
            <div class="hist-item">
                <div class="hist-q">{q[:55]}{'…' if len(q)>55 else ''}</div>
                <div class="hist-t">{fmt_time(h.get('timestamp',''))} · {chunks_used} chunks</div>
            </div>""", unsafe_allow_html=True)


# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown("""
<h1>Ask a <span>clinical question</span></h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#ffffff;border:1px solid #CECBF6;border-left:4px solid #7F77DD;
            border-radius:0 12px 12px 0;padding:16px 22px;margin-bottom:20px;">
    <div style="font-size:16px;color:#1A1740;line-height:1.85;font-weight:300;">
        🩺 <strong style="color:#1A1740;font-weight:500;">Got a lengthy clinical document?</strong>
        Just upload it, ask your question, and get a clean structured summary in seconds.<br>
        No more reading through pages of medical text — the AI finds exactly what matters and presents it clearly.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<p style="color:#AFA9EC;font-size:14px;margin-top:-8px;margin-bottom:24px;'
    'font-family:\'JetBrains Mono\',monospace;">'
    'RAG · Groq Llama 3.3 · ChromaDB · sentence-transformers</p>',
    unsafe_allow_html=True,
)

# Example queries
st.markdown(
    '<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#AFA9EC;'
    'letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">Try an example</div>',
    unsafe_allow_html=True,
)
ex_cols = st.columns(len(EXAMPLES))
for i, (col, ex) in enumerate(zip(ex_cols, EXAMPLES)):
    with col:
        st.markdown('<div class="ex-btn">', unsafe_allow_html=True)
        if st.button(ex, key=f"ex_{i}"):
            st.session_state.query   = ex
            st.session_state.result  = None
            st.session_state.error   = None
            st.session_state.loading = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Source Filter ──────────────────────────────────────────────────────────────
known_sources = get_known_sources(history)
if st.session_state.last_uploaded and st.session_state.last_uploaded not in known_sources:
    known_sources = [st.session_state.last_uploaded] + known_sources

st.markdown("""
<div class="card-filter">
    <div class="section-tag info">🎯 Document Filter — Search Scope</div>
    <div style="font-size:14px;color:#7F77DD;margin-bottom:0px;font-weight:300;">
        Search all indexed documents, or narrow down to a specific uploaded file for accurate personal results.
    </div>
</div>
""", unsafe_allow_html=True)

filter_col1, filter_col2 = st.columns([1, 2])
with filter_col1:
    filter_mode = st.radio(
        "scope",
        ["🌐 All documents", "📄 Specific file"],
        label_visibility="collapsed",
    )

source_filter = None
with filter_col2:
    if filter_mode == "📄 Specific file":
        if known_sources:
            source_filter = st.selectbox(
                "Select file",
                options=known_sources,
                label_visibility="collapsed",
            )
            st.markdown(
                f'<div style="font-size:12px;color:#534AB7;margin-top:6px;'
                f'font-family:\'JetBrains Mono\',monospace;">'
                f'🎯 Searching only in: <b>{source_filter}</b></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="font-size:13px;color:#A32D2D;margin-top:8px;">'
                'No documents ingested yet — upload a file first, then ingest it.</div>',
                unsafe_allow_html=True,
            )

st.markdown("<br>", unsafe_allow_html=True)

# Query input
query = st.text_area(
    "Your clinical question",
    value=st.session_state.query,
    placeholder="Describe symptoms, ask about diagnosis, treatment, medications…",
    height=120,
)

col_btn, col_clear = st.columns([4, 1])
with col_btn:
    submit = st.button("  Summarize  →", disabled=not query.strip() or not online, use_container_width=True)
with col_clear:
    if st.button("✕  Clear", use_container_width=True):
        st.session_state.query   = ""
        st.session_state.result  = None
        st.session_state.error   = None
        st.session_state.loading = False
        st.rerun()


# ── Run query ──────────────────────────────────────────────────────────────────
if submit and query.strip():
    st.session_state.query   = query
    st.session_state.loading = True
    st.session_state.result  = None
    st.session_state.error   = None

    loading_placeholder = st.empty()
    with loading_placeholder:
        render_loading()

    try:
        result = call_summarize(query, n_results, use_mmr, source_filter)
        st.session_state.result  = result
        st.session_state.error   = None
        st.session_state.loading = False
        loading_placeholder.empty()
        st.rerun()
    except Exception as e:
        st.session_state.error   = str(e)
        st.session_state.result  = None
        st.session_state.loading = False
        loading_placeholder.empty()
        st.rerun()


# ── Error ──────────────────────────────────────────────────────────────────────
if st.session_state.error:
    st.markdown(f"""
    <div class="card" style="border-color:#F7C1C1;background:#FCEBEB;border-left:4px solid #E24B4A;">
        <div class="section-tag warn">Error</div>
        <div class="body-text" style="color:#A32D2D;font-size:16px;">{st.session_state.error}</div>
    </div>""", unsafe_allow_html=True)


# ── Result ─────────────────────────────────────────────────────────────────────
elif st.session_state.result:
    r = st.session_state.result
    chunks_used = r.get("num_chunks_used", n_results)
    model       = r.get("model", "llama-3.3-70b-versatile")
    filter_pill = (
        f'<span class="meta-pill teal">🎯 {source_filter}</span>'
        if source_filter
        else '<span class="meta-pill">🌐 All documents</span>'
    )

    st.markdown(f"""
    <div class="meta-row">
        <span class="meta-pill">📄 {chunks_used} chunks retrieved</span>
        <span class="meta-pill">🤖 {model}</span>
        <span class="meta-pill">🔍 top-{n_results} · {'MMR on' if use_mmr else 'MMR off'}</span>
        {filter_pill}
    </div>""", unsafe_allow_html=True)

    overview = r.get("overview", "")
    st.markdown(f"""
    <div class="card-hero">
        <div class="section-tag">Patient / Study Overview</div>
        <div class="body-text" style="font-size:17px;">{overview if overview else 'Not mentioned in provided documents'}</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1: render_section("Key Findings",            r.get("key_findings"))
    with col2: render_section("Diagnosis / Conclusions", r.get("diagnosis"))

    col3, col4 = st.columns(2)
    with col3: render_section("Recommendations / Next Steps", r.get("recommendations"))
    with col4: render_section("Limitations & Risks",          r.get("limitations"), warn=True)

    sources = r.get("sources_used", [])
    if sources:
        chips = "".join(
            f'<span class="chip{"  active" if source_filter and s == source_filter else ""}">📄 {s}</span>'
            for s in sources if s
        )
        st.markdown(f"""
        <div class="card-accent">
            <div class="section-tag src">Source Documents</div>
            <div style="margin-top:6px;">{chips}</div>
        </div>""", unsafe_allow_html=True)


# ── Welcome ────────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div class="welcome">
        <div class="welcome-icon">🩺</div>
        <div class="welcome-title">Ready to summarize clinical documents</div>
        <div class="welcome-sub">
            Select an example query above or type your own clinical question.<br>
            Use the <b style="color:#534AB7;">Document Filter</b> above to search only your uploaded file for accurate personal results.
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    for col, (icon, title, desc) in zip([col1, col2, col3], [
        ("🔍", "Retrieve",  "Semantic search across indexed clinical chunks using sentence-transformers"),
        ("🧠", "Summarize", "Groq Llama 3.3 generates structured summaries across 5 clinical sections"),
        ("📋", "Cite",      "Every claim cited back to the source document — zero hallucination"),
    ]):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:30px 20px;">
                <div style="font-size:36px;margin-bottom:14px;">{icon}</div>
                <div class="section-tag" style="justify-content:center;font-size:12px;">{title}</div>
                <div style="font-size:14px;color:#7F77DD;line-height:1.75;margin-top:8px;">{desc}</div>
            </div>""", unsafe_allow_html=True)
            