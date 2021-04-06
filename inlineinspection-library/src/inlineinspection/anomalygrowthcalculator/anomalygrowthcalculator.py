
""" Headline: Anomaly Processing Inline Inspection Anomaly Growth Caliculation tool 
    Calls:  inlineinspection, inlineinspection.config
    inputs: ILI Feature class(Which is calibrated and imported)
    Description: This tool calculates Anomaly Growth.  
    Output: The output of this tool.
   """

from logging import exception
import arcpy
import inlineinspection
import os
import datetime as dt
import math
from inlineinspection import config
import traceback
import sys
from arcpy import env


class AnomalyGrowthCalculator(object):

    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "ILI Anomaly Growth Calculator"
        self.description = "This Tool Caliculates Anomaly Growth"
        self.canRunInBackground = False
        #self.category = config.ILI_PC_TOOL_CATAGORY  
               
    def getParameterInfo(self):
               
        # Input ILI point featuere - Parameter [0]       
        in_ili_features = arcpy.Parameter(displayName="Input ILI Anomaly Features",
            name="in_ili_features",
            datatype=["GPFeatureLayer","GPTableView"],
            parameterType="Required",
            direction="Input")
        #in_ili_features.filter.list = ["Point"]

        in_ili_odometer_field = arcpy.Parameter(
            displayName="ILI Anomaly Odometer Field", name="in_ili_odometer_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_ili_odometer_field.parameterDependencies = [in_ili_features.name]       
        in_ili_odometer_field.filter.list = ['int', 'long', 'double']

        in_ili_width_field = arcpy.Parameter(
            displayName="ILI Anomaly Width Field", name="in_ili_width_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_ili_width_field.parameterDependencies = [in_ili_features.name]
        in_ili_width_field.filter.list = ['int', 'long', 'double']

        in_ili_length_field = arcpy.Parameter(
            displayName="ILI Anomaly Length Field", name="in_ili_length_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_ili_length_field.parameterDependencies = [in_ili_features.name]       
        in_ili_length_field.filter.list = ['int', 'long', 'double']
        
        out_grid_features = arcpy.Parameter(displayName="Output Grid Line Features",
            name="out_grid_features",
            datatype="GPFeatureLayer",
            parameterType="Optional",
            direction="Output")
        #out_grid_features.filter.list = ["Polyline"]
        out_grid_features.value ="%scratchGDB%\GridLines"

        parameters = [in_ili_features,
                      in_ili_odometer_field,
                      in_ili_pipediameter_field,
                      in_ili_width_field,
                      in_ili_length_field,
                      out_grid_features
                      ]

        return parameters

    def isLicensed(self):  # optional
        return True
        #return LicenseOperation.is_licensed

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):  
        return

    def execute(self, parameters, messages):
               
        arcpy.AddMessage("Log file location: " + inlineinspection.GetLogFileLocation())
        inlineinspection.AddMessage("Starting Anomaly Growth Calculator process...")

        try:          
            ili_inputpoint_fc = parameters[0].valueAsText 
            is_grid_line = parameters[14].value
            is_weld_line = parameters[16].value
            
            if(arcpy.Exists(ili_inputpoint_fc)):                  
                ilicount = int(arcpy.GetCount_management(ili_inputpoint_fc).getOutput(0))                 
                if (ilicount > 0):                      
                    inlineinspection.AddMessage("Record count for ILI {}".format(ilicount))                    
                else:
                    inlineinspection.AddWarning("There is no records to perform Anomaly Growth.")
            else:
                    inlineinspection.AddWarning("There is no feature class for Anomaly Growth.")
            inlineinspection.AddMessage("Completed Anomaly Growth Calculator process.")
            return

        except Exception as e:
            tb = sys.exc_info()[2]
            inlineinspection.AddError("An error occurred on line %i" % tb.tb_lineno)
            inlineinspection.AddError(str(e))

   