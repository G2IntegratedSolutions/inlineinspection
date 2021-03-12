
""" Headline: Anomaly Processing Inline Inspection Anomaly Comparer tool 
    Calls:  inlineinspection, inlineinspection.config
    inputs: ILI Anomaly Ellipse from current and previous years.
    Description: This tool Compares Anomaly.  
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


class AnomalyComparer(object):

    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Anomalies Comparer"
        self.description = "This Tool Compares ILI Anomalies"
        self.canRunInBackground = False
        #self.category = config.ILI_PC_TOOL_CATAGORY  
               
    def getParameterInfo(self):
            
        in_dataset61_features = arcpy.Parameter(category =config.ILI_ANOM_CLOCK_POSITION[0],displayName="Input ILI Anomaly Ellipse Dataset 1 Features",
            name="in_dataset61_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        in_dataset61_features.filter.list = ["Polygon"]

        in_dataset62_features = arcpy.Parameter(category =config.ILI_ANOM_CLOCK_POSITION[0],displayName="Input ILI Anomaly Ellipse Dataset 2 Features",
            name="in_dataset62_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        in_dataset62_features.filter.list = ["Polygon"]

        in_dataset121_features = arcpy.Parameter(category =config.ILI_ANOM_CLOCK_POSITION[1],displayName="Input ILI Anomaly Ellipse Dataset 1 Features",
            name="in_dataset121_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        in_dataset121_features.filter.list = ["Polygon"]

        in_dataset122_features = arcpy.Parameter(category =config.ILI_ANOM_CLOCK_POSITION[1],displayName="Input ILI Anomaly Ellipse Dataset 2 Features",
            name="in_dataset122_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        in_dataset122_features.filter.list = ["Polygon"]

        in_uniqueid_field = arcpy.Parameter(
            displayName="Anomaly Unique ID Field", name="in_uniqueid_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_uniqueid_field.parameterDependencies = [in_dataset122_features.name]
        in_uniqueid_field.filter.list = ['guid']
                
        in_search_distance = arcpy.Parameter(
            displayName="Search Distance",
            name="in_search_distance",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction="Input")
        in_search_distance.value = '.25 Feet'        
        in_search_distance.filter.list = ['Kilometers', 'Miles', 'Meters', 'Feet']     
                
        out_comparer_features = arcpy.Parameter(displayName="Output Anomaly Comparer Table",
            name="out_comparer_features",
            datatype="GPTableView",
            parameterType="Optional",
            direction="Output")       
        out_comparer_features.value ="%scratchGDB%\AnomalyComparer"
               
        parameters = [in_dataset61_features,
                        in_dataset62_features,
                        in_dataset121_features,
                        in_dataset122_features,
                        in_uniqueid_field,
                        in_search_distance,
                        out_comparer_features                        
                      ]

        return parameters

    def isLicensed(self):  # optional
        return True
        #return LicenseOperation.is_licensed

    def updateParameters(self, parameters):
        #Fill the fields after feature selection.
        if(parameters[3].value):
            flds = [] 
            fc=parameters[3].value
            if(fc):
                fls = []           
                fls += [f.name.upper() for f in arcpy.ListFields (fc)]
                
                flds=[]
                for f in fls:
                    x=f.split('.')
                    if len(x)>1:
                        x1=x[1]
                        flds.append(x1)
                    else:
                        flds.append(f)                    
              
            if not parameters[4].value:                
                if config.ILI_ANOM_CON_REQ_FIELDS[6].upper() in flds:
                    parameters[4].value = config.ILI_ANOM_CON_REQ_FIELDS[6]               
        return

    def updateMessages(self, parameters):  
        return

    def execute(self, parameters, messages):
               
        arcpy.AddMessage("Log file location: " + inlineinspection.GetLogFileLocation())
        inlineinspection.AddMessage("Starting Anomaly Compare process...")

        try:          
            ili_prior_anomaly_fc = parameters[0].valueAsText 
            ili_recent_anomaly_fc = parameters[1].valueAsText 
                        
            if(arcpy.Exists(ili_prior_anomaly_fc)):                  
                ilicount = int(arcpy.GetCount_management(ili_prior_anomaly_fc).getOutput(0))  
                #inlineinspection.AddMessage("Record count for ILI Pressure Calculator {}".format(ilicount))
                if (ilicount > 0): 
                    self.ILIAnomalyComparer(parameters)  
                else:
                    inlineinspection.AddWarning("There is no records to perform Anomaly Compare.")
            else:
                    inlineinspection.AddWarning("There is no feature class for Anomaly Compare.")
            inlineinspection.AddMessage("Completed Anomaly Compare process.")
            return

        except Exception as e:
            tb = sys.exc_info()[2]
            inlineinspection.AddError("An error occurred on line %i" % tb.tb_lineno)
            inlineinspection.AddError(str(e))

    def param_changed(self, param, check_value=False):
        changed = param.altered and not param.hasBeenValidated
        if check_value:
            if param.value:
                return changed
            else:
                return False
        else:
            return changed

    def ILIAnomalyComparer(self,parameters):
        try:

            inputPriorAnomalyFC = parameters[0].valueAsText            
            inputRecentAnomalyFC = parameters[1].valueAsText
            searchTolarance = parameters[5].valueAsText
            
            arcpy.env.overwriteOutput = True
            #Checking Near by features which are in specificed Tolarance
            AnomalyNearTable = fr"{arcpy.env.scratchGDB}\AnomalyNearTable"
            arcpy.analysis.GenerateNearTable(inputPriorAnomalyFC, inputRecentAnomalyFC, AnomalyNearTable, searchTolarance, "LOCATION", "ANGLE", "CLOSEST", 0, "GEODESIC")
            inlineinspection.AddMessage("Near Analysis is performed ")
            #Perform Statistics table to check what is the relation ship
            AnomalyStatisticsTable = fr"{arcpy.env.scratchGDB}\AnomalyStatisticsTable"
            arcpy.analysis.Statistics(AnomalyNearTable, AnomalyStatisticsTable, "NEAR_FID COUNT;IN_FID RANGE", "NEAR_FID")
            inlineinspection.AddMessage("Statistics Analysis is performed")                  
                       
            
        except Exception as e:
            tb = sys.exc_info()[2]
            inlineinspection.AddError("An error occurred on line %i" % tb.tb_lineno)
            inlineinspection.AddError(str(e))
            inlineinspection.AddError("Issue in ILI Anomaly 2 Geography.\n{}".format(arcpy.GetMessages(2)))
            return False