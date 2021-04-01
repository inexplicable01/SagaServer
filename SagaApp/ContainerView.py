import os
from flask import request, send_from_directory, safe_join,make_response, jsonify
from flask_restful import Resource
from SagaApp.Container import Container
from SagaApp.Frame import Frame
from glob import glob
import json
import re
import shutil
import uuid
import hashlib
from datetime import datetime
from SagaApp.UserModel import User
from config import typeInput
from flask import current_app
from config import typeRequired,typeInput,typeOutput

CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class ContainerView(Resource):

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

    def get(self, command=None):
        authcheckresult = self.authcheck()
        if not isinstance(authcheckresult, User):
            responseObject = {
                'status': 'Sign in Failed',
                'message': 'authcheck came back none'
            }
            return make_response(jsonify(responseObject))
        user = authcheckresult
        gid = user.group_id
        branch ='Main'

        if command=="containerID":
            containerID = request.form['containerID']
            if os.path.exists(safe_join(self.rootpath, CONTAINERFOLDER,gid, containerID)):
                latestrevfn, revnum = self.latestRev(safe_join(self.rootpath, CONTAINERFOLDER,gid, containerID, branch))
                result = send_from_directory(safe_join(self.rootpath, CONTAINERFOLDER,gid, containerID), 'containerstate.yaml' )
                result.headers['file_name'] = 'containerstate.yaml'
                result.headers['branch'] = branch
                result.headers['revnum'] = str(revnum)
                return result
            else:
                return {"response": "Invalid Container ID"}
        elif command=="List":
            resp = make_response()
            containerinfolist = {}
            for containerid in os.listdir(safe_join(self.rootpath, CONTAINERFOLDER, gid)):
                curcont = Container.LoadContainerFromYaml(safe_join(self.rootpath, CONTAINERFOLDER,gid,containerid,'containerstate.yaml'))
                containerinfolist[containerid] = {'ContainerDescription': curcont.containerName,
                                         'branches':[]}
                for branch in os.listdir(safe_join(self.rootpath, CONTAINERFOLDER,gid,containerid)):
                    if os.path.isdir(safe_join(self.rootpath, CONTAINERFOLDER,gid,containerid,branch)):
                        containerinfolist[containerid]['branches'].append({'name': branch,
                                                                    'revcount':len(glob(safe_join(self.rootpath, CONTAINERFOLDER,gid,containerid,branch,'*')))})

            resp.headers["response"] = "returnlist"
            resp.headers["containerinfolist"] = json.dumps(containerinfolist)
            resp.data = json.dumps(containerinfolist)
            return resp

        elif command=="tester":
            resp = make_response()
            resp.data=json.dumps({'dicit':'pop','plo':3})
            return resp
        elif command=="fullbranch":
            containerID = request.form['containerID']
            branch = request.form['branch']
            # result = send_from_directory(safe_join(self.rootpath, CONTAINERFOLDER, containerID, branch), 'Rev1.yaml')
            filepath = safe_join(self.rootpath, CONTAINERFOLDER, gid, containerID, branch)
            resp = make_response()
            resp.data=json.dumps(os.listdir(filepath))
            return resp
        else:
            resp = make_response()
            resp.headers["response"] = "Incorrect Command"
            return resp

    def post(self, command=None):
        authcheckresult = self.authcheck()

        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            responseObject = {
                'status': 'Sign in Failed',
                'message': 'authcheck came back none'
            }
            return make_response(jsonify(responseObject))
            # return resp, num # user would be a type of response if its not the actual class user
        user = authcheckresult
        gid = user.group_id

        resp = make_response()
        resp.headers["response"] = "Incorrect Command"
        if command=="newContainer":
            containerdict = json.loads(request.form['containerdictjson'])
            # newcont = Container()
            newcont = Container.LoadContainerFromDict(containerdict=containerdict)
            framedict = json.loads(request.form['framedictjson'])
            newcont.workingFrame = Frame.LoadFrameFromDict(framedict)
            newcont.revnum =1
            committime = datetime.timestamp(datetime.utcnow())

            if os.path.exists(safe_join(self.rootpath, CONTAINERFOLDER, gid, newcont.containerId)):
                resp.headers["response"] = "Container Already exists"
                return resp
            else:

                os.mkdir(safe_join(self.rootpath, CONTAINERFOLDER, gid, newcont.containerId))
                os.mkdir(safe_join(self.rootpath, CONTAINERFOLDER, gid, newcont.containerId,'Main'))

                for fileheader, filecon in newcont.FileHeaders.items():
                    if filecon['type'] == typeInput:
                        containerid= filecon['Container']
                        upstreamCont = Container.LoadContainerFromYaml(
                            os.path.join(self.rootpath, CONTAINERFOLDER,  gid, containerid, 'containerstate.yaml'))
                        if type(upstreamCont.FileHeaders[fileheader]['Container']) is list:
                            upstreamCont.FileHeaders[fileheader]['Container'].append(newcont.containerId)
                        else:
                            upstreamCont.FileHeaders[fileheader]['Container']= [
                                upstreamCont.FileHeaders[fileheader]['Container'],newcont.containerId]
                        upstreamCont.save(environ='Server',
                                         outyamlfn=os.path.join(self.rootpath, CONTAINERFOLDER,  gid, containerid,
                                                                    'containerstate.yaml'))

                for fileheader in request.files.keys():
                    print('fileheader' + fileheader)
                    content = request.files[fileheader].read()
                    newcont.workingFrame.filestrack[fileheader].file_id = uuid.uuid4().__str__()
                    newcont.workingFrame.filestrack[fileheader].md5 = hashlib.md5(content).hexdigest()
                    newcont.workingFrame.filestrack[fileheader].committedby = user.email
                    newcont.workingFrame.filestrack[fileheader].style = 'Required'
                    newcont.workingFrame.filestrack[fileheader].commitUTCdatetime = committime
                    # if newcont.workingFrame.filestrack[fileheader].connection:
                    #     downcontainerid = newcont.workingFrame.filestrack[fileheader].connection.refContainerId
                    #     downcontainer = Container.LoadContainerFromYaml(os.path.join(self.rootpath, CONTAINERFOLDER, downcontainerid,'containerstate.yaml'))
                    #     downcontainer.addFileObject(fileheader, {'Container': newcont.containerId, 'type': typeInput}, typeInput)
                    #     downcontainer.workingFrame.addfromOutputtoInputFileTotrack(newcont.workingFrame.filestrack[fileheader].file_name,
                    #                                                                fileheader,
                    #                                                                newcont.workingFrame.filestrack[fileheader],
                    #                                                                typeInput,
                    #                                                                newcont.containerId,
                    #                                                                'Main',
                    #                                                                'Rev' + str(newcont.revnum))
                    #     downcontainer.save(environ='Server',
                    #                  outyamlfn=safe_join(self.rootpath, CONTAINERFOLDER, downcontainer.containerId,
                    #                                      'containerstate.yaml'))
                    #     downcontainer.workingFrame.commitUTCdatetime = committime
                    #     downcontainer.workingFrame.FrameInstanceId = uuid.uuid4().__str__()
                    #     downcontainer.workingFrame.commitMessage = 'Commiting new frame based on ' + newcont.containerId +\
                    #                                                '   ' + newcont.workingFrame.commitMessage
                    #     downcontainer.workingFrame.writeoutFrameYaml( \
                    #         safe_join(self.rootpath, CONTAINERFOLDER, downcontainer.containerId, 'Main','Rev' + str(downcontainer.revnum+1) +'.yaml'))
                    #
                    #     newcont.workingFrame.filestrack[fileheader].connection.Rev = 'Rev' + str(downcontainer.revnum+1)
                    # # if connection.connectionType is output look for the downstream container
                    # load the container and add as input in downstream container
                    # take the latest frame in downstream container and add input file in
                    #  to filestrack  and save that too   new frame for
                    with open(os.path.join(self.rootpath, FILEFOLDER, newcont.workingFrame.filestrack[fileheader].file_id),
                              'wb') as file:
                        file.write(content)
                    # os.unlink(os.path.join(self.rootpath, FILEFOLDER, newframe.filestrack[FileHeader].file_id))

                newcont.allowedUser.append(user.email)
                newcont.save(environ='Server',
                             outyamlfn=safe_join(self.rootpath, CONTAINERFOLDER,  gid, newcont.containerId,'containerstate.yaml'))
                newcont.workingFrame.commitUTCdatetime=committime
                newcont.workingFrame.FrameInstanceId=uuid.uuid4().__str__()
                newcont.workingFrame.writeoutFrameYaml( \
                    safe_join(self.rootpath, CONTAINERFOLDER,  gid, newcont.containerId,'Main','Rev1.yaml'))


                resp.headers["response"] = "Container Made"
                resp.data = json.dumps({'containerdictjson': newcont.dictify(), 'framedictjson': newcont.workingFrame.dictify()})
                return resp
        else:
            resp = make_response()
            resp.headers["response"] = "Incorrect Command"
            return resp

    def delete(self, command=None):
        resp = make_response()
        resp.headers["response"] = "Delete Response"
        authcheckresult = self.authcheck()

        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            responseObject = {
                'status': 'fail',
                'message': 'resp'
            }
            return make_response(jsonify(responseObject))
            # return resp, num # user would be a type of response if its not the actual class user
        user = authcheckresult
        gid = user.group_id

        if command=="deleteContainer":
            containerId = request.form['containerId']
            delCont = Container.LoadContainerFromYaml(os.path.join(self.rootpath, CONTAINERFOLDER, gid, containerId, 'containerstate.yaml'))

            if user.email not in delCont.allowedUser:
                responseObject = {
                        'status': 'fail',
                        'message': 'User  is not allowed to commit to this Container'
                    }
                return make_response(jsonify(responseObject)), 401

            if os.path.exists(safe_join(self.rootpath, CONTAINERFOLDER, containerId)):
                for fileheader, filecon in delCont.FileHeaders.items():
                    if filecon['type']==typeOutput:
                        for containerid in filecon['Container']:
                            downstreamCont = Container.LoadContainerFromYaml(os.path.join(self.rootpath, CONTAINERFOLDER,  gid, containerid, 'containerstate.yaml'))
                            downstreamCont.FileHeaders.pop(fileheader, None)
                            downstreamCont.save(environ='Server',outyamlfn=os.path.join(self.rootpath, CONTAINERFOLDER,  gid, containerid, 'containerstate.yaml'))
                    elif filecon['type']==typeInput:
                        containerid= filecon['Container']
                        upstreamcont = Container.LoadContainerFromYaml(
                            os.path.join(self.rootpath, CONTAINERFOLDER, gid, containerid, 'containerstate.yaml'))
                        if delCont.containerId in upstreamcont.FileHeaders[fileheader]['Container']:
                            upstreamcont.FileHeaders[fileheader]['Container'].remove(delCont.containerId)

                        upstreamcont.save(environ='Server',
                                         outyamlfn=os.path.join(self.rootpath, CONTAINERFOLDER,  gid,containerid,
                                                                'containerstate.yaml'))

                resp.headers["response"] = "I'm gonna delete this"
                resp.data='Deleted'
                shutil.rmtree(safe_join(self.rootpath, CONTAINERFOLDER,  gid, containerId))
                return resp
            else:
                resp.headers["response"] = "Container " + containerId + " doesn't exist"
                return resp
        return resp



    def authcheck(self):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                if user:
                    return user
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)),401
