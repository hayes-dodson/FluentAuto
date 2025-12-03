from ..meshing.utils_detect_zones import detect_enclosure_zone

def set_reference_values(session):
    enclosure = detect_enclosure_zone(session)
    rv = session.solver.Settings.ReferenceValues

    rv.ReferenceZone = enclosure
    rv.ComputeFrom = "inlet"
    print("Reference values computed from inlet.")
