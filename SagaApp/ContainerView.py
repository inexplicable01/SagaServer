import os
import io
from flask import Flask,flash, request, redirect, url_for,send_from_directory , send_file, make_response, safe_join
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import json
import gridfs
import re


class ContainerView(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def get(self):
        containerID = request.form['containerID']

        if os.path.exists(safe_join(self.rootpath, 'Container', containerID)):
            result = send_from_directory(safe_join(self.rootpath, 'Container', containerID), 'containerstate.yaml' )
            result.headers['file_name'] = 'containerstate.yaml'
            return result
        else:
            return {"response": "Invalid Container ID"}

    def post(self):
        # command = request.form['command']
        return {"blah":"blah"}