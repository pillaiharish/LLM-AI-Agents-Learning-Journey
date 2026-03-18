from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import StreamingResponse
import io

from app.file_renamer.renamer import FileRenamer

router = APIRouter(prefix="/api/file-renamer")


@router.post("/rename")
async def rename_file(
    file: UploadFile = File(...),
    action: str = Form("custom"),
    new_name: str = Form(""),
):
    contents = await file.read()

    if action == "random":
        output_name = FileRenamer.random_name(file.filename)
    elif action == "strip":
        output_name = FileRenamer.strip_metadata(file.filename)
    else:
        output_name = FileRenamer.custom_name(new_name or file.filename, file.filename)

    return StreamingResponse(
        io.BytesIO(contents),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{output_name}"'},
    )
