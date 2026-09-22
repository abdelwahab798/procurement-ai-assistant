
import os
import json
from dotenv import load_dotenv

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]
CHAT_DEPLOYMENT = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]


def _get_client():
    from openai import OpenAI
    return OpenAI(base_url=AZURE_OPENAI_ENDPOINT, api_key=AZURE_OPENAI_API_KEY)


def call_llm_with_schema(
    system_prompt: str,
    user_prompt: str,
    schema: dict,
    schema_name: str,
    max_completion_tokens: int = 1500,
) -> dict:
    """
    يستدعي gpt-5-mini، يجبره يرجع JSON متوافق مع schema محدد، ويرجعه كـ dict.
    max_completion_tokens كبير نسبيًا لأن gpt-5-mini بياخد جزء منه في reasoning
    قبل ما يطلع الرد النهائي (لاحظنا ده وإحنا بنختبر الاتصال الأول).
    """
    client = _get_client()

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
                "strict": False,
            },
        },
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError(
            "الموديل رجع رد فاضي (ممكن يكون استهلك كل الـ tokens في reasoning) - "
            "جرب تزود max_completion_tokens."
        )

    return json.loads(content)