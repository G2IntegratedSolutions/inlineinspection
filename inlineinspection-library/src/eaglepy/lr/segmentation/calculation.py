from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import sys
py_version = sys.version_info[0]

import datetime
import eaglepy

class CalculationException(Exception):
    pass
class MissingParameter(CalculationException):
    pass
class ExecuteNotRun(CalculationException):
    pass
class ParameterInvalid(CalculationException):
    pass

#######################################################################################################################
#### Backward Compatability Items
#######################################################################################################################

def ResolveCalculation(calculation):
    return resolve_calculation(calculation)

def ResolveImportForCalculation(calculation):
    return resolve_import_for_calculation(calculation)

#######################################################################################################################
####  End Backward Compatability Items
#######################################################################################################################

def resolve_calculation(calculation):
    """
    Resolves the calculation into the correct format
    If it can be imported, the appropriate string is returned, if not False is returned.
    :param calculation:
    :return:
    """
    if calculation.startswith("calculation"):
        new_calculation = "eaglepy.lr.segmentation.{}".format(calculation)
    else:
        new_calculation = calculation
    try:
        exec ("import {}".format(resolve_import_for_calculation(new_calculation)))
    except ImportError:
        return False
    return new_calculation

def resolve_import_for_calculation(calculation):

    # If no parenthesis or periods, it is in the wrong format, so reject it.
    if calculation.count("(") == 0 or calculation.count(".") == 0:
        return ""
    import_string = calculation.split("(")[0]
    import_parts = import_string.split(".")[:-1]
    return ".".join(import_parts)

class OldCalculationMixin(object):

    def getSourceData(self):
        return self.get_source_data()

    def getNewData(self):
        return self.get_new_data()

    def getDataType(self):
        """Returns the data type of value returned by execute"""
        import eaglepy.DataSource
        if self.answer == self.default:
            return eaglepy.DataSource.convertDataTypeToEsriDataType(self.answer)
        if self.answer is not None:
            return eaglepy.DataSource.convertDataTypeToEsriDataType(self.answer)
        else:
            raise ExecuteNotRun("You must call the execute method before calling getDataType.")


class CalculationBase(object):
    """Base calculation object that handles defaults and data objects."""

    def __init__(self, default=None, data=None, new_data=None, **kwargs):
        super(CalculationBase, self).__init__()
        self.default = default
        self.data = data
        if new_data is not None:
            self.new_data = new_data
        elif 'newData' in kwargs:
            self.new_data = kwargs.pop('newData')
        else:
            raise MissingParameter("The new_data or newData parameter must be specified")
        if self.data is None:
            raise MissingParameter("The data parameter must be specified.")

        self.answer = None
        self.kwargs = kwargs

    def get_source_data(self):
        return self.data

    def get_new_data(self):
        return self.new_data

    def execute(self):
        self.answer = self.default
        return self.answer

    def validate_variable(self, variable):
        if variable.count(".") != 1:
            raise ParameterInvalid("Variable ({}) must contain a row or newRow or new_row parent.")
        parent = variable.split(".")[0]
        if parent not in ('row', 'newRow', 'new_row', ):
            raise ParameterInvalid("Variable must specify: row, newRow or new_row, instead {} found.".format(parent))
        return True

    # TODO: Implement this function within calculations
        # NOTE: this is really for eaglepyx, not eaglepy.
    # def get_data_type(self):
    #     raise NotImplementedError("get_data_type not implemented in new calculations.")


class SimpleFilterMixin(object):
    """Mixin to provide Filter support for a calculation."""

    def get_source_data(self):
        data = super(SimpleFilterMixin, self).get_source_data()
        filter_s = self.kwargs.get("filter_s", list())
        # No filters set, so just return data from parent.
        if len(filter_s) == 0:
            return data
        # Apply filter (from filter property)

        temp_data = data
        for wc in filter_s:
            if len(wc) != 2:
                raise ParameterInvalid("Where clause must contain two elements, column and value: {}".format(str(wc)))
            temp_data = [dictList for dictList in temp_data if dictList[wc[0]] == wc[1]]
        return temp_data


class OrderByMixin(object):
    """Mixin to provide order by support for a calculation."""
    def get_minimum_data(self, data_example=None):
        import eaglepy.DataSource
        if data_example is None:
            return None
        data_type = eaglepy.DataSource.convertDataTypeToEsriDataType(data_example)
        if data_type in ["STRING"]:
            return ""
        elif data_type in ["LONG", "FLOAT", "SHORT", "DOUBLE"]:
            return -float("inf")
        elif data_type in ["DATE"]:
            return datetime.datetime(datetime.MINYEAR, 1, 1)

    def sort_data(self, data, order_by_field):
        reverse = False
        if order_by_field[0] == '-':
            reverse = True
            order_by_field = order_by_field[1:]

        # Find an example value from this column, this gives us a place to start from
        # Null values are replaced by this minimum value.
        if len(data) == 0:
            return data

        if order_by_field not in data[0]:
            raise ParameterInvalid("The order by field ({}) does not exist.".format(order_by_field))

        data_example = None
        for row in data:
            if row[order_by_field]:
                data_example = row[order_by_field]
                break

        # if all the values were null, then we can't sort by this column, just return.
        if data_example is None:
            return data

        data = sorted(data,
                      key=lambda k: k[order_by_field] or self.get_minimum_data(data_example),
                      reverse=reverse)

        return data

    def get_source_data(self):

        source_data = super(OrderByMixin, self).get_source_data()
        order_by = self.kwargs.get('orderby', None)
        if order_by is None:
            return source_data
        if type(order_by) == str:
            order_by = [order_by]
        if type(order_by) != list:
            raise ParameterInvalid("orderby must be a string or list of strings.")

        data = source_data
        #for column in order_by:
        #    data = self.sort_data(data, column)
        data = eaglepy.multi_key_sort(data, order_by)

        return data


class PostOperationMixin(object):
    _answer_post_op = None
    # post_operation - a String that is valid python, with a {} in it to represent the variable
    # The {} is replaced with the internal variable name and then the operation is executed
    # the operation must return a value, that new value becomes the answer that is returned.
    # if the calculation throws an error, it will be silently suppressed, sorry...
    # an example is, if this is a date column: 'getattr({}, "year")' would return the year.

    @property
    def answer(self):
        if not self.kwargs.get('post_operation', None):
            return self._answer_post_op
        else:
            try:
                op = self.kwargs.get('post_operation')
                # Attempt to run the postop string on the value
                new_answer = eval(op.format('self._answer_post_op'))
                return new_answer
            except:
                pass

        return self._answer_post_op

    @answer.setter
    def answer(self, value):
        self._answer_post_op = value


class CalculationSingleInput(CalculationBase):
    """Base calculation object that handles a single input."""
    def __init__(self, **kwargs):
        self.input = kwargs.pop('input', None)
        super(CalculationSingleInput, self).__init__(**kwargs)
        if self.input is None:
            raise ParameterInvalid("input must be specified.")

        # Validate that self.input can be parsed by the variable parser.
        self.validate_variable(self.input)


class SetDefault(OldCalculationMixin, CalculationBase):
    """Returns the default value.  This calculation should be used to specify the value of a field."""
    pass


class Count(OldCalculationMixin, SimpleFilterMixin, CalculationSingleInput):
    """Counts the number of rows in row or new row"""

    def execute(self):

        source_data = self.get_source_data()
        new_data = self.get_new_data()
        parent, column = self.input.split(".")

        if parent.lower() in ('row', ):
            if len(source_data) <= 0:
                self.answer = 0
                return self.answer
            if column not in source_data[0]:
                raise ParameterInvalid("The column {} was not found in the source table.".format(column))
            self.answer = len(source_data)
        else:
            if len(new_data) <= 0:
                self.answer = 0
                return self.answer
            if column not in new_data[0]:
                raise ParameterInvalid("The column {} was not found in the new data, "
                                       "check the order of your calculations.".format(column))
            self.answer = len(new_data)
        return self.answer


class First(OldCalculationMixin, PostOperationMixin, SimpleFilterMixin, OrderByMixin, CalculationSingleInput):
    """
    Selects the First item that is not Null after the orderby is applied.
    If all rows are Null, the default is returned.
    """

    def execute(self):

        source_data = self.get_source_data()
        new_data = self.get_new_data()
        parent, column = self.input.split(".")

        if parent.lower() in ('row', ):
            if len(source_data) <= 0:
                return 0
            if column not in source_data[0]:
                raise ParameterInvalid("The column {} was not found in the source table.".format(column))
            process_data = source_data
        else:
            if len(new_data) <= 0:
                return 0
            if column not in new_data[0]:
                raise ParameterInvalid("The column {} was not found in the new data, "
                                       "check the order of your calculations.".format(column))
            process_data = new_data

        for row in process_data:
            if py_version<=2:
                if row[column] is not None and unicode(row[column]) != "":
                    self.answer = row[column]
                    return self.answer
            else:
                if row[column] is not None and str(row[column]) != "":
                    self.answer = row[column]
                    return self.answer


        # If we get here, these was no not-null value, so return the default, by calling the parent execute
        return super(First, self).execute()

class Concat(OldCalculationMixin, SimpleFilterMixin, OrderByMixin, CalculationSingleInput):
    def execute(self):

        source_data = self.get_source_data()
        new_data = self.get_new_data()
        parent, column = self.input.split(".")
        allow_null = self.kwargs.get("allow_null", False)
        row_default = self.kwargs.get("row_default", None)
        join_character = self.kwargs.get("join_character", ",")
        distinct = self.kwargs.get("distinct", False)

        if parent.lower() in ('row', ):
            if len(source_data) <= 0:
                return 0
            if column not in source_data[0]:
                raise ParameterInvalid("The column {} was not found in the source table.".format(column))
            process_data = source_data
        else:
            if len(new_data) <= 0:
                return 0
            if column not in new_data[0]:
                raise ParameterInvalid("The column {} was not found in the new data, "
                                       "check the order of your calculations.".format(column))
            process_data = new_data

        # Convert to a list of values
        data_list = [r[column] for r in process_data]

        # Fix Null values
        if not allow_null:
            # if allow_null if False we need to remove all of the nulls from data_list
            data_list = [r for r in data_list if r is not None]
        elif row_default is not None:
            # if allow_null is True, and row_default is set to a value, then replace all Nulls with defaults
            temp = list()
            for r in data_list:
                if r is None:
                    temp.append(row_default)
                else:
                    temp.append(r)
            data_list = temp

        # If distinct, convert to a set to remove any duplicate values
        if distinct:
            data_list = list(set(data_list))

        # If there is no data, return the default value.
        if len(data_list) == 0:
            self.answer = self.default
        else:
            self.answer = str(join_character).join([str(i) for i in data_list])
        return self.answer


class NumpyCalculation(OldCalculationMixin, CalculationSingleInput):
    numpy_calculation = None
    allow_null = False
    row_default = None

    def __init__(self, allow_null=False, row_default=None, **kwargs):
        super(NumpyCalculation, self).__init__(**kwargs)
        self.allow_null = allow_null
        self.row_default = row_default

    def execute(self):
        if self.numpy_calculation is None:
            raise CalculationException("No numpy calculation specified.")

        # Import the numpy calculation
        import numpy
        if not hasattr(numpy, self.numpy_calculation):
            raise CalculationException("{} is not a valid numpy calculation".format(self.numpy_calculation))

        # Gather data
        source_data = self.get_source_data()
        new_data = self.get_new_data()
        parent, column = self.input.split('.')

        # Verify the row specification is valid.
        if parent in ('row', ):
            if len(source_data) == 0:
                return super(NumpyCalculation, self).execute()
            if column not in source_data[0]:
                raise ParameterInvalid("The column {} is not in the source table.".format(column))
            process_data = source_data
        else:
            if len(new_data) == 0:
                return super(NumpyCalculation, self).execute()
            if column not in new_data[0]:
                raise ParameterInvalid("The column {} is not in the output table.".format(column))
            process_data = new_data

        # Convert to a list of values
        data_list = [r[column] for r in process_data]

        if not self.allow_null:
            # if allow_null if False we need to remove all of the nulls from data_list
            data_list = [r for r in data_list if r is not None]
        elif self.row_default is not None:
            # if allow_null is True, and row_default is set to a value, then replace all Nulls with defaults
            temp = list()
            for r in data_list:
                if r is None:
                    temp.append(self.row_default)
                else:
                    temp.append(r)
            data_list = temp

        self.answer = self.default

        try:
            self.answer = getattr(numpy, self.numpy_calculation)(data_list)
            if self.answer is not None and type(self.answer).__module__ == numpy.__name__:
                self.answer = numpy.asscalar(self.answer)
        except Exception as e:
            raise CalculationException("Unable to complete calculation: {}".format(e))

        if self.answer is None and self.allow_null:
            self.answer = self.default

        return self.answer

class Sum(SimpleFilterMixin, NumpyCalculation):
    """Sums the values contained within the specified field for all records"""

    def execute(self):
        # Gather data
        source_data = self.get_source_data()
        new_data = self.get_new_data()
        parent, column = self.input.split('.')

        # Verify the row specification is valid.
        if parent in ('row', ):
            if len(source_data) == 0:
                return super(NumpyCalculation, self).execute()
            if column not in source_data[0]:
                raise ParameterInvalid("The column {} is not in the source table.".format(column))
            process_data = source_data
        else:
            if len(new_data) == 0:
                return super(NumpyCalculation, self).execute()
            if column not in new_data[0]:
                raise ParameterInvalid("The column {} is not in the output table.".format(column))
            process_data = new_data

        # Convert to a list of values
        data_list = [r[column] for r in process_data]

        if not self.allow_null:
            # if allow_null if False we need to remove all of the nulls from data_list
            data_list = [r for r in data_list if r is not None]
        elif self.row_default is not None:
            # if allow_null is True, and row_default is set to a value, then replace all Nulls with defaults
            temp = list()
            for r in data_list:
                if r is None:
                    temp.append(self.row_default)
                else:
                    temp.append(r)
            data_list = temp

        if len(data_list) == 0:
            self.answer = self.default
            return self.answer

        self.answer = 0
        for row in data_list:
            try:
                self.answer += row
            except TypeError as e:
                raise CalculationException("Unable to add numbers: {}".format(str(e)))

        return self.answer

class Min(SimpleFilterMixin, NumpyCalculation):
    """Provides  the minimum value from the numpy.amin function"""
    numpy_calculation = "amin"

class Max(SimpleFilterMixin, NumpyCalculation):
    """Provides the maximum value from the numpy.amax function"""
    numpy_calculation = "amax"

class Average(SimpleFilterMixin, NumpyCalculation):
    """Sums the values contained within the specified field for all records"""
    numpy_calculation = "average"

class Median(SimpleFilterMixin, NumpyCalculation):
    """Sums the values contained within the specified field for all records"""
    numpy_calculation = "median"

class Mean(SimpleFilterMixin, NumpyCalculation):
    """Sums the values contained within the specified field for all records"""
    numpy_calculation = "mean"

class Std(SimpleFilterMixin, NumpyCalculation):
    """Sums the values contained within the specified field for all records"""
    numpy_calculation = "std"

class Var(SimpleFilterMixin, NumpyCalculation):
    """Sums the values contained within the specified field for all records"""
    numpy_calculation = "var"
