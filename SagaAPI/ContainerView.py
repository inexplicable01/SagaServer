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

    def __init__(self, appdatadir):
        self.appdatadir = appdatadir

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
                cont = Container.LoadContainerFromYaml(safe_join(self.appdatadir, CONTAINERFOLDER,sectionid, containerID, 'containerstate.yaml'))
                resp.headers['file_name'] = 'containerstate.yaml'
                resp.headers['branch'] = branch
                resp.headers['revnum'] = str(revnum)
                resp.data = json.dumps({
                    'containerdict':  cont.dictify(),
                    'fullframelist':cont.fullFrameHistory(),
                })
                return resp
            else:

                sect = Section.LoadSectionyaml(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml'))
                return {"response": "Invalid Container ID" , "searchedSection":sect.dictify()}
        elif command=="List":
            containerinfolist = {}
            for containerid in os.listdir(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid)):
                if not os.path.exists(safe_join(self.appdatadir, CONTAINERFOLDER,sectionid,containerid,'containerstate.yaml')):
                    continue
                curcont = Container.LoadContainerFromYaml(safe_join(self.appdatadir, CONTAINERFOLDER,sectionid,containerid,'containerstate.yaml'))
                containerinfolist[containerid] = {'ContainerDescription': curcont.containerName,
                                         'branches':[],
                                                  'containerdict':curcont.dictify()}
                for branch in os.listdir(safe_join(self.appdatadir, CONTAINERFOLDER,sectionid,containerid)):
                    if os.path.isdir(safe_join(self.appdatadir, CONTAINERFOLDER,sectionid,containerid,branch)):
                        containerinfolist[containerid]['branches'].append({'name': branch,
                                                                    'revcount':len(glob(safe_join(self.appdatadir, CONTAINERFOLDER,sectionid,containerid,branch,'*')))})

            resp.headers["response"] = "returnlist"
            resp.data = json.dumps(containerinfolist)
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
        elif command=='newestrevnum':
            ## Provides latest Rev number
            containerID = request.form['containerID']
            branch = 'Main'#request.form['branch']
            # result = send_from_directory(safe_join(self.appdatadir, CONTAINERFOLDER, containerID, branch), 'Rev1.yaml')
            for section in user.sections:
                filepath = safe_join(self.appdatadir, CONTAINERFOLDER, section.sectionid, containerID, 'containerstate.yaml')
                if os.path.exists(filepath):
                    cont = Container.LoadContainerFromYaml(filepath)
                    print(cont.revnum)
                    resp.data=json.dumps({'framedict':cont.workingFrame.dictify(),
                                          'newestrevnum':cont.revnum})
                    return resp

            resp.data=json.dumps({'framedict':'Container not found',
                                          'newestrevnum':'Container not found'})
            return resp
        else:
            resp = make_response()
            resp.headers["response"] = "Incorrect Command"
            return resp






