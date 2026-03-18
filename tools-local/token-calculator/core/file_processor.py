import os
import subprocess

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".svg"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac", ".wma", ".webm"}


class FileProcessor:
    @staticmethod
    def classify(filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext in IMAGE_EXTENSIONS:
            return "image"
        if ext in AUDIO_EXTENSIONS:
            return "audio"
        return "text"

    @staticmethod
    def extract_text(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()

        if ext in (".txt", ".md", ".csv"):
            return FileProcessor._read_text(file_path)
        elif ext == ".pdf":
            return FileProcessor._read_pdf(file_path)
        elif ext == ".docx":
            return FileProcessor._read_docx(file_path)
        elif ext == ".doc":
            return FileProcessor._read_doc(file_path)
        elif ext == ".xlsx":
            return FileProcessor._read_xlsx(file_path)
        else:
            return FileProcessor._read_text(file_path)

    @staticmethod
    def _read_text(file_path: str) -> str:
        for encoding in ("utf-8", "latin-1"):
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Cannot decode file: {file_path}")

    @staticmethod
    def _read_pdf(file_path: str) -> str:
        from pypdf import PdfReader

        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)

    @staticmethod
    def _read_docx(file_path: str) -> str:
        from docx import Document

        doc = Document(file_path)
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())

    @staticmethod
    def _read_doc(file_path: str) -> str:
        try:
            result = subprocess.run(
                ["antiword", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return result.stdout
        except FileNotFoundError:
            pass
        raise ValueError(
            "Cannot read .doc files. Install antiword: brew install antiword"
        )

    @staticmethod
    def _read_xlsx(file_path: str) -> str:
        from openpyxl import load_workbook

        wb = load_workbook(file_path, read_only=True, data_only=True)
        rows = []
        for sheet in wb.sheetnames:
            ws = wb[sheet]
            rows.append(f"--- Sheet: {sheet} ---")
            for row in ws.iter_rows(values_only=True):
                cells = [str(c) if c is not None else "" for c in row]
                rows.append("\t".join(cells))
        wb.close()
        return "\n".join(rows)
