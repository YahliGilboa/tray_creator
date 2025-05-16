from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPalette
import sys

class GridCell(QLabel):
    def __init__(self, row, col, controller):
        super().__init__()
        self.row = row
        self.col = col
        self.controller = controller
        self.selected = False
        self.rect_group = None

        self.setFixedSize(40, 40)
        self.setAutoFillBackground(True)
        self.set_default_color()
        self.setFrameStyle(QLabel.Box | QLabel.Plain)
        self.setLineWidth(1)

    def set_default_color(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setPalette(palette)

    def set_hover_color(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("cyan"))
        self.setPalette(palette)

    def set_selected_color(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("blue"))
        self.setPalette(palette)

    def enterEvent(self, event):
        if not self.selected:
            self.set_hover_color()

    def leaveEvent(self, event):
        if not self.selected:
            self.set_default_color()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.controller.cell_clicked(self)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.controller.cell_double_clicked(self)

    def select(self):
        self.selected = True
        self.set_selected_color()

    def deselect(self):
        self.selected = False
        self.rect_group = None
        self.set_default_color()

class GridController(QWidget):
    def __init__(self, rows=10, cols=10):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.cells = {}
        self.selected_pair = []
        self.rectangles = []

        self.setWindowTitle("Grid Page")
        self.setMinimumSize(600, 600)

        layout = QVBoxLayout()
        self.grid_layout = QGridLayout()
        layout.addLayout(self.grid_layout)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)
        self.build_grid()

    def build_grid(self):
        for i in range(self.rows):
            for j in range(self.cols):
                cell = GridCell(i, j, self)
                self.grid_layout.addWidget(cell, i, j)
                self.cells[(i, j)] = cell

    def cell_clicked(self, cell):
        if cell.selected and cell.rect_group:
            return

        if not cell.selected:
            cell.select()
            self.selected_pair.append(cell)

        if len(self.selected_pair) == 2:
            self.select_rectangle()

    def select_rectangle(self):
        c1, c2 = self.selected_pair
        x1, y1 = min(c1.row, c2.row), min(c1.col, c2.col)
        x2, y2 = max(c1.row, c2.row), max(c1.col, c2.col)

        rect = []
        for i in range(x1, x2 + 1):
            for j in range(y1, y2 + 1):
                cell = self.cells[(i, j)]
                cell.select()
                cell.rect_group = (x1, y1, x2, y2)
                rect.append(cell)

        self.rectangles.append(rect)
        self.selected_pair.clear()

    def cell_double_clicked(self, cell):
        if not cell.rect_group:
            return

        x1, y1, x2, y2 = cell.rect_group
        for i in range(x1, x2 + 1):
            for j in range(y1, y2 + 1):
                target = self.cells[(i, j)]
                target.deselect()

        self.rectangles = [r for r in self.rectangles if cell not in r]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GridController()
    window.show()
    sys.exit(app.exec())
