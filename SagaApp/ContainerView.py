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

    def latestRev(self, path):
        rev = 0;
        for fn in os.listdir(path):
            m = re.search('Rev(\d+).yaml',fn)
            if  int(m.group(1))>rev:
                revnum = int(m.group(1))
                latestrev = fn
        return latestrev, revnum

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def get(self):
        containerID = request.form['containerID']
        branch ='Main'

        if os.path.exists(safe_join(self.rootpath, 'Container', containerID)):
            latestrevfn, revnum = self.latestRev(safe_join(self.rootpath, 'Container', containerID, branch))
            result = send_from_directory(safe_join(self.rootpath, 'Container', containerID), 'containerstate.yaml' )
            result.headers['file_name'] = 'containerstate.yaml'
            result.headers['branch'] = branch
            result.headers['revnum'] = str(revnum)
            return result
        else:
            return {"response": "Invalid Container ID"}

    def post(self):
        # command = request.form['command']
        return {"blah":"blah"}