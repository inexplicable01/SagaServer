from SagaCore.Container import Container
from SagaCore.Frame import Frame
from datetime import datetime
import os
from flask import safe_join,current_app
from Config import typeInput, typeOutput, typeRequired
from flask import request, send_from_directory, safe_join,make_response,jsonify
import uuid
import hashlib
import json
import re

Rev='Rev'
CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class SagaOp():
    def __init__(self,rootpath):
        self.rootpath = rootpath

    def latestRev(self, path):
        #add comment
        revnum = 0;
        for fn in os.listdir(path):
            m = re.search('Rev(\d+).yaml',fn)
            if  int(m.group(1))>revnum:
                revnum = int(m.group(1))
                latestrev = fn
        return latestrev, revnum

    def newContainer(self,containerdict,framedict,sectionid,files,user):
        newcont = Container.LoadContainerFromDict(containerdict=containerdict)
        newcont.workingFrame = Frame.LoadFrameFromDict(framedict)
        newcont.revnum = 1
        committime = datetime.timestamp(datetime.utcnow())
        if os.path.exists(safe_join(self.rootpath, CONTAINERFOLDER, sectionid, newcont.containerId)):
            return {"message":"Container Already exists",
                    "data":None}
        else:
            os.mkdir(safe_join(self.rootpath, CONTAINERFOLDER, sectionid, newcont.containerId))
            os.mkdir(safe_join(self.rootpath, CONTAINERFOLDER, sectionid, newcont.containerId, 'Main'))
            for fileheader, filecon in newcont.FileHeaders.items():
                if filecon['type'] == typeInput:
                    containerid = filecon['Container']
                    upstreamCont = Container.LoadContainerFromYaml(
                        os.path.join(self.rootpath, CONTAINERFOLDER, sectionid, containerid, 'containerstate.yaml'))
                    if type(upstreamCont.FileHeaders[fileheader]['Container']) is list:
                        upstreamCont.FileHeaders[fileheader]['Container'].append(newcont.containerId)
                    else:
                        upstreamCont.FileHeaders[fileheader]['Container'] = [
                            upstreamCont.FileHeaders[fileheader]['Container'], newcont.containerId]
                    upstreamCont.save(environ='Server',
                                      outyamlfn=os.path.join(self.rootpath, CONTAINERFOLDER, sectionid, containerid,
                                                             'containerstate.yaml'))

            for fileheader in files.keys():
                print('fileheader' + fileheader)
                content = files[fileheader].read()
                newcont.workingFrame.filestrack[fileheader].file_id = uuid.uuid4().__str__()
                newcont.workingFrame.filestrack[fileheader].md5 = hashlib.md5(content).hexdigest()
                newcont.workingFrame.filestrack[fileheader].committedby = user.email
                newcont.workingFrame.filestrack[fileheader].style = 'Required'
                newcont.workingFrame.filestrack[fileheader].commitUTCdatetime = committime
                with open(os.path.join(self.rootpath, FILEFOLDER,
                                       newcont.workingFrame.filestrack[fileheader].file_id),
                          'wb') as file:
                    file.write(content)
                # os.unlink(os.path.join(self.rootpath, FILEFOLDER, newframe.filestrack[FileHeader].file_id))

            newcont.allowedUser.append(user.email)
            newcont.save(environ='Server',
                         outyamlfn=safe_join(self.rootpath, CONTAINERFOLDER, sectionid, newcont.containerId,
                                             'containerstate.yaml'))
            newcont.workingFrame.commitUTCdatetime = committime
            newcont.workingFrame.FrameInstanceId = uuid.uuid4().__str__()
            newcont.workingFrame.writeoutFrameYaml( \
                safe_join(self.rootpath, CONTAINERFOLDER, sectionid, newcont.containerId, 'Main', 'Rev1.yaml'))


            return {"message":"Container Made",
                    "data":json.dumps(
                {'containerdictjson': newcont.dictify(),
                 'framedictjson': newcont.workingFrame.dictify()})
            }

    def commit(self,curcont:Container,newcont:Container,user,sectionid,commitframe:Frame, commitmsg ,updateinfo,files, mailsender, branch='Main'):
        identical, diff = Container.compare(curcont, newcont)
        if not identical:
            if user.email not in newcont.allowedUser:
                return {
                    'status': 'fail',
                    'message': 'User  is not allowed to change the container.',
                    'commitsuccess': False,
                }
        savenewcont = False
        for fileheader in diff['FileHeaders'].keys():
            if 'MissingInDict1'== diff['FileHeaders'][fileheader]:
                savenewcont=True
                if newcont.FileHeaders[fileheader]['type']== typeInput:
                    print('Added new Input.  containerID needs an output update.  An Output update means add cont')
                    upstreamcontainerid = newcont.FileHeaders[fileheader]['Container']
                    upstreamcont = Container.LoadContainerFromYaml(
                        safe_join(self.rootpath, CONTAINERFOLDER,sectionid, upstreamcontainerid, 'containerstate.yaml'))
                    upstreamcont.FileHeaders[fileheader]['Container'].append(curcont.containerId)
                    upstreamcont.save('Server', safe_join(self.rootpath, CONTAINERFOLDER,sectionid, upstreamcontainerid, 'containerstate.yaml'))
                elif newcont.FileHeaders[fileheader]['type'] == typeRequired:
                    print('Added new Entry to this container')
                elif newcont.FileHeaders[fileheader]['type'] == typeOutput:
                    downcontainerid = newcont.FileHeaders[fileheader]['Container']
                    print('Added a fileheader as an output.')
            if 'MissingInDict2' == diff['FileHeaders'][fileheader]:
                # a fileheader is removed
                savenewcont = True
                if curcont.FileHeaders[fileheader]['type']== typeInput:
                    print('Removed in  Input.  upstreamcontainerid needs an output update.  An Output update means remove cont')
                    upstreamcontainerid = curcont.FileHeaders[fileheader]['Container']
                    upstreamcont = Container.LoadContainerFromYaml(
                        safe_join(self.rootpath, CONTAINERFOLDER, sectionid,upstreamcontainerid, 'containerstate.yaml'))
                    if curcont.containerId in upstreamcont.FileHeaders[fileheader]['Container']:
                        upstreamcont.FileHeaders[fileheader]['Container'].remove(curcont.containerId)
                    upstreamcont.save('Server', safe_join(self.rootpath, CONTAINERFOLDER, sectionid, upstreamcontainerid, 'containerstate.yaml'))
                elif curcont.FileHeaders[fileheader]['type'] == typeRequired:
                    print('Removed new Entry to this container')
                elif curcont.FileHeaders[fileheader]['type'] == typeOutput:
                    print(
                        'Removed an Output.  downcontainerid needs an output update.  An Output update means remove cont')
                    downcontaineridlist = curcont.FileHeaders[fileheader]['Container']
                    fileheaderremovedready= True
                    downcontstr=''
                    for downcontainerid in downcontaineridlist:# check if downstreamcontainer already has
                        downstreamcont = Container.LoadContainerFromYaml(
                            safe_join(self.rootpath, CONTAINERFOLDER, sectionid, downcontainerid, 'containerstate.yaml'))
                        if fileheader in downstreamcont.FileHeaders.keys():
                            fileheaderremovedready = False
                            downcontstr=downcontstr+downstreamcont.containerName+' '
                    if not fileheaderremovedready:
                        return {
                            'status': 'fail',
                            'message': 'You tried to delete a fileheader but you have not removed all the downstream links yet.  You need to remove ' + downcontstr +'downstream connections',
                            'ErrorType': 'Tried to remove output fileheader without clearing dependency.',
                                         'commitsuccess':False
                        }
        latestrevfn, revnum = self.latestRev(safe_join(self.rootpath, CONTAINERFOLDER, sectionid, curcont.containerId, branch))

        attnfiles = [file for file in files.keys()]
        committime = datetime.timestamp(datetime.utcnow())
        updatedfiles={}
        for fileheader, filetrack in commitframe.filestrack.items():
            if fileheader in attnfiles:
                filetrack.md5 = updateinfo[fileheader]['md5']
                filetrack.file_name = updateinfo[fileheader]['file_name']
                filetrack.lastEdited = updateinfo[fileheader]['lastEdited']
                filetrack.committedby = user.email
                filetrack.style = updateinfo[fileheader]['style']
                filetrack.file_id = uuid.uuid4().__str__()
                filetrack.commitUTCdatetime = committime

                content = files[fileheader].read()
                with open(os.path.join(self.rootpath, FILEFOLDER, filetrack.file_id), 'wb') as file:
                    file.write(content)
                if filetrack.connection:
                    if filetrack.connection.connectionType.name == typeOutput:
                        for downcontainerid in newcont.FileHeaders[fileheader]['Container']:
                            downstreamcont = Container.LoadContainerFromYaml(
                                safe_join(self.rootpath, CONTAINERFOLDER, sectionid, downcontainerid,
                                          'containerstate.yaml'))
                            mailsender.prepareMailDownstream(recipemail=downstreamcont.allowedUser,
                                                   fileheader=fileheader,
                                                   filetrack=filetrack, user=user, upcont=curcont,
                                                   commitmsg=commitmsg,
                                                   committime=committime,
                                                   newrevnum=revnum + 1)
                attnfiles.remove(fileheader)
                updatedfiles[fileheader]=filetrack

        for newfiles in attnfiles:
            print('Add a FileTrack to frameRef.filestrack for ' + newfiles)
        commitframe.FrameInstanceId = uuid.uuid4().__str__()
        commitframe.commitMessage = commitmsg
        commitframe.commitUTCdatetime = committime
        commitframe.FrameName = Rev + str(revnum + 1)
        newrevfn = Rev + str(revnum + 1) + ".yaml"
        newframefullpath = os.path.join(self.rootpath, CONTAINERFOLDER, sectionid, curcont.containerId, branch, newrevfn)

        commitframe.writeoutFrameYaml(newframefullpath)

        mailsender.prepareMailthisContainer(thiscontainer =newcont,
                                   updatedfiles=updatedfiles,
                                    user=user,
                                   commitmsg=commitmsg,
                                   committime=committime,
                                   newrevnum=revnum + 1)
        mailsender.sendMail()

        if savenewcont:
            newcont.save('Server',
                         safe_join(self.rootpath, CONTAINERFOLDER, sectionid, curcont.containerId, 'containerstate.yaml'))

        return {
            'newrevfn':newrevfn,
            'commitsuccess' : True
        }
