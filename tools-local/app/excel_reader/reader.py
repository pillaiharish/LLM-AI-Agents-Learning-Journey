import os


class ExcelReader:
    @staticmethod
    def read_sheets(file_path: str) -> dict:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.xls':
            return ExcelReader._read_xls(file_path)
        return ExcelReader._read_xlsx(file_path)

    @staticmethod
    def _read_xlsx(file_path: str) -> dict:
        from openpyxl import load_workbook
        wb = load_workbook(file_path, read_only=True, data_only=True)
        sheets = {}
        for name in wb.sheetnames:
            ws = wb[name]
            rows = []
            for row in ws.iter_rows(values_only=True):
                rows.append([str(c) if c is not None else "" for c in row])
            sheets[name] = rows
        wb.close()
        return sheets

    @staticmethod
    def _read_xls(file_path: str) -> dict:
        import xlrd
        wb = xlrd.open_workbook(file_path)
        sheets = {}
        for name in wb.sheet_names():
            ws = wb.sheet_by_name(name)
            rows = []
            for r in range(ws.nrows):
                rows.append([str(ws.cell_value(r, c)) for c in range(ws.ncols)])
            sheets[name] = rows
        return sheets
