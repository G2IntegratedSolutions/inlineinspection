
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

        """
                parameters[0]->   in_workspace,
                parameters[1]->   in_nhd_intersections_features              
                """
        # Input Pipe Features
        in_pipe_parameter_type = arcpy.Parameter(displayName="Input Pipe Parameter Source",
            name="in_pipe_parameter_type",
            datatype="GPString",
            parameterType="optional",
            direction="Input")
        in_pipe_parameter_type.filter.list = config.ILI_PIPE_PARAMETER_TYPE
        in_pipe_parameter_type.value = config.ILI_PIPE_PARAMETER_TYPE[0]

        # Input ILI point featuere         
        in_ili_features = arcpy.Parameter(displayName="Input Inline Inspection Point Features",
            name="in_ili_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        in_ili_features.filter.list = ["Point"]

         #Catigory 1 parameters 'Length', 'MaxDepthMeasured' ,'MaxDiameter' ,'MeasuredWallThickness' ,'PipeSmys' ,'PipeMAOP', 'AreaOfMetalLoss']
        in_pc_length_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Anomaly Length Field", name="in_pc_length_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_pc_length_field.parameterDependencies = [in_ili_features.name]
        in_pc_length_field.value = config.ILI_PC_REQ_FIELDS[0]

        in_pc_MaxDepthMeasured_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Max Depth Measured Field", name="in_pc_MaxDepthMeasured_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_pc_MaxDepthMeasured_field.parameterDependencies = [in_ili_features.name]
        in_pc_MaxDepthMeasured_field.value = config.ILI_PC_REQ_FIELDS[1]

        in_pc_MaxDiameter_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Diameter", name="in_pc_MaxDiameter_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_pc_MaxDiameter_field.parameterDependencies = [in_ili_features.name]
        in_pc_MaxDiameter_field.value = config.ILI_PC_REQ_FIELDS[2]

        in_pc_MeasuredWallThickness_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Measured Wall Thickness Field", name="in_pc_MeasuredWallThickness_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_pc_MeasuredWallThickness_field.parameterDependencies = [in_ili_features.name]
        in_pc_MeasuredWallThickness_field.value = config.ILI_PC_REQ_FIELDS[3]

        in_pc_PipeSmys_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Pipe Smys Field", name="in_pc_PipeSmys_field",
            datatype="Field", parameterType="Required", direction="Input")
        #in_pc_PipeSmys_field.parameterDependencies = [in_ili_features.name]
        in_pc_PipeSmys_field.value = config.ILI_PC_REQ_FIELDS[4]

        in_pc_PipeMAOP_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY,
            displayName="Pipe MAOP Field", name="in_pc_PipeMAOP_field",
            datatype="Field", parameterType="Required", direction="Input")
        in_pc_PipeMAOP_field.parameterDependencies = [in_ili_features.name]
        in_pc_PipeMAOP_field.value = config.ILI_PC_REQ_FIELDS[5]
        
        #Catigory 2 parameters 'AreaOfMetalLoss', 'modAreaOfMetalLoss', 'flowStress', etc.]
        
        in_pc_AreaOfMetalLoss_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Area of Metal Loss", name="in_pc_AreaOfMetalLoss_field",
            datatype="GPString", parameterType="optional", direction="Input")
        #in_pc_AreaOfMetalLoss_field.parameterDependencies = [in_ili_features.name]
        #in_pc_AreaOfMetalLoss_field.value = config.ILI_PC_ADDING_FIELDS[0]

        in_pc_modAreaOfMetalLoss_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Modified Area of Metal Loss", name="in_pc_modAreaOfMetalLoss_field",
            datatype="GPString", parameterType="optional", direction="Input")
        #in_pc_modAreaOfMetalLoss_field.parameterDependencies = [in_ili_features.name]
        #in_pc_modAreaOfMetalLoss_field.value = config.ILI_PC_ADDING_FIELDS[1]

        in_pc_flowStress_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Flow Stress", name="in_pc_flowStress_field",
            datatype="GPString", parameterType="optional", direction="Input")
        #in_pc_flowStress_field.parameterDependencies = [in_ili_features.name]
        #in_pc_flowStress_field.value = config.ILI_PC_ADDING_FIELDS[2]

        in_pc_modflowStress_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Modified Flow Stress", name="in_pc_modflowStress_field",
            datatype="GPString", parameterType="Required", direction="Input")
        #in_pc_modflowStress_field.parameterDependencies = [in_ili_features.name]
        #in_pc_modflowStress_field.value = config.ILI_PC_ADDING_FIELDS[3]

        in_pc_foliasFactor_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Folias Factor", name="in_pc_foliasFactor_field",
            datatype="GPString", parameterType="Required", direction="Input")
        #in_pc_foliasFactor_field.parameterDependencies = [in_ili_features.name]
        #in_pc_foliasFactor_field.value = config.ILI_PC_ADDING_FIELDS[4]

        in_pc_modFoliasFactor_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Modified Folias Factor", name="in_pc_modFoliasFactor_field",
            datatype="GPString", parameterType="Required", direction="Input")
        #in_pc_modFoliasFactor_field.parameterDependencies = [in_ili_features.name]
        #in_pc_modFoliasFactor_field.value = config.ILI_PC_ADDING_FIELDS[5]

        in_pc_pipeBurstPressure_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Pipe Burst Pressure", name="in_pc_pipeBurstPressurer_field",
            datatype="GPString", parameterType="Required", direction="Input")
        #in_pc_pipeBurstPressure_field.parameterDependencies = [in_ili_features.name]
        #in_pc_pipeBurstPressure_field.value = config.ILI_PC_ADDING_FIELDS[6]

        in_pc_modPipeBurstPressure_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Modified Pipe Burst Pressure", name="in_pc_modPipeBurstPressure_field",
            datatype="GPString", parameterType="Required", direction="Input")
        #in_pc_modPipeBurstPressure_field.parameterDependencies = [in_ili_features.name]
        #in_pc_modPipeBurstPressure_field.value = config.ILI_PC_ADDING_FIELDS[7]

        in_pc_calculatePressure_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Calculate Pressure", name="in_pc_calculatePressure_field",
            datatype="GPString", parameterType="Required", direction="Input")
        #in_pc_calculatePressure_field.parameterDependencies = [in_ili_features.name]
        #in_pc_calculatePressure_field.value = config.ILI_PC_ADDING_FIELDS[8]

        in_pc_referencePressure_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Reference Pressure Pressure", name="in_pc_referencePressure_field",
            datatype="GPString", parameterType="Required", direction="Input")
        #in_pc_referencePressure_field.parameterDependencies = [in_ili_features.name]
        #in_pc_referencePressure_field.value = config.ILI_PC_ADDING_FIELDS[9]

        in_pc_safetyFactor_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Safety Factor", name="in_pc_safetyFactor_field",
            datatype="GPString", parameterType="Required", direction="Input")
        #in_pc_safetyFactor_field.parameterDependencies = [in_ili_features.name]
        #in_pc_safetyFactor_field.value = config.ILI_PC_ADDING_FIELDS[10]

        in_pc_pressureReferencedRatio_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Pressure ReferencedRatio", name="in_pc_pressureReferencedRatio_field",
            datatype="GPString", parameterType="Required", direction="Input")
        #in_pc_pressureReferencedRatio_field.parameterDependencies = [in_ili_features.name]
        #in_pc_pressureReferencedRatio_field.value = config.ILI_PC_ADDING_FIELDS[11]

        in_pc_estimatedRepairFactor_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Estimated Repair Factor", name="in_pc_estimatedRepairFactor_field",
            datatype="GPString", parameterType="Required", direction="Input")
        #in_pc_estimatedRepairFactor_field.parameterDependencies = [in_ili_features.name]
        #in_pc_estimatedRepairFactor_field.value = config.ILI_PC_ADDING_FIELDS[12]

        in_pc_rupturePressureRatio_field = arcpy.Parameter(category =config.ILI_PC_PARAMETER_CATGRY_2,
            displayName="Rupture Pressure Ratio", name="in_pc_rupturePressureRatio_field",
            datatype="GPString", parameterType="Required", direction="Input")
        #in_pc_rupturePressureRatio_field.parameterDependencies = [in_ili_features.name]
        #in_pc_rupturePressureRatio_field.value = config.ILI_PC_ADDING_FIELDS[13]

               
        parameters = [in_pipe_parameter_type, in_ili_features,in_pc_length_field,in_pc_MaxDepthMeasured_field,in_pc_MaxDiameter_field,in_pc_MeasuredWallThickness_field,
                      in_pc_PipeSmys_field,in_pc_PipeMAOP_field,in_pc_AreaOfMetalLoss_field, in_pc_modAreaOfMetalLoss_field,in_pc_flowStress_field, 
                      in_pc_modflowStress_field,in_pc_foliasFactor_field,in_pc_modFoliasFactor_field, in_pc_pipeBurstPressure_field, in_pc_modPipeBurstPressure_field,
                      in_pc_calculatePressure_field, in_pc_referencePressure_field, in_pc_safetyFactor_field, in_pc_pressureReferencedRatio_field, in_pc_estimatedRepairFactor_field, in_pc_rupturePressureRatio_field]

        return parameters

    def isLicensed(self):  # optional
        return True

        #return LicenseOperation.is_licensed

    def updateParameters(self, parameters):

        # Populate dependent fields from the input feature class      
        if(parameters[0].value):
            if parameters[0].value == config.ILI_PIPE_PARAMETER_TYPE[1]:
               parameters[6].datatype = "GPString"
               parameters[6].value == config.ILI_MANUAL_PIPE_INFORMATION_VALUE[0]

        if(parameters[1].value):
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

            # Assigning add field  #config.ILI_PC_ADDING_FIELDS[0]
            flds = []
            fc=parameters[1].value
            flds += [f.name for f in arcpy.ListFields (fc)]
            if not parameters[8].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[0]
               self.populate_add_field(flds,parameters,8,comparevalue)

            if not parameters[9].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[1]
               self.populate_add_field(flds,parameters,9,comparevalue)

            if not parameters[10].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[2]
               self.populate_add_field(flds,parameters,10,comparevalue)   

            if not parameters[11].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[3]
               self.populate_add_field(flds,parameters,11,comparevalue) 

            if not parameters[12].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[4]
               self.populate_add_field(flds,parameters,12,comparevalue) 

            if not parameters[13].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[5]
               self.populate_add_field(flds,parameters,13,comparevalue) 

            if not parameters[14].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[6]
               self.populate_add_field(flds,parameters,14,comparevalue) 

            if not parameters[15].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[7]
               self.populate_add_field(flds,parameters,15,comparevalue) 

            if not parameters[16].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[8]
               self.populate_add_field(flds,parameters,16,comparevalue)

            if not parameters[17].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[9]
               self.populate_add_field(flds,parameters,17,comparevalue) 

            if not parameters[18].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[10]
               self.populate_add_field(flds,parameters,18,comparevalue) 

            if not parameters[19].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[11]
               self.populate_add_field(flds,parameters,19,comparevalue) 

            if not parameters[20].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[12]
               self.populate_add_field(flds,parameters,20,comparevalue) 

            if not parameters[21].value:   
               comparevalue= config.ILI_PC_ADDING_FIELDS[13]
               self.populate_add_field(flds,parameters,21,comparevalue) 
        else:
            for i in range(1, 21):
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

        return

    def execute(self, parameters, messages):
        inlineinspection.AddMessage("Start Logging.")        
        arcpy.AddMessage("Log file location: " + inlineinspection.GetLogFileLocation())
        inlineinspection.AddMessage("Starting ILI Pressure Calculator process...")

        try:
            # INPUT PARAMETERS for the process           
            #in_workspace = parameters[0].valueAsText
            ili_inputpoint_fc = parameters[1].valueAsText
                       
            if(arcpy.Exists(ili_inputpoint_fc)):                  
                ilicount = int(arcpy.GetCount_management(ili_inputpoint_fc).getOutput(0))  
                inlineinspection.AddMessage("Record count for ILI Pressure Calculator {}".format(ilicount))
                if (ilicount > 0):                     
                    ht_result_flag = False
                    calculateilipressures = CalculateILIPressures()
                    ili_result_flag = calculateilipressures.run(parameters)                 
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
            inFeatures=parameters[1].valueAsText
            legthField=parameters[2].valueAsText
            maxDepthMeasure=parameters[3].valueAsText
            maxDiameter=parameters[4].valueAsText
            measuredWallthickness=parameters[5].valueAsText
            pipeSmys=parameters[6].valueAsText
            pipeMAOPField=parameters[7].valueAsText
            areaOfMetalLoss=parameters[8].valueAsText
            modAreaOfMetalLoss=parameters[9].valueAsText
            flowStress=parameters[10].valueAsText
            modFlowStress=parameters[11].valueAsText
            foliasFactor=parameters[11].valueAsText
            modFoliasFactor=parameters[12].valueAsText
            pipeBurstPressure=parameters[13].valueAsText
            modPipeBurstPressure=parameters[14].valueAsText
            calculatedPressure=parameters[15].valueAsText
            referencePressure=parameters[16].valueAsText
            safetyFactor=parameters[17].valueAsText
            pressureReferencedRatio=parameters[18].valueAsText
            estimatedRepairFactor=parameters[19].valueAsText
            rupturePressureRatio=parameters[20].valueAsText

            inlineinspection.AddMessage("Input ILI Feature class {}".format(inFeatures))

            #calculate the first pressure field 1
            fieldName = areaOfMetalLoss
            expression = "(2/3)*(!"+maxDepthMeasure+"!)*(!"+legthField+"!)"
            code_block = ""
            field_type = 'DOUBLE'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)  
            # calculate the first pressure field 2
            fieldName = modAreaOfMetalLoss
            expression = "(.85)*(!"+maxDepthMeasure+"!)*(!"+legthField+"!)"
            code_block =""
            field_type = 'DOUBLE'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            # # calculate the first pressure field 3
            fieldName = flowStress
            expression = "(1.1)*(!"+pipeSmys+"!)"
            code_block = ""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)
            
            # # calculate the first pressure field 4
            fieldName = modFlowStress
            expression = "(!"+pipeSmys+"!+10000)"
            code_block = ""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            # # calculate the first pressure field 5
            fieldName = foliasFactor
            expression = "folias(!"+legthField+"!, !"+maxDiameter+"!,!"+measuredWallthickness+"!)"
            code_block = """def folias(length, diameter, thickness):
                                if length <(20*diameter*thickness)**(.5):
                                    return math.sqrt((1 + 0.8 * (length**2/(diameter*thickness))))
                                else: 
                                    return 0"""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = modFoliasFactor
            expression = "modfolias(!"+legthField+"!, !"+maxDiameter+"!,!"+measuredWallthickness+"!)"
            code_block = """def modfolias(length, diameter, thickness):
                                if length**2/(diameter*thickness)<=50:
                                    return math.sqrt((1+(0.6275*(length**2/(diameter*thickness)))-(0.003375*(((length**2)/(diameter*thickness))**2))))
                                elif length**2/(diameter*thickness)>50:
                                    return ((.032)*((length**2)/(diameter*thickness)))+3.3"""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)


            fieldName = pipeBurstPressure
            expression = "(!"+flowStress+"!)*((1-(!"+areaOfMetalLoss+"!/(!"+measuredWallthickness+"!*!"+legthField+"!)))/(1-(!"+areaOfMetalLoss+"!/(!"+measuredWallthickness+"!*!"+legthField+"!*!"+foliasFactor+"!))))*((2*!"+measuredWallthickness+"!)/!"+maxDiameter+"!)"
            code_block = ""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)


            fieldName = modPipeBurstPressure
            expression = "(!"+modFlowStress+"!)*((1-(!"+modAreaOfMetalLoss+"!/(!"+measuredWallthickness+"!*!"+legthField+"!)))/(1-(!"+modAreaOfMetalLoss+"!/(!"+measuredWallthickness+"!*!"+legthField+"!*(!"+modFlowStress+"!)))))*((2*!"+measuredWallthickness+"!)/!"+maxDiameter+"!)"
            code_block = ""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = calculatedPressure
            expression =  "(!"+pipeBurstPressure+"!*!"+pipeMAOPField+"!)/(!"+pipeSmys+"!)"
            code_block = ""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = referencePressure
            expression = "!"+pipeMAOPField+"!"
            code_block = ""
            field_type = 'LONG'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = safetyFactor
            expression = "(!"+pipeBurstPressure+"!/!"+pipeMAOPField+"!)"
            code_block =""
            field_type = 'DOUBLE'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = pressureReferencedRatio
            expression = "(!"+calculatedPressure+"!/!"+referencePressure+"!)"
            code_block =""
            field_type = 'DOUBLE'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = estimatedRepairFactor
            expression = "(!"+pipeMAOPField+"!/!"+calculatedPressure+"!)"
            code_block =""
            field_type = 'DOUBLE'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

            fieldName = rupturePressureRatio
            expression = "!"+pipeBurstPressure+"!/!"+pipeSmys+"!"
            code_block =""
            field_type = 'DOUBLE'
            self.updatedomainvalues(inFeatures, fieldName, expression, code_block, field_type)

           
        except Exception as e:
            # If an error occurred, print line number and error message
            tb = sys.exc_info()[2]
            arcpy.AddError("An error occurred on line %i" % tb.tb_lineno)
            arcpy.AddError(str(e))