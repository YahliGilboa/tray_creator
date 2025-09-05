import cadquery as cq
from src.tray_logic.traycontainer import TrayContainer
from src.tray_logic.TrayHole import TrayHole
import src.tray_logic.conf as conf


class trayToModelConverter:
    def __init__(self, tray_container: TrayContainer, depth_in_mm: float = conf.DEFAULT_TRAY_DEPTH_MM,
                 half_wall_thickness_in_mm: float = conf.DEFAULT_TRAY_HALF_WALL_THICKNESS_MM,
                 tray_hole_fillet_radius_mm: float = conf.DEFAULT_TRAY_FILLET_RADIUS_MM):
        self.tray_container: TrayContainer = tray_container
        self.height_mm: float = depth_in_mm
        self.half_wall_thickness_mm: float = half_wall_thickness_in_mm
        self.holes_fillet_radius_mm: float = tray_hole_fillet_radius_mm
        self.single_cell_span_mm = ((tray_container.width_mm - 2 * self.half_wall_thickness_mm) /
                                    tray_container.X_Cells)
        self.outer_radii = self.holes_fillet_radius_mm + self.half_wall_thickness_mm * 2

    # y is negative because of how axis are aligned
    def get_tray_hole_size_dimensions_mm(self, tray_hole: TrayHole) -> tuple:
        tray_hole_span_width = self.single_cell_span_mm * tray_hole.x_cells_span
        tray_hole_span_length = self.single_cell_span_mm * tray_hole.y_cells_span
        wall_thickness = 2 * self.half_wall_thickness_mm
        if tray_hole_span_width < wall_thickness or tray_hole_span_length < wall_thickness:
            raise Exception("hole span (chosen grid span) cant be smaller than twice wall thickness")

        else:
            reduced_x_size = tray_hole_span_width - wall_thickness
            reduced_y_size = -(tray_hole_span_length - wall_thickness)

        return reduced_x_size, reduced_y_size

    # + on X and - on y because of how the axis are arranged
    def calculate_middle_hole_pos_mm(self, tray_hole: TrayHole) -> tuple:
        x_offset = ((tray_hole.top_left_index_pos.XIndexPos + 0.5 * tray_hole.x_cells_span) * self.single_cell_span_mm)

        y_offset = -((tray_hole.top_left_index_pos.YIndexPos + 0.5 * tray_hole.y_cells_span) * self.single_cell_span_mm)

        return x_offset, y_offset

    def create_model_from_tray_object(self):
        tray_model = cq.Workplane("XY") \
            .box(self.tray_container.width_mm, self.tray_container.length_mm, self.height_mm) \
            .edges("|Z") \
            .fillet(self.outer_radii)

        topleft_workplane = cq.Workplane("XY") \
            .transformed(offset=(0, 0, self.height_mm / 2)) \
            .center(-self.tray_container.width_mm / 2, self.tray_container.length_mm / 2) \
            .center(self.half_wall_thickness_mm, -self.half_wall_thickness_mm)
        # above is to complete first wall's thickness to full thickness and allow pattern of halfs to happen

        for tray_hole in self.tray_container.tray_holes.values():
            new_rect = topleft_workplane \
                .center(*self.calculate_middle_hole_pos_mm(tray_hole)) \
                .sketch() \
                .rect(*self.get_tray_hole_size_dimensions_mm(tray_hole)) \
                .vertices() \
                .fillet(self.holes_fillet_radius_mm) \
                .finalize() \
                .extrude(-(self.height_mm - self.half_wall_thickness_mm))

            tray_model = tray_model.cut(new_rect)

        return tray_model
