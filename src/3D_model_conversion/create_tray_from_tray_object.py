import cadquery as cq
from src.tray_logic.traycontainer import TrayContainer
from src.tray_logic.TrayHole import TrayHole


def calculate_cell_span_in_grid_mm(tray_container: TrayContainer):
    return (tray_container.width_in_mm / tray_container.X_Cells)


def calculate_cell_size_mm(tray_container: TrayContainer):
    return calculate_cell_span_in_grid_mm(tray_container) - (2 * tray_container.wall_thickness_in_mm)


def calculate_outer_tray_outer_radii(tray: TrayContainer):
    return tray.hole_fillet_radius_mm + tray.wall_thickness_in_mm


def calculate_topleft_pos_mm(tray_container: TrayContainer, tray_hole: TrayHole)->tuple:
    return (
        (calculate_cell_span_in_grid_mm(tray_container) * (tray_hole.top_left_index_pos.XIndexPos)) + \
            tray_container.wall_thickness_in_mm,
        (calculate_cell_span_in_grid_mm(tray_container) * (tray_hole.top_left_index_pos.YIndexPos)) + \
        tray_container.wall_thickness_in_mm)


def create_3Dtray_from_tray_object(tray_container: TrayContainer):
    tray_model = cq.Workplane("XY") \
        .box(tray_container.width_in_mm, tray_container.length_in_mm, tray_container.height_in_mm) \
        .edges("|Z") \
        .fillet(calculate_outer_tray_outer_radii(tray_container))

    topleft_workplane = cq.Workplane("XY") \
        .transformed(offset=(0, 0, tray_container.height_in_mm / 2)) \
        .center(-tray_container.width_in_mm / 2, tray_container.length_in_mm / 2)

    for tray_hole in tray_container.tray_holes:
        new_rect = topleft_workplane.rect(*tray_container.get_tray_hole_dimensions_mm(tray_hole), centered=False). \
            translate((*calculate_topleft_pos_mm(tray_container,tray_hole),0)) \
            .extrude(-(tray_container.height_in_mm - tray_container.wall_thickness_in_mm))
        tray_model = tray_model.cut(new_rect)

    return tray_model


rect = create_3Dtray_from_tray_object(TrayContainer(150, 100))
cq.exporters.export(rect, "pooped_models\\result.stl")
