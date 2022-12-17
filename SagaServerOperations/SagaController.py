from SagaCore.Container import Container
from SagaCore.Section import Section
from SagaCore.Frame import Frame
from datetime import datetime
import os
from os.path import join
from flask import current_app
from SagaCore import roleInput,roleRequired,roleOutput,CONTAINERFN
from flask import safe_join
from SagaDB.UserModel import User, SectionDB, db, UserSections
import uuid
import json
import re
import traceback
import warnings
from SagaServerOperations.MailSender import MailSender
from SagaServerOperations.SagaServerModel import SagaServerModel
# from SagaServerOperations.SagaServerContainerOperations import ContainerServerSave
Rev='Rev'
CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

def writeError(e, errmessage):
    with open('commitError.txt', 'a+') as errorfile:
        # errorfile.write(datetime.utcnow().isoformat() + ': Container: ' + request.form.get('containerID') +'\n')
        errorfile.write(datetime.utcnow().isoformat() + str(e) + '\n')
        errorfile.write(datetime.utcnow().isoformat() + 'ErrorType' + str(e) + '\n')
        errorfile.write(datetime.utcnow().isoformat() + 'Traceback' + traceback.format_exc() + '\n')
        errorfile.write('\n')
    return {
        'status': errmessage,
        'message': str(e),
        'commitsuccess': False,
        'ErrorType': str(e),
        'traceback': traceback.format_exc()}

class SagaController():
    def __init__(self,appdatadir):
        self.appdatadir = appdatadir
        # self.mail = Mail(current_app)
        self.mailsender = MailSender()
        self.sagamodel = SagaServerModel(appdatadir)


    def latestRev(self, path):
        #add comment
        revnum = 0;
        for fn in os.listdir(path):
            m = re.search('Rev(\d+).yaml',fn)
            if  int(m.group(1))>revnum:
                revnum = int(m.group(1))
                latestrev = fn
        return latestrev, revnum

    def newContainerToModel(self,containerdict,framedict,sectionid,files,user, updateinfo):
        # newcont = Container.LoadContainerFromDict(containerdict=containerdict,
        #                                           environ='Server',
        #                                           containerworkingfolder=os.path.join(self.appdatadir,'Container', sectionid,containerdict['containerId']),
        #                                           containeryamlfn=CONTAINERFN,
        #                                                        sectionid=sectionid)
        newcont = Container.LoadVirtualContainer(framedict, containerdict)
        # newcont.workingFrame = Frame.LoadFrameFromDict(framedict)
        newcont.revnum = 1
        committime = datetime.timestamp(datetime.utcnow())
        if os.path.exists(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, newcont.containerId)):
            return {"message":"Container Already exists",
                    "data":None}
        else:
            for citemid, citem in newcont.containeritems.items():
                if citem.containeritemrole == roleInput:
                    containerid = citem.refcontainerid
                    upstreamCont = self.provideContainer(sectionid,containerid)
                    if type(upstreamCont.containeritems[citemid].refcontainerid) is list:
                        if newcont.containerId not in upstreamCont.containeritems[citemid].refcontainerid: #make sure not not duplicate downstream container ids
                            upstreamCont.containeritems[citemid].refcontainerid.append(newcont.containerId)
                    else:
                        upstreamCont.containeritems[citemid].refcontainerid = [
                            upstreamCont.containeritems[citemid].refcontainerid, newcont.containerId]
                    newcont.refframe.filestrack[citemid].lastupdated = 'Rev1'
                    upstreamCont.save(environ='Server')

            for md5 in files.keys():
                # print('fileheader' + fileheader)
                citemid = updateinfo[md5]['citemid']
                track = newcont.refframe.filestrack[citemid]
                track.committedby = user.email
                track.commitUTCdatetime = committime
                track.lastupdated = 'Rev1'
                content = files[md5].read()
                with open(os.path.join(self.appdatadir, FILEFOLDER, md5), 'wb') as file:
                    file.write(content)


            newcont.allowedUser.append(user.email)
            newcont.refframe.commitUTCdatetime = committime
            newcont.refframe.FrameInstanceId = uuid.uuid4().__str__()
            newcont.refframe.parentcontainerid = newcont.containerId
            newcont.refframe.parentcontainername = newcont.containerName
            os.mkdir(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, newcont.containerId))
            os.mkdir(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, newcont.containerId, 'Main'))
            newcont.save(environ='Server',
                         outyamlfn=safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, newcont.containerId,
                                             'containerstate.yaml'))
            newcont.refframe.writeoutFrameYaml( \
                fn=safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, newcont.containerId, 'Main', 'Rev1.yaml'),authorized=True)

            #message, containerdict, framdict,
            return "Container Made",newcont.dictify(),newcont.refframe.dictify()

    def createChildContainer(self,sectionid,parentcontainerid, childcontaineritemrole, childcontainername, childcontainerdescription):
        ## Setup Parent Container details
        parentcontainer = self.provideContainer(sectionid, parentcontainerid)
        latestrevfn, revnum = self.latestRev(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, parentcontainer.containerId, 'Main'))
        committimestamp = datetime.timestamp(datetime.utcnow())
        parentnewRev = Rev + str(revnum + 1)

        ## Setup new child container information
        childcontainerid = uuid.uuid4().__str__()
        containerworkingfolder=safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, childcontainerid)
        os.mkdir(containerworkingfolder)
        os.mkdir(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, childcontainerid, 'Main'))
        ## Create Child Container
        childcontainer = Container(containerworkingfolder=containerworkingfolder,
                           containerName=childcontainername,
                           containerid=childcontainerid,
                           containeritems={},
                           allowedUser=[],
                           readingUsers=[],
                           currentbranch="Main",revnum=0,
                           refframefullpath=safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, childcontainerid, 'Main', 'Rev1.yaml'),
                           refframe=Frame.InitiateFrame(parentcontainerid=childcontainerid, parentcontainername=childcontainername,
                                       containerworkingfolder=containerworkingfolder),        ####ATTENTION YIKES.  This Frame initation sucks.....the childcontainerid is the frame's parentcontainer so its all over the place in terms of naming.

                           workingFrame = None,
                           yamlfn = CONTAINERFN,
                           parentid = parentcontainerid,
                           description=childcontainerdescription,
                           lightload = False
                           )
        childcontainer.save()
        # Add the Child Container to the Parent Container
        childcontainertrack = parentcontainer.refframe.\
            addContainerTrack(childcontainerid,  childcontaineritemrole, childcontainername, parentnewRev, committimestamp)
        parentcontainer.addChildContainer(childcontainername, childcontaineritemrole, childcontainerid, childcontainertrack )
        self.commitNewFrameOfContainer(parentcontainer, revnum + 1)

    def commitNewFrameOfContainer(self, container:Container, newrevnum):
        container.save(fn=CONTAINERFN, commitprocess=True, environ='Server')
        container.refframe.writeoutFrameYaml(fn='Rev'+str(newrevnum)+'.yaml')


    def getContainersBySectionid(self,sectionid):
        containerinfolist={}
        for containerid in os.listdir(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid)):
            containerfn = safe_join(self.appdatadir, CONTAINERFOLDER,sectionid,containerid, 'containerstate.yaml')
            if os.path.exists(containerfn):
                curcont = self.provideContainer(sectionid, containerid)
                containerinfolist[containerid] = {'ContainerDescription': curcont.containerName,
                                                   'branches':[{'name': 'Main',
                                                                'revcount':curcont.revnum}],
                                                  'containerdict':curcont.dictify()}
        return containerinfolist

    def provideContainer(self,sectionid,containerID):
        if not os.path.exists(
                safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, containerID, 'containerstate.yaml')):
            warnings.warn('could not find containerid ' + containerID + ' in sectionid '+sectionid)
            return None

        return Container.LoadContainerFromYaml(
            safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, containerID, 'containerstate.yaml'),
            parentid=sectionid, environ='Server')


    def provideFrame(self,sectionid,containerid, revyaml):
        return Frame.loadRefFramefromYaml(refframefullpath= join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid ,'Main', revyaml),
                                          containerworkingfolder=join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid ))

    def commitNextFrameToModel(self,containerid,framedict,containerdict,
                               user,sectionid, commitmsg ,updateinfo,files, branch='Main'):
        curcont = self.provideContainer(sectionid, containerid)
        if user.email not in curcont.allowedUser:
            return False, {
                'success': False,
                'message': 'User ' + user.first_name + ' ' + user.last_name +' is not allowed to commit to this Container'
            }
        try:
            newcont = Container.LoadVirtualContainer(framedict, containerdict)
            identical, diff = Container.compare(curcont, newcont)
            savenewcont =self.AdjustRelatedContainers( diff,curcont, newcont, sectionid)
            # upstream and downstream container are checked to see if removal of input or outputs need to be notified
            latestrevfn, revnum = self.latestRev(safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, curcont.containerId, branch))
            newrevnum = revnum + 1
            newRev = Rev + str(newrevnum)
        except Exception as e:
            errsum = writeError(e, 'Error occured either in Adjusting Related containers or finding the latest Rev')
            return errsum,{}

        success, newframefullpath,newrevfn,updatedfiles,newcont,committime , errorreport = self.sagamodel.commitNewFrame(curcont=curcont,framedict=framedict,containerdict=containerdict,
                                             user=user,sectionid=sectionid, commitmsg=commitmsg,
                                                         updateinfo=updateinfo,files=files,
                                                         newrevnum=newrevnum, savenewcont=savenewcont)


        if success:
            try:
                self.mailsender.prepareMailthisContainer(thiscontainer =newcont,
                                           updatedfiles=updatedfiles,
                                            user=user,
                                           commitmsg=commitmsg,
                                           committime=committime,
                                           newrevnum=newrevnum)
                self.mailsender.sendMail()
                usernotificationsuccess =True
            except Exception as e:
                commitsuccess = True
                usernotificationsuccess=False
            with open(newframefullpath,'r') as file:
                newrevtxt = file.read()
            return commitsuccess, {
                'newrevfn':newrevfn,
                'updatedfiles': updatedfiles,
                'newcont': newcont,
                'committime': committime,
                'framecontent': newrevtxt,
                'usernotificationsuccess':usernotificationsuccess
            }
        else:
            return False, {}

    def hackassSectionuserfix(self,sect, sectiondb):
        ## Assumes sectiondb is not none
        usersections = UserSections.query.filter(UserSections.section_id == sectiondb.id)
        for usersection in usersections:
            user = User.query.filter(User.id == usersection.user_id).first()
            # usersection.
            sect.addUser(user.email)
        return sect

    def inviteEmailsToSection(self,sectionid,emailsToInvite, user):
        # success, message, failmessage, error
        sectiondb = SectionDB.query.filter(SectionDB.sectionid == sectionid).first()## Assumes sectiondb is not none
        sectionyamlfn = os.path.join(self.appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml')
        sect = Section.LoadSectionyaml(sectionyamlfn)
        sect = self.hackassSectionuserfix(sect, sectiondb)
        if user.email not in sect.sectionusers:
            return False,'','User not allowed to Add to Section ' + sect.sectionname, None
        for email in emailsToInvite:
            addeduser = User.query.filter(User.email == email).first()  ## Does User Exist?
            sect.addUser(email)
            if addeduser:
                usersect = UserSections.query.filter(UserSections.user_id == addeduser.id,
                                          UserSections.section_id == sectiondb.id).first()  ##Query this user is already associated in the DB with this Section
                if usersect is None:## And if User not currently in a UserSection Entry
                    usersection = UserSections(
                        user_id=addeduser.id,
                        section_id=sectiondb.id,
                    )
                    db.session.add(usersection)
                    db.session.commit()
                ## add User to DB
            else:
                print('Send Invite Emails.')
                self.mailsender.sectionAddNonSagaUser(email, sect, user)
                ### Send Invite Email
        sect.save(outyamlfn=sectionyamlfn)
        return  True,'Users added to Section','', None



    ##Expected to return result, ServerMessage, allowedUser
    def AddUserToContainer(self,user, containerId, new_email, sectionid):
        contpath = os.path.join(self.appdatadir, CONTAINERFOLDER, sectionid, containerId, 'containerstate.yaml')
        if os.path.exists(contpath):
            cont = self.provideContainer(sectionid,containerId)
            if user.email in cont.allowedUser:
                addeduser = User.query.filter(User.email == new_email).first() ## Does User Exist?
                cursection = SectionDB.query.filter(SectionDB.sectionid == sectionid).first()
                # user = User.query.filter_by(id=decoderesponse).first()
                if addeduser:
                    if addeduser.isInSection(sectionid):
                        added, executionmessage = cont.addAllowedUser(new_email)
                        if not added:
                            return False, executionmessage, cont.allowedUser
                        else:
                            cont.save(environ='Server')
                            return True, 'User ' + addeduser.email + ' is added', cont.allowedUser
                    else:
                        addeduser.sections.append(cursection)
                        db.session.commit()
                        added, executionmessage = cont.addAllowedUser(new_email)
                        if added:
                            cont.save(environ='Server')
                    # if addeduser.currentsection.sectionid==sectionid:
                    #     self.mailsender.containerAddSagaUser(new_email,cont, user, datetime.utcnow().timestamp())
                        return True, 'User '+addeduser.email+ ' is added', cont.allowedUser
                    # else:
                    #     return False, 'Cannot Add User.  The user you are trying to add belongs to a different section.', []
                else:
                    self.mailsender.containerAddNonSagaUser(new_email,cont)
                    return True, 'Non Saga user is sent an email invtied to join this container', cont.allowedUser
            else:  ## User not an allowedUser
                return False, 'User is not allowed to Add', []
        else:
            return False, 'Could not find container' + containerId, []

    def PingDownstreamContainerToUpdateInputs(self, fileheader, downstreamcont:Container,curcont:Container,user:User, filetrack, commitmsg, committime):
        self.mailsender.prepareMailDownstream(recipemail=downstreamcont.allowedUser,
                                              fileheader=fileheader,
                                              filetrack=filetrack, user=user, upcont=curcont,
                                              commitmsg=commitmsg,
                                              committime=committime,
                                              newrevnum=downstreamcont.revnum)
        self.mailsender.sendMail()



    def AdjustRelatedContainers(self, diff,curcont, newcont, sectionid):
        savenewcont = False
        for citemid in diff['containeritems'].keys():
            if 'MissingInDict1'== diff['containeritems'][citemid]:
                savenewcont=True
                if newcont.containeritems[citemid].containeritemrole== roleInput:
                    print('Added new Input.  containerID needs an output update.  An Output update means add cont')
                    upstreamcontainerid = newcont.containeritems[citemid].refcontainerid
                    upstreamcont = self.provideContainer(sectionid, upstreamcontainerid)
                    upstreamcont.containeritems[citemid].refcontainerid.append(curcont.containerId)
                    upstreamcont.save(environ='Server', outyamlfn=safe_join(self.appdatadir, CONTAINERFOLDER,sectionid, upstreamcontainerid, 'containerstate.yaml'))
                elif newcont.containeritems[citemid].containeritemrole == roleRequired:
                    print('Added new Entry to this container')
                elif newcont.containeritems[citemid].containeritemrole == roleOutput:
                    downcontainerid = newcont.containeritems[citemid].containeritemid
                    print('Added a fileheader as an output.')
            if 'MissingInDict2' == diff['containeritems'][citemid]:
                # a fileheader is removed
                savenewcont = True
                if curcont.containeritems[citemid].containeritemrole== roleInput:
                    print('Removed in  Input.  upstreamcontainerid needs an output update.  An Output update means remove cont')
                    upstreamcontainerid = curcont.containeritems[citemid].refcontainerid
                    upstreamcont = self.provideContainer(sectionid, upstreamcontainerid)
                    if curcont.containerId in upstreamcont.containeritems[citemid].refcontainerid:
                        upstreamcont.containeritems[citemid].refcontainerid.remove(curcont.containerId)
                    upstreamcont.save(environ='Server', outyamlfn=safe_join(self.appdatadir, CONTAINERFOLDER, sectionid, upstreamcontainerid, 'containerstate.yaml'))
                elif curcont.containeritems[citemid].containeritemrole == roleRequired:
                    print('Removed Entry to this container')
                elif curcont.containeritems[citemid].containeritemrole == roleOutput:
                    print(
                        'Removed an Output.  downcontainerid needs an output update.  An Output update means remove cont')
                    downcontaineridlist = curcont.containeritems[citemid].refcontainerid
                    fileheaderremovedready= True
                    downcontstr=''
                    for downcontainerid in downcontaineridlist:# check if downstreamcontainer already has
                        downstreamcont = self.provideContainer(sectionid, downcontainerid)
                        if citemid in downstreamcont.containeritems.keys():
                            fileheaderremovedready = False
                            downcontstr=downcontstr+downstreamcont.containerName+' '
                    if not fileheaderremovedready:
                        return {
                            'status': 'fail',
                            'message': 'You tried to delete a fileheader but you have not removed all the downstream links yet.  You need to remove ' + downcontstr +'downstream connections',
                            'ErrorType': 'Tried to remove output fileheader without clearing dependency.',
                                         'commitsuccess':False
                        }

        return savenewcont
