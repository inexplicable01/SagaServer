import hashlib
import os
import json
from datetime import datetime
from SagaApp.Connection import ConnectionFileObj

class FileTrack:
    def __init__(self, FileHeader, localfilepath, \
                 file_name, connection:ConnectionFileObj=None, style=None, lastEdited=None, committedby='waichak', \
                 md5=None, file_id=None, commitUTCdatetime=None,
                 ):
        self.FileHeader = FileHeader
        self.file_name = file_name
        if md5 is None:
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
        self.connection=connection

    def dictify(self):
        ###Should__dict__be used instead?
        dictout = {}
        for key, value in vars(self).items():
            if key=='connection':
                if value:
                    dictout[key] = value.dictify()
                else:
                    dictout[key] = None
            else:
                dictout[key] = value
        return dictout

    def printdetails(self):
        print(self.md5)

    def __repr__(self):
        dictout = {}
        print('FileHeader:   '+ self.FileHeader)
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
