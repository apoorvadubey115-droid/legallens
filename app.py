"""
LegalLens - Beginner-Friendly Contract Safety Scanner
Main Streamlit Application
"""

# [Summary]: Streamlit web dashboard for contract safety auditing under Indian Law.

import os
import json
import logging
import streamlit as st
from dotenv import load_dotenv

# Configure application logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LegalLens.App")

# Load local environment variables from .env if present
load_dotenv()

from modules.ocr_parser import OCRParser, LegalTextChunker
from modules.vector_store import LegalVectorStore
from modules.auditor import LegalAuditor, DocumentAuditReport
from modules.report_generator import generate_interactive_html_report, generate_word_friendly_doc
from modules.jargon_buster import COMMON_LEGAL_TERMS, find_matching_jargon
from data.sample_contracts import SAMPLE_CONTRACTS_CATALOG

# =====================================================================
# Page Configuration & Styling
# =====================================================================

st.set_page_config(
    page_title="LegalLens | Contract Safety Checker",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for friendly, modern, high-contrast dashboard
st.markdown("""
<style>
    /* Metric Card Styling */
    .metric-card {
        background: #1e2430;
        border-radius: 12px;
        padding: 18px 14px;
        border: 1px solid #334155;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        font-size: 0.82rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        margin-bottom: 0px;
    }

    /* Verdict Banners */
    .verdict-banner-danger {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.25), rgba(185, 28, 28, 0.15));
        border: 2px solid #ef4444;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }
    .verdict-banner-caution {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.25), rgba(180, 83, 9, 0.15));
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }
    .verdict-banner-safe {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(4, 120, 87, 0.15));
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }

    /* Badges */
    .risk-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    .badge-high {
        background-color: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid #ef4444;
    }
    .badge-moderate {
        background-color: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid #f59e0b;
    }
    .badge-safe {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid #10b981;
    }
    .badge-category {
        background-color: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }

    /* Plain-English Quote Box */
    .plain-english-box {
        background-color: #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 12px 16px;
        border-radius: 6px;
        color: #f1f5f9;
        font-size: 0.98rem;
        line-height: 1.5;
        margin: 10px 0 14px 0;
    }

    /* Redline Box */
    .redline-box {
        background-color: rgba(16, 185, 129, 0.1);
        border: 1px solid #059669;
        border-radius: 8px;
        padding: 12px 16px;
        color: #a7f3d0;
        font-family: monospace;
        font-size: 0.88rem;
        line-height: 1.5;
    }

    /* Email Draft Box */
    .email-box {
        background-color: #1e293b;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 16px;
        font-family: sans-serif;
        font-size: 0.92rem;
        color: #e2e8f0;
        line-height: 1.6;
        white-space: pre-wrap;
    }

    /* Legal Jargon Buster Cards */
    .jargon-card-app {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .jargon-card-term {
        font-size: 1.05rem;
        font-weight: 700;
        color: #60a5fa;
        margin-bottom: 2px;
    }
    .jargon-card-literal {
        font-size: 0.85rem;
        color: #94a3b8;
        font-style: italic;
        margin-bottom: 8px;
    }
    .jargon-card-meaning {
        background: rgba(16, 185, 129, 0.1);
        border-left: 3px solid #10b981;
        padding: 8px 12px;
        border-radius: 4px;
        color: #e2e8f0;
        font-size: 0.92rem;
        margin-bottom: 8px;
    }
    .jargon-card-risk {
        background: rgba(239, 68, 68, 0.1);
        border-left: 3px solid #ef4444;
        padding: 8px 12px;
        border-radius: 4px;
        color: #fca5a5;
        font-size: 0.90rem;
        margin-bottom: 8px;
    }
    .jargon-card-shield {
        background: rgba(99, 102, 241, 0.1);
        border-left: 3px solid #818cf8;
        padding: 8px 12px;
        border-radius: 4px;
        color: #c7d2fe;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# State Management & Singletons
# =====================================================================

# Caches ChromaDB & embedding model in memory once
@st.cache_resource(show_spinner="Initializing Legal Benchmark Library...")
def get_vector_store():
    """Initializes local ChromaDB and seeds with risk playbook."""
    return LegalVectorStore()


# Initialize vector store
try:
    vector_store = get_vector_store()
except Exception as e:
    vector_store = None
    st.error(f"Vector store initialization error: {e}")

# Session state defaults
if "audit_report" not in st.session_state:
    st.session_state.audit_report = None
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "document_filename" not in st.session_state:
    st.session_state.document_filename = ""


# =====================================================================
# Sidebar: Easy Configuration
# =====================================================================

with st.sidebar:
    st.title("⚖️ LegalLens India")
    st.caption("Contract Safety Scanner for Indian Law")
    st.divider()

    st.subheader("🔑 AI Connection")
    api_key_env = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=api_key_env,
        type="password",
        help="Auto-loaded from your .env file. Can be changed anytime here."
    )

    selected_model_option = st.selectbox(
        "AI Model Engine",
        options=[
            "gemini-1.5-flash (Recommended — Fast & Stable)",
            "gemini-3.8-flash (Latest Preview)",
            "gemini-1.5-pro (Deep Reasoning)"
        ],
        index=0,
        help="Select which Google Gemini model to query. LegalLens will auto-fallback to backup models if any endpoint is busy."
    )
    st.caption("⚡ Auto-failover active: Cascades instantly if Google experiences high demand.")

    st.divider()
    st.subheader("⚙️ Document Settings")
    force_ocr_toggle = st.checkbox(
        "Force Photo / Scan OCR",
        value=False,
        help="Check this for scanned Indian stamp papers, registered deeds, or photos with bilingual/Indic text."
    )

    with st.expander("🛠️ Advanced Settings", expanded=False):
        chunk_size = st.slider("Section Size (characters)", min_value=800, max_value=2500, value=1600, step=100)
        chunk_overlap = st.slider("Overlap (characters)", min_value=50, max_value=300, value=100, step=25)

    st.divider()
    st.subheader("📚 Indian Legal Knowledge Base")
    if vector_store:
        benchmark_count = len(vector_store.get_all_benchmarks())
        st.success(f"**Playbook Active:** {benchmark_count} Indian statutory benchmarks loaded.")

        with st.expander("🔍 View Indian Legal Benchmarks"):
            benchmarks = vector_store.get_all_benchmarks()
            for b in benchmarks:
                tier_badge = "🔴" if b["risk_tier"] == "High Risk" else ("🟡" if b["risk_tier"] == "Moderate Risk" else "🟢")
                st.markdown(f"**{tier_badge} {b['title']}**")
                st.caption(f"Category: {b['category']}")
                st.write(b["explanation"][:140] + "...")
                st.markdown(f"*Indian Law:* `{b['grounded_legal_standard']}`")
                st.divider()

        if st.button("🔄 Re-Seed Indian Legal Playbook"):
            reseeded_count = vector_store.seed_from_playbook(force=True)
            st.success(f"Re-seeded ChromaDB with {reseeded_count} Indian statutory benchmarks!")
    else:
        st.warning("Benchmark library not connected.")


# =====================================================================
# Main Header & Friendly Quick Guide
# =====================================================================

st.markdown("""
# ⚖️ LegalLens India: Contract Safety Checker
### Know exactly what you're signing under Indian Law — in plain, simple English.
Built specifically for **Indian commercial conditions and the Indian Legal System** (Indian Contract Act 1872, Arbitration & Conciliation Act 1996, DPDP Act 2023, and landmark Supreme Court of India precedents).
Upload your employment bond, commercial lease, freelance contract, or vendor agreement to spot **illegal non-competes (Sec 27 ICA)**, **arbitrary penalty bonds (Sec 74 ICA)**, **unilateral arbitrator traps (Perkins Eastman)**, and **unreasonable deposit forfeitures**.
""")

with st.expander("💡 **How it works (In 3 easy steps):**", expanded=False):
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("**1. Upload Contract** 📄")
        st.caption("Drop your PDF, image, or text file. We automatically read both digital files and scanned photos.")
    with col_b:
        st.markdown("**2. Safety Scan** 🔍")
        st.caption("Our AI compares every clause against standard fair terms to spot hidden traps in seconds.")
    with col_c:
        st.markdown("**3. Negotiate with Ease** 💬")
        st.caption("Get plain-English explanations and a ready-to-send email to ask for fair changes before signing.")

st.write("")

# =====================================================================
# 1. Document Upload & Easy Sample Loaders
# =====================================================================

st.markdown("### 1. Choose or Upload a Contract")

col1, col2 = st.columns([3, 2])

with col1:
    uploaded_file = st.file_uploader(
        "Upload PDF, Word document, or Contract Photo",
        type=["pdf", "png", "jpg", "jpeg", "webp"],
        help="Supports digital PDFs as well as scanned contracts and photos."
    )

with col2:
    st.markdown("**Or pick a ready-to-test sample contract:**")
    selected_sample = st.selectbox(
        "Choose an Example Contract to Review:",
        options=["Select an example..."] + list(SAMPLE_CONTRACTS_CATALOG.keys()),
        index=0,
        label_visibility="collapsed"
    )
    if selected_sample != "Select an example...":
        sample_contract_text = SAMPLE_CONTRACTS_CATALOG[selected_sample]
        sample_doc_name = selected_sample.split("(")[0].strip() + ".txt"
        if st.session_state.document_filename != sample_doc_name:
            st.session_state.document_text = sample_contract_text
            st.session_state.document_filename = sample_doc_name
            st.session_state.audit_report = None
            st.rerun()

# If file is uploaded, extract text
if uploaded_file is not None and uploaded_file.name != st.session_state.document_filename:
    with st.spinner("Reading your document..."):
        parser = OCRParser()
        file_bytes = uploaded_file.read()
        res = parser.parse_document(file_bytes, filename=uploaded_file.name, force_ocr=force_ocr_toggle)
        st.session_state.document_text = res.get("text", "")
        st.session_state.document_filename = uploaded_file.name
        st.session_state.audit_report = None
        st.success(f"Successfully loaded **{uploaded_file.name}**!")

# Preview document text in collapsible drawer
if st.session_state.document_text:
    with st.expander(f"📄 View Contract Text ({st.session_state.document_filename or 'Loaded Document'})", expanded=False):
        st.text_area("Contract Text", value=st.session_state.document_text, height=200, disabled=True)


# =====================================================================
# 2. Run Audit Action & Review Depth Mode
# =====================================================================

st.write("")
st.markdown("### 2. Check Contract Safety")

audit_disabled = not bool(st.session_state.document_text)

# Review Depth Mode: Gives user the best of both worlds
audit_mode_choice = st.radio(
    "Choose Review Depth:",
    options=[
        "⚡ Express Scan (~3s) — Lightning-fast review for quick checks & standard agreements",
        "🧠 Deep Legal Counsel (~15s) — Full AI reasoning engine for complex contracts & high-stakes deals"
    ],
    index=0,
    help="Express Scan eliminates thinking latency using grounded benchmarks. Deep Legal Counsel activates Gemini's internal reasoning tokens to cross-examine complex liabilities across sections."
)
is_deep_mode = "Deep" in audit_mode_choice

if st.button("🚀 Check This Contract (Scan for Traps)", type="primary", disabled=audit_disabled, use_container_width=True):
    if not api_key_input:
        st.error("Please add your Gemini API Key in the left sidebar to run the review.")
    else:
        progress_bar = st.progress(0.0)
        status_text = st.empty()

        def update_progress(ratio, msg):
            progress_bar.progress(ratio)
            status_text.text(msg)

        try:
            update_progress(0.15, "Reading contract sections...")
            chunker = LegalTextChunker(chunk_size=1600, chunk_overlap=100)
            chunks = chunker.split_text_into_chunks(st.session_state.document_text)

            if not chunks:
                st.error("No readable text found. Please upload a clear document.")
            else:
                mode_desc = "deep multi-step reasoning" if is_deep_mode else "fast grounded scan"
                update_progress(0.40, f"Analyzing {len(chunks)} sections with {mode_desc}...")
                auditor = LegalAuditor(api_key=api_key_input, model_name=selected_model_option, deep_thinking=is_deep_mode)
                report = auditor.audit_document(
                    chunks=chunks,
                    vector_store=vector_store,
                    progress_callback=update_progress,
                    deep_thinking=is_deep_mode
                )
                st.session_state.audit_report = report
                st.balloons()
                update_progress(1.0, "Review complete!")
        except Exception as err:
            err_msg = str(err)
            logger.exception("Audit failure exception:")
            if "503" in err_msg or "UNAVAILABLE" in err_msg or "high demand" in err_msg.lower():
                st.error("⏳ **Google Gemini Servers Busy (503 High Demand)**")
                st.info("Google's public AI servers are currently experiencing heavy regional traffic. The fail-over cascade will re-route on your next attempt. Please click **'Check This Contract'** again now.")
            else:
                st.error(f"Audit could not complete: {err_msg}")


# =====================================================================
# 3. Simple, Beginner-Friendly Results Dashboard
# =====================================================================

report: DocumentAuditReport = st.session_state.audit_report

if report is not None:
    # Safely migrate older session_state report objects if new fields are missing
    if not hasattr(report, "negotiation_email_draft"):
        try:
            report = DocumentAuditReport.model_validate(report.model_dump())
            st.session_state.audit_report = report
        except Exception:
            setattr(report, "negotiation_email_draft", "")
    st.markdown("---")

    # Overall Verdict Banner
    score = report.overall_risk_score
    if score >= 70:
        banner_class = "verdict-banner-danger"
        verdict_icon = "🚨"
        verdict_title = "DANGEROUS CONTRACT — DO NOT SIGN AS-IS!"
        verdict_msg = "This agreement contains severe one-sided traps. If you sign this without changes, you could be forced to pay their legal bills, forfeit your earned fees, or be banned from working in your field."
    elif score >= 40:
        banner_class = "verdict-banner-caution"
        verdict_icon = "⚠️"
        verdict_title = "PROCEED WITH CAUTION — NEEDS SIMPLE CHANGES"
        verdict_msg = "This contract is mostly standard, but has a few unfair clauses tilted against you. Ask for our recommended adjustments below before signing."
    else:
        banner_class = "verdict-banner-safe"
        verdict_icon = "✅"
        verdict_title = "FAIR & BALANCED — SAFE TO SIGN"
        verdict_msg = "Great news! This agreement follows standard, fair market practices with mutual protections for both sides."

    st.markdown(f"""
    <div class="{banner_class}">
        <div style="font-size: 1.6rem; font-weight: 800; margin-bottom: 8px;">
            {verdict_icon} {verdict_title}
        </div>
        <div style="font-size: 1.05rem; line-height: 1.5; color: #f8fafc;">
            {verdict_msg}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics Summary Row
    high_count = sum(1 for c in report.audited_clauses if c.risk_tier == "High Risk")
    mod_count = sum(1 for c in report.audited_clauses if c.risk_tier == "Moderate Risk")
    safe_count = sum(1 for c in report.audited_clauses if c.risk_tier == "Safe")
    total_clauses = len(report.audited_clauses)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        score_color = "#ef4444" if score >= 70 else ("#f59e0b" if score >= 40 else "#10b981")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Risk Index</div>
            <div class="metric-value" style="color: {score_color};">{score}/100</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Red Flags (Traps)</div>
            <div class="metric-value" style="color: #ef4444;">🚨 {high_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Cautions (To Fix)</div>
            <div class="metric-value" style="color: #f59e0b;">⚠️ {mod_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Fair Boilerplate</div>
            <div class="metric-value" style="color: #10b981;">✅ {safe_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Sections Reviewed</div>
            <div class="metric-value" style="color: #e2e8f0;">📑 {total_clauses}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Strategic Priority Recommendations
    rec_col1, rec_col2 = st.columns([1, 1])
    with rec_col1:
        st.markdown("#### 💡 In Plain English Summary")
        st.info(report.executive_summary)

    with rec_col2:
        st.markdown("#### 🎯 Top 3 Things to Ask for Before Signing")
        with st.container(border=True):
            for idx, r in enumerate(report.key_strategic_recommendations, 1):
                st.markdown(f"**{idx}.** {r}")

    # Ready-to-Send Negotiation Message
    email_draft = getattr(report, "negotiation_email_draft", "")
    if email_draft:
        st.write("")
        with st.expander("📩 **Ready-to-Send Negotiation Email (Copy & Paste to Client/Vendor)**", expanded=True):
            st.caption("Send this polite, professional message to ask for the necessary contract changes:")
            st.markdown(f'<div class="email-box">{email_draft}</div>', unsafe_allow_html=True)

    # 📖 Legal Jargon Buster (Demystifying Technical Terms)
    st.write("")
    with st.expander("📖 **Legal Jargon Buster: Demystifying Complex Contract Terms in Plain English**", expanded=False):
        st.caption("Contracts often use dense Latin or legal phrasing to conceal one-sided terms. Here is what these technical terms actually mean under Indian Law:")
        jargon_cols = st.columns(2)
        for idx, item in enumerate(COMMON_LEGAL_TERMS):
            col = jargon_cols[idx % 2]
            with col:
                st.markdown(f"""
                <div class="jargon-card-app">
                    <div class="jargon-card-term">📖 {item['term']}</div>
                    <div class="jargon-card-literal">({item['literal']})</div>
                    <div class="jargon-card-meaning"><strong>In Plain English:</strong> {item['plain_english']}</div>
                    <div class="jargon-card-risk"><strong>⚠️ Real-World Trap:</strong> {item['real_life_risk']}</div>
                    <div class="jargon-card-shield"><strong>⚖️ Indian Law Shield:</strong> {item['indian_law_shield']}</div>
                </div>
                """, unsafe_allow_html=True)

    # Interactive Clause Explorer
    st.write("")
    st.markdown("### 🔍 Step-by-Step Clause Breakdown")

    filter_col1, filter_col2 = st.columns([3, 2])
    with filter_col1:
        selected_filter = st.radio(
            "Filter clauses by:",
            options=["Show All", "🚨 Red Flags (Traps)", "⚠️ Cautions (Watch Out)", "✅ Fair Terms"],
            horizontal=True
        )
    with filter_col2:
        search_query = st.text_input("Search issues:", placeholder="e.g. indemnity, non-compete, refund, cancel...")

    # Map filter selections
    displayed_clauses = report.audited_clauses
    if selected_filter == "🚨 Red Flags (Traps)":
        displayed_clauses = [c for c in displayed_clauses if c.risk_tier == "High Risk"]
    elif selected_filter == "⚠️ Cautions (Watch Out)":
        displayed_clauses = [c for c in displayed_clauses if c.risk_tier == "Moderate Risk"]
    elif selected_filter == "✅ Fair Terms":
        displayed_clauses = [c for c in displayed_clauses if c.risk_tier == "Safe"]

    if search_query:
        q = search_query.lower()
        displayed_clauses = [
            c for c in displayed_clauses
            if q in c.clause_title.lower()
            or q in c.original_text.lower()
            or q in c.plain_english_explanation.lower()
            or any(q in issue.lower() for issue in c.flagged_issues)
        ]

    st.caption(f"Showing {len(displayed_clauses)} of {total_clauses} clauses.")

    # Render Simple, Beginner-Friendly Clause Cards
    for clause in displayed_clauses:
        badge_class = "badge-high" if clause.risk_tier == "High Risk" else (
            "badge-moderate" if clause.risk_tier == "Moderate Risk" else "badge-safe"
        )
        icon = "🚨 Red Flag" if clause.risk_tier == "High Risk" else ("⚠️ Caution" if clause.risk_tier == "Moderate Risk" else "✅ Fair")

        with st.container(border=True):
            head_col1, head_col2 = st.columns([3, 1])
            with head_col1:
                st.markdown(f"#### {clause.clause_title}")
                st.markdown(
                    f'<span class="risk-badge {badge_class}">{icon}</span> '
                    f'<span class="risk-badge badge-category">{clause.risk_category}</span>',
                    unsafe_allow_html=True
                )
            with head_col2:
                if clause.matched_benchmark_id:
                    st.caption(f"Standard Ref: `{clause.matched_benchmark_id}`")

            # Plain English Translation (First and Most Prominent!)
            st.markdown("**💬 What this actually means for you:**")
            st.markdown(f'<div class="plain-english-box">{clause.plain_english_explanation}</div>', unsafe_allow_html=True)

            detail_col1, detail_col2 = st.columns(2)
            with detail_col1:
                if clause.flagged_issues:
                    st.markdown("**🚩 Why it's a trap:**")
                    for issue in clause.flagged_issues:
                        st.markdown(f"- {issue}")

            with detail_col2:
                st.markdown("**✍️ What you should ask for instead (Counter-Offer):**")
                st.markdown(f'<div class="redline-box">{clause.suggested_redline}</div>', unsafe_allow_html=True)

            # Jargon Buster for this specific clause
            matched_clause_jargon = find_matching_jargon(
                f"{clause.clause_title} {clause.original_text} {clause.plain_english_explanation} {' '.join(clause.flagged_issues)}"
            )
            if matched_clause_jargon:
                with st.expander("📖 Legal Jargon Translated in this Clause", expanded=False):
                    for j in matched_clause_jargon:
                        st.markdown(f"**{j['term']}** *({j['literal']})*")
                        st.markdown(f"**In Plain English:** {j['plain_english']}")
                        st.caption(f"🛡️ *Indian Law Protection:* {j['indian_law_shield']}")

            # Details folded in accordion so beginners aren't overwhelmed
            with st.expander("📄 Show original contract text & legal reference", expanded=False):
                st.caption("Exact Contract Text:")
                st.text(clause.original_text)
                if clause.grounded_citation:
                    st.caption(f"Legal Standard / Rule: {clause.grounded_citation}")

    # Export Section
    st.divider()
    st.markdown("### 💾 Save & Share Your Contract Safety Report")
    st.caption("Download an interactive, beautifully formatted report to share with colleagues, clients, or retain for your records.")

    doc_base_name = st.session_state.document_filename or "contract"
    # Clean file name for download
    safe_name = "".join(c for c in doc_base_name if c.isalnum() or c in ("-", "_")).strip()
    if not safe_name:
        safe_name = "LegalLens_Audit"

    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        # 1. Standalone Interactive Visual HTML Report (with Print-to-PDF styles)
        html_report_str = generate_interactive_html_report(report, filename=doc_base_name)
        st.download_button(
            label="🌐 Download Interactive Visual Report (.html / Printable PDF)",
            data=html_report_str,
            file_name=f"LegalLens_Report_{safe_name}.html",
            mime="text/html",
            help="Opens directly in Chrome/Edge/Firefox with colored cards, interactive risk filters, and a 1-click Print to PDF feature.",
            use_container_width=True
        )

    with exp_col2:
        # 2. Formatted Microsoft Word Compatible Document (.doc)
        word_report_str = generate_word_friendly_doc(report, filename=doc_base_name)
        st.download_button(
            label="📄 Download Formatted Word Document (.doc)",
            data=word_report_str,
            file_name=f"LegalLens_Report_{safe_name}.doc",
            mime="application/msword",
            help="Opens natively in Microsoft Word, Google Docs, or LibreOffice with structured tables and styled risk boxes.",
            use_container_width=True
        )

    with st.expander("🛠️ Advanced & Developer Formats (Markdown & JSON)", expanded=False):
        dev_col1, dev_col2 = st.columns(2)
        with dev_col1:
            md_lines = [
                f"# LegalLens Safety Report: {report.document_title}",
                f"**Safety Score:** {report.overall_risk_score}/100",
                f"**Verdict:** {verdict_title}\n",
                "## Summary in Plain English",
                f"{report.executive_summary}\n",
                "## Negotiation Message to Send",
                f"{getattr(report, 'negotiation_email_draft', '')}\n",
                "## Top Recommendations",
                "\n".join([f"- {r}" for r in report.key_strategic_recommendations]),
                "\n## Clause by Clause Breakdown",
            ]
            for c in report.audited_clauses:
                md_lines.append(f"\n### [{c.risk_tier}] {c.clause_title}")
                md_lines.append(f"**What it means:** {c.plain_english_explanation}")
                md_lines.append(f"**The Problem:** {', '.join(c.flagged_issues)}")
                md_lines.append(f"**What to ask for:** {c.suggested_redline}")

            md_report_str = "\n".join(md_lines)
            st.download_button(
                label="📝 Download Plain Markdown (.md)",
                data=md_report_str,
                file_name=f"LegalLens_Report_{safe_name}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with dev_col2:
            json_report_str = report.model_dump_json(indent=2)
            st.download_button(
                label="⚙️ Download Technical Data (JSON)",
                data=json_report_str,
                file_name=f"LegalLens_Data_{safe_name}.json",
                mime="application/json",
                use_container_width=True
            )
