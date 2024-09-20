from collections import namedtuple

IndexPos = namedtuple("IndexPos", ['XIndexPos','YIndexPos'])


class TrayHole():
    def __init__(self, top_left_index_pos:IndexPos, bottom_right_index_pos:IndexPos):
        if top_left_index_pos <= bottom_right_index_pos:
            self.top_left_index_pos = top_left_index_pos
            self.bottom_right_index_pos = bottom_right_index_pos
        else:
            raise Exception("cant define a hole other than top left to bottom right")