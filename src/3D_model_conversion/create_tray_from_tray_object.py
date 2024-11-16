import cadquery as cq
from src.tray_logic.traycontainer import TrayContainer


def calculate_outer_tray_outer_radii(tray: TrayContainer):
    return tray.hole_fillet_radius_mm + tray.wall_thickness_in_mm


def create_3Dtray_from_tray_object(tray: TrayContainer):
    tray_box = cq.Workplane("XY") \
        .box(tray.width_in_mm, tray.length_in_mm, tray.height_in_mm) \
        .edges("|Z") \
        .fillet(calculate_outer_tray_outer_radii(tray))

    # this maps on the top face and creates a rect - need to figure out how to create a hole
    #  and extrude it up to the right dimension. ofc in a loop.
    # maybe save correct center before the loop and map to the right hole in each iteration in relation to the center?
    new_workplane = cq.Workplane("XY").transformed(offset=(0, 0, tray_height / 2))
    new_workplane_correct_center = new_workplane.center(-tray_width / 2, tray_length / 2)
    new_workplane_correct_center.box(10, 10, 10)

    return tray_box


rect = create_3Dtray_from_tray_object(TrayContainer(150, 100))
cq.exporters.export(rect, "pooped_models\\result.stl")
