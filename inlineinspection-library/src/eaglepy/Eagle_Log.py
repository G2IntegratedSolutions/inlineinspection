from __future__ import unicode_literals
from __future__ import print_function
import sys
import datetime
import os

class EagleLog():
    """A class for simplified logging in python and in arcpy"""
    def __init__(self, file=None, db=None, params=["PRINT","FILE"], datetimeformat="%Y-%m-%d %H:%M:%S.%f"):
        """Creates a default EagleLog object.  By default the log will write to a file in the users temp directory
        and will be printed to the screen on standard output.
        file - The file where the log should be written to.  By default a temp file will be created.  If
            you want to make your own file, pass the full path to it here, and it will be appended to.
        db - The ArcGIS ".sde" file where the eaglepy logging table is.  All messages will be logged to this
        table if it is specified.  (specifying a table automatically adds "DB" to the param list.
        params - The list of methods that should be used for logging:
                FILE - Write the message to a file, either one in the user's temp directory, or one specified by the file argument
                PRINT - print the log to standard output
                DB - Write the message to a db table (the db argument must be specified as well).  If you specify a db, then you do not need to add the parameter
                    it will be added for you.
                ARCPY - Writes the message out to the arcpy.AddMessage method.  If arcpy has already been imported, it will automatically be added.
        datetimeformat - The formate string according to the python docs from: 8.1.7. strftime() and strptime() Behavior, default is: %Y-%m-%d %H:%M:%S.%f"""

        self._log_location_file = file
        self._log_location_db = db
        self._log_params = params
        self._datetime_format = datetimeformat

        # configure database:
        if (self._log_location_db != None):
            self._log_params.append("DB")

        # check for arcpy
        try:
            import arcpy
            # arcpy.AddMessage("Start Logging from EagleLog")
            self._log_params.append("ARCPY")
        except:
            pass

        # configure file
        # if FILE is specified, and file location is none, then create it
        if("FILE" in self._log_params) and (self._log_location_file == None):
            import tempfile
            tf = tempfile.NamedTemporaryFile(mode='a', prefix="EagleLog_", suffix=".log", delete=False)
            self._log_location_file = tf.name
            tf.close()

        # self.addMessage("START EAGLELOG")

    def addParam(self,param):
        """Adds a logging destination.  Must be in the list: ARCPY, FILE, PRINT, DB"""
        try:
            if param not in self._log_params:
                self._log_params.append(param)
        except ValueError:
            pass

    def removeParam(self,param):
        """Removes a logging destination.  If the destination was not in the list, nothing will happen"""
        try:
            if param in self._log_params:
                self._log_params.remove(param)
        except ValueError:
            pass

    def addMessage(self,msg):
        """Adds a string message to the current logging context, as specified in the constructor
        msg - the string that should be added to the log"""
        for logType in self._log_params:
            try:
                getattr(self, "_addMessage_%s" % (logType))(msg)
            except:
                print(sys.exc_info())
                raise Exception("Unable to add message to: %s" % (logType))

    def _addMessage_FILE(self, message):
        """Adds the specified message to the file specified in __log_location_file"""
        try:
            file = open(self._log_location_file,"a")
            d = datetime.datetime.now()
            ds = d.strftime(self._datetime_format)
            file.write("%s   INFO    %s\n" % (str(ds), str(message)))
            file.close()
        except:
            raise Exception("Unable to write to file: %s" % self._log_location_file)

    def _addMessage_PRINT(self, message):
        """Prints the specified message to standard output using the print command"""
        d = datetime.datetime.now()
        ds = d.strftime(self._datetime_format)
        print(ds, "INFO ", message)

    def _addMessage_DB(self, message):
        """Adds the specified message to the database table specified"""
        raise Exception("DB logging not yet immplemented")

    def _addMessage_ARCPY(self, message):
        """Adds the specified message to the arcpy.AddMessage method"""
        try:
            import arcpy
            arcpy.AddMessage(message)
        except:
            print(sys.exc_info())
            raise Exception("Unable to write to arcpy.")

    def addWarning(self, msg):
        """Adds a string message to the current logging context, as specified in the constructor
        msg - the string that should be added to the log"""
        for logType in self._log_params:
            try:
                getattr(self, "_addWarning_%s" % (logType))(msg)
            except:
                print(sys.exc_info())
                raise Exception("Unable to add warning to: %s" % (logType))

    def _addWarning_FILE(self, message):
        """Adds the specified message to the file specified in __log_location_file"""
        try:
            file = open(self._log_location_file, "a")
            d = datetime.datetime.now()
            ds = d.strftime(self._datetime_format)
            file.write("%s   WARN    %s\n" % (str(ds), str(message)))
            file.close()
        except:
            raise Exception("Unable to write to file: %s" % self._log_location_file)

    def _addWarning_PRINT(self, message):
        """Prints the specified message to standard output using the print command"""
        d = datetime.datetime.now()
        ds = d.strftime(self._datetime_format)
        print(ds,"WARN ", message)

    def _addWarning_DB(self, message):
        """Adds the specified message to the database table specified"""
        raise Exception("DB logging not yet immplemented")

    def _addWarning_ARCPY(self,message):
        """Adds the specified message to the arcpy.AddMessage method"""
        try:
            import arcpy
            arcpy.AddWarning(str(message))
        except:
            print(sys.exc_info())
            raise Exception("Unable to write to arcpy.")

    def addError(self,msg):
        """Adds a string message to the current logging context, as specified in the constructor
        msg - the string that should be added to the log"""
        for logType in self._log_params:
            try:
                getattr(self,"_addError_%s"%(logType))(msg)
            except:
                print(sys.exc_info())
                raise Exception("Unable to add error to: %s"%(logType))

    def _addError_FILE(self, message):
        """Adds the specified message to the file specified in __log_location_file"""
        try:
            file = open(self._log_location_file,"a")
            d = datetime.datetime.now()
            ds = d.strftime(self._datetime_format)
            file.write("%s   ERROR   %s\n" % (str(ds), str(message)))
            file.close()
        except:
            raise Exception("Unable to write to file: %s"%self._log_location_file)

    def _addError_PRINT(self, message):
        """Prints the specified message to standard output using the print command"""
        d = datetime.datetime.now()
        ds = d.strftime(self._datetime_format)
        print(ds,"ERROR", message)

    def _addError_DB(self, message):
        """Adds the specified message to the database table specified"""
        raise Exception("DB logging not yet immplemented")

    def _addError_ARCPY(self, message):
        """Adds the specified message to the arcpy.AddMessage method"""
        try:
            import arcpy
            arcpy.AddError(str(message))
        except:
            print(sys.exc_info())
            raise Exception("Unable to write to arcpy.")

    def getLogFileLocation(self):
        return self._log_location_file

