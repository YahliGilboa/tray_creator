from src.tray_logic.TrayHole import TrayHole, IndexPos
from src.tray_to_model_conversion.create_tray_from_tray_object import trayToModelConverter
from traycontainer import TrayContainer
import cadquery as cq

tray_object = TrayContainer(200, 120)
tray_object.add_hole(TrayHole(IndexPos(0, 0), IndexPos(2, 3)))
tray_object.add_hole(TrayHole(IndexPos(3, 4), IndexPos(4, 5)))
tray_object.add_hole(TrayHole(IndexPos(2, 4), IndexPos(2, 4)))
[print(tray_hole.top_left_index_pos, tray_hole.bottom_right_index_pos) for tray_hole in tray_object.tray_holes]

tray_model = trayToModelConverter(tray_object).create_model_from_tray_object()
cq.exporters.export(tray_model, "pooped_models\\good_shit.stl")
