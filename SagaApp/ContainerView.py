import os
from flask import request, send_from_directory, safe_join,make_response
from flask_restful import Resource
from SagaApp.Container import Container
from SagaApp.Frame import Frame
from glob import glob
import json
import re
import shutil
import uuid
import hashlib
from datetime import datetime


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

    def post(self, command=None):

        branch = 'Main'
        # command = request.form['command']
        resp = make_response()
        resp.headers["response"] = "Incorrect Command"
        if command=="newContainer":
            containerdict = json.loads(request.form['containerdictjson'])
            # newcont = Container()
            newcont = Container('containerstate.yaml',containerdict=containerdict)
            framedict = json.loads(request.form['framedictjson'])
            newframe = Frame(framedict, 'Container/specialsauce/Main/')
            committime = datetime.timestamp(datetime.utcnow())

            if os.path.exists(safe_join(self.rootpath, 'Container', newcont.containerId)):
                resp.headers["response"] = "Container Already exists"
                return resp
            else:
                os.mkdir(safe_join(self.rootpath, 'Container', newcont.containerId))
                os.mkdir(safe_join(self.rootpath, 'Container', newcont.containerId,'Main'))

                for ContainerObjName in request.files.keys():
                    content = request.files[ContainerObjName].read()
                    newframe.filestrack[ContainerObjName].file_id = uuid.uuid4().__str__()
                    newframe.filestrack[ContainerObjName].md5 = hashlib.md5(content).hexdigest()
                    # filetrackobj.committedby = user.email
                    newframe.filestrack[ContainerObjName].style = 'Required'
                    newframe.filestrack[ContainerObjName].commitUTCdatetime = committime
                    with open(os.path.join(self.rootpath, 'Files', newframe.filestrack[ContainerObjName].file_id),
                              'wb') as file:
                        file.write(content)

                    os.unlink(os.path.join(self.rootpath, 'Files', newframe.filestrack[ContainerObjName].file_id))

                newcont.save(environ='Server',
                             outyamlfn=safe_join(self.rootpath, 'Container', newcont.containerId,'containerstate.yaml'))
                newframe.writeoutFrameYaml( \
                    safe_join(self.rootpath, 'Container', newcont.containerId,'Main','Rev1.yaml'))


                resp.headers["response"] = "Container Made"
                return resp
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

    def delete(self, command=None):
        resp = make_response()
        resp.headers["response"] = "Delete Response"
        if command=="deleteContainer":
            containerId = request.form['containerId']
            # newcont = Container()
            # newcont = Container('containerstate.yaml',containerdict=containerdict)
            if os.path.exists(safe_join(self.rootpath, 'Container', containerId)):
                resp.headers["response"] = "I'm gonna delete this"
                shutil.rmtree(safe_join(self.rootpath, 'Container', containerId))
                return resp
            else:
                resp.headers["response"] = "Container " + containerId + " doesn't exist"
                return resp
        return resp
