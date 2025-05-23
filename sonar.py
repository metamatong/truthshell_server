
import random
from typing import Dict
from typing import List, Optional

from perplexity_client import fact_check_image_b64, fact_check_claim


# ──────────────────────────────────────────────────────────────────────────────
# helpers
# ──────────────────────────────────────────────────────────────────────────────
def _score_to_label(score: int) -> str:
    if score > 80:
        return "Very Likely True"
    if score > 60:
        return "Likely True"
    if score > 40:
        return "Uncertain"
    if score > 20:
        return "Likely False"
    return "Very Likely False"


def _mock_sources(n: int = 3) -> List[Dict[str, Optional[str]]]:
    """Return n fake source items."""
    domains = ["example.com", "news.example.net", "research.example.org"]
    snippets = [
        "Independent analysis supports the claim.",
        "Experts are divided on the accuracy of the statement.",
        "No reputable source could confirm the allegation.",
        "Multiple eyewitnesses corroborated the report.",
    ]
    items = []
    for i in range(n):
        items.append(
            {
                "url": f"https://{domains[i % len(domains)]}/article/{random.randint(1000,9999)}",
                "title": f"Mock Source Article #{i+1}",
                "snippet": random.choice(snippets),
            }
        )
    return items


def _make_result() -> Dict[str, object]:
    """Return a dict that matches TruthResponse exactly."""
    score = random.randint(0, 100)
    return {
        "confidence_score": score,
        "confidence_label": _score_to_label(score),
        "sources": _mock_sources(),
        "error_message": None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# public API
# ──────────────────────────────────────────────────────────────────────────────
def analyze_text(claim: str) -> Dict[str, object]:
    return fact_check_claim(claim)


def analyze_image(image_b64: str) -> Dict[str, object]:
    return fact_check_image_b64(image_b64)

def analyze_audio_transcript(transcript: str) -> Dict[str, object]:
    return fact_check_claim(transcript)
