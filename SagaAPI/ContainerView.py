import os
from flask import request, send_from_directory, safe_join,make_response, jsonify
from flask_restful import Resource
from SagaCore.Container import Container
from SagaCore.Section import Section

from glob import glob
import json
import re

from SagaDB.UserModel import User
from SagaAPI.SagaAPI_Util import authcheck
from flask import current_app
from SagaCore.SagaUtil import getFramePathbyRevnum
from SagaServerOperations.SagaServerContainerOperations import fullFrameHistory

CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class ContainerView(Resource):

    def latestRev(self, path):
        #add comment
        revnum = 0;
        for fn in os.listdir(path):
            m = re.search('Rev(\d+).yaml',fn)
            if  int(m.group(1))>revnum:
                revnum = int(m.group(1))
                latestrev = fn
        return latestrev, revnum

    def __init__(self, appdatadir, sagacontroller):
        self.appdatadir = appdatadir
        self.sagacontroller=sagacontroller

    def get(self, command=None):
        authcheckresult = authcheck(request.headers.get('Authorization'))

        # sectionid = request.form['sectionid']
        if not isinstance(authcheckresult, User):
            responseObject = {
                'status': 'Sign in Failed',
                'message': 'authcheck came back none'
            }
            return make_response(jsonify(responseObject))
        user = authcheckresult
        sectionid = user.currentsection.sectionid
        branch ='Main'
        resp = make_response()
        if command=="containerID":
            containerID = request.form['containerID']
            if os.path.exists(safe_join(self.appdatadir, CONTAINERFOLDER,sectionid, containerID)):
                latestrevfn, revnum = self.latestRev(safe_join(self.appdatadir, CONTAINERFOLDER,sectionid, containerID, branch))
                # result = send_from_directory(safe_join(self.appdatadir, CONTAINERFOLDER,sectionid, containerID), 'containerstate.yaml' )
                cont = self.sagacontroller.provideContainer(sectionid, containerID)

                resp.headers['file_name'] = 'containerstate.yaml'
                resp.headers['branch'] = branch
                resp.headers['revnum'] = str(revnum)
                resp.data = json.dumps({
                    'success':True,  'failmessage':'', 'e':None,
                    "message":'Container Retrieved',
                    'containerdict':  cont.dictify(),
                    'fullframelist': fullFrameHistory(cont), 'revnum':revnum
                })
                return resp
            else:

                sect = Section.LoadSectionyaml(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml'))
                return {"response": "Invalid Container ID" , "searchedSection":sect.dictify()}
        elif command=="List":
            containerinfolist = self.sagacontroller.getContainersBySectionid(sectionid)
            resp.data = json.dumps({'success':True, 'message':"returnlist", 'failmessage':'',
                                    'e':None,'containerinfodict':containerinfolist})
            return resp

        elif command=="tester":
            resp.data=json.dumps({'dicit':'pop','plo':3})
            return resp
        elif command=="fullbranch":
            containerID = request.form['containerID']
            branch = request.form['branch']
            # result = send_from_directory(safe_join(self.appdatadir, CONTAINERFOLDER, containerID, branch), 'Rev1.yaml')
            filepath = safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, containerID, branch)
            resp = make_response()
            resp.data=json.dumps(os.listdir(filepath))
            return resp
        elif command=='newestframeofcontainer':
            ## Provides latest Rev number
            maincontainerid = request.form['containerID']
            sectionid = request.form['sectionid']
            branch = 'Main'#request.form['branch']
            # glob.glob result = send_from_directory(safe_join(self.appdatadir, CONTAINERFOLDER, containerID, branch), 'Rev1.yaml')
            # containeridlist = glob.glob(os.path.join(self.appdatadir, 'Container', sectionid))
            newestframedict= {'framedict':'Container not found',
                                          'newestrevnum':'Container not found'}
            if not os.path.exists(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, maincontainerid, 'containerstate.yaml')):
                resp.data = json.dumps(newestframedict)
                return resp

            cont = self.sagacontroller.provideContainer(sectionid,maincontainerid)
            newestframedict= {'framedict':cont.workingFrame.dictify(),
                                  'newestrevnum':cont.revnum
            }
            resp.data=json.dumps(newestframedict)
            return resp
        elif command=='newestrevnum':
            ## Provides latest Rev number
            sectionid = request.form['sectionid']
            branch = 'Main'#request.form['branch']
            # glob.glob result = send_from_directory(safe_join(self.appdatadir, CONTAINERFOLDER, containerID, branch), 'Rev1.yaml')
            containeridlistpath = glob(os.path.join(self.appdatadir, 'Container', sectionid, '*'))
            latestrevdict= {}
            for containeridpath in containeridlistpath:
                containerid = os.path.basename(containeridpath)
                if not os.path.exists(os.path.join(containeridpath, 'containerstate.yaml')):
                    continue
                framefullpath, latestrevnum = getFramePathbyRevnum(safe_join(containeridpath, 'Main'),0)
                latestrevdict[containerid] = {'newestrevnum':latestrevnum}
            resp.data=json.dumps({'success':True, 'message':'', 'failmessage':'', 'e':None,
                'latestrevdict':latestrevdict,
            })
            return resp
        else:
            resp = make_response()
            resp.headers["response"] = "Incorrect Command"
            return resp






