from collections import namedtuple

IndexPos = namedtuple("IndexPos", ['XIndexPos', 'YIndexPos'])


class TrayHole:
    def __init__(self, top_left_index_pos: IndexPos, bottom_right_index_pos: IndexPos):
        if top_left_index_pos <= bottom_right_index_pos:
            self.top_left_index_pos = top_left_index_pos
            self.bottom_right_index_pos = bottom_right_index_pos
            # +1 is because the span includes the first cell itself
            self.x_cells_span = bottom_right_index_pos.XIndexPos - top_left_index_pos.XIndexPos + 1
            self.y_cells_span = bottom_right_index_pos.YIndexPos - top_left_index_pos.YIndexPos + 1
        else:
            # well have to see about that...
            raise Exception("cant define a hole other than top left to bottom right")
