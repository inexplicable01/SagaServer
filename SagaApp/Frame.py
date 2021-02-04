import hashlib
import os
import yaml
# from SagaApp.Container import Container
from SagaApp.FileObjects import FileTrack,FileConnection
from SagaApp.Connection import FileConnection, ConnectionTypes
import json
# from PyQt5.QtWidgets import *
# from PyQt5 import uic
# from PyQt5.QtGui import *
# from PyQt5.QtCore import *

fileobjtypes = ['inputObjs', 'requiredObjs', 'outputObjs']

blankFrame = {'parentContainerId':"",'FrameName': "", 'FrameInstanceId': "",'commitMessage': "",'inlinks': "",'outlinks': "",'AttachedFiles': "", 'commitUTCdatetime': "",'filestrack': ""}


class Frame:
    def __init__(self, framefn = None, filestomonitor = None,localfilepath = 'Default', framedict=None):

        if framefn == None:
            if framedict:
                FrameYaml = framedict
            else:
                FrameYaml = blankFrame
                localfilepath = localfilepath #generalize this file path
        else:
            with open(framefn,'r') as file:
                FrameYaml = yaml.load(file, Loader=yaml.FullLoader)
        # self.containerworkingfolder = os.path.dirname(containerfn)
        self.parentContainerId = FrameYaml['parentContainerId']
        self.FrameName = FrameYaml['FrameName']
        self.FrameInstanceId = FrameYaml['FrameInstanceId']
        self.commitMessage = FrameYaml['commitMessage']
        self.filestomonitor = filestomonitor

        self.inlinks = FrameYaml['inlinks']
        self.outlinks = FrameYaml['outlinks']
        self.AttachedFiles = FrameYaml['AttachedFiles']
        try:
            self.commitUTCdatetime = FrameYaml['commitUTCdatetime']
        except:
            self.commitUTCdatetime = 1587625655.939034
        # self.inoutcheck()
        self.localfilepath=localfilepath
        self.filestrack = {}
        for ftrack in FrameYaml['filestrack']:

            FileHeader = ftrack['FileHeader']
            # cont= Container(os.path.join('Container/',self.parentContainerId, 'containerstate.yaml'))
            conn=None
            if 'connection' in ftrack.keys() and ftrack['connection']:
                conn = FileConnection(ftrack['connection']['refContainerId'],
                    connectionType=ftrack['connection']['connectionType'],
                                         branch=ftrack['connection']['branch'],
                                         Rev=ftrack['connection']['Rev'])

            self.filestrack[FileHeader] = FileTrack(FileHeader=ftrack['FileHeader'],
                                                     file_name=ftrack['file_name'],
                                                     localfilepath=self.localfilepath,
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
        fileobj = FileTrack(FileHeader=FileHeader,
                            file_name=os.path.basename(filepath),
                            )
        # print('fileobj', fileobj)
        self.filestrack[FileHeader]=fileobj

    def addfromOutputtoInputFileTotrack(self, file_name, fileheader, reffiletrack:FileTrack,style,refContainerId,branch,rev):
        # [path, file_name] = os.path.split(fullpath)
        conn = FileConnection(refContainerId,
                              connectionType=ConnectionTypes.Input,
                              branch=branch,
                              Rev=rev)

        # if os.path.exists(fullpath):
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
            elif 'filestomonitor' ==key:
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

    def updateFrame(self):
        for FileHeader in self.filestomonitor.keys():
            ##  Is FileHeader in Frame, , if yes
            ##
            if FileHeader not in self.filestrack.keys():
                # if no, go find file
                print(self.filestrack.keys(),FileHeader)
                path = QFileDialog.getOpenFileName(self, "Open")[0]
                if path:
                    self.cframe.add_fileTrack(path, FileHeader, 'Style')
                    continue
            ## Does the file exist?
            # print('self.localfilepath', self.localfilepath)
            path = self.localfilepath + '/' + self.filestrack[FileHeader].file_name
            if not os.path.exists(path):
                # if not, go find a new file to track
                path = QFileDialog.getOpenFileName(self, "Open")[0]
                if path:
                    self.cframe.add_fileTrack(path, FileHeader, 'Style')
                    # reassign key contrainobj with new fileobj
                    continue
            fileb = open(path, 'rb')
            md5hash = hashlib.md5(fileb.read())
            md5 = md5hash.hexdigest()
            # calculate md5 of file, if md5 has changed, update md5
            if md5 != self.filestrack[FileHeader].md5:
                self.filestrack[FileHeader].md5 = md5
                self.filestrack[FileHeader].lastEdited = os.path.getmtime(path)
            # if file has been updated, update last edited
            if os.path.getmtime(path) != self.filestrack[FileHeader].lastEdited:
                self.filestrack[FileHeader].lastEdited = os.path.getmtime(path)
