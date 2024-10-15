import cadquery as cq
from src.tray_logic.traycontainer import TrayContainer


def calculate_outer_tray_outer_radii(tray: TrayContainer):
    return tray.hole_fillet_radius_mm + tray.wall_thickness_in_mm


def create_3Dtray_from_tray_object(tray: TrayContainer):
    tray_box = cq.Workplane("XY") \
        .box(tray.width_in_mm, tray.length_in_mm, tray.height_in_mm) \
        .edges("|Z") \
        .fillet(calculate_outer_tray_outer_radii(tray))

    print(tray_box.faces().size())
    # tray_box = tray_box.workplane().faces('>Z').center(-tray.width_in_mm / 2, tray.length_in_mm / 2)
    # tray_box = tray_box.box(1,1,1)
    return tray_box


rect = create_3Dtray_from_tray_object(TrayContainer(150, 100))
cq.exporters.export(rect, "pooped_models\\result.stl")
