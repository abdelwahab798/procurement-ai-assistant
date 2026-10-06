import sys
import time
import base64
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
from Req_QA_rag import rqeuster_ask_ploicy, request_validation_reqeuster
from Office_QA_rag import officer_ask_ploicy, summarize_for_officer,request_validation_officer
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
    page_title="Procurement AI Assistant | BBI Consultancy",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Logo Helper
# ============================================================
_LOGO_PATH = Path(__file__).resolve().parent / "bbi_logo.png"


def _logo_b64() -> str:
    if _LOGO_PATH.exists():
        return base64.b64encode(_LOGO_PATH.read_bytes()).decode()
    return ""


LOGO_B64 = _logo_b64()

# ============================================================
# Brand Tokens — Professional Corporate Theme
# ============================================================
NAVY = "#1E3A52"
NAVY_DARK = "#142A3B"
GREEN = "#5FB347"
GREEN_SOFT = "rgba(95, 179, 71, 0.12)"
INK = "#1A2332"
MUTED = "#5B6B79"
BORDER = "rgba(30, 58, 82, 0.12)"

# ============================================================
# Global Custom CSS
# ============================================================
st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Main Dark Theme Colors */
        :root {{
            --bg-color: #0B101D;
            --sidebar-bg: #111827;
            --card-bg: #101928;
            --border-color: #1E293B;
            --accent-green: #22C55E;
            --header-bg: #0B2B47;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
        }}

        /* Global Canvas Background */
        .stApp {{
            background-color: var(--bg-color) !important;
            color: var(--text-main) !important;
            font-family: 'Inter', -apple-system, sans-serif;
        }}

        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1150px;
        }}

        /* Header Banner Styling */
        .app-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1.25rem 2rem;
            background: linear-gradient(90deg, #09253F 0%, #0D3B62 100%);
            border-radius: 12px;
            margin-bottom: 2rem;
            border: 1px solid #1E3A5F;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        }}
        .header-left {{
            display: flex;
            align-items: center;
            gap: 1.2rem;
        }}
        .header-logo-box {{
            width: 44px;
            height: 44px;
            background: #ffffff;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 4px;
        }}
        .header-logo-box img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
        .header-title-box h1 {{
            color: #FFFFFF !important;
            font-size: 1.7rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.01em;
        }}
        .header-title-box p {{
            color: #94A3B8;
            font-size: 0.9rem;
            margin: 0.15rem 0 0 0;
        }}
        .header-badge {{
            background-color: #15803D;
            color: #FFFFFF;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 0.35rem 0.85rem;
            border-radius: 6px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}

        /* Custom Section Titles with Green Vertical Accent */
        .section-title-container {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 1.2rem;
        }}
        .green-accent-bar {{
            width: 4px;
            height: 22px;
            background-color: var(--accent-green);
            border-radius: 2px;
        }}
        .section-title-text {{
            font-size: 1.2rem;
            font-weight: 700;
            color: #FFFFFF;
        }}

        /* Container Card Box */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 12px !important;
            border: 1px solid var(--border-color) !important;
            background-color: var(--card-bg) !important;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}

        /* Inputs & Text Area Dark Theme */
        textarea, select, input, div[data-baseweb="select"] > div {{
            background-color: #1A2436 !important;
            color: #FFFFFF !important;
            border: 1px solid #2B3950 !important;
            border-radius: 8px !important;
        }}
        textarea:focus, input:focus {{
            border-color: var(--accent-green) !important;
            box-shadow: 0 0 0 1px var(--accent-green) !important;
        }}

        /* Change Streamlit Radio Button Red Color to Green */
        div[data-testid="stRadio"] div[role="radiogroup"] label div[aria-checked="true"] {{
            background-color: var(--accent-green) !important;
            border-color: var(--accent-green) !important;
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] label div[aria-checked="true"] > div {{
            background-color: var(--accent-green) !important;
        }}
        div[data-testid="stRadio"] label span {{
            color: #F8FAFC !important;
            font-size: 0.95rem;
            font-weight: 500;
        }}
        div[data-testid="stRadio"] div[aria-checked="true"] {{
            border-color: var(--accent-green) !important;
        }}

        /* Custom Button Styling */
        div.stButton > button {{
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            border: 1px solid var(--accent-green) !important;
            background-color: transparent !important;
            color: #FFFFFF !important;
            transition: all 0.2s ease-in-out;
            float: right;
        }}
        div.stButton > button:hover {{
            background-color: var(--accent-green) !important;
            color: #000000 !important;
        }}

        /* Tabs Styling */
        button[data-baseweb="tab"] {{
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
            padding-bottom: 0.75rem !important;
            border-bottom: 2px solid transparent !important;
        }}
        button[aria-selected="true"] {{
            color: var(--accent-green) !important;
            border-bottom: 2px solid var(--accent-green) !important;
            background: transparent !important;
        }}

        /* Sidebar Customization */
        section[data-testid="stSidebar"] {{
            background-color: var(--sidebar-bg) !important;
            border-right: 1px solid var(--border-color);
        }}
        .sidebar-brand-box {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
        }}
        .sidebar-logo-img {{
            width: 42px;
            height: 42px;
            border-radius: 8px;
            background: #ffffff;
            padding: 4px;
            object-fit: contain;
        }}
        .sidebar-brand-text {{
            font-size: 1.1rem;
            font-weight: 700;
            color: #FFFFFF;
        }}
        .sidebar-heading {{
            font-weight: 600;
            font-size: 0.95rem;
            color: #CBD5E1;
            margin-bottom: 0.5rem;
        }}

        /* Output / Answer Box */
        .answer-box {{
            background-color: #162032;
            border-left: 4px solid var(--accent-green);
            padding: 1.2rem;
            border-radius: 8px;
            margin-top: 1rem;
            color: #E2E8F0;
            line-height: 1.6;
            
        }}

        /* Badges & Metrics */
        .status-badge {{
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
        }}
        .status-complete {{ background: #166534; color: #DCFCE7; }}
        .status-incomplete {{ background: #991B1B; color: #FEE2E2; }}
    </style>
    """,
    unsafe_allow_html=True,
)
# ============================================================
# Header Section
# ============================================================
_logo_html = (
    f'<img src="data:image/png;base64,{LOGO_B64}" alt="BBI" />' if LOGO_B64 else ""
)
st.markdown(
    f"""
    <div class="app-header">
        <div class="header-left">
            {"<div class='header-logo-box'>" + _logo_html + "</div>" if LOGO_B64 else ""}
            <div class="header-title-box">
                <h1>Procurement AI Assistant</h1>
                <p>Enterprise Role-Based Governance & Policy Copilot</p>
            </div>
        </div>
        <div class="header-badge">
            RAG + GROUNDED VALIDATION · AZURE OPENAI
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Sidebar Section — Role & Identity
# ============================================================
with st.sidebar:
    if LOGO_B64:
        st.markdown(
            f"""
            <div class="sidebar-brand-box">
                <img src="data:image/png;base64,{LOGO_B64}" class="sidebar-logo-img" alt="BBI Logo"/>
                <span class="sidebar-brand-text">BBI Consultancy</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="sidebar-brand-box">
                <span class="sidebar-brand-text">BBI Consultancy</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="sidebar-heading">Who are you?</div>', unsafe_allow_html=True)

    role_display = st.radio(
        "Role", options=["Requester", "Procurement Officer"], label_visibility="collapsed"
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
    st.caption("Procurement AI Assistant · BBI Consultancy & AI Solutions")

# ============================================================
# Main Content — Tabs
# ============================================================
tab_policy, tab_requests = st.tabs(["Policy Q&A", "Purchase Requests"])

# ------------------------------------------------------------
# Tab 1: Policy Q&A (RAG)
# ------------------------------------------------------------
with tab_policy:
    with st.container(border=True):
        st.markdown('<div class="section-title">Ask about procurement policy</div>', unsafe_allow_html=True)

        query_input = st.text_area(
            "Enter your question",
            placeholder="Example: What documents are required to onboard a new vendor?",
            key="query_input_policy",
            label_visibility="collapsed",
            height=100,
        )
        ask_btn = st.button("Ask Assistant", type="primary", key="ask_policy_btn")

        if ask_btn:
            if not query_input.strip():
                st.warning("Please enter a question first.")
            else:
                result = None
                with st.status("Working on your question...", expanded=True) as status:
                    st.write("Searching the knowledge base...")
                    try:
                        if role == "officer":
                            result = officer_ask_ploicy(role=role, query=query_input)
                        else:
                            result = rqeuster_ask_ploicy(role=role, query=query_input)
                        st.write("Drafting a grounded answer...")
                        time.sleep(0.2)
                        status.update(label="Done", state="complete", expanded=False)
                    except Exception as e:
                        status.update(label="Something went wrong", state="error", expanded=True)
                        st.error(f"An error occurred: {e}")

                if result:
                    st.markdown("#### Answer")
                    st.markdown(f'<div class="answer-box">{result.get("answer", "-")}</div>', unsafe_allow_html=True)

                    risk = result.get("risk_level")
                    if risk:
                        risk_class = {"Low": "risk-low", "Medium": "risk-medium", "High": "risk-high"}.get(risk, "")
                        st.markdown(
                            f'<p style="margin-top:1rem;"><strong>Risk Level:</strong> '
                            f'<span class="risk-badge {risk_class}">{risk}</span></p>',
                            unsafe_allow_html=True,
                        )

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

                    with st.expander("View Full JSON (Developer Mode)"):
                        st.json(result)

# ------------------------------------------------------------
# Tab 2: Purchase Requests (Validate / Summarize)
# ------------------------------------------------------------
with tab_requests:
    with st.container(border=True):
        st.markdown('<div class="section-title">Purchase Requests</div>', unsafe_allow_html=True)

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

        if available_codes:
            action = "Validate a request"
            pr_code = None

            if role == "officer":
                col_select, col_action = st.columns([2.2, 1.6])
                with col_select:
                    pr_code = st.selectbox(
                        "Select or type Request ID",
                        options=available_codes,
                        format_func=lambda c: f"{c}",
                        key="pr_code_select",
                    )
                with col_action:
                    action = st.radio(
                        "Action",
                        options=["Validate a request", "Summarize all requests"],
                        horizontal=False,
                        key="officer_action",
                    )
            else:
                pr_code = st.selectbox(
                    "Select or type Request ID",
                    options=available_codes,
                    format_func=lambda c: f"{c}",
                    key="pr_code_select",
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
                "Enter your question",
                placeholder=placeholder_txt,
                key="query_input_val",
                label_visibility="collapsed",
                height=90,
            )
            if is_summary_mode:
                st.markdown("</div>", unsafe_allow_html=True)

            check_btn = st.button("Ask", type="primary", key="ask_requests_btn")

            if check_btn:
                if not query_input.strip():
                    st.warning("Please enter your question first.")
                elif is_summary_mode:
                    # Summary Mode
                    result = None
                    with st.status("Building the summary...", expanded=True) as status:
                        st.write("Reading the full purchase request dataset...")
                        try:
                            result = summarize_for_officer(role=role, query=query_input)
                            st.write("Computing status and issue breakdowns...")
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
                                    f'<div class="headline-card"><h3>{result.get("headline")}</h3></div>',
                                    unsafe_allow_html=True,
                                )

                            m1, m2 = st.columns(2)
                            with m1:
                                st.metric("Total Requests", result.get("total_requests", 0))
                            with m2:
                                missing_count = result.get("missing_info_count", 0)
                                st.metric(
                                    "Missing Info Count",
                                    missing_count,
                                    delta=None if missing_count == 0 else f"-{missing_count}",
                                    delta_color="inverse",
                                )

                            col_status, col_issues = st.columns(2)
                            with col_status:
                                st.markdown("##### Status Breakdown")
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
                                st.markdown("##### Key Insights")
                                for insight in insights:
                                    st.markdown(f"- {insight}")

                            actions = result.get("recommended_actions", [])
                            if actions:
                                st.markdown("##### Recommended Actions")
                                for act in actions:
                                    st.success(act)

                            with st.expander("View Full JSON (Developer Mode)"):
                                st.json(result)

                else:
                    # Validation Mode
                    result = None
                    with st.status(f"Validating {pr_code}...", expanded=True) as status:
                        st.write("Looking up the request...")
                        try:
                            if role == "officer":
                                result = request_validation_officer(role=role, query=query_input, pr_id=pr_code)
                            else:
                                result = request_validation_reqeuster(role=role, query=query_input, pr_id=pr_code)
                            st.write("Checking against procurement policy...")
                            time.sleep(0.2)
                            status.update(label="Validation complete", state="complete", expanded=False)
                        except Exception as e:
                            status.update(label="Something went wrong", state="error", expanded=True)
                            st.error(f"An error occurred: {e}")

                    if result:
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            is_complete = result.get("is_complete")
                            badge_class = "complete" if is_complete else "incomplete"
                            badge_text = "Complete" if is_complete else "Incomplete"
                            st.markdown(
                                f'#### Result for `{result.get("pr_id", pr_code)}` '
                                f'<span class="status-badge {badge_class}">{badge_text}</span>',
                                unsafe_allow_html=True,
                            )

                            c1, c2 = st.columns(2)
                            with c1:
                                st.metric("Is Complete?", "Yes" if is_complete else "No")
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

                            with st.expander("View Full JSON (Developer Mode)"):
                                st.json(result)