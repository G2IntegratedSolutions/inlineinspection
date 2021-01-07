import eaglepy
import os

__version__ = '0.0.1'

class _BaseLRObject(object):
    """Basic object for Linear Referencing library, eaglepy.lr"""

    #indicates if the _AddDebug Method is printed to eaglepy.AddMessage
    _debug = False

    def __init__(self, **kwargs):
        """Creates a new _BaseLRObject.  Searches for debug indications, something that tells the system to turn debuging on.
            Search Order for Debug Indication:
                1) - A file called eaglepy.debug at c:\\eaglepy.debug"""
        if os.path.exists("c:\\eaglepy.debug"):
            self._debug = True

    def _addLog(self,message):
        """Adds the specified message to the current logging system via eaglepy.AddMessage"""
        #TODO: REMOVE THIS TO MAKE IT JUST ADD MESSAGE AGAIN
        import datetime
        d = datetime.datetime.now()
        ds = d.strftime("%Y-%m-%d %H:%M:%S.%f")
        tmpMsg = "{} - {}".format(message, ds)
        eaglepy.AddMessage(tmpMsg)

    def _addWarning(self,message):
        """Adds the specified message to the current logging system via eaglepy.AddWarning"""
        eaglepy.AddWarning(message)

    def _addError(self,message):
        """Adds the specified message to the current logging system via eaglepy.AddError"""
        eaglepy.AddError(message)

    def _AddDebug(self,message):
        """If self._debug is True, the specified message is added via eaglepy.AddMessage, if false, nothing happens."""
        if self._debug:
            eaglepy.AddMessage(message)




################################################################################
##Exceptions are defined below
##
################################################################################
class LinearReferencingException(eaglepy.Error):
    """Base linear referencing exception."""
    _lr_details = ""
    _lr_description = ""

    def __init__(self,description,details=""):
        eaglepy.Error.__init__(self,description)
        self._lr_description = description
        self._lr_details = details

    def __str__(self):
        return str(self._lr_description) + " - " + str(self._lr_details)

class MethodNotDefined(LinearReferencingException):
    """Indicates that the method is not defined in a parent object, and should be defined in the child."""
    def __init__(self,methodName):
        LinearReferencingException.__init__("METHOD: "+methodName)

