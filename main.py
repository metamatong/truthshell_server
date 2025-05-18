import base64
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Security, Depends
from fastapi import UploadFile, File, Form, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from sonar_mock import analyze_text, analyze_image
from transcription import transcribe_audio

load_dotenv()

API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("APPROVED_API_KEY")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key: str = Security(api_key_header)):
    if not API_KEY or api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate API KEY")
    return api_key


app = FastAPI(title="TruthShell Backend", version="0.2.0")


class AnalyzeRequest(BaseModel):
    text: Optional[str] = Field(None, description="Plain text claim.")
    image_base64: Optional[str] = Field(None, description="Base64‑encoded image (PNG/JPEG).")
    audio_base64: Optional[str] = Field(None, description="Base64‑encoded audio (WAV).")


logger = logging.getLogger(__name__)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to Vercel!"}


@app.post("/analyze", dependencies=[Depends(get_api_key)])
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


@app.post("/analyze/file", dependencies=[Depends(get_api_key)])
async def analyze_file(
        mode: str = Form(...),  # "audio" | "text" | "image"
        file: UploadFile = File(...)
):
    # Reject oversized files early (Perplexity cap is 5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(413, "File too large (>5 MB)")

    blob = await file.read()
    b64 = base64.b64encode(blob).decode()

    if mode == "audio":
        transcript = transcribe_audio(b64)
        return analyze_text(transcript)

    if mode == "image":
        return analyze_image(b64)

    raise HTTPException(400, "mode must be 'audio' or 'image'")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
