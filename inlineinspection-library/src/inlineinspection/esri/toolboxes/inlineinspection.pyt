#import arcpy

from inlineinspection.pressurecalculator.pressurecalculator import PressureCalculator

class Toolbox(object):

    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""

        self.label = "In Line Inspection Tools"
        self.alias = "inlineinspection"

        # List of tool classes associated with this toolbox
        self.tools = [PressureCalculator             
                      ]
