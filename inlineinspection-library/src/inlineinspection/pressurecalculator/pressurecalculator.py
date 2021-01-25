
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

         # Input Pipe Features - Parameter [1]
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
        in_pc_length_field.value = config.ILI_PC_REQ_FIELDS[0]

        # Parameter [3] 
        in_pc_MaxDepthMeasured_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Max Depth Measured Field", name="in_pc_MaxDepthMeasured_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_pc_MaxDepthMeasured_field.parameterDependencies = [in_ili_features.name]
        in_pc_MaxDepthMeasured_field.value = config.ILI_PC_REQ_FIELDS[1]

        # Parameter [4]
        in_pc_MaxDiameter_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Diameter Field", name="in_pc_MaxDiameter_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_pc_MaxDiameter_field.parameterDependencies = [in_ili_features.name]
        in_pc_MaxDiameter_field.value = config.ILI_PC_REQ_FIELDS[2]

        # Parameter [5]
        in_pc_MeasuredWallThickness_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Measured Wall Thickness Field", name="in_pc_MeasuredWallThickness_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_pc_MeasuredWallThickness_field.parameterDependencies = [in_ili_features.name]
        in_pc_MeasuredWallThickness_field.value = config.ILI_PC_REQ_FIELDS[3]

        # Parameter [6]
        in_pc_PipeSmys_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Pipe SMYS Field", name="in_pc_PipeSmys_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_pc_PipeSmys_field.parameterDependencies = [in_ili_features.name]
        in_pc_PipeSmys_field.value = config.ILI_PC_REQ_FIELDS[4]              

        # Parameter [7]
        in_pc_PipeMAOP_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Pipe MAOP Field", name="in_pc_PipeMAOP_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_pc_PipeMAOP_field.parameterDependencies = [in_ili_features.name]
        in_pc_PipeMAOP_field.value = config.ILI_PC_REQ_FIELDS[5]

        #Catigory 2 parameters 'AreaOfMetalLoss', 'modAreaOfMetalLoss', 'flowStress', etc.]
        
        # Parameter [8]
        in_pc_AreaOfMetalLoss_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Area of Metal Loss Field", name="in_pc_AreaOfMetalLoss_field",
            datatype="GPString", parameterType="Required", direction="Input")
      
        # Parameter [9]
        in_pc_modAreaOfMetalLoss_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Modified Area of Metal Loss Field", name="in_pc_modAreaOfMetalLoss_field",
            datatype="GPString", parameterType="Required", direction="Input")
       
        # Parameter [10]
        in_pc_flowStress_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Flow Stress Field", name="in_pc_flowStress_field",
            datatype="GPString", parameterType="Required", direction="Input")
        # Parameter [11]
        in_pc_modflowStress_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Modified Flow Stress Field", name="in_pc_modflowStress_field",
            datatype="GPString", parameterType="Required", direction="Input")
        # Parameter [12]
        in_pc_foliasFactor_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Folias Factor Field", name="in_pc_foliasFactor_field",
            datatype="GPString", parameterType="Required", direction="Input")
        # Parameter [13]
        in_pc_modFoliasFactor_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Modified Folias Factor Field", name="in_pc_modFoliasFactor_field",
            datatype="GPString", parameterType="Required", direction="Input")
        # Parameter [14]
        in_pc_pipeBurstPressure_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Pipe Burst Pressure Field", name="in_pc_pipeBurstPressurer_field",
            datatype="GPString", parameterType="Required", direction="Input")
        # Parameter [15]
        in_pc_modPipeBurstPressure_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Modified Pipe Burst Pressure Field", name="in_pc_modPipeBurstPressure_field",
            datatype="GPString", parameterType="Required", direction="Input")
       
        # Parameter [16]
        in_pc_calculatePressure_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Calculate Pressure Field", name="in_pc_calculatePressure_field",
            datatype="GPString", parameterType="Required", direction="Input")
       
        # Parameter [17]
        in_pc_referencePressure_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Reference Pressure Pressure Field", name="in_pc_referencePressure_field",
            datatype="GPString", parameterType="Required", direction="Input")
      
        # Parameter [18]
        in_pc_safetyFactor_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Safety Factor Field", name="in_pc_safetyFactor_field",
            datatype="GPString", parameterType="Required", direction="Input")
       
        # Parameter [19]
        in_pc_pressureReferencedRatio_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Pressure Referenced Ratio Field", name="in_pc_pressureReferencedRatio_field",
            datatype="GPString", parameterType="Required", direction="Input")

        # Parameter [20]
        in_pc_estimatedRepairFactor_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Estimated Repair Factor Field", name="in_pc_estimatedRepairFactor_field",
            datatype="GPString", parameterType="Required", direction="Input")

        # Parameter [21]
        in_pc_rupturePressureRatio_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Rupture Pressure Ratio Field", name="in_pc_rupturePressureRatio_field",
            datatype="GPString", parameterType="Required", direction="Input")

             
        # Parameter [22]
        in_pc_PipeSmys_fieldvalue = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_3,
            displayName="Pipe SMYS Value", name="in_pc_PipeSmys_fieldvalue",
            datatype="GPDouble", parameterType="optional", direction="Input")       
        

        # Parameter [23]
        in_pc_PipeMAOP_fieldvalue = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_3,
            displayName="Pipe MAOP Value", name="in_pc_PipeMAOP_fieldvalue",
            datatype="GPDouble", parameterType="optional", direction="Input")        
        

        ## Parameter [24]
        #in_pc_pl_PipeSmys_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
        #    displayName="Pipe Line SMYS Field", name="in_pc_pl_PipeSmys_field",
        #    datatype="Field", parameterType="Required", direction="Input")
        #in_pc_pl_PipeSmys_field.parameterDependencies = [in_ili_pipe_features.name]
        #in_pc_pl_PipeSmys_field.value = config.ILI_PC_REQ_FIELDS[4]

        ## Parameter [25]
        #in_pc_pl_PipeMAOP_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
        #    displayName="Pipe Line MAOP Field", name="in_pc_pl_PipeMAOP_field",
        #    datatype="Field", parameterType="Required", direction="Input")
        #in_pc_pl_PipeMAOP_field.parameterDependencies = [in_ili_pipe_features.name]
        #in_pc_pl_PipeMAOP_field.value = config.ILI_PC_REQ_FIELDS[5]                  
        

        # Input Pipelie featuere - Parameter [24]    
        in_ili_pipe_features = arcpy.Parameter(displayName="Input Pipe Segment Features",
            name="in_ili_pipe_features",
            datatype="GPFeatureLayer",
            parameterType="optional",
            direction="Input")
        in_ili_pipe_features.filter.list = ["Polyline"]

        # Input Pipelie featuere - Parameter [25]    
        #in_ili_stationseries_features = arcpy.Parameter(displayName="Input Station Series Feature Class",
        #    name="in_ili_stationseries_features",
        #    datatype="GPFeatureLayer",
        #    parameterType="optional",
        #    direction="Input")
        #in_ili_stationseries_features.filter.list = ["Polyline"]

        # Input Pipelie featuere - Parameter [26]    
        in_ili_maop_features = arcpy.Parameter(displayName="Input MAOP Features",
            name="in_ili_maop_features",
            datatype="GPFeatureLayer",
            parameterType="optional",
            direction="Input")
        in_ili_maop_features.filter.list = ["Polyline"]

        # Parameter [27]
       # in_ss_routeid_field = arcpy.Parameter(category ="Centerline Route Parameters",
       #    displayName="Unique ID Field", name="in_ss_routeid_field",
       #    datatype="Field", parameterType="Required", direction="Input")
       # in_ss_routeid_field.parameterDependencies = [in_ili_stationseries_features.name]
       # in_ss_routeid_field.value = "Route_ID"

        # Parameter [28]
        #in_ss_begin_m_field = arcpy.Parameter(category ="Centerline Route Parameters",
        #    displayName="Begin Measure Field", name="in_ss_begin_m_field",
        #    datatype="Field", parameterType="optional", direction="Input")
       #in_ss_begin_m_field.parameterDependencies = [in_ili_stationseries_features.name]
        #in_ss_begin_m_field.value = "BeginMeasure"

        # Parameter [29]
        #in_ss_end_m_field = arcpy.Parameter(category ="Centerline Route Parameters",
        #    displayName="End Measure Field", name="in_ss_end_m_field",
        #    datatype="Field", parameterType="optional", direction="Input")
        #in_ss_end_m_field.parameterDependencies = [in_ili_stationseries_features.name]
        #in_ss_end_m_field.value = "EndMeasure"

        # Parameter [30]
        #in_ss_eventid_field = arcpy.Parameter(category ="Centerline Route Parameters",
        #    displayName="Event id Field", name="in_ss_eventid_field",
        #    datatype="Field", parameterType="optional", direction="Input")
        #in_ss_eventid_field.parameterDependencies = [in_ili_stationseries_features.name]
        #in_ss_eventid_field.value = "EventID"

        # Parameter [31]
        in_ps_diameter_field = arcpy.Parameter(category ="Input Pipe Segment Data Fields",
            displayName="Nominal Diameter Field", name="in_ps_diameter_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_ps_diameter_field.parameterDependencies = [in_ili_pipe_features.name]
        in_ps_diameter_field.value = "NominalDiameterCl"

        # Parameter [32]
        #in_ps_thickness_field = arcpy.Parameter(category ="Input Pipe Segment Data Fields",
        #    displayName="Nominal Wall Thickness Field", name="in_ps_thickness_field",
        #    datatype="Field", parameterType="optional", direction="Input")
        #in_ps_thickness_field.parameterDependencies = [in_ili_pipe_features.name]
        #in_ps_thickness_field.value = "NominalWallThicknessCl"

        # Parameter [33]
        in_ps_syms_field = arcpy.Parameter(category ="Input Pipe Segment Data Fields",
            displayName="SMYS Field", name="in_ps_syms_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_ps_syms_field.parameterDependencies = [in_ili_pipe_features.name]
        in_ps_syms_field.value = "SMYSCL"
                
       
        # Parameter [34] previous [33]
        in_maop_field = arcpy.Parameter(category ="Input MAOP Data Field",
            displayName="MAOP Field", name="in_maop_field",
            datatype="Field", parameterType="optional", direction="Input")
        in_maop_field.parameterDependencies = [in_ili_maop_features.name]
        in_maop_field.value = "MAOPRating"
    
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
                      in_ps_diameter_field,
                      in_ps_syms_field,
                      in_maop_field,
                      in_pc_AreaOfMetalLoss_field, 
                      in_pc_modAreaOfMetalLoss_field,
                      in_pc_flowStress_field, 
                      in_pc_modflowStress_field,
                      in_pc_foliasFactor_field,
                      in_pc_modFoliasFactor_field,
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
               parameters[14].enabled = False
               parameters[15].enabled = True
               parameters[16].enabled = True
               parameters[17].enabled = True
               parameters[18].enabled = True
               parameters[19].enabled = True
               parameters[20].enabled = True
               parameters[21].enabled = True
               parameters[22].enabled = True
               parameters[23].enabled = True
               parameters[24].enabled = True
               parameters[25].enabled = True
               parameters[26].enabled = True
               parameters[27].enabled = True
               parameters[28].enabled = True
              
            elif parameters[1].value == config.ILI_PIPE_PARAMETER_TYPE[2]:
               #Pipe Information from Pipe Segment feature class       
               parameters[2].enabled = True
               parameters[3].enabled = True
               parameters[4].enabled = False
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
               parameters[15].enabled = True
               parameters[16].enabled = True
               parameters[17].enabled = True
               parameters[18].enabled = True 
               parameters[19].enabled = True
               parameters[20].enabled = True
               parameters[21].enabled = True
               parameters[22].enabled = True
               parameters[23].enabled = True
               parameters[24].enabled = True
               parameters[25].enabled = True
               parameters[26].enabled = True
               parameters[27].enabled = True
               parameters[28].enabled = True


                             
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
               parameters[14].enabled = False
               parameters[15].enabled = True
               parameters[16].enabled = True
               parameters[17].enabled = True
               parameters[18].enabled = True 
               parameters[19].enabled = True #Output Data Parameters [20]-[33]:
               parameters[20].enabled = True
               parameters[21].enabled = True
               parameters[22].enabled = True
               parameters[23].enabled = True
               parameters[24].enabled = True
               parameters[25].enabled = True
               parameters[26].enabled = True
               parameters[27].enabled = True
               parameters[28].enabled = True
               
        if(parameters[0].value):
            if not parameters[2].value:
               parameters[2].value = config.ILI_PC_REQ_FIELDS[0]
            if not parameters[3].value:
               parameters[3].value = config.ILI_PC_REQ_FIELDS[1]
            if not parameters[4].value:
               parameters[4].value = config.ILI_PC_REQ_FIELDS[2]
            if not parameters[5].value:
               parameters[5].value = config.ILI_PC_REQ_FIELDS[3]
            if not parameters[6].value:
               parameters[6].value = config.ILI_PC_REQ_FIELDS[4]
            if not parameters[7].value:
               parameters[7].value = config.ILI_PC_REQ_FIELDS[5]

        if(parameters[10].value):
            if not parameters[12].value:
               parameters[12].value = config.ILI_PIPE_REQ_FIELDS[0]
            if not parameters[13].value:
               parameters[13].value = config.ILI_PIPE_REQ_FIELDS[1]
          

        if(parameters[11].value):
            if not parameters[14].value:
               parameters[14].value = config.ILI_MAOP_REQ_FIELDS[0]


            # Assigning add field  #config.ILI_PC_ADDING_FIELDS[0]
        if(parameters[0].value):
            flds = []
            fc=parameters[0].value
            flds += [f.name for f in arcpy.ListFields (fc)]

            for i in range(15, 29):
                if not parameters[i].value:
                   j=i-15
                   comparevalue= config.ILI_PC_ADDING_FIELDS[j]
                   self.populate_add_field(flds,parameters,i,comparevalue)

           
        else:
            for i in range(2, 29):
                parameters[i].value = None

        return

    def updateMessages(self, parameters):                     
        """ Check the input ILI feature class has the required fields and belongs to project database:       """
        #if parameters[0].valueAsText is not None:
        #    if(arcpy.Exists(parameters[0].value)):
        #        desc = arcpy.Describe(parameters[0])
        #        fc_path = desc.catalogPath                
        #        ili_inputs_fields = inlineinspection.get_field_names(parameters[0].value)
        #        missing_flds = self.get_missing_fields(ili_inputs_fields, config.ILI_PC_REQ_FIELDS)

        #        if len(missing_flds) > 0:
        #            missingflds = inlineinspection.list_to_string(missing_flds)
        #            parameters[0].setErrorMessage("Inline Inspection feature calss does not have required fields: {}. ".format(missingflds))
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
                        parameters[12].setErrorMessage("You must supply a value for the parameter Diameter")
                    if not parameters[13].value:
                        parameters[13].setErrorMessage("You must supply a value for the parameter SMYS")
                    
                if(parameters[11].value):
                    if not parameters[14].value:
                        parameters[14].setErrorMessage("You must supply a value for the parameter MAOP")

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
            # INPUT PARAMETERS for the process           
            #in_workspace = parameters[0].valueAsText
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
                        #ili_result_flag = calculateilipressures.run(parameters)     
                        calculateilipressures.fieldscaliculation(parameters)
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

    #def build_json_for_segmentor(self, ili_layer, maop_layer,parameters):
    #    try:

    #        # Build json string
    #        #self.structure_segment ="PipeSegment"
    #        #self.projDatabase = r"C:\G2\UnitedBrine\Anomaly Comparison\Freeport\PODS_ili.gdb"
    #        #self.projDataSet="Transmission"
    #        #name_1 = self.structure_segment
    #        #path_1 = os.path.join(self.projDatabase,self.projDataSet, self.structure_segment)
    #        #routeIdentifierField_1 = "RouteEventID"
    #        #fromMeasureField_1 = "BeginMeasure"
    #        #toMeasureField_1 = "EndMeasure"
    #        #fromMeasureField_2="Measure"
    #        #toMeasureField_2="Measure"
    #        #key_1 = "EventID"

    #        self.structure_segment = os.path.basename(parameters[11].valueAsText)
    #        self.projDatabase = r"C:\G2\UnitedBrine\Anomaly Comparison\Freeport\PODS_ili.gdb"
    #        self.projDataSet="Transmission"
    #        name_1 = self.structure_segment
    #        path_1 = parameters[11].valueAsText
    #        routeIdentifierField_1 = parameters[13].valueAsText
    #        fromMeasureField_1 = parameters[14].valueAsText
    #        toMeasureField_1 = parameters[15].valueAsText
    #        fromMeasureField_2="Measure"
    #        toMeasureField_2="Measure"
    #        key_1 = parameters[13].valueAsText


    #        # Build JSON for segmentor!!
    #        segmentor_json = list()
    #        segmentor_json_1 = dict()
    #        segmentor_json_1["name"] = name_1
    #        segmentor_json_1["path"] = path_1
    #        segmentor_json_1["routeIdentifierField"] = routeIdentifierField_1
    #        segmentor_json_1["fromMeasureField"] = fromMeasureField_1
    #        segmentor_json_1["toMeasureField"] = toMeasureField_1
    #        segmentor_json_1["primaryKeyField"] = key_1
    #        # segmentor_json = [segmentor_json_1]
    #        segmentor_json.append(segmentor_json_1)

    #        if ili_layer:
    #            name_2 = ili_layer
    #            path_2 = parameters[0].valueAsText
    #            segmentor_json_2 = dict()
    #            segmentor_json_2["name"] = name_2
    #            segmentor_json_2["path"] = path_2
    #            segmentor_json_2["routeIdentifierField"] = routeIdentifierField_1
    #            segmentor_json_2["fromMeasureField"] = fromMeasureField_2
    #            segmentor_json_2["toMeasureField"] = toMeasureField_2
    #            segmentor_json_2["primaryKeyField"] = key_1
    #            segmentor_json.append(segmentor_json_2)

    #        if maop_layer:
    #            name_3 = maop_layer
    #            path_3 =  parameters[12].valueAsText
    #            segmentor_json_3 = dict()
    #            segmentor_json_3["name"] = name_3
    #            segmentor_json_3["path"] = path_3
    #            segmentor_json_3["routeIdentifierField"] = routeIdentifierField_1
    #            segmentor_json_3["fromMeasureField"] = fromMeasureField_1
    #            segmentor_json_3["toMeasureField"] = toMeasureField_1
    #            segmentor_json_3["primaryKeyField"] = key_1
    #            segmentor_json.append(segmentor_json_3)

    #        segmentor_json_string = json.dumps(segmentor_json)
    #        return segmentor_json_string
    #    except Exception as e:
    #        tb = sys.exc_info()[2]
    #        inlineinspection.AddError("An error occurred on line %i" % tb.tb_lineno)
    #        inlineinspection.AddError(str(e))
    #        inlineinspection.AddError("Issue in json file creation .\n{}".format(arcpy.GetMessages(2)))
    #        return False
    #def build_segmentor_table(self,parameters):
    #    try:

    #        #Create intermediate folder and gdb to store the segmentor related tables 
    #        self.output_dir=r"C:\G2\UnitedBrine\Test\TestOutputdatabase.gdb"
    #        self.ILI_TEMP_FOLDER = "ILI_TEMP"
    #        self.ILI_TEMP_GDB = "ILI_TEMP_GDB.gdb"
    #        tempoutput_workspace = arcpy.env.scratchFolder if arcpy.Exists(arcpy.env.scratchFolder) and arcpy.env.scratchFolder is not None else self.output_dir
    #        tempoutput_dir = os.path.join(tempoutput_workspace, self.ILI_TEMP_FOLDER )
    #        tempoutput_gdb = self.ILI_TEMP_GDB 
    #        self.tempoutputgdb_path = os.path.join(tempoutput_dir, tempoutput_gdb)
    #        inlineinspection.AddMessage("Temp gdb path {}".format(self.tempoutputgdb_path))
        
    #        # Create temp gbd for intermediate process
    #        self.createtempgdb(tempoutput_dir, tempoutput_gdb)

    #        #self.input_centerline =r"C:\G2\UnitedBrine\Anomaly Comparison\Freeport\PODS_ili.gdb\Transmission\StationSeries"
               
    #        #ili_layer ="ILIData"
    #        #maop_layer = "MAOPRating"
    #        #CENTERLINE_UNIQUE_ID ="EventID"
    #        #CENTERLINE_BEGIN_MEASURE ="BeginMeasure"
    #        #CENTERLINE_END_MEASURE ="EndMeasure"


    #        ili_layer =os.path.basename(parameters[0].valueAsText)
    #        pipesegment_layer=os.path.basename(parameters[11].valueAsText)
    #        self.input_centerline =parameters[10].valueAsText
    #        maop_layer = os.path.basename(parameters[12].valueAsText)
    #        CENTERLINE_UNIQUE_ID =parameters[13].valueAsText
    #        CENTERLINE_BEGIN_MEASURE =parameters[14].valueAsText
    #        CENTERLINE_END_MEASURE = parameters[15].valueAsText
    #        diameter_field = parameters[16].valueAsText
    #        thickness_field = parameters[17].valueAsText
    #        syms_field = parameters[18].valueAsText
    #        length_field = parameters[2].valueAsText
    #        MaxDepthMeasured_field = parameters[3].valueAsText
    #        MaxDiameter_field = parameters[4].valueAsText
    #        MeasuredWallThickness_field = parameters[5].valueAsText
    #        maop_field = parameters[19].valueAsText

    #        ili_segmentor = Segmentor()
    #        route_layer = FuncParam(self.input_centerline)  #FuncParam(os.path.join(self.projDatabase.path, HCAOperation.CENTERLINE_TABLE))
    #        route_id = FuncParam(CENTERLINE_UNIQUE_ID)
    #        begin_meas = FuncParam(CENTERLINE_BEGIN_MEASURE)
    #        end_meas = FuncParam(CENTERLINE_END_MEASURE)
                
    #        json_str = self.build_json_for_segmentor(ili_layer,maop_layer,parameters)
    #        inlineinspection.AddMessage("JSON build for segmentor is done")

    #        segmentor_json = FuncParam(json_str)

    #        segmentor_out = FuncParam(self.tempoutputgdb_path + "\\ILISegmentCount_Segmentor")
    #        if arcpy.Exists(segmentor_out.valueAsText):
    #            arcpy.Delete_management(segmentor_out.valueAsText)
    #        segmentor_error = FuncParam(self.tempoutputgdb_path + "\\ILISegmentCount_Segmentor_E")
    #        if arcpy.Exists(segmentor_error.valueAsText):
    #            arcpy.Delete_management(segmentor_error.valueAsText)
    #        seg_parameters = [route_layer, route_id, begin_meas, end_meas, segmentor_json, segmentor_out, segmentor_error]
    #        ili_segmentor.execute(seg_parameters, None)
    #        inlineinspection.AddMessage("JSON build for segmentor is done")

    #        # Attributor

    #        # Delete record from route
    #        where_clause = "layer_Name='route'"  #----
    #        with arcpy.da.UpdateCursor(segmentor_out.valueAsText, '*', where_clause) as cursor:
    #            for row in cursor:
    #                cursor.deleteRow()

    #        # Run attributor
    #        hca_attributor = Attributer()
    #        attributor_in = segmentor_out

    #        # Build json string
    #        attr_list=[{"name":pipesegment_layer,"columns":[{"inputColumnName":"RouteEventID","outputColumnName":"RouteEventID"},
    #                                                    {"inputColumnName":"EventID","outputColumnName":"SegEventID"},
    #                                                               {"inputColumnName": diameter_field,"outputColumnName":diameter_field},
    #                                                               {"inputColumnName": thickness_field,"outputColumnName":thickness_field},
    #                                                               {"inputColumnName": syms_field,"outputColumnName":syms_field}
    #                                                               ]},
    #                   {"name":ili_layer,"columns":[{"inputColumnName":"RouteEventID","outputColumnName":"RouteEventID"},
    #                                                    {"inputColumnName":"EventID","outputColumnName":"ILIEventID"},
    #                                                               {"inputColumnName":length_field,"outputColumnName":length_field},
    #                                                               {"inputColumnName":MaxDepthMeasured_field,"outputColumnName":MaxDepthMeasured_field}
    #                                                               ]},
    #                    {"name":maop_layer,"columns":[{"inputColumnName":"RouteEventID","outputColumnName":"RouteEventID"},
    #                                                    {"inputColumnName":"EventID","outputColumnName":"MAOPEventID"},
    #                                                               {"inputColumnName":maop_field,"outputColumnName":maop_field}
                                                                 
    #                                                               ]}
    #                    ]        

    #        json_str = json.dumps(attr_list)
    #        attributor_json = FuncParam(json_str)
        
    #        attributor_out = FuncParam(self.tempoutputgdb_path + "\\ILISegmentCount_Attributor")
    #        if arcpy.Exists(attributor_out.valueAsText):
    #            arcpy.Delete_management(attributor_out.valueAsText)
    #        attributor_error = FuncParam(self.tempoutputgdb_path + "\\ILISegmentCount_Attributor_E")
    #        if arcpy.Exists(attributor_error.valueAsText):
    #            arcpy.Delete_management(attributor_error.valueAsText)
    #        parameters = [attributor_in, attributor_json, attributor_out, attributor_error]
    #        hca_attributor.execute(parameters, None)
    #        inlineinspection.AddMessage("Attributor execution done")
                
    #        # run statistitator
    #        hca_statistitator = Statistitater()
    #        statistitator_in = attributor_out
    #        group_by = FuncParam("SEGMENT_ID")
    #        stat_list = [{"name":"RouteEventID","calculation":"calculation.First(default=None,input='row.RouteEventID',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"String","length":50}},
    #                   {"name":"FROM_MEASURE","calculation":"calculation.First(default=None,input='row.FROM_MEASURE',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double","precision":10}},
    #                   {"name":"TO_MEASURE","calculation":"calculation.First(default=None,input='row.TO_MEASURE',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double","precision":10}},
    #                   {"name":"NominalDiameterGCL","calculation":"calculation.First(default=None,input='row."+diameter_field+"',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double"}},
    #                   {"name":"NominalWallThicknessGCL","calculation":"calculation.First(default=None,input='row."+thickness_field+"',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double"}},
    #                   {"name":"SMYSGCL","calculation":"calculation.First(default=None,input='row."+syms_field+"',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double"}},
    #                   {"name":"Length","calculation":"calculation.First(default=None,input='row."+length_field+"',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double"}},
    #                   {"name":"MaxDepthMeasured","calculation":"calculation.First(default=None,input='row."+MaxDepthMeasured_field+"',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double"}},
    #                   {"name":"MAOPRating","calculation":"calculation.First(default=None,input='row."+maop_field+"',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Double"}},
    #                   {"name":"ILIEventID","calculation":"calculation.First(default=None,input='row.ILIEventID',orderby='SEGMENT_ID',data=data,newData=newData)","dataType":{"type":"Guid"}}                   
                   
    #                   ]
        
    #        json_str = json.dumps(stat_list)
    #        statistitator_json = FuncParam(json_str)
    #        statistitator_out = FuncParam(self.tempoutputgdb_path + "\\ILISegmentCount_Statistitater2")
    #        if arcpy.Exists(statistitator_out.valueAsText):
    #            arcpy.Delete_management(statistitator_out.valueAsText)
    #        statistitator_error = FuncParam(self.tempoutputgdb_path  + "\\ILISegmentCount_Statistitater_E")
    #        if arcpy.Exists(statistitator_error.valueAsText):
    #            arcpy.Delete_management(statistitator_error.valueAsText)
    #        parameters = [statistitator_in, group_by, statistitator_json, statistitator_out, statistitator_error]
    #        hca_statistitator.execute(parameters, None)
    #        inlineinspection.AddMessage("Statistitator process is done")

    #    except Exception as e:
    #        tb = sys.exc_info()[2]
    #        inlineinspection.AddError("An error occurred on line %i" % tb.tb_lineno)
    #        inlineinspection.AddError(str(e))
    #        inlineinspection.AddError("Issue in dynamic segmention process .\n{}".format(arcpy.GetMessages(2)))
    #        return False

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
        
            diameter_field=parameters[12].valueAsText
            thickness_field = parameters[5].valueAsText  #** need to remove 
            syms_field = parameters[13].valueAsText
            maop_field = parameters[14].valueAsText
            
            
            #Create temp gdb to process and store intermediate data           
            #self.output_dir=r"C:\G2\UnitedBrine\Test\TestOutputdatabase.gdb"
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

            #arcpy.analysis.SpatialJoin(ili_layer, pipesegment_layer, spatialjoin1, "JOIN_ONE_TO_ONE", "KEEP_ALL", r'EventID "EventID" true true false 38 Guid 0 0,First,#,'+ili_layer+',EventID,-1,-1;'+config.OUTPUT_SYMS_FIELDNAME+' "'+config.OUTPUT_SYMS_FIELDNAME+'" true true false 50 Text 0 0,First,#,'+pipesegment_layer+','+syms_field+',0,50;'+config.OUTPUT_DIAMETER_FIELDNAME+' "'+config.OUTPUT_DIAMETER_FIELDNAME+'" true true false 8 Double 0 0,First,#,'+pipesegment_layer+','+diameter_field+',-1,-1;'+config.OUTPUT_THICKNESS_FIELDNAME+' "'+config.OUTPUT_THICKNESS_FIELDNAME+'" true true false 8 Double 0 0,First,#,'+pipesegment_layer+','+thickness_field+',-1,-1', "INTERSECT", None, '')
            inlineinspection.AddMessage("spatial join1 feature {} {} {}".format(spatialjoin1,ili_layer,pipesegment_layer))
            #arcpy.SpatialJoin_analysis(ili_layer, pipesegment_layer, spatialjoin1, "JOIN_ONE_TO_ONE", "KEEP_ALL", r'EventID "EventID" true true false 38 Guid 0 0,First,#,'+ili_layer+',EventID,-1,-1;'+config.OUTPUT_SYMS_FIELDNAME+' "'+config.OUTPUT_SYMS_FIELDNAME+'" true true false 50 Text 0 0,First,#,'+pipesegment_layer+','+syms_field+',0,50;'+config.OUTPUT_DIAMETER_FIELDNAME+' "'+config.OUTPUT_DIAMETER_FIELDNAME+'" true true false 8 Double 0 0,First,#,'+pipesegment_layer+','+diameter_field+',-1,-1;'+config.OUTPUT_THICKNESS_FIELDNAME+' "'+config.OUTPUT_THICKNESS_FIELDNAME+'" true true false 8 Double 0 0,First,#,'+pipesegment_layer+','+thickness_field+',-1,-1', "INTERSECT", None, '')
            arcpy.SpatialJoin_analysis(ili_layer, pipesegment_layer, spatialjoin1, "JOIN_ONE_TO_ONE", "KEEP_ALL", r'EventID "EventID" true true false 38 Guid 0 0,First,#,'+ili_layer+',EventID,-1,-1;'+config.OUTPUT_SYMS_FIELDNAME+' "'+config.OUTPUT_SYMS_FIELDNAME+'" true true false 50 Text 0 0,First,#,'+pipesegment_layer+','+syms_field+',0,50;'+config.OUTPUT_DIAMETER_FIELDNAME+' "'+config.OUTPUT_DIAMETER_FIELDNAME+'" true true false 8 Double 0 0,First,#,'+pipesegment_layer+','+diameter_field+',-1,-1', "INTERSECT", None, '')
            

            inlineinspection.AddMessage("Spatial Join is performed on Pipe Segment")
            #arcpy.analysis.SpatialJoin(spatialjoin1, maop_layer, spatialjoin2, "JOIN_ONE_TO_ONE", "KEEP_ALL", r'EventID "EventID" true true false 38 Guid 0 0,First,#,'+spatialjoin1+',EventID,-1,-1;'+config.OUTPUT_SYMS_FIELDNAME+' "'+config.OUTPUT_SYMS_FIELDNAME+'" true true false 50 Text 0 0,First,#,'+spatialjoin1+','+config.OUTPUT_SYMS_FIELDNAME+',0,50;'+config.OUTPUT_DIAMETER_FIELDNAME+' "'+config.OUTPUT_DIAMETER_FIELDNAME+'" true true false 8 Double 0 0,First,#,'+spatialjoin1+','+config.OUTPUT_DIAMETER_FIELDNAME+',-1,-1;'+config.OUTPUT_THICKNESS_FIELDNAME+' "'+config.OUTPUT_THICKNESS_FIELDNAME+'" true true false 8 Double 0 0,First,#,'+spatialjoin1+','+config.OUTPUT_THICKNESS_FIELDNAME+',-1,-1;'+config.OUTPUT_MAOP_FIELDNAME+' "'+config.OUTPUT_MAOP_FIELDNAME+'" true true false 4 Long 0 0,First,#,'+maop_layer+','+maop_field+',-1,-1', "INTERSECT", None, '')
            inlineinspection.AddMessage(" spatial join2 {}".format(spatialjoin2))
           
            arcpy.SpatialJoin_analysis(spatialjoin1, maop_layer, spatialjoin2, "JOIN_ONE_TO_ONE", "KEEP_ALL", r'EventID "EventID" true true false 38 Guid 0 0,First,#,'+spatialjoin1+',EventID,-1,-1;'+config.OUTPUT_SYMS_FIELDNAME+' "'+config.OUTPUT_SYMS_FIELDNAME+'" true true false 50 Text 0 0,First,#,'+spatialjoin1+','+config.OUTPUT_SYMS_FIELDNAME+',0,50;'+config.OUTPUT_DIAMETER_FIELDNAME+' "'+config.OUTPUT_DIAMETER_FIELDNAME+'" true true false 8 Double 0 0,First,#,'+spatialjoin1+','+config.OUTPUT_DIAMETER_FIELDNAME+',-1,-1;'+config.OUTPUT_MAOP_FIELDNAME+' "'+config.OUTPUT_MAOP_FIELDNAME+'" true true false 4 Long 0 0,First,#,'+maop_layer+','+maop_field+',-1,-1', "INTERSECT", None, '')
            inlineinspection.AddMessage("Spatial Join is performed on MAOP")

            arcpy.management.AddFields(ili_layer, config.OUTPUT_DIAMETER_FIELDNAME+" LONG # # # #;"+config.OUTPUT_SYMS_FIELDNAME+" LONG # # # #;"+config.OUTPUT_MAOP_FIELDNAME+" LONG # # # #")
            inlineinspection.AddMessage("Added temp fields")
          
            #Add join with ILI Layer          
            arcpy.AddJoin_management(ili_layer, "EventID", spatialjoin2, "EventID", "KEEP_ALL")            
            inlineinspection.AddMessage("Join is performed on ILI Data")

            arcpy.management.CalculateField(ili_layer, config.OUTPUT_DIAMETER_FIELDNAME, "!ILIData_SJ2."+config.OUTPUT_DIAMETER_FIELDNAME+"!", "PYTHON3", '', "TEXT")
            arcpy.management.CalculateField(ili_layer, config.OUTPUT_SYMS_FIELDNAME , "!ILIData_SJ2."+config.OUTPUT_SYMS_FIELDNAME+"!", "PYTHON3", '', "TEXT")
            arcpy.management.CalculateField(ili_layer, config.OUTPUT_MAOP_FIELDNAME, "!ILIData_SJ2."+config.OUTPUT_MAOP_FIELDNAME+"!", "PYTHON3", '', "TEXT")
            inlineinspection.AddMessage("Calculate temp fields")

            arcpy.management.RemoveJoin(ili_layer, "ILIData_SJ2")
            inlineinspection.AddMessage("Existing Join is removed from ILI Data")

            calulatepressure= CalculateILIPressures()
            calulatepressure.fieldscaliculation(parameters)
            inlineinspection.AddMessage("Caliculation is performed")            

            arcpy.management.DeleteField(ili_layer, ""+config.OUTPUT_DIAMETER_FIELDNAME+";"+config.OUTPUT_SYMS_FIELDNAME+";"+config.OUTPUT_SYMS_FIELDNAME+"")
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
        

    def updatedomainvalues(self, inFeatures, fieldName, expression, code_block, field_type):
        try:
            # Set the workspace (to avoid having to type in the full path to the data every time)

            inlineinspection.AddMessage("Calculate Pressure process started for {}".format(fieldName))
            # Process: Add valid material types to the domain
            # use a for loop to cycle through all the domain codes in the dictionary
            arcpy.CalculateField_management(inFeatures, fieldName, expression, 'Python 3', code_block, field_type)
            inlineinspection.AddMessage("  Pressures are calculated, process completed for {}".format(fieldName))

        except Exception as e:
            # If an error occurred, print line number and error message
            tb = sys.exc_info()[2]
            inlineinspection.AddError("   Error in domain creation process for {}".format(domain))
            inlineinspection.AddError("   An error occurred on line %i" % tb.tb_lineno)
            inlineinspection.AddError(str(e))

    def run(self,parameters):
        try:
            # Set the workspace (to avoid having to type in the full path to the data every time)
            #inFeatures = arcpy.GetParameterAsText(0)
            inFeatures=parameters[0].valueAsText
            lengthField=parameters[2].valueAsText
            maxDepthMeasure=parameters[3].valueAsText
            maxDiameter=parameters[4].valueAsText
            measuredWallthickness=parameters[5].valueAsText
            pipeSmys=parameters[6].valueAsText
            pipeMAOPField=parameters[7].valueAsText
            areaOfMetalLoss=parameters[15].valueAsText
            modAreaOfMetalLoss=parameters[16].valueAsText
            flowStress=parameters[17].valueAsText
            modFlowStress=parameters[18].valueAsText
            foliasFactor=parameters[19].valueAsText
            modFoliasFactor=parameters[20].valueAsText
            pipeBurstPressure=parameters[21].valueAsText
            modPipeBurstPressure=parameters[22].valueAsText
            calculatedPressure=parameters[23].valueAsText
            referencePressure=parameters[24].valueAsText
            safetyFactor=parameters[25].valueAsText
            pressureReferencedRatio=parameters[26].valueAsText
            estimatedRepairFactor=parameters[27].valueAsText
            rupturePressureRatio=parameters[28].valueAsText

            if(parameters[1].value==config.ILI_PIPE_PARAMETER_TYPE[1]):
                pipeSmysValOrField =parameters[8].valueAsText
                pipeMaopValOrField =parameters[9].valueAsText

            elif(parameters[1].value==config.ILI_PIPE_PARAMETER_TYPE[2]):

                #maxDiameter=parameters[12].valueAsText
                #measuredWallthickness=parameters[13].valueAsText                
                #pipeSmys=parameters[14].valueAsText
                #pipeMAOPField=parameters[15].valueAsText

                maxDiameter=config.OUTPUT_DIAMETER_FIELDNAME
                measuredWallthickness=config.OUTPUT_THICKNESS_FIELDNAME          
                pipeSmys=config.OUTPUT_SYMS_FIELDNAME
                pipeMAOPField=config.OUTPUT_MAOP_FIELDNAME

                pipeSmysValOrField ="!"+pipeSmys+"!"                 
                pipeMaopValOrField ="!"+pipeMAOPField+"!"
                
            else:
                pipeSmys=parameters[6].valueAsText
                pipeSmysValOrField ="!"+pipeSmys+"!"
                pipeMAOPField=parameters[7].valueAsText
                pipeMaopValOrField ="!"+pipeMAOPField+"!"

            inlineinspection.AddMessage("Input ILI Feature class {}".format(inFeatures))

            #calculate the first pressure field 1
            fieldName = areaOfMetalLoss
            expression = "(2/3)*(!"+maxDepthMeasure+"!)*(!"+lengthField+"!)"
            code_block = ""
            field_type = 'DOUBLE'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)  
            # calculate the first pressure field 2
            fieldName = modAreaOfMetalLoss
            expression = "(.85)*(!"+maxDepthMeasure+"!)*(!"+lengthField+"!)"
            code_block =""
            field_type = 'DOUBLE'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            # # calculate the first pressure field 3
            fieldName = flowStress
            expression = "(1.1)*("+pipeSmysValOrField+")"
            code_block = ""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)
            
            # # calculate the first pressure field 4
            fieldName = modFlowStress
            expression = "("+pipeSmysValOrField+"+10000)"
            code_block = ""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            # # calculate the first pressure field 5
            fieldName = foliasFactor
            expression = "folias(!"+lengthField+"!, !"+maxDiameter+"!,!"+measuredWallthickness+"!)"
            code_block = """def folias(length, diameter, thickness):
                                if length <(20*diameter*thickness)**(.5):
                                    return math.sqrt((1 + 0.8 * (length**2/(diameter*thickness))))
                                else: 
                                    return 0"""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = modFoliasFactor
            expression = "modfolias(!"+lengthField+"!, !"+maxDiameter+"!,!"+measuredWallthickness+"!)"
            code_block = """def modfolias(length, diameter, thickness):
                                if length**2/(diameter*thickness)<=50:
                                    return math.sqrt((1+(0.6275*(length**2/(diameter*thickness)))-(0.003375*(((length**2)/(diameter*thickness))**2))))
                                elif length**2/(diameter*thickness)>50:
                                    return ((.032)*((length**2)/(diameter*thickness)))+3.3"""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)


            fieldName = pipeBurstPressure
            expression = "(!"+flowStress+"!)*((1-(!"+areaOfMetalLoss+"!/(!"+measuredWallthickness+"!*!"+lengthField+"!)))/(1-(!"+areaOfMetalLoss+"!/(!"+measuredWallthickness+"!*!"+lengthField+"!*!"+foliasFactor+"!))))*((2*!"+measuredWallthickness+"!)/!"+maxDiameter+"!)"
            code_block = ""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)


            fieldName = modPipeBurstPressure
            expression = "(!"+modFlowStress+"!)*((1-(!"+modAreaOfMetalLoss+"!/(!"+measuredWallthickness+"!*!"+lengthField+"!)))/(1-(!"+modAreaOfMetalLoss+"!/(!"+measuredWallthickness+"!*!"+lengthField+"!*(!"+modFlowStress+"!)))))*((2*!"+measuredWallthickness+"!)/!"+maxDiameter+"!)"
            code_block = ""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = calculatedPressure
            expression =  "(!"+pipeBurstPressure+"!*("+pipeMaopValOrField+")/("+pipeSmysValOrField+"))"
            code_block = ""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = referencePressure
            expression = "("+pipeMaopValOrField+")"
            code_block = ""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = safetyFactor
            expression = "(!"+pipeBurstPressure+"!/"+pipeMaopValOrField+")"
            code_block =""
            field_type = 'DOUBLE'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = pressureReferencedRatio
            expression = "(!"+calculatedPressure+"!/!"+referencePressure+"!)"
            code_block =""
            field_type = 'DOUBLE'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = estimatedRepairFactor
            expression = "(("+pipeMaopValOrField+")/!"+calculatedPressure+"!)"
            code_block =""
            field_type = 'DOUBLE'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = rupturePressureRatio
            expression = "!"+pipeBurstPressure+"!/("+pipeSmysValOrField+")"
            code_block =""
            field_type = 'DOUBLE'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)
                       
        except Exception as e:
            # If an error occurred, print line number and error message
            tb = sys.exc_info()[2]
            arcpy.AddError("An error occurred on line %i" % tb.tb_lineno)
            arcpy.AddError(str(e))
    
    '''Add The output fields if not exist'''
    def addMissingField(self,fc,outFields):
        if(fc):
            flds = []            
            flds += [f.name.upper() for f in arcpy.ListFields (fc)]
            #inlineinspection.AddMessage("FC Fields list {} {} ".format(flds,outFields))

            #f1=[]
            #for f in flds:
            #    x=f.split('.')
            #    if len(x)>1:
            #        x1=x[1]
            #        f1.append(x1)
            #    else:
            #        f1.append(f)

            #inlineinspection.AddMessage("FC Fields list {} ".format(f1))
            for outField in outFields:
                if not outField.upper() in flds: 
                    # Execute AddField for new fields
                    arcpy.AddField_management(fc, outField, "LONG", 9,
                                              field_alias=outField, field_is_nullable="NULLABLE")
                    inlineinspection.AddMessage("{} field added".format(outField))
                   

    def fieldscaliculation(self,parameters):
        try:
            fields=[]            
            #inFeatures = arcpy.GetParameterAsText(0)
            inFeatures=parameters[0].valueAsText
            lengthField=parameters[2].valueAsText
            maxDepthMeasure=parameters[3].valueAsText
            maxDiameter=parameters[4].valueAsText
            measuredWallthickness=parameters[5].valueAsText
            pipeSmys=parameters[6].valueAsText
            pipeMAOPField=parameters[7].valueAsText
            fAreaOfMetalLoss=parameters[15].valueAsText
            fModAreaOfMetalLoss=parameters[16].valueAsText
            fFlowStress=parameters[17].valueAsText
            fModFlowStress=parameters[18].valueAsText
            fFoliasFactor=parameters[19].valueAsText
            fModFoliasFactor=parameters[20].valueAsText
            fPipeBurstPressure=parameters[21].valueAsText
            fModPipeBurstPressure=parameters[22].valueAsText
            fCalculatedPressure=parameters[23].valueAsText
            fReferencePressure=parameters[24].valueAsText
            fSafetyFactor=parameters[25].valueAsText
            fPressureReferencedRatio=parameters[26].valueAsText
            fEstimatedRepairFactor=parameters[27].valueAsText
            fRupturePressureRatio=parameters[28].valueAsText
            eventidField ="EVENTID"

            outputfields=[fAreaOfMetalLoss,fModAreaOfMetalLoss,fFlowStress,fModFlowStress,fFoliasFactor,fModFoliasFactor,fPipeBurstPressure,
             fModPipeBurstPressure,fCalculatedPressure,fReferencePressure,fSafetyFactor,fPressureReferencedRatio,fEstimatedRepairFactor,
             fRupturePressureRatio]           

            #outputfields=[areaOfMetalLoss,lengthField]  

            if(parameters[1].value==config.ILI_PIPE_PARAMETER_TYPE[1]):
                pipeSmysValOrField =parameters[8].valueAsText
                pipeMaopValOrField =parameters[9].valueAsText
                #*** Need to modify this filed as properly
                pipeSmys=lengthField
                pipeMAOPField=lengthField

            elif(parameters[1].value==config.ILI_PIPE_PARAMETER_TYPE[2]):
                #maxDiameter=parameters[12].valueAsText
                #measuredWallthickness=parameters[13].valueAsText                
                #pipeSmys=parameters[14].valueAsText
                #pipeMAOPField=parameters[15].valueAsText         
                
                maxDiameter=config.OUTPUT_DIAMETER_FIELDNAME                 
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
                        row[7]=areaOfMetalLoss
                    else:                        
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Area of Metal Loss is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1             
                    # calculate Mod Area Of Metal Loss              
                    if(rlength and rmaxDepthMeasure):                        
                        modAreaOfMetalLoss = (.85)*(rmaxDepthMeasure)*(rlength)
                        row[8]=modAreaOfMetalLoss
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Mod Area of Metal Loss is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1                        
                    # calculate Flow Stress
                    if(rpipeSmys):                        
                        flowStress = (1.1)*rpipeSmys
                        row[9]=flowStress
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Flow Stress is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculate mod Flow Stress
                    if(rpipeSmys):                        
                        modFlowStress = (rpipeSmys+10000)
                        row[10]=modFlowStress
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Mod Flow Stress is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculate foliasFactor
                    if(rlength and rmaxDiameter and rmeasuredWallthickness):                        
                        foliasFactor=0
                        if rlength <(20*rmaxDiameter*rmeasuredWallthickness)**(.5):
                            foliasFactor= math.sqrt((1 + 0.8 * (rlength**2/(rmaxDiameter*rmeasuredWallthickness))))                      
                        
                        row[11]=foliasFactor
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
                        
                        row[12]=modFoliasFactor
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Mod Folias Factor is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculate pipe Burst Pressure
                    if(flowStress and areaOfMetalLoss and foliasFactor and rlength and rmaxDiameter and rmeasuredWallthickness):                        
                        pipeBurstPressure = flowStress*((1-(areaOfMetalLoss/(rmeasuredWallthickness*rlength)))/(1-(areaOfMetalLoss/(rmeasuredWallthickness*rlength*foliasFactor))))*((2*rmeasuredWallthickness)/rmaxDiameter)
                        
                        row[13]=pipeBurstPressure
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Pipe Burst Pressure is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculate Mod Pipe Burst Pressure
                    if(modFlowStress and modAreaOfMetalLoss and modFoliasFactor and rlength and rmaxDiameter and rmeasuredWallthickness):                        
                        modPipeBurstPressure = (modFlowStress)*((1-(modAreaOfMetalLoss/(rmeasuredWallthickness*rlength)))/(1-(modAreaOfMetalLoss/(rmeasuredWallthickness*rlength*(modFoliasFactor)))))*((2*rmeasuredWallthickness)/rmaxDiameter)
                        #*** Check the formula
                        row[14]=modPipeBurstPressure
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Mod Pipe Burst Pressure is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculated Pressure
                    if(pipeBurstPressure and rpipeMAOP and rpipeSmys):                        
                        calculatedPressure = (pipeBurstPressure*(rpipeMAOP)/(rpipeSmys))
                        row[15]=calculatedPressure
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} calculated Pressure is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculated Reference Pressure
                    if(rpipeMAOP):
                        referencePressure = rpipeMAOP
                        row[16]=referencePressure
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Reference Pressure is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculated Safety Factor
                    if(rpipeMAOP and pipeBurstPressure):
                        safetyFactor = (pipeBurstPressure/rpipeMAOP)
                        row[17]=safetyFactor
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Safety Factor is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculated Pressure Referenced Ratio
                    if(calculatedPressure and referencePressure):
                        pressureReferencedRatio = (calculatedPressure/referencePressure)
                        row[18]=pressureReferencedRatio
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Pressure Referenced Ratio is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculated Estimated Repair Factor
                    if(rpipeMAOP and calculatedPressure):
                        estimatedRepairFactor = (rpipeMAOP/calculatedPressure)
                        row[19]=estimatedRepairFactor
                    else:
                        inlineinspection._inlineinspection_log._addWarning_FILE("{} Estimated Repair Factor is not caliculated as required fileds are null".format(reventid))
                        warningCounter +=1
                    # calculated Rupture Pressure Ratio
                    if(rpipeSmys and pipeBurstPressure):
                        rupturePressureRatio = (pipeBurstPressure/rpipeSmys)
                        row[20]=rupturePressureRatio
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

   