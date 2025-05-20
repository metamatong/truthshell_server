"""
Mock implementation that returns data shaped exactly like

data class TruthResponse(
    @SerializedName("confidence_score") val confidenceScore: Int?,
    @SerializedName("confidence_label") val confidenceLabel: String?,
    @SerializedName("sources")         val sources: List<SourceItem>?,
    @SerializedName("error_message")   val errorMessage: String?
)

data class SourceItem(
    @SerializedName("url")     val url: String,
    @SerializedName("title")   val title: String?,
    @SerializedName("snippet") val snippet: String?
)
"""
import random
from typing import Dict, List, Optional

from perplexity_client import fact_check_image_b64  # keep your real call


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
    return _make_result()


def analyze_image(image_b64: str) -> Dict[str, object]:
    try:
        return fact_check_image_b64(image_b64)  # real call (if available)
    except Exception as exc:
        # fall back to mock while developing
        print("Perplexity call failed:", exc)
        result = _make_result()
        result["error_message"] = str(exc)
        return result


def analyze_audio_transcript(transcript: str) -> Dict[str, object]:
    return _make_result()
