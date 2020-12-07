from inlineinspection.pressurecalculator.pressurecalculator import PressureCalculator

import os
import inlineinspection
from .inlineinspectionlog import InLineInspectionLog

params = ["FILE"]
_inlineinspection_log = InLineInspectionLog(params=params)


# logging procedures
def AddMessage(message):
    """Adds a string message to the current logging system or systems."""
    _inlineinspection_log.addMessage(message)


def AddWarning(message):
    """Adds a string warning to the current logging system or systems."""
    _inlineinspection_log.addWarning(message)


def AddError(message):
    """Adds a string error to the current logging system or systems."""
    _inlineinspection_log.addError(message)


def GetLogFileLocation():
    """Returns the current file that the logs are being written to."""
    return _inlineinspection_log.getLogFileLocation()


def SetLogFileLocation(fileLocation,delete=True):
    """Sets the log file to a new logging location.  If delete is true (default) the previous log file will be deleted first"""
    if GetLogFileLocation() is not None:
        if(os.path.exists(GetLogFileLocation()) and delete):
            os.remove(GetLogFileLocation())

    _eagleLog = InLineInspectionLog(file=fileLocation,params=["FILE","PRINT"])


def SetLogToARCPY(remove=False):
    """Adds the parameter "ARCPY" to the log object.  This ensures that logs are sent to arcpy.
    If remove is set to true (default is False) all other log types are rmoved, thus only arcpy.AddMessage is used."""
    if(remove):
        _inlineinspection_log.removeParam("FILE")
        _inlineinspection_log.removeParam("PRINT")
        _inlineinspection_log.removeParam("DB")
    _inlineinspection_log.addParam("ARCPY")

#end logging


def list_to_string(inlist):
    lststr = ", ".join(str(x) for x in inlist)
    return lststr


def get_utmfrom_point(inpoint):
    try:
        utmzone = str(int(inpoint.X + 186.0) // 6) + ('S' if (inpoint.Y < 0) else 'N')
        return ("WGS 1984 UTM Zone " + utmzone)

    except Exception as e:
        inlineinspection.AddError("Error getting UTM Zone.")
        raise

def check_int_value(in_val):
    try:
        value = int(in_val)
        return True
    except:
        return False

def get_gdb_name(workspace):
    try:
        dir_name = os.path.dirname(workspace)
        base_name = os.path.basename(workspace)
        base_name_no_gdb = base_name
        index = base_name.rfind(".")
        if index > 0:
            base_name_no_gdb = base_name[0:index]

        base_name_gdb = base_name_no_gdb + ".gdb"
        return  dir_name, base_name_gdb

    except Exception as e:
        inlineinspection.AddError("Failed to run get_gdb_name.")
        raise

def get_field_names(inlayer):
    # get the fields names (uppercase) list
    import arcpy
    try:
        return [f.name.upper() for f in arcpy.ListFields(inlayer)]
    except Exception as e:
        inlineinspection.AddError("Error getting fields names.")
        raise


# def unique_values(inlayer, infield):
#     import arcpy
#     with arcpy.da.SearchCursor(inlayer, [infield]) as cursor:
#         return sorted({int(row[0]) for row in cursor})

def get_unique_values(intable, infield):
    """
        Gets unique values in the table for given field name
        :param intable: input table
        :param infield: input field name
        :return: list of unique values
    """
    import arcpy
    try:
        with arcpy.da.SearchCursor(intable, [infield]) as cursor:
            return sorted({row[0] for row in cursor})

    except Exception as e:
        inlineinspection.AddError("Failed to process {}. \n{} ".format("get_unique_values", arcpy.GetMessages(2)))
        raise