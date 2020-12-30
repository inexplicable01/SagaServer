from enum import Enum,auto
import json

class ConnectionTypes(Enum):
    Input=auto()
    Output=auto()

class ConnectionFileObj:
    def __init__(self, ContainerId,connectionType,branch='Main',Rev = None):
        self.refContainerId=ContainerId
        self.connectionType=connectionType
        self.branch=branch
        self.Rev=Rev

    @classmethod
    def create_valid_connection(cls, ContainerId,connectionType:ConnectionTypes,branch='Main',Rev = None):
        if connectionType is None:
            return None
        else:
            return cls(ContainerId,connectionType,branch,Rev)

    def dictify(self):
        dictout = {}
        for key, value in vars(self).items():
            if key=='connectionType':
                dictout[key] = value.name
            else:
                dictout[key] = value
        print(json.dumps(dictout))
        return dictout

    def __repr__(self):
        return 'ConnectionFileObj:  ' + self.refContainerId
    #     print('refContainerId:   ' + self.refContainerId)
    #     # if self.connectionType.name:
    #     #     print('connectionType:   ' + self.connectionType.name)
    #     # print('branch:   ' + self.branch)
    #     # print('Rev:   ' + self.Rev)