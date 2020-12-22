import os
import glob
from flask import safe_join
from SagaApp.Container import Container
import yaml
import datetime
import warnings

# print(os.path.dirname(__file__))
# print(os.getcwd())
# rootpath = os.path.dirname(os.getcwd())
# # os.chdir(path_parent)
# print(rootpath)

containeryamlkeys = ['containerId', 'containerName', 'inputObjs', \
                     'outputObjs', 'references', 'requiredObjs', 'allowedUser']
frameyamlstr = {
    'AttachedFiles': {
        'commitUTCdatetime': {'type': 'UTCdatetime'},
        'dateformat': {'type': 'str'},
        'db_id': {'type': 'str'},
        'file_name': {'type': 'str'},
        'type': 'listdict'
    },
    'FrameInstanceId': {'type': 'str'},
    'FrameName': {'type': 'str'},
    'commitMessage': {'type': 'str'},
    'commitUTCdatetime': {'type': 'UTCdatetime'},
    'filestrack': {
        'type': 'listdict',
        'ContainerObjName': {'type': 'str'},
        'commitUTCdatetime': {'type': 'UTCdatetime'},
        'file_id': {'type': 'str'},
        'file_name': {'type': 'str'},
        'lastEdited': {'type': 'UTCdatetime'},
        'committedby':{'type': 'str'},
        'md5': {'type': 'str'},
        'style': {'type': 'str'},
    },
    'inlinks':
        {'type': 'listdict',
         'fromFrame': {'type': 'str'},
         'infile': {'type': 'str'},
         },
    'outlinks':
        {'type': 'listdict',
         'toFrame': {'type': 'str'},
         'outfile': {'type': 'str'},
         },
    'localfilepath': {'type': 'str'},
    'parentContainerId': {'type': 'str'}

}

def checkvariable(fn, key,value, framekey):
    if value:
        if framekey['type'] == 'listdict':
            if isinstance(value, list):
                for elem in value:
                    ## assume dictionary
                    for subkey, subvalue in elem.items():
                        checkvariable(fn,subkey, subvalue, framekey[subkey])
                # print(key + '  is listdict')
            else:
                warnings.warn(key + ' should be of type list but has value of ' + type(value).__name__ + ' for file ' + fn)
        elif framekey['type'] == 'str':
            if not isinstance(value, str):
                warnings.warn(key + ' should be of type str but has value of ' + type(value).__name__ + ' for file ' + fn)
        elif framekey['type'] == 'UTCdatetime':
            try:
                timestamp = datetime.datetime.fromtimestamp(value).isoformat()
            except:
                warnings.warn(key + ' should be of type UTCdatetime but has value of ' + type(value).__name__+ ' for file ' + fn)

for folder in os.listdir('Container'):
    # print (folder)
    ########## Container Check

    containerfn = safe_join('Container', folder, 'containerstate.yaml')
    if not os.path.isfile(containerfn):
        raise Exception(containerfn + ' doesn''t exist')
    with open(containerfn) as file:
        containeryaml = yaml.load(file, Loader=yaml.FullLoader)
    # print(containeryaml)
    for key, items in containeryaml.items():
        if key not in containeryamlkeys:
            raise Exception('Found a key in ' + folder + ' that should be.  Key: ' + key + '.')

     ######Frame Check
    framedir = safe_join('Container', folder, 'Main')
    for itemfn in os.listdir(framedir):
        framefn = safe_join('Container', folder, 'Main', itemfn)
        with open(framefn) as file:
            frameyaml = yaml.load(file, Loader=yaml.FullLoader)
        # print(frameyaml.keys())
        for key, value in frameyaml.items():
            if key not in frameyamlstr.keys():
                raise Exception('Found a key in ' + folder + ' that should be.  Key: ' + key + '.')
            # print(key + '   '  +frameyamlstr[key]['type'])
            checkvariable(framefn, key,value, frameyamlstr[key])



