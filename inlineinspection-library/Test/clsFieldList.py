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

    fc=r"C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\PipeSegment"
    fc1=r"C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\ILIData"
    fc2=r"C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\MAOPRating"
    fc0=r"C:\G2\UnitedBrine\FromMarissa\UB_PODSSpatial6.gdb\Transmission\StationSeries"
    cls = my_class(fc0)
    #cls.run()
    cls.build_segmentor_table()
    arcpy.AddMessage("****** Process Completed  : {} ******".format(dt.datetime.now()))





