"""
A collection of default settings that are used throughout the liquids hca system.
These can be overridden by using a
config file.
"""

# Alen was here!
#   ------ Hydro trace related config values

ILI_PC_TOOL_CATAGORY =  'ILI Tools'
ILI_PC_TOOL_LABEL ='Pressure Calculator'
ILI_PC_TOOL_DESC = 'Performs Pressure Calculations for ILI'
ILI_SUPPORT_DB_TYPES=[".gdb\\", ".sde\\"]
ILI_TEMP_FOLDER = "ILI_TEMP"
ILI_TEMP_GDB = 'TempOutput_ILI.gdb'

ILI_PC_PARAMETER_CATGRY = "Pressure Calculator Parameters"
ILI_PC_REQ_FIELDS = ['LENGTH' ,'MAXDEPTHMEASURED' ,'MAXDIAMETER' ,'MEASUREDWALLTHICKNESS' ,'PIPESMYS' ,'PIPEMAOP']

ILI_PC_ADDING_FIELDS = ['AreaOfMetalLoss' ,'Mod_AreaOfMetalLoss' ,'FlowStress' ,'Mod_FlowStress' ,'FoliasFactor' ,'Mod_FoliasFactor'
                        ,'PipeBurstPressure' ,'Mod_PipeBurstPressure' ,'CalculatedPressure' ,'ReferencePressure' ,'Safety_Factor' ,'PressureReferencedRatio','RupturePressureRatio'
                        ]


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