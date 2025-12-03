def detect_enclosure_zone(session):
    names = session.meshing.ListNames()
    cell_zones = names.get("cell_zones", [])

    if not cell_zones:
        raise RuntimeError("No cell zones found.")

    # Rule 1: any 'fluid'
    for z in cell_zones:
        if "fluid" in z.lower():
            return z

    # Rule 2: any 'enclosure'
    for z in cell_zones:
        if "enclosure" in z.lower():
            return z

    # Rule 3: largest by cell count
    try:
        counts = session.solution.MeshInfo.CellCountByZone()
        return max(counts, key=counts.get)
    except:
        pass

    return cell_zones[0]
