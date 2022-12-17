import os
from flask import request, make_response, jsonify
from flask_restful import Resource
import uuid
from SagaDB.UserModel import User, db, SectionDB
from SagaCore.Section import Section
import yaml
from flask import current_app
from SagaAPI.SagaAPI_Util import authcheck
import json

from Config import appdatadir

CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class SectionView(Resource):

    def __init__(self, appdatadir, sagacontroller):
        self.appdatadir = appdatadir
        self.sagacontroller = sagacontroller

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
            resp.data = json.dumps({'success':True,
                                     'message':'', 'failmessage':'', 'e':None,
                'sectioninfo':sectioninfo})
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
        resp = make_response()
        if command=='newsection':

            try:
                section_name = request.form['newsectionname']
                new_description = request.form['newsectiondescription']
                # if SECTIONDIDHOLDER==user.sectionid:
                # user.sectionid = newsectionid
                # user.section_name=section_name
                newsect= Section.CreateNewSection(sectionname=section_name,
                                                  description=new_description,
                                                  email=user.email,
                                                  appdatadir=appdatadir)

                ##ATTENTION NEED BETTER CHECKS BEFORE COMMIT IE, does section already exist,
                ## Commit fail etc.
                section = SectionDB(
                    sectionid=newsect.sectionid,
                    sectionname=section_name,
                )
                db.session.add(section)
                user.currentsection = section
                user.sections.append(section)
                db.session.commit()
                resp.data = json.dumps({
                    'success':True,
                    'message':'New Section ' + section_name+ ' Created with ' + newsect.sectionid,
                    'failmessage':'',
                    'e':None,
                    'newsection':section_name})
                return resp
            except Exception as e:
                resp.data = json.dumps({
                    'success': False,
                    'message': e.__str__(),
                    'failmessage': '',
                    'e': e,
                    'newsection': 'failed'})
                return resp
        elif command =='addemailstosection':
            sectionid = request.form['sectionid']## Assumes incoming sectionId is valid.
            emailsToInvite = request.form.getlist('emailsToInvite')## Assumes incoming Emails is in list and correct email format
            success,message,failmessage,error= self.sagacontroller.inviteEmailsToSection(sectionid,emailsToInvite, user)
            resp.data = json.dumps({'success':success, 'message':message, 'failmessage':failmessage, 'e':error})
            return resp






