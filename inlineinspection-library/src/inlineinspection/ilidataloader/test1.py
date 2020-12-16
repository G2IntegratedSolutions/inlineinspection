# Test by Arun 1
# Test By Alen 1
# Test By Arun 2
# tEST bY Alen 2

# 
 # Input Pipe Features
        in_ili_pipe_features = arcpy.Parameter(displayName="Input Pipe Features",
            name="in_ili_pipe_features",
            datatype="GPFeatureLayer",
            parameterType="optional",
            direction="Input")
        in_ili_pipe_features.filter.list = ["Point"]