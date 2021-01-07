import sys
py_version = sys.version_info[0]

import eaglepy, numpy, traceback, json, copy
from eaglepy.lr import _BaseLRObject
import eaglepy.da
import eaglepy.DataSource
import os
from collections import OrderedDict

####################################
##Exceptions
####################################
class InvalidFieldMap(eaglepy.lr.LinearReferencingException):
    pass

class InvalidConnectionType(eaglepy.lr.LinearReferencingException):
    pass

class InvalidRoute(eaglepy.lr.LinearReferencingException):
    pass

class DuplicateOutputColumn(eaglepy.lr.LinearReferencingException):
    pass

class InvalidCalculationType(eaglepy.lr.LinearReferencingException):
    pass

####################################
##Methods
####################################
ROUTE_ID="routeID"
PRIMARY_KEY="primaryKey"
FROM_MEASURE="fromMeasure"
TO_MEASURE="toMeasure"

MEASURE_RANGE_TABLE_COLUMNS = ["ROUTE_ID","MEAS_RANGE_ID","SEGMENT_ID","FEATURE_ID","LAYER_NAME","LAYER_PRIMARY_KEY","FROM_MEASURE","TO_MEASURE","GAP_INDICATOR","METADATA"]
MEASURE_RANGE_TABLE_DATA_TYPES=["S50","S50","S50","S50","S50","S50",numpy.float64,numpy.float64,"S50","S4000"]
MEASURE_RANGE_TABLE_PRIMARY_KEY="MEAS_RANGE_ID"
ERROR_RANGE_TABLE_COLUMNS=["ERROR_ID","ROUTE_ID","INPUT_LAYER","INPUT_LAYER_COL_NAME","INPUT_LAYER_ID","ERROR_TYPE","ERROR_DESCRIPTION"]
ERROR_RANGE_TABLE_DATA_TYPES=["S50","S50","S4000","S50","S50","S50","S4000"]
ERROR_RANGE_TABLE_PRIMARY_KEY="ERROR_ID"


def validateFieldMap(fieldMap):
    """Validates that the specified fieldMap contains the required columns returns true/false"""

    if not PRIMARY_KEY in fieldMap:
        return False
    if not ROUTE_ID in fieldMap:
        return False
    if not FROM_MEASURE in fieldMap:
        return False
    if not TO_MEASURE in fieldMap:
        return False
    #all is well in the world.
    return True

def validateManagedDataSource(dataSource):
    if type(dataSource) != eaglepy.DataSource.ConnectionEsriDAManaged:
        return False
    return True

def fieldMapBlank():
    """Returns a blank fieldMap object with emtpy strings for all of the values"""
    return {ROUTE_ID:"",PRIMARY_KEY:"",FROM_MEASURE:"",TO_MEASURE:""}


class _BaseSegmentation(_BaseLRObject):
    def __init__(self, **kwargs):
        super(_BaseSegmentation, self).__init__()
        self.errorOutput = []

    def _addErrorToLog(self,errorCode,errorDescription="",**kwargs):
        """Takes in the specified error and writes it to the self.errorOutput table.
            errorCode - The text version of the error code, should be one of the following:
                NON_UNIQUE_KEY -
                NULL_ROUTE_ID - x
                INVALID_ROUTE_ID - x
                NULL_INVALID_GEOMETRY
                NO_INVALID_MEASURE - x
                NULL_FROM_MEASURE - x
                MEASURE_SWAP
                MEASURE_NON_NUMBER
                NULL_TO_MEASURE - x
                FIELD_DOES_NOT_EXIST - x
                COULD_NOT_CALCULATE_OUTPUT - x
                COULD_NOT_WRITE_ROW
                CRASH
            errorDescription - Details about the error, this could be a crash dump, or stack trace if needed.
            other possible parameters are:
                ROUTE_ID - The routeID of the layer
                INPUT_LAYER - The full path to the layer in question
                INPUT_LAYER_COL_NAME - The column name of the layer that has the issue
                INPUT_LAYER_ID - The primary key value of the feature in question.
                layer - If specified, the INPUT_LAYER parameter will be specified automatically.
            """
        newErrorRecord = {"ROUTE_ID":"","INPUT_LAYER":"","INPUT_LAYER_COL_NAME":"","INPUT_LAYER_ID":""}
        newErrorRecord["ERROR_ID"] = eaglepy.MakeRandomGUID()
        newErrorRecord["ERROR_TYPE"] = errorCode
        newErrorRecord["ERROR_DESCRIPTION"] = errorDescription
        if "ROUTE_ID" in kwargs:
            newErrorRecord["ROUTE_ID"] = kwargs["ROUTE_ID"]
        if "INPUT_LAYER" in kwargs:
            newErrorRecord["INPUT_LAYER"] = kwargs["INPUT_LAYER"]
        if "INPUT_LAYER_COL_NAME" in kwargs:
            newErrorRecord["INPUT_LAYER_COL_NAME"] = kwargs["INPUT_LAYER_COL_NAME"]
        if "INPUT_LAYER_ID" in kwargs:
            newErrorRecord["INPUT_LAYER_ID"] = kwargs["INPUT_LAYER_ID"]

        if "layer" in kwargs:
            if hasattr(kwargs["layer"],"_inputTable"):
                newErrorRecord["INPUT_LAYER"] = kwargs["layer"]._inputTable
        self.errorOutput.append(newErrorRecord)


    def getErrorTable(self):
        """Returns the segmentation error table as an eaglepy.DataSource.Connection."""
        #self._addLog("Starting Creation of Error Table.")
        fields = ERROR_RANGE_TABLE_COLUMNS
        dataTypes=ERROR_RANGE_TABLE_DATA_TYPES
        primaryKey=ERROR_RANGE_TABLE_PRIMARY_KEY
        conn = eaglepy.DataSource.connect("ConnectionEsriEdit",
                                          fieldNames=fields,
                                          primaryKey=primaryKey,
                                          dataTable=self.errorOutput,
                                          fieldDataTypes=dataTypes)
        #self._addLog("Error Table Creation Complete.")
        return conn


class WhenToWriteMixin(object):
    """
    Special mixin that provides a hook to periodically write data to disk.
    By default the writeToDisk method does nothing.
    """

    def writeToDisk(self, force=False):
        """
        Method to override when a child class wants to write data to disk using some criteria.  Note that
        when force is passed, that criteria should be invalid, and all in-memory data should be written
        to disk.
        @param force: When True, forces the write to disk, when false, some criteria (i.e. number of records)
            should be met in order to make the decision to write to disk.  Default is False
        @return: None.
        """
        return


class Segmentor(_BaseSegmentation):
    """Class that defines the Segmentor object."""
    _routeDataSource = None
    _routeFieldMap= None
    _errorTable = None
    _dataSourceList = []

    ##Constants
    _MD_ID = 0
    _MD_LAYER_NAME=1
    _MD_PRIMARY_KEY_VALUE=2
    _MD_FROM_MEASURE = 3
    _MD_TO_MEASURE = 4


    def __init__(self,routeDataSource=None,routeFieldMap=None):
        """Creates a new Segmentor class.
            routeDataSource - An eaglepy.DataSource.Connection that representes the single route record for this segmentation (optional)
            routeFieldMap - A dictionary that maps required fields to the actual fields in the routeDataSource (optional, required if a routeDataSource is specified).
                routeID - The route identifier field for the dataSource
                primaryKey - The primary key column for the dataSource (Must be the same as routeID)
                fromMeasure - The from measure field of the dataSource
                toMeasure - The to measure field of the dataSource
        """
        _BaseSegmentation.__init__(self)
        self.measureRangeOutput = []
        self._errorTable = None
        self._dataSourceList = []
        self._addLog("Initializing Segmentor.")
        self._routeDataSource = routeDataSource
        self._routeFieldMap = routeFieldMap
        self.hasRoute = False
        self._dataSourceList = []
        if self._routeDataSource is not None:
            #if there is a route, then there must be a field map.
            if self._routeFieldMap is None:
                raise InvalidFieldMap("A fieldMap object must be specified if a routeDataSource is specified.")
            #load the route as if it were any other data source.
            self.addDataSource("route",self._routeDataSource,self._routeFieldMap)
            self.hasRoute = True


    def addDataSource(self,name, dataSource,fieldMap):
        """Adds the specified dataSource to the list of things to segment.  The dataSources must already be filtered for the route in question.
            name - The user specified name of the dataSource, this must be unique
            dataSource - an eaglepy.DataSource.Connection object that points to the datasourece to segment.
            fieldMap - A dictionary that maps the columns this tool looks for to the columns in the dataSource.
                    routeID - The route identifier field for the dataSource
                    primaryKey - The primary key column for the dataSource
                    fromMeasure - The from measure field of the dataSource
                    toMeasure - The to measure field of the dataSource"""
        if validateFieldMap(fieldMap):
            self._dataSourceList.append((name,dataSource,fieldMap))
            self._addLog("Adding Data Source (%s)"%(name))
        else:
            raise InvalidFieldMap("The specified field map for %s was invalid."%(name),str(fieldMap))

    def execute(self):
        """Executes the segmentation process."""
        #TODO: add documentation of what the process does here (see the word doc for details).
        try:
            self._addLog("Executing Segmentation")
            self._addLog("Extracting Feature Data")


            try:
                self._getFeatureData()
            except Exception as e:
                self._addError("Get Feature Data Error.")
                self._addError(traceback.format_exc())
                raise e

            self._addLog("Segmenting Data")
            try:
                self._segmentData()
            except Exception as e:
                self._addError("Segment Data Error.")
                self._addError(traceback.format_exc())
                raise e

            self._addLog("Segmentation Complete")
        except Exception as e:
            #HOLLY SHIT, something has gone really really wrong!
            self._addError("He's dead JIM!")
            self._addError("I am a segmentor, not a Doctor!")
            self._addError(str(e))
            self._addErrorToLog("CRASH",str(e))
            self._addErrorToLog("CRASH",str((traceback.format_exc())))
            raise e
            #if we are in debug mode, then raise the error
            #if self._debug == True:
            #    raise e

    def executeGetFeatureDataBatch(self):
        self._addLog("Extracting Feature Data")
        try:
            self._getFeatureData()
        except Exception as e:
            self._addError("Get Feature Data Error.")
            self._addError(traceback.format_exc())
            raise e

    def _segmentData(self):
        """Segments the data from self.measureD and self.featureD, as created by _getFeatureData()"""
        self.measureRangeOutput = []
        if py_version<=2:
            measureList = self.measureD.keys()
        else:
            measureList = list(self.measureD.keys())
        measureList.sort()

        previousSegmentList = []
        for measureIndex in range(len(measureList)):
            #first look for point features, that is features that start and end at the same measure value
            beginMeasure = measureList[measureIndex]
            endMeasure = measureList[measureIndex]
            #get the list of feature GUIDs as a combination of all features from the previous segment,
            #and all features that start at beginMeasure
            possibleFeatureList = previousSegmentList + self.measureD[beginMeasure]
            possibleFeatureList = list(set(possibleFeatureList))#removes duplicates from the list.

            #reset the previousSegmentList
            previousSegmentList = []

            #test the points
            if self._segment_ifPointsExist(possibleFeatureList):
                validListOfFeatures = self._segment_testPoints(possibleFeatureList,beginMeasure)
                #save the valid list in the previousSegmentList
                previousSegmentList = previousSegmentList+validListOfFeatures

                #store each valid feature in the measureRangeOutput variable as an array
                #each array contains rangeGUID, FromMeasure, ToMeasure, GUID where GUID represents the key of the feature that is valid here.
                #rangeGUID is a guid that is unique for each FromMeasure, ToMeasure combination
                rangeGUID = eaglepy.MakeRandomGUID()
                #check to see if there is a route, if there is check to see if any of the special codes apply to the results.
                gapCode = self._segment_getGapCode(validListOfFeatures,beginMeasure,endMeasure)
                #save each item in validListOfFeatures
                for feat in validListOfFeatures:
                    newRecord = []
                    newRecord.append(rangeGUID)
                    newRecord.append(beginMeasure)
                    newRecord.append(endMeasure)
                    newRecord.append(feat)
                    newRecord.append(gapCode)
                    self.measureRangeOutput.append(newRecord)

                #if there is nothing in the validList OfFeatures, then we still need to output something
                if len(validListOfFeatures) == 0:
                    newRecord = []
                    newRecord.append(rangeGUID)
                    newRecord.append(beginMeasure)
                    newRecord.append(endMeasure)
                    newRecord.append("")
                    newRecord.append(gapCode)
                    self.measureRangeOutput.append(newRecord)


            #now take a look at linear features, that is features that have start and end measure values that are different
            #check to see if we are at the end of the list:
            if measureIndex + 1 == len(measureList):
                continue# we are at the end, so go to the next part of the loop
            endMeasure = measureList[measureIndex+1]

            validListOfFeatures = self._segment_testLines(possibleFeatureList,beginMeasure,endMeasure)

            #save the valid list in the previousSegmentList
            previousSegmentList = []
            previousSegmentList = previousSegmentList+validListOfFeatures

            #save all of the valid features, in the same format as the points.
            rangeGUID = eaglepy.MakeRandomGUID()
            #check to see if there is a route, if there is check to see if any of the special codes apply to the results.
            gapCode = self._segment_getGapCode(validListOfFeatures,beginMeasure,endMeasure)
            for feat in validListOfFeatures:
                newRecord = []
                newRecord.append(rangeGUID)
                newRecord.append(beginMeasure)
                newRecord.append(endMeasure)
                newRecord.append(feat)
                newRecord.append(gapCode)#place holder for gap_indicator flag.
                self.measureRangeOutput.append(newRecord)

            #if there is nothing in the validList OfFeatures, then we still need to output something
            if len(validListOfFeatures) == 0:
                newRecord = []
                newRecord.append(rangeGUID)
                newRecord.append(beginMeasure)
                newRecord.append(endMeasure)
                newRecord.append("")
                newRecord.append(gapCode)
                self.measureRangeOutput.append(newRecord)

    def _segment_getGapCode(self, validListOfFeatures, beginMeasure, endMeasure):
        """Checks the list of valid features, and determines the type of gap (if one exists) over this range.
            If there is a route, then it is first checked to see if the begin/end measures are outside the range of the route.
                if the being measure is less than the beginMeasure of the route, an OUTSIDE_BEGIN is returned
                if the end measure is greater than the endMeasure of the route, and OUTSIDE_END is returned
                if there is only a single valid record:
                    if that single record is the route,
                        if the current beginMeasure is == the begin measure of the route, it is a BEGIN gap
                        if the current endMeasure is == the end measure of the route, it is an END gap
                        otherwise it is an INTERIOR gap.
                if there are multiple records, then we must be inside the route, and there is at least one other item, so there is no gap: NONE
            """
        if self.hasRoute:
            #first check to see if the current measure is outside of the begin/end measure of the route
            #if it is, then return OUTSIDE_BEGIN, OUTSIDE_END
            #this indicates that there is a gap between features, and it is outside the range of the route.
            if beginMeasure < self.routeFromMeasure:
                return "OUTSIDE_BEGIN"
            elif endMeasure > self.routeToMeasure:
                return "OUTSIDE_END"

            #if there is only one feature, and that feature is the route, then there is a gap in one of three conditions:
            #BEGIN, END, INTERIOR.
            if len(validListOfFeatures) == 1:
                #if this single feature is the route, then the codes are either:
                    #BEGIN - only the route exists, and the beginMeasure is the begining of the route
                    #END - Only the route exists, and the endMeasure is the end of the route.
                    #INTERIOR - Only the route exists, but there are no other features, so there is a gap.
                singleFeature = self.featureD[validListOfFeatures[0]]
                if singleFeature[self._MD_LAYER_NAME] == "route":
                    #the single layer is a route, and so we need to test measures against the route
                    #to see where we are
                    if singleFeature[self._MD_FROM_MEASURE] == beginMeasure:
                        return "BEGIN"
                    elif singleFeature[self._MD_TO_MEASURE] == endMeasure:
                        return "END"
                    else:
                        return "INTERIOR"

            else: #there are multiple records, and it is inside the range of the route, so there is no gap here.
                return "NONE"

        else: #there is no route, so all we can do is check to see if there are features or not here.
            if len(validListOfFeatures) > 0:
                #there is at least one feature, so there is no gap here
                return "NONE"
            else:
                #there are gaps here.
                return "GAP"

        return "" #there is no route, so no gap checking occurs.

    def _segment_ifPointsExist(self,possibleList):
        """Returns true if at least one feature in the possibleList has a FromMeasure and ToMeasure that is equal"""
        for p in possibleList:
            featData = self.featureD[p]
            if featData[self._MD_FROM_MEASURE] == featData[self._MD_TO_MEASURE]:
                return True
        return False

    def _segment_testPoints(self,possibleList,beginMeasure):
        """Tests each item in the possibleList to ensure that surrounds the beginMeasure.
                possibleList - a list of GUIDs that represent features that could be valid
                beginMeasure - the current measure value to test agains.
            The test that is checked: featuresFromMeasure <= beginMeasure <= featuresToMeasure
        """
        actualList = []# a list of guids that belong here.
        for p in possibleList:
            featData = self.featureD[p]
            if featData[self._MD_FROM_MEASURE] <= beginMeasure <= featData[self._MD_TO_MEASURE]:
                #the feature is valid and should be in the actual list
                actualList.append(p)
        return actualList

    def _segment_testLines(self,possibleList,beginMeasure,endMeasure):
        """Tests each item in possibleList to ensure that it surroudns the begin/end Measure combination.
                possibleList - a list of GUIDs that represent features that could be valid
                beginMeasure - the begin measure for the range
                endMeasure - the end measure for the range
            The test that is checked: featuresFromMeasure <= beginMeasure <= featuresToMeasure AND featuresFromMeasure <= endMeasure <= featuresToMeasur
        """
        actualList = []
        for p in possibleList:
            featData = self.featureD[p]
            if (featData[self._MD_FROM_MEASURE] <= beginMeasure <= featData[self._MD_TO_MEASURE]) and (featData[self._MD_FROM_MEASURE] <= endMeasure <= featData[self._MD_TO_MEASURE]):
                actualList.append(p)
        return actualList

    def _getFeatureData(self):
        """
        Takes in the data source list, and for each data source, extracts the measure values into a unique list, and extracts the minimum set of attributes
        required inorder to segment the data.  Creates self.measureD and self.featureD
            measureD - A dictionary where the measure is the key, and the value is a list of GUIDs that represent the data stored in featureD
            featureD - a dictionary where a random GUID is the key, and the value is an ordered list containing:
                    GUID
                    The name of the data source
                    Primary Key value from the source layer
                    From_Measure - the from measure value of the original record
                    To_Measure - The to measure value of the original record.
            These are accessed in positional order, to help the constants self._MD_* have been created:
                _MD_ID = 0 - The GUID
                _MD_LAYER_NAME=1 - The layer name
                _MD_PRIMARY_KEY_VALUE=2 - the primary key value from the source layer
                _MD_FROM_MEASURE = 3 - the from emasure value
                _MD_TO_MEASURE = 4 - the to measure value
        """
        self.measureD = {}
        self.featureD = {}
        self.routeID=None

        #load data in from the source list.  This list was poplated by the addDataSource method.
        for dsr in self._dataSourceList:
            dsReClose = False #if set to true, call close on the dataSource when done.
            ds = dsr[1]#get the actual dataSource object from the tuple.
            if ds.status() in ("unloaded","closed"):
                ds.refresh()
                dsReClose = True
            #do processing here
            #get a cursor from the dataSource
            c = ds.cursor()
            c.execute()#no filter required.
            columnsAreValid = False #used to skip the column test for subsequent rows, if the first on is okay.
            for dsRecord in c.fetchall():
                #make sure that all of the columns are valid for this dataset, otherwise, break and go to the next one
                if columnsAreValid == False:
                    lastValidatedField = ""
                    try:
                        lastValidatedField =dsr[2][ROUTE_ID]
                        tmp = dsRecord[dsr[2][ROUTE_ID]]

                        lastValidatedField =dsr[2][PRIMARY_KEY]
                        tmp = dsRecord[dsr[2][PRIMARY_KEY]]

                        lastValidatedField =dsr[2][FROM_MEASURE]
                        tmp = dsRecord[dsr[2][FROM_MEASURE]]

                        lastValidatedField =dsr[2][TO_MEASURE]
                        tmp = dsRecord[dsr[2][TO_MEASURE]]
                    except:
                        #one of the specified columns does not exist.
                        self._addErrorToLog("FIELD_DOES_NOT_EXIST","Check the field mapping for this layer, a column is invalid.  This layer will be skipped.(%s) (%s)"%(str(dsr[0]),str(lastValidatedField)),layer=ds)
                        break


                #if this is the route layer (should be the first one) then get the routeid
                #if it is not the route layer, check to see if the routeid matches
                if dsr[0] == 'route':
                    if c.rowcount != 1:
                        raise InvalidRoute("There must be one route, and only one route in the route input.  If you do not want a route in the segmentation, do not specifiy one.")
                    self.routeID = dsRecord[dsr[2][ROUTE_ID]]
                    self.routeFromMeasure = dsRecord[dsr[2][FROM_MEASURE]]
                    self.routeToMeasure = dsRecord[dsr[2][TO_MEASURE]]
                elif dsr[0] != 'route' and self.routeID is not None and self.hasRoute == True:
                    if dsRecord[dsr[2][ROUTE_ID]] is None:
                        #if the specified route_id is required, and is null, raise an error.
                        self._addErrorToLog("NULL_ROUTE_ID","The specified record does not have a route_id.",layer=ds,INPUT_LAYER_COL_NAME=dsr[2][ROUTE_ID],INPUT_LAYER_ID=dsRecord[dsr[2][PRIMARY_KEY]])
                        continue
                    if self.routeID != dsRecord[dsr[2][ROUTE_ID]]:
                        #the routeID of the current record does not match the routeID of the route, so throw an error
                        #and skip this record.
                        self._addErrorToLog("INVALID_ROUTE_ID","The specified record does not have the correct route_id.",layer=ds,INPUT_LAYER_COL_NAME=dsr[2][ROUTE_ID],INPUT_LAYER_ID=dsRecord[dsr[2][PRIMARY_KEY]])
                        continue
                #check for other error conditions:

                #get isNan for from and to measure, this has to be done inside a try/catch block b/c not every data type can be a NAN
                fromMeasureIsNan = False
                toMeasureIsNan = False
                try:
                    fromMeasureIsNan = numpy.isnan(dsRecord[dsr[2][FROM_MEASURE]])
                except:
                    fromMeasureIsNan = False
                try:
                    toMeasureIsNan = numpy.isnan(dsRecord[dsr[2][TO_MEASURE]])
                except:
                    toMeasureIsNan = False


                #make sure both measure values are valid
                if dsRecord[dsr[2][FROM_MEASURE]] in [None] or fromMeasureIsNan:
                    self._addErrorToLog("NULL_FROM_MEASURE","The specified record has a null from_measure field.",layer=ds,INPUT_LAYER_COL_NAME=dsr[2][FROM_MEASURE],INPUT_LAYER_ID=dsRecord[dsr[2][PRIMARY_KEY]])
                    continue
                if dsRecord[dsr[2][TO_MEASURE]] in [None] or toMeasureIsNan:
                    self._addErrorToLog("NULL_TO_MEASURE","The specified record has a null from_measure field.",layer=ds,INPUT_LAYER_COL_NAME=dsr[2][TO_MEASURE],INPUT_LAYER_ID=dsRecord[dsr[2][PRIMARY_KEY]])
                    continue

                #make sure that the measure values are numbers, if they are strings, cast them to numbers
                if py_version<=2:
                    if isinstance(dsRecord[dsr[2][FROM_MEASURE]], (int, long, float, complex)) == False:
                        #it is not a number, so raise an error for this record.
                        self._addErrorToLog("MEASURE_NON_NUMBER","The FROM_MEASURE field must be a number.",layer=ds,INPUT_LAYER_COL_NAME=dsr[2][FROM_MEASURE],INPUT_LAYER_ID=dsRecord[dsr[2][PRIMARY_KEY]])
                        continue
                else:
                    if isinstance(dsRecord[dsr[2][FROM_MEASURE]], (int, float, complex)) == False:
                        # it is not a number, so raise an error for this record.
                        self._addErrorToLog("MEASURE_NON_NUMBER", "The FROM_MEASURE field must be a number.", layer=ds,
                                            INPUT_LAYER_COL_NAME=dsr[2][FROM_MEASURE],
                                            INPUT_LAYER_ID=dsRecord[dsr[2][PRIMARY_KEY]])
                        continue

                #make sure that the measure values are numbers, if they are strings, cast them to numbers
                if py_version<=2:
                    if isinstance(dsRecord[dsr[2][TO_MEASURE]], (int, long, float, complex)) == False:
                        #it is not a number, so raise an error for this record.
                        self._addErrorToLog("MEASURE_NON_NUMBER","The TO_MEASURE field must be a number.",layer=ds,INPUT_LAYER_COL_NAME=dsr[2][TO_MEASURE],INPUT_LAYER_ID=dsRecord[dsr[2][PRIMARY_KEY]])
                        continue
                else:
                    if isinstance(dsRecord[dsr[2][TO_MEASURE]], (int, float, complex)) == False:
                        # it is not a number, so raise an error for this record.
                        self._addErrorToLog("MEASURE_NON_NUMBER", "The TO_MEASURE field must be a number.", layer=ds,
                                            INPUT_LAYER_COL_NAME=dsr[2][TO_MEASURE],
                                            INPUT_LAYER_ID=dsRecord[dsr[2][PRIMARY_KEY]])
                        continue

                #MAKE SURE THE TO MEASURE IS GREATER THAN THE FROM MEASURE
                reverseMeasure = False
                if dsRecord[dsr[2][FROM_MEASURE]] > dsRecord[dsr[2][TO_MEASURE]]:
                    reverseMeasure = True
                    self._addErrorToLog("MEASURE_SWAP","The from measure should be less than or equal to the to measure.  The measures were flipped for segmentation.",layer=ds,INPUT_LAYER_COL_NAME=dsr[2][FROM_MEASURE],INPUT_LAYER_ID=dsRecord[dsr[2][PRIMARY_KEY]])



                #make a new list object with the following items, in order:
                #GUID, DATA SOURCE NAME, PRIMARY KEY VALUE, FROM MEASURE, TO MEASURE
                #Access these later using the key words self._MD_*
                newRow = []
                newRow.append(eaglepy.MakeRandomGUID())
                newRow.append(dsr[0])# the name of the data source
                newRow.append(dsRecord[dsr[2][PRIMARY_KEY]])#the value from the layer that was in the primary key field

                if reverseMeasure:
                    #if reverseMeaseure is true, then the measure values should be stored in reverse order (this means that to measure is less than from measure)
                    newRow.append(dsRecord[dsr[2][TO_MEASURE]])#the value from the layer that was in the to_measure field
                    newRow.append(dsRecord[dsr[2][FROM_MEASURE]])#the value from the layer that was in the from_measure field
                else:
                    newRow.append(dsRecord[dsr[2][FROM_MEASURE]])#the value from the layer that was in the from_measure field
                    newRow.append(dsRecord[dsr[2][TO_MEASURE]])#the value from the layer that was in the to_measure field

                self.featureD[newRow[self._MD_ID]] = newRow #save the record in the featureDictionary, with the GUID as the primary key.

                #check to see if the from measure is in the measureD list
                if (dsRecord[dsr[2][FROM_MEASURE]]) in self.measureD:
                    self.measureD[dsRecord[dsr[2][FROM_MEASURE]]].append(newRow[self._MD_ID]) #save the ID in the existing measure list
                else:
                    self.measureD[dsRecord[dsr[2][FROM_MEASURE]]] = [newRow[self._MD_ID]] # create a new list object, and store the GUID in it.


                #if the to measure is the same as the from measure, then skip the to_measure bit.
                #if reverseMeasure is true (this means it is for sure a linear event, and that the to measure is less than the from measure)
                if dsRecord[dsr[2][FROM_MEASURE]] < dsRecord[dsr[2][TO_MEASURE]] or reverseMeasure:
                    #check to see if the from measure is in the measureD list
                    if (dsRecord[dsr[2][TO_MEASURE]]) in self.measureD:
                        self.measureD[dsRecord[dsr[2][TO_MEASURE]]].append(newRow[self._MD_ID]) #save the ID in the existing measure list
                    else:
                        self.measureD[dsRecord[dsr[2][TO_MEASURE]]] = [newRow[self._MD_ID]] # create a new list object, and store the GUID in it.

                #done getting data from this record, move to the next.

            #close up the dataSource if it started closed.  Leaves the dataSource in the state found. (helps to reduce memory footprint when loading large layers.)
            if dsReClose == True:
                ds.close()

    def _getJsonMetadata(self,layerName):
        """Returns a JSON string (not to exceed 4000 characters) representing the data source in question.
            layerName - a string layerName that is assigned to the layer who's metadata will be returned."""
        data = {}
        dataSource = None
        dataFieldMap = None
        for ds in self._dataSourceList:
            if ds[0] == layerName:
                dataSource = ds[1]
                dataFieldMap = ds[2]
                break
        #if a matching layer could not be found, return an empty string.
        if dataSource is None or dataFieldMap is None:
            return ""

        data["path"] = ""
        if hasattr(dataSource,"_inputTable") == True:
            data["path"] = dataSource._inputTable
        else:
            if hasattr(dataSource,"_source_cursor") == True:
                if dataSource._source_cursor != None:
                    data["path"] = dataSource._source_cursor._dataSource._inputTable

        data["routeIdentifierField"] = dataFieldMap[ROUTE_ID]
        data["fromMeasureField"] = dataFieldMap[FROM_MEASURE]
        data["toMeasureField"] = dataFieldMap[TO_MEASURE]
        data["primaryKeyField"] = dataFieldMap[PRIMARY_KEY]
        data["dataSourceType"] = str(dataSource.__class__.__name__)
        if hasattr(dataSource,"_whereClause"):
            data["whereClause"] = dataSource._whereClause
        else:
            data["whereClause"] = ""
        import json
        return json.JSONEncoder().encode(data)

    def getMeasureRangeTable(self):
        """Returns the segmentation output as an eaglepy.DataSource.Connection.  If the process has not been executed, None is returned."""
        #if execute has not been called, return None.
        if hasattr(self,"measureD") == False:
            self._addWarning("The execute method must be called before calling getMeasureRangeTable()")
            return None

        self._addLog("Starting Creation of Measure Range Table.")
        #convert the internal list into an eaglepy.DataSource object.
        fields=MEASURE_RANGE_TABLE_COLUMNS
        import numpy
        dataTypes = MEASURE_RANGE_TABLE_DATA_TYPES
        primaryKey=MEASURE_RANGE_TABLE_PRIMARY_KEY
        newDataTable = []
        #converts the list of lists to a dictionary for use in the Datasource.
        self._addLog("Exporting data to measureRangeConnection")
        for aRow in self.measureRangeOutput:
            #each aRow contains: rangeGUID, FromMeasure, ToMeasure, GUID (unique ID of the feature, not the measure range record)
            newRow = {}
            if hasattr(self,"routeID"):
                newRow["ROUTE_ID"] = self.routeID
            else:
                newRow["ROUTE_ID"] = None

            #if there is no data layer here, this is a true gap, then layer_name and primary key are blank.
            try:
                newRow["LAYER_NAME"] = self.featureD[aRow[3]][self._MD_LAYER_NAME]
                newRow["LAYER_PRIMARY_KEY"] = self.featureD[aRow[3]][self._MD_PRIMARY_KEY_VALUE]
            except KeyError:
                newRow["LAYER_NAME"] = ""
                newRow["LAYER_PRIMARY_KEY"] = ""

            newRow["MEAS_RANGE_ID"] = eaglepy.MakeRandomGUID()
            newRow["SEGMENT_ID"] = aRow[0]
            newRow["FEATURE_ID"] = aRow[3]
            newRow["METADATA"] = self._getJsonMetadata(newRow["LAYER_NAME"])
            newRow["FROM_MEASURE"] = aRow[1]
            newRow["TO_MEASURE"] = aRow[2]
            newRow["GAP_INDICATOR"] = aRow[4]
            newDataTable.append(newRow)

        self._addLog("Export Complete, building Connection.")
        conn = eaglepy.DataSource.connect("ConnectionEsriEdit",fieldNames=fields,primaryKey=primaryKey,dataTable=newDataTable,fieldDataTypes=dataTypes)
        self._addLog("Measure Range Table Creating Complete.")
        return conn

    def getMeasureRangeTableBatch(self):
        """Returns the segmentation output as an eaglepy.DataSource.Connection.  If the process has not been executed, None is returned."""
        # if execute has not been called, return None. created to process 100000 records each time
        if hasattr(self, "measureD") == False:
            self._addWarning("The execute method must be called before calling getMeasureRangeTable()")
            return None

        # convert the internal list into an eaglepy.DataSource object.
        fields = MEASURE_RANGE_TABLE_COLUMNS
        import numpy
        dataTypes = MEASURE_RANGE_TABLE_DATA_TYPES
        primaryKey = MEASURE_RANGE_TABLE_PRIMARY_KEY
        newDataTable = []
        # converts the list of lists to a dictionary for use in the Datasource.
        #self._addLog("Exporting data to measureRangeConnection")
        for aRow in self.measureRangeOutput:
            # each aRow contains: rangeGUID, FromMeasure, ToMeasure, GUID (unique ID of the feature, not the measure range record)
            newRow = {}
            if hasattr(self, "routeID"):
                newRow["ROUTE_ID"] = self.routeID
            else:
                newRow["ROUTE_ID"] = None

            # if there is no data layer here, this is a true gap, then layer_name and primary key are blank.
            try:
                newRow["LAYER_NAME"] = self.featureD[aRow[3]][self._MD_LAYER_NAME]
                newRow["LAYER_PRIMARY_KEY"] = self.featureD[aRow[3]][self._MD_PRIMARY_KEY_VALUE]
            except KeyError:
                newRow["LAYER_NAME"] = ""
                newRow["LAYER_PRIMARY_KEY"] = ""

            newRow["MEAS_RANGE_ID"] = eaglepy.MakeRandomGUID()
            newRow["SEGMENT_ID"] = aRow[0]
            newRow["FEATURE_ID"] = aRow[3]
            newRow["METADATA"] = self._getJsonMetadata(newRow["LAYER_NAME"])
            newRow["FROM_MEASURE"] = aRow[1]
            newRow["TO_MEASURE"] = aRow[2]
            newRow["GAP_INDICATOR"] = aRow[4]
            newDataTable.append(newRow)

        #self._addLog("Export Complete, building Connection.")
        conn = eaglepy.DataSource.connect("ConnectionEsriEdit", fieldNames=fields, primaryKey=primaryKey,
                                          dataTable=newDataTable, fieldDataTypes=dataTypes)
        #self._addLog("Measure Range Table Creating Complete.")
        return conn

    def segment_getGapCode(self, validListOfFeatures, beginMeasure, endMeasure):
        return self._segment_getGapCode(validListOfFeatures, beginMeasure, endMeasure)

    def segment_ifPointsExist(self,possibleList):
        return self._segment_ifPointsExist(possibleList)

    def segment_testPoints(self, possibleList, beginMeasure):
        return self._segment_testPoints(possibleList, beginMeasure)

    def segment_testLines(self, possibleList, beginMeasure, endMeasure):
        return self._segment_testLines(possibleList, beginMeasure, endMeasure)



class SegmentorMultiRoute(WhenToWriteMixin, _BaseSegmentation):
    def __init__(self, routeDataSource, routeFieldMap, **kwargs):
        """Creates a new SegmentorMultiRoute class.
        This automatically handles segmenting when the data sources contain multiple routes.  Each data source will be pulled apart, and updated
        so that the appropriate whereClause attribute is set, only allowing data for the specified route to be queried.
        When calling this, you should always set autoLoad=False on the connection objects, this prevents them from loading into memory until needed.

            routeDataSource - An eaglepy.DataSource.Connection that representes the single route record for this segmentation (required)
            routeFieldMap - A dictionary that maps required fields to the actual fields in the routeDataSource (required).
                routeID - The route identifier field for the dataSource
                primaryKey - The primary key column for the dataSource (Must be the same as routeID)
                fromMeasure - The from measure field of the dataSource
                toMeasure - The to measure field of the dataSource
        """
        _BaseSegmentation.__init__(self)
        self._routeDataSource = routeDataSource
        self._routeFieldMap = routeFieldMap
        self.measureRangeOutput = []
        self._dataSourceList = []
        self._addLog("Initializing MultiRoute Segmentor.")
        if validateFieldMap(routeFieldMap) == False:
            raise InvalidFieldMap("The route field map was invalid.")
        #repair the fields that are in the field map to have the correct case.
        for key,field in self._routeFieldMap.items():
            self._routeFieldMap[key] = self._routeDataSource.repairField(field)

    def addDataSource(self,name,dataSource,fieldMap):
        """Adds the specified dataSource to the list of things to segment.  The dataSources must already be filtered for the route in question.
            name - The user specified name of the dataSource, this must be unique
            dataSource - an eaglepy.DataSource.Connection object that points to the datasourece to segment.
            fieldMap - A dictionary that maps the columns this tool looks for to the columns in the dataSource.
                    routeID - The route identifier field for the dataSource
                    primaryKey - The primary key column for the dataSource
                    fromMeasure - The from measure field of the dataSource
                    toMeasure - The to measure field of the dataSource"""
        if validateFieldMap(fieldMap):
            #repair the fields in the fieldMap to make sure they have the correct case
            for key,field in fieldMap.items():
                fieldMap[key] = dataSource.repairField(field)
            self._dataSourceList.append((name,dataSource,fieldMap))
            self._addLog("Adding Data Source (%s)"%(name))
        else:
            raise InvalidFieldMap("The specified field map for %s was invalid."%(name),str(fieldMap))

    def execute(self):
        """Executes a segmentor object for each route found in the route input connection"""
        #get the unique list of routes
        self._routeDataSource.refresh()
        rCursor = self._routeDataSource.cursor()
        rCursor.execute()
        routeList = [row[self._routeFieldMap[ROUTE_ID]] for row in rCursor.fetchall()]
        routeList = list(set(routeList))
        routeCount = 0
        routeTotal = len(routeList)
        rCursor.close()
        for aRoute in routeList:
            routeCount += 1
            self._addLog("**** Executing Segmentation for route: %s (%s of %s)"%(aRoute,routeCount,routeTotal))

            tmpRouteCur = self._routeDataSource.cursor()
            tmpRouteCur.execute("select",whereClause=[(self._routeFieldMap[ROUTE_ID],aRoute)])
            routeDS = eaglepy.DataSource.ConnectionEsriEdit(cursor=tmpRouteCur)
            #create the segmentor
            routeSegmentor = Segmentor(routeDS,self._routeFieldMap)

            #load all of the data sources, if they are not loaded
            for aLayer in self._dataSourceList:
                if aLayer[1].status() in ("unloaded","closed"):
                    aLayer[1].refresh()

            #create a new data source for each dataSource that was passed in.
            tmpDataSourceList = []
            for newLayer in self._dataSourceList:


                tmpLayerCur = newLayer[1].cursor()
                tmpLayerCur.execute("select",whereClause=[(newLayer[2][ROUTE_ID],aRoute)])
                newLayerDS = eaglepy.DataSource.ConnectionEsriEdit(cursor=tmpLayerCur)

                routeSegmentor.addDataSource(newLayer[0],newLayerDS,newLayer[2])
                tmpDataSourceList.append(newLayerDS)

            #execute the segmentor, if an error occurs during segmentation, ignore it.
            #the segmentor class will have delt with the error and this should move onto the next route.
            try:
                routeSegmentor.executeGetFeatureDataBatch()
                routeSegmentor.measureRangeOutput = []
                previousSegmentList = []
                if py_version <= 2:
                    measureList = routeSegmentor.measureD.keys()
                else:
                    measureList = list(routeSegmentor.measureD.keys())
                measureList.sort()
                processedRecordCount=0
                """Segments the data from self.measureD and self.featureD, as created by _getFeatureData()"""
                previousSegmentList = []
                self._addLog("Segmentation Process - processing and saving data to output table....")
                for measureIndex in range(len(measureList)):
                    # first look for point features, that is features that start and end at the same measure value
                    beginMeasure = measureList[measureIndex]
                    endMeasure = measureList[measureIndex]
                    # get the list of feature GUIDs as a combination of all features from the previous segment,
                    # and all features that start at beginMeasure
                    possibleFeatureList = previousSegmentList + routeSegmentor.measureD[beginMeasure]
                    possibleFeatureList = list(set(possibleFeatureList))  # removes duplicates from the list.

                    # reset the previousSegmentList
                    previousSegmentList = []

                    # test the points
                    if routeSegmentor.segment_ifPointsExist(possibleFeatureList):
                        validListOfFeatures = routeSegmentor.segment_testPoints(possibleFeatureList, beginMeasure)
                        # save the valid list in the previousSegmentList
                        previousSegmentList = previousSegmentList + validListOfFeatures

                        # store each valid feature in the measureRangeOutput variable as an array
                        # each array contains rangeGUID, FromMeasure, ToMeasure, GUID where GUID represents the key of the feature that is valid here.
                        # rangeGUID is a guid that is unique for each FromMeasure, ToMeasure combination
                        rangeGUID = eaglepy.MakeRandomGUID()
                        # check to see if there is a route, if there is check to see if any of the special codes apply to the results.
                        gapCode = routeSegmentor.segment_getGapCode(validListOfFeatures, beginMeasure, endMeasure)
                        # save each item in validListOfFeatures
                        for feat in validListOfFeatures:
                            newRecord = []
                            newRecord.append(rangeGUID)
                            newRecord.append(beginMeasure)
                            newRecord.append(endMeasure)
                            newRecord.append(feat)
                            newRecord.append(gapCode)
                            routeSegmentor.measureRangeOutput.append(newRecord)

                        # if there is nothing in the validList OfFeatures, then we still need to output something
                        if len(validListOfFeatures) == 0:
                            newRecord = []
                            newRecord.append(rangeGUID)
                            newRecord.append(beginMeasure)
                            newRecord.append(endMeasure)
                            newRecord.append("")
                            newRecord.append(gapCode)
                            routeSegmentor.measureRangeOutput.append(newRecord)

                    # now take a look at linear features, that is features that have start and end measure values that are different
                    # check to see if we are at the end of the list:
                    if measureIndex + 1 == len(measureList):
                        continue  # we are at the end, so go to the next part of the loop
                    endMeasure = measureList[measureIndex + 1]

                    validListOfFeatures = routeSegmentor.segment_testLines(possibleFeatureList, beginMeasure, endMeasure)

                    # save the valid list in the previousSegmentList
                    previousSegmentList = []
                    previousSegmentList = previousSegmentList + validListOfFeatures

                    # save all of the valid features, in the same format as the points.
                    rangeGUID = eaglepy.MakeRandomGUID()
                    # check to see if there is a route, if there is check to see if any of the special codes apply to the results.
                    gapCode = routeSegmentor.segment_getGapCode(validListOfFeatures, beginMeasure, endMeasure)
                    for feat in validListOfFeatures:
                        newRecord = []
                        newRecord.append(rangeGUID)
                        newRecord.append(beginMeasure)
                        newRecord.append(endMeasure)
                        newRecord.append(feat)
                        newRecord.append(gapCode)  # place holder for gap_indicator flag.
                        routeSegmentor.measureRangeOutput.append(newRecord)

                    # if there is nothing in the validList OfFeatures, then we still need to output something
                    if len(validListOfFeatures) == 0:
                        newRecord = []
                        newRecord.append(rangeGUID)
                        newRecord.append(beginMeasure)
                        newRecord.append(endMeasure)
                        newRecord.append("")
                        newRecord.append(gapCode)
                        routeSegmentor.measureRangeOutput.append(newRecord)


                    if len(routeSegmentor.measureRangeOutput) >=200000:
                        # save the measure Range output
                        processedRecordCount=processedRecordCount+len(routeSegmentor.measureRangeOutput)
                        self.processBatchAndWriteToDisk(routeSegmentor)
                        self._addLog("Processed {0} records".format(processedRecordCount))

                # if routeSegmentor.measureRangeOutput < 200000 then data will ger processed here
                if len(routeSegmentor.measureRangeOutput) < 200000:
                    processedRecordCount = processedRecordCount + len(routeSegmentor.measureRangeOutput)
                    self.processBatchAndWriteToDisk(routeSegmentor)
                    self._addLog("Processed {0} records".format(processedRecordCount))

                ## close and delete all the data sources
                for ds in tmpDataSourceList:
                    ds.close()
                del tmpDataSourceList
                routeDS.close()
                del routeDS
                self._addLog("Process compeleted")
            except Exception as e:
                self._addError("An error occured while executing the segmentor.")
                self._addError(str(e))

        ## The process has completed, force a write to disk
        # self.writeToDisk(force=True)

        return  # return at the end of the execute method.

    def processBatchAndWriteToDisk(self,routeSegmentor=None):
        """
        This is created for process data returned from  routeSegmentor.getMeasureRangeTable() and write to disk
        @param routeSegmentor:
        @return:
        """
        mrtConn = routeSegmentor.getMeasureRangeTableBatch()
        mrtC = mrtConn.cursor()
        mrtC.execute()
        self.measureRangeOutput = []
        for aRow in mrtC.fetchall():
            self.measureRangeOutput.append(aRow)
        mrtC.close()
        del mrtC
        mrtConn.close()
        del mrtConn

        ## save the error table output
        errtConn = routeSegmentor.getErrorTable()
        errtC = errtConn.cursor()
        errtC.execute()
        for aRow in errtC.fetchall():
            self.errorOutput.append(aRow)
        errtC.close()
        del errtC
        errtConn.close()
        del errtConn
        routeSegmentor.measureRangeOutput = []
        ## save to disk, if enabled
        self.writeToDisk(force=True)


    def getMeasureRangeTable(self):
        """Returns the segmentation measure range table as an eaglepy.DataSource.Connection."""
        #if execute has not been called, return None.
        self._addLog("Starting Creation of Measure Range Table.")
        fields = MEASURE_RANGE_TABLE_COLUMNS
        dataTypes=MEASURE_RANGE_TABLE_DATA_TYPES
        primaryKey=MEASURE_RANGE_TABLE_PRIMARY_KEY
        conn = eaglepy.DataSource.connect("ConnectionEsriEdit",fieldNames=fields,primaryKey=primaryKey,dataTable=self.measureRangeOutput,fieldDataTypes=dataTypes)
        self._addLog("Measure Range Table Creation Complete.")
        return conn

class Attributer(WhenToWriteMixin, _BaseSegmentation):
    """Using a dynamic segmentation output from the Dynamic
        Segmentation All tool, this tool will retrieve attribution for each layer
        as specified in the input. The output from this tool will be in the form
        of two tables, one table will contain the same output as the Dynamic
        Segmentation All tool with additional columns containing attribution
        from the input layers, the second table will contain errors encountered
        during the process."""

    def __init__(self, measureRangeTable):
        """Creats an instance of the Attributer Class that will create a new output containing attribution from the original data soruces.

                measureRangeTable - Required - An eaglepy.DataSource object that connects to the measureRangeTable that should be operated on."""
        #set defaults
        _BaseSegmentation.__init__(self)
        self._measureRangeTable = None
        self._addLog("Initializing Attributer")

        #get parameters
        self._measureRangeTable = measureRangeTable
        self._outputAttributeMeasureRangeTable = []
        if self._measureRangeTable.status() != "open":
            self._measureRangeTable.refresh()

        #creates a dictionary where each key is a layer name and the value is a dictionary.
        #   the value dictionary has a key that represents the output column name and a value that represents the source column name
        self._layerColumnMap = {}

        # the list of all layers that are present in the specified measure range table.
        self._fullLayerList = []

        # the dictionary of column name and data type
        self._outputColumns = dict(zip(MEASURE_RANGE_TABLE_COLUMNS,MEASURE_RANGE_TABLE_DATA_TYPES))

    def addOutputColumn(self,layerName,outputColumnName,sourceColumnName):
        """Adds the specified output column to source column mapping.  The specified outputColumn will be present in the output.
            layerName - The name of the layer.  this must match the name specified in the segmentation input.
            outputColumnName - The name of the column in the output of this process.  You should try to make this unique, but that is not a requirment.
            sourceColumnName - The name of the column in the source layer that should be mapped to be outputed in the outputColumnName"""
        layerColumns = {}
        if layerName in self._layerColumnMap.keys():
            layerColumns = self._layerColumnMap[layerName]

        layerColumns[outputColumnName] = sourceColumnName

        self._layerColumnMap[layerName] = layerColumns

    def _getSourceLayerData(self):
        """Returns a dictionary where the key is the layer name, and the value is a second dictionary.
            The second dictionary contains metadata about the layer:
                path - The path to the data source.
                dataSourceType - The class name that was used to extract the data originally
                primaryKeyField - the primary key of the table
                columns - a list of all columns that should be extracted by the query."""
        #get the distinct list of input layers
        mrtC = self._measureRangeTable.cursor()
        mrtC.execute()
        layerNameList = [row["LAYER_NAME"] for row in mrtC.fetchall()]
        layerNameList = set(layerNameList)
        self._fullLayerList = layerNameList
        #reduce the items in layerNameList so that only layers that have mapped data remain
        #this prevents us from quering a layer that we don't actually need
        newLayerNameList = []
        for item in layerNameList:
            if item in self._layerColumnMap.keys():
                newLayerNameList.append(item)
        layerNameList = newLayerNameList

        #create a dictionary that represents the data sources, the key is the layer name, the value is a dictionary
        #   the value dictionary contains, path, dataSourceType, primaryKeyField,whereClause,columns, where columns is the list of columns to be extracted.
        layerSourceData = {}
        for item in layerNameList:
            #get the layer metadata from a cursor
            layerMDCursor = self._measureRangeTable.cursor()
            layerMDCursor.execute("select",whereClause=[('LAYER_NAME',item)])
            layerMetaData = json.JSONDecoder().decode(layerMDCursor.fetchall()[0]['METADATA'])
            newData = {}
            newData["path"] = layerMetaData["path"]
            newData["dataSourceType"] = layerMetaData["dataSourceType"]
            newData["primaryKeyField"] = layerMetaData["primaryKeyField"]
            newData["whereClause"] = layerMetaData["whereClause"]
            newData["columns"] = [layerMetaData["primaryKeyField"],layerMetaData["routeIdentifierField"],layerMetaData["fromMeasureField"]]
            if layerMetaData["fromMeasureField"] != layerMetaData["toMeasureField"]:
                newData["columns"].append(layerMetaData["toMeasureField"])
            #get columns from the _layerColumnMap
            if item not in self._layerColumnMap:
                layerSourceData[item] = newData
                continue
            for extraColumn in self._layerColumnMap[item].values():
                if extraColumn not in newData["columns"]:
                    newData["columns"].append(extraColumn)

            layerSourceData[item] = newData
        return layerSourceData

    def _getLayerConnection(self,layer):
        """returns a connection object for the layer in question.  The layer must be a dictionary from the value of the layerSourceData dictionary in execute."""
        minConn = eaglepy.DataSource.connect("ConnectionEsriDA", inputTable=layer["path"], fieldNames=list(set(layer["columns"])), whereClause="", primaryKey=layer["primaryKeyField"], autoLoad=True)
        return eaglepy.DataSource.ConnectionEsriEdit(connection=minConn)


    def _getBlankOutputRow(self):
        newOutput = {}
        newOutput["ROUTE_ID"] = None
        newOutput["MEAS_RANGE_ID"] = None
        newOutput["SEGMENT_ID"] = None
        newOutput["FEATURE_ID"] = None
        newOutput["LAYER_NAME"] = None
        newOutput["LAYER_PRIMARY_KEY"] = None
        newOutput["METADATA"] = None
        newOutput["FROM_MEASURE"] = None
        newOutput["TO_MEASURE"] = None
        newOutput["GAP_INDICATOR"] = None

        #extrat the new output columns from the metedata
        for layerColumns in self._layerColumnMap.values():
            #loop over the keys in the dictionary to get the extra column names to add
            for outputColumn in layerColumns.keys():
                if outputColumn not in newOutput.keys():
                    newOutput[outputColumn] = None
        return newOutput

    def execute(self):
        """Execute the append attributes process.  This method returns when the process is complete."""
        self._outputAttributeMeasureRangeTable = []
        #get the list of layers, and the source data that goes along with them.
        layerSourceData = self._getSourceLayerData()
        #for each layer, make a connection using the orignal information
        for currLayerName,currLayer in layerSourceData.items():
            self._addLog("Extracting data for %s"%(currLayerName))
            currLayerConn = None
            try:
                currLayerConn = self._getLayerConnection(currLayer)
            except Exception as e:
                self._addError("Unable to load layer: %s."%(currLayerName))
                self._addError(str(e))
                self._addError(traceback.format_exc())
                self._addErrorToLog("LAYER_COULD_NOT_LOAD", errorDescription=str(e),INPUT_LAYER=currLayer["path"])
                continue
            #find all records in the measure range table that are connected to this layer, and start updating the columns.
            mrtCursor = self._measureRangeTable.cursor()
            mrtCursor.execute("select",[("LAYER_NAME",currLayerName)])
            #get the unique set of primary key values out of the measure range table.
            primaryKeyList = [ row["LAYER_PRIMARY_KEY"] for row in mrtCursor.fetchall() ]
            primaryKeyList = set(primaryKeyList)
            mrtCursor.close()
            del mrtCursor

            #########
            ## Extracts the data required for each primary key value and saves it in a dictionary where the key is the primary key value
            ## and the value is a dictionary representing the column comming from this layer.
            #########
            primaryKeyData = {}
            #for each primaryKeyValue, query the connection and get the attributes required.
            for primaryKeyValue in primaryKeyList:
                pkCur = currLayerConn.cursor()
                tmpPKValue = eaglepy.DataSource.castValueToColumnType(primaryKeyValue,
                                                                      currLayer["primaryKeyField"],
                                                                      pkCur)
                pkCur.execute("select", [ (currLayer["primaryKeyField"], tmpPKValue) ])
                newOutput= self._getBlankOutputRow()
                currColumnMap = self._layerColumnMap[currLayerName]
                if pkCur.rowcount != 1:
                    self._addError("Invalid number of rows found in source layer %s for primary key value %s"%(currLayerName,primaryKeyValue))
                    self._addErrorToLog("TOO_MANY_FEW_RECORDS", errorDescription="Too many (or too few) records exist for the specified primary key value.  There should be one.",INPUT_LAYER=currLayer["path"],INPUT_LAYER_ID=primaryKeyValue)
                for singleRow in pkCur.fetchall():
                    for outCol,sourceCol in currColumnMap.items():
                        newOutput[outCol] = singleRow[sourceCol]
                        self._outputColumns[outCol] = eaglepy.DataSource.getDataTypeForColumn(sourceCol,pkCur)
                primaryKeyData[primaryKeyValue] = newOutput

            ############
            ## Loop through each record in the MRT that has this source layer in it, set the columns, and save it in the output array
            ############
            mrtCursor = self._measureRangeTable.cursor()
            mrtCursor.execute("select",[("LAYER_NAME",currLayerName)])
            for aRow in mrtCursor.fetchall():
                newData = {}
                newData = primaryKeyData.get(aRow["LAYER_PRIMARY_KEY"], self._getBlankOutputRow())
                #extract the columns from the measure range record
                for key,value in aRow.items():
                    newData[key] = value
                self._outputAttributeMeasureRangeTable.append(copy.deepcopy(newData))
                self.writeToDisk()
            mrtCursor.close()
            del mrtCursor

        #loop though all layers that are present, but are not pulling attributes
        missingLayers = set(self._fullLayerList) - set(layerSourceData.keys())
        for aLayer in missingLayers:
            #open a cursor for each missing layer, and get the data
            mrtCursor = self._measureRangeTable.cursor()
            mrtCursor.execute("select",[("LAYER_NAME",aLayer)])
            for aRow in mrtCursor.fetchall():
                newData = {}
                newData = self._getBlankOutputRow()
                #extract the columns from the measure range record
                for key,value in aRow.items():
                    newData[key] = value
                self._outputAttributeMeasureRangeTable.append(copy.deepcopy(newData))
                self.writeToDisk()
            mrtCursor.close()
            del mrtCursor

        self.writeToDisk(force=True)




    def getAttributedMeasureRangeTable(self):
        if hasattr(self,"_outputAttributeMeasureRangeTable") == False:
            self._addWarning("The execute method must be called before calling getMeasureRangeTable()")
            return None
        self._addLog("Starting Creation of Attributed Measure Range Table")
        fields = self._outputColumns.keys()
        dataTypes = self._outputColumns.values()
        primaryKey = MEASURE_RANGE_TABLE_PRIMARY_KEY
        newDataTable = self._outputAttributeMeasureRangeTable

        self._addLog("Export Complete, building Connection.")
        conn = eaglepy.DataSource.connect("ConnectionEsriEdit",fieldNames=fields,primaryKey=primaryKey,dataTable=newDataTable,fieldDataTypes=dataTypes)
        self._addLog("Measure Range Table Creating Complete.")
        return conn

class _BaseStatistics(_BaseSegmentation):
    import eaglepy.lr.segmentation.calculation

    def _resolveCalculation(self,calculation):
        return eaglepy.lr.segmentation.calculation.ResolveCalculation(calculation)
        ##Moved to eaglepy.lr.segmentation.calculation.ResolveCalculation

    def _resolveImportForCalculation(self,calculation):
        return eaglepy.lr.segmentation.calculation.ResolveImportForCalculation(calculation)
        ##Moved to eaglepy.lr.segmentation.calculation.ResolveImportForCalculation


class Statistics(WhenToWriteMixin, _BaseStatistics):
    """Calculates statistics on the input table, using the groupByColumnName to first group the input into smaller segments,
    to which the statistics are calculated.
    Use addOutputColumn to add a calculation to the output.
    call execute() to run the calculations
    call getStatisticsOutputTable() to get an eaglepy.DataSource object that represents the output."""
    def __init__(self, inputTable, groupByColumnName):
        """Creates a statistics object
            inputTable - An eaglepy.DataSource object that refrences the source table
            grouByColumnName - a column in inputTable that will be used to group the inputs for calculations
        """
        _BaseStatistics.__init__(self)
        self._inputTable = inputTable
        self._groupByColumnName = groupByColumnName
        self._groupByColumnName = self._inputTable.repairField(self._groupByColumnName)
        self._outputColumns = OrderedDict()

    def addOutputColumn(self, outputColumnName, calculation):
        """Adds an output column to the output table.
            outputColumnName - The name of the column in the output table, must be unique
            calculation - A string that represents the calculation library that will be used, and the inputs for that calc.
        """
        lowerList = [ col.lower() for col in self._outputColumns.keys() ]
        if outputColumnName.lower() in lowerList:
            raise DuplicateOutputColumn("The column %s has already been specified."%(outputColumnName))
        newCalculation = self._resolveCalculation(calculation)
        if newCalculation == False:
            raise InvalidCalculationType("The calculation %s is invalid or could not be found."%(calculation))
        self._outputColumns[outputColumnName] = newCalculation

    def _getBlankOutputRow(self):
        """Returns a dictionary object where the keys are the columns that are outputed, and the values
        are None.  Every column that will be included in the output is returned by this function."""
        tmp = {}
        for key in self._outputColumns:
            tmp[key] = None
        return tmp


##TODO: refactor execute so that it opens a cursor on the input layer, and grabs
    ##about 100,000 records while ensuring complete segments.  This will require that
    ##we order by the segment id in the native esri cursor, somehow...
    ##the resulting data set can then be passed into a new function that will actually do the
    ##stat calcs.  The write to disk function should continue to be used as it is today.

    def _calcStats(self, data=list(), groupByValue=None):
        self._addLog("Calculating Statistics")
        newData = [self._getBlankOutputRow()]
        for colName, calcString in self._outputColumns.items():
            try:
                calcObject = eval(calcString)
                colValue = calcObject.execute()
                newData[0][colName] = colValue
                self._outputDataTypes[colName] = calcObject.getDataType()
            except Exception as e:
                self._addWarning("An error was encountered while calculating {0} for {1}".format(colName,
                                                                                                 groupByValue))
                self._addErrorToLog("COULD_NOT_CALCULATE_OUTPUT",
                                    str(e),
                                    INPUT_LAYER_COL_NAME=colName,
                                    INPUT_LAYER_ID=groupByValue)
        newData[0][self._groupByColumnName] = groupByValue
        self._outputData.append(copy.deepcopy(newData[0]))
        del newData

    def _executeGroupBy(self, processingData=list()):
        self._addLog("Grouping Data")
        previousGroupByValue = None
        currentGroupByValue = None
        data = list()
        for aRow in processingData:
            currentGroupByValue = aRow[self._groupByColumnName]
            if previousGroupByValue is None:
                previousGroupByValue = currentGroupByValue

            if currentGroupByValue == previousGroupByValue:
                ## If the previous value and the same value are the same, then add the row to the data variable.
                data.append(aRow)

            if currentGroupByValue != previousGroupByValue:
                self._calcStats(data=data, groupByValue=previousGroupByValue)
                self.writeToDisk()
                self._addLog("Grouping Data")
                del data
                data = list()
                data.append(aRow)
                previousGroupByValue = currentGroupByValue

        if len(data) > 0:
            self._calcStats(data, groupByValue=previousGroupByValue)
            self.writeToDisk()

    def execute(self):
        self._addLog("Begin Statistics")
        self._outputData = list()
        processingList = list()
        self._addLog("Begin Statistics2")
        #create default output data type columns.
        self._outputDataTypes = self._getBlankOutputRow()
        for key, value in self._outputDataTypes.items():
            self._outputDataTypes[key] = "STRING"
        self._addLog("Begin Statistics3")
        ## override the order by statement
        self._inputTable._orderby = "{} ASC".format(self._groupByColumnName)
        self._inputTable.refresh()
        self._addLog("Begin Statistics4")
        dataCur = self._inputTable.cursor()
        self._addLog("Begin Statistics5")
        dataCur.execute()
        self._addLog("Begin Statistics6")
        currUniqueValue = None
        prevUniqueValue = None
        self._addLog("Loading Data")
        for inputRow in dataCur.fetchall():
            #get the current group by value
            currUniqueValue = inputRow[self._groupByColumnName]
            if prevUniqueValue is None:
                prevUniqueValue = inputRow[self._groupByColumnName]

            if currUniqueValue == prevUniqueValue:
                ## if the current group by value is the same as the previous value then
                ## we always want to add this record to the processing list.
                processingList.append(inputRow)
            else:
                self._calcStats(data=processingList, groupByValue=prevUniqueValue)
                self.writeToDisk()
                del processingList
                processingList = list()
                processingList.append(inputRow)
                prevUniqueValue = inputRow[self._groupByColumnName]

        if len(processingList) > 0:
            ## there are items left in the processing list, so go ahead and run them.
            self._calcStats(data=processingList, groupByValue=prevUniqueValue)

        dataCur.close()
        del dataCur

        self.writeToDisk(force=True)
        self._addLog("Statistics Complete")
        return

    def execute2(self):
        self._addLog("Begin StatisticsAAAAAAA")
        self._outputData = list()
        processingList = list()
        maxProcessingListLength = 25000
        self._addLog("Begin Statistics2")
        #create default output data type columns.
        self._outputDataTypes = self._getBlankOutputRow()
        for key, value in self._outputDataTypes.items():
            self._outputDataTypes[key] = "STRING"
        self._addLog("Begin Statistics3")
        ## override the order by statement
        self._inputTable._orderby = "{} ASC".format(self._groupByColumnName)
        self._inputTable.refresh()
        self._addLog("Begin Statistics4")
        dataCur = self._inputTable.cursor()
        self._addLog("Begin Statistics5")
        dataCur.execute()
        self._addLog("Begin Statistics6")
        currUniqueValue = None
        prevUniqueValue = None
        self._addLog("Loading Data")
        for inputRow in dataCur.fetchall():
            #get the current group by value
            currUniqueValue = inputRow[self._groupByColumnName]
            if prevUniqueValue is None:
                prevUniqueValue = inputRow[self._groupByColumnName]

            if currUniqueValue == prevUniqueValue:
                ## if the current group by value is the same as the previous value then
                ## we always want to add this record to the processing list.
                processingList.append(inputRow)
            elif len(processingList) < maxProcessingListLength:
                ## if the curr and previous values are different and there is still room in the
                ## processing list, then add it to the list, and reset the prev value.
                processingList.append(inputRow)
                prevUniqueValue = inputRow[self._groupByColumnName]
            elif len(processingList) >= maxProcessingListLength:
                ## if the curr and previous values are different and there is no room left in the
                ## processing list, then send it for processing and then reset for the next
                ## set of data.
                self._executeGroupBy(processingList)
                self._addLog("Loading Data")
                del processingList
                processingList = list()
                processingList.append(inputRow)
                prevUniqueValue = inputRow[self._groupByColumnName]
        ## end of for loop
        if len(processingList) > 0:
            ## there are items left in the processing list, so go ahead and run them.
            self._executeGroupBy(processingList)

        dataCur.close()
        del dataCur

        self.writeToDisk(force=True)
        self._addLog("Statistics Complete")
        return

    def getStatisticsOutputTable(self):
        if hasattr(self,"_outputData") == False:
            self._addWarning("The execute method must be called before calling getMeasureRangeTable()")
            return None
        self._addLog("Starting Creation of Statistics Output Table")
        fields = self._outputDataTypes.keys()
        dataTypes = self._outputDataTypes.values()
        primaryKey = self._groupByColumnName
        newDataTable = self._outputData

        self._addLog("Export Complete, building Connection.")
        conn = eaglepy.DataSource.connect("ConnectionEsriEdit",fieldNames=fields,primaryKey=primaryKey,dataTable=newDataTable,fieldDataTypes=dataTypes)
        self._addLog("Statistics Output Table Creating Complete.")
        return conn


class Dissolverator(WhenToWriteMixin, _BaseStatistics):
    """Dissolves linear data with similar attributes into single records.  Searches the input data set in groups
    using the groupByColumnName for sequential records that have no changes in the data stored in the column specified
    by the addDissolveColumn method.  These records are combined together to make a single record that contains the dissolve
    columns and any calculated columns specified by addCalculatedColumn."""

    def __init__(self, inputTable, groupByColumnName,orderByColumnName,beginMeasureColumnName,endMeasureColumnName):
        _BaseStatistics.__init__(self)
        self._inputTable = inputTable
        self._groupByColumnName = groupByColumnName
        self._groupByColumnName = self._inputTable.repairField(self._groupByColumnName)

        self._orderByColumnName = orderByColumnName
        self._orderByColumnName = self._inputTable.repairField(self._orderByColumnName)

        self._beginMeasureColumnName = beginMeasureColumnName
        self._beginMeasureColumnName = self._inputTable.repairField(self._beginMeasureColumnName)

        self._endMeasureColumnName = endMeasureColumnName
        self._endMeasureColumnName = self._inputTable.repairField(self._endMeasureColumnName)

        self._dissolveColumns = []
        self._outputColumns = {}
        self._outputDataTypes = {}
        self._defaultCalculation = ""
        #self.addCalculationColumn(self._groupByColumnName,self._defaultCalculation)
        #self.addCalculationColumn(self._orderByColumnName,self._defaultCalculation)
        #self.addCalculationColumn(self._beginMeasureColumnName,self._defaultCalculation)
        #self.addCalculationColumn(self._endMeasureColumnName,self._defaultCalculation)


    def addDissolveColumn(self,columnName):
        """Adds a dissolve column to the process.  These columns will also be present in the output.
            columnName - The name of the column in the inputTable that should be dissolved upon."""
        lowerList = [ col.lower() for col in self._dissolveColumns ]
        lowerOutputList =[ col.lower() for col in self._outputColumns.keys() ]
        if columnName.lower() in lowerList or columnName.lower() in lowerOutputList:
            raise DuplicateOutputColumn("The column %s has already been specified."%(columnName))

        tmpColumnName = self._inputTable.repairField(columnName)
        self._dissolveColumns.append(tmpColumnName)


    def addCalculationColumn(self,outputColumnName,calculation):
        """Adds an output column to the output table.
            outputColumnName - The name of the column in the output table, must be unique
            calculation - A string that represents the calculation library that will be used, and the inputs for that calc.
        """
        lowerList =[ col.lower() for col in self._outputColumns.keys() ]
        if outputColumnName.lower() in lowerList:
            raise DuplicateOutputColumn("The column %s has already been specified."%(outputColumnName))
        newCalculation = self._resolveCalculation(calculation)
        if newCalculation == False:
            raise InvalidCalculationType("The calculation %s is invalid or could not be found."%(calculation))
        self._outputColumns[outputColumnName] = newCalculation

        return
    def _getBlankOutputRow(self):
        """Returns a Blank output row that contains all fields that should be outputed with a
        default value of None."""
        tmpRow = {}
        tmpRow[self._groupByColumnName] = None
        tmpRow[self._beginMeasureColumnName] = None
        tmpRow[self._endMeasureColumnName] = None
        for aCol in self._dissolveColumns:
            tmpRow[aCol] = None
        for aCol in self._outputColumns.keys():
            tmpRow[aCol] = None

        return tmpRow

    def _calculateColumnsForRowSet(self,rowSet,beginMeasure,endMeasure):
        newRow = self._getBlankOutputRow()
        newRow[self._beginMeasureColumnName] = beginMeasure
        self._outputDataTypes[self._beginMeasureColumnName] = eaglepy.DataSource.convertDataTypeToEsriDataType(beginMeasure)
        newRow[self._endMeasureColumnName] = endMeasure
        self._outputDataTypes[self._endMeasureColumnName] = eaglepy.DataSource.convertDataTypeToEsriDataType(endMeasure)

        if len(rowSet) == 0:
            return newRow
        #copy the dissolved column values from the first row (they are all the same)
        for aCol in self._dissolveColumns:
            newRow[aCol] = rowSet[0][aCol]
            self._outputDataTypes[aCol] = eaglepy.DataSource.convertDataTypeToEsriDataType(rowSet[0][aCol])

        newRow[self._groupByColumnName] = rowSet[0][self._groupByColumnName]
        self._outputDataTypes[self._groupByColumnName] = eaglepy.DataSource.convertDataTypeToEsriDataType(rowSet[0][self._groupByColumnName])


        #use the calculate classes to create the calculate fields.
        data = rowSet
        newData = [newRow]#convert this to an array with a single row in it.
        for colName, calcString in self._outputColumns.items():
            try:
                calcObject = eval(calcString)
                colValue = calcObject.execute()
                newData[0][colName] = colValue
                self._outputDataTypes[colName] = calcObject.getDataType()
            except Exception as e:
                self._addWarning("An error was encountered while calculating %s."%(colName))
                self._addErrorToLog("COULD_NOT_CALCULATE_OUTPUT",str(e),INPUT_LAYER_COL_NAME=colName)

        return newData

    def _dissolveDataSet(self,dataSet):
        """Dissolves the specified dataset according to the information already provided in the init and addDissolve column
        and addCalculationColumn."""
        #sort the dataset by the orderByColumn
        #TODO: This sort could be wrong, need to change this to the eaglepy multi-key sort.
        from eaglepy import multi_key_sort
        sortedDataSet = multi_key_sort(dataSet, [self._orderByColumnName, self._beginMeasureColumnName, self._endMeasureColumnName])
        # sortedDataSet = sorted(dataSet, key=lambda k: (k[self._orderByColumnName],k[self._beginMeasureColumnName],k[self._endMeasureColumnName]))

        #loop over the data looking for breaks in the measure or in the dissolve fields
        currDissolveData = {}
        currBeginMeasure = None
        currEndMeasure = None
        currRowSet = []
        dataSetOutputData = []
        segmentedHere = False
        for aRow in sortedDataSet:
            #if the currBeginMeasure is None, then this is the first loop, so
            #gather the data, and skip around to the next iteration
            if currBeginMeasure is None:
                currBeginMeasure = aRow[self._beginMeasureColumnName]
                currEndMeasure = aRow[self._endMeasureColumnName]
                for aCol in self._dissolveColumns:
                    currDissolveData[aCol] = aRow[aCol]
                currRowSet.append(copy.deepcopy(aRow))
                continue

            if currBeginMeasure == 796561.8:
                print('here')

            # check to see if the currEndMeasure is the same as the begin measure (means continuous)
            if currEndMeasure != aRow[self._beginMeasureColumnName]:
                #this means there is a discontinuity, and so the data breaks at this point.
                dataSetOutputData.extend(self._calculateColumnsForRowSet(currRowSet, currBeginMeasure, currEndMeasure))
                segmentedHere = True

            # check to see if any of the columns in the dissolve have changed
            # We only want to check this if segmentHere is False
            if not segmentedHere:
                for aCol in self._dissolveColumns:
                    if currDissolveData[aCol] != aRow[aCol]:
                        dataSetOutputData.extend(self._calculateColumnsForRowSet(currRowSet,
                                                                                 currBeginMeasure,
                                                                                 currEndMeasure))
                        segmentedHere = True
                        break

            #if the data was segmented, clean up and setup for the next record
            if segmentedHere == True:
                currBeginMeasure = aRow[self._beginMeasureColumnName]
                currEndMeasure = aRow[self._endMeasureColumnName]
                for aCol in self._dissolveColumns:
                    currDissolveData[aCol] = aRow[aCol]
                del currRowSet
                currRowSet = []
                currRowSet.append(copy.deepcopy(aRow))
                segmentedHere = False
                continue
            else:
                #no segment here, so fix up the end measure and keep going
                #this ensures the end measure is pushed forward to check
                #for continuous data.
                currRowSet.append(copy.deepcopy(aRow))
                currEndMeasure = aRow[self._endMeasureColumnName]
        dataSetOutputData.extend(self._calculateColumnsForRowSet(currRowSet, currBeginMeasure, currEndMeasure))
        return dataSetOutputData

    def execute(self):
        """Executes the dissolve process using the specified settings."""
        self._outputData = []
        #get the list of group by values from the input data source
        self._inputTable.refresh()
        gbCur = self._inputTable.cursor()
        gbCur.execute("select")
        groupByList = []
        for aRow in gbCur.fetchall():
            groupByList.append(aRow[self._groupByColumnName])
        groupByList = set(groupByList)
        gbCur.close()
        del gbCur

        #get the data for each group by, and pull it into an array
        for currGroupByValue in groupByList:
            cgbvCur = self._inputTable.cursor()
            cgbvCur.execute("select",[(self._groupByColumnName,currGroupByValue)])
            groupedDataSet = []
            for aRow in cgbvCur.fetchall():
                newRow = {}
                for colData in cgbvCur.description:
                    newRow[colData[0]] = aRow[colData[0]]
                groupedDataSet.append(copy.deepcopy(newRow))
            self._outputData.extend(self._dissolveDataSet(groupedDataSet))
            self.writeToDisk()
        self.writeToDisk(force=True)



        return


    def getDissolveratorOutputTable(self):
        if hasattr(self,"_outputData") == False:
            self._addWarning("The execute method must be called before calling getMeasureRangeTable()")
            return None
        self._addLog("Starting Creation of Statistics Output Table")
        fields = self._outputDataTypes.keys()
        dataTypes = self._outputDataTypes.values()
        primaryKey = self._groupByColumnName
        newDataTable = self._outputData

        self._addLog("Export Complete, building Connection.")
        conn = eaglepy.DataSource.connect("ConnectionEsriEdit",
                                          fieldNames=fields,
                                          primaryKey=primaryKey,
                                          dataTable=newDataTable,
                                          fieldDataTypes=dataTypes)
        self._addLog("Statistics Output Table Creating Complete.")
        return conn





class _BaseManager( _BaseSegmentation):
    def __init__(self, *args, **kwargs):
        super(_BaseManager, self).__init__(*args, **kwargs)

    def _writeDataToDisk(self, force=False):
        """
        Checks each internal record set (measure range and error) for a total count, if either one (or the sum of
        both) is over 100,000 then data will be written to disk.  The arrays are emptied after being written to disk.
        @param force: if set to true (default False) this method will write the current data in measure range
        and error lists to disk no matter the record count.
        @return:
        """
        return


class ManagedOutputMixin(object):
    """
    Mixin that provides access to writing data to disk and management of getting managed data source
    objects by calling getErrorTable and getOutputTable.
    """

    def __init__(self,
                 pathToOutputTable="",
                 pathToErrorTable="",
                 columnsForOutputTable=list(),
                 columnsForErrorTable=list(),
                 **kwargs):
        self._pathToOutputTable = pathToOutputTable
        if self._pathToOutputTable == "":
            self._pathToOutputTable = os.path.join(eaglepy.CreateNewWorkspace(), "OT")

        self._pathToErrorTable = pathToErrorTable
        if self._pathToErrorTable == "":
            self._pathToErrorTable = os.path.join(eaglepy.CreateNewWorkspace(), "ERT")

        self._columnsForOutputTable = columnsForOutputTable
        self._columnsForErrorTable = columnsForErrorTable

        super(ManagedOutputMixin, self).__init__(**kwargs)

    def getErrorTable(self):
        """
        Returns a managed connection object to the data on disk that represents the error table.
        @return: The error table represented as a managed connection object.
        @rtype : eaglepy.DataSource.ConnectionEsriDAManaged
        """
        return eaglepy.DataSource.connect("ConnectionEsriDAManaged",
                                          inputTable=self._pathToErrorTable,
                                          fieldNames=ERROR_RANGE_TABLE_COLUMNS,
                                          primaryKey=ERROR_RANGE_TABLE_PRIMARY_KEY,
                                          autoLoad=False,
                                          maxRecordCount=-1)

    def getOutputTable(self):
        """
        Returns a managed connection object to the data on disk that represents the measure table.
        @return: The error table represented as a managed connection object.
        @rtype : eaglepy.DataSource.ConnectionEsriDAManaged
        """
        return eaglepy.DataSource.connect("ConnectionEsriDAManaged",
                                          inputTable=self._pathToOutputTable,
                                          fieldNames=MEASURE_RANGE_TABLE_COLUMNS,
                                          primaryKey=MEASURE_RANGE_TABLE_PRIMARY_KEY,
                                          autoLoad=False,
                                          maxRecordCount=-1)


class ManagedSegmentor(ManagedOutputMixin, SegmentorMultiRoute):

    def __init__(self, **kwargs):
        """
        Creates a new SegmentorMultiRoute class.
        This automatically handles segmenting when the data sources contain multiple routes.  Each data source will be
        pulled apart, and updated so that the appropriate whereClause attribute is set, only allowing data for the
        specified route to be queried.  When calling this, you should always set autoLoad=False on the connection
        objects, this prevents them from loading into memory until needed.

            @routeDataSource - An eaglepy.DataSource.Connection that represents the single route record for this
                segmentation
            @routeFieldMap - A dictionary that maps required fields to the actual fields in the routeDataSource
                routeID - The route identifier field for the dataSource
                primaryKey - The primary key column for the dataSource (Must be the same as routeID)
                fromMeasure - The from measure field of the dataSource
                toMeasure - The to measure field of the dataSource
            @pathToMeasureRangeTable: The path to the object class that will contain the output.
            @pathToErrorTable: The path to the object class that will contain the error output.
            @columnsForMeasureRangeTable: The list of column objects that represent the measure range table.  If not
                specified, the default process will be used.  This list is passed directly to
                eaglepy.da.EaglepyConnectiontoTable
            @columnsForErrorTable: The list of column objects that represent the error table.  If not
                specified, the default process will be used.  This list is passed directly to
                eaglepy.da.EaglepyConnectiontoTable
        """

        super(ManagedSegmentor, self).__init__(**kwargs)

    def getMeasureRangeTable(self):
        return self.getOutputTable()

    def _getMeasureRangeTable(self):
        """
        Returns the segmentation measure range table as an eaglepy.DataSource.Connection.
        @return: The current measure range table for the in memory data.
        @rtype : eaglepy.DataSource.ConnectionEsriEdit
        """
        #if execute has not been called, return None.
        fields = MEASURE_RANGE_TABLE_COLUMNS
        dataTypes=MEASURE_RANGE_TABLE_DATA_TYPES
        primaryKey=MEASURE_RANGE_TABLE_PRIMARY_KEY
        conn = eaglepy.DataSource.connect("ConnectionEsriEdit",
                                          fieldNames=fields,
                                          primaryKey=primaryKey,
                                          dataTable=self.measureRangeOutput,
                                          fieldDataTypes=dataTypes)
        return conn

    def writeToDisk(self, force=False):
        """
        Checks each internal record set (measure range and error) for a total count, if either one (or the sum of
        both) is over 100,000 then data will be written to disk.  The arrays are emptied after being written to disk.
        # @param force: if set to true (default False) this method will write the current data in measure range
        # and error lists to disk no matter the record count.
        # @return:
        # """
        # mrtCount = len(self.measureRangeOutput)
        # errtCount = len(self.errorOutput)
        # thresholdCount = 100000
        # if mrtCount >= thresholdCount or \
        #                 errtCount >= thresholdCount or \
        #                 (mrtCount + errtCount) >= thresholdCount or force:

            ## write measure range data to disk
        # self._addLog("Writing Measure Range Data to disk.")
        mrtConn = self._getMeasureRangeTable()
        eaglepy.da.EaglepyConnectionToTable(mrtConn,
                                            self._pathToOutputTable,
                                            append=True,
                                            output_columns=self._columnsForOutputTable)
        mrtConn.close()
        del mrtConn
        del self.measureRangeOutput
        self.measureRangeOutput = list()
        # self._addLog("Finished writing measure range data.")

        ## write error table to disk
        # self._addLog("Writing Error Data to disk.")
        #errtConn = super(ManagedSegmentor, self).getErrorTable()
        errtConn = SegmentorMultiRoute.getErrorTable(self)
        eaglepy.da.EaglepyConnectionToTable(errtConn,
                                            self._pathToErrorTable,
                                            append=True,
                                            output_columns=self._columnsForErrorTable)
        errtConn.close()
        del errtConn
        del self.errorOutput
        self.errorOutput = list()
        # self._addLog("Finished writing errors to disk.")

        return


class ManagedAttributer(ManagedOutputMixin, Attributer):

    def __init__(self, **kwargs):
        super(ManagedAttributer, self).__init__(**kwargs)

    def writeToDisk(self, force=False):
        """
        Checks each internal record set (measure range and error) for a total count, if either one (or the sum of
        both) is over 100,000 then data will be written to disk.  The arrays are emptied after being written to disk.
        @param force: if set to true (default False) this method will write the current data in measure range
        and error lists to disk no matter the record count.
        @return:
        """
        mrtCount = len(self._outputAttributeMeasureRangeTable)
        errtCount = len(self.errorOutput)
        thresholdCount = 100000
        if mrtCount >= thresholdCount or \
                        errtCount >= thresholdCount or \
                        (mrtCount + errtCount) >= thresholdCount or force:

            ## write measure range data to disk
            self._addLog("Writing Measure Range Data to disk.")
            #mrtConn = self._getMeasureRangeTable()
            mrtConn = Attributer.getAttributedMeasureRangeTable(self)
            eaglepy.da.EaglepyConnectionToTable(mrtConn,
                                                self._pathToOutputTable,
                                                append=True,
                                                output_columns=self._columnsForOutputTable,
                                                use_all_columns=True)
            mrtConn.close()
            del mrtConn
            del self._outputAttributeMeasureRangeTable
            self._outputAttributeMeasureRangeTable = list()
            self._addLog("Finished writing measure range data.")

            ## write error table to disk
            self._addLog("Writing Error Data to disk.")
            errtConn = Attributer.getErrorTable(self)
            eaglepy.da.EaglepyConnectionToTable(errtConn,
                                                self._pathToErrorTable,
                                                append=True,
                                                output_columns=self._columnsForErrorTable)
            errtConn.close()
            del errtConn
            del self.errorOutput
            self.errorOutput = list()
            self._addLog("Finished writing errors to disk.")

        return

    def getOutputTable(self):
        """
        Returns a managed connection object to the data on disk that represents the measure table.
        @return: The error table represented as a managed connection object.
        @rtype : eaglepy.DataSource.ConnectionEsriDAManaged
        """
        return eaglepy.DataSource.connect("ConnectionEsriDAManaged",
                                          inputTable=self._pathToOutputTable,
                                          fieldNames=self._outputColumns.keys(),
                                          primaryKey=MEASURE_RANGE_TABLE_PRIMARY_KEY,
                                          autoLoad=False,
                                          maxRecordCount=-1)

    def getAttributedMeasureRangeTable(self):
        return self.getOutputTable()


class ManagedStatistics(ManagedOutputMixin, Statistics):
    def __init__(self, **kwargs):
        super(ManagedStatistics, self).__init__(**kwargs)

    def writeToDisk(self, force=False):
        """
        Checks each internal record set (measure range and error) for a total count, if either one (or the sum of
        both) is over 100,000 then data will be written to disk.  The arrays are emptied after being written to disk.
        @param force: if set to true (default False) this method will write the current data in measure range
        and error lists to disk no matter the record count.
        @return:
        """
        mrtCount = len(self._outputData)##
        errtCount = len(self.errorOutput)
        thresholdCount = 100000
        if mrtCount >= thresholdCount or \
                        errtCount >= thresholdCount or \
                        (mrtCount + errtCount) >= thresholdCount or force:

            ## write measure range data to disk
            self._addLog("Writing Measure Range Data to disk.")
            mrtConn = Statistics.getStatisticsOutputTable(self)
            eaglepy.da.EaglepyConnectionToTable(mrtConn,
                                                self._pathToOutputTable,
                                                append=True,
                                                output_columns=self._columnsForOutputTable,
                                                use_all_columns=True)
            mrtConn.close()
            del mrtConn
            del self._outputData
            self._outputData = list()
            self._addLog("Finished writing measure range data.")

            ## write error table to disk
            self._addLog("Writing Error Data to disk.")
            errtConn = Statistics.getErrorTable(self)
            eaglepy.da.EaglepyConnectionToTable(errtConn,
                                                self._pathToErrorTable,
                                                append=True,
                                                output_columns=self._columnsForErrorTable)
            errtConn.close()
            del errtConn
            del self.errorOutput
            self.errorOutput = list()
            self._addLog("Finished writing errors to disk.")

        return

    def getOutputTable(self):
        """
        Returns a managed connection object to the data on disk that represents the measure table.
        @return: The error table represented as a managed connection object.
        @rtype : eaglepy.DataSource.ConnectionEsriDAManaged
        """
        return eaglepy.DataSource.connect("ConnectionEsriDAManaged",
                                          inputTable=self._pathToOutputTable,
                                          fieldNames=self._outputDataTypes.keys(),
                                          primaryKey=self._groupByColumnName,
                                          autoLoad=False,
                                          maxRecordCount=-1)

    def getStatisticsOutputTable(self):
        return self.getOutputTable()


class ManagedDissolverator(ManagedOutputMixin, Dissolverator):
    def __init__(self, **kwargs):
        super(ManagedDissolverator, self).__init__(**kwargs)

    def writeToDisk(self, force=False):
        """
        Checks each internal record set (measure range and error) for a total count, if either one (or the sum of
        both) is over 100,000 then data will be written to disk.  The arrays are emptied after being written to disk.
        @param force: if set to true (default False) this method will write the current data in measure range
        and error lists to disk no matter the record count.
        @return:
        """
        mrtCount = len(self._outputData)##
        errtCount = len(self.errorOutput)
        thresholdCount = 100000
        if mrtCount >= thresholdCount or \
                        errtCount >= thresholdCount or \
                        (mrtCount + errtCount) >= thresholdCount or force:

            ## write measure range data to disk
            self._addLog("Writing Measure Range Data to disk.")
            mrtConn = Dissolverator.getDissolveratorOutputTable(self)
            eaglepy.da.EaglepyConnectionToTable(mrtConn,
                                                self._pathToOutputTable,
                                                append=True,
                                                output_columns=self._columnsForOutputTable,
                                                use_all_columns=True)
            mrtConn.close()
            del mrtConn
            del self._outputData
            self._outputData = list()
            self._addLog("Finished writing measure range data.")

            ## write error table to disk
            self._addLog("Writing Error Data to disk.")
            errtConn = Dissolverator.getErrorTable(self)
            eaglepy.da.EaglepyConnectionToTable(errtConn,
                                                self._pathToErrorTable,
                                                append=True,
                                                output_columns=self._columnsForErrorTable)
            errtConn.close()
            del errtConn
            del self.errorOutput
            self.errorOutput = list()
            self._addLog("Finished writing errors to disk.")

        return

    def getOutputTable(self):
        """
        Returns a managed connection object to the data on disk that represents the measure table.
        @return: The error table represented as a managed connection object.
        @rtype : eaglepy.DataSource.ConnectionEsriDAManaged
        """
        return eaglepy.DataSource.connect("ConnectionEsriDAManaged",
                                          inputTable=self._pathToOutputTable,
                                          fieldNames=self._outputDataTypes.keys(),
                                          primaryKey=self._groupByColumnName,
                                          autoLoad=False,
                                          maxRecordCount=-1)

    def getDissolveratorOutputTable(self):
        return self.getOutputTable()