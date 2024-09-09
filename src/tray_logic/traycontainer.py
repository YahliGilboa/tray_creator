from TrayHole import TrayHole
import src.tray_logic.conf as conf


class TrayContainer():
    # this is cell clumps, but ill call it hole because this will generate it
    tray_holes: list[TrayHole] = []
    X_Cells = 0
    Y_Cells = 0

    def __init__(self, width_in_mm, length_in_mm, height_in_mm=conf.DEFAULT_TRAY_HEIGHT_MM,
                 wall_thickness_in_mm=conf.DEFAULT_TRAY_WALL_THICKNESS_MM):
        self.width_in_mm = width_in_mm
        self.length_in_mm = length_in_mm
        self.height_in_mm = height_in_mm
        self.wall_thickness_in_mm = wall_thickness_in_mm
        self.X_Cells, self.Y_Cells = self.calculate_cell_matrix(width_in_mm, length_in_mm)

    def calculate_cell_matrix(self, width_in_mm, length_in_mm):
        if self.width_in_mm <= self.length_in_mm:
            width_length_tuple = self.calclate_correct_cell_amount(conf.MIN_SMALL_SIDE_CELL_AMOUNT,
                                                                   length_in_mm / width_in_mm)
            x_cells = int(width_length_tuple[0])
            y_cells = int(width_length_tuple[1])
            return x_cells, y_cells
        else:
            width_length_tuple = self.calclate_correct_cell_amount(conf.MIN_SMALL_SIDE_CELL_AMOUNT,
                                                                   width_in_mm / length_in_mm)
            x_cells = int(width_length_tuple[0])
            y_cells = int(width_length_tuple[1])
            return x_cells, y_cells

    def calclate_correct_cell_amount(self, min_small_side_cells, big_to_small_ratio):
        small_side_cells = min_small_side_cells
        while True:
            big_side_cells = big_to_small_ratio * small_side_cells
            if not big_side_cells.is_integer():
                small_side_cells += 1
            else:
                return small_side_cells, big_side_cells

    def add_hole(self, tray_hole: TrayHole):
        if not self.tray_hole_intersect_existing(tray_hole):
            self.tray_holes.append(tray_hole)

    def tray_hole_intersect_existing(self, tray_hole: TrayHole) -> bool:
        tray_hole_intersect = False
        for hole in self.tray_holes:
            x_overlap = tray_hole.top_left_index_pos[0] >= hole.top_left_index_pos[0] or \
                        tray_hole.bottom_right_index_pos[0] <= hole.bottom_right_index_pos[0]

            y_overlap = tray_hole.top_left_index_pos[1] >= hole.top_left_index_pos[1] or \
                        tray_hole.bottom_right_index_pos[1] <= hole.bottom_right_index_pos[1]

            if x_overlap and y_overlap:
                tray_hole_intersect = True

        return tray_hole_intersect

    # def generate_matrix_from_width_height(self,width,height):
#     return [[Tray_Cell()] * int(width)] * int(height)
