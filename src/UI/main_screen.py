from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QVBoxLayout, QPushButton, QLineEdit, \
    QHBoxLayout, QFrame, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QColor, QPalette
import sys
import os

from cadquery import exporters

import src.tray_logic.conf as conf

from src.tray_logic.TrayHole import IndexPos, TrayHole
from src.tray_logic.traycontainer import TrayContainer
from src.tray_to_model_conversion.create_tray_from_tray_object import trayToModelConverter

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

        if event.button() == Qt.RightButton:
            self.controller.delete_cell_group(self)

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
        self.setStyleSheet("border: 6px solid black;")
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
        self.tray_container: TrayContainer | None = None
        self.install_location = os.getcwd()

        self.setWindowTitle("Grid Page")
        self.setMinimumSize(600, 600)

        self.layout = QVBoxLayout()

        self.title_label = QLabel("Grid Creator")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        self.info_label = QLabel("Left click on cell to start bounding box\nLeft click another cell (or self) to complete bounding box\nRight click to delete bounding box")
        self.info_label.setAlignment(Qt.AlignLeft)
        self.info_label.setStyleSheet("font-size: 10px;")
        self.layout.addWidget(self.info_label)

        input_layout = QHBoxLayout()
        self.height_in_mm_input = QLineEdit()
        self.height_in_mm_input.setPlaceholderText("Height in mm")
        self.width_in_mm_input = QLineEdit()
        self.width_in_mm_input.setPlaceholderText("Width in mm")

        input_layout.addWidget(self.height_in_mm_input)
        input_layout.addWidget(self.width_in_mm_input)
        self.layout.addLayout(input_layout)

        optional_layout = QHBoxLayout()
        self.depth_in_mm_input = QLineEdit()
        self.depth_in_mm_input.setPlaceholderText(
            f"depth in mm (default {conf.DEFAULT_TRAY_DEPTH_MM}mm)")
        self.wall_thickness_in_mm_input = QLineEdit()
        self.wall_thickness_in_mm_input.setPlaceholderText(
            f"wall thickness in mm (default {conf.DEFAULT_TRAY_HALF_WALL_THICKNESS_MM * 2}mm)")
        self.fillet_radius_in_mm_input = QLineEdit()
        self.fillet_radius_in_mm_input.setPlaceholderText(
            f"fillet radius in mm (default {conf.DEFAULT_TRAY_FILLET_RADIUS_MM}mm)")

        optional_layout.addWidget(self.depth_in_mm_input)
        optional_layout.addWidget(self.wall_thickness_in_mm_input)
        optional_layout.addWidget(self.fillet_radius_in_mm_input)
        self.layout.addLayout(optional_layout)

        self.toggle_button = QPushButton("Generate Grid")
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_grid)
        self.layout.addWidget(self.toggle_button)

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(CELL_SPACING)
        self.grid_layout.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.grid_container.setLayout(self.grid_layout)
        self.layout.addWidget(self.grid_container, 3)

        self.generate_model_button = QPushButton("Generate model as STL")
        self.generate_model_button.setEnabled(False)
        self.generate_model_button.setVisible(False)
        self.generate_model_button.clicked.connect(self.download_stl_to_folder_from_ui_grid)
        self.layout.addWidget(self.generate_model_button)

        self.setLayout(self.layout)

    def toggle_grid(self):
        if self.grid_visible:
            self.tray_container = None

            self.clear_grid()

            self.toggle_button.setText("Generate Grid")

            self.update_generate_grid_pressability()
            self.generate_model_button.setVisible(False)

            self.grid_visible = False
        else:
            try:
                width_in_mm = int(self.width_in_mm_input.text())
                height_in_mm = int(self.height_in_mm_input.text())
                self.tray_container = TrayContainer(width_in_mm, height_in_mm)
                self.build_grid(self.tray_container.Y_Cells, self.tray_container.X_Cells)

                self.toggle_button.setText("Clear Grid")

                self.generate_model_button.setVisible(True)

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

    def are_all_cells_selected(self):
        total_cells = len(self.cells)
        selected_cells = sum(cell.selected for cell in self.cells.values())
        return total_cells == selected_cells

    def update_generate_grid_pressability(self):
        if self.are_all_cells_selected():
            self.generate_model_button.setEnabled(True)
        else:
            self.generate_model_button.setEnabled(False)

    def cell_clicked(self, cell):
        if cell.selected:
            self.selected_pair.append(cell)

        else:
            self.selected_pair.append(cell)
            cell.select()

        if len(self.selected_pair) == 2:
            self.select_rectangle()

        self.update_generate_grid_pressability()

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

    def delete_cell_group(self, cell):
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

        self.tray_container.remove_hole(IndexPos(x1, y1))

        self.update_generate_grid_pressability()

    def download_stl_to_folder_from_ui_grid(self):
        # this is such a haltura
        all_cell_rect_groups = [cell.rect_group for cell in self.cells.values()]
        distnct_cell_groups = list(set(all_cell_rect_groups))
        # this is in format Y1,X1,Y2,X2 because of what chatgpt did
        tray_holes = [TrayHole(IndexPos(group[1], group[0]), IndexPos(group[3], group[2])) for group in
                      distnct_cell_groups]
        for tray_hole in tray_holes:
            print(tray_hole)
            self.tray_container.add_hole(tray_hole)

        custom_values = {self.depth_in_mm_input: conf.DEFAULT_TRAY_DEPTH_MM,
                         self.fillet_radius_in_mm_input: conf.DEFAULT_TRAY_FILLET_RADIUS_MM,
                         self.wall_thickness_in_mm_input: conf.DEFAULT_TRAY_HALF_WALL_THICKNESS_MM * 2}

        for value in custom_values.keys():
            try:
                custom_values[value] = float(value.text().strip())
            except ValueError:
                pass

        # print(self.tray_container.tray_holes)
        model = trayToModelConverter(self.tray_container,
                                     depth_in_mm=custom_values[self.depth_in_mm_input],
                                     tray_hole_fillet_radius_mm=custom_values[self.fillet_radius_in_mm_input],
                                     half_wall_thickness_in_mm=custom_values[self.wall_thickness_in_mm_input] / 2) \
            .create_model_from_tray_object()

        output_dir = os.path.join(os.getcwd(), "pooped_models")
        os.makedirs(output_dir, exist_ok=True)  # Ensure folder exists

        output_path = os.path.join(output_dir, "bruh.stl")
        print(output_path)
        print(model)
        exporters.export(model, output_path)

        print(f"Exported to {output_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GridController()
    window.show()
    sys.exit(app.exec())
