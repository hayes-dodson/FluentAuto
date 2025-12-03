def get_yplus_statistics(session):
    """
    Pulls y+ field and computes min, max, and average.
    """
    field = session.post.FieldData["yplus"]

    values = field.GetData()

    if not values:
        print("WARNING: y+ field returned no values.")
        return None

    y_min = min(values)
    y_max = max(values)
    y_avg = sum(values) / len(values)

    return {
        "min": y_min,
        "max": y_max,
        "avg": y_avg
    }


def export_yplus_contour(session, file_path):
    """
    Saves a y+ contour image (wall surfaces only).
    """

    surf = session.post.Surface
    walls = [name for name in surf.ListNames() if "wall" in name.lower()]

    if not walls:
        print("WARNING: No wall zones found for y+ contour.")
        return

    # Create contour
    contour = session.post.Contours
    contour["yplus_plot"] = {
        "field": "yplus",
        "surfaces": walls
    }

    session.post.SavePicture(file_name=file_path)
    print(f"Saved y+ contour to: {file_path}")
