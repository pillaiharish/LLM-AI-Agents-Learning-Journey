import os

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse, JSONResponse
import io

from app.chatgpt_viewer.processor import ChatGPTProcessor
from app.chatgpt_viewer.cache import ConversationCache
from app.chatgpt_viewer.search import ConversationSearch
from app.chatgpt_viewer.exporter import ConversationExporter

router = APIRouter(prefix="/api/chatgpt-viewer")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "chatgpt-convo")


def _load_conversations() -> list:
    cache = ConversationCache(DATA_DIR)
    cached = cache.get_cached()
    if cached is not None:
        return cached
    processor = ChatGPTProcessor(DATA_DIR)
    data = processor.process()
    cache.save(data)
    return data


@router.get("/conversations")
async def list_conversations():
    convs = _load_conversations()
    # Return without full messages for the list view
    return [
        {
            "id": c["id"],
            "title": c["title"],
            "create_time": c["create_time"],
            "message_count": c["message_count"],
        }
        for c in convs
    ]


@router.get("/conversation/{conv_id}")
async def get_conversation(conv_id: str):
    convs = _load_conversations()
    for c in convs:
        if c["id"] == conv_id:
            return c
    return JSONResponse({"error": "Conversation not found"}, status_code=404)


@router.get("/search")
async def search_conversations(q: str = Query("")):
    convs = _load_conversations()
    results = ConversationSearch.search(convs, q)
    return [
        {
            "id": c["id"],
            "title": c["title"],
            "create_time": c["create_time"],
            "message_count": c["message_count"],
        }
        for c in results
    ]


EXPORT_MIME = {
    "txt": "text/plain",
    "html": "text/html",
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.get("/export/{conv_id}")
async def export_conversation(conv_id: str, format: str = Query("txt")):
    convs = _load_conversations()
    conv = None
    for c in convs:
        if c["id"] == conv_id:
            conv = c
            break
    if not conv:
        return JSONResponse({"error": "Conversation not found"}, status_code=404)

    fmt = format.lower()
    if fmt == "txt":
        data = ConversationExporter.to_txt(conv)
    elif fmt == "html":
        data = ConversationExporter.to_html(conv)
    elif fmt == "pdf":
        data = ConversationExporter.to_pdf(conv)
    elif fmt == "docx":
        data = ConversationExporter.to_docx(conv)
    else:
        return JSONResponse({"error": f"Unsupported format: {fmt}"}, status_code=400)

    mime = EXPORT_MIME.get(fmt, "application/octet-stream")
    filename = f"conversation.{fmt}"
    return StreamingResponse(
        io.BytesIO(data),
        media_type=mime,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/reprocess")
async def reprocess():
    cache = ConversationCache(DATA_DIR)
    cache.invalidate()
    processor = ChatGPTProcessor(DATA_DIR)
    data = processor.process()
    cache.save(data)
    return {"status": "ok", "count": len(data)}
