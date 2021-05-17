import os
import io
from flask import Flask,flash, request, redirect, url_for,send_from_directory , send_file, make_response, safe_join
from flask_restful import Api, Resource
import zipfile
import shutil
from SagaCore.Container import Container
from SagaCore.Frame import Frame
from SagaAPI import db
from SagaDB.UserModel import User
from SagaDB.FileRecordModel import FileRecord
from SagaAPI.SagaAPI_Util import authcheck
from flask import current_app
from SagaCore.SagaOp import SagaOp
import re
import glob
import json


CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class PermissionsView(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath
        self.sagaop = SagaOp(rootpath)

    def get(self, command=None):

        if command=='getByContainer':
            resp = make_response()
            post_data = request.get_json()
            print(post_data['containerId'])
            containerId = post_data['containerId']
            sectionid = post_data['sectionid']
            contpath = os.path.join(os.path.join(self.rootpath, CONTAINERFOLDER,sectionid, containerId, 'containerstate.yaml'))
            userlist=[]
            sectionUser = User.query.filter(User.sections.any(sectionid=sectionid)).all()
            for user in sectionUser:
                userlist.append(user.printinfo())
            if os.path.exists(contpath):
                cont=Container.LoadContainerFromYaml(contpath)
                resp.data = json.dumps({'allowedUser':cont.allowedUser, 'sectionUser':userlist})
            else:
                resp.data = json.dumps({'allowedUser': [],
                                        'ServerMessage':'Could not find container' + containerId,
                                        'sectionUser':userlist})
            return resp
        # elif command=='Userlist':
        #     resp = make_response()
        #     users = User.query.all()
        #     userlist={}
        #     for user in users:
        #         userlist[user.id]= {'first_name':user.first_name, 'last_name':user.last_name,'email':user.email}
        #     resp.headers["response"] = "Userlist"
        #     resp.data = json.dumps(userlist)
        #     return resp

    def post(self, command=None):
        resp = make_response()
        authcheckresult = authcheck(request.headers.get('Authorization'))

        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            return resp, num
            # return resp, num # user would be a type of response if its not the actual class user
        user = authcheckresult
        if command=='AddUserToContainer':

            resp = make_response()
            post_data = request.get_json()
            containerId = post_data['containerId']
            new_email = post_data['new_email']
            sectionid = post_data['sectionid']
            result, ServerMessage, allowedUser = self.sagaop.AddUserToContainer(user, containerId, new_email, sectionid)
            resp.data = json.dumps({
                'allowedUser': allowedUser,
                'ServerMessage': ServerMessage,
                'result': result})
            return resp