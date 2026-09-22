from src.ploicy_role import get_open_ai_client,search_ploicy_user,format_chunks_for_llm


SYSTEM_PROMPT="""You are a procurement assistant. Answer questions using only the provided procurement policy, vendor onboarding guide, purchase request guidelines, supplier code of conduct, vendor documents, and purchase request dataset. If information is missing, say what is missing and recommend the next procurement action. Do not approve requests by yourself. Always identify the source document or data field used.
"""

def ask_rag(role:str,query:str):
    chunks=search_ploicy_user(role=role,query=query,topk=5)
    context=format_chunks_for_llm(chunks)
    open_ai_cliet=get_open_ai_client()

    user_prompt=f""" user question: {query}
    context_text: """

