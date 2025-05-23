import json
import os
import requests

PPLX_KEY = os.getenv("PERPLEXITY_API_KEY")
PPLX_ENDPOINT = "https://api.perplexity.ai/chat/completions"
MODEL = "sonar-pro"

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "explanation": {"type": "string"}
    },
    "required": ["score", "explanation"]
}

def _post(payload: dict) -> dict:
    headers = {
        "Authorization": f"Bearer {PPLX_KEY}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }
    resp = requests.post(PPLX_ENDPOINT, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return json.loads(resp.json()["choices"][0]["message"]["content"])

def fact_check_claim(claim: str) -> dict:
    """Ask Sonar‑Pro to fact‑check a **text** claim and return structured JSON."""
    payload = {
        "model":   MODEL,
        "stream":  False,
        "messages": [{
            "role": "user",
            "content": (
                "Evaluate the truthfulness of the following claim on a 0‑100 scale "
                "(100 = absolutely true) and return ONLY a JSON object that matches "
                "the schema I’m providing.\n\n"
                f"Claim: {claim}"
            )
        }],
        "response_format": {"type": "json_schema", "json_schema": {"schema": JSON_SCHEMA}},
        "max_tokens": 256
    }
    return _post(payload)

def fact_check_image_b64(image_b64: str) -> dict:
    """Send image + prompt, expect JSON with score & explanation."""
    headers = {
        "Authorization": f"Bearer {PPLX_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    data = {
        "model": MODEL,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": [
                    { "type": "text",
                      "text":
                        ("Extract any factual claim visible in this image "
                         "and evaluate its truthfulness on a 0‑100 scale "
                         "(100 = absolutely true). "
                         "Return ONLY a JSON object matching the provided schema.") },
                    { "type": "image_url",
                      "image_url": {
                          "url": f"data:image/png;base64,{image_b64}"
                      }}
                ]
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": { "schema": JSON_SCHEMA }
        }
    }

    resp = requests.post(PPLX_ENDPOINT, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    return json.loads(resp.json()["choices"][0]["message"]["content"])
