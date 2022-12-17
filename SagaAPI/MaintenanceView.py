import os
import io
from flask import Flask,flash, request, redirect, url_for,send_from_directory , send_file, make_response, safe_join
from flask_restful import Api, Resource
import zipfile
import shutil
from SagaCore.Container import Container
from SagaCore.SagaUtil import *
from SagaCore.Section import Section
from SagaCore.Frame import Frame
from SagaAPI import db
from SagaDB.UserModel import User, Role
from SagaDB.FileRecordModel import FileRecord
from SagaServerOperations.SagaServerContainerOperations import *
from flask import current_app
import re
import glob
import json
from SagaAPI.SagaAPI_Util import authcheck
from os.path import join


CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class MaintenanceView(Resource):

    def __init__(self, appdatadir, sagacontroller):
        self.appdatadir = appdatadir
        self.sagacontroller = sagacontroller

    def get(self, command=None):

        if command=='BuildFileRecords':
            filerecords={}
            for sectionid in os.listdir(join(self.appdatadir, CONTAINERFOLDER)):
                for containerid in os.listdir(join(self.appdatadir, CONTAINERFOLDER,sectionid)):
                    yamlfn = join(self.appdatadir, CONTAINERFOLDER,sectionid, containerid, 'containerstate.yaml')
                    if os.path.exists(yamlfn):
                        cont = self.sagacontroller.provideContainer(sectionid,containerid)
                        print(cont.containerId)
                        yamllist = glob.glob(join(self.appdatadir, CONTAINERFOLDER,sectionid, containerid,'Main', 'Rev*.yaml'))
                        for yamlframefn in yamllist:
                            pastframe = Frame.loadRefFramefromYaml(yamlframefn, join(self.appdatadir, CONTAINERFOLDER,sectionid, containerid))
                            revnum = re.findall('Rev(\d+).yaml', os.path.basename(yamlframefn))
                            revnum = int(revnum[0])
                            for fileheader, filetrack in pastframe.filestrack.items():
                                if filetrack.md5 in filerecords.keys():
                                    if filetrack.file_name == filerecords[filetrack.md5]:
                                        print('FILE ID has two names??? blashempy '+   filetrack.file_name  +'  and '  + filerecords[filetrack.md5])
                                else:
                                    filerecords[filetrack.md5] = {'md5':filetrack.md5, 'filename':filetrack.file_name,'revnum':revnum,
                                                                      'containerid':cont.containerId,'containername':cont.containerName}
            for file_id in os.listdir(join(self.appdatadir, FILEFOLDER)):
                # print(files)
                if file_id not in filerecords.keys():
                    continue
                f = FileRecord(
                            file_id=file_id, filename=filerecords[file_id]['filename'],revnum=filerecords[file_id]['revnum'],
                    containerid=filerecords[file_id]['containerid'],
                    containername=filerecords[file_id]['containername']
                        )
                db.session.add(f)
            db.session.commit()

        elif command=='Userlist':
            resp = make_response()
            users = User.query.all()
            userlist={}
            for user in users:
                userlist[user.id]= {'first_name':user.first_name, 'last_name':user.last_name,'email':user.email}
            resp.headers["response"] = "Userlist"
            resp.data = json.dumps(userlist)
            return resp
        elif command=='SyncFromServer':
            resp = make_response()
            dictinfo = {}
            # users = User.query.all()
            # userlist = {}
            # for user in users:
            #     userlist[user.id] = {'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email}
            for sectionid in os.listdir(join(self.appdatadir, CONTAINERFOLDER)):
                sectfn = join(self.appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml')
                if os.path.exists(sectfn):
                    sect = Section.LoadSectionyaml(sectfn)
                    dictinfo[sectionid] = {'sectiondict':sect.dictify(), 'sectioncondtiondict': {}}

                    for containerid in os.listdir(join(self.appdatadir, CONTAINERFOLDER, sectionid)):
                        yamlfn = join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid, 'containerstate.yaml')
                        if os.path.exists(yamlfn):
                            cont = self.sagacontroller.provideContainer(sectionid, containerid)
                            dictinfo[sectionid]['sectioncondtiondict'][containerid] = {
                                'contdict':cont.dictify(),
                            'framelist':{}
                            }
                            # print(cont.containerId)
                            yamllist = glob.glob(
                                join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid, 'Main', 'Rev*.yaml'))
                            for yamlframefn in yamllist:
                                pastframe = Frame.loadRefFramefromYaml(yamlframefn,  join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid))
                                revnum = re.findall('Rev(\d+).yaml', os.path.basename(yamlframefn))
                                revnum = int(revnum[0])
                                dictinfo[sectionid]['sectioncondtiondict'][containerid]['framelist'][revnum] = pastframe.dictify()
                        #         for fileheader, filetrack in pastframe.filestrack.items():
                        #             if filetrack.md5 in filerecords.keys():
                        #                 if filetrack.file_name == filerecords[filetrack.md5]:
                        #                     print('FILE ID has two names??? blashempy ' + filetrack.file_name + '  and ' +
                        #                           filerecords[filetrack.md5])
                        #             else:
                        #                 filerecords[filetrack.md5] = {'file_id': filetrack.md5,
                        #                                                   'filename': filetrack.file_name, 'revnum': revnum,
                        #                                                   'containerid': cont.containerId,
                        #                                                   'containername': cont.containerName}

            resp.headers["response"] = "FullSectionList"
            resp.data = json.dumps(dictinfo)
            return resp
        elif command=='updateallcontainers':
            for sectionid in os.listdir(join(self.appdatadir, CONTAINERFOLDER)):
                sectfn = join(self.appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml')
                if os.path.exists(sectfn):
                    sect = Section.LoadSectionyaml(sectfn)
                    for containerid in os.listdir(join(self.appdatadir, CONTAINERFOLDER, sectionid)):
                        yamlfn = join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid, 'containerstate.yaml')
                        if os.path.exists(yamlfn):
                            cont = self.sagacontroller.provideContainer(sectionid, containerid)






    def post(self, command=None):
        if command=='SyncToServer':
            authcheckresult = authcheck(request.headers.get('Authorization'))

            if not isinstance(authcheckresult, User):
                (resp, num) = authcheckresult
                return resp, num
                # return resp, num # user would be a type of response if its not the actual class user
            user = authcheckresult
            # sectionid = user.currentsection.sectionid
            resp = make_response()
            resp.headers["status"] = 'Syncing'
            adminrole = Role.query.filter(Role.name == 'Admin').first()
            missingfiles=[]
            if adminrole not in user.roles:
                resp.headers["status"] = 'User not an Admin!!'
                return resp
            else:
                resp.headers["status"] = 'User is an Admin!!'
                dictinfo = json.loads(request.form['dictinfo'])
                # print(dictinfo)
                comparesummary={}
                for sectionid, sectioninfo in dictinfo.items():
                    print(sectionid)
                    #
                    localsect = Section.LoadSectionFromDict(sectioninfo['sectiondict'])
                    ### Check if section exists
                    ### Check if not create it
                    if os.path.exists(join(self.appdatadir, CONTAINERFOLDER,sectionid, 'sectionstate.yaml')):
                        serversect = Section.LoadSectionyaml(join(self.appdatadir, CONTAINERFOLDER,sectionid, 'sectionstate.yaml'))
                        identical, diff = recursivecompare(serversect.dictify(), sectioninfo['sectiondict'])
                        if not identical:
                            comparesummary[sectionid] = diff
                    else:
                        os.mkdir(join(self.appdatadir, CONTAINERFOLDER, sectionid))
                        localsect.save(outyamlfn=join(self.appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml'))

                    # sect.save(outyamlfn=join(self.appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml'))
                    for containerid, containerdict in sectioninfo['sectioncondtiondict'].items():
                        # os.mkdir(join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid))
                        localcont = Container.LoadContainerFromDict(containerdict['contdict'], environ='Server',
                                                               sectionid=sectionid)
                        if os.path.exists(join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid,'containerstate.yaml')):
                            servercont = self.sagacontroller.provideContainer(sectionid, containerid)
                        else:
                            try:
                                os.mkdir(join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid))
                                os.mkdir(join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid,'Main'))
                            except Exception as e:
                                print('Directory already exists')
                            localcont.save(environ='Server')
                        identical, diff = recursivecompare(servercont.dictify(), containerdict['contdict'])
                        if not identical:
                            comparesummary[containerid] = diff
                        print(sectionid, sectioninfo['sectiondict']['sectionname'], containerid)
                        print(containerdict['contdict'])
                        # os.mkdir(join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid, 'Main'))
                        for revnum, framdict in sectioninfo['sectioncondtiondict'][containerid]['framelist'].items():
                            print(revnum)
                            localframe = Frame.LoadFrameFromDict(framdict)
                            framefn =join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid, 'Main',
                                                                               'Rev' + str(revnum) + '.yaml')
                            if os.path.exists(framefn):
                                serverframe=self.sagacontroller.provideFrame(sectionid, containerid, 'Rev' + str(revnum) + '.yaml')
                            else:
                                localframe.writeoutFrameYaml(framefn)
                            identical, diff = recursivecompare(serverframe.dictify(), framdict)
                            if not identical:
                                comparesummary[containerid+'_'+str(revnum)] = diff

                            for fileheader, filetrack in localframe.filestrack.items():
                                if not os.path.exists(join(self.appdatadir,'Files', filetrack.md5)):
                                    missingfiles.append(filetrack.md5)
                resp.data = json.dumps({'compare':comparesummary, 'missingfiles':missingfiles})
                return resp
        elif command == 'SyncSection':
            return 'j'




        # return {"Message":"Succesfully Saved Zip"}