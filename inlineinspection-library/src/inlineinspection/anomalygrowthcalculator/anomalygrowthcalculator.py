
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
import numpy as np
import math
from inlineinspection import config
import traceback
import sys
import locale
from arcpy import env


class AnomalyGrowthCalculator(object):

    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Convert ILI Anomalies to Features"
        self.description = "This to Tools Convert ILI Anomalies to Point, Envelopes and Eclipese Features"
        self.canRunInBackground = False
        #self.category = config.ILI_PC_TOOL_CATAGORY  
               
    def getParameterInfo(self):
               
        # Input ILI point featuere - Parameter [0]       
        in_ili_features = arcpy.Parameter(displayName="Input ILI Features",
            name="in_ili_features",
            datatype=["GPFeatureLayer","GPTableView"],
            parameterType="Required",
            direction="Input")
        #in_ili_features.filter.list = ["Point"]

        in_ili_odometer_field = arcpy.Parameter(
            displayName="Input ILI Pipe Tally Odometer Field", name="in_ili_odometer_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_ili_odometer_field.parameterDependencies = [in_ili_features.name]       
        in_ili_odometer_field.filter.list = ['int', 'long', 'double']

        in_ili_width_field = arcpy.Parameter(
            displayName="Input ILI Pipe Tally Anomaly Width Field", name="in_ili_width_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_ili_width_field.parameterDependencies = [in_ili_features.name]
        in_ili_width_field.filter.list = ['int', 'long', 'double']


        in_ili_length_field = arcpy.Parameter(
            displayName="Input ILI Pipe Tally Anomaly Length Field", name="in_ili_length_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_ili_length_field.parameterDependencies = [in_ili_features.name]       
        in_ili_length_field.filter.list = ['int', 'long', 'double']
        
        in_ili_clockposition_field = arcpy.Parameter(
            displayName="Input ILI Pipe Tally Clock Position Field", name="in_ili_clockposition_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_ili_clockposition_field.parameterDependencies = [in_ili_features.name]
        in_ili_clockposition_field.filter.list = ['int', 'long', 'double']

        in_ili_clockpostion_offset_value = arcpy.Parameter(
            displayName="Input Clock Position Offset", name="in_ili_clockpostion_offset_value",
            datatype="GPDouble", parameterType="optional", direction="Input")

        in_ili_yaxisorientation_value = arcpy.Parameter(
            displayName="Input Y-Axis Clock Orientation", name="in_ili_yaxisorientation_value",
            datatype="GPString", parameterType="optional", direction="Input")
        in_ili_yaxisorientation_value.filter.list=["6:00 Centered","12:00 Centered"]
       
        in_ili_pipediameter_field = arcpy.Parameter(
            displayName="Input Pipeline Diameter Field", name="in_ili_pipediameter_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_ili_pipediameter_field.parameterDependencies = [in_ili_features.name]
        in_ili_pipediameter_field.filter.list = ['int', 'long', 'double']

        in_ili_falsenorthing_value = arcpy.Parameter(
            displayName="Input Clock Position Offset", name="in_ili_falsenorthing_value",
            datatype="GPDouble", parameterType="optional", direction="Input")

        in_ili_falseeasting_value = arcpy.Parameter(
            displayName="Input Clock Position Offset", name="in_ili_falseeasting_value",
            datatype="GPDouble", parameterType="optional", direction="Input")

        out_ili_point_features = arcpy.Parameter(displayName="Output Anomaly Point Features",
            name="out_ili_point_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        out_ili_point_features.filter.list = ["Point"]

        out_ili_ellipse_features = arcpy.Parameter(displayName="Output Anomaly Ellipse Features",
            name="out_ili_ellipse_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        out_ili_ellipse_features.filter.list = ["Point"]

        out_ili_envelop_features = arcpy.Parameter(displayName="Output Anomaly Envelop Features",
            name="out_ili_envelop_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        out_ili_envelop_features.filter.list = ["Point"]

        # Input Pipelie featuere - Parameter [11]    
        in_ili_sr = arcpy.Parameter(displayName="Spatial Refference for Output Features",
            name="in_ili_sr",
            datatype="GPSpatialReference",
            parameterType="Required",
            direction="Input")
        in_ili_sr.filter.value="NAD_1983_UTM_Zone_16N"
     
    
        parameters = [in_ili_features
                      ]

        return parameters

    def isLicensed(self):  # optional
        return True
        #return LicenseOperation.is_licensed

    def updateParameters(self, parameters):
        if(parameters[0].value):
            des = arcpy.Describe(parameters[0].value)          

        return

    def updateMessages(self, parameters):                     
        return

    def execute(self, parameters, messages):
        inlineinspection.AddMessage("Start Logging.")        
        arcpy.AddMessage("Log file location: " + inlineinspection.GetLogFileLocation())
        inlineinspection.AddMessage("Starting ILI Pressure Calculator process...")

        try:          
            ili_inputpoint_fc = parameters[0].valueAsText                       
            if(arcpy.Exists(ili_inputpoint_fc)):                  
                ilicount = int(arcpy.GetCount_management(ili_inputpoint_fc).getOutput(0))  
                inlineinspection.AddMessage("Record count for ILI Pressure Calculator {}".format(ilicount))
                if (ilicount > 0):  
                    inlineinspection.AddMessage("Processing")
                   
                else:
                    inlineinspection.AddWarning("There is no records to perform Pressure Calculation.")
            else:
                    inlineinspection.AddWarning("There is no feature class for Pressure Calculation.")
            inlineinspection.AddMessage("Finished ILI Pressure Calculator process.")
            return

        except Exception as e:
            tb = sys.exc_info()[2]
            arcpy.AddError("An error occurred on line %i" % tb.tb_lineno)
            arcpy.AddError(str(e))

    def param_changed(self, param, check_value=False):
        changed = param.altered and not param.hasBeenValidated
        if check_value:
            if param.value:
                return changed
            else:
                return False
        else:
            return changed

   