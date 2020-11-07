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
import uuid
import yaml
from datetime import datetime
from SagaApp.Frame import Frame
Rev = 'Rev'

class FrameView(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def latestRev(self, path):
        rev = 0;
        for fn in os.listdir(path):
            m = re.search('Rev(\d+).yaml',fn)
            if  int(m.group(1))>rev:
                revnum = int(m.group(1))
                latestrev = fn
        return latestrev, revnum


    def get(self):
        print(self.rootpath)
        containerID = request.form['containerID']
        branch = request.form['branch']

        if os.path.exists(safe_join(self.rootpath,'Container',containerID)):
            if os.path.exists(safe_join(self.rootpath,'Container',containerID, branch)):
                latestrevfn, revnum = self.latestRev(safe_join(self.rootpath,'Container', containerID, branch))
                result = send_from_directory(safe_join(self.rootpath,'Container', containerID, branch),latestrevfn)
                result.headers['file_name'] = latestrevfn
                result.headers['branch'] = branch
                return result
            else:
                latestrevfn, revnum = self.latestRev(safe_join(self.rootpath,'Container', containerID, 'Main'))
                result = send_from_directory(safe_join(self.rootpath,'Container', containerID, 'Main'),latestrevfn)
                result.headers['file_name'] = latestrevfn
                result.headers['branch'] = 'Main'
                return result
        else:
            return {"response": "Invalid Container ID"}

    def post(self):
        containerID=request.form['containerID']
        branch = request.form['branch']
        updateinfo = json.loads(request.form['updateinfo'])
        commitmsg = request.form['commitmsg']
        latestrevfn, revnum = self.latestRev(safe_join(self.rootpath, 'Container', containerID, branch))
        refframe = os.path.join(self.rootpath, 'Container', containerID, branch, latestrevfn)

        with open(refframe) as file:
            frameRefYaml = yaml.load(file, Loader=yaml.FullLoader)
        frameRef = Frame(frameRefYaml,None)
        print(frameRef)
        committime = datetime.timestamp(datetime.utcnow())
        for ContainerObjName, filetrackobj in frameRef.filestrack.items():
            if ContainerObjName in request.files.keys():
                # print(ContainerObjName)
                # print(filetrackobj)
                filetrackobj.md5= updateinfo[ContainerObjName]['md5']
                filetrackobj.file_name = updateinfo[ContainerObjName]['file_name']
                filetrackobj.lastEdited = updateinfo[ContainerObjName]['lastEdited']
                filetrackobj.style = updateinfo[ContainerObjName]['style']
                filetrackobj.file_id = uuid.uuid4().__str__()
                filetrackobj.commitUTCdatetime = committime
                request.files[ContainerObjName].save(os.path.join(self.rootpath, 'Files', filetrackobj.file_id))

                # print(filetrackobj.file_name)
                # print(request.files[filetrackobj.file_name])

        frameRef.FrameInstanceId = uuid.uuid4().__str__()
        frameRef.commitMessage = commitmsg
        frameRef.commitUTCdatetime = committime
        frameRef.FrameName = Rev + str(revnum+1)
        newrevfn = Rev + str(revnum+1) + ".yaml"
        newframefullpath =  os.path.join(self.rootpath, 'Container', containerID, branch, newrevfn)
        frameRef.writeoutFrameYaml(newframefullpath)

        result = send_from_directory(safe_join(self.rootpath, 'Container', containerID, 'Main'), newrevfn)
        result.headers['file_name'] = newrevfn
        result.headers['branch'] = 'Main'
        result.headers['commitsuccess'] = True
        return result