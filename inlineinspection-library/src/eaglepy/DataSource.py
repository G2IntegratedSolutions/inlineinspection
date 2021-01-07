##
##Package that contains eagle Data Source objects.  These are DB2 api objects that
##hold the "database" in memory so that we can operate on esri objects much faster
##instead of relying on cursors
##http://www.python.org/dev/peps/pep-0249/
##

##imports
from __future__ import division

import sys
py_version = sys.version_info[0]
if py_version <= 2:
    import exceptions

import numpy
import string
import copy
import eaglepy
import decimal
from collections import Iterator
import arcpy

####################################################
##Constants
####################################################
apilevel = "2.0"
threadsafety=0
paramstyle="format"#this may not be the correct choice, not sure yet.

####################################################
##Error Definitions
####################################################

if py_version <=2:
    class Warning(exceptions.StandardError):
        pass

    class Error(exceptions.StandardError):
        pass
else:
    class Warning(Exception):
        pass

    class Error(Exception):
        pass


class InterfaceError(Error):
    pass

class DatabaseError(Error):
    pass

class DataError(DatabaseError):
    pass
class OperationalError(DatabaseError):
    pass
class IntegrityError(DatabaseError):
    pass
class InternalError(DatabaseError):
    pass
class ProgrammingError(DatabaseError):
    pass
class NotSupportedError(DatabaseError):
    pass

class InvalidWhereClause(NotSupportedError):
    pass


####################################################
##Connect option
####################################################
def connect(type="",*args,**kwargs):
    """Creates a connection of the specified type and returns it.  Additional parameters should be specified depending on the type of connection
        that is desired.
        types - The conneciton type, must be one of the following: ConnectionEsri, ConnectionEsriEdit, ConnectionEsriEditFromConnectionEsri

        For a ConnectionEsriDA type, the following parameters may be specified:
             inputTable - The feature class to be imported, this should be a full path.
             fieldNames - A python list containing a strings that represent the field names.
             whereClause - An optional where clause to apply before the data is downloaded.
             primaryKey - An optional argument that indicates the column in the source that should be used as the primary key.  If not specified OID@ will be used.
                    This column will be automatically be added to the fieldNames list if it does not already exist.
             autoLoad - A boolean value that indicates if the data should be pulled into RAM now, or when refresh is called.

        For a ConnectionEsriEdit type, the following may be specified:
            Creates a new ConnectionEsriEdit object.  This is an editable version of a ConnectionEsri (or optionally a CursorEsri)
            To convert an entire connection, simply specify the connection parameter, i.e.
                ConnectionEsriEdit(connection=<myConnectionEsriToConver>)

            To convert from a cursor, specify the cursor parameterer, i.e.
                ConnectionEsriEdit(cursor=<myCursorFromAConnectionEsri)

            To create an empyt connection of this type, specify the fieldNames and primaryKey parameters, i.e.:
                ConnectionEsriEdit(fieldNames=['name','anotherName'],primaryKey='name',dataDable=[])
                The primaryKey value must exist int he fieldNames List.
                dataTable - A list of dictionaries that represent the data.

        for a ConnectionEsriEditFromConnectionEsri, use the same inputs as a ConnectionEsri type, but a ConnectionEsriEdit type will be returned.

        NOTE: * ConnectionEsri and ConnectionEsriDA are very similar, however ConnectionEsri uses a function provided by esri to convert the input
            table directly to an in-memory array.  This is much more efficient than ConnectionEsriDA.  Personal Geodatabases do not support
            the functionality required by ConnectionEsri at this time, and so if the input table string contains a .mdb, it will be automatically
            converted to a ConnectionEsriDA.  This will not affect any functionality.
        NOTE: *** ConnectionEsri has been deprecated, and now returns a ConnectionEsriDA by default.
        """
    if type == "ConnectionEsri":
        return ConnectionEsriDA(*args, **kwargs)
    elif type == "ConnectionEsriDA":
        return ConnectionEsriDA(*args, **kwargs)
    elif type == "ConnectionEsriDAManaged":
        return ConnectionEsriDAManaged(*args, **kwargs)
    elif type=="ConnectionEsriEdit":
        return ConnectionEsriEdit(*args,**kwargs)
    elif type=="ConnectionEsriEditFromConnectionEsri":
        return ConnectionEsriEdit(ConnectionEsri(*args,**kwargs))
    else:
        raise NotSupportedError("The type (%s) is not a valid conneciton type."%(type))


def cloneDataSource(dataSource,**kwargs):
    """Clones the specified dataSource, using the original inputs, overridden by any key word arguments specified that apply to this data source.
    The autoLoad flag is not supported in a clone, be sure to set it if you want something specific, otherwise it will default to the default for the class."""
    if type(dataSource) is ConnectionEsri:
        newArgs = {}
        newArgs["inputTable"] = dataSource._inputTable
        newArgs["fieldNames"] = dataSource._fieldNames
        newArgs["whereClause"] = dataSource._whereClause
        newArgs["primaryKey"] = dataSource._primaryKey
        #override any args from **kwargs
        if py_version <=2:
            for key,value in kwargs.iteritems():
                newArgs[key] = value
        else:
            for key,value in kwargs.items():
                newArgs[key] = value
        return connect("ConnectionEsri",**newArgs)
    elif type(dataSource) is ConnectionEsriDA:
        newArgs = {}
        newArgs["inputTable"] = dataSource._inputTable
        newArgs["fieldNames"] = dataSource._fieldNames
        newArgs["whereClause"] = dataSource._whereClause
        newArgs["primaryKey"] = dataSource._primaryKey
        #override any args from **kwargs
        if py_version <=2:
            for key,value in kwargs.iteritems():
                newArgs[key] = value
        else:
            for key,value in kwargs.items():
                newArgs[key] = value
        return connect("ConnectionEsriDA",**newArgs)
    elif type(dataSource) is ConnectionEsriDAManaged:
        newArgs = {}
        newArgs["inputTable"] = dataSource._inputTable
        newArgs["fieldNames"] = dataSource._fieldNames
        newArgs["whereClause"] = dataSource._whereClause
        newArgs["primaryKey"] = dataSource._primaryKey
        newArgs["maxRecordCount"] = dataSource.maxRecordCount
        #override any args from **kwargs
        if py_version <=2:
            for key,value in kwargs.iteritems():
                newArgs[key] = value
        else:
            for key,value in kwargs.items():
                newArgs[key] = value
        return connect("ConnectionEsriDAManaged",**newArgs)
    elif type(dataSource) is ConnectionEsriEdit:
        newArgs = {}
        newArgs["cursor"] = dataSource._source_cursor
        newArgs["fieldNames"] = dataSource._source_fieldNames
        newArgs["primaryKey"] = dataSource._source_primaryKey
        newArgs["dataTable"] = dataSource._source_dataTable
        newArgs["fieldDataTypes"] = dataSource._source_fieldDataTypes
        #override any args from **kwargs
        if py_version <=2:
            for key,value in kwargs.iteritems():
                newArgs[key] = value
        else:
            for key,value in kwargs.items():
                newArgs[key] = value
        return connect("ConnectionEsriEdit",**newArgs)

    else:
        raise NotSupportedError("The specified dataSource type is not supported (%s)"%(str(type(dataSource))))

def castValueToColumnType(value,columnName,cursor):
    """Casts the specified value (usually a string) into the correct data type for the specified column.
        value - data to be cast to the new type
        columnName - the name of the column on the cursor that the value should be cast into
        curosr - the cursor to get the data type from
    Returns the value, cast into the data type of the column, or if the column does not exist, the same value is returned."""
    dataType  = None
    for column in cursor.description:
        if columnName == column[0]:
            #we found the column, so we will try to cast the value object into this data type
            dataType = column[1]
            break
    #if the dataType is None, return value
    if dataType is None:
        return value
    if str(dataType).lower() == 'string' or str(dataType).lower()[0] == "s":
        return str(value)
    if str(dataType).lower() in ["single","double"]:
        return float(value)
    if str(dataType).lower() in ["integer","smallinteger"]:
        return int(value)

    return value

def getDataTypeForColumn(columnName, cursor):
    """Searches the cursor object for the specified columnName, and returns the data type associated with it."""
    dataType = "String"
    for column in cursor.description:
        if columnName == column[0]:
            #we found the column, so we will try to cast the value object into this data type
            dataType = column[1]
            break
    return dataType

def getDataTypeForColumnFromConnection(columnName, connection):
    """
    Searches the connection object for the specified columnName and returns the data tyape associated with it.
    @param columnName: The column name to look for (case sensetive)
    @param connection: The connection to look in
    @return:The data type for that column name or "String" if one could not be found.
    """
    dataType = "String"
    for column in connection._dbapi2Describe:
        if columnName == column[0]:
            #we found the column, so we will try to cast the value object into this data type
            dataType = column[1]
            break
    return dataType


def convertDataTypeToEsriDataType(dataType):
    """Tests the input dataType and converts it to a suitable Esri data type for use by Esri tools.
        If the specific type can not be figured out, STRING is returned."""
    newDataType = "STRING"
    converter = {"string":"STRING",
                "int":"LONG",
                "float":"FLOAT",
                "double":"DOUBLE",
                "number":"FLOAT",
                "date":"DATE",
                "datetime":"DATE",
                "oid":"LONG"}
    #if it is a unicode string and can't be converted to a string,
    #then it must be a string
    if py_version <= 2:
        if isinstance(dataType, unicode):
            try:
                str(dataType)
            except:
                return "STRING"
    else:
        if isinstance(dataType, str):
            try:
                str(dataType)
            except:
                return "STRING"
    if (str(dataType)).lower() in converter.keys():
        newDataType = converter[str(dataType).lower()]
        return newDataType
    if len(str(dataType)) > 0 and str(dataType).lower()[0] == "s":
        return "STRING"
    if dataType is numpy.int64:
        return "LONG"
    if dataType is numpy.float64 or dataType is numpy.float32:
        return "FLOAT"
    if dataType is numpy.int32:
        return "SHORT"
    import datetime
    if dataType is datetime.datetime or dataType is datetime.date or dataType is datetime.time:
        return "DATE"
    if type(dataType) == str:
        return "STRING"
    if type(dataType) == int:
        return "LONG"
    if type(dataType) in [float, decimal.Decimal]:
        return "FLOAT"
    if type(dataType) in [datetime.date, datetime.datetime, datetime.time]:
        return "DATE"
    if type(dataType) == numpy.int32:
        return "LONG"
    if type(dataType) == numpy.int64:
        return "LONG"
    if dataType == decimal.Decimal:
        return "FLOAT"
    return newDataType

####################################################
##Base DB API2 classes (Connection, Cursor)
####################################################
class Connection(object):
    """Base Connection object from the DB API2, Pep 0249"""
    _status = "unused"

    def status(self):
        """Returns the status of the connection, in:
            open - Connection is ready to go
            unloaded - The connection is ready, but not loaded into RAM
            closed - The connection is closed and cannot be reused
            unused - The connection has not been initialized.
        NOTE: This is not part of PEP 0249"""
        return self._status

    def close(self):
        raise NotImplementedError()

    def commit(self):
        raise NotImplementedError()

    def rollback(self):
        raise NotImplementedError()

    def cursor(self):
        raise NotImplementedError()

    def refresh(self):
        return

    def __unicode__(self):
        tmp = "Connection;"
        if py_version <=2:
            for key, value in self.__dict__.iteritems():
                tmp += str(key)+" :"+str(value)+";"
        else:
            for key, value in self.__dict__.items():
                tmp += str(key)+" :"+str(value)+";"
        return tmp

    def __str__(self):
        return self.__unicode__()

####################################################
##Base DB API2 classes (Connection, Cursor)
####################################################
class Cursor(object):
    """Base Cursor object from the DB API2, Pep 0249"""
    rowcount = -1
    description = None
    arraysize = 1
    _status = "unused"

    def callProc(self):
        raise NotSupportedError()

    def close(self):
        raise NotImplementedError()

    def execute(self):
        raise NotImplementedError()

    def executemany(self):
        raise NotSupportedError()

    def fetchone(self):
        raise NotImplementedError()

    def fetchmany(self):
        raise NotSupportedError()

    def fetchall(self):
        raise NotImplementedError()

    def nextset(self):
        raise NotSupportedError()

    def setinputsizes(self):
        raise NotSupportedError()

    def setoutputsizes(self):
        raise NotSupportedError()

    def tonumpyarray(self):
        raise NotImplementedError()

    def __unicode__(self):
        tmp = "Cursor;"
        if py_version <=2:
            for key, value in self.__dict__.iteritems():
                tmp += str(key)+" :"+str(value)+";"
        else:
            for key, value in self.__dict__.items():
                tmp += str(key)+" :"+str(value)+";"
        return tmp

    def __str__(self):
        return self.__unicode__()

####################################################
##blah blah
####################################################


####################################################
##ConnectionEsri Implementation
####################################################
class ConnectionEsri(Connection):
    """Connection object that creates an in-memory copy of the Esri Table or FeatureClass that is specified.
        All changes are applied only to the in-memory copy.  Becarful, this can be a lot of stuff to store in memory,
        so use the whereClause to limit the amount of data that is pulled into memory."""

    def __init__(self, inputTable, fieldNames, whereClause="", primaryKey="OID@", autoLoad=True, orderby=""):
        """Creates a connection object to a Feature Class.  This class downloads the data into memory for faster
            processing, Any changes to this data that are made are not persisted in the original feature class, that
            must be handled separatly.  In order to limit tha ammount of memory pre-allocated, please specify a where
            clause, this will limit the amount of data downloaded by this class.  An additional where clause may be
            specified within the cursor, this where clause is applied in memory.

            ***All changes made to data using a cursor in this connection happen immediately,
                commit and rollback do not apply here.

                inputTable - The feature class to be imported, this should be a full path.
                fieldNames - A python list containing a strings that represent the field names.
                whereClause - An optional where clause to apply before the data is downloaded.
                primaryKey - An optional argument that indicates the column in the source that should be used as
                                the primary key.  If not specified OID@ will be used.
                    This column will be automatically be added to the fieldNames list if it does not already exist.
                autoLoad - A boolean value that indicates if the data should be pulled into RAM now, or when refresh
                                is called."""

        if self._status != 'unused':
            raise Error("Cursor can not be re-opened.")
        self._inputTable = inputTable
        self._fieldNames = fieldNames
        self._whereClause = whereClause
        self._primaryKey = primaryKey
        self._orderby = orderby
        if self._primaryKey not in self._fieldNames:
            self._fieldNames.append(self._primaryKey)
        self._status = "unloaded"
        if autoLoad == True:
            self.refresh()

    def _processFields(self):
        """Processes the fields in self._fieldNames to ensure that they all exist.  Any fields that do not exist are
        automatically removed from the list.  This helps avoid errors but can increase confusion on the user's part.  The
        interface that calls this object must verify column names first!"""
        self._dbapi2Describe = []
        if self._primaryKey == "OID@":
            self._dbapi2Describe.append(["OID@", "Integer", None, None, None, None, None])
        if hasattr(self._arcpyDescribe, "fields"):
            #Get the list of fields from the table
            #verify that all fields in self._fieldNames are in the actual table, if they are not, remove them.
            finalFieldList = []
            arcpyFieldList = []
            for field in self._arcpyDescribe.fields:
                arcpyFieldList.append(field.name)

            if self._primaryKey not in self._fieldNames:
                self._fieldNames.append(self._primaryKey)


            for i in range(len(self._fieldNames)):
                currField = self._fieldNames[i]
                #loop through the arcpyFieldList (From Describe) and find fields that match
                #by comparing for lower case
                if currField.count("@") >= 1 and currField.lower() != "oid@":
                    finalFieldList.append(currField)
                for j in range(len(arcpyFieldList)):
                    if currField.lower() == arcpyFieldList[j].lower():
                        finalFieldList.append(arcpyFieldList[j])
                        break


            #Create the dbapi2Describe list by getting the data type from the
            #original arcpyDescribe result.
            for field in self._arcpyDescribe.fields:
                if field.name in finalFieldList:
                    self._dbapi2Describe.append([field.name,field.type,None,None,None,None,None])
            self._fieldNames = list(set(finalFieldList))

            #if the primary key is not a standard field, then it will be dropped by the above
            #process.  This ensures that shortcuts like OID@ are still added to the field list.
            if self._primaryKey.find("@") > -1:
                self._fieldNames.append(self._primaryKey)

        else:
            raise DatabaseError("The layer (%s) has no columns."%(self._inputTable))

    def repairField(self,fieldName):
        """Takes in the fieldName specified and compares it using string.lower to the list of fields that
        are in this connection, and returns the corect case of the field name.  If no match was found, None is returned."""
        for f in self._fieldNames:
            if fieldName.lower() == f.lower():
                return f
        return None


    def refresh(self):
        """Non DB API 2 method that refreshes the connection, the connection can be closed, and then refresh is called,
            and everything will be back to normal again.  This is to help with memory footprint, so that it is possible
            to clean out memory, and then get it back later if needed."""
        import arcpy

        #describe the input dataset.
        self._arcpyDescribe = []
        try:
            self._arcpyDescribe = arcpy.Describe(self._inputTable)
        except:
            raise DatabaseError("The layer (%s) does not exist, or can not be read."%(self._inputTable))
        self._processFields()

        #decide what function to use to get the NumPy Array baesd on the description type (FeatureClass or Table)
        self._inputTableType = None
        if hasattr(self._arcpyDescribe,"dataType"):
            self._inputTableType = self._arcpyDescribe.dataType

        if self._inputTableType in ['FeatureClass','FeatureLayer','Layer']:
            #attempt to load the array into memory.  If it will not fit, mark it as unloaded, and let the cursor method
            # manage the source.
            try:
                self._dataTable = arcpy.da.FeatureClassToNumPyArray(self._inputTable,
                                                                    self._fieldNames,
                                                                    where_clause=self._whereClause)
                self._status = "open"
            except MemoryError:
                self._status = "unloaded"
            except Exception as e:
                raise IntegrityError("An error occurred while querying data, ensure that all columns exist.  " +
                                     "Double check that you are using the correct primary key, or object id. (%s)"
                                     % (str(e)))
        elif self._inputTableType in ['Table', 'TableView']:
            #attempt to load the array into memory.  If it will not fit, mark it as unloaded, and let the cursor method
            # manage the source.
            try:
                self._dataTable = arcpy.da.TableToNumPyArray(self._inputTable,
                                                             self._fieldNames,
                                                             where_clause=self._whereClause)
                self._status = "open"
            except MemoryError:
                self._status = "unloaded"
            except RuntimeError as e:
                self._status = "error"
                raise DataError("Invalid Column name (probably), details: %s"% (str(e)))
            except ValueError as e:
                self._status = "error"
                raise IntegrityError("Duplicate column name, please specify each column name only once. (%s)" %
                                     (str(e)))
            except Exception as e:
                raise e

        else:
            raise Error("The specified input data type is not supported (%s)" % (str(self._inputTableType)))

    def close(self):
        """Close the connection.  The connection will be unusable after calling this (unless you call refresh first).
            This also deletes the in-memory copy of data, so it will clean up your memory footprint."""
        self._status = "closed"
        del self._dataTable
        del self._arcpyDescribe
        del self._dbapi2Describe
        self._dataTable = None
        self._arcpyDescribe = None
        self._dbapi2Describe = None


    def cursor(self):
        """Creates a new cursor object that is connected to this dataset."""
        #if the status is unloaded, that means it would not fit into memory before, so try again.
        if self._status == "unloaded":
            self.refresh()
        #if the status is still unloaded, it still wont fit, and so you will need to raise a memory error
        if self._status == "unloaded":
            raise MemoryError("Unable to load layer into memory.  Cannot allocate array memory.")

        if self._status != "open":
            raise Error("Connection is not currently open")
        newcursor = CursorEsri(self)
        return newcursor


    def commit(self):
        """Not Supported"""
        raise NotSupportedError()

    def rollback(self):
        """Not Supported"""
        raise NotSupportedError()

####################################################
##CursorEsri Implementation
####################################################
class CursorEsri(Cursor):
    """Cursor object that corresponds to the ConnectionEsri class.  This provides a window into the in-memory data, without
        making another copy of the data.  Updates are completed agains the underlying data that is in-memory.  No updates, deletes,
        or inserts are sent back to the original source table or feature class.  Do not create this manually, instead use:
            ConnectionEsri.cursor to get a new cursor object."""
    _whereClause = []
    _orderby = []
    _updateSet = []
    _status = "closed"
    _dataTable = None

    def __init__(self,dataSource):
        """Creates a new cursor object for a ConnectionEsri object.  This should not be used manually,
            but instead by calling ConnectionEsri.cursor()
                dataSource - Requried object of ConnectionEsri"""
        self._dataSource = dataSource
        self.rowcount = -1
        self._status = "unused"
        self.description = self._dataSource._dbapi2Describe

    def execute(self, operation="select", whereClause=[], orderby=[], updateSet=[]):
        """Retreive a subset of data from the input layer.  This data is held in memory separatly from the input data.  Updates should
            be done with a separate cursor object, and sent via this same execute command
                operation - A string defining the type of operation to be done.  Must be in: select, insert, update, delete
                whereClause - Array of column name, value pairs.  These are applied in order to filter the record set.
                orderby - List of column names to order the result set by.  By default they are sorted Ascending.
                    To sort decending, add a ":desc" after the column name.
                updateSet - List of of column name, value pairs.  Each record that matches the whereClause gets this updateSet applied to it for each column.
                    If you specify an updateSet, the fetchall() method will return the set of records that was created by whereClause, and that updateSet was applied to.
                """
        if operation not in ["select", "update"]:
            raise NotSupportedError("The operation specified (%s) is not supported."% (operation))
        self._lastOperation = operation
        self._whereClause = whereClause
        self._orderby = orderby
        self._updateSet = updateSet
        self.rowcount = -1
        if self._status not in ('unused', 'open'):
            raise Error("Cursor can not be re-opened.")

        #run the filter for each whereClause
        #get a view of the data from the dataSource.  This gives a shallow copy
        #here, the shallow copy allows us to filter data without messing up the source
        #data, but also allows us to make changes to this data here, and affect the data in the dataSource.
        if self._dataSource._status != 'open':
            raise Error("Connection is not currently open.")
        self._dataTable = self._dataSource._dataTable.view()
        try:
            for wc in whereClause:
                if len(wc) != 2:
                    raise InvalidWhereClause(str(wc))
                self._dataTable = self._dataTable[self._dataTable[wc[0]] == wc[1]]
        except InvalidWhereClause as ie:
            raise ie
        except Exception as e:
            #raise e
            raise InvalidWhereClause(str(e))

        #after the where clause has been applied, these records need to be removed from the underlying connection
        if self._lastOperation == 'delete':
            for row in self._dataTable:
                locator = self._dataSource._dataTable[self._dataSource._primaryKey] == row[self._dataSource._primaryKey]
                sourceRow = self._dataSource._dataTable[locator]
                self._dataSource._dataTable.delete(sourceRow)

        #check on the updateSet, and run it.
        if self._updateSet != [] and self._lastOperation == 'update':
            for row in self._dataTable:
                #get the source row that matches this row (using the primarykey field)
                locator = self._dataSource._dataTable[self._dataSource._primaryKey] == row[self._dataSource._primaryKey]
                sourceRow = self._dataSource._dataTable[locator]
                for column,value in self._updateSet:
                    #update both the sourceRow, and the row in the view here.
                    sourceRow[column] = value
                    #dave the sourceRow in the sourceData
                    self._dataSource._dataTable[locator] = sourceRow
                    row[column] = value

        #run the order by on self._dataTable
        if self._orderby != []:
            raise NotImplementedError()

        self.rowcount = self._dataTable.shape[0]
        self._status = "open"

    def fetchall(self):
        """Returns the entire record set, after the filter is applied."""
        return self._dataTable

    def close(self):
        """Closes this cursor.  The connection will remain open.  This cursor will be unusable after closing it.
        Data is deleted here, so this will reduce the memory footprint."""
        self._status ='closed'
        del self._dataTable
        self._dataTable = None

    def tonumpyarray(self):
        return self._dataTable

class ConnectionEsriEdit(Connection):
    """A class that converts a ConnectionEsri into an editable process.  This can take a significant amount of CPU time
    and memory to convert, just fyi."""
    def __init__(self,
                 connection=None,
                 cursor=None,
                 fieldNames=list(),
                 primaryKey="",
                 dataTable=list(),
                 fieldDataTypes=list()):
        """Creates a new ConnectionEsriEdit object.  This is an editable version of a ConnectionEsri
        (or optionally a CursorEsri)
            To convert an entire connection, simply specify the connection parameter, i.e.
                ConnectionEsriEdit(connection=<myConnectionEsriToConver>)

            To convert from a cursor, specify the cursor parameterer, i.e.
                ConnectionEsriEdit(cursor=<myCursorFromAConnectionEsri)

            To create an empyt connection of this type, specify the fieldNames and primaryKey parameters, i.e.:
                ConnectionEsriEdit(fieldNames=['name','anotherName'],primaryKey='name',dataDable=[])
                The primaryKey value must exist int he fieldNames List.
                dataTable - A list of dictionaries that represent the data.
                fieldDataTypes - A list that corresponds to the fieldNames that indicates the data type of the field.
                The type should be one of:
                    float - numpy.float64
                    int - numpy.int64
                    string - S4000
                    or anything that can define a numpy array data type.

        """
        self._source_connection = connection
        self._source_cursor = cursor
        self._source_fieldNames = fieldNames
        self._source_primaryKey = primaryKey
        self._source_dataTable = dataTable
        self._source_fieldDataTypes = fieldDataTypes

        self._status = "unused"
        self._dbapi2Describe = None
        self._dataTable = None
        self._fieldTypes= fieldDataTypes
        if connection is not None:
            self._fromConnection(connection)
        elif cursor is not None:
            self._fromCursor(cursor)
        elif fieldNames is not None and primaryKey is not None:
            self._fromSettings(fieldNames=fieldNames,primaryKey=primaryKey,dataTable=dataTable)
        else:
            raise NotSupportedError("The specified parameter combination does not match, see the help.")

    def _fromConnection(self,connection):
        #get a cursor from the connection, and  copy the data into this object.
        c = connection.cursor()
        c.execute()
        self._fromCursor(c)

    def _fromCursor(self,cursor):
        """Loads from the cursor.  The cursor must already be open."""
        if cursor._status != "open":
            raise NotSupportedError("The cursor must be opened before creating a ConnectionEsriEdit object.")
        c = cursor
        self._dbapi2Describe = c.description
        self._fieldNames = c._dataSource._fieldNames
        self._inputTable = c._dataSource._inputTable
        self._dataTable = []
        for row in c.fetchall():
            newRow = {}
            #get all columns from the description
            for col in self._dbapi2Describe:
                newRow[str(col[0])] = row[str(col[0])]
            #save the new row
            self._dataTable.append(newRow)
        self._status = "open"

    def _fromSettings(self, fieldNames=None, primaryKey=None, dataTable=[]):
        if py_version <=2:
            self._fieldNames = fieldNames
        else:
            self._fieldNames = list(fieldNames)
        self._primaryKey = primaryKey
        if self._primaryKey not in self._fieldNames:
            self._fieldNames.append(self._primaryKey)

        self._dbapi2Describe = []
        for fieldIndex in range(len(self._fieldNames)):
            #default type is String of length 255.
            fType = "S255"
            try:
                if self._fieldTypes != []:
                    fType = self._fieldTypes[fieldIndex]
            except:
                pass

            #if the type is in one of the default types, then change it.
            if (str(fType)).lower() in ["string" ,"int", "float"]:
                converter = {"string": "S4000", "int":numpy.int64, "float": numpy.float64}
                fType = converter[str(fType).lower()]

            if py_version<=2:
                self._dbapi2Describe.append([self._fieldNames[fieldIndex],fType,None,None,None,None,None])
            else:
                keys = list(self._fieldNames)
                #arcpy.AddMessage(keys) #***
                self._dbapi2Describe.append([keys[fieldIndex], fType, None, None, None, None, None])

        self._dataTable = dataTable
        self._status = "open"


    def close(self):
        """Close the connection.  The connection will be unusable after calling this.  This also deletes
            the in-memory copy of data, so it will clean up your memory footprint."""
        self._status = "closed"
        del self._dataTable
        self._dataTable = None


    def cursor(self):
        """Creates a new cursor object that is connected to this dataset."""
        if self._status != "open":
            raise Error("Connection is not currently open")
        newcursor = CursorEsriEdit(self)
        return newcursor


    def commit(self):
        """Not Supported"""
        raise NotSupportedError()

    def rollback(self):
        """Not Supported"""
        raise NotSupportedError()

class CursorEsriEdit(CursorEsri):
    """Cursor object that corresponds to the ConnectionEsriEdit class.  This provides a window into the in-memory data, without
        making another copy of the data.  Updates are completed agains the underlying data that is in-memory.  No updates, deletes,
        or inserts are sent back to the original source table or feature class.  Do not create this manually, instead use:
            ConnectionEsri.cursor to get a new cursor object."""

    def execute(self,operation="select",whereClause=[], orderby=[], updateSet=[]):
        """Retreive a subset of data from the input layer.  This data is held in memory separatly from the input data.  Updates should
            be done with a separate cursor object, and sent via this same execute command
                operation - A string defining the type of operation to be done.  Must be in: select, insert, update, delete
                whereClause - Array of column name, value pairs.  These are applied in order to filter the record set.
                orderby - List of column names to order the result set by.  By default they are sorted Ascending.
                    To sort decending, add a ":desc" after the column name.
                updateSet - List of of column name, value pairs.  Each record that matches the whereClause gets this updateSet applied to it for each column.
                    If you specify an updateSet, the fetchall() method will return the set of records that was created by whereClause, and that updateSet was applied to.
                """
        if operation not in ["select","update","insert","delete"]:
            raise NotSupportedError("The operation specified (%s) is not supported."%(operation))
        self._lastOperation = operation
        self._whereClause = whereClause
        self._orderby = orderby
        self._updateSet = updateSet
        self.rowcount = -1
        if self._status not in ('unused','open'):
            raise Error("Cursor can not be re-opened.")

        #run the filter for each whereClause
        #get a view of the data from the dataSource.  This gives a shallow copy
        #here, the shallow copy allows us to filter data without messing up the source
        #data, but also allows us to make changes to this data here, and affect the data in the dataSource.
        if self._dataSource._status != 'open':
            raise Error("Connection is not currently open.")
        self._dataTable = self._dataSource._dataTable
        try:
            for wc in whereClause:
                if len(wc) != 2:
                    raise InvalidWhereClause()

                self._dataTable = [dictList for dictList in self._dataTable if dictList[wc[0]] == wc[1]]
                #self._dataTable = self._dataTable[self._dataTable[wc[0]] == wc[1]]
        except Exception as e:
            raise e
            #raise InvalidWhereClause()

        #after the where clause has been applied, these records need to be removed from the underlying connection
        if self._lastOperation == 'delete':
            for row in self._dataTable:
                locator = self._dataSource._dataTable.index(row)
                sourceRow = self._dataSource._dataTable[locator]
                self._dataSource._dataTable.delete(sourceRow)

        #check on the updateSet, and run it.
        if self._updateSet != [] and self._lastOperation == 'update':
            for row in self._dataTable:
                #get the source row that matches this row (using the primarykey field)
                locator = self._dataSource._dataTable.index(row)
                sourceRow = self._dataSource._dataTable[locator]
                for column,value in self._updateSet:
                    #update both the sourceRow, and the row in the view here.
                    sourceRow[column] = value
                    #dave the sourceRow in the sourceData
                    self._dataSource._dataTable[locator] = sourceRow
                    row[column] = value

        #run the order by on self._dataTable
        if self._orderby != []:
            raise NotImplementedError()

        self.rowcount = len(self._dataTable)
        self._status = "open"

    def tonumpyarray(self):
        """Converts the cursor's output into a numpy array object.  If you are going to use this in any of the arcpy.da methods to convert
            the numpy array into a table or feature class, you need to check the row count manually.  If the array has no rows, arcpy
            still adds a dummy row in the output feature class.  So do something like this:
                myArray = cursor.tonumpyarray()
                arcpy.da.NumPyArrayToTable(myArray,"c:\myoutput")
                if cursor.rowcount == 0:
                    arcpy.Delete_management("c:\myoutput")
                    """
        fieldsList = []
        typesList = []
        for col in self.description:
            fieldsList.append(col[0])
            typesList.append(col[1])
        newRowSet = []
        for aRow in self._dataTable:
            newRow = ()
            for col in self.description:
                #each row in the list must be a tuple, not a list.  In numpy a tuple is an item, and so will become a row.
                #newRow = newRow+(str(aRow[col[0]]),)
                newRow = newRow + (aRow[col[0]], )
            newRowSet.append(newRow)
        if newRowSet == []: #there was no data to put in the row, so make an empty array
            array = numpy.empty((0,len(fieldsList)), dtype={"names": fieldsList, "formats": typesList})
        else:
            array = numpy.rec.fromrecords(newRowSet, dtype={"names": fieldsList, "formats": typesList})
        return array


class ConnectionEsriDA(ConnectionEsri):
    def refresh(self):
        """Non DB API 2 method that refreshes the connection, the connection can be closed, and then refresh is called,
            and everything will be back to normal again.  This is to help with memory footprint, so that it is possible
            to clean out memory, and then get it back later if needed."""
        import arcpy

        # describe the input dataset.
        self._arcpyDescribe = []
        try:
            self._arcpyDescribe = arcpy.Describe(self._inputTable)
        except:
            raise DatabaseError("The layer (%s) does not exist, or can not be read." % (self._inputTable))
        self._processFields()

        # decide what function to use to get the NumPy Array baesd on the description type (FeatureClass or Table)
        self._inputTableType = None
        if hasattr(self._arcpyDescribe, "dataType"):
            self._inputTableType = self._arcpyDescribe.dataType

        if self._inputTableType not in ('FeatureClass', 'Table', 'FeatureLayer', 'Layer', 'TableView'):
            raise Error("The specified input data type is not supported (%s)" % (str(self._inputTableType)))

        self._dataTable = list()

        try:
            rowExists = False
            sql_clause = (None, None)
            if hasattr(self, "_orderby"):
                if self._orderby != "":
                    sql_clause = (None, "ORDER BY {}".format(self._orderby))
            cursor = arcpy.da.SearchCursor(self._inputTable,
                                           self._fieldNames,
                                           where_clause=self._whereClause,
                                           sql_clause=sql_clause)
            for row in cursor:
                rowExists = True
                newRow = {}
                for colIndex in range(len(self._fieldNames)):
                    newRow[self._fieldNames[colIndex]] = row[colIndex]
                self._dataTable.append(newRow)
        except Exception as e:
            raise e
        finally:
            if rowExists:
                del row
            del cursor

        self._status = "open"

    def cursor(self):
        """Creates a new cursor object that is connected to this dataset."""
        if self._status != "open":
            raise Error("Connection is not currently open")
        newcursor = CursorEsriDA(self)
        return newcursor

class CursorEsriDA(CursorEsriEdit):
    pass

class ConnectionEsriDAManaged(ConnectionEsriDA):
    """
    This special version of ConnectionEsriDA allows the system to better manage memory by limiting the number of
    records that are pulled into RAM for processing at any one time.  This connection can be created from an existing
    ConnectionEsriDA, or can be created in the same way that a ConnectionEsriDA is created.  The system should use
    this connection to create ConnectionEsriEdit connections that represent the subset of data to be processed
    and pass these resulting connection objects into the processing classes.
    """
    def __init__(self, *args, **kwargs):
        """
        Creates a new object of type ConnectionEsriDAManaged
        @param args: Static args passed to ConnectionEsriDA.
        @param max_record_count: Specifies the maximum number of records that can be pulled in any connection or cursor
        @param kwargs: Dynamic/Optional args passed to ConnectionEsriDA.
        """
        ## check to see if kwargs has the max record count param, everything else goes to super
        self.maxRecordCount = kwargs.get('maxRecordCount', -1)
        if 'maxRecordCount' in kwargs:
            del kwargs['maxRecordCount']

        ## force the autoload to false.
        tmpAutoLoad = kwargs.get('autoLoad', True)
        kwargs['autoLoad'] = False
        ## call super class and init.
        super(ConnectionEsriDAManaged, self).__init__(*args, **kwargs)
        self._cursor = None
        self.data_sets_returned = 0
        self.curr_record_count = 0
        self._dataTable = []
        self._status = "unloaded"
        if tmpAutoLoad:
            self.refresh()

    def refresh(self):
        """
        Refreshes the connection by running a describe on the source layer and collectin attribute information.
        @return: No Return
        """

        import arcpy
        #describe the input dataset.
        self._arcpyDescribe = []
        try:
            self._arcpyDescribe = arcpy.Describe(self._inputTable)
        except:
            raise DatabaseError("The layer {} does not exist, or can not be read.".format(self._inputTable))
        self._processFields()

        #decide what function to use to get the NumPy Array baesd on the description type (FeatureClass or Table)
        self._inputTableType = None
        if hasattr(self._arcpyDescribe, "dataType"):
            self._inputTableType = self._arcpyDescribe.dataType

        if self._inputTableType not in ('FeatureClass', 'Table', 'FeatureLayer', 'Layer', 'TableView'):
            raise Error("The specified input data type is not supported (%s)" % (str(self._inputTableType)))

        self._status = "open"

    def _get_cursor(self):
        """
        Gets a cursor using the specified where clause, and column list of the connection.
        @rtype : arcpy.da.SearchCursor
        @return: An arcpy DA SearchCursor using the specified where clause and column info.
        """
        try:
            sql_clause = (None, None)
            if hasattr(self, "_orderby"):
                if self._orderby != "":
                    sql_clause = (None, "ORDER BY {}".format(self._orderby))
            import arcpy
            return arcpy.da.SearchCursor(self._inputTable,
                                         self._fieldNames,
                                         where_clause=self._whereClause,
                                         sql_clause=sql_clause)
        except Exception as e:
            raise DatabaseError("Unable to open da.SearchCursor, {}".format(e))

    def cursor(self):
        """
        Returns a cursor object that can be used to iterate over the data source in chunks.  The chunk size
        is managed automatically and is transparent to the cursor user.
        @return: a CursorEsriDAManaged That can be filtered and iterated on.
        """
        if self._status != "open":
            raise Error("Connection is not currently open")

        return CursorEsriDAManaged(self)

    def close(self):
        """
        closes the connection.
        @return: No return
        """
        if self._cursor:
            del self._cursor
        self._cursor = None
        self.data_sets_returned = 0
        self.curr_record_count = 0
        super(ConnectionEsriDAManaged, self).close()


class CursorEsriDAManaged(CursorEsriDA, Iterator):

    def __init__(self, dataSource):
        """
        Creates a new managed cursor using the specified managed connection.  Only managed connections are allowed.
        @param dataSource: a ConnectionEsriDAManaged
        @return: None.
        """
        self._dataSource = dataSource
        if self._dataSource._status != "open":
            raise Error("Connection must be open to open a cursor")
        self._status = "ready"
        self._cursor = None
        self._dataTable = list()
        self.maxRecordCount = self._dataSource.maxRecordCount
        self.description = self._dataSource._dbapi2Describe
        self._internal_get_count = None

    def __getitem__(self, index):
        """
        Returns the row for the specified index.  Please note that if you are using this and an iterator,
        Things will go horribly wrong... :)  An IndexError will be raised if the index is out of range.
        Also, be warned that the index may not represent the entire dataset, since not all of it is held
        in memory.  To be sure you get the entire data set, use an iterator, or the next() function.
        @param index: Integer that represents the row to be returned.
        @return: The row indicated.
        """
        if len(self._dataTable) == 0:
            if not self._query_data():
                raise IndexError('list index is out of bounds')

        try:
            return self._dataTable[index]
        except IndexError:
            raise IndexError('list index is out of bounds')

    def next(self):

        # If we are out of data, or we have not gotten any data yet.
        if len(self._dataTable) == 0:
            # if there is no more data, raise StopIteration
            if not self._query_data():
                raise StopIteration

        return self._dataTable.pop(0)

    if py_version > 2:
        def __next__(self):
            return self.next()

    def _query_data(self):
        """
        Gets the next data set and stores it in self._dataTable.
        @return: False if no more data exists, True if data was added to self._dataTable
        """
        if self._status != "open":
            raise NotSupportedError("You must first execute a query using the execute method before fetching data.")

        # If there are no records in the layer in question, don't bother opening the cursor at all, just return False
        import arcpy
        if not self._internal_get_count:
            self._internal_get_count = int(arcpy.GetCount_management(self._dataSource._inputTable).getOutput(0))
        if self._internal_get_count == 0:
            self.rowcount = 0
            return False

        # reset internal variables.
        self.curr_record_count = 0
        if self._dataTable:
            del self._dataTable
            self._dataTable = list()

        # if we have already reached the end, then just return none.
        if self._cursor_status == "closed":
            return False

        # manually open a cursor and loop over it to retrieve and store the number of records needed to meet
        # maxRecordCount

        continueLoop = True
        while continueLoop:
            currRow = None
            try:
                currRow = self._cursor.next()
            except StopIteration:
                self._cursor_status = "closed"
                break
            self.curr_record_count += 1
            if self.maxRecordCount < 0:
                continueLoop = True
            elif self.curr_record_count < self.maxRecordCount:
                continueLoop = True
            else:
                continueLoop = False
            # save the data from each column into the self._dataTable variable.
            newRow = {}
            for colIndex in range(len(self._dataSource._fieldNames)):
                newRow[self._dataSource._fieldNames[colIndex]] = currRow[colIndex]
            self._dataTable.append(newRow)

        # apply the where clause and order by info to the new dataTable
        for wc in self._whereClause:
            if len(wc) != 2:
                raise InvalidWhereClause()

            self._dataTable = [dictList for dictList in self._dataTable if dictList[wc[0]] == wc[1]]

        if self._orderby != []:
            raise NotImplementedError()

        self.rowcount = len(self._dataTable)
        # if the len of the dataTable is 0, then we need to to do this again.
        if len(self._dataTable) == 0 and self._cursor_status != "closed":
            return self._query_data()
        elif len(self._dataTable) == 0 and self._cursor_status == "closed":
            return False
        return True

    def fetchall(self):
        if self._status != 'open':
            raise Error('You must call execute on the cursor before fetching data.')
        return self

    def execute(self, operation="select", whereClause=list(), orderby=list(), updateSet=list()):
        self._lastOperation = operation
        self._whereClause = whereClause
        self._orderby = orderby
        self._updateSet = updateSet

        if self._status != 'ready':
            raise Error('The cursor is not ready.  ' +
                        'Did you attempt to re-use a cursor, or this cursor is already closed.')

        if self._lastOperation.lower() != 'select':
            raise NotSupportedError("Only Select is supported on CursorEsriDAManaged")

        import arcpy
        if not self._internal_get_count:
            self._internal_get_count = int(arcpy.GetCount_management(self._dataSource._inputTable).getOutput(0))

        self._status = "open"
        self._cursor = self._dataSource._get_cursor()
        self._cursor_status = "open"
        self._query_data()

    def close(self):
        """Close the connection.  The connection will be unusable after calling this.  This also deletes
            the in-memory copy of data, so it will clean up your memory footprint."""
        self._status = "closed"
        self._cursor_status = "closed"
        del self._dataTable
        self._dataTable = None
        if self._cursor:
            del self._cursor
        self._cursor = None

