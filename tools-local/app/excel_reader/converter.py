import csv
import io
import zipfile


class ExcelConverter:
    @staticmethod
    def sheets_to_csv(sheets: dict, sheet_name: str | None = None) -> dict:
        """Convert sheet data to CSV strings. Returns {sheet_name: csv_string}."""
        result = {}
        targets = {sheet_name: sheets[sheet_name]} if sheet_name and sheet_name in sheets else sheets
        for name, rows in targets.items():
            buf = io.StringIO()
            writer = csv.writer(buf)
            for row in rows:
                writer.writerow(row)
            result[name] = buf.getvalue()
        return result

    @staticmethod
    def csv_to_zip(csv_dict: dict) -> bytes:
        """Pack multiple CSV files into a ZIP archive."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for name, content in csv_dict.items():
                zf.writestr(f"{name}.csv", content)
        return buf.getvalue()
