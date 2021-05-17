import os
import io
from flask import Flask,flash, request, redirect, url_for,send_from_directory , send_file, make_response, safe_join
from flask_restful import Api, Resource
import zipfile
import shutil
from SagaCore.Container import Container
from SagaCore.Section import Section
from SagaCore.Frame import Frame
from SagaAPI import db
from SagaDB.UserModel import User
from SagaDB.FileRecordModel import FileRecord
from flask import current_app
import re
import glob
import json


CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

class MaintenanceView(Resource):

    def __init__(self, rootpath):
        self.rootpath = rootpath

    def get(self, command=None):

        if command=='BuildFileRecords':
            filerecords={}
            for sectionid in os.listdir(os.path.join(self.rootpath, CONTAINERFOLDER)):
                for containerid in os.listdir(os.path.join(self.rootpath, CONTAINERFOLDER,sectionid)):
                    yamlfn = os.path.join(self.rootpath, CONTAINERFOLDER,sectionid, containerid, 'containerstate.yaml')
                    if os.path.exists(yamlfn):
                        cont = Container.LoadContainerFromYaml(yamlfn)
                        print(cont.containerId)
                        yamllist = glob.glob(os.path.join(self.rootpath, CONTAINERFOLDER,sectionid, containerid,'Main', 'Rev*.yaml'))
                        for yamlframefn in yamllist:
                            pastframe = Frame.loadFramefromYaml(yamlframefn, None)
                            revnum = re.findall('Rev(\d+).yaml', os.path.basename(yamlframefn))
                            revnum = int(revnum[0])
                            for fileheader, filetrack in pastframe.filestrack.items():
                                if filetrack.file_id in filerecords.keys():
                                    if filetrack.file_name == filerecords[filetrack.file_id]:
                                        print('FILE ID has two names??? blashempy '+   filetrack.file_name  +'  and '  + filerecords[filetrack.file_id])
                                else:
                                    filerecords[filetrack.file_id] = {'file_id':filetrack.file_id, 'filename':filetrack.file_name,'revnum':revnum,
                                                                      'containerid':cont.containerId,'containername':cont.containerName}
            for file_id in os.listdir(os.path.join(self.rootpath, FILEFOLDER)):
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
            for sectionid in os.listdir(os.path.join(self.rootpath, CONTAINERFOLDER)):
                sectfn = os.path.join(self.rootpath, CONTAINERFOLDER, sectionid, 'sectionstate.yaml')
                if os.path.exists(sectfn):
                    sect = Section.LoadSectionyaml(sectfn)

                    dictinfo[sectionid] = {'sectiondict':sect.dictify(), 'sectioncondtiondict': {}}

                    for containerid in os.listdir(os.path.join(self.rootpath, CONTAINERFOLDER, sectionid)):
                        yamlfn = os.path.join(self.rootpath, CONTAINERFOLDER, sectionid, containerid, 'containerstate.yaml')
                        if os.path.exists(yamlfn):
                            cont = Container.LoadContainerFromYaml(yamlfn)
                            dictinfo[sectionid]['sectioncondtiondict'][containerid] = {
                                'contdict':cont.dictify(),
                            'framelist':{}
                            }
                            # print(cont.containerId)
                            yamllist = glob.glob(
                                os.path.join(self.rootpath, CONTAINERFOLDER, sectionid, containerid, 'Main', 'Rev*.yaml'))
                            for yamlframefn in yamllist:
                                pastframe = Frame.loadFramefromYaml(yamlframefn, None)
                                revnum = re.findall('Rev(\d+).yaml', os.path.basename(yamlframefn))
                                revnum = int(revnum[0])
                                dictinfo[sectionid]['sectioncondtiondict'][containerid]['framelist'][revnum] = pastframe.dictify()
                        #         for fileheader, filetrack in pastframe.filestrack.items():
                        #             if filetrack.file_id in filerecords.keys():
                        #                 if filetrack.file_name == filerecords[filetrack.file_id]:
                        #                     print('FILE ID has two names??? blashempy ' + filetrack.file_name + '  and ' +
                        #                           filerecords[filetrack.file_id])
                        #             else:
                        #                 filerecords[filetrack.file_id] = {'file_id': filetrack.file_id,
                        #                                                   'filename': filetrack.file_name, 'revnum': revnum,
                        #                                                   'containerid': cont.containerId,
                        #                                                   'containername': cont.containerName}

            resp.headers["response"] = "FullSectionList"
            resp.data = json.dumps(dictinfo)
            return resp



    def post(self):
        zipf = zipfile.ZipFile(os.path.join(self.rootpath, 'SagaServer.zip'), 'w', zipfile.ZIP_DEFLATED)
        self.zipdir( CONTAINERFOLDER, zipf)
        self.zipdir('Files', zipf)
        zipf.close()
        return {"Message":"Succesfully Saved Zip"}