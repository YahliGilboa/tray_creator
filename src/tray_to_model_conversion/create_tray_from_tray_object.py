import cadquery as cq
from src.tray_logic.traycontainer import TrayContainer
from src.tray_logic.TrayHole import TrayHole


class trayToModelConverter():
    single_cell_span: float

    def __init__(self, tray_container: TrayContainer):
        self.tray_container = tray_container
        self.single_cell_span_mm = tray_container.width_in_mm / tray_container.X_Cells
        self.outer_radii = self.tray_container.holes_fillet_radius_mm + self.tray_container.wall_thickness_in_mm

    def get_tray_hole_size_dimensions_mm(self, tray_hole: TrayHole):
        tray_hole_span_width = self.single_cell_span_mm * tray_hole.x_cells_span
        tray_hole_span_length = self.single_cell_span_mm * tray_hole.y_cells_span
        reduced_x_size = tray_hole_span_width - 2 * self.tray_container.wall_thickness_in_mm
        reduced_y_size = tray_hole_span_length - 2 * self.tray_container.wall_thickness_in_mm

        return reduced_x_size, reduced_y_size

    # + on X and - on y because of how the axis are arranged
    def calculate_topleft_pos_mm(self, tray_hole: TrayHole) -> tuple:
        x_offset = tray_hole.top_left_index_pos.XIndexPos + self.tray_container.wall_thickness_in_mm / 2
        y_offset = tray_hole.top_left_index_pos.YIndexPos - self.tray_container.wall_thickness_in_mm / 2

        return x_offset, y_offset

    def create_model_from_tray_object(self):
        tray_model = cq.Workplane("XY") \
            .box(self.tray_container.width_in_mm, self.tray_container.length_in_mm, self.tray_container.height_in_mm) \
            .edges("|Z") \
            .fillet(self.outer_radii)

        topleft_workplane = cq.Workplane("XY") \
            .transformed(offset=(0, 0, self.tray_container.height_in_mm / 2)) \
            .center(-self.tray_container.width_in_mm / 2, self.tray_container.length_in_mm / 2)

        for tray_hole in self.tray_container.tray_holes:
            new_rect = topleft_workplane \
                .rect(*self.get_tray_hole_size_dimensions_mm(tray_hole),
                      centered=False) \
                .translate((*self.calculate_topleft_pos_mm(tray_hole), 0)) \
                .extrude((self.tray_container.height_in_mm - self.tray_container.wall_thickness_in_mm))

            print(*self.get_tray_hole_size_dimensions_mm(tray_hole))
            print(*self.calculate_topleft_pos_mm(tray_hole))
            print(self.tray_container.height_in_mm - self.tray_container.wall_thickness_in_mm)

            tray_model = tray_model.cut(new_rect)

        return tray_model
