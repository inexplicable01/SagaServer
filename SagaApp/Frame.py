import hashlib
import os
import yaml
# from SagaApp.Container import Container
from SagaApp.FileObjects import FileTrack,FileConnection
from SagaApp.Connection import FileConnection, ConnectionTypes
import json
from config import typeRequired,typeInput,typeOutput
# from PyQt5.QtWidgets import *
# from PyQt5 import uic
# from PyQt5.QtGui import *
# from PyQt5.QtCore import *

fileobjtypes = ['inputObjs', 'requiredObjs', 'outputObjs']



class Frame:
    @classmethod
    def loadFramefromYaml(cls, framefn = None, filestomonitor = None,localfilepath = 'Default'):
        with open(framefn,'r') as file:
            framedict = yaml.load(file, Loader=yaml.FullLoader)
        try:
            commitUTCdatetime = framedict['commitUTCdatetime']
        except:
            commitUTCdatetime = 1587625655.939034

        cframe = cls(parentcontainerid=framedict['parentcontainerid'],
                     FrameName=framedict['FrameName'],
                     FrameInstanceId=framedict['FrameInstanceId'],
                     commitMessage=framedict['commitMessage'],
                     inlinks=framedict['inlinks'],
                     outlinks=framedict['outlinks'],
                     AttachedFiles=framedict['AttachedFiles'],
                     commitUTCdatetime=commitUTCdatetime,
                     localfilepath=localfilepath,
                     filestracklist=framedict['filestrack'],
                     filestomonitor=filestomonitor)
        return cframe


    @classmethod
    def InitiateFrame(cls, parentcontainerid, parentcontainername, localdir):
        newframe = cls(filestracklist=[], FrameName='Rev1', parentcontainerid=parentcontainerid,parentcontainername=parentcontainername, localfilepath=localdir )
        return newframe

    @classmethod
    def LoadFrameFromDict(cls, framedict, localfilepath='default',filestomonitor = None):
        try:
            commitUTCdatetime = framedict['commitUTCdatetime']
        except:
            commitUTCdatetime = 1587625655.939034

        cframe = cls(parentcontainerid= framedict['parentcontainerid'],
                     FrameName=framedict['FrameName'],
                     FrameInstanceId=framedict['FrameInstanceId'],
                     commitMessage=framedict['commitMessage'],
                     inlinks=framedict['inlinks'],
                     outlinks=framedict['outlinks'],
                     AttachedFiles=framedict['AttachedFiles'],
                     commitUTCdatetime=commitUTCdatetime,
                     localfilepath=localfilepath,
                     filestracklist=framedict['filestrack'],
                     filestomonitor=filestomonitor)
        return cframe

    def __init__(self,parentcontainerid=None,parentcontainername=None, FrameName=None, FrameInstanceId=None,commitMessage=None,filestomonitor=None,
                 inlinks=None,outlinks=None,AttachedFiles=None,commitUTCdatetime=None,localfilepath=None,filestracklist=None,
                 ):
        self.parentcontainerid = parentcontainerid
        self.parentcontainername=parentcontainername
        self.FrameName = FrameName
        self.FrameInstanceId = FrameInstanceId
        self.commitMessage = commitMessage
        self.filestomonitor = filestomonitor
        self.inlinks = inlinks
        self.outlinks = outlinks
        self.AttachedFiles = AttachedFiles
        self.commitUTCdatetime = commitUTCdatetime
        self.localfilepath = localfilepath
        self.filestrack = {}
        for ftrack in filestracklist:
            FileHeader = ftrack['FileHeader']
            conn=None
            if 'connection' in ftrack.keys() and ftrack['connection']:
                conn = FileConnection(ftrack['connection']['refContainerId'],
                    connectionType=ftrack['connection']['connectionType'],
                                         branch=ftrack['connection']['branch'],
                                         Rev=ftrack['connection']['Rev'])
            self.filestrack[FileHeader] = FileTrack(FileHeader=ftrack['FileHeader'],
                                                     file_name=ftrack['file_name'],
                                                     localfilepath=localfilepath,
                                                     md5=ftrack['md5'],
                                                     style=ftrack['style'],
                                                     file_id=ftrack['file_id'],
                                                     commitUTCdatetime=ftrack['commitUTCdatetime'],
                                                     lastEdited=ftrack['lastEdited'],
                                                     connection=conn,
                                                     persist=True)

    def add_fileTrack(self, filepath,FileHeader):

        fileb = open(filepath, 'rb')
        md5hash = hashlib.md5(fileb.read())
        md5 = md5hash.hexdigest()
        # print('md5',md5)
        # print(os.path.dirname(filepath))
        self.filestrack[FileHeader]=FileTrack(FileHeader=FileHeader,
                                                localfilepath = os.path.dirname(filepath),
                                                file_name=os.path.basename(filepath),
                                                style = typeRequired,
                                                md5=md5
                                                )

    def addfromOutputtoInputFileTotrack(self, file_name, fileheader, reffiletrack:FileTrack,style,refContainerId,branch,rev):
        # [path, file_name] = os.path.split(fullpath)
        conn = FileConnection(refContainerId,
                              connectionType=ConnectionTypes.Input,
                              branch=branch,
                              Rev=rev)

        newfiletrackobj = FileTrack(file_name=file_name,
                                    FileHeader=fileheader,
                                    style=style,
                                    committedby=reffiletrack.committedby,
                                    md5=reffiletrack.md5,
                                    file_id=reffiletrack.file_id,
                                    commitUTCdatetime=reffiletrack.commitUTCdatetime,
                                    connection=conn,
                                    localfilepath='',
                                    lastEdited=reffiletrack.lastEdited)

        self.filestrack[fileheader] = newfiletrackobj
        # else:
        #     raise(fullpath + ' does not exist')


    def add_inlinks(self, inlinks):
        self.inlinks.append(inlinks)

    def add_outlinks(self, outlinks):
        self.outlinks.append(outlinks)

    def add_AttachedFiles(self, AttachedFiles):
        self.AttachedFiles.append(AttachedFiles)

    def add_misc(self, misc):
        self.misc.append(misc)

    def filestoCheck(self):
        filestocheck = []
        for filetrackobj in self.filestrack:
            filestocheck.append(filetrackobj['file_name'])
        return filestocheck


    def addFileTotrack(self, fullpath, FileHeader, style):
        [path, file_name] = os.path.split(fullpath)
        if os.path.exists(fullpath):
            newfiletrackobj = FileTrack(file_name=file_name,
                                        FileHeader=FileHeader,
                                        localfilepath=self.localfilepath,
                                        style=style,
                                        lastEdited=os.path.getmtime(fullpath))

            self.filestrack[FileHeader] = newfiletrackobj
        else:
            raise(fullpath + ' does not exist')

    def dictify(self):
        dictout = {}
        for key, value in vars(self).items():
            if 'filestrack' == key:
                filestrack = []
                for FileHeader, filetrackobj in value.items():
                    filestrack.append(filetrackobj.dictify())
                dictout[key] = filestrack
            elif 'filestomonitor'==key:
                continue
            else:
                dictout[key] = value
        return dictout

    def writeoutFrameYaml(self, yamlfn):
        with open(yamlfn, 'w') as outyaml:
            yaml.dump(self.dictify(), outyaml)

    def __repr__(self):
        return json.dumps(self.dictify())

    def compareToAnotherFrame(self, frame2):
        changes = []

        for FileHeader in self.filestomonitor.keys():
            if FileHeader not in self.filestrack.keys():
                changes.append({'FileHeader' :FileHeader, 'reason':'missing'})
                continue
            if self.filestrack[FileHeader].md5 != frame2.filestrack[FileHeader].md5:
                changes.append({'FileHeader' :FileHeader, 'reason':'MD5 Changed'})
                print('MD5 Changed')
                continue
            if self.filestrack[FileHeader].lastEdited != frame2.filestrack[FileHeader].lastEdited:
                changes.append({'FileHeader':FileHeader, 'reason':'DateChangeOnly'})
                print('Date changed without Md5 changin')
                continue
        return changes

