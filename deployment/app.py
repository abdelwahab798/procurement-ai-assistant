import sys
import time
from pathlib import Path

# ============================================================
# Path Setup
# ============================================================
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

import streamlit as st
from src.QA_rag import ask_ploicy, request_validation, summarize_for_officer
from src.csv_response import (
    get_known_requesters,
    get_requester_name,
    prs_for_specfic_requester,
    get_all_pr_codes,
)

# ============================================================
# Page Configuration
# ============================================================
st.set_page_config(
    page_title="Procurement AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Global Styling
# ============================================================
st.markdown(
    """
    <style>
        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 980px;
        }

        /* ---------- Header ---------- */
        .app-header {
            text-align: center;
            padding: 2.2rem 1.5rem;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 18px;
            margin-bottom: 1.8rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15);
        }
        .app-header h1 {
            color: #f8fafc !important;
            font-size: 2.1rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 0.35rem;
        }
        .app-header p { color: #94a3b8; font-size: 0.98rem; margin: 0; }
        .app-header .badge {
            display: inline-block;
            margin-top: 0.7rem;
            padding: 0.25rem 0.8rem;
            border-radius: 999px;
            background: rgba(14, 165, 233, 0.15);
            color: #38bdf8;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.03em;
        }

        /* ---------- Cards ---------- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 16px !important;
            border: 1px solid rgba(226, 232, 240, 0.9) !important;
            box-shadow: 0 1px 4px 0 rgba(0, 0, 0, 0.05) !important;
            padding: 0.6rem 0.3rem;
            margin-bottom: 1.2rem;
        }
        .section-title {
            font-weight: 650;
            font-size: 1.05rem;
            color: #2563eb;
            margin-bottom: 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* ---------- Buttons ---------- */
        div.stButton > button {
            width: 100%;
            border-radius: 10px;
            padding: 0.55rem 1rem;
            font-weight: 600;
            border: none;
            transition: all 0.2s ease-in-out;
        }
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white !important;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.25);
        }
        div.stButton > button[kind="primary"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 14px -2px rgba(37, 99, 235, 0.4);
        }
        div.stButton > button[kind="secondary"] {
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
            color: white !important;
            box-shadow: 0 4px 6px -1px rgba(14, 165, 233, 0.25);
        }
        div.stButton > button[kind="secondary"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 14px rgba(14, 165, 233, 0.45);
        }

        /* ---------- Answer box ---------- */
        .answer-box {
            background-color: rgba(37, 99, 235, 0.05);
            border-left: 4px solid #2563eb;
            padding: 1rem 1.2rem;
            border-radius: 10px;
            margin-top: 0.5rem;
            font-size: 0.98rem;
            line-height: 1.65;
            animation: fadeIn 0.35s ease-in;
        }
        .headline-card {
            background: rgba(37, 99, 235, 0.06);
            border: 1px solid rgba(37, 99, 235, 0.2);
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            margin-bottom: 1.3rem;
            animation: fadeIn 0.35s ease-in;
        }
        .headline-card h3 { margin: 0; font-size: 1.15rem; color: #1e40af; font-weight: 700; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* ---------- Sidebar polish ---------- */
        section[data-testid="stSidebar"] {
            background: #f8fafc;
            border-right: 1px solid rgba(226, 232, 240, 0.9);
        }
        /* Force readable text color inside the sidebar regardless of the
           browser/system theme — prevents white-on-white invisible labels. */
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
            color: #0f172a !important;
        }
        .sidebar-title { font-weight: 700; font-size: 1.05rem; color: #0f172a !important; margin-bottom: 0.3rem; }
        .sidebar-caption { color: #64748b !important; font-size: 0.85rem; margin-bottom: 1.2rem; }

        .summary-glow textarea {
            border: 2px solid #0ea5e9 !important;
            box-shadow: 0 0 16px rgba(14, 165, 233, 0.35) !important;
            background-color: rgba(14, 165, 233, 0.02) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Header
# ============================================================
st.markdown(
    """
    <div class="app-header">
        <h1>Procurement AI Assistant</h1>
        <p>Enterprise Role-Based Governance & Policy Copilot</p>
        <span class="badge">RAG + Grounded Validation • Azure OpenAI</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Sidebar — Role & Identity
# ============================================================
with st.sidebar:
    st.markdown('<div class="sidebar-title"> Who are you?</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-caption">This controls what the assistant can see and do.</div>', unsafe_allow_html=True)

    role_display = st.radio(
        "Role", options=["Requester", "Procurement Officer"], label_visibility="collapsed",
    )
    role = "requester" if role_display == "Requester" else "officer"

    requester_df = None
    requester_name = None
    PR_IDS = []

    if role == "requester":
        known_names = get_known_requesters()
        if known_names:
            requester_name = st.selectbox("Your name", options=known_names, key="requester_name_select")
        else:
            st.warning("No matching names found. Please check spelling or contact admin.")

        if requester_name:
            requester_df = get_requester_name(requester_name)
            if requester_df is not None:
                requester_df.columns = requester_df.columns.str.strip()
                PR_IDS = prs_for_specfic_requester(requester_df)
        st.caption("You can only see and check your own requests.")
    else:
        st.success("Full access: all requests, policies, and summary tools.")

    st.divider()
    st.caption("Procurement AI Assistant · BBI Consultancy")

# ============================================================
# Main content — tabs
# ============================================================
tab_policy, tab_requests = st.tabs([" Policy Q&A", " Purchase Requests"])

# ------------------------------------------------------------
# Tab 1: Policy Q&A (RAG)
# ------------------------------------------------------------
with tab_policy:
    with st.container(border=True):
        st.markdown('<div class="section-title"> Ask about procurement policy</div>', unsafe_allow_html=True)

        query_input = st.text_area(
            "Enter your question",
            placeholder="Example: What documents are required to onboard a new vendor?",
            key="query_input_policy",
            label_visibility="collapsed",
        )
        ask_btn = st.button("Ask Assistant", type="primary", key="ask_policy_btn")

        if ask_btn:
            if not query_input.strip():
                st.warning("Please enter a question first.")
            else:
                result = None
                with st.status("Working on your question...", expanded=True) as status:
                    st.write("🔍 Searching the knowledge base...")
                    try:
                        result = ask_ploicy(role=role, query=query_input)
                        st.write(" Drafting a grounded answer...")
                        time.sleep(0.2)  # brief pause so the step is visible, not a real delay
                        status.update(label="Done", state="complete", expanded=False)
                    except Exception as e:
                        status.update(label="Something went wrong", state="error", expanded=True)
                        st.error(f"An error occurred: {e}")

                if result:
                    st.markdown("#### Answer")
                    st.markdown(f'<div class="answer-box">{result.get("answer", "-")}</div>', unsafe_allow_html=True)

                    risk = result.get("risk_level")
                    if risk:
                        risk_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(risk, "⚪")
                        st.markdown(f"**Risk Level:** {risk_color} {risk}")

                    sources = result.get("source_documents") or []
                    if sources:
                        st.markdown("**Source Documents:**")
                        st.markdown(" ".join(f"`{s}`" for s in sources))

                    missing_info = result.get("missing_information") or []
                    if missing_info:
                        st.markdown("**Missing Information:**")
                        for m in missing_info:
                            st.markdown(f"- {m}")

                    st.markdown("**Recommended Next Action:**")
                    st.info(result.get("recommended_next_action", "-"))

                    with st.expander("🛠️ View Full JSON (Developer Mode)"):
                        st.json(result)

# ------------------------------------------------------------
# Tab 2: Purchase Requests (Validate / Summarize)
# ------------------------------------------------------------
with tab_requests:
    with st.container(border=True):
        st.markdown('<div class="section-title"> Purchase Requests</div>', unsafe_allow_html=True)

        if role == "requester":
            if requester_name is None:
                st.warning("Please select your name in the sidebar first.")
                available_codes = []
            elif requester_df is not None and len(requester_df) == 0:
                st.warning(f"No purchase requests found for '{requester_name}'.")
                available_codes = []
            else:
                available_codes = PR_IDS
        else:
            available_codes = get_all_pr_codes()

        if not available_codes:
            st.stop()

        action = "Validate a request"
        pr_code = None

        if role == "officer":
            col_select, col_action = st.columns([2.2, 1.6])
            with col_select:
                pr_code = st.selectbox(
                    "Select or type Request ID", options=available_codes,
                    format_func=lambda c: f"{c}", key="pr_code_select",
                )
            with col_action:
                action = st.radio(
                    "Action", options=["Validate a request", "Summarize all requests"],
                    horizontal=False, key="officer_action",
                )
        else:
            pr_code = st.selectbox(
                "Select or type Request ID", options=available_codes,
                format_func=lambda c: f"{c}", key="pr_code_select",
            )

        is_summary_mode = action == "Summarize all requests"
        placeholder_txt = (
            "Example: Summarize status breakdown, top compliance issues, and actions..."
            if is_summary_mode
            else "Example: Check if vendor compliance documents are complete..."
        )

        if is_summary_mode:
            st.markdown('<div class="summary-glow">', unsafe_allow_html=True)
        query_input = st.text_area(
            "Enter your question", placeholder=placeholder_txt,
            key="query_input_val", label_visibility="collapsed",
        )
        if is_summary_mode:
            st.markdown("</div>", unsafe_allow_html=True)

        check_btn = st.button("Ask", type="primary", key="ask_requests_btn")

        if check_btn:
            if not query_input.strip():
                st.warning("Please enter your question first.")
            elif is_summary_mode:
                # ---------------- Summary ----------------
                result = None
                with st.status("Building the summary...", expanded=True) as status:
                    st.write("📊 Reading the full purchase request dataset...")
                    try:
                        result = summarize_for_officer(role=role, query=query_input)
                        st.write(" Computing status and issue breakdowns...")
                        time.sleep(0.2)
                        status.update(label="Summary ready", state="complete", expanded=False)
                    except Exception as e:
                        status.update(label="Something went wrong", state="error", expanded=True)
                        st.error(f"An error occurred: {e}")

                if result:
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        if result.get("headline"):
                            st.markdown(
                                f'<div class="headline-card"><h3> {result.get("headline")}</h3></div>',
                                unsafe_allow_html=True,
                            )

                        m1, m2 = st.columns(2)
                        with m1:
                            st.metric("Total Requests", result.get("total_requests", 0))
                        with m2:
                            missing_count = result.get("missing_info_count", 0)
                            st.metric(
                                "Missing Info Count", missing_count,
                                delta=None if missing_count == 0 else f"-{missing_count}",
                                delta_color="inverse",
                            )

                        col_status, col_issues = st.columns(2)
                        with col_status:
                            st.markdown("#####  Status Breakdown")
                            status_data = result.get("status_breakdown", [])
                            if status_data:
                                st.dataframe(status_data, use_container_width=True, hide_index=True)
                            else:
                                st.caption("No status breakdown data available.")
                        with col_issues:
                            st.markdown("##### Top Issues")
                            issues_data = result.get("top_issues", [])
                            if issues_data:
                                st.dataframe(issues_data, use_container_width=True, hide_index=True)
                            else:
                                st.caption("No issues found.")

                        insights = result.get("key_insights", [])
                        if insights:
                            st.markdown("#####  Key Insights")
                            for insight in insights:
                                st.markdown(f"- {insight}")

                        actions = result.get("recommended_actions", [])
                        if actions:
                            st.markdown("#####  Recommended Actions")
                            for act in actions:
                                st.success(f" {act}")

                        with st.expander(" View Full JSON (Developer Mode)"):
                            st.json(result)

            else:
                # ---------------- Validation ----------------
                result = None
                with st.status(f"Validating {pr_code}...", expanded=True) as status:
                    st.write(" Looking up the request...")
                    try:
                        result = request_validation(role=role, query=query_input, pr_id=pr_code)
                        st.write(" Checking against procurement policy...")
                        time.sleep(0.2)
                        status.update(label="Validation complete", state="complete", expanded=False)
                    except Exception as e:
                        status.update(label="Something went wrong", state="error", expanded=True)
                        st.error(f"An error occurred: {e}")

                if result:
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        status_icon = "" if result.get("is_complete") else ""
                        st.markdown(f'#### {status_icon} Result for `{result.get("pr_id", pr_code)}`')

                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric("Is Complete?", "Yes" if result.get("is_complete") else "No")
                        with c2:
                            st.metric("Required Approval Level", result.get("required_approval_level", "-"))

                        missing = result.get("missing_fields") or []
                        if missing:
                            st.markdown("**Missing Fields:**")
                            for m in missing:
                                st.markdown(f"- {m}")

                        violations = result.get("policy_violations") or []
                        if violations:
                            st.markdown("**Policy Violations:**")
                            for v in violations:
                                st.markdown(f"- {v}")

                        st.markdown("**Recommended Action:**")
                        st.info(result.get("recommended_action", "-"))

                        with st.expander(" View Full JSON (Developer Mode)"):
                            st.json(result)