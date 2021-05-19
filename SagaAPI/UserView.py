from flask_restful import Resource
# from flask import , Flask, send_file, send_from_directory, , abort
from flask import render_template,request,make_response,safe_join,current_app,jsonify
from SagaDB.UserModel import User
from SagaAPI.SagaAPI_Util import authcheck
from Config import basedir
from SagaCore.Container import Container
import json
import os

CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class UserView(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def get(self, command=None):
        authcheckresult = authcheck(request.headers.get('Authorization'))

        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            return resp, num
            # return resp, num # user would be a type of response if its not the actual class user
        user = authcheckresult
        sectionid = user.sections[0].sectionid
        resp = make_response()
        if "usercontainers" == command:
            resp.headers["status"] = "Retrieval Success"
            # print(user.sections[0].sectionname)
            usercontainerinfo={
                'usersectionid': user.sections[0].sectionname,
                'usercontainers':{}
            }
            for containerid in os.listdir(safe_join(basedir, CONTAINERFOLDER, sectionid)):
                containerfn = safe_join(basedir, CONTAINERFOLDER, sectionid, containerid, 'containerstate.yaml')
                if os.path.exists(containerfn):
                    curcont = Container.LoadContainerFromYaml(containerfn)
                    usercontainerinfo['usercontainers'][containerid] = curcont.containerName
            # resp.data = json.dumps(usercontainerinfo)
            return make_response(jsonify(usercontainerinfo))

