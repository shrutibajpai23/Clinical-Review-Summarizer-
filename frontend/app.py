"""
frontend/app.py
Clinical Review Summarizer — Orange Pink White Theme v4 + Source Filter
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
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"], .stApp {
    background-color: #f8fafc !important;
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
}

/* Hide footer and main menu but NOT header (sidebar toggle lives there) */
#MainMenu, footer { visibility: hidden; }

/* Hide ONLY the Deploy button */
.stDeployButton { display: none !important; }

/* Make header transparent so it's invisible but the toggle button stays clickable */
[data-testid="stHeader"] {
    background: transparent !important;
    box-shadow: none !important;
}

.block-container { padding: 2.5rem 3rem 4rem !important; max-width: 100% !important; }

/* ── Sidebar expanded ── */
[data-testid="stSidebar"] {
    background-color: #f1f5f9 !important;
    border-right: 1.5px solid #bae6fd !important;
    min-width: 280px !important;
}
[data-testid="stSidebar"] * { color: #0f172a !important; }
[data-testid="stSidebar"] .stMarkdown p { font-size: 14px !important; }

/* ── Sidebar collapsed ── */
[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 0px !important;
    width: 0px !important;
    overflow: visible !important;
}

/* ── Sidebar toggle button — always visible, fixed to viewport ── */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: #14b8a6 !important;
    color: white !important;
    border: 3px solid white !important;
    border-radius: 50% !important;
    width: 42px !important;
    height: 42px !important;
    box-shadow: 0 4px 14px rgba(20, 184, 166, 0.5) !important;
    z-index: 999999 !important;
    position: fixed !important;
    top: 18px !important;
    left: 12px !important;
}
[data-testid="collapsedControl"]:hover {
    background: #0d9488 !important;
    transform: scale(1.08) !important;
}

/* Hide sidebar content when collapsed — but NOT the toggle button */
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

/* Sidebar Logo - Bigger & Cleaner */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] > div:first-child {
    font-size: 1.85rem !important;
    font-weight: 600 !important;
    margin-bottom: 4px !important;
}

/* Main Heading */
h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 3rem !important;
    font-weight: 600 !important;
    color: #0f172a !important;
    letter-spacing: -0.5px !important;
    line-height: 1.15 !important;
}

h1 span {
    background: linear-gradient(135deg, #0ea5e9, #10b981) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    font-style: italic !important;
}

h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #0f172a !important;
}

[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    border: 1.5px solid #bae6fd !important;
    border-radius: 14px !important;
    color: #0f172a !important;
    font-size: 17px !important;
    font-family: 'Inter', sans-serif !important;
    padding: 16px !important;
    line-height: 1.6 !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15) !important;
}
[data-testid="stTextArea"] textarea::placeholder { color: #94a3b8 !important; }
[data-testid="stTextArea"] label { color: #0369a1 !important; font-size: 14px !important; font-weight: 500 !important; }

.stButton > button {
    background: linear-gradient(135deg, #0ea5e9 0%, #10b981 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { opacity: 0.92 !important; transform: translateY(-1px) !important; }
.stButton > button:disabled { background: #e2e8f0 !important; color: #64748b !important; }

[data-testid="stSlider"] label,
[data-testid="stCheckbox"] label,
[data-testid="stRadio"] label {
    color: #1e40af !important;
    font-size: 13px !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

[data-testid="stSelectbox"] label { color: #0369a1 !important; font-size: 13px !important; font-family: 'IBM Plex Mono', monospace !important; }
[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border: 1.5px solid #bae6fd !important;
    border-radius: 10px !important;
    color: #0f172a !important;
}

[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 1.5px dashed #bae6fd !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] svg { fill: #0ea5e9 !important; }

[data-testid="stAlert"] {
    background: #f0f9ff !important;
    border: 1px solid #bae6fd !important;
    border-radius: 12px !important;
}

hr { border-color: #bae6fd !important; }

.card, .card-accent, .card-hero, .card-filter {
    border-radius: 16px;
    box-shadow: 0 1px 8px rgba(14, 165, 233, 0.06);
}
.card-hero {
    background: linear-gradient(135deg, #f0f9ff 0%, #ecfdf5 100%);
    border: 1.5px solid #bae6fd;
}

.section-tag { color: #0ea5e9; }
.section-tag::before { background: #0ea5e9; }
.section-tag.warn { color: #f43f5e; }
.section-tag.warn::before { background: #f43f5e; }
.section-tag.src  { color: #10b981; }
.section-tag.src::before  { background: #10b981; }

.chip.active, .meta-pill.orange {
    border-color: #0ea5e9;
    color: #0ea5e9;
    background: #e0f2fe;
}

.stat-num {
    background: linear-gradient(135deg, #0ea5e9, #10b981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.status-online  { color: #10b981; }
.welcome { background: linear-gradient(135deg, #f0f9ff 0%, #ecfdf5 100%); }
.pulse-ring {
    border-top-color: #0ea5e9;
    border-right-color: #10b981;
}
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
    """Extract unique source filenames from query history."""
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
    r = requests.post(f"{API}/upload",
        files={"file": (file.name, file.getvalue(), "application/octet-stream")}, timeout=60)
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
    st.markdown("### 🩺 ClinicalReview")
    st.markdown('<p style="font-size:13px;color:#92400e;margin-top:-8px;">AI-powered medical summarization</p>', unsafe_allow_html=True)
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
    st.markdown('<p style="font-size:13px;font-weight:600;color:#1a0a00;margin-bottom:4px;">⚙ Retrieval Settings</p>', unsafe_allow_html=True)
    n_results = st.slider("Top-K chunks", 1, 15, 5)
    use_mmr   = st.checkbox("MMR Diversity Ranking", value=True)

    st.markdown("---")
    st.markdown('<p style="font-size:13px;font-weight:600;color:#1a0a00;margin-bottom:4px;">📄 Upload Document</p>', unsafe_allow_html=True)
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
    st.markdown('<p style="font-size:13px;font-weight:600;color:#1a0a00;margin-bottom:8px;">🕐 Recent Queries</p>', unsafe_allow_html=True)
    if not history:
        st.markdown('<div style="font-size:13px;color:#c4a882;font-style:italic;">No queries yet</div>', unsafe_allow_html=True)
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
<h1>Ask a <span style="background:linear-gradient(135deg,#f97316,#ec4899);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;
font-style:italic;">clinical question</span></h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#ffffff;border:1px solid #fde8d8;border-left:4px solid #f97316;
            border-radius:0 12px 12px 0;padding:16px 22px;margin-bottom:20px;
            box-shadow:0 1px 6px rgba(249,115,22,0.06);">
    <div style="font-size:16px;color:#3d1a00;line-height:1.85;font-weight:300;">
        🩺 <strong style="color:#1a0a00;font-weight:500;">Got a lengthy clinical document?</strong>
        Just upload it, ask your question, and get a clean structured summary in seconds.<br>
        No more reading through pages of medical text — the AI finds exactly what matters and presents it clearly.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<p style="color:#c4a882;font-size:15px;margin-top:-8px;margin-bottom:24px;">'
    'RAG · Groq Llama 3.3 · ChromaDB · sentence-transformers</p>',
    unsafe_allow_html=True,
)

# Example queries
st.markdown(
    '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;color:#c4a882;'
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
    <div style="font-size:14px;color:#92400e;margin-bottom:0px;font-weight:300;">
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
            st.markdown(f'<div style="font-size:12px;color:#f97316;margin-top:6px;font-family:\'IBM Plex Mono\',monospace;">🎯 Searching only in: <b>{source_filter}</b></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:13px;color:#dc2626;margin-top:8px;">No documents ingested yet — upload a file first, then ingest it.</div>', unsafe_allow_html=True)

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
    <div class="card" style="border-color:#fecdd3;background:#fff5f5;border-left:4px solid #f43f5e;">
        <div class="section-tag warn">Error</div>
        <div class="body-text" style="color:#be123c;font-size:16px;">{st.session_state.error}</div>
    </div>""", unsafe_allow_html=True)


# ── Result ─────────────────────────────────────────────────────────────────────
elif st.session_state.result:
    r = st.session_state.result
    chunks_used = r.get("num_chunks_used", n_results)
    model       = r.get("model", "llama-3.3-70b-versatile")
    filter_pill = f'<span class="meta-pill orange">🎯 {source_filter}</span>' if source_filter else '<span class="meta-pill">🌐 All documents</span>'

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
            Use the <b style="color:#f97316;">Document Filter</b> above to search only your uploaded file for accurate personal results.
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    for col, (icon, title, desc) in zip([col1,col2,col3],[
        ("🔍","Retrieve", "Semantic search across indexed clinical chunks using sentence-transformers"),
        ("🧠","Summarize","Groq Llama 3.3 generates structured summaries across 5 clinical sections"),
        ("📋","Cite",     "Every claim cited back to the source document — zero hallucination"),
    ]):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:30px 20px;">
                <div style="font-size:36px;margin-bottom:14px;">{icon}</div>
                <div class="section-tag" style="justify-content:center;font-size:12px;">{title}</div>
                <div style="font-size:14px;color:#92400e;line-height:1.75;margin-top:8px;">{desc}</div>
            </div>""", unsafe_allow_html=True)