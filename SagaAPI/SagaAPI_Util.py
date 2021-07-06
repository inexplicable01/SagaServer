from flask import make_response, jsonify
import json
from SagaDB.UserModel import User

def authcheck(auth_header):
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
        decoderesponse = User.decode_auth_token(auth_token)
        if not isinstance(decoderesponse, str):
            user = User.query.filter_by(id=decoderesponse).first()
            if user:
                return user
        responseObject = {
            'status': 'fail',
            'message': decoderesponse
        }
        return make_response(jsonify(responseObject)), 401
    else:
        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return make_response(jsonify(responseObject)), 401

