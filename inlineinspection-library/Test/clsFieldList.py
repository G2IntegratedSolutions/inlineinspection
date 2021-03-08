import arcpy
import datetime as dt


from logging import exception
import inlineinspection
import os
import numpy as np
import math
from inlineinspection import config
#from eaglepy.lr.toolbox import Segmentor,Attributer,Statistitater
#from eaglepy.funcparam import FuncParam
import traceback
import sys
import locale
import json
import arcpy.cim
from arcpy import env


class my_class(object):
    def __init__(self,fc):
       self.fc=fc
       print("-- {}".format(fc))
        
    def run(self):
        try:            
            for fld in arcpy.ListFields(self.fc):
                print("{}".format(fld.name))
                #print("{} , {}".format(fld.name,fld.type))

        except Exception as e:
            tb = sys.exc_info()[2]
            arcpy.AddError("An error occurred on line %i" % tb.tb_lineno)
            arcpy.AddError(str(e))
            return False
        return True
    
    def build_json_for_segmentor(self, ili_layer, maop_layer=None):
        # Build json string
        self.structure_segment ="PipeSegment"
        self.projDatabase = r"C:\G2\UnitedBrine\Anomaly Comparison\Freeport\PODS_ili.gdb"
        self.projDataSet="Transmission"
        name_1 = self.structure_segment
        path_1 = os.path.join(self.projDatabase,self.projDataSet, self.structure_segment)
        routeIdentifierField_1 = "RouteEventID"
        fromMeasureField_1 = "BeginMeasure"
        toMeasureField_1 = "EndMeasure"
        fromMeasureField_2="Measure"
        toMeasureField_2="Measure"
        key_1 = "EventID"
        # Build JSON for segmentor!!
        segmentor_json = list()
        segmentor_json_1 = dict()
        segmentor_json_1["name"] = name_1
        segmentor_json_1["path"] = path_1
        segmentor_json_1["routeIdentifierField"] = routeIdentifierField_1
        segmentor_json_1["fromMeasureField"] = fromMeasureField_1
        segmentor_json_1["toMeasureField"] = toMeasureField_1
        segmentor_json_1["primaryKeyField"] = key_1
        # segmentor_json = [segmentor_json_1]
        segmentor_json.append(segmentor_json_1)

        if ili_layer:
            name_2 = ili_layer
            path_2 = os.path.join(self.projDatabase,self.projDataSet, ili_layer)
            segmentor_json_2 = dict()
            segmentor_json_2["name"] = name_2
            segmentor_json_2["path"] = path_2
            segmentor_json_2["routeIdentifierField"] = routeIdentifierField_1
            segmentor_json_2["fromMeasureField"] = fromMeasureField_2
            segmentor_json_2["toMeasureField"] = toMeasureField_2
            segmentor_json_2["primaryKeyField"] = key_1
            segmentor_json.append(segmentor_json_2)

        if maop_layer:
            name_3 = maop_layer
            path_3 =  os.path.join(self.projDatabase,self.projDataSet, maop_layer)
            segmentor_json_3 = dict()
            segmentor_json_3["name"] = name_3
            segmentor_json_3["path"] = path_3
            segmentor_json_3["routeIdentifierField"] = routeIdentifierField_1
            segmentor_json_3["fromMeasureField"] = fromMeasureField_1
            segmentor_json_3["toMeasureField"] = toMeasureField_1
            segmentor_json_3["primaryKeyField"] = key_1
            segmentor_json.append(segmentor_json_3)

        segmentor_json_string = json.dumps(segmentor_json)
        return segmentor_json_string

    def build_segmentor_table(self):

        #Create intermediate folder and gdb to store the segmentor related tables 
        self.output_dir=r"C:\G2\UnitedBrine\Test\TestOutputdatabase.gdb"
        self.ILI_TEMP_FOLDER = "ILI_TEMP"
        self.ILI_TEMP_GDB = "ILI_TEMP_GDB.gdb"
        tempoutput_workspace = arcpy.env.scratchFolder if arcpy.Exists(arcpy.env.scratchFolder) and arcpy.env.scratchFolder is not None else self.output_dir
        tempoutput_dir = os.path.join(tempoutput_workspace, self.ILI_TEMP_FOLDER )
        tempoutput_gdb = self.ILI_TEMP_GDB 
        self.tempoutputgdb_path = os.path.join(tempoutput_dir, tempoutput_gdb)
        
        # Create temp gbd for intermediate process
        self.createtempgdb(tempoutput_dir, tempoutput_gdb)

        self.input_centerline =r"C:\G2\UnitedBrine\Anomaly Comparison\Freeport\PODS_ili.gdb\Transmission\StationSeries"
        ili_layer ="ILIData"
        maop_layer = "MAOPRating"
        CENTERLINE_UNIQUE_ID ="EventID"
        CENTERLINE_BEGIN_MEASURE ="BeginMeasure"
        CENTERLINE_END_MEASURE ="EndMeasure"
        ili_segmentor = Segmentor()
        route_layer = FuncParam(self.input_centerline)  #FuncParam(os.path.join(self.projDatabase.path, HCAOperation.CENTERLINE_TABLE))
        route_id = FuncParam(CENTERLINE_UNIQUE_ID)
        begin_meas = FuncParam(CENTERLINE_BEGIN_MEASURE)
        end_meas = FuncParam(CENTERLINE_END_MEASURE)
                
        json_str = self.build_json_for_segmentor(ili_layer,maop_layer)

        segmentor_json = FuncParam(json_str)

        segmentor_out = FuncParam(self.tempoutputgdb_path + "\\ILISegmentCount_Segmentor")
        if arcpy.Exists(segmentor_out.valueAsText):
            arcpy.Delete_management(segmentor_out.valueAsText)
        segmentor_error = FuncParam(self.tempoutputgdb_path + "\\ILISegmentCount_Segmentor_E")
        if arcpy.Exists(segmentor_error.valueAsText):
            arcpy.Delete_management(segmentor_error.valueAsText)
        seg_parameters = [route_layer, route_id, begin_meas, end_meas, segmentor_json, segmentor_out, segmentor_error]
        ili_segmentor.execute(seg_parameters, None)

        # Attributor

        # Delete record from route
        where_clause = "layer_Name='route'"  #----
        with arcpy.da.UpdateCursor(segmentor_out.valueAsText, '*', where_clause) as cursor:
            for row in cursor:
                cursor.deleteRow()

        # Run attributor
        hca_attributor = Attributer()
        attributor_in = segmentor_out

        # Build json string
        attr_list=[{"name":"PipeSegment","columns":[{"inputColumnName":"RouteEventID","outputColumnName":"RouteEventID"},
                                                    {"inputColumnName":"EventID","outputColumnName":"SegEventID"},
                                                               {"inputColumnName":"NominalDiameterGCL","outputColumnName":"NominalDiameterGCL"},
                                                               {"inputColumnName":"NominalWallThicknessGCL","outputColumnName":"NominalWallThicknessGCL"},
                                                               {"inputColumnName":"SMYSGCL","outputColumnName":"SMYSGCL"}
                                                               ]},
                   {"name":"ILIData","columns":[{"inputColumnName":"RouteEventID","outputColumnName":"RouteEventID"},
                                                    {"inputColumnName":"EventID","outputColumnName":"ILIEventID"},
                                                               {"inputColumnName":"Length","outputColumnName":"Length"},
                                                               {"inputColumnName":"MaxDepthMeasured","outputColumnName":"MaxDepthMeasured"},
                                                               {"inputColumnName":"MaxDiameter","outputColumnName":"MaxDiameter"},                                                               
                                                               {"inputColumnName":"MeasuredWallThickness","outputColumnName":"MeasuredWallThickness"},
                                                               ]},
                    {"name":"MAOPRating","columns":[{"inputColumnName":"RouteEventID","outputColumnName":"RouteEventID"},
                                                    {"inputColumnName":"EventID","outputColumnName":"MAOPEventID"},
                                                               {"inputColumnName":"MAOPRating","outputColumnName":"MAOPRating"},
                                                               {"inputColumnName":"MOP","outputColumnName":"MOP"}                                                               ]},
                   ]        

        json_str = json.dumps(attr_list)
        attributor_json = FuncParam(json_str)
        
        attributor_out = FuncParam(self.tempoutputgdb_path + "\\ILISegmentCount_Attributor")
        if arcpy.Exists(attributor_out.valueAsText):
            arcpy.Delete_management(attributor_out.valueAsText)
        attributor_error = FuncParam(self.tempoutputgdb_path + "\\ILISegmentCount_Attributor_E")
        if arcpy.Exists(attributor_error.valueAsText):
            arcpy.Delete_management(attributor_error.valueAsText)
        parameters = [attributor_in, attributor_json, attributor_out, attributor_error]
        hca_attributor.execute(parameters, None)

                
        # run statistitator
        hca_statistitator = Statistitater()
        statistitator_in = attributor_out
        group_by = FuncParam("SEGMENT_ID")
        stat_list = [{"name":"Route_ID","calculation":"calculation.First(default=None,input='row.ROUTE_ID',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"String","length":50}},
                   {"name":"FROM_MEASURE","calculation":"calculation.First(default=None,input='row.FROM_MEASURE',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double","precision":10}},
                   {"name":"TO_MEASURE","calculation":"calculation.First(default=None,input='row.TO_MEASURE',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double","precision":10}},
                   {"name":"NominalDiameterGCL","calculation":"calculation.First(default=None,input='row.NominalDiameterGCL',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double"}},
                   {"name":"NominalWallThicknessGCL","calculation":"calculation.First(default=None,input='row.NominalWallThicknessGCL',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double"}},
                   {"name":"SMYSGCL","calculation":"calculation.First(default=None,input='row.SMYSGCL',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double"}},
                   {"name":"Length","calculation":"calculation.First(default=None,input='row.Length',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double"}},
                   {"name":"MaxDepthMeasured","calculation":"calculation.First(default=None,input='row.MaxDepthMeasured',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double"}},
                   {"name":"MAOPRating","calculation":"calculation.First(default=None,input='row.MAOPRating',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double"}},
                   {"name":"ILIEventID","calculation":"calculation.First(default=None,input='row.ILIEventID',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"String"}},
                   
                   {"name":"MOP","calculation":"calculation.First(default=None,input='row.MOP',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double"}}
                   ]
        
        json_str = json.dumps(stat_list)
        statistitator_json = FuncParam(json_str)
        statistitator_out = FuncParam(self.tempoutputgdb_path + "\\ILISegmentCount_Statistitater")
        if arcpy.Exists(statistitator_out.valueAsText):
            arcpy.Delete_management(statistitator_out.valueAsText)
        statistitator_error = FuncParam(self.tempoutputgdb_path  + "\\ILISegmentCount_Statistitater_E")
        if arcpy.Exists(statistitator_error.valueAsText):
            arcpy.Delete_management(statistitator_error.valueAsText)
        parameters = [statistitator_in, group_by, statistitator_json, statistitator_out, statistitator_error]
        hca_statistitator.execute(parameters, None)

    ''' Check Intermediate gdb existing or not if not create '''
    def createtempgdb(self, output_dir, output_gdb):
        try:
            # Check for folder, if not create the folder
            if (not os.path.exists(output_dir)):
                os.makedirs(output_dir)
            gdbpath = os.path.join(output_dir, output_gdb)
            inlineinspection.AddMessage("Creating Intermediate GDB")
            if (not os.path.exists(gdbpath)):
                arcpy.management.CreateFileGDB(output_dir, output_gdb, "CURRENT")
            else:
                arcpy.management.Delete(gdbpath, None)
                arcpy.management.CreateFileGDB(output_dir, output_gdb, "CURRENT")
        except Exception as e:
            tb = sys.exc_info()[2]
            inlineinspection.AddError("An error occurred on line %i" % tb.tb_lineno)
            inlineinspection.AddError(str(e))
            inlineinspection.AddError("Issue in intermediate output folder creation, Please check and try again.\n{}".format(arcpy.GetMessages(2)))
            return False

    def pointinpolytest(self):
                
        polyarray = [[0, 0], [5, 0], [5, 5], [0, 5]]

        px= 2
        py = 2
        
        array = arcpy.Array([arcpy.Point(*coords) for coords in polyarray])
           
        wb_geometry=arcpy.Polygon(array)       
        pTestPoint =arcpy.Point(px,py)        
        #containflag = wb_geometry.contains(pTestPoint)
        containflag = pTestPoint.within(wb_geometry)
        if (containflag):
            print("Point in side")
        else:
            print("Point Out side")


if __name__ == "__main__":
    
    arcpy.AddMessage("****** Process started :{} ********".format(dt.datetime.now()))
    
    #sa_inputpoint_fc = r'C:\G2\Liquid_HCA\New_HCAData\NHDIntersection_02182020\NHD_Intersection.gdb\NHD_Intersections_0217_dm'
    #globalinputs = r"C:\G2\Liquid_HCA\Utah Test Data\UtahNED.gdb\Global_Inputs_SLC"
    #nt_src_dir = r'C:\G2\Liquid_HCA\Data_NDHPlus_HR\UTAHNHD_022520'
    #output_dir = r'C:\Test\CodeTest\DM02'
    #out_htpath=config.HT_FINAL_PATHS_NAME
    #out_waterbodyspread=config.HT_FINAL_WBPOLY_NAME
    #output_gdb = config.HT_OUT_GDBNAME
    #output_workspace=os.path.join(output_dir,output_gdb)

    pipesegment_layer=r"C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\PipeSegment"
    ili_layer=r"C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\ILIData"
    maop_layer=r"C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\MAOPRating"
    fc0=r"C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\StationSeries"

    table =r"C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Company"

    desc = arcpy.Describe(ili_layer)

    print(desc.datatype)

    #cls = my_class(fc0)
    ##cls.run()
    ##cls.build_segmentor_table()
    #cls.pointinpolytest()
    #arcpy.AddMessage("****** Process Completed  : {} ******".format(dt.datetime.now()))

    #diameter_field=parameters[12].valueAsText
    #thickness_field = parameters[13].valueAsText
    #syms_field = parameters[14].valueAsText
    #maop_field = parameters[15].valueAsText

    try:

        #spatialjoin1=r"C:\G2\UnitedBrine\Anomaly Comparison\scratch\ILI_TEMP\ILI_TEMP_GDB.gdb\ILIData_SJ12"
    
        #arcpy.SpatialJoin_analysis(ili_layer, pipesegment_layer, spatialjoin1)
        #arcpy.AddMessage("Spatial Join is performed on Pipe Segment")
        #spatialjoin2=r"C:\G2\UnitedBrine\Anomaly Comparison\scratch\ILI_TEMP\ILI_TEMP_GDB.gdb\ILIData_SJ22"
        #maop_field="MAOPRating"
        #arcpy.SpatialJoin_analysis(spatialjoin1, maop_layer, spatialjoin2, "JOIN_ONE_TO_ONE", "KEEP_ALL", r'EventID "EventID" true true false 38 Guid 0 0,First,#,'+spatialjoin1+',EventID,-1,-1;'+config.OUTPUT_SYMS_FIELDNAME+' "'+config.OUTPUT_SYMS_FIELDNAME+'" true true false 50 Text 0 0,First,#,'+spatialjoin1+','+config.OUTPUT_SYMS_FIELDNAME+',0,50;'+config.OUTPUT_DIAMETER_FIELDNAME+' "'+config.OUTPUT_DIAMETER_FIELDNAME+'" true true false 8 Double 0 0,First,#,'+spatialjoin1+','+config.OUTPUT_DIAMETER_FIELDNAME+',-1,-1;'+config.OUTPUT_THICKNESS_FIELDNAME+' "'+config.OUTPUT_THICKNESS_FIELDNAME+'" true true false 8 Double 0 0,First,#,'+spatialjoin1+','+config.OUTPUT_THICKNESS_FIELDNAME+',-1,-1;'+config.OUTPUT_MAOP_FIELDNAME+' "'+config.OUTPUT_MAOP_FIELDNAME+'" true true false 4 Long 0 0,First,#,'+maop_layer+','+maop_field+',-1,-1', "INTERSECT", None, '')

        ##inlineinspection.AddMessage("Spatial Join is performed on MAOP")
        
        ###Add join with ILI Layer
        ##arcpy.management.AddJoin(ili_layer, "EventID", spatialjoin2, "EventID", "KEEP_ALL")
        #arcpy.AddJoin_management(ili_layer, "EventID", spatialjoin2, "EventID", "KEEP_ALL")

        #if(ili_layer):
        #    flds = []            
        #    flds += [f.name for f in arcpy.ListFields (ili_layer)]
        #    filds=['ILIDATA.ANOMALYDESCRIPTION', 'ILIDATA.AREAOFMETALLOSS', 'ILIDATA.MOD_AREAOFMETALLOSS', 'ILIDATA.FLOWSTRESS', 'ILIDATA.MOD_FLOWSTRESS', 'ILIDATA.FOLIASFACTOR', 'ILIDATA.MOD_FOLIASFACTOR', 'ILIDATA.PIPEBURSTPRESSURE', 'ILIDATA.MOD_PIPEBURSTPRESSURE', 'ILIDATA.CALCULATEDPRESSURE', 'ILIDATA.REFERENCEPRESSURE', 'ILIDATA.SAFETY_FACTOR', 'ILIDATA.PRESSUREREFERENCEDRATIO', 'ILIDATA.ESTIMATEDREPAIRFACTOR', 'ILIDATA.RUPTUREPRESSURERATIO', 'ILIDATA_SJ2.OBJECTID', 'ILIDATA_SJ2.JOIN_COUNT', 'ILIDATA_SJ2.TARGET_FID', 'ILIDATA_SJ2.EVENTID', 'ILIDATA_SJ2.SMYS_SJ', 'ILIDATA_SJ2.NOMINALDIAMETER_SJ', 'ILIDATA_SJ2.NOMINALWALLTHICKNESS_SJ', 'ILIDATA_SJ2.MAOP_SJ']
        #    f1=[]
        #    for f in flds:
        #        x=f.split('.')
        #        if len(x)>1:
        #            x1=x[1]
        #            f1.append(x1)
        #            print(x1)
        #        else:
        #            f1.append(f)
        #            print(f)
           
            #print(f1)
            #for outField in outFields:
            #    if not outField.upper() in flds: 
            #        # Execute AddField for new fields
            #        arcpy.AddField_management(fc, outField, "LONG", 9,
            #                                  field_alias=outField, field_is_nullable="NULLABLE")
            #        inlineinspection.AddMessage("{} field added".format(outField))

        #arcpy.RemoveJoin_management(ili_layer)

        ## Use SearchCursor to access state name and the population count
        #with arcpy.da.SearchCursor(ili_layer,f1) as cursor:
        #    for row in cursor:
        #        # Access and print the row values by index position.
        #        #   state name: row[0]
        #        #   population: row[1]
        #        print('{} has a population of {}'.format(row[0], row[1]))
        #    del row
        #    del cursor

            
        #arcpy.AddMessage("Join is performed on ILI Data")
        #---------------------------------
        arcpy.AddMessage("Process Started")
        arcpy.env.workspace=r"C:\G2\UnitedBrine\Anomaly Comparison\scratch.gdb"
        arcpy.env.overwriteOutput = True
        arcpy.CopyRows_management(ili_layer, "PipeTally_Test")
        arcpy.MakeXYEventLayer_management("PipeTally_Test", "POINT_X", "POINT_Y", "Anomaly_Point_Events")
        arcpy.CopyFeatures_management("Anomaly_Point_Events", "Output_Anomaly_Point_Features")

        Input_Clock_Position_Offset="\"0:00\"" #parameters[0].valueAsText
        Input_Y_Axis_Clock_Orientation="\"6:00 Centered\"" #parameters[0].valueAsText        
        Output_Anomaly_Point_Features=fr"{arcpy.env.scratchGDB}\AnomalyPoint", 
        Output_Anomaly_Ellipse_Features=fr"{arcpy.env.scratchGDB}\AnomalyEllipse", 
        Output_Anomaly_Envelope_Features=fr"{arcpy.env.scratchGDB}\AnomalyEnvelope", 
        Spatial_Reference_for_Output_Features="PROJCS['NAD_1983_UTM_Zone_16N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',1640416.666666667],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-87.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Foot_US',0.3048006096012192]];-5120900 -9998100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
        
        Pipe_Tally_Table_View = "PipeTally"
        # Process: Make XY Event Layer (Make XY Event Layer) (management)
        Anomaly_Point_Events = "AnomalyEvents_Layer"
        #arcpy.management.MakeXYEventLayer(table=Pipe_Tally_Table_View, in_x_field="AnomalyXCoord", in_y_field="AnomalyYCoord", out_layer=Anomaly_Point_Events, spatial_reference=Spatial_Reference_for_Output_Features, in_z_field="")
        arcpy.MakeXYEventLayer_management("PipeTally", "AnomalyXCoord", "AnomalyYCoord", Anomaly_Point_Events)
        arcpy.AddMessage("MakeXYEventLayer is done")
        # Process: Copy Features (Copy Features) (management)
        arcpy.management.CopyFeatures(in_features=Anomaly_Point_Events, out_feature_class=Output_Anomaly_Point_Features, config_keyword="", spatial_grid_1=0, spatial_grid_2=0, spatial_grid_3=0)
        arcpy.AddMessage("CopyFeatures Anomaly_Point_Events is done")
        # Process: Table To Ellipse (Table To Ellipse) (management)
        Anomaly_Ellipse_Polylines = fr"{arcpy.env.scratchGDB}\AnomalyEllipsePolyline"
        arcpy.management.TableToEllipse(in_table=Output_Anomaly_Point_Features, out_featureclass=Anomaly_Ellipse_Polylines, x_field="AnomalyXCoord", y_field="AnomalyYCoord", major_field="AnomalyMajorAxisFt", minor_field="AnomalyMinorAxisFt", distance_units="9003", azimuth_field="Azimuth", azimuth_units="9102", id_field="", spatial_reference=Spatial_Reference_for_Output_Features, attributes="NO_ATTRIBUTES")
        arcpy.AddMessage("TableToEllipse is done")
        # Process: Feature To Polygon (Feature To Polygon) (management)
        arcpy.management.FeatureToPolygon(in_features=[Anomaly_Ellipse_Polylines], out_feature_class=Output_Anomaly_Ellipse_Features, cluster_tolerance="", attributes="ATTRIBUTES", label_features=Output_Anomaly_Point_Features)
        arcpy.AddMessage("FeatureToPolygon is done")
        # Process: Feature Envelope To Polygon (Feature Envelope To Polygon) (management)
        arcpy.management.FeatureEnvelopeToPolygon(in_features=Output_Anomaly_Ellipse_Features, out_feature_class=Output_Anomaly_Envelope_Features, single_envelope="SINGLEPART")
        arcpy.AddMessage("Feature Envelope To Polygon is done")
        arcpy.AddMessage("Process Completed")
    except Exception as e:
            tb = sys.exc_info()[2]
            arcpy.AddError("An error occurred on line %i" % tb.tb_lineno)
            arcpy.AddError(str(e))
            



