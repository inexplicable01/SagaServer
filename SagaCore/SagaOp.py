from SagaCore.Container import Container
from SagaCore.Frame import Frame
from datetime import datetime
import os
from flask import safe_join,current_app
from config import typeInput, typeOutput, typeRequired
import uuid
import hashlib
import json

CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class SagaOp():
    def __init__(self):
        self.hi = 'hi'

    def newContainer(self,containerdict,framedict,section_id,files,user,rootpath):
        newcont = Container.LoadContainerFromDict(containerdict=containerdict)
        newcont.workingFrame = Frame.LoadFrameFromDict(framedict)
        newcont.revnum = 1
        committime = datetime.timestamp(datetime.utcnow())
        if os.path.exists(safe_join(rootpath, CONTAINERFOLDER, section_id, newcont.containerId)):
            return {"message":"Container Already exists",
                    "data":None}
        else:
            os.mkdir(safe_join(rootpath, CONTAINERFOLDER, section_id, newcont.containerId))
            os.mkdir(safe_join(rootpath, CONTAINERFOLDER, section_id, newcont.containerId, 'Main'))
            for fileheader, filecon in newcont.FileHeaders.items():
                if filecon['type'] == typeInput:
                    containerid = filecon['Container']
                    upstreamCont = Container.LoadContainerFromYaml(
                        os.path.join(rootpath, CONTAINERFOLDER, section_id, containerid, 'containerstate.yaml'))
                    if type(upstreamCont.FileHeaders[fileheader]['Container']) is list:
                        upstreamCont.FileHeaders[fileheader]['Container'].append(newcont.containerId)
                    else:
                        upstreamCont.FileHeaders[fileheader]['Container'] = [
                            upstreamCont.FileHeaders[fileheader]['Container'], newcont.containerId]
                    upstreamCont.save(environ='Server',
                                      outyamlfn=os.path.join(rootpath, CONTAINERFOLDER, section_id, containerid,
                                                             'containerstate.yaml'))

                    for fileheader in files.keys():
                        print('fileheader' + fileheader)
                        content = files[fileheader].read()
                        newcont.workingFrame.filestrack[fileheader].file_id = uuid.uuid4().__str__()
                        newcont.workingFrame.filestrack[fileheader].md5 = hashlib.md5(content).hexdigest()
                        newcont.workingFrame.filestrack[fileheader].committedby = user.email
                        newcont.workingFrame.filestrack[fileheader].style = 'Required'
                        newcont.workingFrame.filestrack[fileheader].commitUTCdatetime = committime
                        with open(os.path.join(rootpath, FILEFOLDER,
                                               newcont.workingFrame.filestrack[fileheader].file_id),
                                  'wb') as file:
                            file.write(content)
                        # os.unlink(os.path.join(self.rootpath, FILEFOLDER, newframe.filestrack[FileHeader].file_id))

                    newcont.allowedUser.append(user.email)
                    newcont.save(environ='Server',
                                 outyamlfn=safe_join(rootpath, CONTAINERFOLDER, section_id, newcont.containerId,
                                                     'containerstate.yaml'))
                    newcont.workingFrame.commitUTCdatetime = committime
                    newcont.workingFrame.FrameInstanceId = uuid.uuid4().__str__()
                    newcont.workingFrame.writeoutFrameYaml( \
                        safe_join(rootpath, CONTAINERFOLDER, section_id, newcont.containerId, 'Main', 'Rev1.yaml'))


                    return {"message":"Container Made",
                            "data":json.dumps(
                        {'containerdictjson': newcont.dictify(),
                         'framedictjson': newcont.workingFrame.dictify()})
                    }