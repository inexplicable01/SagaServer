import os
from flask import request, make_response, jsonify
from flask_restful import Resource
import uuid
from SagaDB.UserModel import User, db
import yaml
from flask import current_app
from Config import SECTIONDIDHOLDER,basedir

CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class SectionView(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def get(self, command=None):

        resp = make_response()
        sectioninfo = {}
        if command =='List':
            for section in os.listdir(os.path.join(basedir, 'Container')):
                sectionyamlfn = os.path.join(basedir, 'Container', section, 'sectionstate.yaml')
                with open(sectionyamlfn, 'r') as yml:
                    sectionyaml = yaml.load(yml, Loader=yaml.FullLoader)
                # print(sectionyaml)
                sectioninfo[section] = sectionyaml
            resp.data = yaml.dump(sectioninfo)
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
            with open(os.path.join(self.rootpath, CONTAINERFOLDER, sectionid, 'sectionstate.yaml')) as file:
                sectionyaml = yaml.load(file, Loader=yaml.FullLoader)
            resp.headers["response"] = "Get description Section view"
            print(sectionyaml)
            resp.data = sectionyaml['description']
            return resp


    def post(self, command=None):
        authcheckresult = self.authcheck()

        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            responseObject = {
                'status': 'Sign in Failed',
                'message': 'authcheck came back none'
            }
            return make_response(jsonify(responseObject))
            # return resp, num # user would be a type of response if its not the actual class user
        user = authcheckresult
        section_name = request.form['new_section_name']
        new_description = request.form['new_description']
        newsectionid = uuid.uuid4().__str__()
        if SECTIONDIDHOLDER==user.sectionid:
            user.sectionid = newsectionid
            user.section_name=section_name
            os.mkdir(os.path.join(self.rootpath, CONTAINERFOLDER, newsectionid))
            newsection= {
                "sectionid": newsectionid,
                "sectionname": section_name,
                "description": new_description,
            }

            sectionyaml = open(os.path.join(self.rootpath, CONTAINERFOLDER, newsectionid,'sectionstate.yaml'), 'w')
            yaml.dump(newsection, sectionyaml)
            sectionyaml.close()
            db.session.commit()
            resp = make_response()
            resp.data = newsection
            return resp
        else:
            resp = make_response()





    def authcheck(self):
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
