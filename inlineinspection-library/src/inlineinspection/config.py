"""
A collection of default settings that are used throughout the liquids hca system.
These can be overridden by using a
config file.
"""
#   ------ Hydro trace related config values

ILI_PC_TOOL_CATAGORY =  'ILI Tools'
ILI_PC_TOOL_LABEL ='Pressure Calculator'
ILI_PC_TOOL_DESC = 'Performs Pressure Calculations for ILI'
ILI_SUPPORT_DB_TYPES=[".gdb\\", ".sde\\"]
ILI_TEMP_FOLDER = "ILI_TEMP"
ILI_TEMP_GDB = 'TempOutput_ILI.gdb'

ILI_PC_PARAMETER_CATGRY = "Required Input Data Columns"
ILI_PC_REQ_FIELDS = ['LENGTH' ,'MAXDEPTHMEASURED' ,'MAXDIAMETER' ,'MEASUREDWALLTHICKNESS' ,'PIPESMYS' ,'B31GMAOP']

ILI_PC_PARAMETER_CATGRY_2 = "Output Data Columns"
ILI_PC_ADDING_FIELDS = ['AreaOfMetalLoss' ,'Mod_AreaOfMetalLoss' ,'FlowStress' ,'Mod_FlowStress' ,'FoliasFactor' ,'Mod_FoliasFactor'
                        ,'PipeBurstPressure' ,'Mod_PipeBurstPressure' ,'CalculatedPressure' ,'ReferencePressure' ,'Safety_Factor' ,'PressureReferencedRatio', 'EstimatedRepairFactor', 'RupturePressureRatio'
                        ]
ILI_PIPE_PARAMETER_TYPE = ['Pipe information from ILI Data', 'Manual Pipe Information', 'Pipe Information from Pipe line feature class']


# Event (pipe fill status) table fields
EVENT_TABLE_FIELD_DESCRIPTION = [["POINT_ID", "Text", "Point ID", 27],
                                ["ROUTE_ID", "LONG", "Route ID", None],
                                ["POINT_MEASURE", "DOUBLE", "Point Measure", None],
                                ["POINT_ELEVATION", "DOUBLE", "Point Elevation", None],
                                ["FROM_MEASURE", "DOUBLE", "Begin Measure", None],
                                ["FROM_ELEVATION", "DOUBLE", "Begin Elevation", None ],
                                ["TO_MEASURE", "DOUBLE", "End Measure", None],
                                ["TO_ELEVATION", "DOUBLE", "End Elevation", None ],
                                ["FILL_STAT", "Text", "Fill Status", 20],
                                ["DRAIN_VOL", "DOUBLE", "Drain Volume", None]
                                ]
