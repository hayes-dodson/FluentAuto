import csv
import os


def get_mesh_quality(session):
    """
    Returns dict with orthogonal quality and skewness stats if available.
    Uses solver session (after reading mesh).
    """
    try:
        q = session.mesh.GetQualityMetrics()
    except Exception as e:
        print("[MeshQuality] Metrics unavailable:", e)
        return None

    metrics = {}

    if "orthogonal-quality" in q:
        ortho = q["orthogonal-quality"]
        metrics["ortho_min"] = ortho.get("minimum", None)
        metrics["ortho_max"] = ortho.get("maximum", None)
        metrics["ortho_avg"] = ortho.get("average", None)
    else:
        metrics["ortho_min"] = metrics["ortho_max"] = metrics["ortho_avg"] = None

    if "skewness" in q:
        skew = q["skewness"]
        metrics["skew_min"] = skew.get("minimum", None)
        metrics["skew_max"] = skew.get("maximum", None)
        metrics["skew_avg"] = skew.get("average", None)
    else:
        metrics["skew_min"] = metrics["skew_max"] = metrics["skew_avg"] = None

    return metrics


def save_mesh_quality_csv(metrics, file_path):
    if not metrics:
        return

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        for k, v in metrics.items():
            writer.writerow([k, v])

    print(f"[MeshQuality] Saved CSV: {file_path}")


def print_mesh_quality_summary(metrics):
    if not metrics:
        print("[MeshQuality] No metrics to print.")
        return

    print("\n===== Mesh Quality =====")
    print(f"Orthogonal quality min : {metrics.get('ortho_min')}")
    print(f"Orthogonal quality avg : {metrics.get('ortho_avg')}")
    print(f"Orthogonal quality max : {metrics.get('ortho_max')}")
    print(f"Skewness min           : {metrics.get('skew_min')}")
    print(f"Skewness avg           : {metrics.get('skew_avg')}")
    print(f"Skewness max           : {metrics.get('skew_max')}")
    print("========================\n")
