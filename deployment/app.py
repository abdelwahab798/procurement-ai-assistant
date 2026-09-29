import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

import streamlit as st
from src.QA_rag import ask_ploicy, request_validation
from src.csv_response import get_known_requesters,get_requester_name,prs_for_specfic_requester,get_all_pr_codes

import streamlit as st

st.set_page_config(
    page_title="Procurement AI Assistant",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# Global Styling (theme-aware: works on light AND dark mode)
# ============================================================
st.markdown(
    """
    <style>
        html, body, [class*="css"]  {
            font-family: 'Segoe UI', 'Inter', sans-serif;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 800px;
        }

        /* ---------- Header banner ---------- */
        .app-header {
            text-align: center;
            padding: 1.6rem 1rem;
            background: linear-gradient(135deg, #1f4e79 0%, #2e7ab5 100%);
            border-radius: 16px;
            margin-bottom: 1.6rem;
            box-shadow: 0 4px 14px rgba(0,0,0,0.25);
        }
        .app-header h1 {
            color: #ffffff !important;
            font-size: 1.9rem;
            margin-bottom: 0.2rem;
        }
        .app-header p {
            color: #dce9f5;
            font-size: 0.95rem;
            margin: 0;
        }

        /* ---------- Native container "cards" ---------- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 14px !important;
            padding: 0.4rem 0.2rem;
            margin-bottom: 1.1rem;
        }

        .section-title {
            font-weight: 700;
            font-size: 1.05rem;
            color: #3b8ae0;
            margin-bottom: 0.7rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* ---------- Buttons ---------- */
        div.stButton > button {
            width: 100%;
            border-radius: 10px;
            padding: 0.6rem 1rem;
            font-weight: 600;
            border: none;
            background: linear-gradient(135deg, #1f4e79 0%, #2e7ab5 100%);
            color: white !important;
            transition: 0.2s ease-in-out;
        }
        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(31,78,121,0.45);
        }
        div.stButton > button p {
            color: white !important;
        }

        /* ---------- Answer / highlighted text block ---------- */
        .answer-box {
            background-color: rgba(59, 138, 224, 0.12);
            border-left: 4px solid #3b8ae0;
            padding: 1rem 1.2rem;
            border-radius: 8px;
            margin-top: 0.4rem;
            color: inherit;
        }

        /* ---------- Metrics: transparent overlay so text stays visible on any theme ---------- */
        div[data-testid="stMetric"] {
            background-color: rgba(120, 120, 120, 0.08);
            border-radius: 12px;
            padding: 0.7rem 0.6rem;
            border: 1px solid rgba(120, 120, 120, 0.25);
        }
        div[data-testid="stMetricValue"] {
            color: inherit !important;
        }

        /* ---------- Divider ---------- */
        hr {
            margin: 1.4rem 0;
            border: none;
            border-top: 1px solid rgba(120, 120, 120, 0.25);
        }

        /* ---------- Badges (Request ID chip etc.) ---------- */
        .pr-badge {
            display: inline-block;
            background-color: rgba(59, 138, 224, 0.15);
            color: #3b8ae0;
            border: 1px solid rgba(59, 138, 224, 0.35);
            padding: 0.15rem 0.6rem;
            border-radius: 8px;
            font-family: monospace;
            font-size: 0.95rem;
            margin-left: 0.4rem;
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
        <p>Demo · Role-based Procurement RAG Assistant</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 1) Role Selection
# ============================================================
with st.container(border=True):
    st.markdown('<div class="section-title"> 1. Select Your Role</div>', unsafe_allow_html=True)

    role_display = st.radio(
        "Role",
        options=["Requester", "Procurement Officer"],
        horizontal=True,
        label_visibility="collapsed",
    )
    role = "requester" if role_display == "Requester" else "officer"

    requester_df = None
    requester_name = None

    if role == "requester":
        known_names = get_known_requesters()

        if known_names:
            requester_name = st.selectbox(
                "Select or search your name from matched list",
                options=known_names,
                key="requester_name_select",
            )
        else:
            st.warning("No matching names found. Please check spelling or contact admin.")

        if requester_name:
            requester_df = get_requester_name(requester_name)
            requester_df.columns.str.strip()
            PR_IDS=prs_for_specfic_requester(requester_df)
    else:
        st.success("Procurement Officer Mode: You can view all documents and purchase requests.")

# ============================================================
# 2) Action Selector
# ============================================================
with st.container(border=True):
    st.markdown('<div class="section-title"> 2. Select Action</div>', unsafe_allow_html=True)

    mode = st.radio(
        "Mode",
        options=["Policy Q&A", "Validate Purchase Request"],
        label_visibility="collapsed",
    )

# ============================================================
# Screen A: Policy Q&A (RAG)
# ============================================================
if mode == "Policy Q&A":
    with st.container(border=True):
        st.markdown('<div class="section-title"> Policy Q&A</div>', unsafe_allow_html=True)

        query_input = st.text_area(
            "Enter your question",
            placeholder="Example: What documents are required to onboard a new vendor?",
            key="query_input",
        )
        ask_btn = st.button("Ask", type="primary")

        if ask_btn:
            if not query_input.strip():
                st.warning("Please type your question.")
            else:
                with st.spinner("Searching and generating response..."):
                    try:
                        result = ask_ploicy(role=role,query=query_input)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                        result = None

                if result:
                    st.markdown("####  Answer")
                    st.markdown(f'<div class="answer-box">{result.get("answer", "-")}</div>', unsafe_allow_html=True)

                    risk = result.get("risk_level")
                    if risk:
                        risk_color = {None:"","Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(risk, "")
                        st.markdown(f"**Risk Level:** {risk_color} {risk}")

                    sources = result.get("source_documents") or []
                    if sources:
                        st.markdown("** Source Documents:**")
                        for s in sources:
                            st.markdown(f"- {s}")

                    missing_info = result.get("missing_information") or []
                    if missing_info:
                        st.markdown("** Missing Information:**")
                        for m in missing_info:
                            st.markdown(f"- {m}")

                    st.markdown("** Recommended Next Action:**")
                    st.info(result.get("recommended_next_action", "-"))

                    with st.expander(" View Full JSON (Developer Mode)"):
                        st.json(result)

# ============================================================
# Screen B: Validate Purchase Request
# ============================================================
else:
    with st.container(border=True):
        st.markdown('<div class="section-title"> Validate Purchase Request</div>', unsafe_allow_html=True)

        if role == "requester":
            if requester_name is None:
                st.warning("Please select your name above first.")
                available_codes = []
            elif requester_df is not None and len(requester_df) == 0:
                st.warning(f"No purchase requests found for '{requester_name}'.")
                available_codes = []
            else:
                available_codes = PR_IDS
        else:
            available_codes = get_all_pr_codes()

        if available_codes:
            # Streamlit's selectbox supports typing directly into it to filter items
            pr_code = st.selectbox(
                "Select or type Request ID to filter",
                options=available_codes,
                format_func=lambda c: f"{c}",
                key="pr_code_select")
            query_input = st.text_area(
            "Enter your question",
            placeholder="Example: What documents are required to onboard a new vendor?",
            key="query_input",
        )
            check_btn = st.button("Validate Request", type="primary")

            if check_btn:
                with st.spinner("Validating request..."):
                    try:
                        result = request_validation(
                            role=role,
                            query=query_input,
                            pr_id=pr_code)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                        result = None

                if result:
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        status_icon = "✅" if result.get("is_complete") else "⚠️"
                        st.markdown(
                            f'#### {status_icon} Result for Request '
                            f'<span class="pr-badge">{result.get("pr_id", pr_code)}</span>',
                            unsafe_allow_html=True,
                        )

                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric("Is Complete?", "Yes" if result.get("is_complete") else "No")
                        with c2:
                            st.metric("Required Approval Level", result.get("required_approval_level", "-"))

                        missing = result.get("missing_fields") or []
                        if missing:
                            st.markdown("** Missing Fields:**")
                            for m in missing:
                                st.markdown(f"- {m}")

                        violations = result.get("policy_violations") or []
                        if violations:
                            st.markdown("** Policy Violations:**")
                            for v in violations:
                                st.markdown(f"- {v}")

                        st.markdown("** Recommended Action:**")
                        st.info(result.get("recommended_action", "-"))

                        with st.expander(" View Full JSON (Developer Mode)"):
                            st.json(result)