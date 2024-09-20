from traycontainer import TrayContainer
import pprint
from src.tray_logic.TrayHole import TrayHole,IndexPos

container = TrayContainer(200, 120)
container.add_hole(TrayHole(IndexPos(0,0),IndexPos(2,3)))
container.add_hole(TrayHole(IndexPos(3,4),IndexPos(4,5)))
container.add_hole(TrayHole(IndexPos(2,4),IndexPos(2,4)))
[print(tray_hole.top_left_index_pos,tray_hole.bottom_right_index_pos) for tray_hole in container.tray_holes]

container.add_hole(TrayHole(IndexPos(2,4),IndexPos(1,5)))
