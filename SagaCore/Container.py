from SagaCore.Frame import Frame

import hashlib
import os
import yaml
import glob
import time
import requests
import json
from Config import typeInput, typeOutput, typeRequired, NEEDSDOCTOR, appdatadir
from SagaCore.SagaUtil import getFramebyRevnum
import uuid
import io
import warnings

from datetime import datetime

CONTAINERFOLDER = 'Container'  #This shouldn't be in here...too tired to remove.
# current_app['CONTAINERFOLDER']

Rev = 'Rev'
blankcontainer = {'containerName':"" ,'containerId':"",'FileHeaders': {} ,'allowedUser':[]}

class Container:
    def __init__(self, containerworkingfolder,containerName,containerId,
                 FileHeaders,allowedUser,currentbranch,revnum,refframefilepath,description,parentid,
                 workingFrame: Frame):
        self.containerworkingfolder = containerworkingfolder
        self.containerName = containerName
        self.containerId = containerId
        self.FileHeaders = FileHeaders
        self.allowedUser = allowedUser
        self.currentbranch = currentbranch
        # self.filestomonitor =filestomonitor
        self.revnum =revnum
        self.refframefilepath =refframefilepath
        try: ### ATTENTION
            self.refframe = Frame.loadFramefromYaml(refframefilepath, self.containerworkingfolder)
        except:
            self.refframe = None
        self.workingFrame= workingFrame
        self.description = description
        self.parentid=parentid

    @classmethod
    def LoadContainerFromDict(cls, containerdict, sectionid, currentbranch='Main',revnum='', environ='FrontEnd'):
        # containeryaml = containerdict

        if environ=='FrontEnd':
            containerworkingfolder = os.path.join(os.getcwd(), CONTAINERFOLDER, containerdict['containerId'])
        elif environ=='Server':
            containerworkingfolder = os.path.join(os.getcwd(), 'mysite', CONTAINERFOLDER, sectionid, containerdict['containerId'])

        ##This is problematic as this only works for Client side.    working folder is meant for client side only and can only serve as confusion for the server side
        ## How to make sure Container class can be identical on client side and server side.
        ## Need to think of a way to further remove seperation of concern.
        ## Loading containers on Client side is fundamentally different than loading them on the server side.

        FileHeaders = containerdict['FileHeaders']
        refframefilepath, revnum = getFramebyRevnum(os.path.join(containerworkingfolder, currentbranch), revnum)
        try:
            workingFrame = Frame.loadFramefromYaml(refframefilepath,containerworkingfolder)
        except Exception as e:
            workingFrame = Frame.InitiateFrame(parentcontainerid=containerdict['containerId'],
                                               parentcontainername=containerdict['containerName'])
        if 'description' not in containerdict.keys():
            containerdict['description'] = 'Need Description'
        if 'parentid' not in containerdict.keys():
            containerdict['parentid'] = sectionid
        container = cls(containerworkingfolder=containerworkingfolder,
                           containerName=containerdict['containerName'],
                           containerId=containerdict['containerId'],
                           FileHeaders=FileHeaders,
                           allowedUser=containerdict['allowedUser'],
                            parentid=containerdict['parentid'],
                           currentbranch=currentbranch, revnum=revnum,
                           refframefilepath=refframefilepath, workingFrame=workingFrame, description=containerdict['description'])
        container.FixConnections()
        return container

    # @classmethod
    # def InitiateContainer(cls, containerName, localdir):
    #     containerid = uuid.uuid4().__str__()
    #     newcontainer = cls(containerworkingfolder=localdir,
    #                        containerName=containerName,
    #                        containerId=containerid,
    #                        FileHeaders={},
    #                        allowedUser=[],
    #                        currentbranch="Main",revnum='1',
    #                        refframefilepath='dont have one yet',
    #                        workingFrame = Frame.InitiateFrame(parentcontainerid=containerid, parentcontainername=containerName, localdir=localdir),
    #                        description='')
    #     return newcontainer

    @classmethod
    def LoadContainerFromYaml(cls, containerfn,sectionid,  currentbranch='Main',revnum='', ):
        needtosave=False
        containerworkingfolder = os.path.dirname(containerfn)
        with open(containerfn) as file:
            containeryaml = yaml.load(file, Loader=yaml.FullLoader)
        FileHeaders={}
        for fileheader, fileinfo in containeryaml['FileHeaders'].items():
            if fileinfo['type'] == typeOutput:
                if type(fileinfo['Container']) != list:
                    fileinfo['Container']=[fileinfo['Container']]
            FileHeaders[fileheader] = fileinfo
        try:
            refframefilepath, revnum = getFramebyRevnum(os.path.join(containerworkingfolder, currentbranch), revnum)
            workingFrame = Frame.loadFramefromYaml(refframefilepath, containerworkingfolder)
        except Exception as e:
            refframefilepath = 'Dont have one yet'
            revnum='1'
            workingFrame = Frame.InitiateFrame()
        if 'description' not in containeryaml.keys():
            containeryaml['description'] = 'Need Description'
        if 'parentid' not in containeryaml.keys():
            containeryaml['parentid'] = sectionid
            needtosave=True
        container = cls(containerworkingfolder=containerworkingfolder,
                           containerName=containeryaml['containerName'],
                           containerId=containeryaml['containerId'],
                           FileHeaders=FileHeaders,
                           allowedUser=containeryaml['allowedUser'],
                            parentid=containeryaml['parentid'],
                           currentbranch=currentbranch, revnum=revnum,
                           refframefilepath=refframefilepath, workingFrame=workingFrame,
                        description=containeryaml['description'])
        if needtosave:
            container.save()
        # container.FixConnections()
        return container

    def CommitNewContainer(self, commitmessage,authtoken,BASE, client=None):

        # self.tempFrame.description = self.descriptionText.toPlainText()
        self.workingFrame.commitMessage = commitmessage

        url = BASE + 'CONTAINERS/newContainer'
        payload = {'containerdictjson': json.dumps(self.dictify()), 'framedictjson': json.dumps(self.workingFrame.dictify())}

        headers = {
            'Authorization': 'Bearer ' + authtoken['auth_token']
        }
        if client== None:
            filesToUpload = {}
            for fileheader, filetrack in self.workingFrame.filestrack.items():
                if filetrack.style in [typeOutput, typeRequired]:
                    filepath = os.path.join(self.containerworkingfolder, filetrack.file_name)
                    filesToUpload[fileheader] = open(filepath, 'rb')
                    fileb = open(filepath, 'rb')
                    filetrack.md5 = hashlib.md5(fileb.read()).hexdigest()
            response = requests.request("POST", url, headers=headers, data=payload, files=filesToUpload)
        else:
            # print('got to here')
            data = {key: str(value) for key, value in payload.items()}
            for fileheader, filetrack in self.workingFrame.filestrack.items():
                if filetrack.style in [typeOutput, typeRequired]:
                    filepath = os.path.join(self.workingFrame.localfilepath, filetrack.file_name)
                    with open(filepath, 'rb') as f:
                        data[fileheader] = (io.BytesIO(f.read()), filetrack.file_name)

            print('data', data)
            response = client.post("/CONTAINERS/newContainer", headers=headers, data=data, content_type='multipart/form-data',)
        if 'Container Made' == response.headers['response']:
            # print(response)
            resp = json.loads(response.data)
            returncontdict = resp['containerdictjson']
            returnframedict = resp['framedictjson']
            self.allowedUser= returncontdict['allowedUser']
            self.workingFrame.FrameInstanceId = returnframedict['FrameInstanceId']
            self.workingFrame.commitMessage = returnframedict['commitMessage']
            self.workingFrame.commitUTCdatetime = returnframedict['commitUTCdatetime']
            for filetrack in returnframedict['filestrack']:
                fileheader = filetrack['FileHeader']
                self.workingFrame.filestrack[fileheader].commitUTCdatetime = filetrack['commitUTCdatetime']
                if not self.workingFrame.filestrack[fileheader].md5 == filetrack['md5']:
                    warnings.warn('MD5 changed')
                self.workingFrame.filestrack[fileheader].committedby = filetrack['committedby']
                # self.workingFrame.filestrack[fileheader].file_id = filetrack['file_id']

            frameyamlfn = os.path.join(self.containerworkingfolder, self.currentbranch,self.workingFrame.FrameName + '.yaml')
            self.workingFrame.writeoutFrameYaml(frameyamlfn)
            self.save()
            return True
        else:
            return False

    def commit(self, cframe: Frame, commitmsg, BASE):
        committed = False
        # # frameYamlfileb = framefs.get(file_id=ObjectId(curframe.FrameInstanceId))
        with open(self.refframefilepath) as file:
            frameRefYaml = yaml.load(file, Loader=yaml.FullLoader)
        frameRef = Frame.loadFramefromYaml(frameRefYaml, self.containerworkingfolder)
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
            newframe = Frame.loadFramefromYaml(frameyaml, self.containerworkingfolder)
            # Write out new frame information
            # The frame file is saved to the frame FS
            self.refframefilepath = frameyamlfn
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

    def filestomonitor(self):
        ftm={}
        for FileHeader, file in self.FileHeaders.items():
            ftm[FileHeader] = file['type']
        return ftm

    def commithistory(self):
        historyStr = ''
        # glob.glob() +'/'+ Rev + revnum + ".yaml"
        yamllist = glob.glob(self.containerworkingfolder + '/' + self.currentbranch + '*.yaml')
        for yamlfn in yamllist:
            pastframe = Frame.loadFramefromYaml(yamlfn, self.containerworkingfolder)
            # print(pastframe.commitMessage)
            historyStr = historyStr + pastframe.FrameName + '\t' + pastframe.commitMessage + '\t\t\t\t' + \
                         time.ctime(pastframe.commitUTCdatetime) + '\t\n'
        return historyStr

    def save(self, environ='Server', outyamlfn = None):
        if outyamlfn:
            outyaml = open(outyamlfn, 'w')
        else:
            if environ=='FrontEnd':
                outyaml = open(os.path.join(self.containerworkingfolder, self.containerName), 'w')
            elif environ=='Server':
                outyaml = open(os.path.join(self.containerworkingfolder, 'containerstate.yaml'), 'w')

        yaml.dump(self.dictify(), outyaml)
        outyaml.close()

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
        keytosave = ['containerName', 'containerId', 'FileHeaders', 'allowedUser', 'description', 'parentid']
        for key, value in vars(self).items():
            if key in keytosave:
                dictout[key] = value
        return dictout

    def addAllowedUser(self, new_email):
        if new_email not in self.allowedUser:
            self.allowedUser.append(new_email)
            self.save()
            return True , 'User Added to ' + self.containerName
        return False , 'User is already in the allowedUser, Container '+ self.containerName+ ' was not Updated'

    @staticmethod
    def compare(cont1,cont2):
        return recursivecompare(cont1.dictify(), cont2.dictify())

    def fullFrameHistory(self):
        fullframelist = {}
        yamllist = glob.glob(os.path.join(self.containerworkingfolder, self.currentbranch, '*.yaml'))
        for yamlfn in yamllist:

            pastframe = Frame.loadFramefromYaml(yamlfn, self.containerworkingfolder)
            # print(pastframe.commitMessage)
            fullframelist[os.path.basename(yamlfn)] = pastframe.dictify()
            # historyStr = historyStr + pastframe.FrameName + '\t' + pastframe.commitMessage + '\t\t\t\t' + \
            #              time.ctime(pastframe.commitUTCdatetime) + '\t\n'
        return fullframelist

    def FixConnections(self):
        revnum = 1
        filemd5={}
        while revnum<100:
            REVSTR= 'Rev' + str(revnum)
            yamlfn = os.path.join(self.containerworkingfolder, 'Main', 'Rev'+str(revnum)+'.yaml')
            if os.path.exists(yamlfn):
                try:
                    pastframe = Frame.loadFramefromYaml(yamlfn, self.containerworkingfolder)
                except:
                    print(self.containerName + '  Rev'+str(revnum)+'.yaml doesnt exist')
                    revnum+=1
                    continue
                for fileheader, filetrack in pastframe.filestrack.items():
                    # if filetrack.lastupdated == NEEDSDOCTOR:
                    if fileheader in filemd5.keys():
                        if filemd5[fileheader]['md5'] == filetrack.md5:
                            filetrack.lastupdated = filemd5[fileheader]['latestrev']
                        else:
                            filetrack.lastupdated = REVSTR
                            filemd5[fileheader] = {'latestrev': REVSTR, 'md5': filetrack.md5}
                    else:
                        filemd5[fileheader] = {'latestrev': REVSTR, 'md5': filetrack.md5}
                        filetrack.lastupdated = REVSTR
                pastframe.writeoutFrameYaml(yamlfn=yamlfn)
            revnum += 1
                    # if filetrack.connection.connectionType.name==typeOutput:
                    #         print(self.containerId + ' ID with name ' + self.containerName + ' and ' + revnum + ' has ' + fileheader +' has broken Input rev ')

                    # if filetrack.connection.connectionType.name==typeInput:
                    #     if self.containerName=='ConflictsTester' and filetrack.FileHeader=='Requirements':
                    #         b = 5
                    #
                    #     pastrevnum=1
                    #     found = False
                    #     while pastrevnum<100:
                    #         sectionfolder = os.path.dirname(self.containerworkingfolder)
                    #         frameyaml = os.path.join(sectionfolder,filetrack.connection.refContainerId, 'Main','Rev' + str(pastrevnum)+'.yaml')
                    #         if os.path.exists(frameyaml):
                    #             upstreampastframe = Frame.loadFramefromYaml(frameyaml, None)
                    #             if fileheader in upstreampastframe.filestrack.keys():
                    #                 if upstreampastframe.filestrack[fileheader].md5 == filetrack.md5:
                    #                     print(self.containerId + ' ID with name ' + self.containerName + ' and ' + str(
                    #                         revnum) + ' has ' + fileheader + ' has broken Input but found it at ' + filetrack.connection.refContainerId+ ' at rev ' +upstreampastframe.FrameName )
                    #                     if filetrack.connection.Rev is None:
                    #                         filetrack.connection.Rev = upstreampastframe.FrameName
                    #                     else:
                    #                         if filetrack.connection.Rev !=upstreampastframe.FrameName:
                    #                             print(filetrack.connection.Rev, upstreampastframe.FrameName)
                    #                             filetrack.connection.Rev = upstreampastframe.FrameName
                    #                     found = True
                    #                     break
                    #         else:
                    #             pass
                    #         pastrevnum+=1
                    #     if not found:
                    #         print(self.containerId + ' ID with name ' + self.containerName + ' and ' + str(
                    #             revnum) + ' has ' + fileheader + ' has broken Input and cannot match to upstream md5')


def recursivecompare(dict1, dict2):
    diff = {}
    identical = True
    dict2keys = list(dict2.keys())
    for key, value in dict1.items():
        if key not in dict2.keys():
            # catches the keys missing in dict2 which is the new cont which means its something deleted
            diff[key]='MissingInDict2'
            identical = False
            continue
        else:
            dict2keys.remove(key)
        if type(value) is not dict:
            if dict2[key] != value:
                identical = False
                diff[key] = [value, dict2[key]]
        else:
            id, difference = recursivecompare(value, dict2[key])
            identical = identical if id else id
            diff[key] = difference
    for remainingkey in dict2keys:
        diff[remainingkey]='MissingInDict1'
        # catches the keys missing in dict1 whic means the new cont has fileheaders curcont doesnt which means user added new fileheader
    return identical, diff


