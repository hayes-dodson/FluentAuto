import csv
import os


def export_case_summary_csv(
    file_path,
    case_name,
    Cd,
    Cl,
    SCx,
    SCz,
    area_full,
    yplus_stats=None,
    mesh_metrics=None
):
    """
    Appends a single-row summary for this case to a CSV.
    Creates file with header if it doesn't exist.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    file_exists = os.path.exists(file_path)

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "case",
                "Cd",
                "Cl",
                "SCx",
                "SCz",
                "Area",
                "yplus_min",
                "yplus_avg",
                "yplus_max",
                "ortho_min",
                "ortho_avg",
                "ortho_max",
                "skew_min",
                "skew_avg",
                "skew_max"
            ])

        y_min = y_avg = y_max = None
        if yplus_stats:
            y_min = yplus_stats.get("min")
            y_avg = yplus_stats.get("avg")
            y_max = yplus_stats.get("max")

        o_min = o_avg = o_max = s_min = s_avg = s_max = None
        if mesh_metrics:
            o_min = mesh_metrics.get("ortho_min")
            o_avg = mesh_metrics.get("ortho_avg")
            o_max = mesh_metrics.get("ortho_max")
            s_min = mesh_metrics.get("skew_min")
            s_avg = mesh_metrics.get("skew_avg")
            s_max = mesh_metrics.get("skew_max")

        writer.writerow([
            case_name,
            Cd,
            Cl,
            SCx,
            SCz,
            area_full,
            y_min,
            y_avg,
            y_max,
            o_min,
            o_avg,
            o_max,
            s_min,
            s_avg,
            s_max
        ])

    print(f"[Summary] Appended row to {file_path}")
