import hashlib
import os
from datetime import datetime
from SagaCore.Connection import FileConnection
from Config import NEEDSDOCTOR, typeRequired

class FileTrack:
    def __init__(self, FileHeader, md5, \
                 file_name, style,connection:FileConnection,
                 lastEdited, committedby='default@gmail.com',   commitUTCdatetime=None,
                 persist: bool = True, ctnrootpathlist = [], lastupdated=NEEDSDOCTOR
                 ):
        self.FileHeader = FileHeader
        self.file_name = file_name
        # self.localfilepath = localfilepath
        self.lastEdited= lastEdited
        self.committedby = committedby
        self.lastupdated = lastupdated
        self.md5 = md5
        self.style = style
        # self.file_id = file_id
        self.commitUTCdatetime = commitUTCdatetime
        if connection is None:
            connection = FileConnection(
                None, typeRequired, branch='Main', Rev = None
            )
        self.lastupdated = lastupdated
        self.connection=connection
        self.persist=persist
        if len(ctnrootpathlist)>0:
            self.ctnrootpath=os.path.join(*ctnrootpathlist)
        else:
            self.ctnrootpath='.'

    def dictify(self):
        ###Should__dict__be used instead?
        dictout = {}
        for key, value in vars(self).items():
            if key=='connection':
                if value:
                    dictout[key] = value.dictify()
                else:
                    dictout[key] = None
            elif key=='ctnrootpath':
                ctnrootpathlist=[]
                if value=='.':
                    dictout[key] = []
                else:
                    for folder in value.split(os.path.sep):
                        ctnrootpathlist.append(folder)
                    dictout['ctnrootpathlist'] = ctnrootpathlist
            else:
                dictout[key] = value
        return dictout

    def printdetails(self):
        print(self.md5)

    def __repr__(self):
        str=''
        # print('FileHeader:   '+ self.FileHeader)
        str +='\nFileHeader:   '+ self.FileHeader + '\n'
        str += 'file_name:   ' + self.file_name + '\n'
        str += 'md5:   ' + self.md5 + '\n'
        if self.lastEdited:
            str += 'lastEdited:   ' + datetime.fromtimestamp(self.lastEdited).isoformat()+ '\n'
        str += 'committedby:   ' + self.committedby+ '\n'
        if self.style:
            str += 'style:   ' + self.style+ '\n'
        # if self.file_id:
        #     str += 'file_id:   ' + self.file_id+ '\n'
        if self.commitUTCdatetime:
            str += 'commitUTCdatetime:   ' + datetime.fromtimestamp(self.commitUTCdatetime).isoformat()+ '\n'
        str += 'connection:     ' + self.connection.__repr__() + '\n'
        str += f'persist: {self.persist}\n'
        return str
