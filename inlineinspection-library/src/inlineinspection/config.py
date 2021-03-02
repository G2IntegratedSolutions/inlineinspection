"""
A collection of default settings that are used throughout the PIMS system.
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

ILI_PC_PARAMETER_CATGRY = "Input ILI Data Fields"
ILI_PC_REQ_FIELDS = ['LENGTH' ,'MAXDEPTHMEASURED' ,'PIPEDIAMETER' ,'MEASUREDWALLTHICKNESS' ,'PIPESMYS' ,'B31GMAOP']

ILI_PC_PARAMETER_CATGRY_2 = "Output Calculated ILI Fields"
ILI_PC_ADDING_FIELDS = ['PipeBurstPressure' ,'Mod_PipeBurstPressure' ,'CalculatedPressure' ,'ReferencePressure' ,'Safety_Factor' ,'PressureReferencedRatio', 'EstimatedRepairFactor', 'RupturePressureRatio'
                        ]
ILI_PC_HIDDEN_ADDING_FIELDS = ['AreaOfMetalLoss' ,'Mod_AreaOfMetalLoss' ,'FlowStress' ,'Mod_FlowStress' ,'FoliasFactor' ,'Mod_FoliasFactor']
ILI_PIPE_PARAMETER_TYPE = ['Pipe Information From ILI Data', 'Manual Pipe Information', 'Pipe Information from Pipe Segment Feature Class']

ILI_PC_PARAMETER_CATGRY_3 = "Input Required Manual Data Values"
ILI_PS_PARAMETER_CATGRY = "Input Pipe Segment Parameters"
ILI_MAOP_PARAMETER_CATGRY = "Input MAOP Parameters"


ILI_PIPE_REQ_FIELDS = ["SMYSGCL" ]
ILI_MAOP_REQ_FIELDS = ["MAOPRating"]

#ILI_MANUAL_PIPE_INFORMATION_VALUE = [42000,720]

ILI_STATIONSERIED_REQ_FIELDS = ['EventID', 'BeginMeasure', 'EndMeasure']


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

OUTPUT_SYMS_FIELDNAME = "SMYS_SJ" 
OUTPUT_MAOP_FIELDNAME ="MAOP_SJ"


ILI_ANOM_CON_REQ_FIELDS =['AbsoluteOdometer','Width','Length','ClockPosition','PipeDiameter']