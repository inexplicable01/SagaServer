from flask_restful import Resource
# from flask import , Flask, send_file, send_from_directory, , abort
from flask import render_template,request,make_response,safe_join,current_app,jsonify
from SagaDB.UserModel import User
from SagaAPI.SagaAPI_Util import authcheck
from Config import appdatadir
from SagaCore.Container import Container
import json
import os
from SagaAPI import db
import yaml

CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class UserView(Resource):

    def __init__(self, appdatadir):
        self.appdatadir = appdatadir

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
            for containerid in os.listdir(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid)):
                containerfn = safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid, 'containerstate.yaml')
                if os.path.exists(containerfn):
                    curcont = Container.LoadContainerFromYaml(containerfn)
                    usercontainerinfo['usercontainers'][containerid] = curcont.containerName
            # resp.data = json.dumps(usercontainerinfo)
            return make_response(jsonify(usercontainerinfo))
        elif "getusersections" == command:
            sectioninfo={}
            for section in user.sections:
                sectionyamlfn = os.path.join(appdatadir, 'Container', section.sectionid, 'sectionstate.yaml')
                with open(sectionyamlfn, 'r') as yml:
                    sectionyaml = yaml.load(yml, Loader=yaml.FullLoader)
                # print(sectionyaml)
                sectioninfo[section.sectionid] = sectionyaml
            returndict = {'sectioninfo':sectioninfo, 'currentsection':user.currentsection.sectionname}
            return make_response(jsonify(returndict))
        elif "checkcontainerpermissions" == command:
            containerid = request.form['containerid']
            # check if containerID exists in user's currention section
            if not os.path.exists(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid)):
                # search if this container exists in any of the other sections
                for section in user.sections:
                    if os.path.exists(safe_join(self.appdatadir, CONTAINERFOLDER, section.sectionid, containerid)):
                        resp.headers[
                            'message'] = "User currently in section " + user.currentsection.sectionname + \
                                        ". User section need to switch to " + section.sectionname + \
                                         " for container " + containerid
                        resp.data = json.dumps(
                            {'sectionid': section.sectionid, 'containerid': containerid, 'goswitch': True})
                        return resp
                resp.headers['message'] =  "Container ID " + containerid + "does not exist in any section that the user is allowed to access"
                resp.data = json.dumps({'sectionid':None, 'containerid':containerid, 'goswitch':False})
                return resp

            else:
                # With the containerid supplied, the user current section is supplied, no switching needed
                resp.data = json.dumps({'sectionid':user.currentsection.sectionid , 'containerid':containerid, 'goswitch':False})
                resp.headers['message'] = "User section currently in " + user.currentsection.sectionid  + " and  it containers " + containerid
                return resp

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

            newsectionid = request.form['newsectionid']
            # print(newsectionid)
            report = user.switchToSection(newsectionid)##ATTENTION Wrote hack code to add
            # user to section even if they didn't have it
            db.session.commit()
            user = User.query.filter(User.id == user.id).first()# Is this really necessary?
            resp.data=json.dumps({'report':report,'usersection':user.currentsection.sectionname})
            resp.headers["status"] = "Switch Success"
            return resp
        #
        # elif "addusertosection"==command:
        #     report = user.addToSection(newsectionid)











