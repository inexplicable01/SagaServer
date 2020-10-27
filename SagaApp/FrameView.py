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


class FrameView(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def latestRev(self, path):
        rev = 0;
        for fn in os.listdir(path):
            m = re.search('Rev(\d+).yaml',fn)
            if  int(m.group(1))>rev:
                rev = int(m.group(1))
                latestrev = fn
        return latestrev


    def get(self):
        print(self.rootpath)
        containerID = request.form['containerID']
        branch = request.form['branch']

        if os.path.exists(safe_join(self.rootpath,'Container',containerID)):
            if os.path.exists(safe_join(self.rootpath,'Container',containerID, branch)):
                latestrevfn = self.latestRev(safe_join(self.rootpath,'Container', containerID, branch))
                result = send_from_directory(safe_join(self.rootpath,'Container', containerID, branch),latestrevfn)
                result.headers['file_name'] = latestrevfn
                result.headers['branch'] = branch
                return result
            else:
                latestrevfn = self.latestRev(safe_join(self.rootpath,'Container', containerID, 'Main'))
                result = send_from_directory(safe_join(self.rootpath,'Container', containerID, 'Main'),latestrevfn)
                result.headers['file_name'] = latestrevfn
                result.headers['branch'] = 'Main'
                return result
        else:
            return {"response": "Invalid Container ID"}

    def post(self):
        return {"blah":"blah"}