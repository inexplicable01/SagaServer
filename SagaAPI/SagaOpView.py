import os
from flask import request, send_from_directory, safe_join,make_response,jsonify
from flask_restful import Resource
from SagaCore.Container import Container
from SagaDB.UserModel import User
from flask import current_app
import json
from Config import typeInput, typeOutput, typeRequired
from SagaAPI.SagaAPI_Util import authcheck
from SagaCore.Frame import Frame
import shutil
from datetime import datetime
import traceback
from SagaCore.SagaOp import SagaOp

Rev='Rev'
CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class SagaOperationsView(Resource):

    def __init__(self, appdatadir):
        self.appdatadir = appdatadir
        self.sagaop = SagaOp(appdatadir)

    def post(self, command=None):
        authcheckresult = authcheck(request.headers.get('Authorization'))

        if not isinstance(authcheckresult, User):
            (resp, num) = authcheckresult
            return resp, num
            # return resp, num # user would be a type of response if its not the actual class user
        user = authcheckresult
        sectionid = user.currentsection.sectionid
        try:
            resp = make_response()
            if command == "newContainer":
                containerdict = json.loads(request.form['containerdictjson'])
                framedict = json.loads(request.form['framedictjson'])
                result = self.sagaop.newContainer(containerdict,framedict,sectionid,request.files,user)

                resp.headers["response"] = result["message"]
                if result["data"]:
                    resp.data = result["data"]
                return resp

            elif command == "commit":
                containerID = request.form.get('containerID')
                branch = request.form['branch']
                updateinfo = json.loads(request.form['updateinfo'])
                commitmsg = request.form['commitmsg']
                curcont = Container.LoadContainerFromYaml(
                    safe_join(self.appdatadir, CONTAINERFOLDER,  sectionid, containerID, 'containerstate.yaml'), sectionid)
                # containerdict = json.loads(request.form['containerdictjson'])
                # newcont = Container.LoadContainerFromDict(containerdict)
                if user.email not in curcont.allowedUser:
                    responseObject = {
                            'status': 'fail',
                            'message': 'User  is not allowed to commit to this Container'
                        }
                    return make_response(jsonify(responseObject)), 401
                containerdict= json.loads(request.form['containerdictjson'])
                newcont = Container.LoadContainerFromDict(containerdict=containerdict, environ='Server', sectionid=sectionid)
                framedict = json.loads(request.form['framedictjson'])
                commitframe = Frame.LoadFrameFromDict(framedict)
                # mailsender = MailSender()
                commitreport = self.sagaop.commit(curcont,newcont, user , sectionid, commitframe, commitmsg, updateinfo, request.files)

                if commitreport['commitsuccess']:
                    commitresponse = send_from_directory(
                        safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, curcont.containerId, branch),
                        commitreport['newrevfn'])
                    commitresponse.headers['file_name'] = commitreport['newrevfn']
                    commitresponse.headers['branch'] = 'Main'
                    commitresponse.headers['commitsuccess'] = commitreport['commitsuccess']
                    return commitresponse
                else:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Commit Failed'
                    }
                    return make_response(jsonify(responseObject))


            elif command == "deleteContainer":
                    containerId = request.form['containerId']
                    delCont = Container.LoadContainerFromYaml(
                        os.path.join(self.appdatadir, CONTAINERFOLDER, sectionid, containerId, 'containerstate.yaml'))

                    if user.email not in delCont.allowedUser:
                        responseObject = {
                            'status': 'fail',
                            'message': 'User  is not allowed to commit to this Container'
                        }
                        return make_response(jsonify(responseObject)), 401

                    if os.path.exists(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid,containerId)):
                        for fileheader, filecon in delCont.FileHeaders.items():
                            if filecon['type'] == typeOutput:
                                for containerid in filecon['Container']:
                                    downstreamCont = Container.LoadContainerFromYaml(
                                        os.path.join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid,
                                                     'containerstate.yaml'))
                                    downstreamCont.FileHeaders.pop(fileheader, None)
                                    downstreamCont.save(environ='Server',
                                                        outyamlfn=os.path.join(self.appdatadir, CONTAINERFOLDER, sectionid,
                                                                               containerid, 'containerstate.yaml'))
                            elif filecon['type'] == typeInput:
                                containerid = filecon['Container']
                                upstreamcont = Container.LoadContainerFromYaml(
                                    os.path.join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid,
                                                 'containerstate.yaml'))
                                if delCont.containerId in upstreamcont.FileHeaders[fileheader]['Container']:
                                    upstreamcont.FileHeaders[fileheader]['Container'].remove(delCont.containerId)

                                upstreamcont.save(environ='Server',
                                                  outyamlfn=os.path.join(self.appdatadir, CONTAINERFOLDER, sectionid,
                                                                         containerid,
                                                                         'containerstate.yaml'))

                        resp.headers["response"] = "I'm gonna delete this"
                        resp.data = 'Deleted'
                        shutil.rmtree(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, containerId))
                        return resp
                    else:
                        resp.headers["response"] = "Container " + containerId + " doesn't exist"
                        return resp
        except Exception as e:
            with open('commitError.txt','a+') as errorfile:
                # errorfile.write(datetime.utcnow().isoformat() + ': Container: ' + request.form.get('containerID') +'\n')
                errorfile.write(datetime.utcnow().isoformat() + str(e)+'\n')
                errorfile.write(datetime.utcnow().isoformat() + 'ErrorType' + str(e)+'\n')
                errorfile.write(datetime.utcnow().isoformat() + 'Tracebacj' + traceback.format_exc() + '\n')
                errorfile.write('\n')
            responseObject = {
                'status': 'fail',
                'message': str(e),
                'ErrorType':str(e),
                'traceback': traceback.format_exc()
            }

            return make_response(jsonify(responseObject))
