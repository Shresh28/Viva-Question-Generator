"""Streamlit interface for VivaPrep AI."""

from hashlib import sha256
from html import escape
import os

from dotenv import load_dotenv
import streamlit as st

from src.ai_generator import AIGenerationError, generate_questions
from src.exporters import format_txt, make_pdf
from src.pdf_processor import PDFProcessingError, extract_pdf

load_dotenv()
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "25"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

st.set_page_config(page_title="VivaPrep AI", page_icon=":books:", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root {
  --bg: #090D18; --surface: #101727; --surface-2: #141D30; --surface-3: #18233A;
  --line: #24314A; --line-soft: #1C273C; --text: #F0F3FA; --muted: #9AA7BC;
  --quiet: #71809A; --violet: #9788FF; --blue: #72B7FF; --teal: #67D9C3;
  --amber: #F1C47C; --hard: #C1A0FF;
}
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--text); }
.stApp { color:var(--text); background:radial-gradient(ellipse at 82% 0%, #20204455 0, transparent 30%), radial-gradient(ellipse at 4% 28%, #102B3B4D 0, transparent 25%), var(--bg); }
.block-container { max-width:1160px; padding-top:1.5rem; padding-bottom:2.8rem; }
header[data-testid="stHeader"] { background:#090D18CC; }
#MainMenu, footer { visibility:hidden; }
[data-testid="stToolbar"] { right:1rem; }
.hero { position:relative; overflow:hidden; padding:1.8rem 2.15rem 1.75rem; border:1px solid #30304D; border-radius:18px; margin:.15rem 0 1.55rem; background:linear-gradient(110deg,#111A2D 0%,#15192E 66%,#1A1B35 100%); box-shadow:0 18px 55px #00000030; }
.hero:after { content:''; position:absolute; width:210px; height:210px; right:5%; top:-120px; border:1px solid #9383FF30; border-radius:50%; box-shadow:0 0 0 28px #9383FF08,0 0 0 58px #9383FF06; pointer-events:none; }
.hero-badge { display:inline-flex; align-items:center; gap:8px; color:#C6BEFF; font-size:.68rem; font-weight:700; letter-spacing:1.6px; text-transform:uppercase; margin-bottom:.62rem; }
.hero-badge:before { content:''; width:7px; height:7px; border-radius:50%; background:#9B8CFF; box-shadow:0 0 12px #9B8CFF; }
.hero h1 { margin:0; color:var(--text); font:800 clamp(2rem,4vw,2.65rem)/1.12 'Manrope',sans-serif; letter-spacing:-1.2px; }
.hero h1 span { color:#A99DFF; background:linear-gradient(90deg,#A99DFF,#73BCFF); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.hero p { max-width:650px; color:#A9B5C9; font-size:.98rem; margin:.62rem 0 0; }
.section-kicker { color:#9D92FF; font-size:.68rem; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; margin:.1rem 0 .42rem; }
.section-title { color:var(--text); font:700 1.14rem 'Manrope',sans-serif; margin:0 0 .35rem; }
.section-copy { color:var(--muted); font-size:.88rem; line-height:1.55; margin:0 0 .8rem; }
.surface-card { height:100%; padding:1.05rem 1.2rem; background:linear-gradient(145deg,#121B2B,#101726); border:1px solid var(--line-soft); border-radius:14px; }
.kit-total { color:var(--text); font:800 1.75rem 'Manrope',sans-serif; letter-spacing:-.7px; }
.kit-sub { color:var(--muted); font-size:.83rem; margin:.1rem 0 .55rem; }
.level-pills { display:flex; flex-wrap:wrap; gap:6px; }
.level-pill { padding:.26rem .5rem; border:1px solid var(--line); border-radius:7px; font-size:.72rem; font-weight:600; color:#C7D0E0; background:#FFFFFF05; }
.level-pill.easy { border-color:#328F7B4D; color:#83DDC7; }
.level-pill.medium { border-color:#B58A4A55; color:#F1C47C; }
.level-pill.hard { border-color:#8E6CC255; color:#C6A8FF; }
div[data-testid="stFileUploaderDropzone"] { min-height:158px; background:#0F1726; border:1px dashed #46516B; border-radius:14px; transition:border-color .18s ease,background .18s ease,box-shadow .18s ease; }
div[data-testid="stFileUploaderDropzone"]:hover { border-color:#988CFF; background:#131A2B; box-shadow:0 0 0 3px #9688FF13; }
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] { background:#0F1726 !important; border:1px dashed #46516B !important; color:#DCE4F2 !important; }
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"]:hover { background:#131A2B !important; border-color:#988CFF !important; }
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] > div { background:transparent !important; color:#DCE4F2 !important; }
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] span,
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] small { color:#C3CCDA !important; }
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] button { background:#1A2340 !important; color:#E2DEFF !important; border-color:#454069 !important; }
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] svg { color:#C3CCDA !important; fill:currentColor; }
div[data-testid="stFileUploaderDropzone"] button { background:#1A2340; color:#D9D5FF; border:1px solid #454069; border-radius:8px; font-weight:600; }
div[data-testid="stFileUploaderDropzone"] button:hover { border-color:#9788FF; color:white; }
div[data-testid="stFileUploader"] section { border:0; }
div[data-testid="stFileUploaderDropzoneInstructions"] { color:#C3CCDA; }
div[data-testid="stFileUploaderDropzoneInstructions"] small { color:var(--quiet); }
div[data-testid="stRadio"] > label { color:#DCE3EF; font-weight:600; }
div[role="radiogroup"] label { color:#C5CDDA; }
.stButton > button, .stDownloadButton > button { min-height:2.65rem; border-radius:9px; font-weight:700; transition:all .16s ease; }
.stButton > button[kind="primary"] { color:#fff; border:1px solid #8175E9; background:linear-gradient(100deg,#6659D5,#7767E8 62%,#4D7DCF); box-shadow:0 7px 22px #6559D52B; }
.stButton > button[kind="primary"]:hover { border-color:#B3AAFF; box-shadow:0 9px 28px #7568E74D; transform:translateY(-1px); }
.stButton > button:focus, .stDownloadButton > button:focus { box-shadow:0 0 0 3px #9688FF45; }
.stDownloadButton > button { color:#DCE4F2; background:#151F32; border:1px solid #2E3B54; }
.stDownloadButton > button:hover { color:white; border-color:#7C70D9; background:#1A2340; }
.file-panel { display:flex; flex-wrap:wrap; margin:.75rem 0 1rem; background:#111A2A; border:1px solid #26334A; border-radius:12px; overflow:hidden; }
.file-stat { flex:1 1 130px; padding:.75rem .95rem; border-right:1px solid #202C41; }
.file-stat:first-child { flex:2 1 260px; }
.file-stat:last-child { border-right:0; }
.file-label { color:var(--quiet); font-size:.65rem; font-weight:700; letter-spacing:1.1px; text-transform:uppercase; }
.file-value { color:#E8EDF6; font-size:.85rem; font-weight:600; margin-top:.24rem; overflow-wrap:anywhere; }
.status-ready { color:#7ADBC3; }
.status-missing { color:#F0BE79; }
.local-note { color:#A7B2C6; font-size:.77rem; padding:.4rem 0 .1rem; }
div[data-testid="stExpander"] { border:1px solid #253149; border-radius:11px; background:#111A29; margin:.52rem 0; transition:border-color .15s ease,background .15s ease; }
div[data-testid="stExpander"]:hover { border-color:#424565; background:#131D2E; }
div[data-testid="stExpander"] summary { color:#E7ECF5; font-weight:600; }
div[data-testid="stExpander"] summary:hover { color:#B6AEFF; }
div[data-testid="stTextArea"] textarea { color:#DAE2EF; background:#0E1523; border:1px solid #28344B; border-radius:9px; }
.results-title-row { display:flex; align-items:end; justify-content:space-between; gap:1rem; margin:1.8rem 0 .9rem; }
.results-title { color:var(--text); font:700 1.45rem 'Manrope',sans-serif; margin:0; }
.results-caption { color:var(--muted); font-size:.81rem; margin-top:.28rem; }
.total-badge { white-space:nowrap; padding:.42rem .7rem; border:1px solid #47416F; border-radius:8px; color:#C3BBFF; background:#9788FF12; font-size:.77rem; font-weight:700; }
.stats-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:9px; margin:.8rem 0 1rem; }
.stat-box { padding:.75rem .9rem; background:#111A29; border:1px solid #243149; border-radius:11px; }
.stat-name { color:var(--quiet); font-size:.65rem; font-weight:700; letter-spacing:1px; text-transform:uppercase; }
.stat-value { color:#F1F4F9; font:700 1.35rem 'Manrope',sans-serif; margin-top:.15rem; }
.stat-box.easy { border-top:2px solid #49AC92; }
.stat-box.medium { border-top:2px solid #D39B4E; }
.stat-box.hard { border-top:2px solid #9A7AE4; }
.stTabs [data-baseweb="tab-list"] { gap:7px; padding:4px; background:#0D1421; border:1px solid #202B40; border-radius:11px; }
.stTabs [data-baseweb="tab"] { height:2.65rem; padding:0 .9rem; color:#9AA7BC; border-radius:8px; background:transparent; font-weight:700; }
.stTabs [aria-selected="true"] { color:white !important; background:#1B2540 !important; box-shadow:inset 0 0 0 1px #44416D; }
.difficulty-head { display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:.95rem 1rem; margin:.65rem 0 .85rem; border:1px solid #2A354B; border-radius:11px; background:#111A29; }
.difficulty-name { font:700 1rem 'Manrope',sans-serif; color:#EFF2F8; }
.difficulty-desc { color:var(--muted); font-size:.78rem; margin-top:.18rem; }
.difficulty-count { font-size:.72rem; font-weight:700; border-radius:7px; padding:.3rem .5rem; }
.difficulty-head.easy { border-left:3px solid #49AC92; }.difficulty-head.easy .difficulty-count { color:#83DDC7; background:#49AC9215; }
.difficulty-head.medium { border-left:3px solid #D39B4E; }.difficulty-head.medium .difficulty-count { color:#F1C47C; background:#D39B4E15; }
.difficulty-head.hard { border-left:3px solid #9A7AE4; }.difficulty-head.hard .difficulty-count { color:#C6A8FF; background:#9A7AE415; }
.footer { text-align:center; color:#63718A; font-size:.75rem; border-top:1px solid #1F2A3D; padding-top:1.05rem; margin-top:2.25rem; }
div[data-testid="stAlert"] { border-radius:10px; }
@media(max-width:700px) {
 .block-container { padding:1rem 1rem 2rem; }
 .hero { padding:1.45rem 1.25rem; border-radius:14px; }
 .hero:after { right:-120px; }
 .file-stat { flex:1 1 100%; border-right:0; border-bottom:1px solid #202C41; padding:.62rem .8rem; }
 .file-stat:first-child { flex:1 1 100%; }
 .file-stat:last-child { border-bottom:0; }
 .stats-grid { grid-template-columns:repeat(2,1fr); }
 .results-title-row { align-items:start; flex-direction:column; }
 .stTabs [data-baseweb="tab"] { padding:0 .55rem; font-size:.78rem; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<section class="hero">
  <div class="hero-badge">AI-powered preparation</div>
  <h1>Walk into your viva <span>prepared.</span></h1>
  <p>Turn your project report into personalized viva questions and answers in seconds.</p>
</section>
""", unsafe_allow_html=True)

upload_col, summary_col = st.columns([1.45, .75], gap="large", vertical_alignment="center")
with upload_col:
    st.markdown('<div class="section-kicker">Your report</div><div class="section-title">Upload your project report</div><div class="section-copy">Drop your PDF here or browse files. VivaPrep will find the key ideas worth preparing for.</div>', unsafe_allow_html=True)
    upload = st.file_uploader("Drop your PDF here or browse files", type=["pdf"], help=f"PDF only - maximum file size {MAX_UPLOAD_MB} MB")
with summary_col:
    st.markdown("""
    <div class="surface-card">
      <div class="kit-total">15 questions</div>
      <div class="kit-sub">A balanced preparation kit</div>
      <div class="level-pills"><span class="level-pill easy">05 Easy</span><span class="level-pill medium">05 Medium</span><span class="level-pill hard">05 Hard</span></div>
    </div>
    """, unsafe_allow_html=True)

if upload is not None:
    digest = sha256(upload.getvalue()).hexdigest()
    if st.session_state.get("report_digest") != digest:
        st.session_state.report_digest = digest
        st.session_state.pop("viva_result", None)
    try:
        if upload.size > MAX_UPLOAD_BYTES:
            raise PDFProcessingError(f"This file is over the {MAX_UPLOAD_MB} MB limit. Please upload a smaller PDF.")
        report = extract_pdf(upload, upload.name, MAX_UPLOAD_BYTES)
        status_class = "status-ready" if report.has_readable_text else "status-missing"
        status_label = "Text ready" if report.has_readable_text else "Text not found"
        file_size_mb = upload.size / (1024 * 1024)
        st.markdown(f"""
        <div class="file-panel">
          <div class="file-stat"><div class="file-label">File</div><div class="file-value">{escape(report.filename)}</div></div>
          <div class="file-stat"><div class="file-label">Pages</div><div class="file-value">{report.page_count}</div></div>
          <div class="file-stat"><div class="file-label">Size</div><div class="file-value">{file_size_mb:.1f} MB</div></div>
          <div class="file-stat"><div class="file-label">Status</div><div class="file-value {status_class}">{status_label}</div></div>
        </div>
        """, unsafe_allow_html=True)
        for warning in report.warnings:
            st.warning(warning)
        if report.has_readable_text:
            settings_col, action_col = st.columns([1, 1], vertical_alignment="bottom")
            with settings_col:
                answer_length = st.radio("Answer length", ["Short", "Detailed"], horizontal=True,
                                         help="Short answers are usually 2-3 sentences; Detailed answers are usually 3-5.")
            with action_col:
                st.markdown('<div class="local-note">Local Ollama model - your report stays on this device</div>', unsafe_allow_html=True)
                button_label = "Generate Viva Questions"
                if st.session_state.get("viva_result"):
                    button_label = "Regenerate Questions"
                generate = st.button(button_label, type="primary", use_container_width=True)
            with st.expander("Preview extracted report text"):
                st.text_area("Extracted text", report.text, height=220, label_visibility="collapsed")
            if generate:
                text = report.text
                if len(text) > 70000:
                    text = text[:56000] + "\n\n[Middle of report omitted to fit the analysis limit.]\n\n" + text[-14000:]
                    st.caption("This long report was shortened for analysis; its opening and closing sections were retained.")
                try:
                    with st.spinner("Analyzing your project report and preparing viva questions..."):
                        st.session_state.viva_result = generate_questions(text, answer_length)
                    st.success("Your viva preparation set is ready.")
                except AIGenerationError as exc:
                    st.error(str(exc))
                except Exception:
                    st.error("Something went wrong while preparing your questions. Please try again.")
    except PDFProcessingError as exc:
        st.error(str(exc))
    except Exception:
        st.error("We could not process this upload. Please try a valid, searchable PDF.")

result = st.session_state.get("viva_result")
if result:
    snapshot = result["project_info"]
    technologies = ", ".join(snapshot["technologies"]) if snapshot["technologies"] else "Not specified in the report"
    st.markdown('<div class="section-kicker" style="margin-top:1.6rem">Project summary</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="surface-card" style="height:auto">
      <div class="section-title">{escape(snapshot['title'])}<span style="color:#9B91F0;font-size:.8rem;font-weight:600;margin-left:.55rem">{escape(snapshot['domain'])}</span></div>
      <div class="section-copy" style="margin:.55rem 0">{escape(snapshot['objective'])}</div>
      <div style="color:#8795AC;font-size:.77rem"><b style="color:#B6C0D0">Technologies</b> &nbsp; {escape(technologies)}</div>
    </div>
    """, unsafe_allow_html=True)
    counts = {level: sum(item["difficulty"] == level for item in result["questions"])
              for level in ("Easy", "Medium", "Hard")}
    st.markdown(f"""
    <div class="results-title-row">
      <div><h2 class="results-title">Your Viva Preparation Kit</h2><div class="results-caption">Questions generated from your project report</div></div>
      <span class="total-badge">15 TOTAL QUESTIONS</span>
    </div>
    <div class="stats-grid">
      <div class="stat-box"><div class="stat-name">Total</div><div class="stat-value">15</div></div>
      <div class="stat-box easy"><div class="stat-name">Easy</div><div class="stat-value">{counts['Easy']}</div></div>
      <div class="stat-box medium"><div class="stat-name">Medium</div><div class="stat-value">{counts['Medium']}</div></div>
      <div class="stat-box hard"><div class="stat-name">Hard</div><div class="stat-value">{counts['Hard']}</div></div>
    </div>
    """, unsafe_allow_html=True)
    tabs = st.tabs([f"Easy  ·  {counts['Easy']:02d}", f"Medium  ·  {counts['Medium']:02d}", f"Hard  ·  {counts['Hard']:02d}"])
    descriptions = {
        "Easy": ("Core understanding", "Project purpose, problem, objectives, and essential concepts."),
        "Medium": ("Design and implementation", "Methodology, architecture, tools, modules, and workflow."),
        "Hard": ("Technical reasoning", "Trade-offs, limitations, challenges, security, and future scope."),
    }
    for tab, level in zip(tabs, ("Easy", "Medium", "Hard")):
        with tab:
            title, description = descriptions[level]
            st.markdown(f"""
            <div class="difficulty-head {level.lower()}">
              <div><div class="difficulty-name">{level} <span style="color:#8795AC;font-weight:500">/ {title}</span></div><div class="difficulty-desc">{description}</div></div>
              <span class="difficulty-count">{counts[level]} QUESTIONS</span>
            </div>
            """, unsafe_allow_html=True)
            items = [item for item in result["questions"] if item["difficulty"] == level]
            for idx, item in enumerate(items, 1):
                with st.expander(f"{idx:02d}   {item['question']}", expanded=idx == 1):
                    st.markdown("**Suggested answer**")
                    st.write(item["answer"])
    st.markdown('<div style="height:.4rem"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Take your kit with you</div>', unsafe_allow_html=True)
    txt_col, pdf_col = st.columns(2)
    safe_name = "vivaprep_questions"
    with txt_col:
        st.download_button("Download TXT", format_txt(result), file_name=f"{safe_name}.txt",
                           mime="text/plain", use_container_width=True)
    with pdf_col:
        st.download_button("Download PDF", make_pdf(result), file_name=f"{safe_name}.pdf",
                           mime="application/pdf", use_container_width=True)

st.markdown('<div class="footer">VivaPrep AI &nbsp;·&nbsp; Personalized viva preparation, powered locally by Ollama</div>', unsafe_allow_html=True)

