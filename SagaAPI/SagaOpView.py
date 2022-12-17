import os
from flask import request, send_from_directory, safe_join,make_response,jsonify
from flask_restful import Resource
from SagaCore.Container import Container
from SagaDB.UserModel import User
from flask import current_app
import json
from SagaCore import roleInput, roleOutput, roleRequired
from SagaAPI.SagaAPI_Util import authcheck
# from SagaCore.Frame import Frame
import shutil
from datetime import datetime
import traceback

# from SagaServerOperations.SagaServerContainerOperations import ContainerServerSave

Rev='Rev'
CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class SagaOperationsView(Resource):

    def __init__(self, appdatadir, sagacontroller):
        self.appdatadir = appdatadir
        self.sagacontroller = sagacontroller

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
                updateinfo = json.loads(request.form['updateinfo'])
                message, containerdict, framedict = self.sagacontroller.newContainerToModel(containerdict,framedict,sectionid,request.files,user,updateinfo)
                resp.data = json.dumps({
                        'success':True,
                        'message':message,
                        'failmessage':'',
                        'e':None,
                        'containerdictjson':containerdict,
                        'framedictjson':framedict,
                    })
                return resp

            elif command == "commit":
                containerid = request.form.get('containerID')
                branch = request.form['branch']
                updateinfo = json.loads(request.form['updateinfo'])
                commitmsg = request.form['commitmsg']
                containerdict= json.loads(request.form['containerdictjson'])
                framedict = json.loads(request.form['framedictjson'])

                success, commitreport = self.sagacontroller.commitNextFrameToModel(containerid,framedict,containerdict, user , sectionid, commitmsg, updateinfo, request.files)

                if success:
                    # commitresponse = send_from_directory(
                    #     safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid, branch),
                    #     commitreport['newrevfn'])
                    resp.data = json.dumps({
                        'success':success,
                        'yamlframefn': commitreport['newrevfn'],
                        'framecontent': commitreport['framecontent'],
                        'message':'', 'failmessage':'', 'e':None
                    })
                    return resp
                else:
                    resp.data = json.dumps({
                        'success':False,
                        'yamlframefn': commitreport['newrevfn'],
                        'framecontent': commitreport['framecontent'],
                        'message': '', 'failmessage': '', 'e': None
                    })
                    return resp, 401

            elif command == "makechildcontainer":
                parentcontainerid = request.form.get('parentcontainerid')
                childcontaineritemrole = request.form.get('childcontaineritemrole')
                childcontainername = request.form.get('childcontainername')
                childcontainerdescription= request.form.get('childcontainerdescription')

                self.sagacontroller.createChildContainer(sectionid,parentcontainerid,
                                                 childcontaineritemrole, childcontainername,
                                                 childcontainerdescription)
            elif command == "deleteContainer":
                    containerId = request.form['containerId']
                    delCont = self.sagacontroller.provideContainer(sectionid,containerId)
                    if user.email not in delCont.allowedUser:
                        responseObject = {
                            'status': 'fail',
                            'message': 'User  is not allowed to commit to this Container'
                        }
                        return make_response(jsonify(responseObject)), 401

                    if os.path.exists(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid,containerId)):
                        for fileheader, filecon in delCont.FileHeaders.items():
                            if filecon['type'] == roleOutput:
                                for containerid in filecon['Container']:
                                    downstreamCont = self.sagacontroller.provideContainer(sectionid,containerid)
                                    downstreamCont.FileHeaders.pop(fileheader, None)
                                    downstreamCont.save(environ='Server',
                                                        outyamlfn=os.path.join(self.appdatadir, CONTAINERFOLDER, sectionid,
                                                                               containerid, 'containerstate.yaml'))
                            elif filecon['type'] == roleInput:
                                containerid = filecon['Container']
                                upstreamcont = self.sagacontroller.provideContainer(sectionid,containerid)
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
                'success': 'fail',
                'message': str(e),
                'traceback': traceback.format_exc(),
                'failmessage':'Failed!', 'e':e
            }

            return make_response(jsonify(responseObject))
