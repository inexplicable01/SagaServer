import os
from flask import request, jsonify, send_from_directory , make_response, safe_join
from flask_restful import Resource
import json
import re
import uuid
import yaml
from datetime import datetime
from SagaApp.Frame import Frame
from SagaApp.UserModel import User
from SagaApp.Container import Container
from flask import current_app

CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']
Rev = 'Rev'


class FrameView(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def latestRev(self, path):
        revnum = 0;
        for fn in os.listdir(path):
            m = re.search('Rev(\d+).yaml',fn)
            if  int(m.group(1))>revnum:
                revnum = int(m.group(1))
                latestrev = fn
        return latestrev, revnum


    def get(self):
        authcheckresult = self.authcheck()
        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            return resp
            # return resp, num # user would be a type of response if its not the actual class user
        user = authcheckresult
        gid = user.group_id
        containerID = request.form['containerID']
        branch = request.form['branch']

        if 'rev' in request.form.keys():
            rev = request.form['rev']

            if os.path.exists(safe_join(self.rootpath,CONTAINERFOLDER, gid, containerID,branch,rev)):
                result = send_from_directory(safe_join(self.rootpath,CONTAINERFOLDER, gid, containerID,branch),rev)
                # result.headers['file_name'] = rev
                result.headers['branch'] = branch
                return result
            else:
                return {"response": "Invalid Frame Yaml" + rev}


        if os.path.exists(safe_join(self.rootpath,CONTAINERFOLDER, gid, containerID)):
            if os.path.exists(safe_join(self.rootpath,CONTAINERFOLDER, gid, containerID, branch)):
                latestrevfn, revnum = self.latestRev(safe_join(self.rootpath,CONTAINERFOLDER,  gid, containerID, branch))
                result = send_from_directory(safe_join(self.rootpath,CONTAINERFOLDER,  gid, containerID, branch),latestrevfn)
                result.headers['file_name'] = latestrevfn
                result.headers['branch'] = branch
                return result
        else:
            return {"response": "Invalid Container ID"}

    def post(self):
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
        containerID = request.form.get('containerID')
        curcont = Container.LoadContainerFromYaml(safe_join(self.rootpath, CONTAINERFOLDER, gid,  containerID, 'containerstate.yaml'))

        if user.email in curcont.allowedUser:
            return user
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User  is not allowed to commit to this Container'
            }
            return make_response(jsonify(responseObject)), 401

        branch = request.form['branch']
        updateinfo = json.loads(request.form['updateinfo'])
        commitmsg = request.form['commitmsg']
        latestrevfn, revnum = self.latestRev(safe_join(self.rootpath, CONTAINERFOLDER, gid, containerID, branch))

        frameRef = Frame.loadFramefromYaml(os.path.join(self.rootpath, CONTAINERFOLDER, gid, containerID, branch, latestrevfn))
        # print(frameRef)
        committime = datetime.timestamp(datetime.utcnow())
        for FileHeader, filetrackobj in frameRef.filestrack.items():
            if FileHeader in request.files.keys():

                filetrackobj.md5= updateinfo[FileHeader]['md5']
                filetrackobj.file_name = updateinfo[FileHeader]['file_name']
                filetrackobj.lastEdited = updateinfo[FileHeader]['lastEdited']
                filetrackobj.committedby = user.email
                filetrackobj.style = updateinfo[FileHeader]['style']
                filetrackobj.file_id = uuid.uuid4().__str__()
                filetrackobj.commitUTCdatetime = committime
                # request.files[FileHeader].save(os.path.join(self.rootpath, 'Files', filetrackobj.file_id))
                content = request.files[FileHeader].read()
                with open(os.path.join(self.rootpath, FILEFOLDER, filetrackobj.file_id), 'wb') as file:
                    file.write(content)

                # print(filetrackobj.file_name)
                # print(request.files[filetrackobj.file_name])

        frameRef.FrameInstanceId = uuid.uuid4().__str__()
        frameRef.commitMessage = commitmsg
        frameRef.commitUTCdatetime = committime
        frameRef.FrameName = Rev + str(revnum+1)
        newrevfn = Rev + str(revnum+1) + ".yaml"
        newframefullpath =  os.path.join(self.rootpath, CONTAINERFOLDER, gid, containerID, branch, newrevfn)
        frameRef.writeoutFrameYaml(newframefullpath)

        result = send_from_directory(safe_join(self.rootpath, CONTAINERFOLDER, gid,containerID, 'Main'), newrevfn)
        result.headers['file_name'] = newrevfn
        result.headers['branch'] = 'Main'
        result.headers['commitsuccess'] = True
        return result

    def authcheck(self ):
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