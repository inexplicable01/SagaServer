import os
import io
from flask import Flask,flash, request,g, jsonify, url_for,send_from_directory , send_file, make_response, safe_join
from flask_restful import Api, Resource
from flask import current_app
from SagaDB.UserModel import User, Role, UserRoles, UserSections, SectionDB
import json

from SagaAPI.SagaAPI_Util import authcheck
FILEFOLDER = current_app.config['FILEFOLDER']

class GeneralView(Resource):
    # General / UpdatedInstallation
    def __init__(self, appdatadir, webserverdir,sagauserdb, sagacontroller):
        self.appdatadir = appdatadir
        self.webserverdir=webserverdir
        self.sagauserdb= sagauserdb
        self.sagacontroller = sagacontroller




    def get(self, command=None):
        authcheckresult = authcheck(request.headers.get('Authorization'))

        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            return resp

        if command=='UpdatedInstallation':
            # file_id = request.form['file_id']
            # file_name=request.form['file_name']
            if os.path.exists(safe_join(self.webserverdir,'static/executable/Saga.exe')):
                result = send_from_directory(safe_join(self.webserverdir,'static/executable/'),'Saga.exe')
                result.headers['file_name'] = 'Saga.exe'
                result.headers['status'] = 'Success'
                return result
            else:
                resp = make_response()
                resp.headers['status'] = 'Failed'
                resp.data = json.dumps({ "response": safe_join(self.webserverdir,'static/executable/Saga.exe') + " missing"  })
                return resp
        elif command=='returnDBinYAML':
            writeNewYaml = request.form['WriteNewYaml']
            resp = make_response()
            resp.headers['status'] = 'Success'
            # self.sagauserdb.updatefromdb(User=User, Role=Role, UserRoles=UserRoles, UserSections=UserSections, Section=Section)
            if writeNewYaml=='True':
                self.sagauserdb.updatefromdb(User=User, Role=Role, UserRoles=UserRoles, UserSections=UserSections,
                                             SectionDB=SectionDB)
                self.sagauserdb.writeoutyamlfile()
            resp.data = json.dumps(self.sagauserdb.dictify())
            return resp

        resp = make_response()
        resp.headers['status'] = 'Failed'
        resp.data = json.dumps({"response": "Invalid command under GENERAL"})
        return resp

    # def post(self):
    #     authcheckresult = authcheck(request.headers.get('Authorization'))
    #
    #     if not isinstance(authcheckresult, User):
    #         (resp, num) = authcheckresult
    #         return resp, num
    #         # return resp, num # user would be a type of response if its not the actual class user
    #     user = authcheckresult
    #     resp = make_response()
    #     resp.headers["status"] = 'Uploading file'
    #     adminrole = Role.query.filter(Role.name == 'Admin').first()
    #     if adminrole not in user.roles:
    #         resp.headers["status"] = 'User not an Admin!!'
    #         return resp
    #     else:
    #         file_id = request.form['file_id']
    #         content = request.files[file_id].read()
    #         with open(os.path.join(self.appdatadir, FILEFOLDER, file_id), 'wb') as file:
    #             file.write(content)
    #         resp.headers["status"] = 'Adding File success'
    #         return resp
    #
    #     try:
    #         for fileheader in request.files.keys():
    #             content = request.files[fileheader].read()
    #             with open(os.path.join(self.appdatadir, FILEFOLDER, fileheader),
    #                       'wb') as file:
    #                 file.write(content)
    #         return {"response":"Success"}
    #     except Exception as e:
    #         return {"response":"fail"}