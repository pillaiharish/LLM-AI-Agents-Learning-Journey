import os
import tempfile

from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import StreamingResponse
import io

from app.excel_reader.reader import ExcelReader
from app.excel_reader.converter import ExcelConverter

router = APIRouter(prefix="/api/excel-reader")


def _save_temp(file_bytes: bytes, filename: str) -> str:
    ext = os.path.splitext(filename)[1]
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    tmp.write(file_bytes)
    tmp.close()
    return tmp.name


@router.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    contents = await file.read()
    tmp_path = _save_temp(contents, file.filename)
    try:
        sheets = ExcelReader.read_sheets(tmp_path)
        return {"sheets": sheets}
    finally:
        os.unlink(tmp_path)


@router.post("/convert-csv")
async def convert_csv(file: UploadFile = File(...), sheet: str = Form("__all__")):
    contents = await file.read()
    tmp_path = _save_temp(contents, file.filename)
    try:
        sheets = ExcelReader.read_sheets(tmp_path)
    finally:
        os.unlink(tmp_path)

    if sheet == "__all__":
        csv_dict = ExcelConverter.sheets_to_csv(sheets)
        if len(csv_dict) == 1:
            name, content = next(iter(csv_dict.items()))
            return StreamingResponse(
                io.BytesIO(content.encode()),
                media_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{name}.csv"'},
            )
        zip_bytes = ExcelConverter.csv_to_zip(csv_dict)
        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/zip",
            headers={"Content-Disposition": 'attachment; filename="sheets.zip"'},
        )
    else:
        csv_dict = ExcelConverter.sheets_to_csv(sheets, sheet)
        content = next(iter(csv_dict.values()))
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{sheet}.csv"'},
        )
