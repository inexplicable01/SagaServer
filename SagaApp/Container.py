from SagaApp.Frame import Frame

import copy
import hashlib
import os
import yaml
import glob
import time
import requests
import json
import re
from config import basedir , typeInput, typeOutput, typeRequired
from SagaApp.SagaUtil import latestFrameInBranch, FrameNumInBranch
from flask import current_app

from datetime import datetime

CONTAINERFOLDER = 'Container'  #This shouldn't be in here...too tired to remove.
# current_app['CONTAINERFOLDER']

Rev = 'Rev'
blankcontainer = {'containerName':"" ,'containerId':"",'FileHeaders': {} ,'allowedUser':[]}

class Container:
    # def __init__(self, containerfn='Default',currentbranch='Main',revnum=None, containerdict=None):
    #     if containerdict is None and containerfn == 'Default':
    #         containeryaml = blankcontainer
    #         self.containerworkingfolder = os.path.join(basedir, 'Container')
    #     else:
    #         if containerdict:
    #             containeryaml = containerdict
    #             self.containerworkingfolder = os.path.join(os.getcwd(),'Container',containeryaml['containerId'])
    #         else:
    #             self.containerworkingfolder = os.path.dirname(containerfn)
    #             with open(containerfn) as file:
    #                 containeryaml = yaml.load(file, Loader=yaml.FullLoader)
    #     # self.containerfn = containerfn
    #     self.containerName = containeryaml['containerName']
    #     self.containerId = containeryaml['containerId']
    #     self.FileHeaders = containeryaml['FileHeaders']
    #     self.allowedUser = containeryaml['allowedUser']
    #     # self.yamlTracking = containeryaml['yamlTracking']
    #     self.currentbranch = currentbranch
    #     self.filestomonitor = {}
    #     for FileHeader, file in self.FileHeaders.items():
    #         self.filestomonitor[FileHeader]= file['type']
    #     self.refframe , self.revnum = FrameNumInBranch(\
    #         os.path.join(basedir, 'Container', self.containerId, currentbranch),\
    #         revnum)
    #     try:
    #         self.workingFrame = Frame(self.refframe, self.filestomonitor, self.containerworkingfolder)
    #     except Exception as e:
    #         self.workingFrame = Frame()

    def __init__(self, containerworkingfolder,containerName,containerId,
                 FileHeaders,allowedUser,currentbranch,filestomonitor,revnum,refframe,
                 workingFrame: Frame):
        self.containerworkingfolder = containerworkingfolder
        self.containerName = containerName
        self.containerId = containerId
        self.FileHeaders = FileHeaders
        self.allowedUser = allowedUser
        self.currentbranch = currentbranch
        self.filestomonitor =filestomonitor
        self.revnum =revnum
        self.refframe =refframe
        self.workingFrame= workingFrame

    @classmethod
    def LoadContainerFromDict(cls, containerdict, currentbranch='Main',revnum='1'):
        # containeryaml = containerdict
        containerworkingfolder = os.path.join(os.getcwd(), CONTAINERFOLDER, containerdict['containerId'])
        FileHeaders = containerdict['FileHeaders']
        filestomonitor = {}
        for FileHeader, file in FileHeaders.items():
            filestomonitor[FileHeader]= file['type']
        refframe, revnum = FrameNumInBranch(os.path.join(containerworkingfolder, currentbranch), revnum)
        try:
            workingFrame = Frame(refframe, filestomonitor, containerworkingfolder)
        except Exception as e:
            workingFrame = Frame()
        container = cls(containerworkingfolder=containerworkingfolder,
                           containerName=containerdict['containerName'],
                           containerId=containerdict['containerId'],
                           FileHeaders=FileHeaders,
                           allowedUser=containerdict['allowedUser'],
                           currentbranch=currentbranch,filestomonitor=filestomonitor, revnum=revnum,
                           refframe=refframe, workingFrame=workingFrame)
        return container

    @classmethod
    def InitiateContainer(cls):
        newcontainer = cls(containerworkingfolder=basedir,
                           containerName="",
                           containerId="",
                           FileHeaders={},
                           allowedUser=[],
                           currentbranch="Main",filestomonitor={},revnum='1',
                           refframe='dont have one yet', workingFrame = Frame())
        return newcontainer

    @classmethod
    def LoadContainerFromYaml(cls, containerfn, currentbranch='Main',revnum='1'):
        containerworkingfolder = os.path.dirname(containerfn)
        with open(containerfn) as file:
            containeryaml = yaml.load(file, Loader=yaml.FullLoader)
        FileHeaders={}
        for fileheader, fileinfo in containeryaml['FileHeaders'].items():
            if fileinfo['type'] == typeOutput:
                if type(fileinfo['Container']) != list:
                    fileinfo['Container']=[fileinfo['Container']]
            FileHeaders[fileheader] = fileinfo
        filestomonitor = {}
        for FileHeader, file in FileHeaders.items():
            filestomonitor[FileHeader]= file['type']

        try:
            refframe, revnum = FrameNumInBranch(os.path.join(containerworkingfolder, currentbranch), revnum)
            workingFrame = Frame(refframe, filestomonitor, containerworkingfolder)
        except Exception as e:
            refframe = 'Dont have one yet'
            revnum='1'
            workingFrame = Frame()
        container = cls(containerworkingfolder=containerworkingfolder,
                           containerName=containeryaml['containerName'],
                           containerId=containeryaml['containerId'],
                           FileHeaders=FileHeaders,
                           allowedUser=containeryaml['allowedUser'],
                           currentbranch=currentbranch,filestomonitor=filestomonitor, revnum=revnum,
                           refframe=refframe, workingFrame=workingFrame)
        return container

    def commit(self, cframe: Frame, commitmsg, BASE):
        committed = False
        # # frameYamlfileb = framefs.get(file_id=ObjectId(curframe.FrameInstanceId))
        with open(self.refframe) as file:
            frameRefYaml = yaml.load(file, Loader=yaml.FullLoader)
        frameRef = Frame(frameRefYaml, self.filestomonitor, self.containerworkingfolder)
        # allowCommit, changes = self.Container.checkFrame(cframe)
        # print(frameRef.FrameName)

        filesToUpload = {}
        updateinfo = {}
        for FileHeader, filetrackobj in cframe.filestrack.items():
            filepath = os.path.join(self.containerworkingfolder, filetrackobj.file_name)
            # Should file be committed?
            commit_file, md5 = self.CheckCommit(filetrackobj, filepath, frameRef)
            committime = datetime.timestamp(datetime.utcnow())
            if commit_file:
                # new file needs to be committed as the new local file is not the same as previous md5
                filesToUpload[FileHeader] = open(filepath,'rb')
                updateinfo[FileHeader] = {
                    'file_name': filetrackobj.file_name,
                    'lastEdited': filetrackobj.lastEdited,
                    'md5': filetrackobj.md5,
                    'style': filetrackobj.style,
                }

        updateinfojson = json.dumps(updateinfo)

        response = requests.post(BASE + 'FRAMES',
                                 data={'containerID': self.containerId, 'branch': self.currentbranch,
                                       'updateinfo': updateinfojson, 'commitmsg':commitmsg},  files=filesToUpload)
        # print(response)
        if response.headers['commitsuccess']:
            # Updating new frame information
            frameyamlfn = os.path.join(self.containerId, self.currentbranch, response.headers['file_name'])
            open(frameyamlfn, 'wb').write(response.content)
            with open(frameyamlfn) as file:
                frameyaml = yaml.load(file, Loader=yaml.FullLoader)
            newframe = Frame(frameyaml, self.filestomonitor,self.containerworkingfolder)
            # Write out new frame information
            # The frame file is saved to the frame FS
            self.refframe = frameyamlfn
            return newframe, response.headers['commitsuccess']
        else:
            return cframe, response.headers['commitsuccess']


    def CheckCommit(self, filetrackobj, filepath, frameRef):
        fileb = open(filepath, 'rb')
        md5hash = hashlib.md5(fileb.read())
        md5 = md5hash.hexdigest()
        if filetrackobj.FileHeader not in frameRef.filestrack.keys():
            return True, md5
        if (md5 != frameRef.filestrack[filetrackobj.FileHeader].md5):
            return True, md5
        if frameRef.filestrack[filetrackobj.FileHeader].lastEdited != os.path.getmtime(
                os.path.join(self.containerworkingfolder, filetrackobj.file_name)):
            frameRef.filestrack[filetrackobj.FileHeader].lastEdited = os.path.getmtime(
                os.path.join(self.containerworkingfolder, filetrackobj.file_name))
            return True, md5
        return False, md5
        # Make new Yaml file  some meta data sohould exit in Yaml file

    def checkFrame(self, cframe):
        allowCommit = False
        cframe.updateFrame()
        with open(self.refframe) as file:
            fyaml = yaml.load(file, Loader=yaml.FullLoader)
        ref = Frame(fyaml, self.filestomonitor,self.containerworkingfolder)
        print('ref', ref.FrameName)
        changes = cframe.compareToAnotherFrame(ref)
        # print(len(changes))
        if len(changes) > 0:
            allowCommit = True
        return allowCommit, changes

    def commithistory(self):
        historyStr = ''
        # glob.glob() +'/'+ Rev + revnum + ".yaml"
        yamllist = glob.glob(self.containerworkingfolder + '/' + self.currentbranch + '*.yaml')
        for yamlfn in yamllist:
            # print(yamlfn)
            with open(yamlfn) as file:
                pastYaml = yaml.load(file, Loader=yaml.FullLoader)
            # print(pastYaml)
            pastframe = Frame(pastYaml, self.filestomonitor,self.containerworkingfolder)
            # print(pastframe.commitMessage)
            historyStr = historyStr + pastframe.FrameName + '\t' + pastframe.commitMessage + '\t\t\t\t' + \
                         time.ctime(pastframe.commitUTCdatetime) + '\t\n'
        return historyStr

    def save(self, environ='FrontEnd', outyamlfn = ''):
        if environ=='FrontEnd':
            outyaml = open(os.path.join(self.containerworkingfolder, self.containerfn), 'w')
        elif environ=='Server':
            outyaml = open(outyamlfn, 'w')

        yaml.dump(self.dictify(), outyaml)
        outyaml.close()

    def returnType(self, FileHeader):
        if FileHeader in self.FileHeaders.keys():
            return self.FileHeaders[FileHeader]['type']
        else:
            print(FileHeader + 'not in this frame')
            return None

    def addFileObject(self, fileheader, fileInfo, fileType:str):
        if fileType ==typeInput:
            self.FileHeaders[fileheader] = fileInfo
        elif fileType == typeRequired:
            self.FileHeaders[fileheader] = fileInfo
        elif fileType == typeOutput:
            self.FileHeaders[fileheader] = fileInfo

    def __repr__(self):
        return json.dumps(self.dictify())

    def dictify(self):
        dictout = {}
        keytosave = ['containerName', 'containerId', 'FileHeaders', 'allowedUser']
        for key, value in vars(self).items():
            if key in keytosave:
                dictout[key] = value
        return dictout

    @staticmethod
    def compare(cont1,cont2):
        return recursivecompare(cont1.dictify(), cont2.dictify())

def recursivecompare(dict1, dict2):
    diff = {}
    identical = True
    for key, value in dict1.items():
        if type(value) is not dict:
            if dict2[key] != value:
                identical = False
                diff[key] = [value, dict2[key]]
        else:
            id, difference = recursivecompare(value, dict2[key])
            identical = identical if id else id
            diff[key] = difference
    return identical, diff

