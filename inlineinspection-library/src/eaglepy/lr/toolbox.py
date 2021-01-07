import arcpy
import eaglepy, eaglepy.da
import eaglepy.DataSource
from eaglepy.lr.segmentation import _BaseSegmentation
import eaglepy.lr.segmentation
import os
import arcpy.da
#from arcpy import env
import json
import eaglepy.lr.segmentation.calculation


def GetMeasureRangeTableFieldList():
    column_list = list()
    column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="ROUTE_ID",
                                                           type="STRING",
                                                           length=50))
    column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="MEAS_RANGE_ID",
                                                           type="STRING",
                                                           length=50))
    column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="SEGMENT_ID",
                                                           type="STRING",
                                                           length=50))
    column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="FEATURE_ID",
                                                           type="STRING",
                                                           length=50))
    column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="LAYER_NAME",
                                                           type="STRING",
                                                           length=50))
    column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="LAYER_PRIMARY_KEY",
                                                           type="STRING",
                                                           length=50))
    column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="FROM_MEASURE",
                                                           type="DOUBLE"))
    column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="TO_MEASURE",
                                                           type="DOUBLE"))
    column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="GAP_INDICATOR",
                                                           type="STRING",
                                                           length=50))
    column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="METADATA",
                                                           type="STRING",
                                                           length=4000))

    return column_list


def GetErrorTableFieldList():
    """Returns a python list object of arcpy.Fields for a standard error table"""

    err_column_list = list()
    err_column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="ERROR_ID",
                                                               type="STRING",
                                                               length=50))
    err_column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="ROUTE_ID",
                                                               type="STRING",
                                                               length=50))
    err_column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="INPUT_LAYER",
                                                               type="STRING",
                                                               length=4000))
    err_column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="INPUT_LAYER_COL_NAME",
                                                               type="STRING",
                                                               length=50))
    err_column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="INPUT_LAYER_ID",
                                                               type="STRING",
                                                               length=50))
    err_column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="ERROR_TYPE",
                                                               type="STRING",
                                                               length=50))
    err_column_list.append(eaglepy.da.ArcpyFieldFromAttributes(name="ERROR_DESCRIPTION",
                                                               type="STRING",
                                                               length=4000))
    return err_column_list


class Segmentor(object):
   def __init__(self):
      """Tool used to dynamically segment"""
      self.label = "Segmentor Tool"
      self.description = "The Segmentor tool is used to perform dynamic segmentation."
      self.category="Linear Referencing"
      self.canRunInBackground = False

   def getParameterInfo(self):

      param0 = arcpy.Parameter(displayName="Route Feature Class",name="routeFeatureClass",datatype="Feature Layer",parameterType="Required",direction="Input")

      param1 = arcpy.Parameter(displayName="Route ID",name="routeID",datatype="Field",parameterType="Required",direction="Input")

      param2 = arcpy.Parameter(displayName="Begin Station",name="beginStation",datatype="Field",parameterType="Required",direction="Input")

      param3 = arcpy.Parameter(displayName="End Station",name="endStation",datatype="Field",parameterType="Required",direction="Input")

      param4 = arcpy.Parameter(displayName="Input Layers",name="inputLayers",datatype=["File","String"],parameterType="Required",direction="Input")

      param5 = arcpy.Parameter(displayName="Measure Range Table",name="measureRangeTable",datatype="Table",parameterType="Required",direction="Output")

      param6 = arcpy.Parameter(displayName="Error Table",name="errorTable",datatype="Table",parameterType="Required",direction="Output")

      param0.filter.list=['Polyline']
      param1.filter.list = ['Short', 'Long', 'Text', 'GUID', 'Double']
      param1.parameterDependencies = [param0.name]

      param2.parameterDependencies=[param0.name]
      param3.parameterDependencies=[param0.name]

      routeIDField=arcpy.Field()
      routeIDField.name="ROUTE_ID"

      measRangeIDField=arcpy.Field()
      measRangeIDField.name="MEAS_RANGE_ID"

      segmentIDField=arcpy.Field()
      segmentIDField.name="SEGMENT_ID"

      featureIDField=arcpy.Field()
      featureIDField.name="FEATURE_ID"

      layerNameField=arcpy.Field()
      layerNameField.name="LAYERNAME"

      metaDataField=arcpy.Field()
      measRangeIDField.name="METADATA"

      fromMeasureField=arcpy.Field()
      fromMeasureField.name="FROM_MEASURE"

      toMeasureField=arcpy.Field()
      toMeasureField.name="TO_MEASURE"

      gapIndicatorField=arcpy.Field()
      gapIndicatorField.name="GAPINDICATOR"

      routeIDErrorField=arcpy.Field()
      routeIDErrorField.name="ROUTE_ID"

      inputLayerField=arcpy.Field()
      inputLayerField.name="INPUT_LAYER"

      inputLayerColNameField=arcpy.Field()
      inputLayerColNameField.name="INPUT_LAYER_COL_NAME"

      inputLayerIDField=arcpy.Field()
      inputLayerIDField.name="INPUT_LAYER_ID"

      errorTypeField=arcpy.Field()
      errorTypeField.name="ERROR_TYPE"

      errorDescriptionField=arcpy.Field()
      errorDescriptionField.name="ERROR_DESCRIPTION"

      param5.schema.additionalFields=[routeIDField]
      param5.schema.additionalFields=[measRangeIDField]
      param5.schema.additionalFields=[segmentIDField]
      param5.schema.additionalFields=[featureIDField]
      param5.schema.additionalFields=[layerNameField]
      param5.schema.additionalFields=[metaDataField]
      param5.schema.additionalFields=[fromMeasureField]
      param5.schema.additionalFields=[toMeasureField]
      param5.schema.additionalFields=[gapIndicatorField]

      param6.schema.additionalFields=[routeIDErrorField]
      param6.schema.additionalFields=[inputLayerField]
      param6.schema.additionalFields=[inputLayerColNameField]
      param6.schema.additionalFields=[inputLayerIDField]
      param6.schema.additionalFields=[errorTypeField]
      param6.schema.additionalFields=[errorDescriptionField]

      param5.schema.fieldsRule="All"
      param6.schema.fieldsRule="All"

      params = [param0, param1, param2, param3, param4, param5, param6,]
      return params

   def isLicensed(self):
      return True

   def updateParameters(self, parameters):
      """Modify the values and properties of parameters before internal
      validation is performed.  This method is called whenever a parameter
      has been changed."""
      if parameters[5].altered == False and parameters[5].value:
        try:
           parameters[5].value = os.path.join(arcpy.env.workspace,"ELR_SEG_MRT")
        except:
           pass
      if parameters[6].altered == False and parameters[6].value:
        try:
           parameters[6].value = os.path.join(arcpy.env.workspace,"ELR_SEG_EMRT")
        except:
           pass
      return

   def updateMessages(self, parameters):
      """Modify the messages created by internal validation for each tool
      parameter.  This method is called after internal validation."""
      return

   def validateJSONandFields(self, data, parameters):
      count=1
      flag=0

      for newdata in self.data:
         if not "name" in newdata:
            arcpy.AddError("Name attribute does not exist in JSON item number %s"%count)
            arcpy.AddError("********************************************************************")
            flag=1

         if not "path" in newdata:
            arcpy.AddError("Path attribute does not exist in JSON item number %s"%count)
            arcpy.AddError("********************************************************************")
            flag=1

         if not "routeIdentifierField" in newdata:
            arcpy.AddError("routeIdentifierField attribute does not exist in JSON item number %s"%count)
            arcpy.AddError("********************************************************************")
            flag=1

         if not "fromMeasureField" in newdata:
            arcpy.AddError("fromMeasureField attribute does not exist in JSON item number %s"%count)
            arcpy.AddError("********************************************************************")
            flag=1

         if not "toMeasureField" in newdata:
            arcpy.AddError("toMeasureField attribute does not exist in JSON item number %s"%count)
            arcpy.AddError("********************************************************************")
            flag=1

         try:
            descObject=arcpy.Describe(newdata["path"])
            layerRouteIdentifierField=0
            layerFromMeasureField=0
            layerToMeasureField=0
            layerPrimaryKeyField=0
            layerObjectId=0

            try:
                example=descObject.OIDFieldName
                layerObjectId=1
            except:
                 layerObjectId=0

            for d in descObject.Fields:

                if(d.name.lower()==newdata.get("routeIdentifierField","").lower()):
                    layerRouteIdentifierField=1
                if(d.name.lower()==newdata.get("fromMeasureField","").lower()):
                    layerFromMeasureField=1
                if(d.name.lower()==newdata.get("toMeasureField","").lower()):
                    layerToMeasureField=1
                if(d.name.lower()==newdata.get("primaryKeyField","").lower()):
                    layerPrimaryKeyField=1

            if layerRouteIdentifierField==0:
               arcpy.AddError("routeIdentifierField(%s) field does not exist for layer in JSON item number %s"% (newdata["routeIdentifierField"], count))
               arcpy.AddError("********************************************************************")
               flag=1
            if layerFromMeasureField==0:
               arcpy.AddError("fromMeasureField(%s) field does not exist for layer in JSON item number %s"%(newdata["fromMeasureField"],count))
               arcpy.AddError("********************************************************************")
               flag=1
            if layerToMeasureField==0:
               arcpy.AddError("toMeasureField(%s) field does not exist for layer in JSON item number %s"%(newdata["toMeasureField"],count))
               arcpy.AddError("********************************************************************")
               flag=1
            if layerPrimaryKeyField==0:
               if layerObjectId==0:
                  arcpy.AddError("Object ID does not exist for layer in JSON item number %s."%count)
                  arcpy.AddError("When a primary key is not set there must be an Object ID.")
                  arcpy.AddError("********************************************************************")
                  flag=1

         except Exception as e:
            arcpy.AddError("Layer does not exist for layer number %s"%count)
            arcpy.AddError(e.message)
            arcpy.AddError("********************************************************************")
            flag=1

         count+=1
         if flag==1:
            raise Exception("Errors occurred. Cannot continue Segmentor execution")
      return

   def addConnectionObjectsToSegmentor(self, layerData, parameters):
      primaryKey=False
      routeConnectionObject=eaglepy.DataSource.connect("ConnectionEsriDA",parameters[0].valueAsText,[parameters[1].valueAsText,parameters[2].valueAsText,parameters[3].valueAsText], "", parameters[1].valueAsText, autoLoad=True)
      routeFieldMap=eaglepy.lr.segmentation.fieldMapBlank()
      routeFieldMap[eaglepy.lr.segmentation.FROM_MEASURE]=str(parameters[2].value)
      routeFieldMap[eaglepy.lr.segmentation.TO_MEASURE]=str(parameters[3].value)
      routeFieldMap[eaglepy.lr.segmentation.ROUTE_ID]=str(parameters[1].value)
      routeFieldMap[eaglepy.lr.segmentation.PRIMARY_KEY]=str(parameters[1].value)

      mrtColumnList = GetMeasureRangeTableFieldList()
      err_column_list = GetErrorTableFieldList()

      if arcpy.Exists(parameters[5].valueAsText):
          arcpy.Delete_management(parameters[5].valueAsText)
      if arcpy.Exists(parameters[6].valueAsText):
          arcpy.Delete_management(parameters[6].valueAsText)

      segmentationObject=eaglepy.lr.segmentation.ManagedSegmentor(routeDataSource=routeConnectionObject,
                                                                  routeFieldMap=routeFieldMap,
                                                                  pathToOutputTable=parameters[5].valueAsText,
                                                                  pathToErrorTable=parameters[6].valueAsText,
                                                                  columnsForOutputTable=mrtColumnList,
                                                                  columnsForErrorTable=err_column_list)

      count=1
      layerCount=0
      layerConnectionObject=[]

      for newdata in layerData:

         primaryKey="primaryKeyField" in newdata

         pathHolder=newdata["path"]

         descObject=arcpy.Describe(newdata["path"])
         for d in descObject.Fields:
            d.name=newdata.get("routeIdentifierField","")
            d.name=newdata.get("fromMeasureField","")
            d.name=newdata.get("toMeasureField","")

         try:
            layerFieldMap=eaglepy.lr.segmentation.fieldMapBlank()
            layerFieldMap[eaglepy.lr.segmentation.FROM_MEASURE]=newdata["fromMeasureField"]
            layerFieldMap[eaglepy.lr.segmentation.TO_MEASURE]=newdata["toMeasureField"]
            layerFieldMap[eaglepy.lr.segmentation.ROUTE_ID]=newdata["routeIdentifierField"]
            if primaryKey==False:
                layerFieldMap[eaglepy.lr.segmentation.PRIMARY_KEY]="OID@"
                layerConnectionObject=eaglepy.DataSource.connect("ConnectionEsriDA", str(newdata["path"]),list(set(["OID@",newdata["fromMeasureField"], newdata["toMeasureField"],newdata["routeIdentifierField"]])),"","OID@",autoLoad=False)
                segmentationObject.addDataSource(newdata["name"],layerConnectionObject,layerFieldMap)
            elif primaryKey==True:
                layerFieldMap[eaglepy.lr.segmentation.PRIMARY_KEY]=newdata["primaryKeyField"]
                layerConnectionObject=eaglepy.DataSource.connect("ConnectionEsriDA", str(newdata["path"]),list(set([newdata["primaryKeyField"],newdata["fromMeasureField"], newdata["toMeasureField"], newdata["routeIdentifierField"]])),"",newdata["primaryKeyField"],autoLoad=False)
                segmentationObject.addDataSource(newdata["name"],layerConnectionObject,layerFieldMap)
            layerCount+=1
         except Exception as e:
            arcpy.AddError(e.message)
         count+=1
      return segmentationObject

   def execute(self, parameters, messages):
      """The source code of the tool."""
      eaglepy._eagleLog.removeParam("PRINT")
      eaglepy._eagleLog.addParam("ARCPY")

      if parameters[5].valueAsText==parameters[6].valueAsText:
        arcpy.AddError("Measure Range Table and Error Table names cannot be identical.")
        raise arcpy.ExecuteError

      try:
         path=str(parameters[4].valueAsText)
         json_data=open(path).read()
         self.data=json.loads(json_data)
      except ValueError as e:
         arcpy.AddError("Invalid JSON found in file.")
         return
      except:
         try:
            self.data=json.loads(parameters[4].valueAsText)
         except ValueError as e:
            arcpy.AddError("Invalid JSON within input string.")
            return
         except:
            arcpy.AddError("Unable to retrieve JSON object.")
            return

      self.validateJSONandFields(self.data,parameters)
      seg=self.addConnectionObjectsToSegmentor(self.data, parameters)

      seg.execute()

      arcpy.AddMessage("Done")

      return

class Attributer(object):
   def __init__(self):
      """Tool used to retrieve attributes from features"""
      self.label="Attributer Tool"
      self.description="Attributer tool is used to retrieve attributes from features"
      self.category="Linear Referencing"
      self.canRunInBackground=False

   def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(displayName="Dynamic Segmentation Table",name="dynamicSegmentationTable",datatype="Table View",parameterType="Required",direction="Input")

        param1 = arcpy.Parameter(displayName="Input Layers",name="inputLayers",datatype=["File","String"],parameterType="Required",direction="Input")

        param2 = arcpy.Parameter(displayName="Output Attributed Measure Range",name="outputAttributedMeasureRangeTable",datatype="Table",parameterType="Required",direction="Output")

        param3 = arcpy.Parameter(displayName="Output Error Table",name="outputErrorTable",datatype="Table",parameterType="Required",direction="Output")

        params = [param0, param1, param2, param3,]

        return params

   def isLicensed(self):
      return True

   def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[2].altered==False and parameters[2].value:
           try:
              parameters[2].value=os.path.join(arcpy.env.workspace,"ELR_SEG_AMRT")
           except:
              pass
        if parameters[3].altered==False and parameters[3].value:
           try:
              parameters[3].value=os.path.join(arcpy.env.workspace,"ELR_SEG_EAMRT")
           except:
              pass
        return

   def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

   def getAllColumns(self):
      attrList = []
      count=1
      for newdata in self.data:
         for col in newdata["columns"]:
            attrList.append([newdata["name"],col["outputColumnName"],col["inputColumnName"]])
      return attrList

   def validateJSON(self, data, parameters):
      count=1
      flag=0
      self.masterOutputFieldList = list()
      for newdata in self.data:
         if not "name" in newdata:
            arcpy.AddError("Name attribute does not exist in JSON item number %s"%count)
            arcpy.AddError("********************************************************************")
            flag=1

         if not "columns" in newdata:
            arcpy.AddError("Columns attribute does not exist in JSON item number %s"%count)
            arcpy.AddError("********************************************************************")
            flag=1
         else:
            columnCount=1
            for col in newdata["columns"]:
               if not "inputColumnName" in col:
                  arcpy.AddError("inputColumnName attribute does not exist for column map %s in layer number %s"%(columnCount,count))
                  arcpy.AddError("********************************************************************")
                  flag=1
               if not "outputColumnName" in col:
                  arcpy.AddError("outputColumnName attribute does not exist for column map %s in layer number %s"%(columnCount,count))
                  arcpy.AddError("********************************************************************")
                  flag=1
               columnCount+=1

         if flag==1:
            raise Exception("Errors occurred. Cannot continue Attributer execution")

         fc = parameters[0].valueAsText
         whereClause = "LAYER_NAME='%s'"%newdata["name"]
         fields=["LAYER_NAME","METADATA"]
         problemFields=[]

         with arcpy.da.SearchCursor(fc, fields,whereClause) as cursor:
            for item in cursor:
               metaData=dict()
               metaData=json.loads(item[1])

               try:
                  fieldList=[]
                  columnList=[]
                  try:
                     if metaData["path"] is not None:
                        desc=arcpy.Describe(metaData["path"])
                        #look through input columns and if they are in the desc.fields list,
                        #change the name to the outputColumnName, and append them to the master list
                        for aCol in newdata["columns"]:
                            #find the input column name in the desc.fields list
                            for arcpyField in desc.fields:
                                if arcpyField.name == aCol["inputColumnName"]:
                                    tmpField = arcpyField
                                    tmpField.name = aCol["outputColumnName"]
                                    tmpField.aliasName = aCol["outputColumnName"]
                                    self.masterOutputFieldList.append(tmpField)
                                    break
                        #done getting data types.

                        for d in desc.Fields:
                           fieldList.append(d.name)
                        for column in newdata["columns"]:
                           for xKey,xValue in column.items():
                              if(xKey=="inputColumnName"):
                                 columnList.append(xValue)
                        for c in columnList:
                           if c not in fieldList:
                              problemFields.append((c,newdata["name"]))
                  except:
                     pass

               except Exception as e:
                  arcpy.AddError("Layer does not exist for layer number %s"%count)
                  arcpy.AddError(e.message)
                  arcpy.AddError("********************************************************************")
                  flag=1

               for problem in problemFields:
                  arcpy.AddError("%s field does not exist for layer %s"%(problem[0], problem[1]))
                  arcpy.AddError("********************************************************************")
                  flag=1
               break
         count+=1
      if flag==1:
         raise Exception("Errors occurred. Cannot continue Attributer execution")
      return

   def execute(self, parameters, messages):
      """The source code of the tool."""
      eaglepy._eagleLog.removeParam("PRINT")
      eaglepy._eagleLog.addParam("ARCPY")
      self.mrtFieldNames = ["ROUTE_ID","MEAS_RANGE_ID","SEGMENT_ID","LAYER_NAME","LAYER_PRIMARY_KEY","METADATA","FROM_MEASURE","TO_MEASURE","GAP_INDICATOR","FEATURE_ID"]

      try:
         path=str(parameters[1].valueAsText)
         json_data=open(path).read()
         self.data=json.loads(json_data)
      except ValueError as e:
         arcpy.AddError("Invalid JSON found in file. Check syntax.")
         return
      except:
         try:
            self.data=json.loads(parameters[1].valueAsText)
         except ValueError as e:
            arcpy.AddError("Invalid JSON within input string. Check syntax.")
            return
         except:
            arcpy.AddError("Unable to retrieve JSON object.")
            return

      self.validateJSON(self.data,parameters)
      mrt=eaglepy.DataSource.connect("ConnectionEsriDAManaged",
                                     inputTable=parameters[0].valueAsText,
                                     fieldNames=self.mrtFieldNames,
                                     autoLoad=False,
                                     maxRecordCount=50000)

    # Add extra output fields to the master field list (self.masterOutputFieldList)
      self.masterOutputFieldList.append(eaglepy.da.ArcpyFieldFromAttributes(
                                                            name="ROUTE_ID",
                                                            type="STRING",
                                                            length=50))
      self.masterOutputFieldList.append(eaglepy.da.ArcpyFieldFromAttributes(
                                                            name="MEAS_RANGE_ID",
                                                            type="STRING",
                                                            length=50))
      self.masterOutputFieldList.append(eaglepy.da.ArcpyFieldFromAttributes(
                                                            name="SEGMENT_ID",
                                                            type="STRING",
                                                            length=50))
      self.masterOutputFieldList.append(eaglepy.da.ArcpyFieldFromAttributes(
                                                            name="FEATURE_ID",
                                                            type="STRING",
                                                            length=50))
      self.masterOutputFieldList.append(eaglepy.da.ArcpyFieldFromAttributes(
                                                            name="LAYER_NAME",
                                                            type="STRING",
                                                            length=50))
      self.masterOutputFieldList.append(eaglepy.da.ArcpyFieldFromAttributes(
                                                            name="LAYER_PRIMARY_KEY",
                                                            type="STRING",
                                                            length=50))
      self.masterOutputFieldList.append(eaglepy.da.ArcpyFieldFromAttributes(
                                                            name="FROM_MEASURE",
                                                            type="DOUBLE"))
      self.masterOutputFieldList.append(eaglepy.da.ArcpyFieldFromAttributes(
                                                            name="TO_MEASURE",
                                                            type="DOUBLE"))
      self.masterOutputFieldList.append(eaglepy.da.ArcpyFieldFromAttributes(
                                                            name="GAP_INDICATOR",
                                                            type="STRING",
                                                            length=50))
      self.masterOutputFieldList.append(eaglepy.da.ArcpyFieldFromAttributes(
                                                            name="METADATA",
                                                            type="STRING",
                                                            length=4000))

      attr = eaglepy.lr.segmentation.ManagedAttributer(measureRangeTable=mrt,
                                                       pathToOutputTable=parameters[2].valueAsText,
                                                       pathToErrorTable=parameters[3].valueAsText,
                                                       columnsForOutputTable=self.masterOutputFieldList,
                                                       columnsForErrorTable=GetErrorTableFieldList())

      attrList = self.getAllColumns()

      #add each column to both the currAMRT list and as an output column to the attributer.
      for oneAttr in attrList:
          attr.addOutputColumn(oneAttr[0],oneAttr[1],oneAttr[2])

      attr.execute()
      arcpy.AddMessage("Done.")
      return

class Statistitater(object):
   def __init__(self):
      """Tool used to retrieve attributes from features"""
      self.label="Statistitater Tool"
      self.description="Statistitater tool is used to execute business rules on the Attributed Measure Range Table"
      self.category="Linear Referencing"
      self.canRunInBackground=False

   def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(displayName="Attributed Measure Range Table",name="attributedMeasureRangeTable",datatype="Table View",parameterType="Required",direction="Input")

        param1 = arcpy.Parameter(displayName="Group By",name="groupBy",datatype="Field",parameterType="Required",direction="Input")

        param2 = arcpy.Parameter(displayName="Calculation Rules",name="calculationRules",datatype=["File","String"],parameterType="Required",direction="Input")

        param3 = arcpy.Parameter(displayName="Output Business Measure Range",name="outputBusinessMeasureRangeTable",datatype="Table",parameterType="Required",direction="Output")

        param4 = arcpy.Parameter(displayName="Output Error Table",name="outputErrorTable",datatype="Table",parameterType="Required",direction="Output")

        param1.parameterDependencies=[param0.name]

        params = [param0, param1, param2, param3,param4]

        return params

   def isLicensed(self):
      return True

   def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[3].altered==False and parameters[3].value:
            try:
               parameters[3].value=os.path.join(arcpy.env.workspace,"ELR_SEG_SMRT")
            except:
               pass
        if parameters[4].altered==False and parameters[4].value:
            try:
               parameters[4].value=os.path.join(arcpy.env.workspace,"ELR_SEG_ESMRT")
            except:
               pass
        return

   def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

   def validateJSON(self, data, parameters):
      unique=[]
      problems=[]
      fields=[]
      nameProblems=[]
      calculationProblems=[]
      flag=0
      count=1
      for d in self.data:
         if "name" in d:
            fields.append(d["name"])
         else:
            try:
               if d["name"] is not None:
                  arcpy.AddError("There must be a name item in the JSON object for item number %s. Please add item and re-run. See tool's help for examples."%count)
                  arcpy.AddError("********************************************************************")
                  flag=1
            except:
               pass

         if not "calculation" in d:
            try:
                if d["calculation"] is not None:
                   arcpy.AddError("There must be a calculation item in the JSON object for item number %s. Please add item and re-run. See tool's help for examples."%count)
                   arcpy.AddError("********************************************************************")
                   flag=1
            except:
                pass

         if "calculation" in d:
            calc = d["calculation"]
            newCalc = eaglepy.lr.segmentation.calculation.ResolveCalculation(calc)

            if newCalc == False:
               arcpy.AddError("There was an error with the calculation for item number %s. Please correct item and re-run. See tool's help for examples."%count)
               arcpy.AddError("********************************************************************")
               flag=1
         count+=1

      for z in fields:

         if z==parameters[1].valueAsText:
            arcpy.AddError("There can be no items in the Calculate Rules JSON object with the same name as the Group By field. %s's name must be changed in the JSON object file/string."%z)
            arcpy.AddError("********************************************************************")
            flag=1

      for y in fields:

         if y not in unique:
            unique.append(y)
            pass
         else:
            problems.append(y)

      for x in problems:
         arcpy.AddError("There must be unique names within the Calculate Rules JSON object. %s has appeared more than once in the file."%problems[0])
         arcpy.AddError("********************************************************************")
         flag=1

      if flag==1:
         raise Exception("Errors occurred. Cannot continue Statistitater execution")
      return

   def execute(self, parameters, messages):
        """The source code of the tool."""
        eaglepy._eagleLog.removeParam("PRINT")
        eaglepy._eagleLog.addParam("ARCPY")
        fieldsMRT=[]
        desc=arcpy.Describe(parameters[0].valueAsText)
        for d in desc.Fields:
            fieldsMRT.append(d.name)

        mrt=eaglepy.DataSource.connect("ConnectionEsriDAManaged",
                                       inputTable=parameters[0].valueAsText,
                                       fieldNames=fieldsMRT,
                                       autoLoad=False,
                                       maxRecordCount=50000
                                       )

        try:
             path=str(parameters[2].valueAsText)
             json_data=open(path).read()
             self.data=json.loads(json_data)
        except ValueError as e:
             arcpy.AddError("Invalid JSON found in file. Check syntax.")
             return
        except:
            try:
                self.data=json.loads(parameters[2].valueAsText)
            except ValueError as e:
                arcpy.AddError("Invalid JSON within input string. Check syntax.")
                return
            except:
                arcpy.AddError("Unable to retrieve JSON object.")

        self.validateJSON(self.data,parameters)

        masterFieldList = list()
        for item in self.data:
            if "dataType" in item:
                typeDict = item["dataType"]
                typeDict["name"] = item["name"]
                typeDict["aliasName"] = item["name"]
                arcpyField = eaglepy.da.ArcpyFieldFromAttributes(**typeDict)
                masterFieldList.append(arcpyField)

        #append any extra fields to the end (standard fields)
        for d in desc.Fields:
            if d.name == parameters[1].valueAsText:
                masterFieldList.append(d)
                break

        stat=eaglepy.lr.segmentation.ManagedStatistics(inputTable=mrt,
                                                       groupByColumnName=parameters[1].valueAsText,
                                                       pathToOutputTable=parameters[3].valueAsText,
                                                       pathToErrorTable=parameters[4].valueAsText,
                                                       columnsForOutputTable=masterFieldList,
                                                       columnsForErrorTable=GetErrorTableFieldList()
                                                       )



        for item in self.data:
            try:
               if item["name"] is not None:
                  stat.addOutputColumn(item["name"],item["calculation"])
            except:
               pass

        stat.execute()



        return


class Dissolverator(object):
    def __init__(self):
        """Tool used to retrieve attributes from features"""
        self.label = "Dissolverator Tool"
        self.description = "dissolves"
        self.category = "Linear Referencing"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        tableToDissolve = arcpy.Parameter(displayName="Table to Dissolve",
                                          name="tableToDissolve",
                                          datatype="Table View",
                                          parameterType="Required",
                                          direction="Input")

        groupBy = arcpy.Parameter(displayName="Group By",
                                  name="groupBy",
                                  datatype="Field",
                                  parameterType="Required",
                                  direction="Input")

        orderBy = arcpy.Parameter(displayName="Order By",
                                  name="orderBy",
                                  datatype="Field",
                                  parameterType="Required",
                                  direction="Input")

        beginStation = arcpy.Parameter(displayName="Begin Station",
                                       name="beginStation",
                                       datatype="Field",
                                       parameterType="Required",
                                       direction="Input")

        endStation = arcpy.Parameter(displayName="End Station",
                                     name="endStation",
                                     datatype="Field",
                                     parameterType="Required",
                                     direction="Input")

        dissolveColumns = arcpy.Parameter(displayName="Dissolve Columns",
                                          name="dissolveColumns",
                                          datatype="Field",
                                          parameterType="Required",
                                          direction="Input",
                                          multiValue=True)

        statisticsColumns = arcpy.Parameter(displayName="Statistics Columns",
                                            name="statisticsColumns",
                                            datatype=["File", "String"],
                                            parameterType="Optional",
                                            direction="Input")

        outputDissolvedData = arcpy.Parameter(displayName="Output Dissolved Data",
                                              name="outputDissolvedData",
                                              datatype="Table",
                                              parameterType="Required",
                                              direction="Output")

        outputErrorTable = arcpy.Parameter(displayName="Output Error Table",
                                           name="outputErrorTable",
                                           datatype="Table",
                                           parameterType="Required",
                                           direction="Output")

        groupBy.parameterDependencies=[tableToDissolve.name]
        orderBy.parameterDependencies=[tableToDissolve.name]
        beginStation.parameterDependencies=[tableToDissolve.name]
        endStation.parameterDependencies=[tableToDissolve.name]
        dissolveColumns.parameterDependencies=[tableToDissolve.name]
        beginStation.filter.list = ['Double', 'Short', 'Long', 'Float']
        endStation.filter.list = ['Double', 'Short', 'Long', 'Float']

        params = [tableToDissolve,
                  groupBy,
                  orderBy,
                  beginStation,
                  endStation,
                  dissolveColumns,
                  statisticsColumns,
                  outputDissolvedData,
                  outputErrorTable]

        return params

    def isLicensed(self):
      return True


    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if not parameters[7].altered and parameters[7].value:
            try:
               parameters[7].value = os.path.join(arcpy.env.workspace, "ELR_SEG_DMRT")
            except:
               pass
        if parameters[8].altered==False and parameters[8].value:
            try:
               parameters[8].value=os.path.join(arcpy.env.workspace,"ELR_SEG_EDMRT")
            except:
               pass
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def validateJSON(self, data, parameters):
        unique = list()
        problems = list()
        fields = list()
        nameProblems = list()
        calculationProblems = list()
        flag = 0
        count = 1
        for d in self.data:
            try:
                if d["name"] is not None:
                    fields.append(d["name"])
            except:
                arcpy.AddError("There must be a name item in the JSON object for item number %s. "
                               "Please add item and re-run. See tool's help for examples." % count)
                arcpy.AddError("********************************************************************")
                flag = 1
            try:
                if d["calculation"] is not None:
                    pass
            except:
                arcpy.AddError("There must be a calculation item in the JSON object for item number %s. "
                               "Please add item and re-run. See tool's help for examples." % count)
                arcpy.AddError("********************************************************************")
                flag = 1

            try:
                if d["calculation"] is not None:
                    calc = d["calculation"]
                    newCalc = eaglepy.lr.segmentation.calculation.ResolveCalculation(calc)
                    if not newCalc:
                        arcpy.AddError("There was an error with the calculation for item number %s. "
                                       "Please correct item and re-run. See tool's help for examples." % count)
                        arcpy.AddError("********************************************************************")
                        flag = 1
            except:
                pass
        count += 1

        for z in fields:
            if z == parameters[1].valueAsText:
                arcpy.AddError("There can be no items in the Calculate Rules JSON object with the same name as the "
                               "Group By field. %s's name must be changed in the JSON object file/string." % z)
                arcpy.AddError("********************************************************************")
                flag = 1

        for y in fields:
            if y not in unique:
                unique.append(y)
            else:
                problems.append(y)

        for x in problems:
            arcpy.AddError("There must be unique names within the Calculate Rules JSON object. "
                           "%s has appeared more than once in the file." % problems[0])
            arcpy.AddError("********************************************************************")
            flag = 1

        if flag == 1:
            raise Exception("Errors occurred. Cannot continue Dissolverator execution")
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        eaglepy._eagleLog.removeParam("PRINT")
        eaglepy._eagleLog.addParam("ARCPY")
        dissolveColumnList=parameters[5].valueAsText.split(";")

        fieldsMRT=[]
        sourceMRTFields = dict()
        desc = arcpy.Describe(parameters[0].valueAsText)
        for d in desc.Fields:
            fieldsMRT.append(d.name)
            sourceMRTFields[d.name] = d

        mrt = eaglepy.DataSource.connect("ConnectionEsriDAManaged",
                                         inputTable=parameters[0].valueAsText,
                                         fieldNames=fieldsMRT,
                                         maxRecordCount=50000)

        masterFieldList = list()

        inputColumns = arcpy.ListFields(parameters[0].valueAsText)
        for field in inputColumns:
            if field.name == parameters[1].valueAsText:
                masterFieldList.append(field)
            elif field.name == parameters[3].valueAsText:
                masterFieldList.append(field)
            elif field.name == parameters[4].valueAsText:
                masterFieldList.append(field)

        for d in dissolveColumnList:
            for field in inputColumns:
                if d == field.name:
                    masterFieldList.append(field)
                    break

        # if parameters[6].valueAsText is not None:
        #     try:
        #         path = str(parameters[6].valueAsText)
        #         json_data = open(path).read()
        #         self.data = json.loads(json_data)
        #     except ValueError as e:
        #         arcpy.AddError("Invalid JSON found in file. Check syntax.")
        #         return
        #     except:
        #         try:
        #             self.data = json.loads(parameters[6].valueAsText)
        #         except ValueError as e:
        #             arcpy.AddError("Invalid JSON within input string. Check syntax.")
        #             return
        #         except:
        #             arcpy.AddError("Unable to retrieve JSON object.")
        #
        #     self.validateJSON(self.data, parameters)
        #
        #     for item in self.data:
        #         if "dataType" in item:
        #             typeDict = item["dataType"]
        #             typeDict["name"] = item["name"]
        #             typeDict["aliasName"] = item["name"]
        #             arcpyField = eaglepy.da.ArcpyFieldFromAttributes(**typeDict)
        #             masterFieldList.append(arcpyField)

        #append any extra fields to the end (standard fields)
        dissolver = eaglepy.lr.segmentation.ManagedDissolverator(inputTable=mrt,
                                                                 groupByColumnName=parameters[1].valueAsText,
                                                                 orderByColumnName=parameters[2].valueAsText,
                                                                 beginMeasureColumnName=parameters[3].valueAsText,
                                                                 endMeasureColumnName=parameters[4].valueAsText,
                                                                 pathToOutputTable=parameters[7].valueAsText,
                                                                 pathToErrorTable=parameters[8].valueAsText,
                                                                 columnsForOutputTable=masterFieldList,
                                                                 columnsForErrorTable=GetErrorTableFieldList()
                                                                 )

        # if parameters[6].valueAsText is not None:
        #     for c in self.data:
        #         dissolver.addCalculationColumn(c["name"], c["calculation"])

        for d in dissolveColumnList:
            dissolver.addDissolveColumn(d)

        #Execute the dissolve
        dissolver.execute()

        arcpy.AddMessage("Done.")
        return