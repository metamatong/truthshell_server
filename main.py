from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

from transcription import transcribe_audio
from sonar_mock import analyze_text, analyze_image

app = FastAPI(title="TruthShell Backend", version="0.2.0")


class AnalyzeRequest(BaseModel):
    text: Optional[str] = Field(None, description="Plain text claim.")
    image_base64: Optional[str] = Field(None, description="Base64‑encoded image (PNG/JPEG).")
    audio_base64: Optional[str] = Field(None, description="Base64‑encoded audio (WAV).")


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    # Ensure exactly one input type
    supplied = [v for v in (req.text, req.image_base64, req.audio_base64) if v is not None]
    if len(supplied) != 1:
        return {"error": "Provide exactly one of text, image_base64, or audio_base64."}

    if req.text:
        return analyze_text(req.text)

    if req.image_base64:
        return analyze_image(req.image_base64)

    if req.audio_base64:
        try:
            transcript = transcribe_audio(req.audio_base64)
        except Exception as exc:
            return {"error": f"Audio transcription failed: {exc}"}
        return analyze_text(transcript)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
