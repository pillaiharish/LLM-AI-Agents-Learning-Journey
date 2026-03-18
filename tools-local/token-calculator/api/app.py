import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.routes import router

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")


def create_app() -> FastAPI:
    app = FastAPI(title="Token Calculator")
    app.include_router(router)
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return app
