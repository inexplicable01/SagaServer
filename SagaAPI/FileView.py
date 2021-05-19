import os
import io
from flask import Flask,flash, request, redirect, url_for,send_from_directory , send_file, make_response, safe_join
from flask_restful import Api, Resource
from flask import current_app
from SagaDB.UserModel import User, Role
import json
from SagaAPI.SagaAPI_Util import authcheck

FILEFOLDER = current_app.config['FILEFOLDER']

class FileView(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def get(self):
        file_id = request.form['file_id']
        file_name=request.form['file_name']
        if os.path.exists(safe_join(self.rootpath,FILEFOLDER,file_id)):
            result = send_from_directory(safe_join(self.rootpath,FILEFOLDER),file_id)
            result.headers['file_name'] = file_name
            result.headers['status'] = 'Success'
            return result
        else:
            resp = make_response()
            resp.headers['status'] = 'Failed'
            resp.data = json.dumps({ "response": "Invalid file ID  "+file_id})

            return resp

    def post(self):
        authcheckresult = authcheck(request.headers.get('Authorization'))

        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            return resp, num
            # return resp, num # user would be a type of response if its not the actual class user
        user = authcheckresult
        resp = make_response()
        resp.headers["status"] = 'Uploading file'
        adminrole = Role.query.filter(Role.name == 'Admin').first()
        if adminrole not in user.roles:
            resp.headers["status"] = 'User not an Admin!!'
            return resp
        else:
            file_id = request.form['file_id']
            content = request.files[file_id].read()
            with open(os.path.join(self.rootpath, FILEFOLDER, file_id), 'wb') as file:
                file.write(content)
            resp.headers["status"] = 'Adding File success'
            return resp
    #
    #     try:
    #         for fileheader in request.files.keys():
    #             content = request.files[fileheader].read()
    #             with open(os.path.join(self.rootpath, FILEFOLDER, fileheader),
    #                       'wb') as file:
    #                 file.write(content)
    #         return {"response":"Success"}
    #     except Exception as e:
    #         return {"response":"fail"}