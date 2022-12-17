import os
from flask import request, send_from_directory, safe_join,make_response,jsonify
from flask_restful import Resource
from SagaCore.Container import Container
from SagaDB.UserModel import User
from flask import current_app
import json
# from Config import roleInput, roleOutput, roleRequired
from SagaAPI.SagaAPI_Util import authcheck
from SagaCore.Frame import Frame
import shutil
from datetime import datetime
import traceback


Rev='Rev'
CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class PingView(Resource):

    def __init__(self, appdatadir, webserverdir,sagauserdb, sagacontroller):
        self.appdatadir = appdatadir
        self.webserverdir=webserverdir
        self.sagauserdb= sagauserdb
        self.sagacontroller = sagacontroller

    def post(self, command=None):

        authcheckresult = authcheck(request.headers.get('Authorization'))

        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            return resp, num
            # return resp, num # user would be a type of response if its not the actual class user
        user = authcheckresult
        sectionid = user.currentsection.sectionid

        if command=='PingContainerToUpdateInputs':
            fileheader = request.form['fileheader']
            upstreamcontid = request.form['downstreamcontainerid']
            downstreamid = request.form['upstreamcontainerid']
            upstreamcont = self.sagacontroller.provideContainer(sectionid,upstreamcontid)
            downstreamcont = self.sagacontroller.provideContainer(sectionid,downstreamid)
            self.sagacontroller.PingDownstreamContainerToUpdateInputs( fileheader=fileheader,
                                                                downstreamcont=downstreamcont ,
                                                               curcont=upstreamcont, user=user, filetrack=upstreamcont.refframe.filestrack[fileheader],
                                                               commitmsg=upstreamcont.refframe.commitMessage,
                                                               committime = upstreamcont.refframe.commitUTCdatetime)