import cadquery as cq
from src.tray_logic.traycontainer import TrayContainer
from src.tray_logic.TrayHole import TrayHole


class trayToModelConverter():
    def __init__(self, tray_container: TrayContainer):
        self.tray_container = tray_container
        self.single_cell_span_mm = tray_container.width_in_mm / tray_container.X_Cells
        self.outer_radii = self.tray_container.holes_fillet_radius_mm + self.tray_container.wall_thickness_in_mm

    # y is negative because of how axis are aligned
    def get_tray_hole_size_dimensions_mm(self, tray_hole: TrayHole) -> tuple:
        tray_hole_span_width = self.single_cell_span_mm * tray_hole.x_cells_span
        tray_hole_span_length = self.single_cell_span_mm * tray_hole.y_cells_span
        twice_wall_thickness = 2 * self.tray_container.wall_thickness_in_mm
        if tray_hole_span_width < twice_wall_thickness or tray_hole_span_length < twice_wall_thickness:
            raise Exception("hole span (chosen grid span) cant be smaller than twice wall thickness")

        else:
            reduced_x_size = tray_hole_span_width - twice_wall_thickness
            reduced_y_size = -(tray_hole_span_length - twice_wall_thickness)

        return reduced_x_size, reduced_y_size

    # + on X and - on y because of how the axis are arranged
    def calculate_middle_hole_pos_mm(self, tray_hole: TrayHole) -> tuple:
        x_offset = ((tray_hole.top_left_index_pos.XIndexPos + 0.5 * tray_hole.x_cells_span) * self.single_cell_span_mm)

        y_offset = -((tray_hole.top_left_index_pos.YIndexPos + 0.5 * tray_hole.y_cells_span) * self.single_cell_span_mm)

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
                .center(*self.calculate_middle_hole_pos_mm(tray_hole)) \
                .sketch() \
                .rect(*self.get_tray_hole_size_dimensions_mm(tray_hole)) \
                .vertices() \
                .fillet(self.tray_container.holes_fillet_radius_mm) \
                .finalize() \
                .extrude(-(self.tray_container.height_in_mm - self.tray_container.wall_thickness_in_mm))

            print(self.tray_container.X_Cells, self.tray_container.Y_Cells)
            print(self.single_cell_span_mm)
            print(tray_hole.x_cells_span, tray_hole.y_cells_span)
            print(*self.get_tray_hole_size_dimensions_mm(tray_hole))
            print(*self.calculate_middle_hole_pos_mm(tray_hole))
            print(self.tray_container.height_in_mm - self.tray_container.wall_thickness_in_mm)

            tray_model = tray_model.cut(new_rect)

        return tray_model
