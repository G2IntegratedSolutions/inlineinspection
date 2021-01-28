
""" Headline: Anomaly Processing Inline Inspection pressure caliculation tool 
    Calls:  inlineinspection, inlineinspection.config
    inputs: ILI Feature class(Which is calibrated and imported)
    Description: This tool calculates severity ratios, burst/safe pressures, according to B31G and Modified B31G.  
    Output: The output of this tool estimates burst pressure values for Metal Loss anomalies based on depth, length and pressure.
   """

from logging import exception
import arcpy
import inlineinspection
import os
import datetime as dt
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


class PressureCalculator(object):

    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = config.ILI_PC_TOOL_LABEL
        self.description = config.ILI_PC_TOOL_DESC
        self.canRunInBackground = False
        self.category = config.ILI_PC_TOOL_CATAGORY  
               
    def getParameterInfo(self):
               
        # Input ILI point featuere - Parameter [0]       
        in_ili_features = arcpy.Parameter(displayName="Input ILI Features",
            name="in_ili_features",
            datatype=["GPFeatureLayer","GPTableView"],
            parameterType="Required",
            direction="Input")
        #in_ili_features.filter.list = ["Point"]

         # Input Pipe Parameter type - Parameter [1]
        in_pipe_parameter_type = arcpy.Parameter(displayName="Input Pipe Parameter Source",
            name="in_pipe_parameter_type",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        in_pipe_parameter_type.filter.list = config.ILI_PIPE_PARAMETER_TYPE
        in_pipe_parameter_type.value = config.ILI_PIPE_PARAMETER_TYPE[0]
                
        # CATEGORY 1 PARAMETERS ['Length', 'MaxDepthMeasured' ,'MaxDiameter' ,'MeasuredWallThickness' ,'PipeSmys' ,'PipeMAOP', 'AreaOfMetalLoss']
        # Parameter [2]  
        in_pc_length_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Anomaly Length Field", name="in_pc_length_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_pc_length_field.parameterDependencies = [in_ili_features.name]       
        in_pc_length_field.filter.list = ['int', 'long', 'double']
        
        # Parameter [3] 
        in_pc_MaxDepthMeasured_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Max Depth Measured Field", name="in_pc_MaxDepthMeasured_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_pc_MaxDepthMeasured_field.parameterDependencies = [in_ili_features.name]
        in_pc_MaxDepthMeasured_field.filter.list = ['int', 'long', 'double']

        # Parameter [4]
        in_pc_MaxDiameter_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Diameter Field", name="in_pc_MaxDiameter_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_pc_MaxDiameter_field.parameterDependencies = [in_ili_features.name]
        in_pc_MaxDiameter_field.filter.list = ['int', 'long', 'double']

        # Parameter [5]
        in_pc_MeasuredWallThickness_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Measured Wall Thickness Field", name="in_pc_MeasuredWallThickness_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_pc_MeasuredWallThickness_field.parameterDependencies = [in_ili_features.name]
        in_pc_MeasuredWallThickness_field.filter.list = ['int', 'long', 'double']

        # Parameter [6]
        in_pc_PipeSmys_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Pipe SMYS Field", name="in_pc_PipeSmys_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_pc_PipeSmys_field.parameterDependencies = [in_ili_features.name]
        in_pc_PipeSmys_field.filter.list = ['int', 'long', 'double']         

        # Parameter [7]
        in_pc_PipeMAOP_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Pipe MAOP Field", name="in_pc_PipeMAOP_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_pc_PipeMAOP_field.parameterDependencies = [in_ili_features.name]
        in_pc_PipeMAOP_field.filter.list = ['int', 'long', 'double']

        # Parameter [8]
        in_pc_PipeSmys_fieldvalue = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_3,
            displayName="Pipe SMYS Value", name="in_pc_PipeSmys_fieldvalue",
            datatype="GPDouble", parameterType="optional", direction="Input")      
        
        # Parameter [9]
        in_pc_PipeMAOP_fieldvalue = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_3,
            displayName="Pipe MAOP Value", name="in_pc_PipeMAOP_fieldvalue",
            datatype="GPDouble", parameterType="optional", direction="Input")        
                      
        # Input Pipelie featuere - Parameter [10]    
        in_ili_pipe_features = arcpy.Parameter(displayName="Input Pipe Segment Features",
            name="in_ili_pipe_features",
            datatype="GPFeatureLayer",
            parameterType="optional",
            direction="Input")
        in_ili_pipe_features.filter.list = ["Polyline"]

        # Input Pipelie featuere - Parameter [11]    
        in_ili_maop_features = arcpy.Parameter(displayName="Input MAOP Features",
            name="in_ili_maop_features",
            datatype="GPFeatureLayer",
            parameterType="optional",
            direction="Input")
        in_ili_maop_features.filter.list = ["Polyline"]

        # Parameter [12]
        in_ps_syms_field = arcpy.Parameter(category ="Input Pipe Segment Data Fields",
            displayName="SMYS Field", name="in_ps_syms_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_ps_syms_field.parameterDependencies = [in_ili_pipe_features.name]      
        #in_ps_syms_field.filter.list = ['int', 'long', 'double']
                
        # Parameter [13]
        in_maop_field = arcpy.Parameter(category ="Input MAOP Data Field",
            displayName="MAOP Field", name="in_maop_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_maop_field.parameterDependencies = [in_ili_maop_features.name]       
        in_maop_field.filter.list = ['int', 'long', 'double']

        # Parameter [14]
        in_pc_pipeBurstPressure_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Pipe Burst Pressure Field", name="in_pc_pipeBurstPressurer_field",
            datatype="GPString", parameterType="Required", direction="Input")
        in_pc_pipeBurstPressure_field.filter.list = ['int', 'long', 'double']

        # Parameter [15]
        in_pc_modPipeBurstPressure_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Modified Pipe Burst Pressure Field", name="in_pc_modPipeBurstPressure_field",
            datatype="GPString", parameterType="Required", direction="Input")
        in_pc_modPipeBurstPressure_field.filter.list = ['int', 'long', 'double']
       
        # Parameter [16]
        in_pc_calculatePressure_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Calculated Safety Pressure Field", name="in_pc_calculatePressure_field",
            datatype="GPString", parameterType="Required", direction="Input")
        in_pc_calculatePressure_field.filter.list = ['int', 'long', 'double']

        # Parameter [17]
        in_pc_referencePressure_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Reference Pressure Field", name="in_pc_referencePressure_field",
            datatype="GPString", parameterType="Required", direction="Input")
        in_pc_referencePressure_field.filter.list = ['int', 'long', 'double']
      
        # Parameter [18]
        in_pc_safetyFactor_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Safety Factor Field", name="in_pc_safetyFactor_field",
            datatype="GPString", parameterType="Required", direction="Input")
        in_pc_modPipeBurstPressure_field.filter.list = ['int', 'long', 'double']
       
        # Parameter [19]
        in_pc_pressureReferencedRatio_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Pressure Referenced Ratio Field", name="in_pc_pressureReferencedRatio_field",
            datatype="GPString", parameterType="Required", direction="Input")
        in_pc_pressureReferencedRatio_field.filter.list = ['int', 'long', 'double']

        # Parameter [20]
        in_pc_estimatedRepairFactor_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Estimated Repair Factor Field", name="in_pc_estimatedRepairFactor_field",
            datatype="GPString", parameterType="Required", direction="Input")
        in_pc_estimatedRepairFactor_field.filter.list = ['int', 'long', 'double']

        # Parameter [21]
        in_pc_rupturePressureRatio_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Rupture Pressure Ratio Field", name="in_pc_rupturePressureRatio_field",
            datatype="GPString", parameterType="Required", direction="Input")
        in_pc_rupturePressureRatio_field.filter.list = ['int', 'long', 'double']
    
        parameters = [in_ili_features,
                      in_pipe_parameter_type, 
                      in_pc_length_field,
                      in_pc_MaxDepthMeasured_field,
                      in_pc_MaxDiameter_field,
                      in_pc_MeasuredWallThickness_field,
                      in_pc_PipeSmys_field,
                      in_pc_PipeMAOP_field,
                      in_pc_PipeSmys_fieldvalue,
                      in_pc_PipeMAOP_fieldvalue, 
                      in_ili_pipe_features,
                      in_ili_maop_features,
                      in_ps_syms_field,
                      in_maop_field,
                      in_pc_pipeBurstPressure_field, 
                      in_pc_modPipeBurstPressure_field,
                      in_pc_calculatePressure_field, 
                      in_pc_referencePressure_field, 
                      in_pc_safetyFactor_field, 
                      in_pc_pressureReferencedRatio_field, 
                      in_pc_estimatedRepairFactor_field, 
                      in_pc_rupturePressureRatio_field                  
                      ]

        return parameters

    def isLicensed(self):  # optional
        return True
        #return LicenseOperation.is_licensed

    def updateParameters(self, parameters):
        if(parameters[0].value):
            des = arcpy.Describe(parameters[0].value)
            if(des.datatype=='FeatureClass' or des.datatype=='FeatureLayer'):
                parameters[1].filter.list = config.ILI_PIPE_PARAMETER_TYPE
            else:
                parameters[1].filter.list = config.ILI_PIPE_PARAMETER_TYPE[:2]

        # Populate dependent fields from the input feature class      
        if(parameters[1].value):
            if parameters[1].value == config.ILI_PIPE_PARAMETER_TYPE[1]: 
               # Manual Pipe Information
               parameters[2].enabled = True
               parameters[3].enabled = True
               parameters[4].enabled = True
               parameters[5].enabled = True
               parameters[6].enabled = False
               parameters[7].enabled = False
               parameters[8].enabled = True
               parameters[9].enabled = True
               parameters[10].enabled = False 
               parameters[11].enabled = False
               parameters[12].enabled = False
               parameters[13].enabled = False
               parameters[14].enabled = True 
               parameters[15].enabled = True
               parameters[16].enabled = True
               parameters[17].enabled = True
               parameters[18].enabled = True
               parameters[19].enabled = True
               parameters[20].enabled = True
               parameters[21].enabled = True
              
            elif parameters[1].value == config.ILI_PIPE_PARAMETER_TYPE[2]:
               #Pipe Information from Pipe Segment feature class       
               parameters[2].enabled = True
               parameters[3].enabled = True
               parameters[4].enabled = True
               parameters[5].enabled = True
               parameters[6].enabled = False              
               parameters[7].enabled = False              
               parameters[8].enabled = False
               parameters[9].enabled = False
               parameters[10].enabled = True
               parameters[11].enabled = True 
               parameters[12].enabled = True
               parameters[13].enabled = True
               parameters[14].enabled = True
               parameters[21].enabled = True
                             
            else:                                     
               #Pipe information from ILI Data
               parameters[2].enabled = True
               parameters[3].enabled = True
               parameters[4].enabled = True
               parameters[5].enabled = True
               parameters[6].enabled = True               
               parameters[7].enabled = True 
               parameters[8].enabled = False #Manual SMYS Value from user
               parameters[9].enabled = False #Manual MAOP Value from user
               parameters[10].enabled = False
               parameters[11].enabled = False
               parameters[12].enabled = False
               parameters[13].enabled = False
               parameters[14].enabled = True
               parameters[15].enabled = True
               parameters[16].enabled = True
               parameters[17].enabled = True
               parameters[18].enabled = True
               parameters[19].enabled = True
               parameters[20].enabled = True
               parameters[21].enabled = True
               
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
              
            if not parameters[2].value:
                if config.ILI_PC_REQ_FIELDS[0].upper() in flds:
                    parameters[2].value = config.ILI_PC_REQ_FIELDS[0]
            if not parameters[3].value:
                if config.ILI_PC_REQ_FIELDS[1].upper() in flds:
                    parameters[3].value = config.ILI_PC_REQ_FIELDS[1]
            if not parameters[4].value:
                if config.ILI_PC_REQ_FIELDS[2].upper() in flds:
                    parameters[4].value = config.ILI_PC_REQ_FIELDS[2]
            if not parameters[5].value:
                if config.ILI_PC_REQ_FIELDS[3].upper() in flds:
                    parameters[5].value = config.ILI_PC_REQ_FIELDS[3]
            if not parameters[6].value:
                if config.ILI_PC_REQ_FIELDS[4].upper() in flds:
                    parameters[6].value = config.ILI_PC_REQ_FIELDS[4]
            if not parameters[7].value:
                if config.ILI_PC_REQ_FIELDS[5].upper() in flds:
                    parameters[7].value = config.ILI_PC_REQ_FIELDS[5]

        if(parameters[10].value):
            flds_p = [] 
            fc=parameters[10].value
            if(fc):
                fls = []           
                fls += [f.name.upper() for f in arcpy.ListFields (fc)]
                
                flds=[]
                for f in fls:
                    x=f.split('.')
                    if len(x)>1:
                        x1=x[1]
                        flds_p.append(x1)
                    else:
                        flds_p.append(f)          
            if not parameters[12].value:
               if config.ILI_PIPE_REQ_FIELDS[0].upper() in flds_p:
                    parameters[12].value = config.ILI_PIPE_REQ_FIELDS[0]
          
        if(parameters[11].value):
            flds_m = [] 
            fc=parameters[11].value
            if(fc):
                fls = []           
                fls += [f.name.upper() for f in arcpy.ListFields (fc)]
                
                flds=[]
                for f in fls:
                    x=f.split('.')
                    if len(x)>1:
                        x1=x[1]
                        flds_m.append(x1)
                    else:
                        flds_m.append(f)          
            if not parameters[13].value:
                if config.ILI_MAOP_REQ_FIELDS[0].upper() in flds_m:
                    parameters[13].value = config.ILI_MAOP_REQ_FIELDS[0]

        # Assigning add field  #config.ILI_PC_ADDING_FIELDS[0]
        if(parameters[0].value):
            flds = []
            fc=parameters[0].value
            flds += [f.name for f in arcpy.ListFields (fc)]

            for i in range(14, 22):
                if not parameters[i].value:
                   j=i-14
                   comparevalue= config.ILI_PC_ADDING_FIELDS[j]
                   self.populate_add_field(flds,parameters,i,comparevalue)           
        else:
            for i in range(2, 22):
                parameters[i].value = None

        return

    def updateMessages(self, parameters):                     
      
        if(parameters[1].value):
            if parameters[1].value == config.ILI_PIPE_PARAMETER_TYPE[1]: 
                if(parameters[0].Value):
                    if not parameters[2].value:
                        parameters[2].setErrorMessage("You must supply a value for the parameter Length")
                    if not parameters[3].value:
                        parameters[3].setErrorMessage("You must supply a value for the parameter Max Depth Measure")
                    if not parameters[4].value:
                        parameters[4].setErrorMessage("You must supply a value for the parameter Diameter")
                    if not parameters[5].value:
                        parameters[5].setErrorMessage("You must supply a value for the parameter Wall Thickness")
                    if not parameters[8].value:
                        parameters[8].setErrorMessage("You must supply a value for the parameter Pipe SMYS")
                    if not parameters[9].value:
                       parameters[9].setErrorMessage("You must supply a value for the parameter Pipe MAOP")
     
            elif parameters[1].value == config.ILI_PIPE_PARAMETER_TYPE[2]:
                if(parameters[0].value):
                    if not parameters[2].value:
                        parameters[2].setErrorMessage("You must supply a value for the parameter Length")
                    if not parameters[3].value:
                        parameters[3].setErrorMessage("You must supply a value for the parameter Max Depth Measure")
                if(parameters[10].value):   
                    if not parameters[12].value:
                        parameters[12].setErrorMessage("You must supply a value for the parameter SMYS")
                    
                if(parameters[11].value):
                    if not parameters[13].value:
                        parameters[13].setErrorMessage("You must supply a value for the parameter MAOP")

            elif parameters[1].value == config.ILI_PIPE_PARAMETER_TYPE[0]:   
                if(parameters[0].value):
                    if not parameters[2].value:
                        parameters[2].setErrorMessage("You must supply a value for the parameter Length")
                    if not parameters[3].value:
                        parameters[3].setErrorMessage("You must supply a value for the parameter Max Depth Measure")
                    if not parameters[4].value:
                        parameters[4].setErrorMessage("You must supply a value for the parameter Diameter")
                    if not parameters[5].value:
                        parameters[5].setErrorMessage("You must supply a value for the parameter Wall Thickness")
                    if not parameters[6].value:
                        parameters[6].setErrorMessage("You must supply a value for the parameter Pipe SMYS")
                    if not parameters[7].value:
                        parameters[7].setErrorMessage("You must supply a value for the parameter Pipe MAOP")
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
                    if(parameters[1].value==config.ILI_PIPE_PARAMETER_TYPE[2]):
                       #self.build_segmentor_table(parameters)
                       self.build_spatialjoin_table(parameters)
                       #inlineinspection.AddMessage("Option 3 is proceeding ")
                    else:
                        ht_result_flag = False
                        calculateilipressures = CalculateILIPressures()                           
                        calculateilipressures.fieldsCaliculation(parameters)
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

    def get_missing_fields(self, infields, required_fields):
        '''
        :param infields: list of layer fields
        :param required_fields:  list of required fields
        :return: checks the required fields in the infields and returns missing fields
        '''
        missing_flds = []
        for fld in required_fields:
            if fld.upper() not in infields:
                missing_flds.append(fld)

        return missing_flds

    def populate_add_field(self,flds,parameters,idx,addfield):
        inlineinspection.AddMessage("Processing field {} ".format(addfield))
        if(not addfield in flds):
                   #datatype="Field"  
                   flds_1 = []
                   flds_1 =flds
                   flds_1.append(addfield)
                   parameters[idx].filter.list = flds_1

        else:
                    parameters[idx].filter.list = flds

        parameters[idx].value = addfield
   
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

    def build_spatialjoin_table(self,parameters):

        try:
            ili_layer =parameters[0].valueAsText
            pipesegment_layer=parameters[10].valueAsText       
            maop_layer = parameters[11].valueAsText
           
            syms_field = parameters[12].valueAsText
            maop_field = parameters[13].valueAsText            
            
            #Create temp gdb to process and store intermediate data
            self.ILI_TEMP_FOLDER = "ILI_TEMP"
            self.ILI_TEMP_GDB = "ILI_TEMP_GDB.gdb"
            tempoutput_workspace = arcpy.env.scratchFolder if arcpy.Exists(arcpy.env.scratchFolder) and arcpy.env.scratchFolder is not None else self.output_dir
            tempoutput_dir = os.path.join(tempoutput_workspace, self.ILI_TEMP_FOLDER )
            tempoutput_gdb = self.ILI_TEMP_GDB 
            self.tempoutputgdb_path = os.path.join(tempoutput_dir, tempoutput_gdb)
                   
            # Create temp gbd for intermediate process
            self.createtempgdb(tempoutput_dir, tempoutput_gdb)
            inlineinspection.AddMessage("Temp gdb is created and the path is {}".format(self.tempoutputgdb_path))

            spatial_join1 = FuncParam(self.tempoutputgdb_path  + "\\ILIData_SJ1")
            spatialjoin1 =spatial_join1.valueAsText
            if arcpy.Exists(spatialjoin1):
                arcpy.Delete_management(spatialjoin1)

            spatial_join2 = FuncParam(self.tempoutputgdb_path  + "\\ILIData_SJ2")
            spatialjoin2 =spatial_join2.valueAsText
            if arcpy.Exists(spatialjoin2):
                arcpy.Delete_management(spatialjoin2)

            inlineinspection.AddMessage("spatial join1 feature {} {} {}".format(spatialjoin1,ili_layer,pipesegment_layer))
            arcpy.SpatialJoin_analysis(ili_layer, pipesegment_layer, spatialjoin1, "JOIN_ONE_TO_ONE", "KEEP_ALL", r'EventID "EventID" true true false 38 Guid 0 0,First,#,'+ili_layer+',EventID,-1,-1;'+config.OUTPUT_SYMS_FIELDNAME+' "'+config.OUTPUT_SYMS_FIELDNAME+'" true true false 50 Long 0 0,First,#,'+pipesegment_layer+','+syms_field+',0,50', "INTERSECT", None, '')
            inlineinspection.AddMessage("Spatial Join is performed on Pipe Segment")
                       
            arcpy.SpatialJoin_analysis(spatialjoin1, maop_layer, spatialjoin2, "JOIN_ONE_TO_ONE", "KEEP_ALL", r'EventID "EventID" true true false 38 Guid 0 0,First,#,'+spatialjoin1+',EventID,-1,-1;'+config.OUTPUT_SYMS_FIELDNAME+' "'+config.OUTPUT_SYMS_FIELDNAME+'" true true false 4 Long 0 0,First,#,'+spatialjoin1+','+config.OUTPUT_SYMS_FIELDNAME+',-1,-1;'+config.OUTPUT_MAOP_FIELDNAME+' "'+config.OUTPUT_MAOP_FIELDNAME+'" true true false 4 Long 0 0,First,#,'+maop_layer+','+maop_field+',-1,-1', "INTERSECT", None, '')
            inlineinspection.AddMessage("Spatial Join is performed on MAOP")

            #Check and delete if fields existing.
            ili_flds=[]           
            ili_flds += [f.name.upper() for f in arcpy.ListFields (ili_layer)]
            delete_fields=""
            if(config.OUTPUT_SYMS_FIELDNAME in ili_flds):
                delete_fields=""+config.OUTPUT_SYMS_FIELDNAME
            if(config.OUTPUT_MAOP_FIELDNAME in ili_flds):
                if(len(delete_fields)>0):
                    delete_fields=delete_fields+";"+config.OUTPUT_MAOP_FIELDNAME
                else:
                    delete_fields=""+config.OUTPUT_MAOP_FIELDNAME

            if(len(delete_fields)>0):
                arcpy.management.DeleteField(ili_layer, delete_fields)
                inlineinspection.AddMessage("Deleted existing temp fields")

            arcpy.management.AddFields(ili_layer, ""+config.OUTPUT_SYMS_FIELDNAME+" LONG # # # #;"+config.OUTPUT_MAOP_FIELDNAME+" LONG # # # #")
            inlineinspection.AddMessage("Added temp fields")
          
            #Add join with ILI Layer          
            arcpy.AddJoin_management(ili_layer, "EventID", spatialjoin2, "EventID", "KEEP_ALL")            
            inlineinspection.AddMessage("Join is performed on ILI Data")
            ili_layer_name=os.path.basename(ili_layer)
            
            arcpy.management.CalculateField(ili_layer, ili_layer_name+'.'+config.OUTPUT_SYMS_FIELDNAME , "!ILIData_SJ2."+config.OUTPUT_SYMS_FIELDNAME+"!", "PYTHON3", '', "TEXT")
            arcpy.management.CalculateField(ili_layer, ili_layer_name+'.'+config.OUTPUT_MAOP_FIELDNAME, "!ILIData_SJ2."+config.OUTPUT_MAOP_FIELDNAME+"!", "PYTHON3", '', "TEXT")
            inlineinspection.AddMessage("Calculate temp fields")

            arcpy.management.RemoveJoin(ili_layer, "ILIData_SJ2")
            inlineinspection.AddMessage("Existing Join is removed from ILI Data")

            calulatepressure= CalculateILIPressures()
            calulatepressure.fieldsCaliculation(parameters)
            inlineinspection.AddMessage("Caliculation is performed")            

            arcpy.management.DeleteField(ili_layer, ""+config.OUTPUT_SYMS_FIELDNAME+";"+config.OUTPUT_MAOP_FIELDNAME+"")
            inlineinspection.AddMessage("Deleted temp fields")

        except Exception as e:
            tb = sys.exc_info()[2]
            inlineinspection.AddError("An error occurred on line %i" % tb.tb_lineno)
            inlineinspection.AddError(str(e))
            inlineinspection.AddError("Issue in build spatial join creation, Please check and try again.\n{}".format(arcpy.GetMessages(2)))
            return False

class CalculateILIPressures(object):

    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        #self.label = "ILI Pressure Calculator Tool"        
    
    '''Add The output fields if not exist'''
    def addMissingField(self,fc,outFields):
        if(fc):
            flds = []            
            flds += [f.name.upper() for f in arcpy.ListFields (fc)]           
            f1=[]
            for f in flds:
                x=f.split('.')
                if len(x)>1:
                    x1=x[1]
                    f1.append(x1)
                else:
                    f1.append(f)
           
            for outField in outFields:
                if not outField.upper() in flds: 
                    # Execute AddField for new fields
                    arcpy.AddField_management(fc, outField, "LONG", 9,
                                              field_alias=outField, field_is_nullable="NULLABLE")
                    inlineinspection.AddMessage("{} field added".format(outField))        

    def fieldsCaliculation(self,parameters):
        try:
            fields=[]     
            inFeatures=parameters[0].valueAsText
            lengthField=parameters[2].valueAsText
            maxDepthMeasure=parameters[3].valueAsText
            maxDiameter=parameters[4].valueAsText
            measuredWallthickness=parameters[5].valueAsText
            pipeSmys=parameters[6].valueAsText
            pipeMAOPField=parameters[7].valueAsText                       

            fPipeBurstPressure=parameters[14].valueAsText
            fModPipeBurstPressure=parameters[15].valueAsText
            fCalculatedPressure=parameters[16].valueAsText
            fReferencePressure=parameters[17].valueAsText
            fSafetyFactor=parameters[18].valueAsText
            fPressureReferencedRatio=parameters[19].valueAsText
            fEstimatedRepairFactor=parameters[20].valueAsText
            fRupturePressureRatio=parameters[21].valueAsText
            eventidField ="EVENTID"

            outputfields=[fPipeBurstPressure,fModPipeBurstPressure,fCalculatedPressure,fReferencePressure,fSafetyFactor,fPressureReferencedRatio,fEstimatedRepairFactor,fRupturePressureRatio]           
                      
            if(parameters[1].value==config.ILI_PIPE_PARAMETER_TYPE[1]):
                pipeSmysValOrField =parameters[8].valueAsText
                pipeMaopValOrField =parameters[9].valueAsText
                #*** Need to modify this filed as properly
                pipeSmys=lengthField
                pipeMAOPField=lengthField

            elif(parameters[1].value==config.ILI_PIPE_PARAMETER_TYPE[2]):                           
                pipeSmys=config.OUTPUT_SYMS_FIELDNAME
                pipeMAOPField=config.OUTPUT_MAOP_FIELDNAME                
            else:
                pipeSmys=parameters[6].valueAsText                
                pipeMAOPField=parameters[7].valueAsText               

            infields=[lengthField,maxDepthMeasure,maxDiameter,measuredWallthickness,pipeSmys,pipeMAOPField,eventidField]
            fields=infields+outputfields
            inlineinspection.AddMessage("Input ILI Feature class {}".format(inFeatures))
            #*** Check output fields are existing or not if not add fields     
            self.addMissingField(inFeatures,outputfields)
            # Create update cursor for feature class 
            warningCounter=0
            with arcpy.da.UpdateCursor(inFeatures, fields) as cursor:
                # Update the fields based on the values               
                for row in cursor:                   
                    reventid=row[6]
                    rlength = row[0]
                    rmaxDepthMeasure = row[1]
                    rmaxDiameter =row[2]
                    rmeasuredWallthickness =row[3]
                    if(parameters[1].value==config.ILI_PIPE_PARAMETER_TYPE[1]):
                        rpipeSmys = float(pipeSmysValOrField)
                        rpipeMAOP = float(pipeMaopValOrField)
                    else:
                        rpipeSmys = row[4]
                        rpipeMAOP =row[5]

                    areaOfMetalLoss = None
                    modAreaOfMetalLoss = None
                    flowStress = None
                    modFlowStress =None
                    foliasFactor = None
                    modFoliasFactor = None
                    pipeBurstPressure = None
                    modPipeBurstPressure = None
                    calculatedPressure = None
                    referencePressure = None
                    safetyFactor = None
                    pressureReferencedRatio = None
                    estimatedRepairFactor = None
                    rupturePressureRatio = None

                    #calculate Area Of Metal Loss
                    if(rlength and rmaxDepthMeasure):                        
                        areaOfMetalLoss = (2/3)*(rmaxDepthMeasure)*(rlength)
                      
                    else:                        
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Area of Metal Loss is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1             
                    # calculate Mod Area Of Metal Loss              
                    if(rlength and rmaxDepthMeasure):                        
                        modAreaOfMetalLoss = (.85)*(rmaxDepthMeasure)*(rlength)
                      
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Mod Area of Metal Loss is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1                        
                    # calculate Flow Stress
                    if(rpipeSmys):                        
                        flowStress = (1.1)*rpipeSmys
                       
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Flow Stress is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculate mod Flow Stress
                    if(rpipeSmys):                        
                        modFlowStress = (rpipeSmys+10000)
                        
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Mod Flow Stress is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculate foliasFactor
                    if(rlength and rmaxDiameter and rmeasuredWallthickness):                        
                        foliasFactor=0
                        if rlength <(20*rmaxDiameter*rmeasuredWallthickness)**(.5):
                            foliasFactor= math.sqrt((1 + 0.8 * (rlength**2/(rmaxDiameter*rmeasuredWallthickness))))                      
                                             
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Folias Factor is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculate mod Folias Factor
                    if(rlength and rmaxDiameter and rmeasuredWallthickness):                        
                        modFoliasFactor=0
                        if rlength**2/(rmaxDiameter*rmeasuredWallthickness)<=50:
                            modFoliasFactor = math.sqrt((1+(0.6275*(rlength**2/(rmaxDiameter*rmeasuredWallthickness)))-(0.003375*(((rlength**2)/(rmaxDiameter*rmeasuredWallthickness))**2))))
                        elif rlength**2/(rmaxDiameter*rmeasuredWallthickness)>50:
                            modFoliasFactor = ((.032)*((rlength**2)/(rmaxDiameter*rmeasuredWallthickness)))+3.3                   
                       
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Mod Folias Factor is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculate pipe Burst Pressure
                    if(flowStress and areaOfMetalLoss and foliasFactor and rlength and rmaxDiameter and rmeasuredWallthickness):                        
                        pipeBurstPressure = flowStress*((1-(areaOfMetalLoss/(rmeasuredWallthickness*rlength)))/(1-(areaOfMetalLoss/(rmeasuredWallthickness*rlength*foliasFactor))))*((2*rmeasuredWallthickness)/rmaxDiameter)
                        
                        row[7]=pipeBurstPressure
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Pipe Burst Pressure is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculate Mod Pipe Burst Pressure
                    if(modFlowStress and modAreaOfMetalLoss and modFoliasFactor and rlength and rmaxDiameter and rmeasuredWallthickness):                        
                        modPipeBurstPressure = (modFlowStress)*((1-(modAreaOfMetalLoss/(rmeasuredWallthickness*rlength)))/(1-(modAreaOfMetalLoss/(rmeasuredWallthickness*rlength*(modFoliasFactor)))))*((2*rmeasuredWallthickness)/rmaxDiameter)
                        #*** Check the formula
                        row[8]=modPipeBurstPressure
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Mod Pipe Burst Pressure is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculated Pressure
                    if(pipeBurstPressure and rpipeMAOP and rpipeSmys):                        
                        calculatedPressure = (pipeBurstPressure*(rpipeMAOP)/(rpipeSmys))
                        row[9]=calculatedPressure
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} calculated Pressure is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculated Reference Pressure
                    if(rpipeMAOP):
                        referencePressure = rpipeMAOP
                        row[10]=referencePressure
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Reference Pressure is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculated Safety Factor
                    if(rpipeMAOP and pipeBurstPressure):
                        safetyFactor = (pipeBurstPressure/rpipeMAOP)
                        row[11]=safetyFactor
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Safety Factor is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculated Pressure Referenced Ratio
                    if(calculatedPressure and referencePressure):
                        pressureReferencedRatio = (calculatedPressure/referencePressure)
                        row[12]=pressureReferencedRatio
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Pressure Referenced Ratio is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculated Estimated Repair Factor
                    if(rpipeMAOP and calculatedPressure):
                        estimatedRepairFactor = (rpipeMAOP/calculatedPressure)
                        row[13]=estimatedRepairFactor
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Estimated Repair Factor is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculated Rupture Pressure Ratio
                    if(rpipeSmys and pipeBurstPressure):
                        rupturePressureRatio = (pipeBurstPressure/rpipeSmys)
                        row[14]=rupturePressureRatio
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Rupture Pressure Ratio is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    
                    cursor.updateRow(row) 
                    
            inlineinspection.AddWarning("Total number of warning {} due to values are null or empty, Please check the log file for details".format(warningCounter))
        except Exception as e:
            # If an error occurred, print line number and error message
            tb = sys.exc_info()[2]
            arcpy.AddError("An error occurred on line %i" % tb.tb_lineno)
            arcpy.AddError(str(e))

   