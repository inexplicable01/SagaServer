import os
from flask import request, send_from_directory, safe_join,make_response
from flask_restful import Resource
from SagaApp.Container import Container
from glob import glob
import json
import re


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

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def get(self, command=None):

        branch ='Main'

        if command=="containerID":
            containerID = request.form['containerID']
            if os.path.exists(safe_join(self.rootpath, 'Container', containerID)):
                latestrevfn, revnum = self.latestRev(safe_join(self.rootpath, 'Container', containerID, branch))
                result = send_from_directory(safe_join(self.rootpath, 'Container', containerID), 'containerstate.yaml' )
                result.headers['file_name'] = 'containerstate.yaml'
                result.headers['branch'] = branch
                result.headers['revnum'] = str(revnum)
                return result
            else:
                return {"response": "Invalid Container ID"}
        elif command=="List":
            resp = make_response()
            containerinfolist = {}
            for containerid in os.listdir(safe_join(self.rootpath, 'Container')):
                curcont = Container(safe_join(self.rootpath, 'Container',containerid,'containerstate.yaml'))
                containerinfolist[containerid] = {'ContainerDescription': curcont.containerName,
                                         'branches':[]}
                for branch in os.listdir(safe_join(self.rootpath, 'Container',containerid)):
                    if os.path.isdir(safe_join(self.rootpath, 'Container',containerid,branch)):
                        containerinfolist[containerid]['branches'].append({'name': branch,
                                                                    'revcount':len(glob(safe_join(self.rootpath, 'Container',containerid,branch,'*')))})



            resp.headers["response"] = "returnlist"
            resp.headers["containerinfolist"] = json.dumps(containerinfolist)
            return resp
        else:
            resp = make_response()
            resp.headers["response"] = "Incorrect Command"
            return resp

    def post(self):
        # command = request.form['command']
        return {"blah":"blah"}