import arcpy
import datetime as dt


from logging import exception
import inlineinspection
import os
import numpy as np
import math
from inlineinspection import config
from eaglepy.lr.toolbox import Segmentor,Attributer,Statistitater
from eaglepy.funcparam import FuncParam
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

        spatialjoin1=r"C:\G2\UnitedBrine\Anomaly Comparison\scratch\ILI_TEMP\ILI_TEMP_GDB.gdb\ILIData_SJ1"
        #arcpy.analysis.SpatialJoin(ili_layer, pipesegment_layer, spatialjoin1, "JOIN_ONE_TO_ONE", "KEEP_ALL", r'EventID "EventID" true true false 38 Guid 0 0,First,#,'+ili_layer+',EventID,-1,-1;SMYS_SJ "SMYS_SJ" true true false 50 Text 0 0,First,#,'+pipesegment_layer+',SMYSGCL,0,50; NominalDiameter_SJ  "NominalDiameter_SJ" true true false 8 Double 0 0,First,#,'+pipesegment_layer+',NominalDiameterGCL,-1,-1;NominalWallThicknessGCL "NominalWallThicknessGCL" true true false 8 Double 0 0,First,#,'+pipesegment_layer+',NominalWallThicknessGCL,-1,-1', "INTERSECT", None, '')
    
        #arcpy.SpatialJoin_analysis(r"C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\ILIData", 
        #                           r"C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\PipeSegment", 
        #                           r"C:\G2\UnitedBrine\Test\TestOutputdatabase.gdb\ILIData_SpatialJoin1", 
        #                           "JOIN_ONE_TO_ONE", "KEEP_ALL",
        #                          r'EventID "EventID" true true false 38 Guid 0 0,First,#,C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\ILIData,EventID,-1,-1;NominalWallThicknessCl "NominalWallThicknessCl" true true false 50 Text 0 0,First,#,C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\PipeSegment,NominalWallThicknessCl,0,50;SMYSCL "SMYSCL" true true false 4 Long 0 0,First,#,C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\PipeSegment,SMYSCL,-1,-1', "INTERSECT", None, '')
    
        arcpy.SpatialJoin_analysis(ili_layer, pipesegment_layer, spatialjoin1)
        arcpy.AddMessage("Spatial Join is performed on Pipe Segment")
        spatialjoin1=r"C:\G2\UnitedBrine\Anomaly Comparison\scratch\ILI_TEMP\ILI_TEMP_GDB.gdb\ILIData_SJ2"
        arcpy.SpatialJoin_analysis(spatialjoin1, maop_layer, spatialjoin2, "JOIN_ONE_TO_ONE", "KEEP_ALL", r'EventID "EventID" true true false 38 Guid 0 0,First,#,'+spatialjoin1+',EventID,-1,-1;'+config.OUTPUT_SYMS_FIELDNAME+' "'+config.OUTPUT_SYMS_FIELDNAME+'" true true false 50 Text 0 0,First,#,'+spatialjoin1+','+config.OUTPUT_SYMS_FIELDNAME+',0,50;'+config.OUTPUT_DIAMETER_FIELDNAME+' "'+config.OUTPUT_DIAMETER_FIELDNAME+'" true true false 8 Double 0 0,First,#,'+spatialjoin1+','+config.OUTPUT_DIAMETER_FIELDNAME+',-1,-1;'+config.OUTPUT_THICKNESS_FIELDNAME+' "'+config.OUTPUT_THICKNESS_FIELDNAME+'" true true false 8 Double 0 0,First,#,'+spatialjoin1+','+config.OUTPUT_THICKNESS_FIELDNAME+',-1,-1;'+config.OUTPUT_MAOP_FIELDNAME+' "'+config.OUTPUT_MAOP_FIELDNAME+'" true true false 4 Long 0 0,First,#,'+maop_layer+','+maop_field+',-1,-1', "INTERSECT", None, '')

        #inlineinspection.AddMessage("Spatial Join is performed on MAOP")

        ##Remove existing join
        #arcpy.management.RemoveJoin(ili_layer)
        #arcpy.AddMessage("Existing Join is removed from ILI Data")
        ##Add join with ILI Layer
        #arcpy.management.AddJoin(ili_layer, "EventID", spatialjoin2, "EventID", "KEEP_ALL")
        #arcpy.AddMessage("Join is performed on ILI Data")
    except Exception as e:
            tb = sys.exc_info()[2]
            arcpy.AddError("An error occurred on line %i" % tb.tb_lineno)
            arcpy.AddError(str(e))
            



