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


class Files(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def get(self):
        file_id = request.form['file_id']
        file_name=request.form['file_name']
        if os.path.exists(safe_join(self.rootpath,'Files',file_id)):
            result = send_from_directory(safe_join(self.rootpath,'Files'),file_id)
            result.headers['file_name'] = file_name
            return result
        else:
            return {"response": "Invalid file ID  "+file_id}

    def post(self):
        return {"blah":"blah"}