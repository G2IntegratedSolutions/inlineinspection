from __future__ import unicode_literals
import arcpy
import arcpy.sa
import numpy
from .. import eaglepy
import json
from decimal import Decimal
import os
# #from .DjangoHelper import (configure_pipeline_m_domain,
#                            unconfigure_pipeline_m_domain,
#                            configure_pipeline_z_domain,
#                            unconfigure_pipeline_z_domain)
from os.path import join
temp_fc_location = "%scratchGDB%"

def centerline_to_control_points(input_polyline, route_id_column, begin_station_column, end_station_column,
                              out_path, out_name, output_spatial_reference_wkid, station_measure_unit="Feet"):
    """
    Takes a centerline and explodes it into points, calculates X, Y, Z and M and stationing. Exports everything into a
    PointZM feature class
    :param input_polyline: path to the polyline to be used as input centerline
    :param route_id_column: column that contains an ID for the route, usually name. This is required!
    :param begin_station_column: the begin station column, if it exists, otherwise None
    :param end_station_column:  the end station column if it exists, otherwise None
    :param out_path: the path to the workspace where the output will be saved
    :param out_name: the name of the output PointZM feature class
    :param output_spatial_reference_wkid: the spatial reference WKID of the output, if wished to be changed.
                                          To keep it the same as the input use None
    :param station_measure_unit: the unit for measure and stationing. Default is Feet
    :return: out_feature_class: the feature class containing the control points derived from the input_polyline
    """

    #create temporary feature class in scratch gdb to be projected
    try:
        temp_projected_table_name = eaglepy.MakeRandomTableName("ctcp")
        temp_projected_output = join(temp_fc_location, temp_projected_table_name)
        clean_up_temporary_data(temp_projected_output)
    except Exception as e:
        arcpy.AddError("Unable to create temporary output in scratch workspace. "
                       "Make sure scratch workspace is set up on the machine and you have permissions to edit it")
        raise e

    #project input feature class to the temp feature class
    temp_projected_output = project_to_utm(input_polyline, temp_projected_output)

    #add a LENGTH field and calculate it based on the unit provided in the parameters
    arcpy.AddField_management(temp_projected_output, 'LENGTH', 'DOUBLE')
    calculate_field_expression = "!shape.length@{0}!".format(station_measure_unit.lower())
    arcpy.CalculateField_management(temp_projected_output, 'LENGTH', calculate_field_expression, "PYTHON_9.3")

    #run create routes tool to create measures for polyline
    #if unable to create in memory feature class, create it in scratch
    temp_in_memory_table_name = None
    try:
        temp_in_memory_output = r"in_memory\export_file"
    except:
        temp_in_memory_table_name = eaglepy.MakeRandomTableName("ctcpim")
        temp_in_memory_output = join(temp_fc_location, temp_in_memory_table_name)

    # Use LENGTH as the backup route_id_column in case the user doesn't set one up.
    # This will only be valid when the function is called directly. If in toolbox, this will be a required field
    if route_id_column is None:
        route_id_column = "LENGTH"
    # check that the route_id is not null
    cursor = arcpy.da.SearchCursor(input_polyline, [route_id_column])
    row = cursor.next()
    if row[0] is None:
        route_id_column = "LENGTH"
    del cursor

    try:
        arcpy.CreateRoutes_lr(temp_projected_output, route_id_column, temp_in_memory_output,
                              "ONE_FIELD", "LENGTH", None, "UPPER_LEFT")
    except Exception as e:
        arcpy.AddError("Unable to run CreateRoutes_lr tool. Please refer to the error message "
                       "and tool documentation to determine the cause of the error")
        raise e

    # run search cursor on projected polyline to get measures
    # this fc should have M because it was created by the create routes tool
    vertices_measure = []
    projected_cursor = arcpy.da.SearchCursor(temp_in_memory_output, ['SHAPE@M'], None, None, True)
    for row in projected_cursor:
        vertices_measure.append(round(row[0], 2))
    del projected_cursor
    clean_up_temporary_data(temp_in_memory_output)

    #if feature class was created in scratch, delete it
    if temp_in_memory_table_name:
        clean_up_temporary_data(temp_in_memory_output)

    # Create stations for points. If begin_station and end_station are not specified or have null values,
    # use measure values
    stations_list = []
    if begin_station_column and end_station_column:
        #get only the first record of the cursor, in case there are other records in the table
        station_cursor = arcpy.da.SearchCursor(input_polyline, [begin_station_column, end_station_column])
        row = station_cursor.next()
        begin_station_value = row[0]
        end_station_value = row[1]
        del station_cursor

        if begin_station_value is None or end_station_value is None \
                or not eaglepy.is_number(begin_station_value) or not eaglepy.is_number(end_station_value):
            stations_list = vertices_measure
        else:
            for vertex in vertices_measure:
                station_value = create_station_from_measure(begin_station_value, end_station_value, vertices_measure[0],
                                                            vertices_measure[-1], vertex)
                stations_list.append(station_value)
    else:
        stations_list = vertices_measure

    # Create output feature class
    desc = arcpy.Describe(input_polyline)
    if output_spatial_reference_wkid:
        output_spatial_reference = arcpy.SpatialReference( output_spatial_reference_wkid )
    else:
        output_spatial_reference = desc.spatialReference
    try:
        out_feature_class = arcpy.CreateFeatureclass_management(out_path, out_name, "POINT", None,
                                                            "ENABLED", "ENABLED", output_spatial_reference)

        ## create list of field types allowed to be added from the input FC
        allowable_field_types = ['String', 'Integer', 'Date', 'BLOB', 'Double', 'Raster', 'Single', 'SmallInteger']
        ## Add X, Y, Z, Station fields to feature class
        fields_to_be_added = [{'name': 'X_COORD', 'type': 'DOUBLE'},
                              {'name': 'Y_COORD', 'type': 'DOUBLE'},
                              {'name': 'Z_COORD', 'type': 'DOUBLE'},
                              {'name': 'MEASURE', 'type': 'DOUBLE'},
                              {'name': 'STATION', 'type': 'DOUBLE'}]

        for field in fields_to_be_added:
            arcpy.AddField_management(out_feature_class, field['name'], field['type'])

        ## Get all fields from input FC and add them to the output FC
        ## Create list to hold the fields to be copied from input to output fc
        fields_to_be_copied = []
        ignore_fields = ["shape.stlength()", "shape.starea()"]
        if desc.hasGlobalID:
            ignore_fields.append(desc.globalIDFieldName.lower())
        for field in desc.Fields:
            if field.type in allowable_field_types and field.name.lower() not in ignore_fields:
                if not any(d['name'] == field.name for d in fields_to_be_added):
                    arcpy.AddField_management(out_feature_class, field.name, esri_field_types_converter(field.type))
                    fields_to_be_copied.append(field.name)


        # Determine if input feature class has Z or M
        search_fields = ['SHAPE@X', 'SHAPE@Y']
        if desc.hasM:
            search_fields.append('SHAPE@M')

        if desc.hasZ:
            search_fields.append('SHAPE@Z')

        for field_name in fields_to_be_copied:
            search_fields.append(field_name)

        #get polyline from input feature and explode it
        search_cursor = arcpy.da.SearchCursor(input_polyline, search_fields, None, output_spatial_reference, True)

        # set up insert cursor to insert results into output point FC
        insert_fields = ['SHAPE@JSON', 'X_COORD', 'Y_COORD', 'Z_COORD', 'MEASURE', 'STATION']
        for field_name in fields_to_be_copied:
            insert_fields.append(field_name)
        insert_cursor = arcpy.da.InsertCursor(out_feature_class, insert_fields)

        counter = 0
        for row in search_cursor:
            d = dict(zip(search_fields, row))
            #get all the coordinates
            x_coord = d['SHAPE@X']
            y_coord = d['SHAPE@Y']
            try:
                z_coord = d['SHAPE@Z']
            except KeyError:
                z_coord = 0
            try:
                m_coord = d['SHAPE@M']
            except KeyError:
                m_coord = vertices_measure[counter]

            #create json with coordinates
            point_feature = json.dumps({'x': x_coord,
                                        'y': y_coord,
                                        'z': z_coord,
                                        'm': m_coord})
            # insert point into new feature class
            field_values = [point_feature, x_coord, y_coord, z_coord, m_coord, stations_list[counter]]
            for field_name in fields_to_be_copied:
                field_value = d[field_name]
                field_values.append(field_value)
            insert_cursor.insertRow(field_values)
            counter += 1

        # Clean up cursors and temp files
        del search_cursor
        del insert_cursor
        clean_up_temporary_data(temp_projected_output)
    except Exception as e:
        arcpy.AddError("Unable to create output feature class {}. "
                       "Verify that you have the appropriate permissions and rerun the tool"
                       .format(join(out_path, out_name)))
        raise e

    return out_feature_class


def clean_up_temporary_data(temporary_feature_class):
    """
    Checks if the feature class exists and attempts to delete it.
    If it cannot delete it, it gives warning that the feature was not deleted
    :param temporary_feature_class: feature class to be deleted
    :return:
    """
    if arcpy.Exists(temporary_feature_class):
        try:
            arcpy.Delete_management(temporary_feature_class)
        except:
            arcpy.AddWarning("Unable to delete temporary feature class {}. "
                             "Please check to make sure you have appropriate "
                             "permissions and remove it manually.".format(temporary_feature_class))

def project_to_utm(input_feature_class, output_feature_class):
    """
    Function takes a feature class, determines the proper UTM and projects it. If the featureclass is already projected,
    it just returns the input back to the user
    :param input_feature_class: feature class to be projected
    :param output_feature_class: resulting feature class that has been projected to the appropriate UTM
    :return:
    """
    desc = arcpy.Describe(input_feature_class)
    geometry = arcpy.CopyFeatures_management(input_feature_class, arcpy.Geometry())[0]
    if type(geometry).__name__ == '_passthrough':
        ## The geometry is actually None, so we should raise an eerror.
        raise IOError("Null Geometry Found in input_feature_calss, unable to project data.")
    projected_sr = arcpy.SpatialReference(eaglepy.GetUTMForGeometry(geometry))

    if desc.spatialReference != projected_sr:
        ## The Project_management tool does not honor FeatureLayers, so we need to call CopyFeatures first
        tmp_layer_to_project = os.path.join("%scratchGDB%", eaglepy.MakeRandomTableName("tltpnp"))
        arcpy.CopyFeatures_management(input_feature_class, tmp_layer_to_project)
        arcpy.Project_management(tmp_layer_to_project, output_feature_class, projected_sr)
        clean_up_temporary_data(tmp_layer_to_project)
        return output_feature_class
    else:
        return input_feature_class

def create_station_from_measure(begin_station_value, end_station_value,
                            begin_measure_value,  end_measure_value,
                            selected_measure_value):
    """
    Function calculates value based on formula S = (((S2-S1)/(O2-O1))*(O-O1))+S1 where:
    S = station value to be calculated
    S1 and S2 are first and second station values of 2 successive selected rows in the pipe table
    O1 and O2 are first and second odometer reading values or 2 successive selected rows in the ILI table
    O is the odometer reading for the working row
    :param begin_station_value: S1 in the formula
    :param end_station_value: S2 in the formula
    :param begin_measure_value: O1 in the formula
    :param end_measure_value: O2 in formula
    :param selected_measure_value: O in formula
    :return: the calculated value for the selected station
    """
    return round((Decimal(end_station_value) - Decimal(begin_station_value)) / \
                (Decimal(end_measure_value) - Decimal(begin_measure_value)) * \
                (Decimal(selected_measure_value) - Decimal(begin_measure_value)) + Decimal(begin_station_value), 2)
def esri_field_types_converter(non_esri_type):
    return{
        'String': 'TEXT',
        'Integer': 'LONG',
        'Date': 'DATE',
        'BLOB': 'BLOB',
        'Double': 'DOUBLE',
        'GUID': 'GUID',
        'Raster': 'RASTER',
        'Single': 'FLOAT',
        'SmallInteger': 'SHORT'
    }[non_esri_type]


