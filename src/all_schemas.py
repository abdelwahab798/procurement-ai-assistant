PROCUREMENT_ASSISTANT_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "source_documents": {"type": "array", "items": {"type": "string"}},
        "missing_information": {"type": "array", "items": {"type": "string"}},
        "recommended_next_action": {"type": "string"},
        "risk_level": {
            "type": ["string", "null"],
            "enum": ["Low", "Medium", "High", "No risk"], 
        },
    },
    "required": [
        "answer",
        "source_documents",
        "missing_information",
        "recommended_next_action",
        "risk_level",
    ],
    "additionalProperties": False,
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
        "missing_fields",
        "policy_violations",
        "recommended_action",
    ],
    "additionalProperties": False,  
}


OFFICER_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "headline": {
            "type": "string"
        },
        "total_requests": {
            "type": "integer"
        },
        "missing_info_count": {
            "type": "integer"
        },
        "status_breakdown": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "count": {"type": "integer"}
                },
                "required": ["status", "count"],
                "additionalProperties": False
            }
        },
        "top_issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "issue": {"type": "string"},
                    "count": {"type": "integer"}
                },
                "required": ["issue", "count"],
                "additionalProperties": False
            }
        },
        "key_insights": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "recommended_actions": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": [
        "headline",
        "total_requests",
        "missing_info_count",
        "status_breakdown",
        "top_issues",
        "key_insights",
        "recommended_actions"
    ],
    "additionalProperties": False
}