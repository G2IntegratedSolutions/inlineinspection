import arcpy
import eaglepy
import numpy
import os
import time
import eaglepy.DataSource

class DataAccessException(Exception):
    pass

class TableAlreadyExists(DataAccessException):
    pass

class CouldNotCreateTable(DataAccessException):
    pass

#arcpy.da.NumPyArrayToTable(array, "c:/data/gdb.gdb/out_table")
def NumPyArrayToTable(in_array, out_table):
    """Exports a numpy array to the geodatabase table specified.  The table must not already exist.
    If it does exist, nothing will happen, and an error will be raised.
    """
    if arcpy.Exists(out_table) == True:
        raise TableAlreadyExists("The specified table (%s) already exists."%(out_table))

    #get the columns from the numpy array
    columnList = []#list of columns that exist in the output.  Each item in the list is a tuple where
        #the first item is the name, and the second item is the data type in numpy format.


    #create the output table using the columns specified in the list of columns
    try:
        arcpy.CreateTable_management(os.path.dirname(out_table),os.path.basename(out_table))
    except Exception as e:
        raise CouldNotCreateTable("Could not create table %s.  Details: %s"%(out_table,str(e)))



def EaglepyConnectionToTable(in_connection,
                             out_table,
                             output_columns = list(),
                             log_object = None,
                             append = False,
                             use_all_columns = False,
                             geometry_type = None,
                             spatial_reference = None):
    """
       Exports an eaglepy.DataSource.Connection object to an Esri Object class on disk.
       @param in_connection: The eaglepy.DataSource.Connection object.
       @param out_table: The full path of the table to output.  If this table already exists, an error will be thrown
           unless append is set to true, then the data will be appended (the schema must match exactly).
       @param output_columns: An optional list of arcpy.Field objects used to specify the data types of the fields created
           by the tool.  Only these columns will be outputted.  If use_all_columns is set, these columns will be combined
           with the columns from the describe of the in_connection parameter to make a global set of unique columns for the new
           table.  If not specified, all columns in the describe will be used instead.
       @param log_object: If specified this object must have an _addErrorToLog method.  It will be called if an error
           occurs.
       @param append:  If True, the data will be appended to an existing table, if False and the table exists, an error
           is raised.  If True and the table does not exist, it is still created.
       @param use_all_columns:  If True, the output_columns list will be combined with the describe results from the
           connection.  If False either output_columns (if set) or the describe output will be used to create the table.
       @return:None
   """

    if arcpy.Exists(out_table) == True and append == False:
        raise TableAlreadyExists("The specified table (%s) already exists."%(out_table))

    cur = in_connection.cursor()
    cur.execute()
    ##Create the field list as a list of tuples, the 0th item should be the name, the 1st item should be an
    # arcpy.Field object.

    uniqueColumnList = list() ##a list of column names
    columnList = list() ## a list of tuples: (column_name, arcpy.Field object)
    if output_columns is not None and len(output_columns) > 0:
        #use these columns for sure.
        for aCol in output_columns:
            n1 = list()
            n1.append(aCol.name)
            n1.append(aCol)
            if aCol.name.lower() not in [a.lower() for a in uniqueColumnList]:
                columnList.append(n1)
                uniqueColumnList.append(aCol.name)

        #if use_all_columns is true, mix in the columns from the describe
        if use_all_columns:
            #get the columns from the input connection
            for aCol in cur.description:
                if aCol[0] not in uniqueColumnList:
                    ## add the column and make the arcpy.Field object for it.
                    n1 = list()
                    n1.append(aCol[0])
                    n1.append(ArcpyFieldFromAttributes(name=aCol[0],
                                                       aliasName=aCol[0],
                                                       type=eaglepy.DataSource.convertDataTypeToEsriDataType(aCol[1]),
                                                       length=4000))
                    if aCol[0].lower() not in [ a.lower() for a in uniqueColumnList]:
                        columnList.append(n1)
                        uniqueColumnList.append(aCol[0])
    else:
        ## use only the columns from the describe
        #get the columns from the input connection
        for aCol in cur.description:
            ## add the column and make the arcpy.Field object for it.
            n1 = list()
            n1.append(aCol[0])
            n1.append(ArcpyFieldFromAttributes(name=aCol[0],
                                               aliasName=aCol[0],
                                               type=eaglepy.DataSource.convertDataTypeToEsriDataType(aCol[1]),
                                               length=4000))
            columnList.append(n1)
            uniqueColumnList.append(aCol[0])

    # Is there a geometry column?
    if geometry_type is None:
        destinationColumnList = uniqueColumnList
    else:
        destinationColumnList = list()
        for aCol in columnList:
            if aCol[1].type.lower() == "geometry":
                name = "Shape@"
            else:
                name = aCol[0]
            destinationColumnList.append(name)

    ## if append is set to false, then the table needs to be created.
    if not arcpy.Exists(out_table):
        #create the output table using the columns specified in the list of columns
        try:
            if geometry_type is None:
                arcpy.CreateTable_management(os.path.dirname(out_table),os.path.basename(out_table))
            else:
                arcpy.CreateFeatureclass_management(os.path.dirname(out_table),
                                                    os.path.basename(out_table),
                                                    geometry_type,
                                                    "#",
                                                    "ENABLED",
                                                    "ENABLED",
                                                    spatial_reference)
        except Exception as e:
            raise CouldNotCreateTable("Could not create table %s.  Details: %s"%(out_table,str(e)))

        eaglepy.AddMessage("Table {} Created, adding columns.".format(out_table))

        # Add fields
        turnOnSleep = False
        sleepValue = .85
        for aColumn in columnList:
            # If the column type is Geometry don't do anything with it.
            if aColumn[1].type.lower() == "geometry":
                continue

            ## Change OID fields to LONG, since the OID field was already created by the create table command.
            if aColumn[1].type == "OID":
                aColumn[1].type = "LONG"

            eaglepy.AddMessage("Adding Column {} of type {}".format(aColumn[1].name, aColumn[1].type))
            try:
                if turnOnSleep:
                    time.sleep(sleepValue)
                arcpy.AddField_management(out_table,
                                          aColumn[1].name,
                                          aColumn[1].type,
                                          aColumn[1].precision,
                                          aColumn[1].scale,
                                          aColumn[1].length,
                                          aColumn[1].aliasName
                )
            except Exception as e:
                try:
                    if turnOnSleep:
                        raise e
                    turnOnSleep = True
                    arcpy.AddField_management(out_table,
                                          aColumn[1].name,
                                          aColumn[1].type,
                                          aColumn[1].precision,
                                          aColumn[1].scale,
                                          aColumn[1].length,
                                          aColumn[1].aliasName
                    )
                except Exception as e:
                    raise e

    #open cursors and add data
    insCursor = arcpy.da.InsertCursor(out_table, destinationColumnList)

    for sourceRow in cur.fetchall():
        #make tuple of current soureRow data
        newRow = ()
        for aColumn in uniqueColumnList:
            newRow = newRow + (sourceRow[aColumn],)
        try:
            insCursor.insertRow(newRow)
        except Exception as e:
            errorString = "A row could not be inserted.  Details:{}; Data:{}".format(str(e), str(newRow))
            eaglepy.AddWarning(errorString)
            if log_object is not None:
                try:
                    log_object._addErrorToLog(
                                            "COULD_NOT_WRITE_ROW",
                                            errorString)
                except:
                    eaglepy.AddWarning("Unable to write to error log.")


    del insCursor
    cur.close()


def ArcpyFieldFromAttributes(**kwargs):
    """Sets the keyword arguments specified onto a new arcpy.Field object and
    returns that field object."""
    f = arcpy.Field()
    for key, value in kwargs.items():
            setattr(f, key, value)
    return f

def AddArcpyFieldByAttributes(input_table, name, type, **kwargs):
    arcpy.AddField_management(input_table,
                              name,
                              type,
                              kwargs.get('precision', None),
                              kwargs.get('scale', None),
                              kwargs.get('length', None),
                              kwargs.get('aliasName', None),
                              kwargs.get('nullable', 'NULLABLE'),
                              kwargs.get('required', 'NON_REQUIRED'),
                              kwargs.get('domain', None)
    )
    return input_table


def AppendArcpyFieldToLayer(layer, field):
    """
        Appends the specified arcpy.Field object to the specified layer (table or feature class)
        Using arcpy.AddField.
    """
    arcpy.AddField_management(in_table=layer,
                              field_name=field.name,
                              field_type=field.type,
                              field_precision=field.precision,
                              field_scale=field.scale,
                              field_length=field.length,
                              field_alias=field.aliasName,
                              field_is_nullable=field.isNullable,
                              field_is_required=field.required,
                              field_domain=field.domain)