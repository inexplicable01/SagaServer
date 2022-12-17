from SagaCore.Container import Container
from SagaCore.Frame import Frame
from datetime import datetime
import os
from os.path import join
from flask import current_app
from SagaCore import *
from flask import safe_join

import uuid
import json
import re
import traceback
import warnings
from SagaServerOperations.MailSender import MailSender
# from SagaServerOperations.SagaServerContainerOperations import ContainerServerSave
Rev='Rev'
CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']


class SagaServerModel():
    def __init__(self,appdatadir):
        self.appdatadir = appdatadir
        # self.mail = Mail(current_app)

    def commitNewFrame(self,curcont:Container,framedict,containerdict,user,sectionid, commitmsg ,updateinfo,files, newrevnum,savenewcont, branch='Main'):
        newcont = Container.LoadVirtualContainer(framedict, containerdict)
        committime = datetime.timestamp(datetime.utcnow())
        # commitframe = Frame.LoadFrameFromDict(framedict)
        # # mailsender = MailSender()
        newRev = Rev + str(newrevnum)
        updatedfiles = {}
        try:
            for md5 in files.keys():
                citemid = updateinfo[md5]['citemid']
                track = newcont.refframe.filestrack[citemid]
                track.committedby = user.email
                track.lastupdated = newRev
                track.commitUTCdatetime = committime

                content = files[md5].read()
                with open(os.path.join(self.appdatadir, FILEFOLDER, md5), 'wb') as file:
                    file.write(content)

                if track.containeritemrole == roleOutput:
                    for downcontainerid in newcont.containeritems[citemid].refcontainerid:
                        downstreamcont = self.provideContainer(sectionid,downcontainerid)
                        self.mailsender.prepareMailDownstream(recipemail=downstreamcont.allowedUser,
                                               fileheader=citemid,
                                               filetrack=track, user=user, upcont=curcont,
                                               commitmsg=commitmsg,
                                               committime=committime,
                                               newrevnum=newrevnum)
                # md5keys.remove(md5)
                updatedfiles[citemid]=track

            # for newfiles in md5keys:
            #     print('Add a FileTrack to frameRef.filestrack for ' + newfiles)
            newcont.refframe.FrameInstanceId = uuid.uuid4().__str__()
            newcont.refframe.commitMessage = commitmsg
            newcont.refframe.commitUTCdatetime = committime
            newcont.refframe.FrameName = newRev
            newrevfn = newRev + ".yaml"
            newframefullpath = os.path.join(self.appdatadir, CONTAINERFOLDER, sectionid, curcont.containerId, branch, newrevfn)

        except Exception as e:
            return False, None,None,None,None,None,{ 'message': 'Error occured while dealing with new frame and new files.',
                    'error': e
                    }

        try:
            curcont.save(environ='Server',
                         outyamlfn = safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, curcont.containerId,
                                   'containerstate_' + str(datetime.utcnow().timestamp()) +'.yaml'))###Create a backup of old container.
            if savenewcont:
                newcont.save(environ='Server',
                             outyamlfn=safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, curcont.containerId, 'containerstate.yaml'))
            newcont.refframe.writeoutFrameYaml(fn=newframefullpath, authorized=True)
        except Exception as e:
            if os.path.exists(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, curcont.containerId, 'containerstate.yaml')):
                os.remove(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, curcont.containerId, 'containerstate.yaml'))
            return False,{'message': 'Error occured while saving new Frames Yaml.   Commit is canceled, and all operations are reversed.',
                    'error': e
            }

        return True,newframefullpath,newrevfn,updatedfiles,newcont,committime, None



