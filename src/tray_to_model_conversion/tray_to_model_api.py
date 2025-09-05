import os
import pprint

from flask import Flask, send_file, request
import cadquery as cq

from src.tray_logic.TrayHole import TrayHole, IndexPos
from src.tray_logic.traycontainer import TrayContainer
from src.tray_to_model_conversion.create_tray_from_tray_object import trayToModelConverter

PATH_TO_MODEL = r"..\pooped_models\tray_model.stl"
app = Flask(__name__)


# request should be in this format(send in postman for testing):
#########################################
# {
#    "trayWidth": 200,
#    "trayHeight": 120,
#    "trayHoles": [
#        {
#            "TopLeftX": 1,
#            "TopLeftY": 1,
#            "BottomRightX": 1,
#            "BottomRightY":1
#        }
#    ]
# }
########################################
@app.route('/create_model_from_tray_object', methods=['POST'])
def create_create_model_from_tray_object():
    data = request.json
    tray_width: float = data.get('trayWidth')
    tray_height: float = data.get('trayHeight')
    tray_holes: list(TrayHole) = [TrayHole(IndexPos(tray_hole.get('TopLeftX'), tray_hole.get('TopLeftY')),
                                           IndexPos(tray_hole.get('BottomRightX'), tray_hole.get('BottomRightY')))
                                  for tray_hole in data.get('trayHoles')]

    tray_container = TrayContainer(tray_width, tray_height)
    for tray_hole in tray_holes:
        tray_container.add_hole(tray_hole)

    tray_model = trayToModelConverter(tray_container).create_model_from_tray_object()
    cq.exporters.export(tray_model, PATH_TO_MODEL)
    return send_file(PATH_TO_MODEL, as_attachment=True)


app.run(debug=True)
