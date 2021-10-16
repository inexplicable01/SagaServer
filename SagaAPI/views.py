from flask.views import MethodView
from flask import Blueprint, request, make_response, jsonify

from SagaAPI import db
# from SagaApp.db import get_db
from SagaDB.UserModel import User,BlacklistToken, UserSections

from SagaCore.Section import Section
from flask import current_app
import os
from Config import appdatadir,worldmapid,version_num
import json

auth_blueprint = Blueprint('auth', __name__)
CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']


def buildreturndata(user:User, sectionnames, sectionids, version_num):
    return {'user_id': user.id,
                        'email': user.email,
                        'admin': user.admin,
                        'registered_on': user.registered_on.timestamp(),
                        'first_name': user.first_name,
                        'current_sectionname': user.currentsection.sectionname,
                        'current_sectionid': user.currentsection.sectionid,
                        'sectionname_list':sectionnames,
                        'sectionid_list': sectionids,
                        'last_name': user.last_name,
                        'version_num': version_num
                    }




class RegisterAPI(MethodView):
    """
    User Registration Resource
    """
    def get(self):
        responseObject = {
            'status': 'Register Get Online',
            'message': 'Fill in',
        }
        return make_response(jsonify(responseObject)), 200


    def post(self):
        # get the post data
        # post_data = request.get_json()
        resp = make_response()
        try:
            email = request.form['email']
            password = request.form['password']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
        except Exception as e:
            responseObject = {
                'status': 'fail',
                'message': 'missing either email, password, first_name, last_name ' + str(e)
            }
            resp.data = json.dumps(responseObject)
            return resp, 401
        try:
            sectionid = request.form['sectionid']
        except Exception as e:
            sectionid = worldmapid

        sectionyaml = os.path.join(appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml')
        cursection = Section.LoadSectionyaml(sectionyaml)
        section_name = cursection.sectionname
        # check if user already exists
        user = User.query.filter_by(email=email).first()
        if not user:
            try:
                user = User(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    sectionids=[cursection.sectionid],
                    currentsection_id=cursection.sectionid,
                )
                # insert the user
                db.session.add(user)
                db.session.commit()
                # generate the auth token
                auth_token, exptimestamp = user.encode_auth_token(user.id)
                sectionids = []
                sectionnames = []
                for section in user.sections:
                    sectionids.append(section.sectionid)
                    sectionnames.append(section.sectionname)
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully registered.',
                    'auth_token': auth_token.decode(),
                    'exptimestamp': exptimestamp,
                }

                # print('exp' + exptimestamp)
                resp.data = json.dumps(responseObject)
                return resp, 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': str(e) + '.  User Registration Failed'
                }
                resp.data = json.dumps(responseObject)
                return resp, 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            resp.data = json.dumps(responseObject)
            return resp, 202

class LoginAPI(MethodView):
    """
    User Login Resource
    """
    def post(self):
        # get the post data
        resp = make_response()
        post_data = request.get_json()
        if post_data:
            email = post_data.get('email')
            password = post_data.get('password')
        else:
            email = request.form['email']
            password= request.form['password']
        try:
            # fetch the user data
            user = User.query.filter_by(
                email=email
            ).first()
            if user and user.password==password:
                auth_token, exptimestamp = user.encode_auth_token(user.id)
                if auth_token:
                    sectionids =[]
                    sectionnames=[]
                    # for section in user.sections:
                    #     sectionids.append(section.sectionid)
                    #     sectionnames.append(section.sectionname)
                    signinresp = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode(),
                        # 'useremail': user.email,
                        # 'first_name': user.first_name,
                        # 'current_sectionname': user.currentsection.sectionname,
                        # 'current_sectionid': user.currentsection.sectionid,
                        # 'sectionname_list':sectionnames,
                        # 'sectionid_list': sectionids,
                        # 'last_name': user.last_name,
                        'exptimestamp':exptimestamp,
                        # 'version_num': version_num
                    }
                    # print('exp' + exptimestamp)
                    resp.data=json.dumps(signinresp)
                    return resp , 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User does not exist.'
                }
                resp.data = json.dumps(responseObject)
                return resp , 404
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Unable to Login user. Error likely with database.'
            }
            resp.data = json.dumps(responseObject)
            return resp, 500

class UserAPI(MethodView):
    """
    User Resource
    """
    def get(self):
        # get the auth token
        resp = make_response()
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                resp.data = json.dumps(responseObject)
                return resp, 401
        else:
            auth_token = ''
        if auth_token:
            userid = User.decode_auth_token(auth_token)
            if not isinstance(userid, str):
                user = User.query.filter_by(id=userid).first()
                sectionids = []
                sectionnames = []
                for section in user.sections:
                    sectionids.append(section.sectionid)
                    sectionnames.append(section.sectionname)
                responseObject = {
                    'status': 'success',
                    'data': buildreturndata(user, sectionnames, sectionids, version_num),
                }
                resp.data = json.dumps(responseObject)
                return resp, 200
            responseObject = {
                'status': 'fail',
                'message': 'id not str'
            }
            resp.data = json.dumps(responseObject)
            return resp, 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            resp.data = json.dumps(responseObject)
            return resp, 401

    def post(self):
        resp = make_response()
        auth_header = request.headers.get('Authorization')
        post_data = request.get_json()
        if 'email' in post_data.keys():
            email = post_data.get('email')
            password = post_data.get('password')
        else:
            email = request.form['email']
            password = request.form['password']
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
            userid = User.decode_auth_token(auth_token)
            if not isinstance(userid, str):
                user = User.query.filter_by(id=userid).first()
                nonupdatedpro={}
                if post_data['updates']:
                    for key, value in post_data['updates'].items():
                        if key in vars(user).keys():
                            setattr(user, key, value)
                        else:
                            nonupdatedpro[key] = value
                    # print(user)
                db.session.commit()
                user = User.query.filter_by(id=userid).first()
                sectionids = []
                sectionnames = []
                for section in user.sections:
                    sectionids.append(section.sectionid)
                    sectionnames.append(section.sectionname)
                responseObject = {
                    'status': 'Update success',
                    'data': buildreturndata(user, sectionnames, sectionids),
                    'nonupdatedproperty': nonupdatedpro
                }
                resp.data = json.dumps(responseObject)
                return resp, 200
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            resp.data = json.dumps(responseObject)
            return resp, 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            resp.data = json.dumps(responseObject)
            return resp, 500

class LogoutAPI(MethodView):
    """
    Logout Resource
    """
    def post(self):
        # get auth token
        resp = make_response()
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            userid = User.decode_auth_token(auth_token)
            if not isinstance(userid, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # insert the token
                    db.session.add(blacklist_token)
                    db.session.commit()
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    }
                    resp.data = json.dumps(responseObject)
                    return resp, 200
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': e
                    }
                    resp.data = json.dumps(responseObject)
                    return resp, 404
            else:
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                resp.data = json.dumps(responseObject)
                return resp, 500
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            resp.data = json.dumps(responseObject)
            return resp, 403




registration_view = RegisterAPI.as_view('register_api')
login_view = LoginAPI.as_view('login_api')
user_view = UserAPI.as_view('user_api')
logout_view = LogoutAPI.as_view('logout_api')

auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['GET','POST']
)
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)
auth_blueprint.add_url_rule(
    '/auth/userdetails',
    view_func=user_view,
    methods=['GET', 'POST']
)

auth_blueprint.add_url_rule(
    '/auth/logout',
    view_func=logout_view,
    methods=['POST']
)
