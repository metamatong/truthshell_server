import random
from typing import Dict

def _make_result() -> Dict[str, str]:
    """
    Simulate analysis of a claim's factuality.
    Returns a dictionary with a 'score' (0 to 100) and an 'explanation'.
    """
    # Generate a random factuality score
    score = random.randint(0, 100)
    # Determine a description based on the score range
    if score > 80:
        explanation = ("The claim is likely true. It is supported by strong evidence or well-known facts, "
                       "indicating that it accurately reflects reality.")
    elif score > 60:
        explanation = ("The claim appears mostly true, though it may contain some minor inaccuracies or be missing context. "
                       "Overall, the core of the statement is factual.")
    elif score > 40:
        explanation = ("The factual accuracy of the claim is uncertain. Some evidence supports it, but there are also conflicting sources "
                       "or ambiguous information making it hard to verify conclusively.")
    elif score > 20:
        explanation = ("The claim is likely unverified or unverifiable. There is little reliable evidence to confirm it, and it may be misleading "
                       "without additional context or sources.")
    else:
        explanation = ("The claim is likely false. It contradicts established facts or reliable sources, indicating that it does not hold up under scrutiny.")
    return {"score": score, "explanation": explanation}

def analyze_text(claim: str):
    return _make_result()

def analyze_image(image_base64: str):
    return _make_result()

def analyze_audio_transcript(transcript: str):
    return _make_result()
