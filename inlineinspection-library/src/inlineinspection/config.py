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

ILI_PC_PARAMETER_CATGRY = "Pressure Calculator Parameters"
ILI_PC_REQ_FIELDS = ['LENGTH' ,'MAXDEPTHMEASURED' ,'MAXDIAMETER' ,'MEASUREDWALLTHICKNESS' ,'PIPESMYS' ,'PIPEMAOP']

ILI_PC_ADDING_FIELDS = ['AreaOfMetalLoss' ,'Mod_AreaOfMetalLoss' ,'FlowStress' ,'Mod_FlowStress' ,'FoliasFactor' ,'Mod_FoliasFactor'
                        ,'PipeBurstPressure' ,'Mod_PipeBurstPressure' ,'CalculatedPressure' ,'ReferencePressure' ,'Safety_Factor' ,'PressureReferencedRatio','RupturePressureRatio'
                        ]




#Summarize elevation fields
SUMMARIZE_ELEVATION_FIELD = "MEANELEVATION"

#OSPointM fields
ROUTE_ID_FIELD = "ROUTE_ID"
POINT_ID_FIELD = "POINT_ID"
LINE_ID_FIELD = "LINE_ID"
MEASURE_FIELD = "MEASURE"
ELEVATION_FIELD = "ELEVATION"
DDELEV_FIELD = "DD_ELEV"
NOM_DIA_FIELD = "NOM_DIAM"
INT_DIAM_FIELD = "INT_DIAM"
NOM_W_T_FIELD = "NOM_W_T"
LOC_MINMAX_FIELD = "LOC_MINMAX"
DRAIN_CALC_FIELD = "DRAIN_CALC"
DRAIN_VOLUME_FIELD = "DRAIN_VOL"
DRAIN_RATE_FIELD = "DRAIN_RATE"
OFRES_TIME_FIELD = "OFRES_TIME"
HTRES_TIME_FIELD = "HTRES_TIME"
ROUTE_DESC_FIELD = "ROUTE_DESC"
H_LOOP_ID_FIELD = "H_LOOP_ID"
L_LOOP_ID_FIELD = "L_LOOP_ID"
DRN_VOL_UP_FIELD = "DRN_VOL_UP"
DRN_VOL_DN_FIELD = "DRN_VOL_DN"
N_DRNVOLUP_FIELD = "N_DRNVOLUP"
N_DRNVOLDN_FIELD = "N_DRNVOLDN"
UP_MAX_ELV_FIELD = "UP_MAX_ELV"
DN_MAX_ELV_FIELD = "DN_MAX_ELV"
UPMAXELV_M_FIELD = "UPMAXELV_M"
DNMAXELV_M_FIELD = "DNMAXELV_M"
Z_LENGTH_FIELD = "Z_LENGTH"


# VALVE_REQUIED_FIELDS = [ "FROM_MEAS", "ROUTE_ID", "ELEVATION"]

GLOBAL_INPUTS_REQUIRED_FIELDS = ["ROUTE_ID", "SPL_PT_INT", "PIPE_ROUGH", "FLOW_RATE", "P_OP_TEMP",
                                 "P_SD_TIME", "OFRES_TIME", "HTRES_TIME", "N_INT_DIAM", "FLOWEQSTN",
                                "M_PROD_TYP", "PROD_DNSTY", "API_GRAV",  "KIN_VISC",
                                "KVISC_TEMP",  "EQ_TYPE", "EQ_FORM", "FINGAS_1", "FINGAS_2",
                                 "T_DIST", "PCT_VDIST", "P_VAPOR", "C5_VOL_PCT", "T_AMB", "WIND_VEL",
                                "SLICK_THK", "SLKTHKSMWB", "MAXWBAREA", "WB_ADHSN", "DEPTH_H2O",
                                "BANK_ANGLE", "ADHSN_RT", "INFIL_RT", "Z_TOL", "XY_TOL",
                                "CL_DW_BUF", "CL_EC_BUF", "CL_HPA_BUF", "CL_NW_BUF", "CL_OPA_BUF",
                                "OF_DW_BUF", "OF_EC_BUF", "OF_HPA_BUF", "OF_NW_BUF", "OF_OPA_BUF",
                                "HT_DW_BUF", "HT_EC_BUF", "HT_HPA_BUF", "HT_NW_BUF", "HT_OPA_BUF"]


# Global Inputs table field names
G_ROUTE_ID_FIELD = "ROUTE_ID"
ORIGINAL_ROUTE_ID_FIELD = "ORIGINAL_ROUTE_ID"
FROM_MEASURE_FIELD = "FROM_MEAS"
TO_MEASURE_FIELD = "TO_MEAS"
SPL_PT_INT_FIELD = "SPL_PT_INT"

FLOWRATE_FIELD = "FLOW_RATE"
KIN_VISC_FIELD = "KIN_VISC"
PRODDNSTY_FIELD = "PROD_DNSTY"
PSDTIME_FIELD = "P_SD_TIME"
KVISC_TEMP_FIELD = "KVISC_TEMP"
T_AMB_FIELD = "T_AMB"
G_N_INT_DIAM = "N_INT_DIAM"
G_XY_TOLERANCE_FIELD = "XY_TOL"
ZTOL_FILED = "Z_TOL"
MAX_PT_FIELD = "MAX_PT"
AVG_PT_FIELD = "AVG_PT"
FLOWEQSTN_FIELD = "FLOWEQSTN"
VAPORPRES_FIELD = "P_VAPOR"
C5_VOL_PCT_FIELD = "C5_VOL_PCT"
P_OP_TEMP_FIELD = "P_OP_TEMP"
PIPE_ROUGH_FIELD = "PIPE_ROUGH"
FINGAS_1_FIELD = "FINGAS_1"
FINGAS_2_FIELD = "FINGAS_2"
EQ_FORM_FORM_FIELD = "EQ_FORM"
WALL_THICKNESS_FIELD = "NOM_W_T"
EQ_TYPE_FIELD = "EQ_TYPE"
T_DIST_FIELD = "T_DIST"
API_GRAV_FIELD = "API_GRAV"
ADHSN_RT_FIELD = "ADHSN_RT"
INFIL_RT_FIELD = "INFIL_RT"
PRODUCT_TYPE_FIELD = "M_PROD_TYP"

# EDGE table fields
EDGE_FIELD_DESCRIPTION = [["EDGEID", "LONG", "Edge ID", None],
                          ["ROUTE_ID", "LONG", "Route ID", None],
                          ["FROM_JCTID", "LONG", "From Junction ID", None],
                          ["TO_JCTID", "LONG", "To Junction ID", None],
                          ["FROM_MEAS", "DOUBLE", "Begin Measure", None],
                          ["TO_MEAS", "DOUBLE", "End Measure", None],
                          ["FROM_ELEV", "DOUBLE", "Begin Elevation", None],
                          ["TO_ELEV", "DOUBLE", "End Elevation", None]
                          ]

# JUNCTIONS table fields
JUNCTIONS_FIELD_DESCRIPTION = [["JCTID", "LONG", "Junction ID", None],
                                ["JCT_TYPE", "TEXT", "Junction Type", None],
                                ["ROUTE_ID", "LONG", "Route ID", None],
                                ["MEASURE", "DOUBLE", "Measure", None],
                                ["ELEVATION", "DOUBLE", "Elevation", None],
                                ["LONG", "DOUBLE", "Longitude", None],
                                ["LAT", "DOUBLE", "Latitude", None],
                                ["ISCONNECTED", "SHORT", "Is Connected", None],
                                ["LOOP_EDGEIDS", "Text", "Loop Edge IDs", 250]
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


# OSPointM field names
OSPOINTM_FIELD_DESCRIPTION = [
                                ["ORIGINAL_ROUTE_ID", "Text", "Original Route ID", 50],
                                [ "ROUTE_ID", "Long", "Route ID", None ],
                                [ "POINT_ID", "Text", "Point ID", 27],
                                [ "MEASURE", "Double", "Measure", None ],
                                [ "INT_DIAM", "Double", "Interior Diameter", None ],
                                [ "NOM_DIAM", "Double", "Outside Diameter", None ],
                                # [ "MAOPRATING", "Double", "MAOP Rating", None ],
                                [ "ELEVATION", "Double", "Elevation", None ],
                                # [ "TERR_SLOPE", "Double", "Terrain Slope", None ],
                                # [ "TERR_AZIM", "Double", "Terrain Azimuth", None ],
                                [ "LOC_MINMAX", "Text", "Local MinMax", 16],
                                # [ "PIPE_SLOPE", "Double", "Pipe Slope", None ],
                                # [ "PIPE_AZIM", "Double", "Pipe Azimuth", None ],
                                # [ "SPILL_DIR", "Text", "Spill Direction", 10],
                                # [ "SPILL_AZIM", "Double", "Spill Azimuth", None ],
                                [ "OSANALYSIS", "Text", "OS Analysis", 20],
                                [ "DRAIN_CALC", "Text", "Draindown Calc", 16],
                                [ "DD_ELEV", "Double", "Draindown Elevation", None ],
                                [ "Z_LENGTH", "Double", "Z Length", None ],
                                # [ "DD_MINMAX", "Text", "Draindown MinMax", 16],
                                [ "DRAIN_VOL", "Double", "Drain Volume", None ],
                                [ "DRAIN_RATE", "Double", "Drain Rate", None ],
                                [ "UP_MAX_ELV", "Double", "UP Max Elevation", None ],
                                [ "DN_MAX_ELV", "Double", "DN Max Elevation", None ],
                                [ "UPMAXELV_M", "Double", "UP Max Elevation Measure", None ],
                                [ "DNMAXELV_M", "Double", "DN Max Elevation Measure", None ],
                                [ "H_LOOP_ID", "Text", "High Loop ID", 150],
                                [ "L_LOOP_ID", "Text", "Lown Loop ID", 150],
                                [ "OFRES_TIME", "Double", "OF Response Time", None ],
                                [ "HTRES_TIME", "Double", "HT Response Time", None ],
                                [ "DRN_VOL_UP", "Double", "UP Draindown Volume", None ],
                                [ "N_DRNVOLUP", "Double", "UP Network Draindown Volume", None ],
                                [ "DRN_VOL_DN", "Double", "DN Draindown Volume", None ],
                                [ "N_DRNVOLDN", "Double", "DN Network Draindown Volume", None ],
                                [ "INT_METHOD", "Text", "Intersection Method", 24],
                                [ "CL_DIR_INT", "Double", "Centerline Direct Intersection", None ],
                                [ "CL_IND_INT", "Double", "Centerline Indirect Intersection", None ],
                                [ "CL_NW_DIR", "Double", "Centerline NW Direct", None ],
                                [ "CL_NW_IND", "Double", "Centerline NW Indirect", None ],
                                [ "CL_HPA_DIR", "Double", "Centerline HPA Direct", None ],
                                [ "CL_HPA_IND", "Double", "Centerline HPA Indirect", None ],
                                [ "CL_OPA_DIR", "Double", "Centerline OPA Direct", None ],
                                [ "CL_OPA_IND", "Double", "Centerline OPA Indirect", None ],
                                [ "CL_EC_DIR", "Double", "Centerline EC Direct", None ],
                                [ "CL_EC_IND", "Double", "Centerline EC Indirect", None ],
                                [ "CL_DW_DIR", "Double", "Centerline DW Direct", None ],
                                [ "CL_DW_IND", "Double", "Centerline DW Indirect", None ],
                                [ "OF_DIR_INT", "Double", "OF Direct Intersection", None ],
                                [ "OF_IND_INT", "Double", "OF Indirect Intersection", None ],
                                [ "OF_NW_DIR", "Double", "OF NW Direct", None ],
                                [ "OF_NW_IND", "Double", "OF NW Indirect", None ],
                                [ "OF_HPA_DIR", "Double", "OF HPA Direct", None ],
                                [ "OF_HPA_IND", "Double", "OF HPA Indirect", None ],
                                [ "OF_OPA_DIR", "Double", "OF OPA Direct", None ],
                                [ "OF_OPA_IND", "Double", "OF OPA Indirect", None ],
                                [ "OF_EC_DIR", "Double", "OF EC Direct", None ],
                                [ "OF_EC_IND", "Double", "OF EC Indirect", None ],
                                [ "OF_DW_DIR", "Double", "OF DW Direct", None ],
                                [ "OF_DW_IND", "Double", "OF DW Indirect", None ],
                                # [ "LS_DIR_INT", "Double", "LS Direct Intersection", None ],
                                # [ "LS_IND_INT", "Double", "LS Indirect Intersection", None ],
                                # [ "LS_NW_DIR", "Double", "LS NW Direct", None ],
                                # [ "LS_NW_IND", "Double", "LS NW Indirect", None ],
                                # [ "LS_HPA_DIR", "Double", "LS HPA Direct", None ],
                                # [ "LS_HPA_IND", "Double", "LS HPA Indirect", None ],
                                # [ "LS_OPA_DIR", "Double", "LS OPA Direct", None ],
                                # [ "LS_OPA_IND", "Double", "LS OPA Indirect", None ],
                                # [ "LS_EC_DIR", "Double", "LS EC Direct", None ],
                                # [ "LS_EC_IND", "Double", "LS EC Indirect", None ],
                                # [ "LS_DW_DIR", "Double", "LS DW Direct", None ],
                                # [ "LS_DW_IND", "Double", "LS DW Indirect", None ],
                                [ "HT_DIR_INT", "Double", "HT Direct Intersection", None ],
                                [ "HT_IND_INT", "Double", "HT Indirect Intersection", None ],
                                [ "HT_NW_DIR", "Double", "HT NW Direct", None ],
                                [ "HT_NW_IND", "Double", "HT NW Indirect", None ],
                                [ "HT_HPA_DIR", "Double", "HT HPA Direct", None ],
                                [ "HT_HPA_IND", "Double", "HT HPA Indirect", None ],
                                [ "HT_OPA_DIR", "Double", "HT OPA Direct", None ],
                                [ "HT_OPA_IND", "Double", "HT OPA Indirect", None ],
                                [ "HT_EC_DIR", "Double", "HT EC Direct", None ],
                                [ "HT_EC_IND", "Double", "HT EC Indirect", None ],
                                [ "HT_DW_DIR", "Double", "HT DW Direct", None ],
                                [ "HT_DW_IND", "Double", "HT DW Indirect", None ],
                                [ "WB_DIR_INT", "Double", "WB Direct Intersection", None ],
                                [ "WB_IND_INT", "Double", "WB Indirect Intersection", None ],
                                [ "WB_NW_DIR", "Double", "WB NW Direct", None ],
                                [ "WB_NW_IND", "Double", "WB NW Indirect", None ],
                                [ "WB_HPA_DIR", "Double", "WB HPA Direct", None ],
                                [ "WB_HPA_IND", "Double", "WB HPA Indirect", None ],
                                [ "WB_OPA_DIR", "Double", "WB OPA Direct", None ],
                                [ "WB_OPA_IND", "Double", "WB OPA Indirect", None ],
                                [ "WB_EC_DIR", "Double", "WB EC Direct", None ],
                                [ "WB_EC_IND", "Double", "WB EC Indirect", None ],
                                [ "WB_DW_DIR", "Double", "WB DW Direct", None ],
                                [ "WB_DW_IND", "Double", "WB DW Indirect", None ],
                                # [ "PI_DIR_INT", "Double", "PI Direct Intersection", None ],
                                # [ "PI_IND_INT", "Double", "PI Indirect Intersection", None ],
                                # [ "PI_SIS_DIR", "Double", "PI SIS Direct", None ],
                                # [ "PI_SIS_IND", "Double", "PI SIS Indirect", None ],
                                # [ "PI_BHO_DIR", "Double", "PI BHO Direct", None ],
                                # [ "PI_BHO_IND", "Double", "PI BHO Indirect", None ],
                                # [ "PI_IS_DIR", "Double", "PI IS Direct", None ],
                                # [ "PI_IS_IND", "Double", "PI IS Indirect", None ],
                                [ "HCA_CA_PNT", "Double", "HCA CA Point", None ],
                                # [ "GRID_GROUP", "Text", "Grid Group", 16],
                                [ "NW_INDEX", "Double", "NW Index", None ],
                                [ "HPA_INDEX", "Double", "HPA Index", None ],
                                [ "OPA_INDEX", "Double", "OPA Index", None ],
                                [ "DW_INDEX", "Double", "DW Index", None ],
                                [ "EC_INDEX", "Double", "EC Index", None ],
                                [ "HCA_INDEX", "Double", "HCA Index", None ],
                                [ "RISK_INDEX", "Double", "RISK Index", None ],
                                [ "EFRD_INDEX", "Double", "EFRD Index", None ],
                                [ "EFRD_CLASS", "Double", "EFRD Class", None ],
                                [ "ODRAIN_VOL", "Double", "ODRAIN Volume", None ],
                                [ "OEFRDINDEX", "Double", "OEFRD Index", None ],
                                [ "OEFRDCLASS", "Double", "OEFRD Class", None ],
                                [ "PDRAIN_VOL", "Double", "PDRAIN Volume", None ],
                                [ "PEFRDINDEX", "Double", "PEFRD Index", None ],
                                [ "PEFRDCLASS", "Double", "PEFRD Class", None ],
                                [ "SAEFRDINDX", "Double", "SAEFRD Index", None ]
                                ]


GLOBAL_INPUTS_TABLE_FIELD_DESCRIPTION = [
                                ["ORIGINAL_ROUTE_ID", "Text", "Original Route ID", 50],
                                ["ROUTE_ID", "Long", "Route ID", None],
                                ["FROM_MEAS", "Double", "Begin Measure", None],
                                ["TO_MEAS", "Double", "End Measure", None],
                                ["SPL_PT_INT", "Long", "Release Point Interval", None],
                                # ["POS_ACC", "Long", "Positional Accuracy", None],
                                ["FLOWEQSTN", "Short", "Flow Direction", None],
                                ["FLOW_RATE", "Long", "Flow Rate", None],
                                ["P_VAPOR", "Double", "Vapor Pressure", None],
                                ["Z_TOL", "Double", "Z Tolerance", None],
                                ["XY_TOL", "Double", "X Y Tolerance", None],
                                ["P_OP_TEMP", "Double", "Operating Temperature", None],
                                ["P_SD_TIME", "Long", "Shutdown Time", None],
                                ["OFRES_TIME", "Long", "OF Response Time", None],
                                ["HTRES_TIME", "Long", "HT Response Time", None],
                                ["M_PROD_TYP", "Text", "Product Type", 100],
                                ["PROD_DNSTY", "Double", "Density", None],
                                ["API_GRAV", "Double", "API Gravity", None],
                                ["KIN_VISC", "Double", "Kinematic Viscocity", None],
                                ["KVISC_TEMP", "Double", "Kinematic Viscocity Temperature", None],
                                ["C5_VOL_PCT", "Double", "C5 Volume Percent", None],
                                ["EQ_TYPE", "Text", "Equation Type", 16],
                                ["EQ_FORM", "Text", "Equation Form", 16],
                                ["FINGAS_1", "Double", "Fingas Coefficient 1", None],
                                ["FINGAS_2", "Double", "Fingas Coefficient 2", None],
                                ["T_AMB", "Double", "Ambient Temperature", None],
                                ["T_DIST", "Double", "Distillation Temperature", None],
                                ["PCT_VDIST", "Double", "Percent Volume Distilled", None],
                                ["N_INT_DIAM", "Double", "Nominal Interior Diameter", None],
                                ["PIPE_ROUGH", "Double", "Pipe Roughness", None],
                                ["ADHSN_RT", "Double", "Adhesion Rate", None],
                                ["INFIL_RT", "Double", "Infiltration Rate", None],
                                # ["STREAM_VEL", "Double", "Stream Velocity", None],
                                ["WIND_VEL", "Double", "Wind Velocity", None],
                                ["DEPTH_H2O", "Double", "Depth H2O", None],
                                ["BANK_ANGLE", "Double", "Bank Angle", None],
                                ["WB_ADHSN", "Double", "WB Shoreline Adhesion", None],
                                ["SLICK_THK", "Double", "Slick Thickness Large WB", None],
                                ["SLKTHKSMWB", "Double", "Slick Thickness Small WB", None],
                                ["MAXWBAREA", "Double", "Max WB Area", None],
                                ["CL_NW_BUF", "Long", "Centerline NW Buffer", None],
                                ["CL_HPA_BUF", "Long", "Centerline HPA Buffer", None],
                                ["CL_OPA_BUF", "Long", "Centerline OPA Buffer", None],
                                ["CL_EC_BUF", "Long", "Centerline EC Buffer", None],
                                ["CL_DW_BUF", "Long", "Centerline DW Buffer", None],
                                ["OF_NW_BUF", "Long", "OF NW Buffer", None],
                                ["OF_HPA_BUF", "Long", "OF_HPA_Buffer", None],
                                ["OF_OPA_BUF", "Long", "OF OPA Buffer", None],
                                ["OF_EC_BUF", "Long", "OF EC Buffer", None],
                                ["OF_DW_BUF", "Long", "OF DW Buffer", None],
                                ["HT_NW_BUF", "Long", "HT NW Buffer", None],
                                ["HT_HPA_BUF", "Long", "HT HPA Buffer", None],
                                ["HT_OPA_BUF", "Long", "HT OPA Buffer", None],
                                ["HT_EC_BUF", "Long", "HT EC Buffer", None],
                                ["HT_DW_BUF", "Long", "HT DW Buffer", None]
                                ]

PRODUCT_PROPERTIES_LOOKUP_TABLE_FIELD_DESCRIPTION = [["PRODUCT_ID", "Long", "Product ID", None],
                                                    ["M_PROD_TYP", "Text", "Product Type", 100],
                                                    ["EQ_TYPE", "Text", "Equation Type", 16],
                                                    ["EQ_FORM", "Text", "Equation Form", 16],
                                                    ["FINGAS_1", "Double", "Fingas Coefficient 1", None],
                                                    ["FINGAS_2", "Double", "Fingas Coefficient 2", None],
                                                    ["PROD_DNSTY", "Double", "Density", None],
                                                    ["API_GRAV", "Double", "API Gravity", None],
                                                    ["KIN_VISC", "Double", "Kinematic Viscocity", None],
                                                    ["KVISC_TEMP", "Double", "Kinematic Viscocity Temperature", None],
                                                    ["PCT_VDIST", "Double", "Percent Volume Distilled", None],
                                                    ["T_DIST", "Double", "Distillation Temperature", None],
                                                    ["SOURCE", "Text", "Source", 10]

                                                    ]

PRODUCT_PROPERTIES_LOOKUP_TABLE_FIELDS = ["PRODUCT_ID", "M_PROD_TYP", "EQ_TYPE", "EQ_FORM", "FINGAS_1", "FINGAS_2",
                                          "PROD_DNSTY", "API_GRAV", "KIN_VISC", "KVISC_TEMP", "PCT_VDIST", "T_DIST", "SOURCE"]

PRODUCT_PROPERTIES_LOOKUP_TABLE_RECORDS = [
                        [1, 'Alaminos Canyon Block 25', 'Fingas', 'Logarithmic', 2.01, 0.045, 0.8663, 30.89, 30, 15, 17, 180, 'Fingas'],
                        [2, 'Alaska North Slope (2002)', 'Fingas', 'Logarithmic', 2.86, 0.045, 0.8754, 29.3, 13.14, 15, 23, 180, 'Fingas'],
                        [3, 'Alaska North Slope (2011)', 'Fingas', 'Logarithmic', 2.47, 0.045, 0.887, 29.3, 17.36, 15, 26, 180, 'Fingas'],
                        [4, 'Alaska North Slope (2015)', 'Fingas', 'Logarithmic', 2.71, -0.045, 0.8639, 31.3, 9.85, 15, 25, 180, 'Fingas'],
                        [5, 'Alberta Sweet Mixed Blend(#5)', 'Fingas', 'Logarithmic', 3.35, 0.045, 0.8404, 35.7, 7.14, 15, 26, 180, 'Fingas'],
                        [6, 'Access West Winter Blend (Alberta)', 'Fingas', 'Logarithmic', 1.72, 0.045, 0.9399, 20.9, 372.38, 15, 33, 180, 'Fingas'],
                        [7, 'Amauligak - f24', 'Fingas', 'Logarithmic', 1.91, 0.045, 0.8896, 27.4, 15.74, 15, 13, 180, 'Fingas'],
                        [8, 'Anadarko H1A-376', 'Fingas', 'Square Root', 2.66, 0.013, 0.8507, 33.8, 12.93, 15, 14, 180, 'Fingas'],
                        [9, 'Arabian Light (2001)', 'Fingas', 'Logarithmic', 2.4, 0.045, 0.8641, 31.3, 15.04, 15, 16, 180, 'Fingas'],
                        # [10, 'Arabian  Medium (2000)', 'Fingas', 'Logarithmic', 2.18, 0.045, 0.8738, 29.5, 25.17, 15, , 180, 'Fingas'],
                        # [11, 'Av Gas 80', 'Fingas', 'Logarithmic', 15.4, 0.045, 0.6953, 71.8, 1.44, 15, , 180, 'Fingas'],
                        [12, 'Avalon  J-34', 'Fingas', 'Logarithmic', 1.58, 0.045, 0.844, 36, 170.62, 15, 13, 180, 'Fingas'],
                        [13, 'Aviation Gasoline 100 LL', 'Fingas', 'Logarithmic', 0.5, 0.045, 0.7143, 66.6, 1.4, 15, 85, 180, 'Fingas'],
                        [14, 'Barrow Island, Australia', 'Fingas', 'Logarithmic', 4.67, 0.045, 0.841, 36.7, 2.38, 15, 5, 180, 'Fingas'],
                        [15, 'BCF-24, Venezuela', 'Fingas', 'Logarithmic', 1.08, 0.045, 0.9129, 23.4, 136.93, 15, 4, 180, 'Fingas'],
                        [16, 'Belridge Crude, CA, USA(Heavy)', 'Fingas', 'Square Root', 0.01, 0.013, 0.9746, 13.6, 12938.64, 15, 1, 180, 'Fingas'],
                        # [17, 'Bent Horn A-02, NS, Canada', 'Fingas', 'Logarithmic', 3.19, 0.045, 0.8177, 41.5, 14.68, 15, , 180, 'Fingas'],
                        [18, 'Beta, CA, USA', 'Fingas', 'Square Root', -0.08, 0.013, 0.9738, 13.7, 13739.99, 15, 5, 180, 'Fingas'],
                        [19, 'Boscan, Venezuela', 'Fingas', 'Square Root', -0.15, 0.013, 0.993, 10.1, 488922.46, 15, 2, 180, 'Fingas'],
                        [20, 'Brent, United Kingdom(Blend)', 'Fingas', 'Logarithmic', 3.39, 0.048, 0.8351, 37.8, 7.18, 15, 29, 180, 'Fingas'],
                        [21, 'California API 11', 'Fingas', 'Square Root', -0.13, 0.013, 0.9882, 10.3, 34405.99, 15, 5, 180, 'Fingas'],
                        [22, 'California API 15', 'Fingas', 'Square Root', -0.14, 0.013, 0.977, 13.2, 6550.67, 15, 7, 180, 'Fingas'],
                        [23, 'Cano Limon, Colombia(ESD)', 'Fingas', 'Logarithmic', 1.71, 0.045, 0.8817, 28.8, 52.17, 15, 14, 180, 'Fingas'],
                        [24, 'Carpenteria, CA, USA', 'Fingas', 'Logarithmic', 1.68, 0.045, 0.9155, 22.9, 17.94, 15, 1, 180, 'Fingas'],
                        [25, 'Cold Lake Winter Blend  [2013]', 'Fingas', 'Logarithmic', 1.51, 0.045, 0.9249, 21, 308.14, 15, 27, 180, 'Fingas'],
                        [26, 'Cusiana, Colombia(ESD)', 'Fingas', 'Logarithmic', 3.39, 0.045, 0.8328, 38.3, 8.41, 15, 25, 180, 'Fingas'],
                        [27, 'Diesel (2002)', 'Fingas', 'Square Root', 0.02, 0.013, 0.831, 37.5, 3.37, 15, 27, 180, 'Fingas'],
                        [28, 'Dos Cuadros, CA, USA', 'Fingas', 'Logarithmic', 1.88, 0.045, 0.9, 25.6, 56.67, 15, 17, 180, 'Fingas'],
                        [29, 'DOBA', 'Fingas', 'Square Root', -0.11, 0.013, 0.9271, 20.7, 3343.76, 15, 4, 180, 'Fingas'],
                        [30, 'Ekofisk, Norway(ESD)', 'Fingas', 'Logarithmic', 4.92, 0.045, 0.8283, 39.2, 6.04, 15, 28, 180, 'Fingas'],
                        [31, 'Empire Crude, LA, USA', 'Fingas', 'Logarithmic', 2.21, 0.045, 0.8554, 33.8, 12.86, 15, 16, 180, 'Fingas'],
                        [32, 'Endicott, AK, USA', 'Fingas', 'Logarithmic', 0.9, 0.045, 0.9149, 23, 91.81, 15, 9, 180, 'Fingas'],
                        [33, 'Eugene Island Block 32', 'Fingas', 'Logarithmic', 0.77, 0.045, 0.8399, 36.9, 11.91, 15, 7, 180, 'Fingas'],
                        [34, 'Eugene Island Block 43', 'Fingas', 'Logarithmic', 1.57, 0.045, 0.8404, 36.8, 15.47, 15, 13, 180, 'Fingas'],
                        [35, 'Everdell, AB, Canada', 'Fingas', 'Logarithmic', 3.38, 0.045, 0.8064, 44, 4.96, 15, 28, 180, 'Fingas'],
                        [36, 'FCC Heavy cycle', 'Fingas', 'Square Root', 0.17, 0.013, 0.9075, 24.3, 3.31, 15, 5, 180, 'Fingas'],
                        # [37, 'FCC Light', 'Fingas', 'Square Root', -0.17, 0.013, 1.062, 1.6, 6984.93, 15, , 180, 'Fingas'],
                        # [38, 'FCC Medium cycle', 'Fingas', 'Square Root', -0.16, 0.013, 0.9835, 12.3, 31.52, 15, , 180, 'Fingas'],
                        [39, 'FCC-VGO', 'Fingas', 'Square Root', 2.5, 0.013, 0.8662, 31.8, 1.15, 15, 91, 180, 'Fingas'],
                        [40, 'Federated (new -1998)', 'Fingas', 'Logarithmic', 3.45, 0.045, 0.8298, 38.9, 6.03, 15, 28, 180, 'Fingas'],
                        [41, 'Fuel Oil #5', 'Fingas', 'Square Root', -0.14, 0.013, 0.9883, 11.6, 1426.7, 15, 1, 180, 'Fingas'],
                        [42, 'Garden Banks 387, GOM, USA', 'Fingas', 'Logarithmic', 1.84, 0.045, 0.8782, 29.5, 33.02, 15, 10, 180, 'Fingas'],
                        [43, 'Genesis, GOM, USA', 'Fingas', 'Logarithmic', 2.12, 0.045, 0.8841, 28.4, 29.41, 15, 10, 180, 'Fingas'],
                        [44, 'Green Canyon Block 109', 'Fingas', 'Logarithmic', 1.58, 0.045, 0.8921, 27, 43.72, 15, 12, 180, 'Fingas'],
                        [45, 'Green Canyon Block 184', 'Fingas', 'Logarithmic', 3.55, 0.045, 0.8314, 39.4, 6.01, 15, 25, 180, 'Fingas'],
                        [46, 'Green Canyon Block 200', 'Fingas', 'Logarithmic', 3.11, 0.045, 0.8501, 33.9, 12.94, 15, 23, 180, 'Fingas'],
                        [47, 'Green Canyon Block 65', 'Fingas', 'Logarithmic', 1.56, 0.045, 0.9365, 19.5, 189, 15, 9, 180, 'Fingas'],
                        [48, 'Gulfaks, Norway(ESD)', 'Fingas', 'Logarithmic', 2.29, 0.034, 0.8701, 31, 14.94, 15, 18, 180, 'Fingas'],
                        [49, 'Harmony ', 'Fingas', 'Logarithmic', 0.85, 0.045, 0.9456, 17.8, 3257.2, 15, 19, 180, 'Fingas'],
                        [50, 'Heavy Reformate', 'Fingas', 'Square Root', -0.17, 0.013, 0.9226, 10.1, 1431.82, 15, 1, 180, 'Fingas'],
                        [51, 'Heidrun, Norway', 'Fingas', 'Logarithmic', 1.95, 0.045, 0.8835, 28.6, 20.37, 15, 16, 180, 'Fingas'],
                        [52, 'High Viscosity Fuel Oil', 'Fingas', 'Square Root', -0.12, 0.013, 1.014, 8, 13274.16, 15, 1, 180, 'Fingas'],
                        [53, 'Hondo, CA, USA', 'Fingas', 'Logarithmic', 1.49, 0.045, 0.9356, 19.6, 785.59, 15, 12, 180, 'Fingas'],
                        [54, 'Hout, Kuwait', 'Fingas', 'Logarithmic', 2.29, 0.045, 0.8628, 32.4, 17.39, 15, 20, 180, 'Fingas'],
                        [55, 'IFO-120', 'Fingas', 'Square Root', -0.11, 0.013, 0.9567, 16.1, 1609.7, 15, 5, 180, 'Fingas'],
                        [56, 'IFO-180(2011)', 'Fingas', 'Square Root', -0.15, 0.013, 0.9664, 14.7, 19867.55, 15, 2, 180, 'Fingas'],
                        [57, 'Iranian Heavy', 'Fingas', 'Logarithmic', 2.27, 0.045, 0.8756, 31, 22.84, 15, 18, 180, 'Fingas'],
                        [58, 'Isthmus, Mexico', 'Fingas', 'Logarithmic', 2.48, 0.045, 0.8645, 32, 15.04, 15, 19, 180, 'Fingas'],
                        # [59, 'Jet A1', 'Fingas', 'Square Root', 0.59, 0.013, 0.8159, 41.8, 2.45, 15, , 180, 'Fingas'],
                        [60, 'Komineft, Russian', 'Fingas', 'Logarithmic', 2.73, 0.045, 0.8408, 36.7, 15.46, 15, 21, 180, 'Fingas'],
                        [61, 'Lago, Angola', 'Fingas', 'Logarithmic', 1.13, 0.045, 0.8907, 27.3, 171.78, 15, 10, 180, 'Fingas'],
                        [62, 'Lago Treco, Venezuela', 'Fingas', 'Logarithmic', 1.12, 0.045, 0.923, 22.6, 294.69, 15, 11, 180, 'Fingas'],
                        [63, 'Lucula, Angola', 'Fingas', 'Logarithmic', 2.17, 0.045, 0.8574, 33.4, 50.15, 15, 16, 180, 'Fingas'],
                        [64, 'Main Pass Block 306', 'Fingas', 'Logarithmic', 2.86, 0.045, 0.8606, 32.8, 10.46, 15, 23, 180, 'Fingas'],
                        [65, 'Main Pass Block 37', 'Fingas', 'Logarithmic', 3.04, 0.045, 0.8311, 33, 8.42, 15, 25, 180, 'Fingas'],
                        [66, 'Malongo, Angola', 'Fingas', 'Logarithmic', 1.67, 0.045, 0.8701, 31, 72.41, 15, 13, 180, 'Fingas'],
                        [67, 'Mars TLP, GOM, USA', 'Fingas', 'Logarithmic', 2.18, 0.045, 0.8883, 27.6, 37.15, 15, 10, 180, 'Fingas'],
                        [68, 'Maui, New Zealand', 'Fingas', 'Square Root', -0.14, 0.013, 0.8081, 44.3, 18.56, 15, 31, 180, 'Fingas'],
                        [69, 'Mississipi Canyon Block 807', 'Fingas', 'Logarithmic', 2.28, 0.045, 0.9461, 17.5, 5.07, 15, 18, 180, 'Fingas'],
                        [70, 'Mississippi Canyon Bk. 72', 'Fingas', 'Logarithmic', 2.15, 0.045, 0.8649, 32, 18.5, 15, 16, 180, 'Fingas'],
                        [71, 'Mississippi Canyon Block 194', 'Fingas', 'Logarithmic', 2.62, 0.045, 0.8483, 32, 8.25, 15, 18, 180, 'Fingas'],
                        [72, 'Mississippi Canyon Block 807', 'Fingas', 'Logarithmic', 2.05, 0.045, 0.8894, 27.5, 46.1, 15, 18, 180, 'Fingas'],
                        [73, 'Morpeth Block EW921', 'Fingas', 'Square Root', 1.58, 0.013, 0.8996, 25.1, 50.02, 15, 11, 180, 'Fingas'],
                        [74, 'Neptune Spar (Viosca Knoll 826)', 'Fingas', 'Logarithmic', 3.75, 0.045, 0.8687, 31.2, 19.57, 15, 9, 180, 'Fingas'],
                        [75, 'Norman Wells, Canada', 'Fingas', 'Logarithmic', 3.11, 0.045, 0.832, 38.4, 6.01, 15, 23, 180, 'Fingas'],
                        [76, 'North Star, Alaska, USA', 'Fingas', 'Logarithmic', 2.93, 0.045, 0.8573, 32.5, 10.38, 15, 26, 180, 'Fingas'],
                        [77, 'Odoptu, Russian', 'Fingas', 'Logarithmic', 4.27, 0.045, 0.8556, 32.9, 6.19, 15, 33, 180, 'Fingas'],
                        [78, 'Panuke, NS, Canada', 'Fingas', 'Logarithmic', 7.12, 0.045, 0.7757, 50.8, 1, 15, 51, 180, 'Fingas'],
                        [79, 'Petronius Block VK786A', 'Fingas', 'Square Root', 2.27, 0.013, 0.8713, 30, 31.67, 15, 14, 180, 'Fingas'],
                        [80, 'Pitas Point, CA, USA', 'Fingas', 'Logarithmic', 7.04, 0.045, 0.8341, 38, 2.4, 15, 28, 180, 'Fingas'],
                        [81, 'Platform Gail (Sockeye)', 'Fingas', 'Logarithmic', 1.68, 0.045, 0.9297, 20.6, 436.7, 15, 13, 180, 'Fingas'],
                        [82, 'Platform Holly, CA, USA', 'Fingas', 'Logarithmic', 1.09, 0.045, 0.9928, 11, 3338.03, 15, 12, 180, 'Fingas'],
                        [83, 'Point Arguello- comingled', 'Fingas', 'Logarithmic', 1.43, 0.045, 0.9248, 21.4, 576.34, 15, 12, 180, 'Fingas'],
                        [84, 'Point Arguello Heavy', 'Fingas', 'Logarithmic', 0.94, 0.045, 0.9447, 18.2, 3440.25, 15, 9, 180, 'Fingas'],
                        [85, 'Point Arguello Light', 'Fingas', 'Logarithmic', 2.44, 0.045, 0.8739, 30.3, 25.17, 15, 19, 180, 'Fingas'],
                        # [86, 'Polypropylene Tetramer', 'Fingas', 'Other', , , 0.7746, 51.1, 2.58, 15, 12, 180, 'Fingas'],
                        [87, 'Port Hueneme, CA, USA', 'Fingas', 'Logarithmic', 0.3, 0.045, 0.9662, 14.8, 4275.51, 15, 4, 180, 'Fingas'],
                        [88, 'Rock, California, USA', 'Fingas', 'Square Root', -0.11, 0.013, 0.9674, 14.5, 4506.92, 15, 9, 180, 'Fingas'],
                        [89, 'Rangely, CO, USA', 'Fingas', 'Logarithmic', 1.89, 0.045, 0.8567, 33.7, 38.52, 15, 14, 180, 'Fingas'],
                        [90, 'Sakhalin, Russia', 'Fingas', 'Logarithmic', 4.16, 0.045, 0.8632, 32.3, 4.63, 15, 29, 180, 'Fingas'],
                        [91, 'Santa Clara, CA, USA', 'Fingas', 'Logarithmic', 1.63, 0.045, 0.9202, 22.1, 330.36, 15, 14, 180, 'Fingas'],
                        [92, 'Ship Shoal Block 239', 'Fingas', 'Logarithmic', 2.71, 0.045, 0.8972, 26.1, 37.9, 15, 20, 180, 'Fingas'],
                        [93, 'Ship Shoal Block 269', 'Fingas', 'Logarithmic', 3.37, 0.045, 0.8309, 38.7, 6.02, 15, 25, 180, 'Fingas'],
                        [94, 'Sockeye, CA, USA', 'Fingas', 'Logarithmic', 2.14, 0.045, 0.8965, 26.2, 50.2, 15, 18, 180, 'Fingas'],
                        [95, 'Sockeye (2001)', 'Fingas', 'Logarithmic', 1.52, 0.045, 0.9354, 19.32, 813.56, 15, 11, 180, 'Fingas'],
                        [96, 'Sockeye Co-mingled', 'Fingas', 'Logarithmic', 1.38, 0.045, 0.935, 19.8, 588.24, 15, 13, 180, 'Fingas'],
                        # [97, 'Sockeye Sour, CA, USA', 'Fingas', '', 1.52, 0.045, 0.9354, 19.3, 812.5, 15, 11, 180, 'Fingas'],
                        # [98, 'Sockeye Sweet', 'Fingas', 'Logarithmic', 2.39, 0.045, 0.8792, 29.4, 22.75, 15, , 180, 'Fingas'],
                        # [99, 'South Louisiana', 'Fingas', 'Logarithmic', 2.39, 0.045, 0.839, 37, 8.46, 15, , 180, 'Fingas'],
                        [100, 'South Louisiana (2001)', 'Fingas', 'Logarithmic', 2.74, 0.045, 0.8562, 32.7, 11.79, 15, 18, 180, 'Fingas'],
                        [101, 'South Pass Block 60', 'Fingas', 'Logarithmic', 2.91, 0.045, 0.8453, 35.8, 10.65, 15, 23, 180, 'Fingas'],
                        [102, 'South Pass Block 67', 'Fingas', 'Logarithmic', 2.17, 0.045, 0.9564, 16.4, 25.09, 15, 26, 180, 'Fingas'],
                        [103, 'South Pass Block 93', 'Fingas', 'Logarithmic', 1.5, 0.045, 0.8574, 33.4, 22.16, 15, 15, 180, 'Fingas'],
                        [104, 'South Timbalier Block 130', 'Fingas', 'Logarithmic', 2.77, 0.045, 0.8487, 35.1, 8.25, 15, 20, 180, 'Fingas'],
                        [105, 'Statfjord, Norway', 'Fingas', 'Logarithmic', 2.67, 0.06, 0.8354, 37.8, 7.18, 15, 20, 180, 'Fingas'],
                        [106, 'Takula, Angola', 'Fingas', 'Logarithmic', 1.95, 0.045, 0.8637, 32.2, 127.36, 15, 18, 180, 'Fingas'],
                        [107, 'Terra Nova, NL, Canada(Petawawa)', 'Fingas', 'Logarithmic', 2.32, 0.045, 0.8624, 14.5, 20.29, 15, 21, 180, 'Fingas'],
                        [108, 'Thevenard Island, Australia', 'Fingas', 'Logarithmic', 5.74, 0.045, 0.7855, 48.6, 1.27, 15, 42, 180, 'Fingas'],
                        [109, 'Vasconia, Colombia', 'Fingas', 'Logarithmic', 0.84, 0.045, 0.8958, 26.3, 80.38, 15, 7, 180, 'Fingas'],
                        [110, 'Viosca Knoll Block 826', 'Fingas', 'Logarithmic', 2.04, 0.045, 0.8668, 31.6, 18.46, 15, 16, 180, 'Fingas'],
                        [111, 'Viosca Knoll Block 990', 'Fingas', 'Logarithmic', 3.16, 0.045, 0.8337, 38.1, 8.4, 15, 22, 180, 'Fingas'],
                        [112, 'Waxy Light and Heavy', 'Fingas', 'Logarithmic', 1.52, 0.045, 0.9311, 20.4, 197.62, 15, 10, 180, 'Fingas'],
                        [113, 'West Delta Block 30 w/water', 'Fingas', 'Square Root', -0.04, 0.013, 0.9894, 11.4, 1192.64, 15, 4, 180, 'Fingas'],
                        [114, 'West Texas Intermediate', 'Fingas', 'Logarithmic', 3.08, 0.045, 0.8474, 34.4, 10.15, 15, 20, 180, 'Fingas'],
                        [115, 'West Texas Sour', 'Fingas', 'Logarithmic', 2.57, 0.045, 0.8743, 30.2, 14.87, 15, 19, 180, 'Fingas']
                        ]

HCA_INT_METHOD_LOOKUP_TABLE_FIELD_DESCRIPTION = [["INT_METHOD", "Text", "Intersection Method", 20],
                                                ["INT_METHOD_DESC", "Text", "Intersection Method Description", 100]]
HCA_INT_METHOD_LOOKUP_TABLE_FIELDS = ["INT_METHOD", "INT_METHOD_DESC"]
HCA_INT_METHOD_LOOKUP_TABLE_RECORDS = [
                    ["CL_DIR", "Centerline Direct Intersection"],
                    ["CL_IND", "Centerline Indirect Intersection"],
                    ["CLOFHTWB_DIR", "Centerline Overland Flow Hydrographic Transport Waterbody Direct Intersection"],
                    ["CLOFHTWB_IND", "Centerline Overland Flow Hydrographic Transport Waterbody Indirect Intersection"],
                    ["OFHTWB_DIR", "Overland Flow Hydrographic Transport Waterbody Direct Intersection"],
                    ["OFHTWB_IND", "Overland Flow Hydrographic Transport Waterbody Indirect Intersection"]
                   ]

HCA_GROUP_LOOKUP_TABLE_FIELD_DESCRIPTION = [["HCA_GROUP", "Text", "HCA Group", 20],
                                            ["HCA_GROUP_DESC", "Text", "HCA Group Description", 60]]

HCA_GROUP_LOOKUP_TABLE_FIELDS = ["HCA_GROUP", "HCA_GROUP_DESC"]
HCA_GROUP_LOOKUP_TABLE_RECORDS = [["HpaOpaNwEcDw", "Any Hpa, Opa, Nw, Ec, or Dw Intersections"],
                                    ["Hpa", "High Population Area Intersections"],
                                    ["Opa", "Other Populated Area Intersections"],
                                    ["Nw", "Commercially Navigable Waterway Intersections"],
                                    ["Ec", "Ecological Area Intersections"],
                                    ["Dw", "Drinking Water Area Intersections"],
                                    ["None", "No HCA Intersections"]
                                    ]

HCA_CA_SEGMENTS_DEF_TABLE_FIELD_DESCRIPTION = [["CA_DEF_ID", "Long", "CA Definition ID", None],
                                                ["INT_METHOD", "Text", "Intersection Method", 20],
                                                ["HCA_GROUP", "Text", "HCA Group", 20],
                                                ["HCA_CA_SEG_DEF_SQL", "Text", "HCA CA Segment Def SQL", 1000]
                                                ]

HCA_CA_SEGMENTS_DEF_TABLE_FIELDs = ["CA_DEF_ID", "INT_METHOD", "HCA_GROUP","HCA_CA_SEG_DEF_SQL"]
HCA_CA_SEGMENTS_DEF_TABLE_RECORDS = [[1, "CL_DIR", "HpaOpaNwEcDw", "((CL_NW_DIR > 0) OR (CL_HPA_DIR > 0) OR (CL_OPA_DIR > 0) OR (CL_EC_DIR > 0) OR (CL_DW_DIR > 0))"],
                                    [2, "CL_DIR", "Hpa", "(CL_HPA_DIR > 0)"],
                                    [3, "CL_DIR", "Opa", "(CL_OPA_DIR > 0)"],
                                    [4, "CL_DIR", "Nw", "(CL_NW_DIR > 0)"],
                                    [5, "CL_DIR", "Ec", "(CL_EC_DIR > 0)"],
                                    [6, "CL_DIR", "Dw", "(CL_DW_DIR > 0)"],
                                    # [7, "CL_DIR", "None", "(CL_DIR_INT <= 0)"],

                                    [8, "CL_IND", "HpaOpaNwEcDw", "((CL_NW_IND > 0) OR (CL_HPA_IND > 0) OR (CL_OPA_IND > 0) OR (CL_EC_IND > 0) OR (CL_DW_IND > 0) )"],
                                    [9, "CL_IND", "Hpa", "(CL_HPA_IND > 0)"],
                                    [10, "CL_IND", "Opa", "(CL_OPA_IND > 0)"],
                                    [11, "CL_IND", "Nw", "(CL_NW_IND > 0)"],
                                    [12, "CL_IND", "Ec", "(CL_EC_IND > 0)"],
                                    [13, "CL_IND", "Dw", "(CL_DW_IND > 0)"],

                                    [14, "CLOFHTWB_DIR", "HpaOpaNwEcDw", "((CL_NW_DIR > 0) OR (CL_HPA_DIR > 0) OR (CL_OPA_DIR > 0) OR "
                                                                           "(CL_EC_DIR > 0) OR (CL_DW_DIR > 0) OR (OF_NW_DIR > 0) OR "
                                                                           "(OF_HPA_DIR > 0) OR (OF_OPA_DIR > 0) OR (OF_EC_DIR > 0) OR "
                                                                           "(OF_DW_DIR > 0) OR "                                                                           
                                                                           "(HT_NW_DIR > 0) OR (HT_HPA_DIR > 0) OR (HT_OPA_DIR > 0) OR "
                                                                           "(HT_EC_DIR > 0) OR (HT_DW_DIR > 0) OR (WB_NW_DIR > 0) OR "
                                                                           "(WB_HPA_DIR > 0) OR (WB_OPA_DIR > 0) OR (WB_EC_DIR > 0) OR (WB_DW_DIR > 0))"],
                                    [15, "CLOFHTWB_DIR", "Hpa", "((CL_HPA_DIR > 0) OR (OF_HPA_DIR > 0) OR (HT_HPA_DIR > 0) OR (WB_HPA_DIR > 0))"],
                                    [16, "CLOFHTWB_DIR", "Opa", "((CL_OPA_DIR > 0) OR (OF_OPA_DIR > 0) OR (HT_OPA_DIR > 0) OR (WB_OPA_DIR > 0))"],
                                    [17, "CLOFHTWB_DIR", "Nw", "((CL_NW_DIR > 0) OR (OF_NW_DIR > 0) OR (HT_NW_DIR > 0) OR (WB_NW_DIR > 0))"],
                                    [18, "CLOFHTWB_DIR", "Ec", "((CL_EC_DIR > 0) OR (OF_EC_DIR > 0) OR (HT_EC_DIR > 0) OR (WB_EC_DIR > 0))"],
                                    [19, "CLOFHTWB_DIR", "Dw", "((CL_DW_DIR > 0) OR (OF_DW_DIR > 0) OR (HT_DW_DIR > 0) OR (WB_DW_DIR > 0))"],
                                    # [20, "CLOFHTWB_DIR", "None", "((CL_DIR_INT <= 0) AND (OF_DIR_INT <= 0) AND (HT_DIR_INT <= 0) AND (WB_DIR_INT <= 0 ))"],

                                    [21, "CLOFHTWB_IND", "HpaOpaNwEcDw", "((CL_NW_IND > 0) OR (CL_HPA_IND > 0) OR (CL_OPA_IND > 0) OR "
                                                                           "(CL_EC_IND > 0) OR (CL_DW_IND > 0) OR (OF_NW_IND > 0) OR "
                                                                           "(OF_HPA_IND > 0) OR (OF_OPA_IND > 0) OR (OF_EC_IND > 0) OR "
                                                                           "(OF_DW_IND > 0) OR "                                                                          
                                                                           "(HT_NW_IND > 0) OR (HT_HPA_IND > 0) OR (HT_OPA_IND > 0) OR "
                                                                           "(HT_EC_IND > 0) OR (HT_DW_IND > 0) OR  (WB_NW_IND > 0) OR "
                                                                           "(WB_HPA_IND > 0) OR (WB_OPA_IND > 0) OR (WB_EC_IND > 0) OR (WB_DW_IND > 0) )"],
                                    [22, "CLOFHTWB_IND", "Hpa", "((CL_HPA_IND > 0) OR (OF_HPA_IND > 0) OR (HT_HPA_IND > 0) OR (WB_HPA_IND > 0))"],
                                    [23, "CLOFHTWB_IND", "Opa", "((CL_OPA_IND > 0) OR (OF_OPA_IND > 0) OR (HT_OPA_IND > 0) OR (WB_OPA_IND > 0))"],
                                    [24, "CLOFHTWB_IND", "Nw", "((CL_NW_IND > 0) OR (OF_NW_IND > 0) OR (HT_NW_IND > 0) OR (WB_NW_IND > 0))"],
                                    [25, "CLOFHTWB_IND", "Ec", "((CL_EC_IND > 0) OR (OF_EC_IND > 0) OR (HT_EC_IND > 0) OR (WB_EC_IND > 0))"],
                                    [26, "CLOFHTWB_IND", "Dw", "((CL_DW_IND > 0) OR (OF_DW_IND > 0) OR (HT_DW_IND > 0) OR (WB_DW_IND > 0))"],
                                    # [27, "CLOFHTWB_IND", "None", "((CL_IND_INT <= 0) AND (OF_IND_INT <= 0) AND (HT_IND_INT <= 0) AND (WB_IND_INT <= 0 ))"],

                                    [28, "OFHTWB_DIR", "HpaOpaNwEcDw", "((OF_NW_DIR > 0) OR (OF_HPA_DIR > 0) OR (OF_OPA_DIR > 0) OR "
                                                                         "(OF_EC_DIR > 0) OR (OF_DW_DIR > 0) OR "                                                                        
                                                                         "(HT_NW_DIR > 0) OR (HT_HPA_DIR > 0) OR "
                                                                         "(HT_OPA_DIR > 0) OR (HT_EC_DIR > 0) OR (HT_DW_DIR > 0) OR "
                                                                         "(WB_NW_DIR > 0) OR (WB_HPA_DIR > 0) OR (WB_OPA_DIR > 0) OR "
                                                                         "(WB_EC_DIR > 0) OR (WB_DW_DIR > 0) )"],
                                    [29, "OFHTWB_DIR", "Hpa", "((OF_HPA_DIR > 0) OR (HT_HPA_DIR > 0) OR (WB_HPA_DIR > 0))"],
                                    [30, "OFHTWB_DIR", "Opa", "((OF_OPA_DIR > 0) OR (HT_OPA_DIR > 0) OR (WB_OPA_DIR > 0))"],
                                    [31, "OFHTWB_DIR", "Nw", "((OF_NW_DIR > 0) OR (HT_NW_DIR > 0) OR (WB_NW_DIR > 0))"],
                                    [32, "OFHTWB_DIR", "Ec", "((OF_EC_DIR > 0) OR (HT_EC_DIR > 0) OR (WB_EC_DIR > 0))"],
                                    [33, "OFHTWB_DIR", "Dw", "((OF_DW_DIR > 0) OR (HT_DW_DIR > 0) OR (WB_DW_DIR > 0))"],
                                    # [34, "OFHTWB_DIR", "None", "((OF_DIR_INT <= 0) AND (HT_DIR_INT <= 0) AND (WB_DIR_INT <= 0 ))"],

                                    [35, "OFHTWB_IND", "HpaOpaNwEcDw", "((OF_NW_IND > 0) OR (OF_HPA_IND > 0) OR (OF_OPA_IND > 0) OR "
                                                                         "(OF_EC_IND > 0) OR (OF_DW_IND > 0) OR "                                                                       
                                                                         "(HT_NW_IND > 0) OR (HT_HPA_IND > 0) OR "
                                                                         "(HT_OPA_IND > 0) OR (HT_EC_IND > 0) OR (HT_DW_IND > 0) OR "
                                                                         "(WB_NW_IND > 0) OR (WB_HPA_IND > 0) OR (WB_OPA_IND > 0) OR "
                                                                         "(WB_EC_IND > 0) OR (WB_DW_IND > 0))"],
                                    [36, "OFHTWB_IND", "Hpa", "((OF_HPA_IND > 0) OR (HT_HPA_IND > 0) OR (WB_HPA_IND > 0))"],
                                    [37, "OFHTWB_IND", "Opa", "((OF_OPA_IND > 0) OR (HT_OPA_IND > 0) OR (WB_OPA_IND > 0))"],
                                    [38, "OFHTWB_IND", "Nw", "((OF_NW_IND > 0) OR (HT_NW_IND > 0) OR (WB_NW_IND > 0))"],
                                    [39, "OFHTWB_IND", "Ec", "((OF_EC_IND > 0) OR (HT_EC_IND > 0) OR (WB_EC_IND > 0))"],
                                    [40, "OFHTWB_IND", "Dw", "((OF_DW_IND > 0) OR (HT_DW_IND > 0) OR (WB_DW_IND > 0))"]
                                     ]

NHD_HUC4_VELOCITY_TABLE_FIELD_DESCRIPTION = [["SUBREGION", "Text", "Sub Region", 14],
                                    ["VEL_AVG", "Double", "VEL_AVG", 8],
                                    ["VEL_STDEV" , "Double", "VEL_STDEV", 8],
                                    ["VEL_1STDEV" , "Double", "VEL_1STDEV" , 8],
                                    ["VEL_2STDEV" , "Double", "VEL_2STDEV" , 8]
                                    ]

NHD_HUC4_VELOCITY_TABLE_FIELDS = ['SUBREGION', 'VEL_AVG', 'VEL_STDEV', 'VEL_1STDEV', 'VEL_2STDEV']
NHD_HUC4_VELOCITY_TABLE_RECORDS = [["103", 2.07, 1.72, 3.79, 5.5 ], ["104", 1.71, 1.56, 3.27, 4.83]
                                , ["105", 1.63, 1.21, 2.85, 4.06], ["106", 1.31, 1.2 , 2.51, 3.7 ]
                                , ["107", 1.72, 1.27, 2.99, 4.26], ["108", 1.56, 1.18, 2.74, 3.92]
                                , ["109", 1.3 , 0.98, 2.28, 3.26], ["110", 1.5 , 1.09, 2.59, 3.68]
                                , ["111", 1.51, 1.15, 2.66, 3.81], ["201", 1.76, 1.29, 3.05, 4.35]
                                , ["202", 1.57, 1.23, 2.8 , 4.03], ["203", 1.15, 0.89, 2.03, 2.92]
                                , ["204", 1.31, 0.92, 2.24, 3.16], ["205", 1.62, 1.06, 2.68, 3.74]
                                , ["206", 1.09, 0.76, 1.85, 2.61], ["207", 1.29, 1.02, 2.31, 3.33]
                                , ["208", 1.37, 0.97, 2.34, 3.31], ["301", 1.21, 0.82, 2.03, 2.85]
                                , ["302", 1.21, 0.77, 1.98, 2.75], ["303", 1.06, 0.83, 1.89, 2.73]
                                , ["304", 1.23, 0.83, 2.06, 2.89], ["305", 1.3 , 0.96, 2.26, 3.21]
                                , ["306", 1.34, 0.78, 2.11, 2.89], ["307", 1.4 , 0.84, 2.24, 3.07]
                                , ["308", 0.55, 0.43, 0.98, 1.42], ["309", 0.66, 0.43, 1.1 , 1.53]
                                , ["310", 0.86, 0.56, 1.42, 1.99], ["311", 1.06, 0.68, 1.74, 2.41]
                                , ["312", 0.93, 0.52, 1.45, 1.97], ["313", 1.35, 0.81, 2.16, 2.96]
                                , ["314", 1.44, 0.78, 2.22, 2.99], ["315", 1.51, 0.93, 2.44, 3.37]
                                , ["316", 1.41, 1.03, 2.44, 3.47], ["317", 1.55, 0.88, 2.43, 3.31]
                                , ["318", 1.25, 0.81, 2.06, 2.86], ["401", 1.47, 0.91, 2.38, 3.29]
                                , ["402", 1.7 , 1.08, 2.78, 3.85], ["403", 1.48, 1.  , 2.48, 3.48]
                                , ["404", 1.18, 0.82, 2.  , 2.82], ["405", 1.47, 0.78, 2.24, 3.02]
                                , ["406", 1.78, 0.75, 2.52, 3.27], ["407", 2.17, 0.87, 3.04, 3.9 ]
                                , ["408", 1.44, 0.81, 2.26, 3.07], ["409", 1.19, 0.71, 1.9 , 2.6 ]
                                , ["410", 1.51, 1.03, 2.54, 3.57], ["411", 2.09, 1.18, 3.27, 4.44]
                                , ["412", 1.54, 1.03, 2.57, 3.6 ], ["413", 1.81, 1.2 , 3.02, 4.22]
                                , ["414", 1.52, 1.15, 2.67, 3.82], ["415", 1.79, 1.32, 3.11, 4.44]
                                , ["501", 1.82, 1.11, 2.93, 4.04], ["502", 1.61, 1.11, 2.72, 3.82]
                                , ["503", 1.74, 1.14, 2.87, 4.01], ["504", 1.8 , 0.97, 2.77, 3.74]
                                , ["505", 1.56, 1.19, 2.75, 3.94], ["506", 1.59, 1.07, 2.66, 3.73]
                                , ["507", 1.72, 1.15, 2.86, 4.01], ["508", 1.81, 1.07, 2.88, 3.95]
                                , ["509", 1.6 , 1.09, 2.7 , 3.79], ["510", 1.56, 1.06, 2.62, 3.68]
                                , ["511", 1.59, 0.93, 2.53, 3.46], ["512", 1.48, 1.  , 2.47, 3.47]
                                , ["513", 1.54, 1.  , 2.54, 3.54], ["514", 1.21, 1.04, 2.25, 3.29]
                                , ["601", 1.47, 1.02, 2.49, 3.52], ["602", 1.2 , 0.74, 1.94, 2.68]
                                , ["603", 1.2 , 0.84, 2.05, 2.89], ["604", 1.51, 1.02, 2.53, 3.55]
                                , ["701", 1.74, 0.98, 2.72, 3.7 ], ["702", 1.68, 1.28, 2.96, 4.24]
                                , ["703", 2.56, 2.01, 4.57, 6.58], ["704", 1.69, 1.03, 2.72, 3.76]
                                , ["705", 1.61, 1.07, 2.67, 3.74], ["706", 1.69, 0.95, 2.64, 3.59]
                                , ["707", 1.53, 0.76, 2.29, 3.06], ["708", 1.61, 1.07, 2.67, 3.74]
                                , ["709", 1.61, 0.81, 2.41, 3.22], ["710", 1.8 , 1.24, 3.04, 4.28]
                                , ["711", 1.38, 1.04, 2.42, 3.46], ["712", 1.26, 0.82, 2.08, 2.9 ]
                                , ["713", 1.38, 0.83, 2.21, 3.04], ["714", 2.24, 1.63, 3.87, 5.5 ]
                                , ["801", 1.56, 1.11, 2.67, 3.79], ["802", 1.3 , 0.81, 2.12, 2.93]
                                , ["803", 1.27, 0.84, 2.11, 2.95], ["804", 1.25, 0.84, 2.09, 2.93]
                                , ["805", 0.93, 0.55, 1.48, 2.04], ["806", 1.64, 1.05, 2.69, 3.75]
                                , ["807", 1.41, 0.67, 2.08, 2.76], ["808", 0.88, 0.53, 1.41, 1.94]
                                , ["809", 2.45, 1.52, 3.97, 5.49], ["901", 1.01, 0.74, 1.75, 2.5 ]
                                , ["902", 1.35, 1.01, 2.36, 3.36], ["903", 1.43, 0.86, 2.28, 3.14]
                                , ["1001", 1.96, 1.13, 3.09, 4.22], ["1002", 2.66, 1.36, 4.02, 5.38]
                                , ["1003", 2.11, 1.17, 3.28, 4.46], ["1004", 1.93, 1.21, 3.14, 4.35]
                                , ["1005", 1.51, 0.98, 2.5 , 3.48], ["1006", 1.8 , 0.98, 2.78, 3.77]
                                , ["1007", 2.74, 1.86, 4.6 , 6.46], ["1008", 2.15, 1.38, 3.53, 4.9 ]
                                , ["1009", 1.71, 1.07, 2.79, 3.86], ["1010", 2.19, 1.52, 3.71, 5.23]
                                , ["1011", 1.26, 0.92, 2.18, 3.09], ["1012", 1.4 , 0.9 , 2.3 , 3.2 ]
                                , ["1013", 1.31, 0.93, 2.25, 3.18], ["1014", 1.76, 1.12, 2.88, 4.  ]
                                , ["1015", 2.21, 0.99, 3.2 , 4.19], ["1016", 1.19, 0.91, 2.11, 3.02]
                                , ["1017", 1.41, 0.97, 2.37, 3.34], ["1018", 1.92, 1.29, 3.21, 4.5 ]
                                , ["1019", 1.66, 1.14, 2.8 , 3.94], ["1020", 1.7 , 0.89, 2.59, 3.49]
                                , ["1021", 2.25, 0.92, 3.17, 4.09], ["1022", 1.92, 1.12, 3.04, 4.16]
                                , ["1023", 2.99, 1.35, 4.34, 5.69], ["1024", 3.03, 1.51, 4.54, 6.05]
                                , ["1025", 1.31, 0.73, 2.03, 2.76], ["1026", 1.44, 0.85, 2.29, 3.14]
                                , ["1027", 1.69, 0.96, 2.64, 3.6 ], ["1028", 1.38, 1.  , 2.38, 3.38]
                                , ["1029", 1.77, 1.07, 2.83, 3.9 ], ["1030", 3.54, 1.22, 4.77, 5.99]
                                , ["1101", 1.96, 1.03, 2.99, 4.02], ["1102", 1.97, 1.21, 3.18, 4.38]
                                , ["1103", 1.57, 0.87, 2.43, 3.3 ], ["1104", 1.24, 1.09, 2.33, 3.42]
                                , ["1105", 1.54, 1.07, 2.61, 3.69], ["1106", 1.76, 0.9 , 2.67, 3.57]
                                , ["1107", 1.85, 1.4 , 3.25, 4.65], ["1108", 1.25, 0.88, 2.13, 3.  ]
                                , ["1109", 1.91, 1.69, 3.6 , 5.28], ["1110", 1.53, 0.98, 2.52, 3.5 ]
                                , ["1111", 1.57, 1.18, 2.75, 3.93], ["1112", 1.36, 0.95, 2.31, 3.25]
                                , ["1113", 1.55, 1.1 , 2.65, 3.75], ["1114", 1.12, 1.08, 2.2 , 3.28]
                                , ["1201", 1.11, 0.68, 1.79, 2.47], ["1202", 1.14, 0.62, 1.76, 2.38]
                                , ["1203", 1.49, 1.02, 2.51, 3.53], ["1204", 1.3 , 0.91, 2.21, 3.13]
                                , ["1205", 1.19, 0.93, 2.12, 3.05], ["1206", 1.59, 1.35, 2.94, 4.29]
                                , ["1207", 1.55, 1.13, 2.68, 3.81], ["1208", 1.08, 0.87, 1.95, 2.82]
                                , ["1209", 1.59, 1.2 , 2.79, 3.99], ["1210", 1.5 , 0.96, 2.46, 3.42]
                                , ["1211", 1.25, 0.99, 2.24, 3.22], ["1301", 0.  , 0.  , 0.  , 0.  ]
                                , ["1302", 2.22, 1.38, 3.6 , 4.98], ["1303", 2.13, 1.25, 3.38, 4.63]
                                , ["1304", 2.57, 1.36, 3.94, 5.3 ], ["1305", 2.57, 0.43, 3.  , 3.43]
                                , ["1306", 1.7 , 1.07, 2.77, 3.84], ["1307", 1.17, 1.01, 2.18, 3.19]
                                , ["1308", 0.  , 0.  , 0.  , 0.  ], ["1309", 0.  , 0.  , 0.  , 0.  ]
                                , ["1401", 2.05, 1.56, 3.62, 5.18], ["1402", 2.53, 1.56, 4.09, 5.65]
                                , ["1403", 2.43, 1.54, 3.96, 5.5 ], ["1404", 2.01, 1.34, 3.35, 4.7 ]
                                , ["1405", 2.27, 1.45, 3.72, 5.17], ["1406", 1.97, 1.29, 3.25, 4.54]
                                , ["1407", 1.88, 1.11, 3.  , 4.11], ["1408", 2.64, 1.69, 4.33, 6.02]
                                , ["1501", 2.13, 1.34, 3.47, 4.81], ["1502", 1.35, 1.26, 2.61, 3.87]
                                , ["1503", 1.8 , 1.04, 2.84, 3.88], ["1504", 1.75, 1.22, 2.97, 4.19]
                                , ["1505", 1.74, 1.35, 3.09, 4.44], ["1506", 1.47, 1.23, 2.7 , 3.94]
                                , ["1507", 1.62, 1.55, 3.18, 4.73], ["1508", 0.72, 0.76, 1.48, 2.23]
                                , ["1601", 1.83, 1.24, 3.07, 4.31], ["1602", 1.79, 1.3 , 3.09, 4.39]
                                , ["1603", 1.95, 1.21, 3.16, 4.37], ["1604", 1.49, 0.97, 2.46, 3.43]
                                , ["1605", 1.65, 1.24, 2.89, 4.13], ["1606", 1.83, 0.72, 2.55, 3.28]
                                , ["1701", 2.38, 1.55, 3.93, 5.48], ["1702", 0.  , 0.  , 0.  , 0.  ]
                                , ["1703", 0.  , 0.  , 0.  , 0.  ], ["1704", 2.49, 1.46, 3.94, 5.4 ]
                                , ["1705", 2.58, 1.51, 4.09, 5.6 ], ["1706", 2.82, 1.95, 4.77, 6.72]
                                , ["1707", 2.32, 1.43, 3.75, 5.18], ["1708", 1.75, 1.42, 3.17, 4.58]
                                , ["1709", 2.14, 1.57, 3.72, 5.29], ["1710", 1.92, 1.4 , 3.32, 4.72]
                                , ["1711", 0.  , 0.  , 0.  , 0.  ], ["1712", 1.38, 0.8 , 2.18, 2.98]
                                , ["1801", 2.29, 1.73, 4.02, 5.74], ["1802", 2.15, 1.78, 3.93, 5.7 ]
                                , ["1803", 1.12, 1.01, 2.12, 3.13], ["1804", 1.47, 1.14, 2.61, 3.76]
                                , ["1805", 1.26, 1.28, 2.54, 3.82], ["1806", 1.39, 1.11, 2.51, 3.62]
                                , ["1807", 1.68, 1.56, 3.23, 4.79], ["1808", 0.  , 0.  , 0.  , 0.  ]
                                , ["1809", 1.46, 1.01, 2.47, 3.47], ["1810", 1.45, 0.95, 2.39, 3.34]
                                ]



# HCA Could Affect Segments table fields
HCA_CA_SEGMENTS_TABLE_FIELD_DESCRIPTION = [["CA_SEG_ID_UNIQUE", "LONG", " Unique CA Segment ID", None],
                                ["CA_SEG_ID", "LONG", "CA Segment ID", None],
                                ["CA_DEF_ID", "LONG", "CA Definition ID", None],
                                ["ROUTE_ID", "LONG", "Route ID", None],
                                ["ROUTE_NAME", "TEXT", "Route Name", 50],
                                ["FROM_LONGITUDE", "DOUBLE", "Begin Longitude", None],
                                ["FROM_LATITUDE", "DOUBLE", "Begin Latitude", None],
                                # ["FROM_SERIES", "LONG", "Begin Series", None ],
                                # ["FROM_STATION", "DOUBLE", "Begin Station", None],
                                ["FROM_MEASURE", "DOUBLE", "Begin Measure", None ],
                                ["TO_LONGITUDE", "DOUBLE", "End Longitude", None],
                                ["TO_LATITUDE", "DOUBLE", "End Latitude", None],
                                # ["TO_SERIES", "LONG", "End Series", None],
                                # ["TO_STATION", "DOUBLE", "End Station", None],
                                ["TO_MEASURE", "DOUBLE", "End Measure", None],
                                ["LENGTH", "DOUBLE", "Length", None],
                                ["CALCLENGTH", "DOUBLE", "Calc Length", None],
                                ["BUFF_DIST", "DOUBLE", "Buffer Distance", None],
                                ["HCA_GROUP", "TEXT", "HCA Group", 20],
                                ["HCA_GROUP_DESC", "TEXT", "HCA Group Description", 60],
                                ["INT_METHOD", "TEXT", "Intersection Method", 20],
                                ["INT_METHOD_DESC", "TEXT", "Intersection Method Description", 100]
                                # ["EFFECTIVE_FROM_DATE", "DATE", "EFFECTIVE_FROM_DATE", None],
                                # ["EFFECTIVE_TO_DATE", "DATE", "EFFECTIVE_TO_DATE", 20],
                                # ["CURRENT_INDICATOR_LF", "TEXT", "CURRENT_INDICATOR_LF", 3]
                                ]

# HCA Intersections table fields
HCA_INTERSECTIONS_TABLE_FIELD_DESCRIPTION = [
                                                ['POINT_ID', 'TEXT', 'Point ID', 27],
                                                ['ROUTE_ID', 'Double', 'Route ID', None],
                                                ['HCA_TYPE', 'TEXT', 'HCA Type', 3],
                                                ['INT_TYPE', 'TEXT', 'Intersection Type', 3],
                                                ['G2_HCA_ID', 'TEXT', 'G2 HCA ID', 16],
                                                ['TIME_IN', 'Double', 'Time In', None],
                                                ['VOL_IN', 'Double', 'Volume In', None],
                                                ['TIME_OUT', 'Double', 'Time Out', None],
                                                ['VOL_OUT', 'Double', 'Volume Out', None],
                                                ['INTERSECT_AREA', 'Double', 'Intersect Area', None],
                                                ['BUFF_DIST', 'Double', 'Buffer Distance', None],
                                                # ['PIC_RAD', 'Double', 'PIC Rad', None],
                                                # ['POS_ACC', 'Double', 'Positional Accuracy', None],
                                                # ['ADJ_PIC', 'Double', 'ADJ PIC', None],
                                                # ['DIST_IN', 'Double', 'Distance In', None],
                                                # ['REM_VOL_IN', 'Double', 'Remaining Volume In', None],
                                                ['DIST_IN', 'Double', 'Distance In', None],
                                                ['DIST_OUT', 'Double', 'Distance Out', None],
                                                ['DATEOFRUN', 'DATE', 'Date of Run', None],
                                                # ['INT_WT_VAL', 'Double', 'INT WT VALD', None],
                                                # ['VALID_INDICATOR_LF', 'TEXT', 'Valid Indicator LF', 1],
                                                ['HT_ID', 'TEXT', 'HT ID', 50]
                                            ]

# NHD Intersections table fields
NHD_INTERSECTIONS_TABLE_FIELD_DESCRIPTION = [
                                                ['POINT_ID', 'TEXT', 'Point ID', 27],
                                                ['ROUTE_ID', 'Double', 'Route ID', None],
                                                ['NHD_TYPE', 'TEXT', 'NHD Type', 15],
                                                ['INT_TYPE', 'TEXT', 'Intersection Type', 3],
                                                ['NHD_ID', 'TEXT', 'NHD ID', 40],
                                                ['TIME_IN', 'Double', 'Time In', None],
                                                ['REM_TIME', 'Double', 'Remaining Time', None],
                                                ['REM_VOL', 'Double', 'Remaining Volume', None],
                                                ['BUFF_DIST', 'Double', 'Buffer Distance', None],
                                                ["DRAIN_VOL", "Double", "Draindown Volume", None],
                                                ["DRAIN_RATE", "Double", "Drain Rate", None],
                                                ["HTRES_TIME", "Double", "HT Response Time", None],
                                                ['DIST_IN', 'Double', 'Distance In', None],
                                                ['DATEOFRUN', 'DATE', 'Date of Run', None],
                                                ['NETCDF_DATE', 'DATE', 'NetCDF Timestamp', None]
                                            ]

# Overland Spread Polygons fields
OVERLAND_SPREAD_POLYGONS_FIELD_DESCRIPTION = [
                                                ['POINT_ID', 'TEXT', 'Point ID', 27],
                                                ['ROUTE_ID', 'Double', 'Route ID', None],
                                                [ "MEASURE", "Double", "Measure", None ],
                                                ['POLYGON_TYPE', 'TEXT', 'Polygon Type', 30],
                                                ['MAX_COL_HEIGHT', 'Double', 'Maximum Column Height', None],
                                                ['TIME_IN', 'Double', 'Time In', None],
                                                ["DRAIN_VOL", "Double", "Draindown Volume", None],
                                                ['OVERLAND_SPREAD_VOL', 'Double', 'Overland Spread Volume', None],
                                                ['PRODUCT_LOSS', 'Double', 'Product Loss', None],
                                                ['REM_VOL', 'Double', 'Remaining Volume', None],
                                                ["DRAIN_RATE", "Double", "Drain Rate", None],
                                                ["OFRES_TIME", "Long", "OF Response Time", None],
                                                ["HTRES_TIME", "Double", "HT Response Time", None]
                                            ]

#  WGS 1984 Web Mercator Auxiliary Sphere, WKID: 3857, used in calculating HCA intersections
WEB_MERCATOR_WKID = 3857
HCA_ID_FIELD = "G2_HCA_ID"
FOOT_TO_MILES_CONVERSION = 0.000189394

HT_HCA_IDENTIFIER_FIELD=["HCA_TYPE","G2_HCA_ID","ROUTE_ID","HT_BUFF"]


"""Constants used to calculate pgh"""
AIR_PRESSURE = 101300
GRAVITY = 9.81
NO_OF_DECIMAL_PLACES = 2
MEASURE_UNITS = "FEET"

WHERECLAUSE_NHD_FLOWLINE_EXCLUDE_FTYPES = "(420, 566)"
NHD_AREA_FOR_RADIALSPREED_NHD_INTERSECTIONS = "(307, 312, 336, 343, 364, 398, 403, 431,  445, 455, 460, 484, 537)"
WHERECLAUSE_NHD_WATERBODY_EXCLUDE_FTYPES = "(378)"
NHD_AREA_FOR_RADIALSPREED_ONLY = "(307, 312, 364, 398, 403, 445, 484, 537)"


NHD_WATERBODY_MIN_AREA = 0.0404686  # Area in SqKm to filter out small waterbody/area features
NHD_LAYER_ID_FIELD = "NHDPLUSID"  # field name used to build geometric network
ROUTE_BUFFER_DIST_TO_CLIP_NHD_FEATURES = "2 Kilometers"
SPATIAL_REFERENCE_UNITS = ["METER", "FOOT_US"]

WHERECLAUSE_NHD_FLOWLINE = "{} > {} AND FTYPE NOT IN {}".format("Stream_Vel", 0, WHERECLAUSE_NHD_FLOWLINE_EXCLUDE_FTYPES)
WHERECLAUSE_NHD_AREA = "{} IN {} AND {} > {}".format("FType", NHD_AREA_FOR_RADIALSPREED_NHD_INTERSECTIONS, "AREASQKM", 0.0404686)
WHERECLAUSE_NHD_WATERBODY = "{} > {} AND FTYPE NOT IN {}".format("AREASQKM", 0.0404686, WHERECLAUSE_NHD_WATERBODY_EXCLUDE_FTYPES)

NHD_HUC4_FC_NAME = "NHDHU4Boundary"
NHD_HUC4_BND_FIELD_NAME = "HUC4"
NHD_HUC4_DATA_FIELD_NAME = "VPUID"

CUBIC_METERS_SECOND_TO_BARRELS_HOUR = 22643.3
CUBIC_METERS_TO_BARREL = 6.28981

"""# NHD Data download tool parameters """
NHD_TOOL_LABEL = " NHD Plus High Resolution Data Download"
NHD_TOOL_DESC = " NHD Plus High Resolution data download for selected watershed boundaries"

NHD_SOURCE_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/NHDPlusHR/Beta/GDB/"
NHD_FILE_FORMAT = "NHDPLUS_H_{}_HU4_GDB.zip"
NHD_HUC4_MAPSERVICE="https://edits.nationalmap.gov/arcgis/rest/services/WBD/HUC_Reference/MapServer/2/query"
# NHD_HUC4_MAPSERVICES={'USGS Production map service':'https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/2/query', 'USGS Beta map service':'https://edits.nationalmap.gov/arcgis/rest/services/WBD/HUC_Reference/MapServer/2/query'}
NHD_HUC4_MAPSERVICES={'USGS map service':'https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/2/query'}
SUBREGION_DATA = r"C:\G2\Liquid_HCA\Utah Test Data\NHD\NHDNWISWatersheds.gdb\ArcHydroHUC4SubRegions"
SUBREGION_FIELDS= ['SUBREGION', 'VEL_AVG', 'VEL_STDEV', 'VEL_1STDEV', 'VEL_2STDEV']

NHD_PRECIP_TBLFORMAT = "NHDPlusIncrPrecipMM{}"
NHD_TEMP_TBLFORMAT = "NHDPlusIncrTempMM{}"
NHD_EROMMA_TBL = "NHDPlusEROMMA"
NHD_VAA_TBL = "NHDPlusFlowlineVAA"
NHD_TEMP_FOLDER = "NHD_TEMP"

NHD_REQ_FC = ['NHDFlowline', 'NHDArea', 'NHDWaterbody'] # it should be Flowline, Area, Waterbody order only
NHD_DEFAULT_BUFFER="10 Miles"

NHD_SOURCE_DS = "Hydrography"
NHD_COMM_JOINFIELD = "NHDPlusID"
NHD_JOIN_TABLE = "NHDPlusVelocity"
NHD_JOIN_COLUMNS = "QEMA;AreaSqKm;TotDASqKm;SlopeLenKm;PrecipAvg;PrecipMax;TempAvg;TempMax;VEMA;VelMaxfps;Vel2bStdfps;Vel2aStdfps;CalculatedVel;VelProvenance"

# Create network dataset from template
NHD_NETWORK_TEMPLATE_PATH = "HydroNDTemplate.xml"
NHD_NETWORK_NAMEFROM_TEMPLATE = "NHDFlowline_ND"

NHD_NETWORK_CALICULATED_FIELDS = [["Stream_Vel", "DOUBLE", "!CalculatedVel!"],
                            ["OneWay", "TEXT", "'FT'"],
                            ["TravelTime", "DOUBLE", "!LengthKM! / (!CalculatedVel!*0.0003048*60)"]]
# NHD_NETWORK_CALICULATED_FORMULA="Stream_Vel !CalculatedVel!;OneWay \"\'FT\'\";TravelTime \'!LengthKM! / (!CalculatedVel!*0.0003048*60)\'"
NHD_NETWORK_CALICULATED_FORMULA="Stream_Vel !CalculatedVel!;OneWay Reclass(!FlowDir!);TravelTime '!LengthKM! / (!CalculatedVel!*0.0003048*60)'", r"def Reclass(arg):\n	if arg == 1:\n		return 'FT'\n	elif arg == 'WithDigitized':\n		return 'FT'\n	else:\n		return 'BOTH'"
NHD_NETWORK_CALICULATED_FORMULA_FUN=r"def Reclass(arg):\n	if arg == 1:\n		return 'FT'\n	elif arg == 'WithDigitized':\n		return 'FT'\n	else:\n		return 'BOTH'"

# Areas    Bay/Inlet ,SeaOcean
NHD_AREA_FOR_RADIALSPREED=[ 312, 445]
# Areas    Inundation
# **** NHD_AREA_FOR_RADIALSPREED sub types
# 307 - Area to be Submerged
# 312 - BayInlet
# 336 - CanalDitch
# 343 - DamWeir
# 364 - Foreshore
# 398 - Lock Chamber
# 403 - Inundation Area
# 431 - Rapids
# 445 - SeaOcean
# 455 - Spillway
# 460 - StreamRiver
# 484 - Wash
# 537 - Area of Complex Channels
NHD_AREA_FOR_RADIALSPREED = [343, 431, 455, 460, 484, 537]
NHD_AREA_FOR_2BSTD = [307, 312, 336, 364, 398, 403, 445]
NHD_IS_TEMPFOLDER_REQUIRED=False  # Not used in tool

NHD_CLEAR_TOOL_LABEL = "Clear Intermediate Data"
NHD_CLEAR_TOOL_DESC = "To remove intermediate temporary data created in NHD, Hydro Trace  processing"

NHD_GDB_NAME='NHD_HR.gdb'


#   ------ Hydro trace related config values

HT_TOOL_CATAGORY =  'Hydro Trace'
HT_TOOL_LABEL ='Hydro Trace'
HT_TOOL_DESC = 'Performs hydro Trace'
HT_SUPPORT_DB_TYPES=[".gdb\\", ".sde\\"]
HT_TEMP_FOLDER = "HT_TEMP"
HT_TEMP_GDB = 'TempOutput_SA.gdb'

# Hydro trace related Global Inputs table field names
G_EQ_TYPE = 'EQ_TYPE'
G_EQ_FORM = 'EQ_FORM'
G_FINGAS_1 = 'FINGAS_1'
G_FINGAS_2 = 'FINGAS_2'
G_T_AMB = 'T_AMB'
G_T_DIST = 'T_DIST'
G_WIND_VEL = 'WIND_VEL'
G_DEPTH_H2O = 'DEPTH_H2O'
G_WB_ADHSN = 'WB_ADHSN'
G_SLICK_THK = 'SLICK_THK'
G_SLKTHKSMWB = 'SLKTHKSMWB'
G_API_GRAV = 'API_GRAV'
G_BANK_ANGL = 'BANK_ANGLE'
G_PROD_DNSTY='PROD_DNSTY'

BARRELS_TO_CUBIC_METERS = 0.158987296
HT_APPEND_DATA=False
HT_FINAL_PATHS_NAME="HydrographicTransportPaths"
HT_FINAL_WBPOLY_NAME="WaterbodySpreadPolygons"
HT_OUT_GDBNAME="Output_HT.gdb"
HT_FINAL_HCA_INTERSECTION_TBL_NAME="HCA_INTERSECTIONS"
HT_WB_BUFFER_RADIAL="1 Meters"
HT_AREA_BUFFER_RADIAL="1 Meters"
HT_RADIAL_SMOOTH="100 Meters"
HT_RASTER_GRID_CELL_SIZE=10

HT_NHDINT_INFIELDS= ["POINT_ID", "ROUTE_ID", "NHD_TYPE", "NHD_ID","TIME_IN","REM_TIME", "REM_VOL", "DRAIN_VOL","DRAIN_RATE", "SHAPE@","OID@","HTRES_TIME"]

HT_HCA_LABEL ='Calculate Hydro Trace HCA Intersections'
HT_HCA_DESC = 'Hydro Trace HCA Intersections results will be populated'

HT_HCA_IDENTIFIER_FIELD=["HCA_TYPE","G2_HCA_ID","ROUTE_ID","HT_BUFF"]

# LISENCE_TO_EMAIL = "surendra.pinjala@g2-is.com"
LISENCE_TO_EMAIL = "licensing@g2-is.com"


HT_NHDINT_REQ_FIELDS = ['POINT_ID' ,'ROUTE_ID' ,'NHD_TYPE' ,'NHD_ID' ,'TIME_IN' ,'REM_TIME' ,'REM_VOL' ,'DRAIN_VOL' ,'DRAIN_RATE' ,'HTRES_TIME' ,'DIST_IN']
HT_GLOBAL_REQ_FIELDS = [G_EQ_TYPE, G_EQ_FORM, G_FINGAS_1, G_FINGAS_2, G_T_AMB, G_WIND_VEL, G_DEPTH_H2O, G_WB_ADHSN, G_SLICK_THK, G_SLKTHKSMWB, ROUTE_ID_FIELD,G_API_GRAV,G_BANK_ANGL,G_PROD_DNSTY,FLOWRATE_FIELD,PSDTIME_FIELD,HTRES_TIME_FIELD]
HT_LS_NHDINT_PARAMETER_CATGRY = "Land Spill NHD Intersection Parameters"
HT_GLOBAL_PARAMETER_CATGRY = "Global Input Parameters"
HT_NHD_PARAMETER_CATGRY = "NHD Input Parameters"
HT_HCA_PARAMETER_CATGRY = "HCA Input Parameters"
HT_NGTV_WHERE_CLAUSE = "(POINT_ID IS NOT NULL And ROUTE_ID > 0 ) And (HTREM_TIME<0 or REM_VOL<0)"
HT_NHDINT_TBL_NAME = "NHD_Intersections"
GLOBAL_INPUT_TBL_NAME = "GLOBAL_INPUTS"
HT_HCA_FC_NAME = "HIGH_CONSEQUENCE_AREAS"
NHD_DS_NAME='NWDataset'


GEOCLAW_CASES_ON_AZURE_REACTIVATE_ERRORS = ["ConnectionResetError", "MaxRetryError", "HTTPError"]
GEOCLAW_CASES_ON_AZURE_RESUBMIT_ERRORS = ["AssertionError", "FileNotFoundError"]
GEOCLAW_GEO_DATA_SEA_LEVEL = -4.0
GEOCLAW_DRY_TOLERANCE = 0.0001

HT_SYMBOLLAYER_TRACEPATH="HydrographicTransportPaths.lyrx"
HT_SYMBOLLAYER_SPREAD="WaterbodySpreadPolygons.lyrx"
HT_SYMBOLLAYER_FLOWLINE="NHDFlowline.lyrx"
HT_SYMBOLLAYER_AREAS="NHDArea.lyrx"
HT_SYMBOLLAYER_WATERBODY="NHDWaterbody.lyrx"
HT_SYMBOLLAYER_BOUNDARY="NHDHU4Boundary.lyrx"



