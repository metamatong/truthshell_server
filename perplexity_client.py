import json
import os
import re
from urllib.parse import urlparse

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
    """Fire-and-forget helper that preserves citations."""
    headers = {
        "Authorization": f"Bearer {PPLX_KEY}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }

    resp = requests.post(PPLX_ENDPOINT, headers=headers,
                         json=payload, timeout=60)
    resp.raise_for_status()
    raw = resp.json()                       # full outer response

    # 1️⃣  core JSON (score, explanation) from the inner content
    core = json.loads(raw["choices"][0]["message"]["content"])

    # 2️⃣  citations list (may be missing if search was disabled)
    urls = raw.get("citations", [])

    # 3️⃣  make a neat sources array with index + domain
    sources = [
        {"index": i+1,
         "url": u,
         "domain": urlparse(u).netloc.replace("www.", "")}
        for i, u in enumerate(urls)
    ]

    # 4️⃣  scrub any dangling “[n]” refs and attach sources
    core["explanation"] = re.sub(r"\[\d+\]", "", core["explanation"]).strip()
    core["sources"]     = sources

    return core

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
