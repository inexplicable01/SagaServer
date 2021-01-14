import os
from flask import request, send_from_directory, safe_join,make_response,jsonify
from flask_restful import Resource
from SagaApp.Container import Container
from SagaApp.Frame import Frame
import re
import uuid
from datetime import datetime
from UserModel import User
import json

Rev='Rev'

class CommitView(Resource):

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

        try:
            containerID = request.form.get('containerID')
            curcont = Container(safe_join(self.rootpath, 'Container', containerID, 'containerstate.yaml'))
            if user.email not in curcont.allowedUser:
                responseObject = {
                        'status': 'fail',
                        'message': 'User  is not allowed to commit to this Container'
                    }
                return make_response(jsonify(responseObject)), 401

            containerdict= json.loads(request.form['containerdictjson'])

            newcont = Container(containerdict=containerdict)
            identical, diff = Container.compare(curcont, newcont)
            if not identical and user.email not in curcont.allowedUser:
                responseObject = {
                    'status': 'fail',
                    'message': 'User  is not allowed to change the container.'
                }
                return make_response(jsonify(responseObject)), 401
            branch = request.form['branch']
            updateinfo = json.loads(request.form['updateinfo'])
            commitmsg = request.form['commitmsg']
            latestrevfn, revnum = self.latestRev(safe_join(self.rootpath, 'Container', containerID, branch))
            refframe = os.path.join(self.rootpath, 'Container', containerID, branch, latestrevfn)

            framedict = json.loads(request.form['framedictjson'])
            frameupload = Frame(None,None,None,framedict)
            # frameRef = Frame(refframe, curcont.filestomonitor, os.path.join(self.rootpath, 'Files'))

            attnfiles = [file for file in request.files.keys()]
            committime = datetime.timestamp(datetime.utcnow())
            for fileheader, filetrack in frameupload.filestrack.items():
                if fileheader in attnfiles:
                    filetrack.md5 = updateinfo[fileheader]['md5']
                    filetrack.file_name = updateinfo[fileheader]['file_name']
                    filetrack.lastEdited = updateinfo[fileheader]['lastEdited']
                    filetrack.committedby = user.email
                    filetrack.style = updateinfo[fileheader]['style']
                    filetrack.file_id = uuid.uuid4().__str__()
                    filetrack.commitUTCdatetime = committime
                    # request.files[fileheader].save(os.path.join(self.rootpath, 'Files', filetrack.file_id))
                    content = request.files[fileheader].read()
                    with open(os.path.join(self.rootpath, 'Files', filetrack.file_id), 'wb') as file:
                        file.write(content)
                    attnfiles.remove(fileheader)

            for newfiles in attnfiles:
              print('Add a FileTrack to frameRef.filestrack for ' + newfiles)
            frameupload.FrameInstanceId = uuid.uuid4().__str__()
            frameupload.commitMessage = commitmsg
            frameupload.commitUTCdatetime = committime
            frameupload.FrameName = Rev + str(revnum + 1)
            newrevfn = Rev + str(revnum + 1) + ".yaml"
            newframefullpath = os.path.join(self.rootpath, 'Container', containerID, branch, newrevfn)
            if 'objective' in request.form.keys():
                responseObject = {
                    'status': 'Success',
                    'message': 'Reached end of Commit Post'
                }
                return make_response(jsonify(responseObject))
            else:
                frameupload.writeoutFrameYaml(newframefullpath)
                result = send_from_directory(safe_join(self.rootpath, 'Container', containerID, branch), newrevfn)
                result.headers['file_name'] = newrevfn
                result.headers['branch'] = 'Main'
                result.headers['commitsuccess'] = True
            return result
        except Exception as e:
            # print(e)
            responseObject = {
                'status': 'fail',
                'message': str(e)
            }
            return responseObject
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