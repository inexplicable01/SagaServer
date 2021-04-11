import os
import io
from flask import Flask,flash, request, redirect, url_for,send_from_directory , send_file, make_response, safe_join
from flask_restful import Api, Resource
import zipfile
import shutil

class Reset(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def zipdir(self, folder, ziph):
        # ziph is zipfile handle
        rootdepth = self.rootpath.count(os.path.sep)
        for root, dirs, files in os.walk(os.path.join(self.rootpath,folder)):
            folders = root.split(os.path.sep)
            for file in files:
                ziph.write(os.path.join(root, file),os.path.join(*folders[rootdepth+1:], file))

    def get(self):
        shutil.rmtree(os.path.join(self.rootpath, CONTAINERFOLDER))
        shutil.rmtree(os.path.join(self.rootpath, 'Files'))
        with zipfile.ZipFile(os.path.join(self.rootpath, 'SagaServer.zip'), 'r') as zip_ref:
            zip_ref.extractall(self.rootpath)
        return {"Message": "Succesfully Rebased"}

    def post(self):
        zipf = zipfile.ZipFile(os.path.join(self.rootpath, 'SagaServer.zip'), 'w', zipfile.ZIP_DEFLATED)
        self.zipdir( CONTAINERFOLDER, zipf)
        self.zipdir('Files', zipf)
        zipf.close()
        return {"Message":"Succesfully Saved Zip"}