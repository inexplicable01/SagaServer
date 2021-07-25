import os
from flask import request, make_response, jsonify
from flask_restful import Resource
import uuid
from SagaDB.UserModel import User, db, Section
import yaml
from flask import current_app
from SagaAPI.SagaAPI_Util import authcheck
import json

from Config import SECTIONDIDHOLDER,appdatadir

CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class SectionView(Resource):

    def __init__(self, appdatadir):
        self.appdatadir = appdatadir

    def get(self, command=None):

        resp = make_response()
        sectioninfo = {}
        if command =='List':
            for section in os.listdir(os.path.join(self.appdatadir, CONTAINERFOLDER)):
                sectionyamlfn = os.path.join(self.appdatadir, CONTAINERFOLDER, section, 'sectionstate.yaml')
                with open(sectionyamlfn, 'r') as yml:
                    sectionyaml = yaml.load(yml, Loader=yaml.FullLoader)
                # print(sectionyaml)
                sectioninfo[section] = sectionyaml
            resp.data = json.dumps(sectioninfo)
            return resp
        else:
            authcheckresult = self.authcheck()
            if not isinstance(authcheckresult, User):
                responseObject = {
                    'status': 'Sign in Failed',
                    'message': 'authcheck came back none'
                }
                return make_response(jsonify(responseObject))
            user = authcheckresult
            sectionid = request.form['sectionid']
            with open(os.path.join(self.appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml')) as file:
                sectionyaml = yaml.load(file, Loader=yaml.FullLoader)
            resp.headers["response"] = "Get description Section view"
            print(sectionyaml)
            resp.data = sectionyaml['description']
            return resp


    def post(self, command=None):
        authcheckresult = authcheck(request.headers.get('Authorization'))

        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            responseObject = {
                'status': 'Sign in Failed',
                'message': 'authcheck came back none'
            }
            return make_response(jsonify(responseObject))
            # return resp, num # user would be a type of response if its not the actual class user
        user = authcheckresult
        if command=='newsection':
            resp = make_response()
            try:
                section_name = request.form['newsectionname']
                new_description = request.form['newsectiondescription']
                newsectionid = uuid.uuid4().__str__()
                # if SECTIONDIDHOLDER==user.sectionid:
                # user.sectionid = newsectionid
                # user.section_name=section_name
                os.mkdir(os.path.join(self.appdatadir, CONTAINERFOLDER, newsectionid))
                newsection= {
                    "sectionid": newsectionid,
                    "sectionname": section_name,
                    "description": new_description,
                }
                sectionyaml = open(os.path.join(self.appdatadir, CONTAINERFOLDER, newsectionid,'sectionstate.yaml'), 'w')
                yaml.dump(newsection, sectionyaml)

                ##ATTENTION NEED BETTER CHECKS BEFORE COMMIT IE, does section already exist,
                ## Commit fail etc.
                sectionyaml.close()
                section = Section(
                    sectionid=newsectionid,
                    sectionname=section_name,
                )
                db.session.add(section)
                user.currentsection = section
                user.sections.append(section)
                db.session.commit()
                resp.data = json.dumps(newsection)
                resp.headers['status'] = 'New Section ' + section_name+ ' Created with ' + newsectionid
                return resp
            except Exception as e:
                resp.headers['status'] = 'New Section commit Failed'
                resp.headers['exception'] = e.__str__()
                return resp





