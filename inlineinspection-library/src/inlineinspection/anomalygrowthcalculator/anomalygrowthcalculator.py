
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
        self.label = "Convert ILI Anomalies to Point, Envelope and Ellipse Features"
        self.description = "This Tool Convert ILI Anomalies to Point, Envelopes and Eclipese Features"
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
            displayName="Input ILI Pipe Tally Odometer Field", name="in_ili_odometer_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_ili_odometer_field.parameterDependencies = [in_ili_features.name]       
        in_ili_odometer_field.filter.list = ['int', 'long', 'double']

        in_ili_width_field = arcpy.Parameter(
            displayName="Input ILI Pipe Tally Anomaly Width Field", name="in_ili_width_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_ili_width_field.parameterDependencies = [in_ili_features.name]
        in_ili_width_field.filter.list = ['int', 'long', 'double']

        in_ili_length_field = arcpy.Parameter(
            displayName="Input ILI Pipe Tally Anomaly Length Field", name="in_ili_length_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_ili_length_field.parameterDependencies = [in_ili_features.name]       
        in_ili_length_field.filter.list = ['int', 'long', 'double']
        
        in_ili_clockposition_field = arcpy.Parameter(
            displayName="Input ILI Pipe Tally Clock Position Field", name="in_ili_clockposition_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_ili_clockposition_field.parameterDependencies = [in_ili_features.name]
        in_ili_clockposition_field.filter.list = ['Text']

        in_ili_clockpostion_offset_value = arcpy.Parameter(
            displayName="Input Clock Position Offset", name="in_ili_clockpostion_offset_value",
            datatype="GPString", parameterType="Required", direction="Input")
        in_ili_clockpostion_offset_value.value="0:00"
         
        in_ili_yaxisorientation_value = arcpy.Parameter(
            displayName="Input Y-Axis Clock Orientation", name="in_ili_yaxisorientation_value",
            datatype="GPString", parameterType="Required", direction="Input")
        in_ili_yaxisorientation_value.filter.list=["6:00 Centered","12:00 Centered"]
        in_ili_yaxisorientation_value.value="6:00 Centered"
       
        in_ili_pipediameter_field = arcpy.Parameter(
            displayName="Input Pipeline Diameter Field", name="in_ili_pipediameter_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_ili_pipediameter_field.parameterDependencies = [in_ili_features.name]
        in_ili_pipediameter_field.filter.list = ['int', 'long', 'double']

        in_ili_falsenorthing_value = arcpy.Parameter(
            displayName="Input False Northing Value", name="in_ili_falsenorthing_value",
            datatype="GPDouble", parameterType="Required", direction="Input")
        in_ili_falsenorthing_value.value=0

        in_ili_falseeasting_value = arcpy.Parameter(
            displayName="Input False Easting Value", name="in_ili_falseeasting_value",
            datatype="GPDouble", parameterType="Required", direction="Input")
        in_ili_falseeasting_value.value=0
         
        in_ili_sr = arcpy.Parameter(displayName="Spatial Refference for Output Features",
            name="in_ili_sr",
            datatype="GPSpatialReference",
            parameterType="Required",
            direction="Input")
        in_ili_sr.value="PROJCS['NAD_1983_UTM_Zone_16N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',1640416.666666667],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-87.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Foot_US',0.3048006096012192]];-5120900 -9998100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"   
       
        out_ili_point_features = arcpy.Parameter(displayName="Output Anomaly Point Features",
            name="out_ili_point_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        out_ili_point_features.filter.list = ["Point"]
        out_ili_point_features.value="%scratchGDB%\AnomalyPoint"

        out_ili_ellipse_features = arcpy.Parameter(displayName="Output Anomaly Ellipse Features",
            name="out_ili_ellipse_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        out_ili_ellipse_features.filter.list = ["Polygon"]
        out_ili_ellipse_features.value ="%scratchGDB%\AnomalyEllipse"

        out_ili_envelop_features = arcpy.Parameter(displayName="Output Anomaly Envelop Features",
            name="out_ili_envelop_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        out_ili_envelop_features.filter.list = ["Polygon"]
        out_ili_envelop_features.value ="%scratchGDB%\AnomalyEnvelope"
         
        # Generate Grid Lines
        in_is_grid_line = arcpy.Parameter(
             displayName="Generate Grid Lines",
             name="in_is_grid_line",
             datatype="GPBoolean",  parameterType="Optional",
             direction="Input")
        in_is_grid_line.value = True

        out_grid_features = arcpy.Parameter(displayName="Output Grid Line Features",
            name="out_grid_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        out_grid_features.filter.list = ["Polyline"]
        out_grid_features.value ="%scratchGDB%\GridLines"

        # Generate Weld Lines
        in_is_weld_line = arcpy.Parameter(
             displayName="Generate Weld Lines",
             name="in_is_weld_line",
             datatype="GPBoolean",  parameterType="Optional",
             direction="Input")
        in_is_weld_line.value = True

        in_ili_weld_features = arcpy.Parameter(
            displayName="Input ILI Weld Features", name="in_ili_weld_features",
             datatype=["GPFeatureLayer","GPTableView"], parameterType="Optional", direction="Input")

        out_weld_features = arcpy.Parameter(displayName="Output Weld Line Features",
            name="out_weld_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        out_weld_features.filter.list = ["Polyline"]
        out_weld_features.value ="%scratchGDB%\WeldLines"

        parameters = [in_ili_features,
                      in_ili_odometer_field,
                      in_ili_width_field,
                      in_ili_length_field,
                      in_ili_clockposition_field,
                      in_ili_clockpostion_offset_value,                      
                      in_ili_yaxisorientation_value,
                      in_ili_pipediameter_field,
                      in_ili_falsenorthing_value,
                      in_ili_falseeasting_value,
                      in_ili_sr,                      
                      out_ili_point_features,
                      out_ili_ellipse_features,
                      out_ili_envelop_features,                      
                      in_is_grid_line,
                      out_grid_features,
                      in_is_weld_line,
                      in_ili_weld_features,
                      out_weld_features
                      ]

        return parameters

    def isLicensed(self):  # optional
        return True
        #return LicenseOperation.is_licensed

    def updateParameters(self, parameters):
        #Fill the fields after feature selection.
        if(parameters[0].value):
            flds = [] 
            fc=parameters[0].value
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
              
            if not parameters[1].value:                
                if config.ILI_ANOM_CON_REQ_FIELDS[0].upper() in flds:
                    parameters[1].value = config.ILI_ANOM_CON_REQ_FIELDS[0]
            if not parameters[2].value:                
                if config.ILI_ANOM_CON_REQ_FIELDS[1].upper() in flds:
                    parameters[2].value = config.ILI_ANOM_CON_REQ_FIELDS[1]
            if not parameters[3].value:
                if config.ILI_ANOM_CON_REQ_FIELDS[2].upper() in flds:
                    parameters[3].value = config.ILI_ANOM_CON_REQ_FIELDS[2]
            if not parameters[4].value:
                if config.ILI_ANOM_CON_REQ_FIELDS[3].upper() in flds:
                    parameters[4].value = config.ILI_ANOM_CON_REQ_FIELDS[3]
            if not parameters[7].value:
                if config.ILI_ANOM_CON_REQ_FIELDS[4].upper() in flds:
                    parameters[7].value = config.ILI_ANOM_CON_REQ_FIELDS[4]        
        
        #To enable Grid option based on the check box selection
        if(parameters[14].value):
            parameters[15].enabled = True
        else:
            parameters[15].enabled = False        

        #To enable Grid option based on the check box selection
        if(parameters[16].value):
            parameters[17].enabled = True
            parameters[18].enabled = True
        else:
            parameters[17].enabled = False
            parameters[18].enabled = False

        return

    def updateMessages(self, parameters):  
        if(parameters[0].value):
            if(parameters[16].Value):
                if not parameters[17].value:
                    parameters[17].setErrorMessage("Please select input Weld Featues/Table,\n As Generate Weld Option is selected.")
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
                #inlineinspection.AddMessage("Record count for ILI Pressure Calculator {}".format(ilicount))
                if (ilicount > 0):                      
                    #with arcpy.EnvManager(scratchWorkspace=r"C:\G2\UnitedBrine\Anomaly Comparison\Anomaly Comparison.gdb", workspace=r"C:\G2\UnitedBrine\Anomaly Comparison\Anomaly Comparison.gdb"): 
                    
                    #Generate Output point,llipse, Envelop for the Anamalies
                    self.ILIAnomaly2Geography(parameters)    
                    
                    #Genrate Grid lines only if the option is selected
                    if(is_grid_line):
                        self.iliGrid2Geography(parameters)
                    
                    #Genrate Weld lines only if the option is selected
                    if(is_weld_line):
                        self.iliWeld2Geography(parameters)
                else:
                    inlineinspection.AddWarning("There is no records to perform Anomaly Conversion.")
            else:
                    inlineinspection.AddWarning("There is no feature class for Anomaly Conversion.")
            inlineinspection.AddMessage("Completed Anomaly growth Calculator process.")
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

    def ILIAnomaly2Geography(self,parameters):
        try:

            Input_ILI_Pipe_Tally_Table = parameters[0].valueAsText
            Input_ILI_Pipe_Tally_Odometer_Field = parameters[1].valueAsText
            Input_ILI_Pipe_Tally_Anomaly_Width_Field = parameters[2].valueAsText
            Input_ILI_Pipe_Tally_Anomaly_Length_Field =parameters[3].valueAsText
            Input_ILI_Pipe_Tally_Clock_Position_Field =parameters[4].valueAsText
            Input_Clock_Position_Offset="\""+parameters[5].valueAsText+"\"" # "\"0:00\"" #parameters[5].valueAsText            
            Input_Y_Axis_Clock_Orientation= "\""+parameters[6].valueAsText+"\"" #parameters[6].valueAsText
            Input_Pipeline_Diameter_Value =parameters[7].valueAsText
            Input_False_Northing_Value=parameters[8].valueAsText
            Input_False_Easting_Value=parameters[9].valueAsText
            Spatial_Reference_for_Output_Features= parameters[10].valueAsText #"PROJCS['NAD_1983_UTM_Zone_16N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',1640416.666666667],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-87.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Foot_US',0.3048006096012192]];-5120900 -9998100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
            
            Output_Anomaly_Point_Features=parameters[11].valueAsText
            Output_Anomaly_Ellipse_Features=parameters[12].valueAsText 
            Output_Anomaly_Envelope_Features=parameters[13].valueAsText

            # Convert ILI Anomalies to Point, Envelope and Ellipse Features
            # To allow overwriting outputs change overwriteOutput option to True.
            arcpy.env.overwriteOutput = True

            #Select all the features which have clock position value            
            Input_ILI_Pipe_Tally_Table_View = arcpy.management.SelectLayerByAttribute(Input_ILI_Pipe_Tally_Table, "NEW_SELECTION", Input_ILI_Pipe_Tally_Clock_Position_Field +" IS NOT NULL",None)

            # Process: Copy Rows (Copy Rows) (management)
            Pipe_Tally_Table = fr"{arcpy.env.scratchGDB}\PipeTally"
            arcpy.management.CopyRows(in_rows=Input_ILI_Pipe_Tally_Table_View, out_table=Pipe_Tally_Table, config_keyword="")
            inlineinspection.AddMessage("Rows copy is done")
            # Process: Make Table View (Make Table View) (management)
            Pipe_Tally_Table_View = "PipeTally_View"
            arcpy.management.MakeTableView(in_table=Pipe_Tally_Table, out_view=Pipe_Tally_Table_View, where_clause="", workspace="", field_info="")
            inlineinspection.AddMessage("Make Table View is done")
            # Process: Add Anomaly X Coord Field (Add Field) (management)
            Anomaly_X_Coord_Field_Added = arcpy.management.AddField(in_table=Pipe_Tally_Table_View, field_name="AnomalyXCoord", field_type="DOUBLE", field_precision=15, field_scale=7, field_length=None, field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[0]
            inlineinspection.AddMessage("Anomaly X Coord Field Added")
            # Process: Calculate Anomaly X Coord Field (Calculate Field) (management)
            Anomaly_X_Coord_Field_Calculated = arcpy.management.CalculateField(in_table=Anomaly_X_Coord_Field_Added, field="AnomalyXCoord", expression=f"!{Input_ILI_Pipe_Tally_Odometer_Field}! - {Input_False_Easting_Value}", expression_type="PYTHON_9.3", code_block="", field_type="TEXT")[0]
            inlineinspection.AddMessage("Anomaly X Coord Field Calculated")
            # Process: Add Anomaly Y Coord Field (Add Field) (management)
            Anomaly_Y_Coord_Field_Added = arcpy.management.AddField(in_table=Pipe_Tally_Table_View, field_name="AnomalyYCoord", field_type="DOUBLE", field_precision=15, field_scale=7, field_length=None, field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[0]
            inlineinspection.AddMessage("Anomaly Y Coord Field Added")
            # Process: Calculate Anomaly Y Coord Field (Calculate Field) (management)
            #arcpy.management.CalculateField(Pipe_Tally_Table_View, "AnomalyYCoord", 'calc_anomaly_y_coord(!'+Input_ILI_Pipe_Tally_Clock_Position_Field +'!, !'+Input_Pipeline_Diameter_Value +'!, 0, '+Input_Clock_Position_Offset +','+Input_Y_Axis_Clock_Orientation +')', "PYTHON3", "def calc_anomaly_y_coord(clock_pos, pipe_od, false_northing, clock_offset, y_axis" +
            arcpy.management.CalculateField(Pipe_Tally_Table_View, "AnomalyYCoord", 'calc_anomaly_y_coord(!'+Input_ILI_Pipe_Tally_Clock_Position_Field +'!, !'+Input_Pipeline_Diameter_Value +'!, '+str(Input_False_Northing_Value)+', '+Input_Clock_Position_Offset +','+Input_Y_Axis_Clock_Orientation +')', "PYTHON3", "def calc_anomaly_y_coord(clock_pos, pipe_od, false_northing, clock_offset, y_axis" +
    "_clock):\n    clock_parts = clock_pos.split(\':\')\n    clock_hours = float(clock_pa" +
    "rts[0])\n    clock_minutes = float(clock_parts[1])\n    pipe_od = float(pipe_od)\n " +
    "   offset_parts = clock_offset.split(\':\')\n    offset_hours = float(offset_parts[" +
    "0])\n    offset_minutes = float(offset_parts[1])\n\n    false_northing = float(false_northing)\n\n  # Correct clock minutes for" +
    " the clock minutes offset\n    if offset_hours < 0:\n        offset_minutes = offs" +
    "et_minutes * (-1)\n    clock_minutes = clock_minutes + offset_minutes\n    if cloc" +
    "k_minutes > 59:\n        clock_minutes = clock_minutes - 60\n        clock_hours =" +
    " clock_hours + 1\n    elif clock_minutes < 0:\n        clock_minutes = clock_minut" +
    "es + 60\n        clock_hours = clock_hours - 1\n\n    # Correct clock hours for the" +
    " clock hours offset\n    clock_hours = clock_hours + offset_hours\n    if clock_ho" +
    "urs > 12:\n        clock_hours = clock_hours - 12\n    elif clock_hours < 0:\n     " +
    "   clock_hours = clock_hours + 12\n\n    # Calculate y-coordinate\n    if y_axis_cl" +
    "ock == \"6:00 Centered\":\n        if clock_hours == 12:\n            y_coord = ((cl" +
    "ock_minutes / 60 / 12) * (pipe_od / 12 * math.pi)) + false_northing\n        else" +
    ":\n            y_coord = (((clock_hours / 12) + (clock_minutes / 60 / 12)) * (pip" +
    "e_od / 12 * math.pi)) + false_northing\n    else:  # y_axis_clock = \"12:00 Center" +
    "ed\"\n        if clock_hours == 12:\n            y_coord = (-1) * (((clock_minutes " +
    "/ 60 / 12) * (pipe_od / 12 * math.pi)) + false_northing)\n        elif 1 <= clock" +
    "_hours < 6:\n            y_coord = (-1) * ((((clock_hours / 12) + (clock_minutes " +
    "/ 60 / 12)) * (pipe_od / 12 * math.pi)) + false_northing)\n        else:  # 6 <= " +
    "clock_hours <= 11\n            y_coord = ((1 - ((clock_hours / 12) + (clock_minut" +
    "es / 60 / 12))) * (pipe_od / 12 * math.pi)) + false_northing\n    return y_coord\n" +
    "", "TEXT")

            inlineinspection.AddMessage("Anomaly Y Coord Field Calculated")
            # Process: Add Anomaly Major Axis Field (Add Field) (management)
            Anomaly_Major_Axis_Field_Added = arcpy.management.AddField(in_table=Pipe_Tally_Table_View, field_name="AnomalyMajorAxisFt", field_type="DOUBLE", field_precision=15, field_scale=3, field_length=None, field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[0]
            inlineinspection.AddMessage("Anomaly Major Axis Field Added")
            # Process: Calculate Anomaly Major Axis Field (Calculate Field) (management)
            Anomaly_Major_Axis_Field_Calculated = arcpy.management.CalculateField(in_table=Pipe_Tally_Table_View, field="AnomalyMajorAxisFt", expression=f"!{Input_ILI_Pipe_Tally_Anomaly_Width_Field}! / 12", expression_type="PYTHON_9.3", code_block="", field_type="TEXT")[0]
            inlineinspection.AddMessage("Anomaly Major Axis Field Calculated")
            # Process: Add Anomaly Minor Axis Field (Add Field) (management)
            Anomaly_Minor_Axis_Field_Added = arcpy.management.AddField(in_table=Pipe_Tally_Table_View, field_name="AnomalyMinorAxisFt", field_type="DOUBLE", field_precision=15, field_scale=3, field_length=None, field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[0]
            inlineinspection.AddMessage("Anomaly Minor Axis Field Added")
            # Process: Calculate Anomaly Minor Axis Field (Calculate Field) (management)
            Anomaly_Minor_Axis_Field_Calculated = arcpy.management.CalculateField(in_table=Pipe_Tally_Table_View, field="AnomalyMinorAxisFt", expression=f"!{Input_ILI_Pipe_Tally_Anomaly_Length_Field}! / 12", expression_type="PYTHON_9.3", code_block="", field_type="TEXT")[0]
            inlineinspection.AddMessage("Anomaly Minor Axis Field Calculated")
            # Process: Add Azimuth Field (Add Field) (management)
            Azimuth_Field_Added = arcpy.management.AddField(in_table=Pipe_Tally_Table_View, field_name="Azimuth", field_type="DOUBLE", field_precision=15, field_scale=2, field_length=None, field_alias="", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")[0]
            inlineinspection.AddMessage("Azimuth Field Added")
            # Process: Calculate Azimuth Field (Calculate Field) (management)
            Azimuth_Field_Calculated = arcpy.management.CalculateField(in_table=Pipe_Tally_Table_View, field="Azimuth", expression="0.1", expression_type="PYTHON_9.3", code_block="", field_type="TEXT")[0]
            inlineinspection.AddMessage("Azimuth Field Calculated")
            # Process: Make XY Event Layer (Make XY Event Layer) (management)          
            Anomaly_Point_Events = "AnomalyEvents_Layer"  
            #Anomaly_Point_Events = fr"{arcpy.env.scratchGDB}\AnomalyEvents_Layer",
            #arcpy.CopyRows_management(Pipe_Tally_Table_View, "Pipe_Tally_Table_View")
            #inlineinspection.AddMessage("Pipe_Tally_Table_View copy done")
            arcpy.management.MakeXYEventLayer(table=Pipe_Tally_Table_View, in_x_field="AnomalyXCoord", in_y_field="AnomalyYCoord", out_layer=Anomaly_Point_Events, spatial_reference=Spatial_Reference_for_Output_Features, in_z_field="")
            #arcpy.MakeXYEventLayer_management(Pipe_Tally_Table_View, "AnomalyXCoord", "AnomalyYCoord", Anomaly_Point_Events, Spatial_Reference_for_Output_Features)
            inlineinspection.AddMessage("Make XY Event Layer Created")
            #Process: Copy Features (Copy Features) (management)
            #Output_Anomaly_Point_Features = "AnomalyPoint"
            arcpy.management.CopyFeatures(in_features=Anomaly_Point_Events, out_feature_class=Output_Anomaly_Point_Features, config_keyword="", spatial_grid_1=0, spatial_grid_2=0, spatial_grid_3=0)
            inlineinspection.AddMessage("Copy Features to Anomaly Point Events")
            # Process: Table To Ellipse (Table To Ellipse) (management)
            Anomaly_Ellipse_Polylines = "AnomalyEllipsePolyline"
            #arcpy.management.TableToEllipse(in_table=Output_Anomaly_Point_Features, out_featureclass=Anomaly_Ellipse_Polylines, x_field="AnomalyXCoord", y_field="AnomalyYCoord", major_field="AnomalyMajorAxisFt", minor_field="AnomalyMinorAxisFt", distance_units="9003", azimuth_field="Azimuth", azimuth_units="9102", id_field="", spatial_reference=Spatial_Reference_for_Output_Features, attributes="NO_ATTRIBUTES")
            arcpy.management.TableToEllipse(Output_Anomaly_Point_Features, Anomaly_Ellipse_Polylines, "AnomalyXCoord", "AnomalyYCoord", "AnomalyMajorAxisFt", "AnomalyMinorAxisFt", "FEET", "Azimuth", "DEGREES", None, Spatial_Reference_for_Output_Features, "NO_ATTRIBUTES")
            inlineinspection.AddMessage("Converted from Table To Ellipse")            

            # Process: Feature To Polygon (Feature To Polygon) (management)
            #arcpy.management.FeatureToPolygon([Anomaly_Ellipse_Polylines], Output_Anomaly_Ellipse_Features, None, "ATTRIBUTES", None)
            
            arcpy.management.FeatureToPolygon(in_features=[Anomaly_Ellipse_Polylines], out_feature_class=Output_Anomaly_Ellipse_Features, cluster_tolerance="", attributes="ATTRIBUTES", label_features=Output_Anomaly_Point_Features)
            inlineinspection.AddMessage("Converted Feature To Polygon")
            
            # Process: Feature Envelope To Polygon (Feature Envelope To Polygon) (management)
            arcpy.management.FeatureEnvelopeToPolygon(in_features=Output_Anomaly_Ellipse_Features, out_feature_class=Output_Anomaly_Envelope_Features, single_envelope="SINGLEPART")
            inlineinspection.AddMessage("Converted Feature Envelope To Polygon")
            
        except Exception as e:
            tb = sys.exc_info()[2]
            inlineinspection.AddError("An error occurred on line %i" % tb.tb_lineno)
            inlineinspection.AddError(str(e))
            inlineinspection.AddError("Issue in ILI Anomaly 2 Geography.\n{}".format(arcpy.GetMessages(2)))
            return False

    def iliWeld2Geography(self,parameters):
        try:
           
            Input_ILI_Pipe_Tally_Table = parameters[0].valueAsText
            Input_ILI_Pipe_Tally_Odometer_Field = parameters[1].valueAsText
            Input_ILI_Pipe_Tally_Anomaly_Width_Field = parameters[2].valueAsText
            Input_ILI_Pipe_Tally_Anomaly_Length_Field =parameters[3].valueAsText
            Input_ILI_Pipe_Tally_Clock_Position_Field =parameters[4].valueAsText
            Input_Clock_Position_Offset="\""+parameters[5].valueAsText+"\""             
            Input_Y_Axis_Clock_Orientation= "\""+parameters[6].valueAsText+"\"" 
            Input_Pipeline_Diameter_Value =parameters[7].valueAsText
            Input_False_Northing_Value=parameters[8].valueAsText
            Input_False_Easting_Value=parameters[9].valueAsText
            Spatial_Reference_for_Output_Features= parameters[10].valueAsText 
            Output_Anomaly_Point_Features=parameters[11].valueAsText
            Output_Anomaly_Ellipse_Features=parameters[12].valueAsText 
            Output_Anomaly_Envelope_Features=parameters[13].valueAsText
            Input_ILI_Weld_Table = parameters[17].valueAsText
            Output_Weld_Features=parameters[18].valueAsText
                        
            # To allow overwriting outputs change overwriteOutput option to True.
            arcpy.env.overwriteOutput = True
            
            # Process: Copy Rows (Copy Rows) (management)
            Pipe_WeldTally_Table = fr"{arcpy.env.scratchGDB}\PipeWeldTally"
            arcpy.management.CopyRows(in_rows=Input_ILI_Weld_Table, out_table=Pipe_WeldTally_Table, config_keyword="")
            inlineinspection.AddMessage("Rows copy is done")
           
            arcpy.management.AddFields(Pipe_WeldTally_Table, "WeldXMinCoord DOUBLE # # # #;WeldYMinCoord DOUBLE # # # #;WeldXMaxCoord DOUBLE # # # #;WeldYMaxCoord DOUBLE # # # #")
            inlineinspection.AddMessage("Weld Tally Fields are added")
            
            if ("6:00 Centered" in Input_Y_Axis_Clock_Orientation):                 
                    #ymin_coord = (((0 / 12) + (0 / 60 / 12)) * (pipe_od / 12 * math.pi)) + false_northing                
                    #ymax_coord = (((12 / 12) + (0 / 60 / 12)) * (pipe_od / 12 * math.pi)) + false_northing

                    arcpy.management.CalculateFields(Pipe_WeldTally_Table, "PYTHON3", "WeldXMinCoord !"+Input_ILI_Pipe_Tally_Odometer_Field+"!;WeldYMinCoord  float("+str(Input_False_Northing_Value)+");WeldXMaxCoord !"+Input_ILI_Pipe_Tally_Odometer_Field+"!;WeldYMaxCoord \'((!"+Input_Pipeline_Diameter_Value+"!/ 12) * math.pi) + float("+str(Input_False_Northing_Value)+")\'", '')
                    #                arcpy.management.CalculateFields("PipeWeldTally", "PYTHON3", "WeldXMinCoord !AbsoluteOdometer!;WeldYMinCoord 0;WeldXMaxCoord !AbsoluteOdometer!" +
                    #";WeldYMaxCoord \'(!PipeDiameter!/12)*math.pi+float(str(\"0.0\"))\'", '')
                    inlineinspection.AddMessage("Weld Tally Fields are Calculated with 6:00 Centered")
            else:
                    ##if 1 <= clock_hours < 6:
                    #    ymin_coord = (-1) * ((((6 / 12) + (0 / 60 / 12)) * (pipe_od / 12 * math.pi)) + false_northing)
                    ##else:  # 6 <= clock_hours <= 11
                    #    ymax_coord = ((1 - ((6 / 12) + (0 / 60 / 12))) * (pipe_od / 12 * math.pi)) + false_northing
                    arcpy.management.CalculateFields(Pipe_WeldTally_Table, "PYTHON3", "WeldXMinCoord !"+Input_ILI_Pipe_Tally_Odometer_Field+"!;WeldYMinCoord \'(-1)*((((6 / 12) + (0 / 60 / 12)) * (!"+Input_Pipeline_Diameter_Value+"!/ 12 * math.pi)) + float("+str(Input_False_Northing_Value)+"))\';WeldXMaxCoord !"+Input_ILI_Pipe_Tally_Odometer_Field+"!;WeldYMaxCoord \'(0.5 * (!"+Input_Pipeline_Diameter_Value+"!/12 * math.pi)) + float("+str(Input_False_Northing_Value)+")\'", '')
                    inlineinspection.AddMessage("Weld Tally Fields are Calculated with 12:00 Centered")

            #arcpy.management.CalculateFields(Pipe_WeldTally_Table, "PYTHON3", "WeldXMinCoord !"+Input_ILI_Pipe_Tally_Odometer_Field+"!;WeldYMinCoord 0.0;WeldXMaxCoord !"+Input_ILI_Pipe_Tally_Odometer_Field+"!;WeldYMaxCoord !"+Input_Pipeline_Diameter_Value+"!", '')
            #inlineinspection.AddMessage("Weld Tally Fields are Calculated")

            arcpy.management.XYToLine(Pipe_WeldTally_Table, Output_Weld_Features, "WeldXMinCoord", "WeldYMinCoord", "WeldXMaxCoord", "WeldYMaxCoord", "GEODESIC", "WeldNumber",Spatial_Reference_for_Output_Features , "NO_ATTRIBUTES")
            inlineinspection.AddMessage("Weld Line Features are Created")

        except Exception as e:
            tb = sys.exc_info()[2]
            inlineinspection.AddError("An error occurred on line %i" % tb.tb_lineno)
            inlineinspection.AddError(str(e))
            inlineinspection.AddError("Error in Weld Line Features Creation")

    def iliGrid2Geography(self,parameters):
        try:
            Input_ILI_Pipe_Tally_Table = parameters[0].valueAsText
            Input_ILI_Pipe_Tally_Odometer_Field = parameters[1].valueAsText
            Input_ILI_Pipe_Tally_Anomaly_Width_Field = parameters[2].valueAsText
            Input_ILI_Pipe_Tally_Anomaly_Length_Field =parameters[3].valueAsText
            Input_ILI_Pipe_Tally_Clock_Position_Field =parameters[4].valueAsText
            Input_Clock_Position_Offset="\""+parameters[5].valueAsText+"\""             
            Input_Y_Axis_Clock_Orientation= "\""+parameters[6].valueAsText+"\"" 
            Input_Pipeline_Diameter_Value =parameters[7].valueAsText
            Input_False_Northing_Value=parameters[8].valueAsText
            Input_False_Easting_Value=parameters[9].valueAsText
            Spatial_Reference_for_Output_Features= parameters[10].valueAsText 
            Output_Anomaly_Point_Features=parameters[11].valueAsText
            Output_Anomaly_Ellipse_Features=parameters[12].valueAsText 
            Output_Anomaly_Envelope_Features=parameters[13].valueAsText
            Output_Grid_Features=parameters[15].valueAsText 
            Input_is_weld_value = parameters[16].value
            Input_ILI_Weld_Table = parameters[17].valueAsText
            Output_Weld_Features=parameters[18].valueAsText

            # To allow overwriting outputs change overwriteOutput option to True.
            arcpy.env.overwriteOutput = True
            
            # Process: Copy Rows (Copy Rows) (management)
            Pipe_GridTally_Table = fr"{arcpy.env.scratchGDB}\PipeGridTally"
            arcpy.management.CopyRows(in_rows=Input_ILI_Weld_Table, out_table=Pipe_GridTally_Table, config_keyword="")
            inlineinspection.AddMessage("Grid Rows copy is done")

            field_to_find_x_max = Input_ILI_Pipe_Tally_Odometer_Field
            field_to_find_y_max = Input_Pipeline_Diameter_Value
           
            x_max_AnamalyValue = arcpy.da.SearchCursor(Input_ILI_Pipe_Tally_Table, field_to_find_x_max, "{} IS NOT NULL".format(field_to_find_x_max), sql_clause = (None, "ORDER BY {} DESC".format(field_to_find_x_max))).next()[0]
            x_max_value =0.0
            x_max_WeldValue = 0.0
            if(Input_is_weld_value):
                x_max_WeldValue = arcpy.da.SearchCursor(Pipe_GridTally_Table, field_to_find_x_max, "{} IS NOT NULL".format(field_to_find_x_max), sql_clause = (None, "ORDER BY {} DESC".format(field_to_find_x_max))).next()[0]
            x_max_value=x_max_WeldValue if x_max_AnamalyValue < x_max_WeldValue else x_max_AnamalyValue
            
            y_max_value = arcpy.da.SearchCursor(Pipe_GridTally_Table, field_to_find_y_max, "{} IS NOT NULL".format(field_to_find_y_max), sql_clause = (None, "ORDER BY {} DESC".format(field_to_find_y_max))).next()[0]
            
            if ("6:00 Centered" in Input_Y_Axis_Clock_Orientation):                 
                ymin_coord = (((0 / 12) + (0 / 60 / 12)) * (y_max_value / 12 * math.pi)) + float(Input_False_Northing_Value)               
                ymax_coord = (((12 / 12) + (0 / 60 / 12)) * (y_max_value / 12 * math.pi)) + float(Input_False_Northing_Value)
               
            else:                
                ymin_coord = (-1) * ((((6 / 12) + (0 / 60 / 12)) * (y_max_value / 12 * math.pi)) + float(Input_False_Northing_Value))               
                ymax_coord = ((1 - ((6 / 12) + (0 / 60 / 12))) * (y_max_value / 12 * math.pi)) + float(Input_False_Northing_Value)
                


            x_min_value = 0           
            split_interval =5           
            grid_interval =round((ymax_coord-ymin_coord)/(split_interval-1),1)

            inlineinspection.AddMessage(" ymin_coord {} ,ymax_coord {}, grid_interval {} ".format(ymin_coord,ymax_coord,grid_interval))
            
            grid_id=["6:00","3:00","12:00","9:00","6:00"]            
            if ("6:00 Centered" in Input_Y_Axis_Clock_Orientation):
                grid_id=["12:00","3:00","6:00","9:00","12:00"]
                                            
            fc_name = os.path.basename(Output_Grid_Features)
            wspace = os.path.dirname(Output_Grid_Features)
           
            GridLable_Column="ClockPosition"
            Output_Grid_FeatureClass = arcpy.management.CreateFeatureclass(wspace, fc_name, "POLYLINE", None, "DISABLED", "DISABLED", Spatial_Reference_for_Output_Features)
            arcpy.management.AddFields(Output_Grid_FeatureClass, GridLable_Column+" TEXT # 255 # #;GridXMinCoord DOUBLE # # # #;GridYMinCoord DOUBLE # # # #;GridXMaxCoord DOUBLE # # # #;GridYMaxCoord DOUBLE # # # #")

            # Inserting into polyline logic           
            point = arcpy.Point()
            array = arcpy.Array()

            featureList = []
            cursor = arcpy.InsertCursor(Output_Grid_FeatureClass,["SHAPE@",GridLable_Column])
            feat = cursor.newRow()

            for interval in range(0,split_interval):
                # Set X and Y for start and end points
                point.X = x_min_value
                point.Y = ymin_coord+interval*grid_interval
                array.add(point)
                point.X = x_max_value
                point.Y = ymin_coord+interval*grid_interval
                array.add(point)   
                # Create a Polyline object based on the array of points
                polyline = arcpy.Polyline(array)
                # Clear the array for future use
                array.removeAll()
                # Append to the list of Polyline objects
                featureList.append(polyline)
                # Insert the feature
                feat.shape = polyline
                feat.setValue(GridLable_Column,grid_id[interval])
                feat.setValue("GridXMinCoord",x_min_value)
                feat.setValue("GridYMinCoord",interval*grid_interval)
                feat.setValue("GridXMaxCoord",x_max_value)
                feat.setValue("GridYMaxCoord",interval*grid_interval)
                cursor.insertRow(feat)
            del feat
            del cursor

            inlineinspection.AddMessage("Grid Line Features are created")

        except Exception as e:
            tb = sys.exc_info()[2]
            inlineinspection.AddError("An error occurred on line %i" % tb.tb_lineno)
            inlineinspection.AddError(str(e))
            inlineinspection.AddError("Error in Grid Line Features creation")