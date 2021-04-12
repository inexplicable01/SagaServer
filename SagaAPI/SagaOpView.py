import os
from flask import request, send_from_directory, safe_join,make_response,jsonify
from flask_restful import Resource
from SagaCore.Container import Container
from SagaCore.Frame import Frame
import re
import uuid
from SagaUser.UserModel import User
from flask import current_app
import json
from Config import typeInput, typeOutput, typeRequired
from SagaAPI.SagaAPI_Util import authcheck
from flask_mail import Message,Mail
from SagaCore.MailSender import MailSender
from SagaCore.Frame import Frame
import shutil
import uuid
import hashlib
from datetime import datetime
from SagaCore.SagaOp import SagaOp

Rev='Rev'
CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class SagaOperationsView(Resource):

    def latestRev(self, path):
        #add comment
        revnum = 0;
        for fn in os.listdir(path):
            m = re.search('Rev(\d+).yaml',fn)
            if  int(m.group(1))>revnum:
                revnum = int(m.group(1))
                latestrev = fn
        return latestrev, revnum

    def __init__(self, rootpath):
        self.rootpath = rootpath
        self.mail = Mail(current_app)
        self.sagaop = SagaOp()

    def post(self, command=None):
        authcheckresult = authcheck(request.headers.get('Authorization'))

        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            responseObject = {
                'status': 'fail',
                'message': 'User Check came back failed'
            }
            return make_response(jsonify(responseObject))
            # return resp, num # user would be a type of response if its not the actual class user
        user = authcheckresult
        sectionid = user.sectionid
        try:
            resp = make_response()
            if command == "newContainer":
                containerdict = json.loads(request.form['containerdictjson'])
                framedict = json.loads(request.form['framedictjson'])
                result = self.sagaop.newContainer(containerdict,framedict,sectionid,request.files,user, self.rootpath)

                resp.headers["response"] = result["message"]
                if result["data"]:
                    resp.data = result["data"]
                return resp

            elif command == "commit":
                containerID = request.form.get('containerID')
                curcont = Container.LoadContainerFromYaml(safe_join(self.rootpath, CONTAINERFOLDER,  sectionid, containerID, 'containerstate.yaml'))
                if user.email not in curcont.allowedUser:
                    responseObject = {
                            'status': 'fail',
                            'message': 'User  is not allowed to commit to this Container'
                        }
                    return make_response(jsonify(responseObject)), 401

                containerdict= json.loads(request.form['containerdictjson'])

                newcont = Container.LoadContainerFromDict(containerdict=containerdict)

                # All of this has to be replaced with world map logic
                identical, diff = Container.compare(curcont, newcont)
                if not identical:
                    if user.email not in curcont.allowedUser:
                        responseObject = {
                            'status': 'fail',
                            'message': 'User  is not allowed to change the container.'
                        }
                        return make_response(jsonify(responseObject)), 401

                savenewcont = False
                for fileheader in diff['FileHeaders'].keys():
                    if 'MissingInDict1'== diff['FileHeaders'][fileheader]:
                        savenewcont=True
                        if newcont.FileHeaders[fileheader]['type']== typeInput:
                            print('Added new Input.  containerID needs an output update.  An Output update means add cont')
                            upstreamcontainerid = newcont.FileHeaders[fileheader]['Container']
                            upstreamcont = Container.LoadContainerFromYaml(
                                safe_join(self.rootpath, CONTAINERFOLDER,sectionid, upstreamcontainerid, 'containerstate.yaml'))
                            upstreamcont.FileHeaders[fileheader]['Container'].append(containerID)
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
                            if containerID in upstreamcont.FileHeaders[fileheader]['Container']:
                                upstreamcont.FileHeaders[fileheader]['Container'].remove(containerID)
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
                                responseObject = {
                                    'status': 'fail',
                                    'message': 'You tried to delete a fileheader but you have not removed all the downstream links yet.  You need to remove ' + downcontstr +'downstream connections',
                                    'ErrorType': 'Tried to remove output fileheader without clearing dependency.'
                                }
                                return make_response(jsonify(responseObject))

                branch = request.form['branch']
                updateinfo = json.loads(request.form['updateinfo'])
                commitmsg = request.form['commitmsg']

                latestrevfn, revnum = self.latestRev(safe_join(self.rootpath, CONTAINERFOLDER, sectionid, containerID, branch))


                # refframe = os.path.join(self.rootpath, 'Container', containerID, branch, latestrevfn)

                framedict = json.loads(request.form['framedictjson'])
                frameupload = Frame.LoadFrameFromDict(framedict)



                attnfiles = [file for file in request.files.keys()]
                committime = datetime.timestamp(datetime.utcnow())
                mailsender = MailSender()
                for fileheader, filetrack in frameupload.filestrack.items():
                    if fileheader in attnfiles:
                        filetrack.md5 = updateinfo[fileheader]['md5']
                        filetrack.file_name = updateinfo[fileheader]['file_name']
                        filetrack.lastEdited = updateinfo[fileheader]['lastEdited']
                        filetrack.committedby = user.email
                        filetrack.style = updateinfo[fileheader]['style']
                        filetrack.file_id = uuid.uuid4().__str__()
                        filetrack.commitUTCdatetime = committime

                        content = request.files[fileheader].read()
                        with open(os.path.join(self.rootpath, FILEFOLDER, filetrack.file_id), 'wb') as file:
                            file.write(content)
                        if filetrack.connection:
                            if filetrack.connection.connectionType.name == typeOutput:
                                for downcontainerid  in curcont.FileHeaders[fileheader]['Container']:
                                    downstreamcont = Container.LoadContainerFromYaml(
                                        safe_join(self.rootpath, CONTAINERFOLDER, sectionid, downcontainerid,
                                                  'containerstate.yaml'))
                                    mailsender.prepareMail(recipemail=downstreamcont.allowedUser,
                                                           fileheader=fileheader,
                                                           filetrack=filetrack, user=user, upcont = curcont,
                                                           commitmsg=commitmsg,
                                                           committime=committime,
                                                            newrevnum=revnum + 1)
                        attnfiles.remove(fileheader)

                for newfiles in attnfiles:
                  print('Add a FileTrack to frameRef.filestrack for ' + newfiles)
                frameupload.FrameInstanceId = uuid.uuid4().__str__()
                frameupload.commitMessage = commitmsg
                frameupload.commitUTCdatetime = committime
                frameupload.FrameName = Rev + str(revnum + 1)
                newrevfn = Rev + str(revnum + 1) + ".yaml"
                newframefullpath = os.path.join(self.rootpath, CONTAINERFOLDER,sectionid, containerID, branch, newrevfn)

                frameupload.writeoutFrameYaml(newframefullpath)
                mailsender.sendMail()


                if savenewcont:
                    newcont.save('Server', safe_join(self.rootpath, CONTAINERFOLDER,sectionid, containerID, 'containerstate.yaml'))
                result = send_from_directory(safe_join(self.rootpath, CONTAINERFOLDER,sectionid, containerID, branch), newrevfn)
                result.headers['file_name'] = newrevfn
                result.headers['branch'] = 'Main'
                result.headers['commitsuccess'] = True
                return result
            elif command == "deleteContainer":
                    containerId = request.form['containerId']
                    delCont = Container.LoadContainerFromYaml(
                        os.path.join(self.rootpath, CONTAINERFOLDER, sectionid, containerId, 'containerstate.yaml'))

                    if user.email not in delCont.allowedUser:
                        responseObject = {
                            'status': 'fail',
                            'message': 'User  is not allowed to commit to this Container'
                        }
                        return make_response(jsonify(responseObject)), 401

                    if os.path.exists(safe_join(self.rootpath, CONTAINERFOLDER, sectionid,containerId)):
                        for fileheader, filecon in delCont.FileHeaders.items():
                            if filecon['type'] == typeOutput:
                                for containerid in filecon['Container']:
                                    downstreamCont = Container.LoadContainerFromYaml(
                                        os.path.join(self.rootpath, CONTAINERFOLDER, sectionid, containerid,
                                                     'containerstate.yaml'))
                                    downstreamCont.FileHeaders.pop(fileheader, None)
                                    downstreamCont.save(environ='Server',
                                                        outyamlfn=os.path.join(self.rootpath, CONTAINERFOLDER, sectionid,
                                                                               containerid, 'containerstate.yaml'))
                            elif filecon['type'] == typeInput:
                                containerid = filecon['Container']
                                upstreamcont = Container.LoadContainerFromYaml(
                                    os.path.join(self.rootpath, CONTAINERFOLDER, sectionid, containerid,
                                                 'containerstate.yaml'))
                                if delCont.containerId in upstreamcont.FileHeaders[fileheader]['Container']:
                                    upstreamcont.FileHeaders[fileheader]['Container'].remove(delCont.containerId)

                                upstreamcont.save(environ='Server',
                                                  outyamlfn=os.path.join(self.rootpath, CONTAINERFOLDER, sectionid,
                                                                         containerid,
                                                                         'containerstate.yaml'))

                        resp.headers["response"] = "I'm gonna delete this"
                        resp.data = 'Deleted'
                        shutil.rmtree(safe_join(self.rootpath, CONTAINERFOLDER, sectionid, containerId))
                        return resp
                    else:
                        resp.headers["response"] = "Container " + containerId + " doesn't exist"
                        return resp
        except Exception as e:
            with open('commitError.txt','a+') as errorfile:
                # errorfile.write(datetime.now().isoformat() + ': Container: ' + request.form.get('containerID') +'\n')
                errorfile.write(datetime.now().isoformat() + str(e)+'\n')
                errorfile.write(datetime.now().isoformat() + 'ErrorType' + str(e)+'\n')
                errorfile.write('\n')
            responseObject = {
                'status': 'fail',
                'message': str(e),
                'ErrorType':str(e)
            }

            return make_response(jsonify(responseObject))
