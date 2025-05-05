import base64
import tempfile
import os
try:
    import whisper
except ImportError:
    whisper = None

def transcribe_audio(audio_base64: str) -> str:
    """
    Decode a base64-encoded audio file (WAV format) and transcribe it to text.
    """
    # Remove data URL prefix if present (e.g., "data:audio/wav;base64,")
    if audio_base64.startswith("data:"):
        audio_base64 = audio_base64.split(",", 1)[1]
    # Decode the base64 string to bytes
    try:
        audio_bytes = base64.b64decode(audio_base64)
    except Exception as e:
        raise ValueError("Invalid base64 audio data") from e
    # Write the audio bytes to a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(audio_bytes)
        temp_file_path = temp_file.name
    # Transcribe the audio using Whisper if available, otherwise SpeechRecognition
    transcription_text = ""
    if whisper is not None:
        # Load Whisper model (using a smaller model for speed; adjust model size as needed)
        model = whisper.load_model("base")
        result = model.transcribe(temp_file_path)
        transcription_text = result.get("text", "").strip()
    else:
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_file_path) as source:
                audio_data = recognizer.record(source)  # read the entire audio file
                transcription_text = recognizer.recognize_google(audio_data)
        except Exception as e:
            # Clean up temp file in case of an error
            os.remove(temp_file_path)
            raise RuntimeError("Audio transcription failed: " + str(e))
    # Remove the temporary file after transcription
    os.remove(temp_file_path)
    return transcription_text
