from Rectangle import Rectangle
from Tray_Cell import Tray_Cell
import math
import conf
from Tray_Cell import Tray_Cell

class Tray_Container(Rectangle):
    tray_cells = []
    # this is cell clumps, but ill call it hole because this will generate it
    tray_holes = []

    def __init__(self,width,height):
        super().__init__(width,height)
        self.tray_cells = self.calculate_cell_matrix(width,height)

    def calculate_cell_matrix(self,width,height):
        if self.width <= self.height:
           width_height_dict = self.calclate_correct_cell_amount(conf.MIN_SIDE_CELL_AMOUNT,height/width)
           return self.generate_matrix_from_width_height(width_height_dict['small_side'],width_height_dict['big_side'])

        width_height_dict = self.calclate_correct_cell_amount(conf.MIN_SIDE_CELL_AMOUNT,width/height)
        return self.generate_matrix_from_width_height(width_height_dict['big_side'],width_height_dict['small_side'])

    def calclate_correct_cell_amount(self,small_side_cells,big_to_small_ratio):
        while True:
            big_side_cells = big_to_small_ratio * small_side_cells
            if not big_side_cells.is_integer():
                small_side_cells += 1
            else:
                return {'small_side':small_side_cells,'big_side':big_side_cells}

    def generate_matrix_from_width_height(self,width,height):
        return [[0] * int(width)] * int(height)


