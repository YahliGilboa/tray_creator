import cadquery as cq
from src.tray_logic.traycontainer import TrayContainer

container = TrayContainer(200, 100,)

rect = cq.Workplane("XY").box(container.width_in_mm, container.length_in_mm, container.height_in_mm)

cq.exporters.export(rect, "pooped_models\\result.stl")


