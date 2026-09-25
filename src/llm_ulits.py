import os
import json
from dotenv import load_dotenv
from ploicy_role import get_open_ai_client

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]
CHAT_DEPLOYMENT=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]





def call_llm_with_schema(system_prompt: str,user_prompt: str,schema: dict,schema_name: str,max_completion_tokens: int = 50000,strict: bool = True
) -> dict:
    client=get_open_ai_client()

    response = client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=max_completion_tokens,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "schema": schema,
                "strict": strict,
            },
        },
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("LLM returned empty content.")
    return json.loads(content)