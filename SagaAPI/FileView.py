import os
import io
from flask import Flask,flash, request, redirect, url_for,send_from_directory , send_file, make_response, safe_join
from flask_restful import Api, Resource
from flask import current_app
FILEFOLDER = current_app.config['FILEFOLDER']


class FileView(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def get(self):
        file_id = request.form['file_id']
        file_name=request.form['file_name']
        if os.path.exists(safe_join(self.rootpath,FILEFOLDER,file_id)):
            result = send_from_directory(safe_join(self.rootpath,FILEFOLDER),file_id)
            result.headers['file_name'] = file_name
            return result
        else:
            return {"response": "Invalid file ID  "+file_id}

    # def post(self):
    #
    #     try:
    #         for fileheader in request.files.keys():
    #             content = request.files[fileheader].read()
    #             with open(os.path.join(self.rootpath, FILEFOLDER, fileheader),
    #                       'wb') as file:
    #                 file.write(content)
    #         return {"response":"Success"}
    #     except Exception as e:
    #         return {"response":"fail"}