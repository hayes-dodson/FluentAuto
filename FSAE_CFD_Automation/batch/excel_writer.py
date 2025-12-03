import os
import csv
import openpyxl


def csv_to_excel(csv_path, excel_path):
    """
    Reads a CSV summary and writes an Excel workbook.
    Overwrites Excel file if it already exists.
    """
    if not os.path.exists(csv_path):
        print(f"[Excel] CSV not found, nothing to convert: {csv_path}")
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Summary"

    with open(csv_path, "r", newline="") as f:
        reader = csv.reader(f)
        for row_idx, row in enumerate(reader, start=1):
            for col_idx, val in enumerate(row, start=1):
                ws.cell(row=row_idx, column=col_idx).value = val

    os.makedirs(os.path.dirname(excel_path), exist_ok=True)
    wb.save(excel_path)
    print(f"[Excel] Wrote Excel summary: {excel_path}")
