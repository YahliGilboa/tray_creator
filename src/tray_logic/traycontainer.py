from src.tray_logic.TrayHole import TrayHole, IndexPos
import src.tray_logic.conf as conf


class TrayContainer:
    tray_holes: dict[IndexPos, TrayHole] = {}
    X_Cells: int
    Y_Cells: int

    def __init__(self, width_in_mm: float, length_in_mm: float):
        self.width_mm: float = width_in_mm
        self.length_mm: float = length_in_mm
        self.X_Cells, self.Y_Cells = self.calculate_cell_matrix(width_in_mm, length_in_mm)

    def calculate_cell_matrix(self, width_in_mm: float, length_in_mm: float):
        if self.width_mm <= self.length_mm:
            width_and_length = self.calclate_correct_cell_amount(conf.MIN_SMALL_SIDE_CELL_AMOUNT,
                                                                 length_in_mm / width_in_mm)
            x_cells = int(width_and_length[0])
            y_cells = int(width_and_length[1])
            return x_cells, y_cells
        else:
            width_and_length = self.calclate_correct_cell_amount(conf.MIN_SMALL_SIDE_CELL_AMOUNT,
                                                                 width_in_mm / length_in_mm)
            x_cells = int(width_and_length[1])
            y_cells = int(width_and_length[0])

            return x_cells, y_cells

    def calclate_correct_cell_amount(self, min_small_side_cells: int, big_to_small_ratio: int) -> int:
        small_side_cells = min_small_side_cells
        while True:
            big_side_cells = big_to_small_ratio * small_side_cells
            if not big_side_cells.is_integer():
                small_side_cells += 1
            else:
                return small_side_cells, big_side_cells

    def add_hole(self, tray_hole: TrayHole):
        if self.hole_intersects_existing_hole(tray_hole):
            raise Exception("cant create two intersecting holes")

        if self.hole_out_of_bounds(tray_hole):
            raise Exception("cant create hole out of bounds")

        self.tray_holes[tray_hole.top_left_index_pos] = tray_hole

    def remove_hole(self, top_left_index_pos: IndexPos):
        if top_left_index_pos in self.tray_holes:
            self.tray_holes.pop(top_left_index_pos)

    def hole_out_of_bounds(self, tray_hole: TrayHole) -> bool:
        if tray_hole.top_left_index_pos.XIndexPos + 1 > self.X_Cells or tray_hole.top_left_index_pos.XIndexPos < 0:
            return True

        if tray_hole.bottom_right_index_pos.XIndexPos + 1 > self.X_Cells or tray_hole.bottom_right_index_pos.XIndexPos < 0:
            return True

        if tray_hole.top_left_index_pos.YIndexPos + 1 > self.Y_Cells or tray_hole.top_left_index_pos.YIndexPos < 0:
            return True

        if tray_hole.bottom_right_index_pos.YIndexPos + 1 > self.Y_Cells or tray_hole.bottom_right_index_pos.YIndexPos < 0:
            return True

        return False

    def hole_intersects_existing_hole(self, new_tray_hole: TrayHole) -> bool:
        tray_hole_intersect = False
        for hole in self.tray_holes.values():
            x_not_intersect = new_tray_hole.top_left_index_pos.XIndexPos > hole.bottom_right_index_pos.XIndexPos or \
                              new_tray_hole.bottom_right_index_pos.XIndexPos < hole.top_left_index_pos.XIndexPos

            y_not_intersect = new_tray_hole.top_left_index_pos.YIndexPos > hole.bottom_right_index_pos.YIndexPos or \
                              new_tray_hole.bottom_right_index_pos.YIndexPos < hole.top_left_index_pos.YIndexPos

            if not (x_not_intersect or y_not_intersect):
                tray_hole_intersect = True
        return tray_hole_intersect
