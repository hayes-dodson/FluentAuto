import os
from datetime import datetime

from config.settings import SETTINGS
from batch.excel_writer import csv_to_excel

# We will define run_case(geometry_path, output_dir) in main.py
from main import run_case


def run_batch():
    """
    Runs multiple geometries in a queue:
      - finds geometry files in geometry_root_dir
      - creates a result folder per geometry
      - calls run_case() for each
      - builds a global Excel summary at the end
    """
    geom_root = SETTINGS["geometry_root_dir"]
    ext = SETTINGS["geometry_extension"]
    out_root = SETTINGS["output_root"]
    batch_size = SETTINGS["batch_size"]

    os.makedirs(out_root, exist_ok=True)

    # Find geometry files
    all_files = [
        f for f in os.listdir(geom_root)
        if f.lower().endswith(ext.lower())
    ]

    if not all_files:
        print(f"[Batch] No *{ext} files found in: {geom_root}")
        return

    # Trim to batch size
    geom_files = all_files[:batch_size]

    print(f"[Batch] Found {len(geom_files)} geometries to run:")

    for f in geom_files:
        print("   -", f)

    # Global summary CSV (all cases)
    global_summary_csv = os.path.join(out_root, "global_summary.csv")

    for f in geom_files:
        base = os.path.splitext(f)[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        case_name = f"{base}_{timestamp}"

        case_out_dir = os.path.join(out_root, case_name)
        os.makedirs(case_out_dir, exist_ok=True)

        geom_path = os.path.join(geom_root, f)

        print("\n======================================")
        print(f"[Batch] Running case: {case_name}")
        print(f"[Batch] Geometry:    {geom_path}")
        print(f"[Batch] Output dir:  {case_out_dir}")
        print("======================================\n")

        # Run single-case pipeline
        run_case(
            geometry_path=geom_path,
            output_dir=case_out_dir,
            global_summary_csv=global_summary_csv,
        )

    # After all cases: convert global_summary.csv → Excel
    excel_path = os.path.join(out_root, "global_summary.xlsx")
    csv_to_excel(global_summary_csv, excel_path)

    print("\n[Batch] All cases finished.")
    print("[Batch] Excel summary:", excel_path)


if __name__ == "__main__":
    run_batch()
