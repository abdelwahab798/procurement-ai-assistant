from ploicy_role import get_open_ai_client,search_ploicy_user,format_chunks_for_llm
from llm_ulits import call_llm_with_schema
from all_schemas import PROCUREMENT_ASSISTANT_RESPONSE_SCHEMA,PURCHASE_REQUEST_VALIDATION_SCHEMA
from csv_response import get_pr_by_id,format_pr_for_llm


SYSTEM_PROMPT="""You are a procurement assistant. Answer questions using only the provided
procurement policy, vendor onboarding guide, purchase request guidelines, supplier code of
conduct, vendor documents, and purchase request dataset. If information is missing, say what
is missing and recommend the next procurement action. Do not approve requests by yourself.
Always identify the source document or data field used.
 
If the user asks a general policy question without specifying a particular vendor/request
record, set risk_level to null and missing_information to an empty array [] (the fields must
still appear in the JSON output, since the schema requires them - just use null/empty values,
do not fabricate a risk level or missing items for general informational questions).
STRICT GROUNDING RULE: Never introduce a requirement, document, field, or risk that is not
explicitly present in the provided context, even as a "commonly required" or "best practice"
suggestion. If the context does not fully answer the question, say so explicitly instead of
supplementing with outside knowledge - even if you label it as an assumption.
OUTPUT FORMATTING RULE: Keep each item in source_documents as a short plain filename only
(e.g. "Procurement_Policy.pdf"), with no embedded citations or parenthetical notes. Put any
citation detail, quotes, or field references as plain sentences inside the "answer" field
instead of inside array items, If the answer would contain more than 6-7 distinct points, summarize it to the 
most important 5-6 points instead of listing everything exhaustively."
"""

def ask_ploicy(role:str,query:str):
    chunks=search_ploicy_user(role=role,query=query,topk=5)
    context=format_chunks_for_llm(chunks)
    open_ai_cliet=get_open_ai_client()

    user_prompt=f""" user question: {query}
    context_text from documents: {context} """

    result=call_llm_with_schema(system_prompt=SYSTEM_PROMPT,user_prompt=user_prompt,schema=PROCUREMENT_ASSISTANT_RESPONSE_SCHEMA,schema_name="procurement_assistant_response",max_completion_tokens=128000)
    return result

def request_validation(role:str,query:str,pr_id:str):
    chunks=search_ploicy_user(role=role,query=query,topk=5)
    context=format_chunks_for_llm(chunks)
    pr_record=get_pr_by_id(pr_id)
    pr_format=format_pr_for_llm(pr_record)

    user_prompt=f"""PR will valdation is {pr_id}, colums: {pr_format},context{context},
    Requirement: Verify the completeness of the request; determine the required approval level based on policy; and identify missing fields, any policy violations, and the recommended action."""

    result=call_llm_with_schema(system_prompt=SYSTEM_PROMPT,user_prompt=user_prompt,schema=PURCHASE_REQUEST_VALIDATION_SCHEMA,schema_name="PURCHASE_REQUEST_VALIDATION",max_completion_tokens=128000)
    return result

if __name__=="__main__":
    question=input("please enter your question: ")
    role=input("please enter your role: ")
    pr_id=input("please enter your pr_id: ")


    result=request_validation(role=role,query=question,pr_id=pr_id)
    print(result)





