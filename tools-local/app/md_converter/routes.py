import io
import os

from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse

from app.md_converter.converter import MarkdownConverter

router = APIRouter(prefix="/api/md-converter")


def _stem(filename: str) -> str:
    return os.path.splitext(filename)[0] if filename else "document"


@router.post("/to-html")
async def convert_to_html(
    file: UploadFile = File(None),
    text: str = Form(None),
    filename: str = Form("document.md"),
):
    """Convert Markdown → styled HTML. Download the HTML file."""
    if file and file.filename:
        raw = (await file.read()).decode("utf-8", errors="replace")
        title = _stem(file.filename)
        out_name = _stem(file.filename) + ".html"
    elif text:
        raw = text
        title = _stem(filename)
        out_name = _stem(filename) + ".html"
    else:
        return JSONResponse({"error": "No input provided"}, status_code=400)

    html = MarkdownConverter.md_to_html(raw, title)
    return StreamingResponse(
        io.BytesIO(html.encode("utf-8")),
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{out_name}"'},
    )


@router.post("/to-pdf")
async def convert_to_pdf(
    file: UploadFile = File(None),
    text: str = Form(None),
    filename: str = Form("document.md"),
):
    """Convert Markdown → HTML → PDF. Download the PDF file."""
    if file and file.filename:
        raw = (await file.read()).decode("utf-8", errors="replace")
        title = _stem(file.filename)
        out_name = _stem(file.filename) + ".pdf"
    elif text:
        raw = text
        title = _stem(filename)
        out_name = _stem(filename) + ".pdf"
    else:
        return JSONResponse({"error": "No input provided"}, status_code=400)

    try:
        pdf = MarkdownConverter.md_to_pdf(raw, title)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    return StreamingResponse(
        io.BytesIO(pdf),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{out_name}"'},
    )


@router.post("/html-to-pdf")
async def html_to_pdf(
    file: UploadFile = File(None),
    html: str = Form(None),
    filename: str = Form("document.html"),
):
    """Convert existing HTML → PDF. Download the PDF file."""
    if file and file.filename:
        raw_html = (await file.read()).decode("utf-8", errors="replace")
        out_name = _stem(file.filename) + ".pdf"
    elif html:
        raw_html = html
        out_name = _stem(filename) + ".pdf"
    else:
        return JSONResponse({"error": "No input provided"}, status_code=400)

    try:
        pdf = MarkdownConverter.html_to_pdf(raw_html)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    return StreamingResponse(
        io.BytesIO(pdf),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{out_name}"'},
    )


@router.post("/preview")
async def preview_html(
    file: UploadFile = File(None),
    text: str = Form(None),
    filename: str = Form("document.md"),
):
    """Return rendered HTML as JSON for in-browser preview (not a download)."""
    if file and file.filename:
        raw = (await file.read()).decode("utf-8", errors="replace")
        title = _stem(file.filename)
    elif text:
        raw = text
        title = _stem(filename)
    else:
        return JSONResponse({"error": "No input provided"}, status_code=400)

    html = MarkdownConverter.md_to_html(raw, title)
    return {"html": html, "title": title}
