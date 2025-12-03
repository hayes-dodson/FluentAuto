import os


def get_yplus_statistics(session):
    """
    Returns dict with min/avg/max y+ from wall-adjacent cells.
    """
    try:
        field = session.post.FieldData["yplus"]
        values = field.GetData()
    except Exception as e:
        print("[y+] Unable to retrieve y+ field:", e)
        return None

    if not values:
        print("[y+] No y+ values.")
        return None

    y_min = min(values)
    y_max = max(values)
    y_avg = sum(values) / len(values)

    return {"min": y_min, "max": y_max, "avg": y_avg}


def print_yplus_summary(stats):
    if not stats:
        return

    print("\n===== y+ Report =====")
    print(f"y+ min : {stats['min']:.3f}")
    print(f"y+ avg : {stats['avg']:.3f}")
    print(f"y+ max : {stats['max']:.3f}")
    print("=====================\n")


def export_yplus_contour(session, file_path):
    """
    Saves a y+ contour image on all wall zones.
    """
    try:
        surf_api = session.post.Surface
        wall_surfs = [n for n in surf_api.ListNames() if "wall" in n.lower()]
        if not wall_surfs:
            print("[y+] No wall surfaces found for y+ contour.")
            return

        contour = session.post.Contours
        contour["yplus_plot"] = {
            "field": "yplus",
            "surfaces": wall_surfs
        }

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        session.post.SavePicture(file_name=file_path)
        print(f"[y+] Saved y+ contour: {file_path}")
    except Exception as e:
        print("[y+] Failed to export y+ contour:", e)
