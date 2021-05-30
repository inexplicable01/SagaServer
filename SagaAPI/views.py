from flask.views import MethodView
from flask import Blueprint, request, make_response, jsonify

from SagaAPI import db
# from SagaApp.db import get_db
from SagaDB.UserModel import User,BlacklistToken, UserSections

from SagaCore.Section import Section
from flask import current_app
import os
from Config import basedir,worldmapid

auth_blueprint = Blueprint('auth', __name__)
CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
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
            return make_response(jsonify(responseObject)), 401

        # if 'sectionname' in request.form.keys():
        #     ## User wants to make a new section
        #     section_name = request.form['sectionname']
        #     description = request.form['sectiondescription']
        #     newsection = Section.CreateNewSection(section_name, description=description)
        #     sectionid = newsection.sectionid
        #     section_name = newsection.sectionname
        #
        # elif 'sectionid' in request.form.keys():
        #     sectionid = request.form['sectionid']
        #     sectionyaml = os.path.join(basedir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml')
        #     cursection = Section.LoadSectionyaml(sectionyaml)
        #     section_name = cursection.sectionname
        # else:
        #     responseObject = {
        #         'status': 'fail',
        #         'message': 'Section definitions were not done well '
        #     }
        #     return make_response(jsonify(responseObject)), 401
        ## this is not consistent with the website registration, additional work is needed for better seperation of concern
        sectionid = worldmapid
        sectionyaml = os.path.join(basedir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml')
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
                    sectionname=section_name,
                    sectionid=sectionid,
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
                    'useremail': user.email,
                    'first_name': user.first_name,
                    'current_sectionname': user.currentsection.sectionname,
                    'current_sectionid': user.currentsection.sectionid,
                    'sectionname_list': sectionnames,
                    'sectionid_list': sectionids,
                    'last_name': user.last_name,
                    'exptimestamp':exptimestamp
                }
                # print('exp' + exptimestamp)
                return make_response(jsonify(responseObject)), 201
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': str(e) + ' Please try again.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User already exists. Please Log in.',
            }
            return make_response(jsonify(responseObject)), 202

class LoginAPI(MethodView):
    """
    User Login Resource
    """
    def post(self):
        # get the post data
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
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token.decode(),
                        'useremail': user.email,
                        'first_name': user.first_name,
                        'current_sectionname': user.currentsection.sectionname,
                        'current_sectionid': user.currentsection.sectionid,
                        'sectionname_list':sectionnames,
                        'sectionid_list': sectionids,
                        'last_name': user.last_name,
                        'exptimestamp':exptimestamp
                    }
                    # print('exp' + exptimestamp)
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User does not exist.'
                }
                return make_response(jsonify(responseObject)), 404
        except Exception as e:
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(responseObject)), 500

class UserAPI(MethodView):
    """
    User Resource
    """
    def get(self):
        # get the auth token
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
                sectionids = []
                sectionnames = []
                for section in user.sections:
                    sectionids.append(section.sectionid)
                    sectionnames.append(section.sectionname)
                responseObject = {
                    'status': 'success',
                    'data': {
                        'user_id': user.id,
                        'email': user.email,
                        'admin': user.admin,
                        'registered_on': user.registered_on,
                        'first_name': user.first_name,
                        'current_sectionname': user.currentsection.sectionname,
                        'current_sectionid': user.currentsection.sectionid,
                        'sectionname_list':sectionnames,
                        'sectionid_list': sectionids,
                        'last_name': user.last_name
                    }
                }
                return make_response(jsonify(responseObject)), 200
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
            return make_response(jsonify(responseObject)), 401

    def post(self):
        auth_header = request.headers.get('Authorization')
        post_data = request.get_json()
        # if 'email' in post_data.keys():
        #     email = post_data.get('email')
        #     password = post_data.get('password')
        # else:
        #     email = request.form['email']
        #     password = request.form['password']
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
                nonupdatedpro={}
                if post_data['updates']:
                    for key, value in post_data['updates'].items():
                        if key in vars(user).keys():
                            setattr(user, key, value)
                        else:
                            nonupdatedpro[key] = value
                    # print(user)
                db.session.commit()
                user = User.query.filter_by(id=resp).first()
                sectionids = []
                sectionnames = []
                for section in user.sections:
                    sectionids.append(section.sectionid)
                    sectionnames.append(section.sectionname)
                responseObject = {
                    'status': 'Update success',
                    'data': {
                        'user_id': user.id,
                        'email': user.email,
                        'admin': user.admin,
                        'registered_on': user.registered_on,
                        'first_name': user.first_name,
                        'current_sectionname': user.currentsection.sectionname,
                        'current_sectionid': user.currentsection.sectionid,
                        'sectionname_list':sectionnames,
                        'sectionid_list': sectionids,
                        'last_name': user.last_name
                    },
                    'nonupdatedproperty': nonupdatedpro
                }
                return make_response(jsonify(responseObject)), 200
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
            return make_response(jsonify(responseObject)), 401

class LogoutAPI(MethodView):
    """
    Logout Resource
    """
    def post(self):
        # get auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
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
                    return make_response(jsonify(responseObject)), 200
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': e
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
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
            return make_response(jsonify(responseObject)), 403




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
