import arcpy
import datetime as dt

import os
import math
import traceback
import sys
from arcpy import env

if __name__ == "__main__":

    ili_layer=r"C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\ILIData"
    
    try:

        arcpy.AddMessage("Process Started")
        arcpy.env.workspace=r"C:\G2\UnitedBrine\Anomaly Comparison\scratch.gdb"
        arcpy.env.overwriteOutput = True
        #arcpy.CopyRows_management(ili_layer, "PipeTally_Test")
        #arcpy.MakeXYEventLayer_management("PipeTally_Test", "POINT_X", "POINT_Y", "Anomaly_Point_Events")
        #arcpy.CopyFeatures_management("Anomaly_Point_Events", "Output_Anomaly_Point_Features")

        arcpy.management.CopyRows(ili_layer, "PipeTally_Test")
        arcpy.management.MakeXYEventLayer("PipeTally_Test", "POINT_X", "POINT_Y", "Anomaly_Point_Events")
        arcpy.management.CopyFeatures("Anomaly_Point_Events", "Output_Anomaly_Point_Features")

        
        arcpy.AddMessage("Process Completed")
    except Exception as e:
            tb = sys.exc_info()[2]
            arcpy.AddError("An error occurred on line %i" % tb.tb_lineno)
            arcpy.AddError(str(e))
            








