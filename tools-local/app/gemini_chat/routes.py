from fastapi import APIRouter, Form, UploadFile, File
from pydantic import BaseModel
from typing import Optional

from app.gemini_chat.client import GeminiClient, GEMINI_MODELS
from app.gemini_chat.session import SessionManager

router = APIRouter(prefix="/api/gemini-chat")
sessions = SessionManager()


@router.get("/models")
async def list_models():
    return GEMINI_MODELS


class NewSessionRequest(BaseModel):
    memory: bool = True


@router.post("/session/new")
async def new_session(req: NewSessionRequest):
    sid = sessions.create()
    sessions.set_memory(sid, req.memory)
    return {"session_id": sid}


@router.get("/sessions")
async def list_all_sessions():
    return sessions.list_sessions()


@router.post("/send")
async def send_message(
    api_key: str = Form(...),
    model: str = Form("gemini-2.0-flash"),
    message: str = Form(...),
    session_id: str = Form(...),
    files: list[UploadFile] = File(default=[]),
):
    session = sessions.get(session_id)
    if not session:
        return {"error": "Session not found"}

    # Process uploaded files
    file_parts = []
    for f in files:
        content = await f.read()
        if content:
            part = GeminiClient.file_to_part(content, f.filename)
            file_parts.append(part)

    # Get history if memory is on
    history = sessions.get_history(session_id)

    try:
        result = GeminiClient.send_message(
            api_key=api_key,
            model=model,
            message=message,
            history=history,
            files=file_parts if file_parts else None,
        )
    except RuntimeError as e:
        return {"error": str(e)}

    # Build user parts for history (text only, skip file data to save memory)
    user_parts = [{"text": message}]
    if file_parts:
        user_parts.insert(0, {"text": f"[Attached {len(file_parts)} file(s)]"})

    sessions.add_exchange(session_id, user_parts, result["text"])

    return {
        "text": result["text"],
        "usage": result["usage"],
    }


class MemoryToggle(BaseModel):
    session_id: str
    memory: bool


@router.post("/memory")
async def toggle_memory(req: MemoryToggle):
    sessions.set_memory(req.session_id, req.memory)
    return {"memory": req.memory}


@router.get("/context/{session_id}")
async def get_context(session_id: str):
    history = sessions.get_history(session_id)
    return {"history": history, "message_count": len(history)}


@router.post("/session/clear")
async def clear_session(session_id: str = Form(...)):
    sessions.clear(session_id)
    return {"status": "cleared"}
