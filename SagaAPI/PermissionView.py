import os
import io
from flask import Flask,flash, request, redirect, url_for,send_from_directory , send_file, make_response, safe_join
from flask_restful import Api, Resource
# import zipfile
# import shutil
# from SagaCore.Container import Container
# from SagaCore.Frame import Frame
# from SagaAPI import db
from SagaDB.UserModel import User
from SagaDB.FileRecordModel import FileRecord
from SagaCore import CONTAINERFN
from SagaAPI.SagaAPI_Util import authcheck
from flask import current_app

import re
import glob
import json


CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class PermissionsView(Resource):

    def __init__(self, appdatadir, sagacontroller):
        self.appdatadir = appdatadir
        self.sagacontroller = sagacontroller

    def get(self, command=None):

        if command=='getByContainer':
            resp = make_response()
            post_data = request.get_json()
            if post_data:
                containerId = post_data['containerId']
                sectionid = post_data['current_sectionid']
            else:
                containerId = request.form['containerId']
                current_sectionid = request.form['current_sectionid']


            contpath = os.path.join(os.path.join(self.appdatadir, CONTAINERFOLDER,current_sectionid, containerId, CONTAINERFN))
            userlist=[]
            sectionUser = User.query.filter(User.sections.any(sectionid=current_sectionid)).all()
            for user in sectionUser:
                userlist.append(user.printinfo())
            if os.path.exists(contpath):
                cont = self.sagacontroller.provideContainer(current_sectionid, containerId)
                resp.data = json.dumps({'allowedUser':cont.allowedUser, 'sectionUser':userlist,'success':True,
                                        'message':'', 'failmessage':'', 'e':None})
            else:
                resp.data = json.dumps({'allowedUser': [],'success':False,  'failmessage':'', 'e':None,
                                        'message':'Could not find container' + containerId,
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
            if post_data:
                containerId = post_data.get('containerId')
                new_email = post_data.get('new_email')
                sectionid = post_data.get('sectionid')
            else:
                containerId = request.form['containerId']
                new_email = request.form['new_email']
                sectionid = request.form['sectionid']
            success, ServerMessage, allowedUser = self.sagacontroller.AddUserToContainer(user, containerId, new_email, sectionid)
            resp.data = json.dumps({
                'allowedUser': allowedUser,
                'message': ServerMessage,
                'success': success,
            'failmessage':'',
                'e':None})
            return resp