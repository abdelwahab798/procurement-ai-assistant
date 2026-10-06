from ploicy_role import search_ploicy_user,format_chunks_for_llm
from llm_ulits import call_llm_with_schema
from all_schemas import PROCUREMENT_ASSISTANT_RESPONSE_SCHEMA,PURCHASE_REQUEST_VALIDATION_SCHEMA
from csv_response import get_pr_by_id,format_pr_for_llm
from system_prmpts import Requester_ASK_POLICY_SYSTEM_PROMPT,VALIDATE_PR_SYSTEM_PROMPT



def rqeuster_ask_ploicy(role:str,query:str):
    chunks=search_ploicy_user(role=role,query=query,topk=5)
    context=format_chunks_for_llm(chunks)

    user_prompt=f""" user role: {role} user question: {query}
    context_text from documents: {context} """

    result=call_llm_with_schema(system_prompt=Requester_ASK_POLICY_SYSTEM_PROMPT,user_prompt=user_prompt,schema=PROCUREMENT_ASSISTANT_RESPONSE_SCHEMA,schema_name="procurement_assistant_response",max_completion_tokens=128000)
    return result

def request_validation(role:str,query:str,pr_id:str):
    chunks=search_ploicy_user(role=role,query=query,topk=5)
    context=format_chunks_for_llm(chunks)
    pr_record=get_pr_by_id(pr_id)
    pr_format=format_pr_for_llm(pr_record)

    user_prompt=f""" user role {role},PR will valdation is {pr_id}, colums: {pr_format},context{context},
    Requirement: Verify the completeness of the request; determine the required approval level based on policy; and identify missing fields, any policy violations, and the recommended action."""

    result=call_llm_with_schema(system_prompt=VALIDATE_PR_SYSTEM_PROMPT,user_prompt=user_prompt,schema=PURCHASE_REQUEST_VALIDATION_SCHEMA,schema_name="PURCHASE_REQUEST_VALIDATION",max_completion_tokens=128000)
    return result
