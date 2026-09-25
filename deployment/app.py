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

st.set_page_config(page_title="Procurement AI Assistant", page_icon="📋", layout="centered")

st.title("📋 Procurement AI Assistant")
st.caption("Demo - Role-based Procurement RAG Assistant")

# ============================================================
# 1) Role Selection
# ============================================================
st.subheader("1. Select Your Role")
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
    st.info("Requester Mode: You can only view general public documents and your own personal requests.")

    # 1. Get all known requesters
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

st.divider()

# ============================================================
# 2) Action Selector
# ============================================================
st.subheader("2. Select Action")
mode = st.radio(
    "Mode",
    options=["Policy Q&A", "Validate Purchase Request"],
    label_visibility="collapsed",
)

st.divider()

# ============================================================
# Screen A: Policy Q&A (RAG)
# ============================================================
if mode == "Policy Q&A":
    st.subheader("Policy Q&A")

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
                st.markdown("### Answer")
                st.write(result.get("answer", "-"))

                risk = result.get("risk_level")
                if risk:
                    risk_color = {None:"","Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(risk, "")
                    st.markdown(f"**Risk Level:** {risk_color} {risk}")

                sources = result.get("source_documents") or []
                if sources:
                    st.markdown("**Source Documents:**")
                    for s in sources:
                        st.markdown(f"- {s}")

                missing_info = result.get("missing_information") or []
                if missing_info:
                    st.markdown("**Missing Information:**")
                    for m in missing_info:
                        st.markdown(f"- {m}")

                st.markdown("**Recommended Next Action:**")
                st.info(result.get("recommended_next_action", "-"))

                with st.expander("View Full JSON (Developer Mode)"):
                    st.json(result)

# ============================================================
# Screen B: Validate Purchase Request
# ============================================================
else:
    st.subheader("Validate Purchase Request")

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
                    st.markdown(f"### {status_icon} Result for Request `{result.get('pr_id', pr_code)}`")

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

                    with st.expander("View Full JSON (Developer Mode)"):
                        st.json(result)