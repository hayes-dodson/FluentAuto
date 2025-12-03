def export_contour(session, variable, plane="xy", file="contour.png"):
    post = session.post
    surf = post.Surface.Plane
    surf["plt"] = {"type": plane, "point": [0,0,0]}
    contour = post.Contours
    contour["c"] = {"field": variable, "surfaces": ["plt"]}
    post.SavePicture(file_name=file)
    print("Contour saved:", file)
