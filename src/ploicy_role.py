import os
from dotenv import load_dotenv
from openai import OpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

load_dotenv()
 
AZURE_SEARCH_ENDPOINT=os.environ["AZURE_SEARCH_ENDPOINT"]
AZURE_SEARCH_API_KEY=os.environ["AZURE_SEARCH_API_KEY"]
AZURE_SEARCH_INDEX_NAME=os.environ["AZURE_SEARCH_INDEX_NAME"]
 
AZURE_OPENAI_ENDPOINT=os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_API_KEY=os.environ["AZURE_OPENAI_API_KEY"]
EMBEDDING_DEPLOYMENT=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
 

ROLE_ACCESS_MAP={
    "requester": ["public"],
    "officer": ["public", "internal"]}


def get_open_ai_client():
    return OpenAI(base_url=AZURE_OPENAI_ENDPOINT,api_key=AZURE_OPENAI_API_KEY)

def get_azure_sarch_client():
    return SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(AZURE_SEARCH_API_KEY))


def embedding_quey(query:str):
    client=get_open_ai_client()
    embedded_query=client.embeddings.create(input=query,model=EMBEDDING_DEPLOYMENT)
    return embedded_query.data[0].embedding


def filter_user(role:str):
    role=role.strip().lower()
    if role not in ROLE_ACCESS_MAP:
        print(f"this role : {role} not in roles menu")
    access_level=ROLE_ACCESS_MAP[role]
    filter_expression = " or ".join([f"access_level eq '{lvl}'" for lvl in access_level])
    return filter_expression


def search_ploicy_user(role:str,query:str,topk:int=5):
    embedded_query=embedding_quey(query)
    filter_expression=filter_user(role)
    search_client=get_azure_sarch_client()

    vector_query=VectorizedQuery(vector=embedded_query,k_nearest_neighbors=topk,fields="snippet_vector")

    resutls=search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        filter=filter_expression,
        select=["snippet", "blob_url", "access_level"],
        top=topk)

    chunks=[]

    for chunk in resutls:
        chunks.append({
            "snippet":chunk["snippet"],
            "blob_url":chunk["blob_url"],
            "document_name":chunk["blob_url"].split("/")[-1] if chunk.get("blob_url") else "UnKnown",
            "access_level":chunk["access_level"]})

    return chunks

def format_chunks_for_llm(chunks: list[dict]) -> str:
    if not chunks:
        return "There is no docs"
 
    parts=[]
    for i, c in enumerate(chunks, 1):
        parts.append(f"[source {i}: {c['document_name']}]\n{c['snippet']}")
    return "\n\n".join(parts)


if __name__=="__main__":
    test_query="What documents are required to onboard a new vendor?"
    for role in ["requester", "officer"]:
        print("=" * 70)
        print(f"Role: {role}")
        print(f"Query: {test_query}")
        print("=" * 70)

        chunks=search_ploicy_user(role=role,query=test_query,topk=5)
        print(f"number of chunnks: {len(chunks)}")
        for chunk in chunks:
            print(f"  - {chunk['document_name']}  (access_level={chunk['access_level']})")

        print("\n--- Text will send to LLM---")
        print(format_chunks_for_llm(chunks)[:500] + "...\n")
    
 









