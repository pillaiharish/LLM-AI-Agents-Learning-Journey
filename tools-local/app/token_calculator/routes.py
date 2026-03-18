from fastapi import APIRouter, Form, UploadFile, File

from app.token_calculator.calculator import TokenCalculator

router = APIRouter(prefix="/api/token-calculator")


@router.post("/calculate/text")
async def calculate_text(text: str = Form(...), model: str = Form(None)):
    return TokenCalculator.calculate_from_text(text, model or None)


@router.post("/calculate/file")
async def calculate_file(file: UploadFile = File(...), model: str = Form(None)):
    contents = await file.read()
    return TokenCalculator.calculate_from_file_bytes(contents, file.filename, model or None)


@router.get("/models")
async def get_models():
    return TokenCalculator.get_models()
