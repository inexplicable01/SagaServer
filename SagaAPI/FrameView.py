import os
from flask import request, jsonify, send_from_directory , make_response, safe_join
from flask_restful import Resource
import json
import re
import glob
import uuid
from datetime import datetime
from SagaAPI import db
from SagaCore.Frame import Frame
from SagaDB.UserModel import User
from SagaAPI.SagaAPI_Util import authcheck
from SagaCore.Container import Container
from flask import current_app

CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']
Rev = 'Rev'


class FrameView(Resource):
    #Frame View deals mainly with get
    # When making a new frame aka commit, it can involve multiple containers and even other frames in other containers.
    # Being able to do this is a core ability of SAGA.
    # So it should be managed with related containers and frames in mind, which is why its managed somewhere else
    # However there are occasions where you need individual frame resourses which is provided here.
    def __init__(self, appdatadir):
        self.appdatadir = appdatadir

    def latestRev(self, path):
        revnum = 0;
        for fn in os.listdir(path):
            m = re.search('Rev(\d+).yaml',fn)
            if  int(m.group(1))>revnum:
                revnum = int(m.group(1))
                latestrev = fn
        return latestrev, revnum


    def get(self):
        authcheckresult = authcheck(request.headers.get('Authorization'))
        containerID = request.form['containerID']
        branch = request.form['branch']
        # sectionid = request.form['sectionid']
        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            return resp
            # return resp, num # user would be a type of response if its not the actual class user
        user = authcheckresult
        sectionid = user.currentsection.sectionid
        switchreport = None
        #check if containerID exists in user's currention section
        if not os.path.exists(safe_join(self.appdatadir,CONTAINERFOLDER, sectionid, containerID)):
            # search if this container exists in any of the other containers
            for section in user.sections:
                if os.path.exists(safe_join(self.appdatadir,CONTAINERFOLDER, section.sectionid, containerID)):
                    # switchreport = user.switchToSection(section.sectionid)
                    # db.session.commit()

                    sectionid = section.sectionid,
                    # user = User.query.filter(User.id == user.id).first()# Is this really necessary?
                    # resp.data=json.dumps({'report':report,'usersection':user.currentsection.sectionname})
                    # return resp
            if not switchreport:
                return {"response": "Container ID " + containerID +"does not exist in any section"}


        if 'rev' in request.form.keys():
            rev = request.form['rev']
            if os.path.exists(safe_join(self.appdatadir,CONTAINERFOLDER, sectionid, containerID,branch,rev)):
                result = send_from_directory(safe_join(self.appdatadir,CONTAINERFOLDER, sectionid, containerID,branch),rev)
                result.headers['branch'] = branch
                result.headers['switchreport'] = switchreport
                return result
            else:
                return {"response": "Invalid Frame Yaml" + rev}


        if os.path.exists(safe_join(self.appdatadir,CONTAINERFOLDER, sectionid, containerID)):
            if os.path.exists(safe_join(self.appdatadir,CONTAINERFOLDER, sectionid, containerID, branch)):
                latestrevfn, revnum = self.latestRev(safe_join(self.appdatadir,CONTAINERFOLDER,  sectionid, containerID, branch))
                result = send_from_directory(safe_join(self.appdatadir,CONTAINERFOLDER,  sectionid, containerID, branch),latestrevfn)
                result.headers['file_name'] = latestrevfn
                result.headers['branch'] = branch
                result.headers['switchreport'] = switchreport
                return result
        else:
            return {"response": "Invalid Container ID"}

    # def post(self):
    #     authcheckresult = authcheck(request.headers.get('Authorization'))
    #
    #     if not isinstance(authcheckresult, User):
    #         (resp, num) = authcheckresult
    #         responseObject = {
    #             'status': 'fail',
    #             'message': 'resp'
    #         }
    #         return make_response(jsonify(responseObject))
    #         # return resp, num # user would be a type of response if its not the actual class user
    #     user = authcheckresult
    #     sectionid = user.sectionid
    #     containerID = request.form.get('containerID')
    #     curcont = Container.LoadContainerFromYaml(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid,  containerID, 'containerstate.yaml'))
    #
    #     if user.email in curcont.allowedUser:
    #         return user
    #     else:
    #         responseObject = {
    #             'status': 'fail',
    #             'message': 'User  is not allowed to commit to this Container'
    #         }
    #         return make_response(jsonify(responseObject)), 401
    #
    #     branch = request.form['branch']
    #     updateinfo = json.loads(request.form['updateinfo'])
    #     commitmsg = request.form['commitmsg']
    #     latestrevfn, revnum = self.latestRev(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, containerID, branch))
    #
    #     frameRef = Frame.loadFramefromYaml(os.path.join(self.appdatadir, CONTAINERFOLDER, sectionid, containerID, branch, latestrevfn))
    #     # print(frameRef)
    #     committime = datetime.timestamp(datetime.utcnow())
    #     for FileHeader, filetrackobj in frameRef.filestrack.items():
    #         if FileHeader in request.files.keys():
    #
    #             filetrackobj.md5= updateinfo[FileHeader]['md5']
    #             filetrackobj.file_name = updateinfo[FileHeader]['file_name']
    #             filetrackobj.lastEdited = updateinfo[FileHeader]['lastEdited']
    #             filetrackobj.committedby = user.email
    #             filetrackobj.style = updateinfo[FileHeader]['style']
    #             filetrackobj.file_id = uuid.uuid4().__str__()
    #             filetrackobj.commitUTCdatetime = committime
    #             # request.files[FileHeader].save(os.path.join(self.appdatadir, 'Files', filetrackobj.file_id))
    #             content = request.files[FileHeader].read()
    #             with open(os.path.join(self.appdatadir, FILEFOLDER, filetrackobj.file_id), 'wb') as file:
    #                 file.write(content)
    #
    #             # print(filetrackobj.file_name)
    #             # print(request.files[filetrackobj.file_name])
    #
    #     frameRef.FrameInstanceId = uuid.uuid4().__str__()
    #     frameRef.commitMessage = commitmsg
    #     frameRef.commitUTCdatetime = committime
    #     frameRef.FrameName = Rev + str(revnum+1)
    #     newrevfn = Rev + str(revnum+1) + ".yaml"
    #     newframefullpath =  os.path.join(self.appdatadir, CONTAINERFOLDER, sectionid, containerID, branch, newrevfn)
    #     frameRef.writeoutFrameYaml(newframefullpath)
    #
    #     result = send_from_directory(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid,containerID, 'Main'), newrevfn)
    #     result.headers['file_name'] = newrevfn
    #     result.headers['branch'] = 'Main'
    #     result.headers['commitsuccess'] = True
    #     return result

