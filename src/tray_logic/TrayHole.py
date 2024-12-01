from collections import namedtuple

IndexPos = namedtuple("IndexPos", ['XIndexPos', 'YIndexPos'])


class TrayHole():
    def __init__(self, top_left_index_pos: IndexPos, bottom_right_index_pos: IndexPos):
        if top_left_index_pos <= bottom_right_index_pos:
            self.top_left_index_pos = top_left_index_pos
            self.bottom_right_index_pos = bottom_right_index_pos
            self.x_cells_span = top_left_index_pos.XIndexPos - bottom_right_index_pos.XIndexPos
            self.y_cells_span = top_left_index_pos.YIndexPos - bottom_right_index_pos.YIndexPos
        else:
            # well have to see about that...
            raise Exception("cant define a hole other than top left to bottom right")
