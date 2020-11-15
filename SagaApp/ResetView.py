import os
import io
from flask import Flask,flash, request, redirect, url_for,send_from_directory , send_file, make_response, safe_join
from flask_restful import Api, Resource
import zipfile
import shutil

class Reset(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def zipdir(self,path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))

    def get(self):
        shutil.rmtree(os.path.join(self.rootpath, 'Container'))
        shutil.rmtree(os.path.join(self.rootpath, 'Files'))
        with zipfile.ZipFile('SagaServer.zip', 'r') as zip_ref:
            zip_ref.extractall(self.rootpath)

    def post(self):
        zipf = zipfile.ZipFile('SagaServer.zip', 'w', zipfile.ZIP_DEFLATED)
        self.zipdir(os.path.join(self.rootpath, 'Container'), zipf)
        self.zipdir(os.path.join(self.rootpath, 'Files'), zipf)
        zipf.close()
        return {"Message":"Succesfully Rebased"}