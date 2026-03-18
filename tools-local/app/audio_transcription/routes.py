from fastapi import APIRouter, Form, UploadFile, File

from app.audio_transcription.transcriber import AudioTranscriber

router = APIRouter(prefix="/api/audio-transcription")


@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    endpoint: str = Form(...),
    endpoint_type: str = Form("ollama"),
    model: str = Form(""),
):
    """
    endpoint_type: "ollama", "openai", or "generic"
    endpoint: e.g. "http://192.168.1.100:11434" for Ollama
    model: e.g. "whisper" or "llama3.2-vision" (depends on endpoint_type)
    """
    audio_bytes = await file.read()
    filename = file.filename or "audio.mp3"

    if endpoint_type == "ollama":
        result = AudioTranscriber.transcribe_ollama(endpoint, model, audio_bytes, filename)
    elif endpoint_type == "openai":
        result = AudioTranscriber.transcribe_openai_compatible(endpoint, audio_bytes, filename)
    elif endpoint_type == "generic":
        result = AudioTranscriber.transcribe_generic(endpoint, model, audio_bytes, filename)
    else:
        return {"text": "", "error": f"Unknown endpoint type: {endpoint_type}"}

    return result
