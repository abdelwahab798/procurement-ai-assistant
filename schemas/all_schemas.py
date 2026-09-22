
PROCUREMENT_ASSISTANT_RESPONSE_SCHEMA={
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "source_documents": {"type": "array", "items": {"type": "string"}},
        "missing_information": {"type": "array", "items": {"type": "string"}},
        "recommended_next_action": {"type": "string"},
        "risk_level": {"type": "string", "enum": ["Low", "Medium", "High"]},
    },
    "required": ["answer", "source_documents", "recommended_next_action"],
}

PURCHASE_REQUEST_VALIDATION_SCHEMA = {
    "type": "object",
    "properties": {
        "pr_id": {"type": "string"},
        "is_complete": {"type": "boolean"},
        "required_approval_level": {"type": "string"},
        "missing_fields": {"type": "array", "items": {"type": "string"}},
        "policy_violations": {"type": "array", "items": {"type": "string"}},
        "recommended_action": {"type": "string"},
    },
    "required": [
        "pr_id",
        "is_complete",
        "required_approval_level",
        "recommended_action",
    ],
}