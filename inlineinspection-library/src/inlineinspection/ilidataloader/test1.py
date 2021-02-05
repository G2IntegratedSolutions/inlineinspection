
in_ili_pipe_features = arcpy.Parameter(displayName="Input Pipe Features",
    name="in_ili_pipe_features",
    datatype="GPFeatureLayer",
    parameterType="optional",
    direction="Input")
in_ili_pipe_features.filter.list = ["Point"]
