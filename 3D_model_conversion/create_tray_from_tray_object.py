import cadquery
from tray_logic.Tray_Container import Tray_Container

container = Tray_Container(200, 100)

rect = cadquery.result = cadquery.Workplane("top").box(container.width, container.length_in_mm, 5)

