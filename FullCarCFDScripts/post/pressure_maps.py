import os

def export_pressure_map(session, file_path, plane_type="xy", origin=None):
    """
    Exports a static pressure contour on a plane (default XY at origin).
    """
    if origin is None:
        origin = [0.0, 0.0, 0.0]

    try:
        surf = session.post.Surface.Plane
        surf["p_plane"] = {
            "type": plane_type,
            "point": origin
        }

        contour = session.post.Contours
        contour["p_contour"] = {
            "field": "pressure",
            "surfaces": ["p_plane"]
        }

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        session.post.SavePicture(file_name=file_path)
        print(f"[Pressure] Saved map: {file_path}")
    except Exception as e:
        print("[Pressure] Failed to export map:", e)
