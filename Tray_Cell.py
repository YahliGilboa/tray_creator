from Rectangle import Rectangle

class Tray_Cell():
    def __init__(self):
        self.is_occupied = False

    def occupy(self):
        self.is_occupied = True

    def unoccupy(self):
        self.is_occupied = False