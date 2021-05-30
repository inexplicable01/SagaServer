from flask_restful import Resource
# from flask import , Flask, send_file, send_from_directory, , abort
from flask import render_template,request,make_response,safe_join,current_app,jsonify
from SagaDB.UserModel import User
from SagaAPI.SagaAPI_Util import authcheck
from Config import basedir
from SagaCore.Container import Container
import json
import os
from SagaAPI import db
import yaml

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
        sectionid = user.currentsection.sectionid
        resp = make_response()
        if "usercontainers" == command:
            resp.headers["status"] = "Retrieval Success"
            # print(user.sections[0].sectionname)
            usercontainerinfo={
                'usersectionname': user.sections[0].sectionname,
                'usercontainers':{}
            }
            for containerid in os.listdir(safe_join(basedir, CONTAINERFOLDER, sectionid)):
                containerfn = safe_join(basedir, CONTAINERFOLDER, sectionid, containerid, 'containerstate.yaml')
                if os.path.exists(containerfn):
                    curcont = Container.LoadContainerFromYaml(containerfn)
                    usercontainerinfo['usercontainers'][containerid] = curcont.containerName
            # resp.data = json.dumps(usercontainerinfo)
            return make_response(jsonify(usercontainerinfo))
        elif "getusersections" == command:
            sectioninfo={}
            for section in user.sections:
                sectionyamlfn = os.path.join(basedir, 'Container', section.sectionid, 'sectionstate.yaml')
                with open(sectionyamlfn, 'r') as yml:
                    sectionyaml = yaml.load(yml, Loader=yaml.FullLoader)
                # print(sectionyaml)
                sectioninfo[section.sectionid] = sectionyaml
            returndict = {'sectioninfo':sectioninfo, 'currentsection':user.currentsection.sectionname}
            return make_response(jsonify(returndict))

    def post(self, command=None):
        authcheckresult = authcheck(request.headers.get('Authorization'))

        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            return resp, num
            # return resp, num # user would be a type of response if its not the actual class user
        user = authcheckresult
        # sectionid = user.switchToSection()
        resp = make_response()
        if "switchusersection" == command:
            resp.headers["status"] = "Retrieval Success"
            newsectionid = request.form['newsectionid']
            # print(newsectionid)
            report = user.switchToSection(newsectionid)
            db.session.commit()
            user = User.query.filter(User.id == user.id).first()
            resp.data=json.dumps({'report':report,'usersection':user.currentsection.sectionname})
            # # print(user.sections[0].sectionname)
            # usercontainerinfo={
            #     'usersectionname': user.sections[0].sectionname,
            #     'usercontainers':{}
            # }
            # for containerid in os.listdir(safe_join(basedir, CONTAINERFOLDER, sectionid)):
            #     containerfn = safe_join(basedir, CONTAINERFOLDER, sectionid, containerid, 'containerstate.yaml')
            #     if os.path.exists(containerfn):
            #         curcont = Container.LoadContainerFromYaml(containerfn)
            #         usercontainerinfo['usercontainers'][containerid] = curcont.containerName
            # # resp.data = json.dumps(usercontainerinfo)
            return resp


