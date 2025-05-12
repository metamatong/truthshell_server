import base64
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field

from sonar_mock import analyze_text, analyze_image
from transcription import transcribe_audio

load_dotenv()

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


@app.post("/analyze/file")
async def analyze_file(
        mode: str = Form(...),  # "audio" | "text" | "image"
        file: UploadFile = File(...)
):
    if mode != "audio":
        raise HTTPException(400, "Only audio supported here")

    # Turn the binary into base‑64 so we can reuse transcribe_audio()
    audio_b64 = base64.b64encode(await file.read()).decode()
    transcript = transcribe_audio(audio_b64)
    return analyze_text(transcript)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
