"""
frontend/app.py
Clinical Review Summarizer — Clean Medical UI
Palette: Clinical White · Navy · Teal · Amber on soft grey
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
    --blue-mid:     #4A90D9;
    --teal:         #00796B;
    --teal-light:   #E0F2F0;
    --green:        #2E7D32;
    --green-light:  #E8F5E9;
    --amber:        #F57C00;
    --amber-light:  #FFF3E0;
    --red:          #C62828;
    --red-light:    #FFEBEE;
    --purple:       #6A1B9A;
    --purple-light: #F3E5F5;
    --coral:        #E53935;
    --border:       rgba(13,33,55,0.10);
    --border-em:    rgba(13,33,55,0.18);
    --shadow-sm:    0 1px 4px rgba(0,0,0,0.06), 0 0 0 0.5px rgba(0,0,0,0.06);
    --shadow-md:    0 4px 16px rgba(0,0,0,0.08), 0 0 0 0.5px rgba(0,0,0,0.06);
    --r:            12px;
    --r-sm:         8px;
    --r-pill:       100px;
}

html, body, [class*="css"], .stApp {
    background-color: var(--bg) !important;
    color: var(--ink) !important;
    font-family: 'Inter', sans-serif !important;
}
#MainMenu, footer, .stDeployButton { visibility: hidden; display: none !important; }
[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; }
.block-container { padding: 2rem 2.5rem 5rem !important; max-width: 1000px !important; margin: 0 auto !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.80) !important; }
[data-testid="stSidebar"] .stMarkdown p { font-size: 12px !important; color: rgba(255,255,255,0.42) !important; line-height: 1.65 !important; }
[data-testid="stSidebar"] label { color: rgba(255,255,255,0.40) !important; font-size: 10px !important; font-family: 'IBM Plex Mono', monospace !important; letter-spacing: 1px !important; text-transform: uppercase !important; }
[data-testid="stSidebar"] [data-testid="stSlider"] * { accent-color: #4A90D9 !important; }
[data-testid="stSidebar"] [data-testid="stCheckbox"] label { font-size: 11px !important; color: rgba(255,255,255,0.40) !important; font-family: 'IBM Plex Mono', monospace !important; }

/* ── Headings ── */
h1 { font-family: 'Merriweather', serif !important; font-size: 2.2rem !important; font-weight: 700 !important; color: var(--ink) !important; letter-spacing: -0.5px !important; line-height: 1.2 !important; margin-bottom: 4px !important; }
h1 em { color: var(--blue) !important; font-style: italic !important; font-weight: 400 !important; }
h2, h3 { font-family: 'Merriweather', serif !important; color: var(--ink) !important; }

/* ── Buttons ── */
.stButton > button {
    background: var(--blue) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--r) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 0.65rem 1.4rem !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:hover {
    background: #1976D2 !important;
    box-shadow: 0 4px 14px rgba(21,101,192,0.30) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:disabled {
    background: var(--surface3) !important;
    color: var(--ink4) !important;
    box-shadow: none !important;
}

/* Example buttons */
div.ex-btn .stButton > button {
    background: var(--surface) !important;
    border: 1px solid var(--border-em) !important;
    border-radius: var(--r-pill) !important;
    color: var(--ink3) !important;
    font-size: 12px !important;
    padding: 5px 14px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}
div.ex-btn .stButton > button:hover {
    background: var(--teal-light) !important;
    border-color: var(--teal) !important;
    color: var(--teal) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Mode buttons */
div.mode-active .stButton > button {
    background: var(--blue) !important;
    color: #fff !important;
    font-weight: 600 !important;
    border-radius: var(--r) !important;
    box-shadow: 0 4px 12px rgba(21,101,192,0.25) !important;
    border: none !important;
}
div.mode-inactive .stButton > button {
    background: var(--surface) !important;
    color: var(--ink3) !important;
    border: 1.5px solid var(--border-em) !important;
    border-radius: var(--r) !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}
div.mode-inactive .stButton > button:hover {
    background: var(--blue-light) !important;
    border-color: rgba(21,101,192,0.30) !important;
    color: var(--blue) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Clear button */
div.clear-btn .stButton > button {
    background: var(--surface) !important;
    color: var(--ink3) !important;
    border: 1.5px solid var(--border-em) !important;
    box-shadow: none !important;
    font-weight: 500 !important;
}
div.clear-btn .stButton > button:hover {
    background: var(--surface2) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Sidebar upload button */
div.sb-btn .stButton > button {
    background: rgba(21,101,192,0.15) !important;
    color: #90CAF9 !important;
    border: 1px solid rgba(21,101,192,0.30) !important;
    border-radius: var(--r-sm) !important;
    font-size: 12px !important;
    box-shadow: none !important;
}
div.sb-btn .stButton > button:hover {
    background: rgba(21,101,192,0.25) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Text area ── */
[data-testid="stTextArea"] textarea {
    background: var(--surface) !important;
    border: 1.5px solid var(--border-em) !important;
    border-radius: var(--r) !important;
    color: var(--ink) !important;
    font-size: 14px !important;
    font-family: 'Inter', sans-serif !important;
    padding: 14px 16px !important;
    line-height: 1.7 !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(21,101,192,0.08) !important;
}
[data-testid="stTextArea"] textarea::placeholder { color: var(--ink4) !important; }
[data-testid="stTextArea"] label {
    font-size: 10px !important;
    color: var(--ink4) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}

/* ── Slider & checkbox ── */
[data-testid="stSlider"] label { color: rgba(255,255,255,0.40) !important; font-size: 11px !important; font-family: 'IBM Plex Mono', monospace !important; }
[data-testid="stSlider"] * { accent-color: #4A90D9 !important; }
[data-testid="stCheckbox"] label { font-size: 12px !important; }

/* ── Radio ── */
[data-testid="stRadio"] > div > div > label {
    background: var(--surface) !important;
    border: 1px solid var(--border-em) !important;
    border-radius: var(--r-pill) !important;
    padding: 5px 16px 5px 12px !important;
    font-size: 12px !important;
    color: var(--ink3) !important;
    cursor: pointer !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 5px !important;
    margin-bottom: 5px !important;
    font-weight: 500 !important;
}
[data-testid="stRadio"] > div > div > label > div:first-child { display: none !important; }
[data-testid="stRadio"] > div > div > label:has(input:checked) {
    background: var(--blue) !important;
    border-color: var(--blue) !important;
    color: #fff !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--surface) !important;
    border: 1.5px solid var(--border-em) !important;
    border-radius: var(--r-sm) !important;
    color: var(--ink) !important;
    font-size: 13px !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--surface2) !important;
    border: 1.5px dashed var(--border-em) !important;
    border-radius: var(--r) !important;
}
[data-testid="stFileUploader"] * { color: var(--ink3) !important; font-size: 12px !important; }
[data-testid="stFileUploaderFileName"] { color: var(--ink) !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 12px !important; }
[data-testid="stBaseButton-secondary"] {
    background: var(--surface) !important;
    color: var(--teal) !important;
    border: 1px solid var(--border-em) !important;
    border-radius: var(--r-sm) !important;
    font-size: 12px !important;
}
[data-testid="stFileUploader"] svg { fill: var(--teal) !important; }
button[title="Remove file"] { background: var(--surface) !important; color: var(--coral) !important; border-radius: 50% !important; }

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: var(--surface) !important;
    border: 1px solid var(--border-em) !important;
    border-radius: var(--r) !important;
    font-size: 13px !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div {
    color: var(--ink) !important;
    font-size: 13px !important;
}
/* Success alert specifically */
[data-testid="stAlert"][data-baseweb="notification"] {
    background: var(--green-light) !important;
    border: 1px solid rgba(46,125,50,0.25) !important;
}
[data-testid="stAlert"][data-baseweb="notification"] p,
[data-testid="stAlert"][data-baseweb="notification"] span,
[data-testid="stAlert"][data-baseweb="notification"] div {
    color: #1B5E20 !important;
    font-weight: 500 !important;
}
/* Streamlit success/error/warning text override */
.stSuccess, .stSuccess * { color: #1B5E20 !important; background: var(--green-light) !important; }
.stError,   .stError *   { color: #7B1B1B !important; background: var(--red-light) !important; }
.stWarning, .stWarning * { color: #7A3E00 !important; background: var(--amber-light) !important; }
.stInfo,    .stInfo *    { color: #0D2137 !important; background: var(--blue-light) !important; }
/* Force all alert inner text to be dark regardless of parent bg */
[data-testid="stAlert"] * { color: var(--ink) !important; }
[data-testid="stNotification"] * { color: var(--ink) !important; }
div[class*="stSuccess"] p  { color: #1B5E20 !important; font-weight: 500 !important; }
div[class*="stError"]   p  { color: #7B1B1B !important; font-weight: 500 !important; }
div[class*="stWarning"] p  { color: #7A3E00 !important; font-weight: 500 !important; }
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

/* ══════════════════════════════
   CARDS
══════════════════════════════ */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 18px 20px;
    margin-bottom: 12px;
    box-shadow: var(--shadow-sm);
}

.card-hero {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--blue);
    border-radius: 0 var(--r) var(--r) 0;
    padding: 20px 22px;
    margin-bottom: 14px;
    box-shadow: var(--shadow-sm);
}

/* Risk cards */
.card-risk-low {
    background: var(--green-light);
    border: 1px solid rgba(46,125,50,0.22);
    border-radius: var(--r);
    padding: 16px 20px;
    margin-bottom: 14px;
}
.card-risk-moderate {
    background: var(--amber-light);
    border: 1px solid rgba(245,124,0,0.22);
    border-radius: var(--r);
    padding: 16px 20px;
    margin-bottom: 14px;
}
.card-risk-high {
    background: var(--red-light);
    border: 1px solid rgba(198,40,40,0.22);
    border-radius: var(--r);
    padding: 16px 20px;
    margin-bottom: 14px;
}
.card-risk-unknown {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 16px 20px;
    margin-bottom: 14px;
}

/* ══════════════════════════════
   TAGS
══════════════════════════════ */
.tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-family: 'IBM Plex Mono', monospace;
    color: var(--blue);
    margin-bottom: 10px;
}
.tag::before {
    content: '';
    display: inline-block;
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--blue);
}
.tag.warn   { color: var(--amber); }   .tag.warn::before   { background: var(--amber); }
.tag.green  { color: var(--teal); }    .tag.green::before  { background: var(--teal); }
.tag.amber  { color: var(--amber); }   .tag.amber::before  { background: var(--amber); }
.tag.purple { color: var(--purple); }  .tag.purple::before { background: var(--purple); }
.tag.red    { color: var(--red); }     .tag.red::before    { background: var(--red); }

.body  { font-size: 14px; color: var(--ink2); line-height: 1.85; font-weight: 400; }
.muted { font-size: 13px; color: var(--ink4); font-style: italic; }

/* ══════════════════════════════
   PILLS & CHIPS
══════════════════════════════ */
.pills { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
.pill {
    font-size: 11px;
    padding: 4px 10px;
    border-radius: var(--r-pill);
    background: var(--surface2);
    border: 1px solid var(--border-em);
    color: var(--ink3);
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 500;
}
.pill.green  { background: var(--green-light);  border-color: rgba(46,125,50,0.25);   color: var(--green); }
.pill.amber  { background: var(--amber-light);  border-color: rgba(245,124,0,0.25);   color: var(--amber); }
.pill.red    { background: var(--red-light);    border-color: rgba(198,40,40,0.25);   color: var(--red); }
.pill.blue   { background: var(--blue-light);   border-color: rgba(21,101,192,0.20);  color: var(--blue); }
.pill.teal   { background: var(--teal-light);   border-color: rgba(0,121,107,0.20);   color: var(--teal); }

.chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: var(--r-sm);
    background: var(--blue-light);
    border: 1px solid rgba(21,101,192,0.15);
    color: var(--blue);
    margin: 3px;
    font-family: 'IBM Plex Mono', monospace;
}

/* ══════════════════════════════
   CONDITIONS & TESTS
══════════════════════════════ */
.cond-row {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--purple);
    border-radius: 0 var(--r-sm) var(--r-sm) 0;
    padding: 12px 14px;
    margin-bottom: 8px;
}
.cond-name { font-size: 13px; font-weight: 600; color: var(--ink); }
.cond-meta { font-size: 10px; color: var(--purple); font-family: 'IBM Plex Mono', monospace; margin-top: 4px; letter-spacing: 0.3px; }
.cond-ev   { font-size: 12px; color: var(--ink3); margin-top: 5px; line-height: 1.55; }

.test-row {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--teal);
    border-radius: 0 var(--r-sm) var(--r-sm) 0;
    padding: 12px 14px;
    margin-bottom: 8px;
}
.test-name { font-size: 13px; font-weight: 600; color: var(--ink); }
.test-freq { font-size: 10px; color: var(--teal); font-family: 'IBM Plex Mono', monospace; margin-top: 3px; }
.test-why  { font-size: 12px; color: var(--ink3); margin-top: 5px; line-height: 1.5; }

/* ══════════════════════════════
   LIFESTYLE ROWS
══════════════════════════════ */
.ls-row { padding: 9px 0; border-bottom: 1px solid var(--border); }
.ls-row:last-child { border-bottom: none; }
.ls-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1.2px; color: var(--ink4); font-family: 'IBM Plex Mono', monospace; margin-bottom: 3px; }
.ls-val   { font-size: 13px; color: var(--ink2); line-height: 1.6; }

/* ══════════════════════════════
   PRECAUTIONS
══════════════════════════════ */
.prec-item { display: flex; gap: 10px; align-items: flex-start; padding: 9px 0; border-bottom: 1px solid var(--border); }
.prec-item:last-child { border-bottom: none; }
.prec-num {
    width: 22px; height: 22px;
    border-radius: 50%;
    background: var(--teal);
    color: #fff;
    font-size: 10px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; margin-top: 1px;
    font-family: 'IBM Plex Mono', monospace;
}
.prec-text { font-size: 13px; color: var(--ink2); line-height: 1.6; }

/* ══════════════════════════════
   LOADER
══════════════════════════════ */
.loader {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 56px 24px;
    text-align: center;
    margin: 16px 0;
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}
.loader-bar {
    height: 3px;
    background: var(--surface2);
    border-radius: 2px;
    margin: 0 auto 32px;
    width: 200px;
    overflow: hidden;
}
.loader-fill {
    height: 100%;
    width: 40%;
    background: linear-gradient(90deg, var(--blue), var(--teal));
    border-radius: 2px;
    animation: loadbar 1.5s ease-in-out infinite alternate;
}
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

/* ══════════════════════════════
   WELCOME
══════════════════════════════ */
.welcome {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 52px 40px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}
.welcome::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--blue), var(--teal));
}
.welcome-icon  { font-size: 48px; margin-bottom: 16px; }
.welcome-title { font-family: 'Merriweather', serif; font-size: 24px; font-weight: 700; color: var(--ink); margin-bottom: 12px; }
.welcome-sub   { font-size: 14px; color: var(--ink3); line-height: 1.9; max-width: 420px; margin: 0 auto; }

/* ══════════════════════════════
   SCOPE & FILTER
══════════════════════════════ */
.scope-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--teal);
    border-radius: 0 var(--r) var(--r) 0;
    padding: 14px 18px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-sm);
}
.scope-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: var(--teal); font-family: 'IBM Plex Mono', monospace; margin-bottom: 6px; }
.scope-desc  { font-size: 13px; color: var(--ink3); line-height: 1.8; }

/* ══════════════════════════════
   SUBTITLE BANNER
══════════════════════════════ */
.subtitle-banner {
    background: var(--blue-light);
    border: 1px solid rgba(21,101,192,0.14);
    border-left: 3px solid var(--blue);
    border-radius: 0 var(--r) var(--r) 0;
    padding: 14px 20px;
    margin-bottom: 22px;
    font-size: 13px;
    color: var(--ink2);
    line-height: 1.9;
}
.subtitle-banner strong { color: var(--blue); font-weight: 600; }

/* ══════════════════════════════
   DISCLAIMER
══════════════════════════════ */
.disclaimer {
    background: var(--amber-light);
    border-left: 3px solid var(--amber);
    border-radius: 0 var(--r-sm) var(--r-sm) 0;
    padding: 12px 16px;
    font-size: 12px;
    color: #7A3E00;
    line-height: 1.7;
    margin-top: 14px;
}

/* ══════════════════════════════
   SIDEBAR HISTORY
══════════════════════════════ */
.hist { padding: 8px 10px; border-radius: 8px; cursor: pointer; margin-bottom: 2px; }
.hist:hover { background: rgba(255,255,255,0.06); }
.hist-q { font-size: 12px; color: rgba(255,255,255,0.75); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500; }
.hist-m { font-size: 10px; color: rgba(255,255,255,0.28); margin-top: 2px; font-family: 'IBM Plex Mono', monospace; }

/* ══════════════════════════════
   STAT CARDS (sidebar)
══════════════════════════════ */
.stat { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 14px 10px; text-align: center; }
.stat-n { font-size: 26px; font-weight: 700; color: #90CAF9; font-family: 'IBM Plex Mono', monospace; line-height: 1; }
.stat-l { font-size: 9px; color: rgba(255,255,255,0.28); text-transform: uppercase; letter-spacing: 2px; margin-top: 5px; font-family: 'IBM Plex Mono', monospace; }

/* ══════════════════════════════
   RISK BANNER (predict mode)
══════════════════════════════ */
.risk-icon-wrap { font-size: 22px; margin-bottom: 8px; }
.risk-badge {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: var(--r-pill);
    font-family: 'IBM Plex Mono', monospace;
    display: inline-block;
    margin-bottom: 8px;
}
.card-risk-high   .risk-badge { background: var(--red);   color: #fff; }
.card-risk-moderate .risk-badge { background: var(--amber); color: #fff; }
.card-risk-low    .risk-badge { background: var(--green);  color: #fff; }
.card-risk-unknown .risk-badge { background: var(--ink4);  color: #fff; }

.card-risk-high   .body { color: #7B1B1B; }
.card-risk-moderate .body { color: #7A3E00; }
.card-risk-low    .body { color: #1B5E20; }
</style>
""", unsafe_allow_html=True)


# ── API helpers ────────────────────────────────────────────────────────────────
def check_health():
    try:
        r = requests.get(f"{API}/health", timeout=3)
        d = r.json()
        return True, d.get("chromadb", {}).get("total_chunks", 0)
    except:
        return False, 0

def get_history():
    try:
        r = requests.get(f"{API}/history?limit=50", timeout=3)
        return r.json().get("history", [])
    except:
        return []

def get_known_sources(history):
    seen, out = set(), []
    for h in history:
        for s in h.get("sources_used", []):
            if s and s not in seen:
                seen.add(s); out.append(s)
    return out

def call_summarize(query, n_results, use_mmr, source_filter=None):
    payload = {"query": query, "n_results": n_results, "use_mmr": use_mmr}
    if source_filter:
        payload["source_filter"] = source_filter
    r = requests.post(f"{API}/summarize", json=payload, timeout=60)
    if not r.ok:
        raise Exception(r.json().get("detail", "API error"))
    return r.json()

def call_predict(query, n_results, use_mmr, source_filter=None):
    payload = {"query": query, "n_results": n_results, "use_mmr": use_mmr}
    if source_filter:
        payload["source_filter"] = source_filter
    r = requests.post(f"{API}/predict", json=payload, timeout=90)
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


# ── Render helpers ─────────────────────────────────────────────────────────────
def render_card(tag_label, content, warn=False, green=False, pink=False):
    cls      = "tag warn" if warn else ("tag green" if green else ("tag purple" if pink else "tag"))
    is_empty = not content or "not mentioned" in content.lower() or "insufficient" in content.lower()
    body_cls = "muted" if is_empty else "body"
    text     = content if content else "Not mentioned in provided documents"
    st.markdown(
        f'<div class="card"><div class="{cls}">{tag_label}</div>'
        f'<div class="{body_cls}">{text}</div></div>',
        unsafe_allow_html=True,
    )

def render_loading(mode="summarize"):
    label = "Predicting health risks..." if mode == "predict" else "Summarizing clinical document..."
    st.markdown(f"""
    <div class="loader">
        <div class="loader-bar"><div class="loader-fill"></div></div>
        <div class="loader-t">{label}</div>
        <div class="loader-s">retrieving chunks · calling groq llama 3.3</div>
        <div class="loader-steps">
            <div class="lstep"><div class="lstep-dot"></div><div class="lstep-lbl">Embed</div></div>
            <div class="lstep"><div class="lstep-dot"></div><div class="lstep-lbl">Retrieve</div></div>
            <div class="lstep"><div class="lstep-dot"></div><div class="lstep-lbl">Generate</div></div>
            <div class="lstep"><div class="lstep-dot"></div><div class="lstep-lbl">Cite</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def risk_card_cls(lvl):
    return {
        "low":      "card-risk-low",
        "moderate": "card-risk-moderate",
        "high":     "card-risk-high",
    }.get(lvl.lower(), "card-risk-unknown")

def risk_pill_cls(lvl):
    return {
        "low":      "pill green",
        "moderate": "pill amber",
        "high":     "pill red",
    }.get(lvl.lower(), "pill")

def risk_icon(lvl):
    return {"low": "🟢", "moderate": "🟡", "high": "🔴"}.get(lvl.lower(), "⚪")


# ── Prediction renderer ────────────────────────────────────────────────────────
def render_prediction(r, n_results, use_mmr, source_filter):
    lvl         = r.get("risk_level", "unknown")
    chunks_used = r.get("num_chunks_used", n_results)
    model       = r.get("model", "llama-3.3-70b-versatile")
    fp          = f'<span class="pill">{source_filter}</span>' if source_filter else '<span class="pill">All docs</span>'

    st.markdown(
        f'<div class="pills">'
        f'<span class="pill">{chunks_used} chunks</span>'
        f'<span class="pill">{model.split("-")[0]}</span>'
        f'<span class="{risk_pill_cls(lvl)}">{risk_icon(lvl)} {lvl.upper()} RISK</span>'
        f'{fp}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="{risk_card_cls(lvl)}">'
        f'<div class="risk-badge">{lvl.upper()} RISK</div>'
        f'<div class="tag amber">Risk Profile</div>'
        f'<div class="body">{r.get("risk_summary","")}</div></div>',
        unsafe_allow_html=True,
    )

    conditions = r.get("predicted_conditions", [])
    st.markdown('<div class="card"><div class="tag purple">Predicted Conditions</div>', unsafe_allow_html=True)
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
        precautions = r.get("precautions", [])
        st.markdown('<div class="card"><div class="tag green">Precautions</div>', unsafe_allow_html=True)
        if precautions:
            for i, p in enumerate(precautions):
                st.markdown(
                    f'<div class="prec-item">'
                    f'<div class="prec-num">{i+1}</div>'
                    f'<div class="prec-text">{p}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="muted">No precautions listed.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        ls    = r.get("lifestyle_changes", {})
        icons = {"diet": "🥗", "exercise": "🏃", "sleep": "😴", "habits": "🚭", "stress": "🧘"}
        st.markdown('<div class="card"><div class="tag green">Lifestyle Changes</div>', unsafe_allow_html=True)
        any_ls = False
        for key, icon in icons.items():
            val = ls.get(key, "").strip()
            if val and val.lower() != "insufficient data":
                any_ls = True
                st.markdown(
                    f'<div class="ls-row">'
                    f'<div class="ls-label">{icon} {key}</div>'
                    f'<div class="ls-val">{val}</div></div>',
                    unsafe_allow_html=True,
                )
        if not any_ls:
            st.markdown('<div class="muted">No lifestyle data available.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    tests = r.get("follow_up_tests", [])
    if tests:
        st.markdown('<div class="card"><div class="tag">Follow-up Tests</div>', unsafe_allow_html=True)
        for t in tests:
            st.markdown(
                f'<div class="test-row">'
                f'<div class="test-name">🧪 {t.get("test","")}</div>'
                f'<div class="test-freq">Frequency: {t.get("frequency","As advised")}</div>'
                f'<div class="test-why">{t.get("reason","")}</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3: render_card("Clinical Reasoning", r.get("reasoning", ""))
    with col4: render_card("Data Gaps",          r.get("data_gaps", ""), warn=True)

    sources = r.get("sources_used", [])
    if sources:
        chips = "".join(f'<span class="chip">📄 {s}</span>' for s in sources if s)
        st.markdown(f'<div class="card"><div class="tag">Sources</div>{chips}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="disclaimer">⚠ <strong>Medical Disclaimer:</strong> '
        f'{r.get("disclaimer","This is an AI-generated prediction for informational purposes only. Always consult a qualified healthcare professional before making any medical decisions.")}'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Constants ──────────────────────────────────────────────────────────────────
EXAMPLES_SUMMARIZE = [
    "What is the primary diagnosis?",
    "What medications were prescribed?",
    "Post-op recommendations?",
    "What comorbidities are present?",
]
EXAMPLES_PREDICT = [
    "What diseases am I at risk of?",
    "Predict future cardiac risks",
    "Assess diabetes risk from labs",
    "Long-term risks from this report",
]


# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "query": "", "result": None, "pred_result": None,
    "error": None, "loading": False, "last_uploaded": None, "mode": "summarize",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 20px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
            <div style="width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,#1565C0,#00796B);
                display:flex;align-items:center;justify-content:center;font-size:16px;">🩺</div>
            <div>
                <div style="font-family:'Merriweather',serif;font-size:15px;font-weight:700;color:#FFFFFF;letter-spacing:-0.3px;">ClinicalReview</div>
                <div style="font-size:9px;color:rgba(255,255,255,0.28);margin-top:2px;font-family:'IBM Plex Mono',monospace;letter-spacing:2px;text-transform:uppercase;">AI · RAG · Medical Intelligence</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    online, chunks = check_health()
    history        = get_history()

    color  = "#4CAF50" if online else "#EF5350"
    label  = "API Online" if online else "API Offline"
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:7px;font-size:11px;font-family:\'IBM Plex Mono\',monospace;">'
        f'<div style="width:7px;height:7px;border-radius:50%;background:{color};animation:pulse 2s ease-in-out infinite;"></div>'
        f'<span style="color:{color};font-weight:600;">{label}</span>'
        f'</div>'
        f'<style>@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}</style>',
        unsafe_allow_html=True,
    )
    if not online:
        st.caption("Start backend first:")
        st.code("uvicorn backend.main:app --port 8000", language=None)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="stat"><div class="stat-n">{chunks}</div><div class="stat-l">Chunks</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat"><div class="stat-n">{len(history)}</div><div class="stat-l">Queries</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:9px;font-weight:700;color:rgba(255,255,255,0.28);margin-bottom:10px;letter-spacing:2px;text-transform:uppercase;font-family:\'IBM Plex Mono\',monospace;">⚙ Retrieval Settings</div>', unsafe_allow_html=True)
    n_results = st.slider("Top-K chunks", 1, 15, 5)
    use_mmr   = st.checkbox("MMR Diversity Ranking", value=True)

    st.markdown("---")
    st.markdown('<div style="font-size:9px;font-weight:700;color:rgba(255,255,255,0.28);margin-bottom:10px;letter-spacing:2px;text-transform:uppercase;font-family:\'IBM Plex Mono\',monospace;">📄 Upload Document</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("File", type=["txt", "pdf", "docx"], label_visibility="collapsed")
    if uploaded:
        # Cache file bytes so button click doesn't lose file on Streamlit rerun
        st.session_state["_pending_file"]      = uploaded.getvalue()
        st.session_state["_pending_file_name"] = uploaded.name
    has_pending = bool(st.session_state.get("_pending_file"))
    if has_pending:
        st.markdown('<div class="sb-btn">', unsafe_allow_html=True)
        if st.button("➕  Ingest into ChromaDB", key="ingest_btn"):
            with st.spinner("Processing..."):
                try:
                    import io
                    file_bytes = st.session_state["_pending_file"]
                    file_name  = st.session_state["_pending_file_name"]
                    class _F:
                        def __init__(self, b, n):
                            self._b = b; self.name = n
                        def getvalue(self): return self._b
                    res = upload_file(_F(file_bytes, file_name))
                    st.session_state.last_uploaded = file_name
                    st.session_state.pop("_pending_file", None)
                    st.session_state.pop("_pending_file_name", None)
                    st.success(f"✅  {file_name} — {res.get('chunks_added', res.get('chunks_stored','?'))} chunks added")
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
            q    = h.get("query", "")
            icon = "🔮" if h.get("type") == "predict" else "📋"
            st.markdown(
                f'<div class="hist">'
                f'<div class="hist-q">{icon} {q[:46]}{"..." if len(q)>46 else ""}</div>'
                f'<div class="hist-m">{fmt_time(h.get("timestamp",""))} · {h.get("type","summarize")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown('<h1>Clinical <em>Document AI</em></h1>', unsafe_allow_html=True)

st.markdown("""
<div class="subtitle-banner">
    🩺 <strong>Got a lengthy clinical document?</strong>
    Upload it, ask your question, and get a clean structured summary in seconds —
    or switch to <strong>Predict mode</strong> to see what health risks the patient may face in the future,
    based entirely on their current clinical data.
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div style="font-size:9px;color:var(--ink4);margin-bottom:24px;font-family:\'IBM Plex Mono\',monospace;letter-spacing:2px;text-transform:uppercase;">'
    'RAG · GROQ LLAMA 3.3 · CHROMADB · SENTENCE-TRANSFORMERS</div>',
    unsafe_allow_html=True,
)

# Mode switcher
mc1, mc2 = st.columns(2)
with mc1:
    active = st.session_state.mode == "summarize"
    st.markdown(f'<div class="{"mode-active" if active else "mode-inactive"}">', unsafe_allow_html=True)
    if st.button("📋  Summarize Document", key="btn_sum", use_container_width=True):
        st.session_state.update({"mode": "summarize", "result": None, "pred_result": None, "error": None})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with mc2:
    active = st.session_state.mode == "predict"
    st.markdown(f'<div class="{"mode-active" if active else "mode-inactive"}">', unsafe_allow_html=True)
    if st.button("🔮  Predict & Precautions", key="btn_pred", use_container_width=True):
        st.session_state.update({"mode": "predict", "result": None, "pred_result": None, "error": None})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
mode = st.session_state.mode

# Example queries
EXAMPLES = EXAMPLES_PREDICT if mode == "predict" else EXAMPLES_SUMMARIZE
st.markdown(
    '<div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;'
    'color:var(--ink4);font-family:\'IBM Plex Mono\',monospace;margin-bottom:8px;">Try an example</div>',
    unsafe_allow_html=True,
)
ex_cols = st.columns(len(EXAMPLES))
for i, (col, ex) in enumerate(zip(ex_cols, EXAMPLES)):
    with col:
        st.markdown('<div class="ex-btn">', unsafe_allow_html=True)
        if st.button(ex, key=f"ex_{i}"):
            st.session_state.update({"query": ex, "result": None, "pred_result": None, "error": None})
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
        <strong style="color:var(--ink2);">🌐 All documents</strong> — search across everything you have uploaded<br>
        <strong style="color:var(--ink2);">📄 One file</strong> — search only within one specific patient document
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
            st.markdown('<div style="font-size:13px;color:var(--coral);margin-top:8px;">No documents yet — upload one first.</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

placeholder = (
    "Describe patient data, ask about risk factors, blood values, lab results..."
    if mode == "predict"
    else "Ask about diagnosis, treatment, medications, findings..."
)
query = st.text_area("Your question", value=st.session_state.query, placeholder=placeholder, height=110)

btn_label = "🔮  Predict Risks & Precautions" if mode == "predict" else "📋  Summarize Document"
bcol, ccol = st.columns([5, 1])
with bcol:
    submit = st.button(btn_label, disabled=not query.strip() or not online, use_container_width=True)
with ccol:
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("✕ Clear", use_container_width=True):
        st.session_state.update({"query": "", "result": None, "pred_result": None, "error": None})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ── Run ────────────────────────────────────────────────────────────────────────
if submit and query.strip():
    st.session_state.update({"query": query, "result": None, "pred_result": None, "error": None})
    ph = st.empty()
    with ph:
        render_loading(mode)
    try:
        if mode == "predict":
            st.session_state.pred_result = call_predict(query, n_results, use_mmr, source_filter)
        else:
            st.session_state.result = call_summarize(query, n_results, use_mmr, source_filter)
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
        f'<div class="tag red">Error</div>'
        f'<div class="body" style="color:var(--red);">{st.session_state.error}</div></div>',
        unsafe_allow_html=True,
    )


# ── Summarize result ───────────────────────────────────────────────────────────
elif st.session_state.result:
    r           = st.session_state.result
    chunks_used = r.get("num_chunks_used", n_results)
    model       = r.get("model", "llama-3.3-70b-versatile")
    fp          = f'<span class="pill">{source_filter}</span>' if source_filter else '<span class="pill">All docs</span>'

    st.markdown(
        f'<div class="pills">'
        f'<span class="pill blue">{chunks_used} chunks</span>'
        f'<span class="pill">{model.split("-")[0]}</span>'
        f'{fp}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="card-hero">'
        f'<div class="tag">Patient / Study Overview</div>'
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


# ── Predict result ─────────────────────────────────────────────────────────────
elif st.session_state.pred_result:
    render_prediction(st.session_state.pred_result, n_results, use_mmr, source_filter)


# ── Welcome ────────────────────────────────────────────────────────────────────
else:
    icon  = "🔮" if mode == "predict" else "🩺"
    title = "Predict future health risks" if mode == "predict" else "Summarize clinical documents"
    sub   = (
        "Upload blood reports, lab results, or clinical notes.<br>"
        "The AI predicts possible future conditions, estimates probabilities,<br>"
        "and suggests <strong>precautions</strong> and lifestyle changes."
        if mode == "predict" else
        "Upload a clinical document and ask your question.<br>"
        "Get a clean structured summary with source citations."
    )
    st.markdown(
        f'<div class="welcome">'
        f'<div class="welcome-icon">{icon}</div>'
        f'<div class="welcome-title">{title}</div>'
        f'<div class="welcome-sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    feat_data = [
        ("blue",   "#1565C0", "🔍", "Retrieve",  "Semantic search across indexed clinical chunks using sentence-transformers"),
        ("teal",   "#00796B", "🧠", "Summarize", "Groq Llama 3.3 generates structured summaries across 5 clinical sections"),
        ("purple", "#6A1B9A", "🔮", "Predict",   "AI predicts future health risks and precautions from current clinical data"),
    ]
    for col, (color_name, color_hex, ico, lbl, desc) in zip([col1, col2, col3], feat_data):
        with col:
            bg = {"blue": "#E3EDF9", "teal": "#E0F2F0", "purple": "#F3E5F5"}[color_name]
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:28px 16px;">
                <div style="width:44px;height:44px;border-radius:11px;background:{bg};
                    display:flex;align-items:center;justify-content:center;
                    font-size:20px;margin:0 auto 14px;">{ico}</div>
                <div style="font-size:9px;font-weight:700;letter-spacing:2px;text-transform:uppercase;
                    font-family:'IBM Plex Mono',monospace;color:{color_hex};margin-bottom:8px;">{lbl}</div>
                <div style="font-size:12px;color:var(--ink4);line-height:1.8;">{desc}</div>
            </div>""", unsafe_allow_html=True)