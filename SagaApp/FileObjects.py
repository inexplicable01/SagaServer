import hashlib
import os
import json
from datetime import datetime

class FileTrackObj:
    def __init__(self, ContainerObjName, localfilepath, file_name,style=None,lastEdited=None, committedby='waichak', md5=None,file_id=None,commitUTCdatetime=None):
        self.ContainerObjName = ContainerObjName
        self.file_name = file_name
        if  md5 is None:
            fullpath = os.path.join(localfilepath, file_name)
            fileb = open(fullpath , 'rb')
            md5hash = hashlib.md5(fileb.read())
            md5=md5hash.hexdigest()
        self.lastEdited= lastEdited#
        self.committedby = committedby  #
        self.md5 = md5
        self.style = style
        self.file_id = file_id
        self.commitUTCdatetime = commitUTCdatetime

    def yamlify(self):
        dictout = {}
        for key, value in vars(self).items():
            dictout[key] = value
        return dictout

    def printdetails(self):
        print(self.md5)

    def __repr__(self):
        dictout = {}
        print('ContainerObjName:   '+ self.ContainerObjName)
        print('file_name:   ' + self.file_name)
        print('md5:   ' + self.md5)
        if self.lastEdited:
            print('lastEdited:   ' + datetime.fromtimestamp(self.commitUTCdatetime).isoformat())
        print('committedby:   ' + self.committedby)
        print('style:   ' + self.style)
        print('file_id:   ' + self.file_id)
        if self.commitUTCdatetime:
            print('commitUTCdatetime:   ' + datetime.fromtimestamp(self.commitUTCdatetime).isoformat())

        for key, value in vars(self).items():
            dictout[key] = value
        # return json.dumps(dictout)


class InputFileObj(FileTrackObj):
    def __init__(self, ContainerObjName, file_name,localFilePath,style,fromContainerId,md5=None,file_id=None,commitUTCdatetime=None):
        super().__init__(self, ContainerObjName, file_name,localFilePath,style,md5,file_id,commitUTCdatetime)
        self.fromContainerId=fromContainerId

class OutFileObj(FileTrackObj):
    def __init__(self, ContainerObjName, file_name,localFilePath,style,toContainerID,md5=None,file_id=None,commitUTCdatetime=None):
        super().__init__(self, ContainerObjName, file_name,localFilePath,style,md5,file_id,commitUTCdatetime)
        self.toContainerID=toContainerID