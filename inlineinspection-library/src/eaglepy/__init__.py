# imports (These are imports that are always used!)
import os
import sys
import datetime
#import sys
#raise Exception("TEST" + str(sys.path))
#import Eagle_Log

from eaglepy.Eagle_Log import EagleLog

py_version = sys.version_info[0]
if py_version <= 2:
    import exceptions

__version__ = '1.1.10'

# configure logging
_eagleLog = EagleLog()

# configure eaglepy environment
_eimEnv = {}

# workspace location
_workspaceFile = ""

# Utm cache dictionary
_utmCache = dict()

# Global list to keep track of random table names that are generated
_tableNames = list()

#eaglepy_license = get_eaglepy_license()
#eaglepy_license.validate_with_exception()

# end init code
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# logging procedures
def AddMessage(message):
    """Adds a string message to the current logging system or systems."""
    _eagleLog.addMessage(message)

def AddWarning(message):
    """Adds a string warning to the current logging system or systems."""
    _eagleLog.addWarning(message)

def AddError(message):
    """Adds a string error to the current logging system or systems."""
    _eagleLog.addError(message)

def GetLogFileLocation():
    """Returns the current file that the logs are being written to."""
    return _eagleLog.getLogFileLocation()

def SetLogFileLocation(fileLocation,delete=True):
    """Sets the log file to a new logging location.  If delete is true (default) the previous log file will be deleted first"""
    if GetLogFileLocation() is not None:
        if(os.path.exists(GetLogFileLocation()) and delete):
            os.remove(GetLogFileLocation())

    _eagleLog = Eagle_Log.EagleLog(file=fileLocation,params=["FILE","PRINT"])

def SetLogToARCPY(remove=False):
    """Adds the parameter "ARCPY" to the log object.  This ensures that logs are sent to arcpy.
    If remove is set to true (default is False) all other log types are rmoved, thus only arcpy.AddMessage is used."""
    if(remove):
        _eagleLog.removeParam("FILE")
        _eagleLog.removeParam("PRINT")
        _eagleLog.removeParam("DB")
    _eagleLog.addParam("ARCPY")

#end logging
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#workspace functions

def CreateNewWorkspace(path=None, setEsri=False):
    """Creates a new File Geodatabase in the temp directory (or in the path if specified).  Returns the full path to the gdb.
        path - (optional) a path to a folder where the scratchworkspace should be created."""
    wsPath = path
    if(path==None):
        #create a path
        import tempfile
        wsPath = os.path.join(tempfile.gettempdir(), "EagleScratch")

    #create containing folder
    if (os.path.exists(wsPath) == False):
        os.makedirs(wsPath)

    scratchDBName = MakeRandomFileName()
    scratchDB = os.path.join(wsPath,scratchDBName+".gdb")

    import arcpy
    arcpy.CreateFileGDB_management(wsPath, scratchDBName, "CURRENT")
    #setup arcmap workspace
    if(setEsri):
        arcpy.env.workspace = scratchDB
        arcpy.env.scratchWorkspace = scratchDB
    _workspaceFile = scratchDB
    return _workspaceFile

def GetCurrentWorkspace(create=True,path=None,setEsri=False):
    """Returns the current path to the workspace gdb.  If there is no workspace, one is created.  If a path is specified, it will be passed to CreateNewWorkspace.
        create (default:true) - Creates a new workspace geodatabase if one does not exist.
        path (default:None) - path where the new workspace geodatabase should be created.  This is passed to CreateNewWorkspace"""
    if (_workspaceFile == ""):
        return CreateNewWorkspace(path,setEsri)
    else:
        return _workspaceFile

#end workspace

#-------------------------------------------------------------------------------
#Begin SQL Functions
def GetSDEConnectionFromFullPath(path,testConnection=True):
    """Given a full path to an SDE FeatureClass, return the path to the connection file (the .SDE file).
        Only 120 levels are supported.  Past 120 levels, an error will be returned, so don't do that...
        this function should also work on personal GDBs and File GDBs.
            path - the path to the feature class, table, etc.
            testConnection (default True) - Specifies if the connection file should be tested before it is returned.  Set this to False for Personal and file GDB."""
    tmpPath = path
    depthCount = 0
    depthMax = 120
    while os.path.exists(tmpPath) == False:
        tmpPath = os.path.dirname(tmpPath)
        #if we have gone more than the depth max, raise an exception.
        depthCount += 1
        if(depthCount > depthMax):
            raise Exception("Too many levels found (max of %s)...This is a bad problem, Geodatabases only have 2 levels, and you are at: %s"%(depthMax,depthCount))

    #if the user specified not to test the connection (default is to test) then return the path.
    if(testConnection == False):
        return tmpPath

    #now that we have the file, test the connection.
    if(TestArcSDEConnectionFromFile(tmpPath)):
        return tmpPath
    else:
        raise Exception("Invalid connection file (%s), failed test."%(tmpPath))

def GetTableNameFromFullPath(path):
    """Returns the table name from a full Esri path to the table.
        path - The full path to the table"""
    return os.path.basename(path)

def TestArcSDEConnectionFromFile(path):
    """Tests a connection to an ARCSde database.  Returns true if the connection worked, false if not.
            path - The full file path to an ArcSDE connection (.SDE file)."""
    #ensure that the file exists first.
    if(os.path.exists(path) == False):
        return False

    try:
        #try the SDE connection.
        import arcpy
        conn = arcpy.ArcSDESQLExecute(path)
        #connection worked, delete the variable.
        try:
            del conn
        except:
            pass
        #return True, connection worked.
        return True
    except:
        #connection failed, return false.
        return False

def CalculateFieldUsingSQLStatic(path,fieldName,fieldValue,whereClause=None,valueType=None):
    """Sets the specified field name to the specified fieldValue (static values only).  If specified, the whereClause is used to filter the update.
        path - The path to the feature class (full path that includes an SDE connection file)
        fieldName - the field to update
        fieldValue - the value to update the field with.
        whereCaluse (Optional) - A where clause to be applied to the table during the update.
        valueType (Optional) - Used to specify if the fieldValue is non static.  For example, SQL indicates that the field value should not be escaped
            and should be used directly inside the sql statement.  This allows you to use native SQL functions within the Update statement.
        ***WARNING: ONLY SUPPORTS NUMBERS AND STRING FIELDS!!!"""

    #make an sde connection
    import arcpy, string
    #get the path to the connection
    connPath = GetSDEConnectionFromFullPath(path)
    tableName = GetTableNameFromFullPath(path)
    if(TestArcSDEConnectionFromFile(connPath) == False):
        raise Exception("Unable to connect to : %s"%(connPath))

    sdeConn = arcpy.ArcSDESQLExecute(connPath)
    #determine if the fieldValue is a number or a string
    dataType = "STRING"
    try:
        tmp = fieldValue
        tmp += 1
        dataType = "NUMBER"
    except:
        dataType = "STRING"

    #clean up the string and/or number fields.
    newFieldValue = ''
    if(dataType == "STRING"):
        newFieldValue = fieldValue
        newFieldValue = string.replace(newFieldValue,"'","''")
        newFieldValue = "'%s'"%(newFieldValue)
    else:
        newFieldValue = fieldValue

    #change the value of the field depending on the specified type
    if(valueType != None):
        if valueType.upper() == 'SQL':
            newFieldValue = fieldValue
        #other valueTypes go here.

    sql = "update %s set %s = %s"%(tableName,fieldName,newFieldValue)
    if(whereClause != None):
        sql = sql +" where %s "%(whereClause)

    try:
        print(sql)
        sqlResults = sdeConn.execute(sql)
        print(sqlResults)
    except:
        raise Exception("Unable to execute SQL: %s"%(str(sys.exc_info())))


#end SQL functions
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#Enviornment functions

def GetEnvironment(name):
    """Tries to get a saved environment value, return None if it does not exist.
        All names are converted to lower case!"""
    try:
        return _eimEnv[name.lower()]
    except:
        return None

def SetEnvironment(name, value):
    """Sets an environment value.  raises an exception if it fails to save.
        All names are converted to lower case!"""
    _eimEnv[name.lower()] = value

def GetEnvironmentAsJson():
    """Returns a json string representing the eagle environment variables.
        All names are in lower case."""
    import json
    return json.JSONEncoder().encode(_eimEnv)

def SetEnvironmentAsJson(newEnvironment):
    """Replaces the environment variables with the specified json representation.
            newEnvironment - The Json string representation (as returned by GetEnvironmentAsJson).
            All names are converted to lower case!"""
    import json
    _eimEnv = {}
    tmp = {}
    tmp = json.JSONDecoder().decode(newEnvironment)
    if py_version <=2:
        for key,value in tmp.iteritems():
            _eimEnv[key.lower()] = value
    else:
        for key,value in list(tmp.items()):
            _eimEnv[key.lower()] = value

#end Environment functions
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
#Managed Executable functions
def ExecuteFile(pathToExe,
                parameters=None,
                maxExecutionTime=10,
                registerSignals=True,
                parallel=False,
                workingDirectory=None):
    """Automatically calls the pathToExe as an executable.  If parallel is set to True, it will be
    executed in a separate thread so as not to block this one.  Beware though, you are responsible
    for managing the parallel threads... see eaglepy.ManagedExe.ManagedExeParallel for details."""
    if parallel == False:
        import eaglepy.ManagedExe
        me = eaglepy.ManagedExe.ManagedExe(pathToExe,
                                           registerSignals=registerSignals,
                                           workingDirectory=workingDirectory)
        me.run(maxExecutionTime,parameters)
    else:
        import eaglepy.ManagedExe
        pme = eaglepy.ManagedExe.ManagedExeParallel(pathToExe,registerSignals=registerSignals)
        pme.prepRun(maxExecutionTime,parameters)
        pme.start()


#end Managed Executable functions
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
#Misc functions
def StringToDecimalOrNone(value):
    from decimal import Decimal
    if str(value) == '#':
        return None
    try:
        return Decimal(value)
    except Exception as e:
        AddWarning(e)
        return None

def MakeRandomGUID():
    """Returns a random guid, including the curly brackets around the string, and in upper case"""
    import uuid
    return "{"+str(uuid.uuid4()).upper()+"}"

def MakeRandomFileName():
    """Returns a random file name (a random guid).  You must append your own extension if you wish to add one."""
    return MakeRandomGUID()

def MakeRandomNumber(min=0,max=9999):
    """Returns a random integer between 0 and 9999 or between min and max if specified"""
    import random
    return random.randint(min,max)

def MakeRandomTableName(baseName=None):
    """Creates a random table name that is safe to use in an MDB, FileGeodatabae, Oracle or SQLServer database.
    This function does NOT check for the existance of such a table, but does create a random one.  If base is provided,
    then a random number between 0 and 9999 is appended to the end of the base.  If base is not provided, then a randon
    string is fist calculated, then a random number between 0 and 9999 is appended to the end.  if no base is provided, then
    the string will always start with ER for "Eagle Random" """
    global _tableNames

    if(baseName == None):
        import base64
        rs = base64.urlsafe_b64encode(os.urandom(8))
        name = "ER%s%s"%(rs[:-2].upper(),str(MakeRandomNumber()))
        while(name in _tableNames):
            name = "ER%s%s"%(rs[:-2].upper(),str(MakeRandomNumber()))
        _tableNames.append(name)
        return name
    else:
        #remove any characters that are not a-Z, 0-9
        import string
        if type(baseName) is str:
            cleanBaseName = baseName.translate(string.maketrans("",""), string.punctuation)
        else:
            if py_version <=2:
                if type(baseName) is unicode:
                    import sys
                    import unicodedata
                    tbl = dict.fromkeys(i for i in xrange(sys.maxunicode)
                        if unicodedata.category(unichr(i)).startswith('P'))
                    cleanBaseName = str(baseName.translate(tbl))
            else:
                if type(baseName) is str(baseName, 'utf-8'):
                    import sys
                    import unicodedata
                    tbl = dict.fromkeys(i for i in range(sys.maxunicode)
                        if unicodedata.category(chr(i)).startswith('P'))
                    cleanBaseName = str(baseName.translate(tbl))

        name = "%s%s"%(cleanBaseName,str(MakeRandomNumber()))
        while(name in _tableNames):
            name = "%s%s"%(cleanBaseName,str(MakeRandomNumber()))
        _tableNames.append(name)
        return name

def RemovePunctuation(inputString):
    """Removes punctuation from a string while leaving the rest in tact."""
    import string
    return inputString.translate(string.maketrans("",""), string.punctuation)

def GetCurrentDateTimeStamp(dateTimeFormat="%Y-%m-%d %H:%M:%S.%f"):
    d = datetime.datetime.now()
    ds = d.strftime(dateTimeFormat)
    return str(ds)


def GetEaglepyDataFolder():
    import os
    return os.path.join(os.path.dirname(__file__), "data")


def AddField(input_table, field):
    import arcpy
    if getattr(field, 'isNullable', True):
        nullable = 'NULLABLE'
    else:
        nullable = 'NON_NULLABLE'

    # there is a bug in 10.2.1 and lower (sum is 13) that prevents us from adding non_nullable fields, so we have
    # to protect against that bug.
    if nullable == 'NON_NULLABLE' and sum([int(i) for i in GetArcpyVersion().split('.') ]) <= 13:
        nullable = 'NULLABLE'
    arcpy.AddField_management(input_table,
                                      field.name,
                                      field.type,
                                      field.precision,
                                      field.scale,
                                      field.length,
                                      field.aliasName,
                                      nullable,
                                      'NON_REQUIRED',
                                      field.domain)

def AddField_management(in_table, field_name, field_type, *args):
    """
    Function intended to replace the arcpy.AddField_management
    Handles existing field names by adding _x to the end to create unique field name
    Use with the same parameters as arcpy.AddField_management
    http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#//001700000047000000
    """
    import arcpy

    fields_list = ListFields(in_table)
    x = 0
    new_field_name = field_name

    while is_value_in_list(new_field_name,fields_list):
        x += 1
        new_field_name = field_name + "_" + str(x)

    optional_parameters_string = ''
    for optional_parameter in args:
        optional_parameters_string = optional_parameters_string + ", \'{0}\'".format(optional_parameter)

    arcpy.AddField_management(in_table, new_field_name, field_type, optional_parameters_string)

    return new_field_name

def is_value_in_list(value, valuelist):
    for element in valuelist:
        if element == value:
            return True
    return False

def IsNull(test, default='', allow_blank=True):
    """
    If test is None, return the default value, if not None, return Test.
    """
    if test is None:
        return default
    if allow_blank and test == '':
        return default
    return test


def truncate(f, n):
    """
    Truncates/pads a float f to n decimal places without rounding
    From this amazing SO post on floating point numbers
    http://stackoverflow.com/questions/783897/truncating-floats-in-python
    If you don't understand why we need this, then don't touch it!
    """
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])


def ListFields(file_path):
    import arcpy
    cursor = arcpy.da.SearchCursor(file_path, "*", "1=0")
    field_list = cursor.fields
    del cursor
    return field_list


def GetUTMForGeometry(test_geometry):
    """
    Tests to see if the Geometry specified is within a UTM, and returns the Projection name of the UTM that it exists in
    or returns None if the Geometry is not in a UTM.
    """
    import arcpy
    geom = test_geometry.projectAs(arcpy.SpatialReference(4326)).centroid
    global _utmCache
    if len(_utmCache) == 0:
        ## query the utm layers from the gdb and store them
        cPath = os.path.join(GetEaglepyDataFolder(), "projections.gdb", "PCSData")
        c = arcpy.da.SearchCursor(in_table=cPath,
                                  field_names=["CRS_CODE", "SHAPE@"],
                                  where_clause="Proj_Type = 'UTM - 1983'")
        for aUtm in c:
            _utmCache[aUtm[0]] = aUtm[1]
        del c

    ## For each utm zone, check to see if it contains the geometry
    if py_version <= 2:
        for name, shape in _utmCache.iteritems():
            if shape.contains(geom):
                return name
    else:
        for name, shape in list(_utmCache.items()):
            if shape.contains(geom):
                return name
    return None


def StringToBool(string):
    """Converts the specified string to a boolean value."""
    if isinstance(string, bool):
        return string
    if string.lower().strip()[0] == u't':
        return True
    else:
        return False


def FindParameterByName(parameterList, parameterName):
    """Searches through the parameter list specifeid and returns the one with the
    name specified.  Returns None if a matching parameter was not found.s"""
    for p in parameterList:
        if p.name == parameterName:
            return p
    return None


def GetParametersForToolboxTool(tool_name):
    import arcpy
    data = arcpy.Usage(tool_name)
    if data.find("Method {} not found.".format(tool_name)) > 0:
        raise Exception("Tool not found.")
    if not data.find("(") > -1 and not data.find(")") > -1:
        raise Exception(data)
    # Parse data to get the list of parameters and return them
    parameter_list = data.split("(")[1].split(")")[0].split(',')
    parameter_final_list = list()
    for parameter_name in parameter_list:
        parameter = parameter_name.strip()
        parameter_metadata = dict()
        parameter_metadata["required"] = True

        if parameter.startswith("{") and parameter.endswith("}"):
            parameter_metadata["required"] = False
            parameter = parameter.strip("{")
            parameter = parameter.strip("}")
        parameter_metadata["name"] = parameter
        parameter_final_list.append(parameter_metadata)
    return parameter_final_list

def BuildOrWhereClauseFromList(column_name, option_list, quote_options=True):
    if option_list is None or len(option_list) == 0:
        return ""
    sql_string = ""
    for option in option_list:
        if option is None:
            sql_string += " is NULL OR"
            continue
        if quote_options:
            sql_string += "{} = '{}' OR ".format(column_name, option)
        else:
            sql_string += "{} = {} OR ".format(column_name, option)
    sql_string = sql_string[:-3]
    return "({})".format(sql_string)


def GetArcpyVersion():
    import arcpy
    return arcpy.GetInstallInfo().get('Version', '10.2.1')


def StripReturnsAndTabs(input_string):
    """
    Strips all Returns and tabs from the input string and replaces them with spaces.  The following are replaced
    with spaces: \n, \r \t.  If the input_string is None, and empty string will be returned.
    """
    if input_string is None:
        return ''
    str_value = str(input_string)
    str_value = str_value.replace("\n", " ")
    str_value = str_value.replace("\r", " ")
    str_value = str_value.replace("\t", " ")
    return str_value

def multi_key_sort(items, columns):
    """
    Sort algorithm to sort a list of dictionaries
    Add - in front of the column to sort in descending order
    :param items: list of dictionaries
    :param columns: list of columns to sort by
    :return:
    """
    from operator import itemgetter
    if py_version > 2:
        from functools import cmp_to_key
    comparers = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]

    def gmv(*args):
        import eaglepy.DataSource
        specified_type = None
        for test_type in args:
            if test_type is not None:
                specified_type = test_type
                break
        if specified_type is None:
            # All compare values are None, simply return -inf for all of them
            return -float("inf")
        # Use this value to determine the type, and return the appropriate minimum value for this type
        data_type = eaglepy.DataSource.convertDataTypeToEsriDataType(specified_type)
        if data_type in ["STRING"]:
            return ""
        elif data_type in ["LONG", "FLOAT", "SHORT", "DOUBLE"]:
            return -float("inf")
        elif data_type in ["DATE"]:
            return datetime.datetime(datetime.MINYEAR, 1, 1)

    def comparer(left, right):
        for fn, mult in comparers:
            min_value = gmv(fn(left), fn(right))
            if py_version <=2:
                result = cmp(fn(left) or min_value, fn(right) or min_value)
            else:
                a = fn(left) or min_value
                b = fn(right) or min_value
                result = (a > b) - (a < b)
            if result:
                return mult * result
        else:
            return 0
    if py_version <=2:
        return sorted(items, cmp=comparer)
    else:
        return sorted(items, key=cmp_to_key((comparer)))

def is_number(s):
    """
    Function checks if a text is a number or not.
    :param s: text to be checked
    :return: True if text is number, False if text is not number
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


#end Misc Functions
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
#start Conversion Functions

def Convert(fromNumber, rate):
    """Converts the fromNumber to another number by multiplying it by the rate.
    This function will always return a float"""
    return float(fromNumber) * float(rate)

def ConvertFeetToMeters(feet):
    """Converts Feet to Meters by multiplying feet by 0.3048"""
    return Convert(feet, 0.3048)

def ConvertMetersToFeet(meters):
    """Converts Meters to Feet by multiplying meters by 3.28084"""
    return Convert(meters, 3.28084)

#end Conversion Functions
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#Import Functions


def _get_toolbox_path():
    import os.path
    return os.path.join(os.path.dirname(__file__), "ESRI", "TOOLBOXES", "eaglepy.pyt")


def toolbox_need_reload():
    import arcpy
    from . import toolbox_loader
    for tool in toolbox_loader.TOOL_LIST:
        if not hasattr(arcpy, "{}_eaglepy".format(tool)):
            return True
    return False


def add_toolbox():
    import arcpy
    if not toolbox_need_reload():
        return
    ## List toolboxes to see if eaglepy is already there.
    eaglepy_toolbox = arcpy.ListToolboxes("eaglepy")
    if len(eaglepy_toolbox) == 1:
        arcpy.RemoveToolbox(_get_toolbox_path())

    arcpy.AddToolbox(_get_toolbox_path())
    return


#end Import Functions
#-------------------------------------------------------------------------------
if py_version <=2:
    class Error(exceptions.StandardError):
        pass
else:
    class Error(Exception):
        pass