from Rectangle import Rectangle
from Tray_Cell import Tray_Cell
import math
import conf
from Tray_Cell import Tray_Cell


class Tray_Container(Rectangle):
    # this is cell clumps, but ill call it hole because this will generate it
    tray_holes = []
    X_Cells = 0
    Y_Cells = 0

    def __init__(self, width_in_mm, height_in_mm):
        super().__init__(width_in_mm, height_in_mm)
        # self.grid_cell_amounts = {'width_cell_amount': 0, 'height_cell_amount': 0}
        self.X_Cells, self.Y_Cells = self.calculate_cell_matrix(width_in_mm, height_in_mm)

    def calculate_cell_matrix(self, width_in_mm, height_in_mm):
        if self.width <= self.height:
            width_height_dict = self.calclate_correct_cell_amount(conf.MIN_SMALL_SIDE_CELL_AMOUNT,
                                                                  height_in_mm / width_in_mm)
            width_in_mm = int(width_height_dict[0])
            height_in_mm = int(width_height_dict[1])
            return width_in_mm, height_in_mm
        else:
            width_height_dict = self.calclate_correct_cell_amount(conf.MIN_SMALL_SIDE_CELL_AMOUNT,
                                                                  width_in_mm / height_in_mm)
            height_in_mm = int(width_height_dict[0])
            width_in_mm = int(width_height_dict[1])
            return width_in_mm, height_in_mm

    def calclate_correct_cell_amount(self, min_small_side_cells, big_to_small_ratio):
        small_side_cells = min_small_side_cells
        while True:
            big_side_cells = big_to_small_ratio * small_side_cells
            if not big_side_cells.is_integer():
                small_side_cells += 1
            else:
                return small_side_cells, big_side_cells

    # def add_hole(self):

# def generate_matrix_from_width_height(self,width,height):
#     return [[Tray_Cell()] * int(width)] * int(height)
