from SagaApp.Frame import Frame
from SagaApp.Connection import ConnectionTypes, ConnectionFileObj
from pymongo import MongoClient
from bson.objectid import ObjectId
import gridfs
import copy
import hashlib
import os
import yaml
import glob
import time
import requests
import json
import re
from config import basedir
from SagaApp.SagaUtil import latestFrameInBranch, FrameNumInBranch

from datetime import datetime

Rev = 'Rev'
blankcontainer = {'containerName':"" ,'containerId':"",'FileHeaders': {} ,'allowedUser':[] }

class Container:
    def __init__(self, containerfn='Default',currentbranch='Main',revnum=None, containerdict=None):
        if containerdict is None and containerfn == 'Default':
            containeryaml = blankcontainer
            self.containerworkingfolder = os.path.join(basedir, 'Container')
        else:
            if containerdict:
                containeryaml = containerdict
                self.containerworkingfolder = os.path.join(os.getcwd(),'Container',containeryaml['containerId'])
            else:
                self.containerworkingfolder = os.path.dirname(containerfn)
                with open(containerfn) as file:
                    containeryaml = yaml.load(file, Loader=yaml.FullLoader)
        self.containerfn = containerfn
        self.containerName = containeryaml['containerName']
        self.containerId = containeryaml['containerId']
        self.FileHeaders = containeryaml['FileHeaders']
        self.allowUsers = containeryaml['allowedUser']
        # self.yamlTracking = containeryaml['yamlTracking']
        self.currentbranch = currentbranch
        self.filestomonitor = {}
        for FileHeader, file in self.FileHeaders.items():
            self.filestomonitor[FileHeader]= file['type']
        self.refframe , self.revnum = FrameNumInBranch(\
            os.path.join(basedir, 'Container', self.containerId, currentbranch),\
            revnum)

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
        dictout = {}
        if environ=='FrontEnd':
            outyaml = open(os.path.join(self.containerworkingfolder, self.containerfn), 'w')
        elif environ=='Server':
            outyaml = open(outyamlfn, 'w')
        keytosave = ['containerName', 'containerId',  'FileHeaders', 'allowedUser']
        for key, value in vars(self).items():
            if key in keytosave:
                dictout[key] = value
        yaml.dump(dictout, outyaml)
        outyaml.close()

    def returnType(self, FileHeader):
        if FileHeader in self.FileHeaders.keys():
            return self.FileHeaders[FileHeader]['type']
        else:
            print(FileHeader + 'not in this frame')
            return None

    def __repr__(self):
        dictout = {}
        keytosave = ['containerName', 'containerId', 'FileHeaders', 'allowedUser']
        for key, value in vars(self).items():
            if key in keytosave:
                dictout[key] = value
        return json.dumps(dictout)
