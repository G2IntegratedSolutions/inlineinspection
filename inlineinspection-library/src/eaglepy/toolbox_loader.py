IMPORT_LIST = ['from eaglepy.lr.toolbox import Segmentor',
               'from eaglepy.lr.toolbox import Attributer',
               'from eaglepy.lr.toolbox import Statistitater',
               'from eaglepy.lr.toolbox import Dissolverator'
               ]

TOOL_LIST = ['Segmentor',
             'Attributer',
             'Statistitater',
             'Dissolverator'
             ]

## Run all the imports here
for import_text in IMPORT_LIST:
    exec (import_text)


def get_toolbox_classes():
    return [eval(tool) for tool in TOOL_LIST]