from src.tray_logic.TrayHole import TrayHole, IndexPos
from src.tray_to_model_conversion.create_tray_from_tray_object import trayToModelConverter
from traycontainer import TrayContainer
import cadquery as cq

tray_object = TrayContainer(200, 120)
tray_object.add_hole(TrayHole(IndexPos(0, 0), IndexPos(0, 0)))
tray_object.add_hole(TrayHole(IndexPos(1, 0), IndexPos(2, 0)))
tray_object.add_hole(TrayHole(IndexPos(0, 1), IndexPos(2, 2)))
tray_object.add_hole(TrayHole(IndexPos(0, 3), IndexPos(3, 6)))
tray_object.add_hole(TrayHole(IndexPos(24, 0), IndexPos(24, 0)))
try:
    tray_object.add_hole(TrayHole(IndexPos(25, 0), IndexPos(25, 0)))
except Exception:
    print(Exception)

[print(tray_hole.top_left_index_pos, tray_hole.bottom_right_index_pos) for tray_hole in tray_object.tray_holes]

tray_model = trayToModelConverter(tray_object).create_model_from_tray_object()
cq.exporters.export(tray_model, "pooped_models\\bruh.stl")
