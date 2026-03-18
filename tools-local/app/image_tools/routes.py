import io
import os

from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import StreamingResponse
from PIL import Image

from app.image_tools.resizer import ImageResizer
from app.image_tools.converter import ImageConverter
from app.image_tools.editor import ImageEditor

router = APIRouter(prefix="/api/image-tools")


def _open_image(file_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(file_bytes))


def _image_response(img: Image.Image, filename: str, fmt: str = "PNG") -> StreamingResponse:
    buf = io.BytesIO()
    if img.mode == 'RGBA' and fmt.upper() == 'JPEG':
        img = img.convert('RGB')
    img.save(buf, format=fmt)
    buf.seek(0)
    mime = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}.get(fmt, "image/png")
    return StreamingResponse(
        buf, media_type=mime,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/resize")
async def resize_image(
    file: UploadFile = File(...),
    width: int = Form(...),
    height: int = Form(...),
):
    img = _open_image(await file.read())
    result = ImageResizer.resize(img, width, height)
    name = os.path.splitext(file.filename)[0] + f"_{width}x{height}" + os.path.splitext(file.filename)[1]
    fmt = img.format or "PNG"
    return _image_response(result, name, fmt)


@router.post("/convert")
async def convert_image(
    file: UploadFile = File(...),
    format: str = Form(...),
):
    img = _open_image(await file.read())
    data, mime, ext = ImageConverter.convert(img, format)
    name = os.path.splitext(file.filename)[0] + ext
    return StreamingResponse(
        io.BytesIO(data), media_type=mime,
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@router.post("/adjust")
async def adjust_image(
    file: UploadFile = File(...),
    brightness: float = Form(100),
    saturation: float = Form(100),
    hue: float = Form(0),
):
    img = _open_image(await file.read())
    result = ImageEditor.adjust(img, brightness, saturation, hue)
    fmt = img.format or "PNG"
    name = os.path.splitext(file.filename)[0] + "_adjusted" + os.path.splitext(file.filename)[1]
    return _image_response(result, name, fmt)
