import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")


def create_app() -> FastAPI:
    app = FastAPI(title="Dev Tools")

    from app.token_calculator.routes import router as token_router
    from app.json_linter.routes import router as json_router
    from app.file_renamer.routes import router as renamer_router
    from app.excel_reader.routes import router as excel_router
    from app.image_tools.routes import router as image_router
    from app.storage_analyzer.routes import router as storage_router
    from app.network_scanner.routes import router as network_router
    from app.chatgpt_viewer.routes import router as chatgpt_router
    from app.gemini_chat.routes import router as gemini_router
    from app.audio_transcription.routes import router as audio_router
    from app.md_converter.routes import router as md_router

    app.include_router(token_router)
    app.include_router(json_router)
    app.include_router(renamer_router)
    app.include_router(excel_router)
    app.include_router(image_router)
    app.include_router(storage_router)
    app.include_router(network_router)
    app.include_router(chatgpt_router)
    app.include_router(gemini_router)
    app.include_router(audio_router)
    app.include_router(md_router)

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return app
