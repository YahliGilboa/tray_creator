from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QVBoxLayout, QPushButton, QLineEdit, \
    QHBoxLayout, QFrame, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QColor, QPalette
import sys

from tray_logic.traycontainer import TrayContainer

CELL_SIZE = 40
CELL_SPACING = 5  # Constant spacing


class GridCell(QLabel):
    def __init__(self, row, col, controller):
        super().__init__()
        self.row = row
        self.col = col
        self.controller = controller
        self.selected = False
        self.rect_group = None

        self.setFixedSize(CELL_SIZE, CELL_SIZE)
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


class BoundingBox(QFrame):
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        self.setStyleSheet("border: 2px solid black;")
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2


class GridController(QWidget):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.selected_pair = []
        self.rectangles = []
        self.bounding_boxes = []
        self.grid_visible = False
        self.tray_container = None

        self.setWindowTitle("Grid Page")
        self.setMinimumSize(600, 600)

        self.layout = QVBoxLayout()

        self.title_label = QLabel("Grid Creator")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        input_layout = QHBoxLayout()
        self.height_in_mm_input = QLineEdit()
        self.height_in_mm_input.setPlaceholderText("Height in mm")
        self.width_in_mm_input = QLineEdit()
        self.width_in_mm_input.setPlaceholderText("Width in mm")
        input_layout.addWidget(self.height_in_mm_input)
        input_layout.addWidget(self.width_in_mm_input)
        self.layout.addLayout(input_layout)

        self.toggle_button = QPushButton("Generate Grid")
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_grid)
        self.layout.addWidget(self.toggle_button)

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(CELL_SPACING)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.grid_container.setLayout(self.grid_layout)
        self.layout.addWidget(self.grid_container)

        self.setLayout(self.layout)

    def toggle_grid(self):
        if self.grid_visible:
            self.tray_container = None
            self.clear_grid()
            self.toggle_button.setText("Generate Grid")
            self.grid_visible = False
        else:
            try:
                width_in_mm = int(self.cols_input.text())
                height_in_mm = int(self.rows_input.text())
                self.tray_container = TrayContainer(width_in_mm,height_in_mm)
                self.build_grid(rows, cols)
                self.toggle_button.setText("Clear Grid")
                self.grid_visible = True
            except ValueError:
                pass

    def build_grid(self, rows, cols):
        self.cells = {}
        for i in range(rows):
            for j in range(cols):
                cell = GridCell(i, j, self)
                self.grid_layout.addWidget(cell, i, j)
                self.cells[(i, j)] = cell

    def clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        for _, _, _, _, box in self.bounding_boxes:
            box.deleteLater()
        self.cells.clear()
        self.selected_pair.clear()
        self.rectangles.clear()
        self.bounding_boxes.clear()

    def cell_clicked(self, cell):
        if cell.selected and cell.rect_group:
            return

        if not cell.selected:
            self.selected_pair.append(cell)
            cell.select()

        if len(self.selected_pair) == 2:
            self.select_rectangle()

    def select_rectangle(self):
        c1, c2 = self.selected_pair
        x1, y1 = min(c1.row, c2.row), min(c1.col, c2.col)
        x2, y2 = max(c1.row, c2.row), max(c1.col, c2.col)

        for i in range(x1, x2 + 1):
            for j in range(y1, y2 + 1):
                if self.cells[(i, j)].rect_group is not None:
                    self.selected_pair.clear()
                    return

        rect = []
        for i in range(x1, x2 + 1):
            for j in range(y1, y2 + 1):
                cell = self.cells[(i, j)]
                cell.select()
                cell.rect_group = (x1, y1, x2, y2)
                rect.append(cell)

        self.rectangles.append(rect)
        QTimer.singleShot(0, lambda: self.draw_bounding_box(x1, y1, x2, y2))
        self.selected_pair.clear()

    def draw_bounding_box(self, x1, y1, x2, y2):
        top_left = self.grid_layout.itemAtPosition(x1, y1).widget()
        bottom_right = self.grid_layout.itemAtPosition(x2, y2).widget()

        # Convert local position of top-left and bottom-right cells to global in container
        top_left_pos = top_left.mapTo(self, top_left.rect().topLeft())
        bottom_right_pos = bottom_right.mapTo(self, bottom_right.rect().bottomRight())

        x = top_left_pos.x()
        y = top_left_pos.y()
        w = bottom_right_pos.x() - x + 1
        h = bottom_right_pos.y() - y + 1

        box = BoundingBox(x1, y1, x2, y2)
        box.setParent(self)
        box.setGeometry(x, y, w, h)
        box.show()
        self.bounding_boxes.append((x1, y1, x2, y2, box))

    def cell_double_clicked(self, cell):
        if not cell.rect_group:
            return

        x1, y1, x2, y2 = cell.rect_group
        for i in range(x1, x2 + 1):
            for j in range(y1, y2 + 1):
                self.cells[(i, j)].deselect()

        self.rectangles = [r for r in self.rectangles if cell not in r]

        for info in self.bounding_boxes:
            if info[:4] == (x1, y1, x2, y2):
                info[4].deleteLater()
        self.bounding_boxes = [info for info in self.bounding_boxes if info[:4] != (x1, y1, x2, y2)]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GridController()
    window.show()
    sys.exit(app.exec())
