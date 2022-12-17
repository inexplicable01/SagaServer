import requests
from Config import BASE, waichak
import re
import glob
import json
import os
import datetime
# Sign in as admin
import warnings
from SagaCore.Container import Container
from SagaCore.Section import Section
from SagaCore.Frame import Frame
from SagaServerOperations.SagaController import SagaController

from os.path import join
from Config import appdatadir
# from SagaServerOperations.SagaServerContainerOperations import ContainerServerSave
PYTHONANYWHERE = "http://fatpanda1985.pythonanywhere.com/"
# PYTHONANYWHERE = BASE
data = {"email": waichak['email'],
        "password": waichak['password']}

response = requests.post(PYTHONANYWHERE + 'auth/login',
                    data=data
                         )
authtoken = response.json()
print('usertoken[status] ' + authtoken['status'])
with open('token.txt', 'w') as tokenfile:
    json.dump(authtoken, tokenfile)
CONTAINERFOLDER='Container'
print(authtoken)

def syncFromServer(authtoken):
    response = requests.get(PYTHONANYWHERE + 'MAINTENANCE/SyncFromServer')
                             # json={"email": adminlogin['email'],
                             #       "password": adminlogin['password']}
                             # )
    fullcontainerdict = json.loads(response.content)
    if os.path.exists(join(appdatadir,'Container')):
        os.rename(join(appdatadir,'Container'), join(appdatadir,'Container_'+datetime.datetime.utcnow().strftime('%y_%m_%d_%H_%M_%S')))
    os.mkdir(join(appdatadir,'Container'))
    if not os.path.exists(join(appdatadir,'Files')):
        os.mkdir(join(appdatadir, 'Files'))
    for sectionid, sectioninfo in fullcontainerdict.items():
        print(sectionid)
        os.mkdir(os.path.join(appdatadir,'Container', sectionid))
        sect = Section.LoadSectionFromDict(sectioninfo['sectiondict'])
        sect.save(outyamlfn=os.path.join(appdatadir,'Container', sectionid, 'sectionstate.yaml'))
        for containerid, containerdict in sectioninfo['sectioncondtiondict'].items():
            os.mkdir(os.path.join(appdatadir,'Container', sectionid,containerid))
            cont = Container.LoadContainerFromDict(containerdict['contdict'], environ='Server',sectionid=sectionid)
            cont.save(environ='Server', outyamlfn=os.path.join(appdatadir,'Container', sectionid,containerid, 'containerstate.yaml'))
            print(sectionid,sectioninfo['sectiondict']['sectionname'],containerid)
            print(containerdict['contdict'])
            os.mkdir(os.path.join(appdatadir,'Container', sectionid,containerid, 'Main'))
            for revnum, framdict in sectioninfo['sectioncondtiondict'][containerid]['framelist'].items():
                print(revnum)
                frame = Frame.LoadFrameFromDict(framdict)
                framefn = os.path.join(appdatadir,'Container', sectionid, containerid, 'Main', 'Rev'+str(revnum)+'.yaml')
                frame.writeoutFrameYaml(framefn)
                for fileheader, filetrack in frame.filestrack.items():
                    if filetrack.md5:
                        fileok = True

                        try:
                            with open(os.path.join(appdatadir, 'Files', filetrack.md5), 'r') as fhandle:
                                for line in fhandle:
                                    if "Invalid file" in line:
                                        fileok = False
                        except Exception as e:
                            print(fhandle)


                        if not os.path.exists(os.path.join(appdatadir,'Files',filetrack.md5)) or not fileok:
                            response = requests.get(BASE + 'FILES',
                                                    data={'md5': filetrack.md5, 'file_name': filetrack.file_name})
                            # Loops through the filestrack in curframe and request files listed in the frame
                            fn = os.path.join(os.path.join(appdatadir,'Files',filetrack.md5))
                            if response.headers['status'] == 'Success':
                                open(fn, 'wb').write(response.content)
                                os.utime(fn, (filetrack.lastEdited, filetrack.lastEdited))
                            else:
                                # open(fn, 'w').write('Terrible quick bug fix')
                                # There should be a like a nuclear warning here is this imples something went wrong with the server and the frame bookkeeping system
                                # This might be okay meanwhile as this is okay to break during dev but not during production.
                                # print('could not find file ' + filetrack.md5 + ' on server')
                                warnings.warn('cannot find file ' + filetrack.file_name + ' with ' + filetrack.md5)






syncFromServer(authtoken)

def pushToServer(authtoken):
    dictinfo = {}
    for sectionid in os.listdir(os.path.join(appdatadir,CONTAINERFOLDER)):
        sectfn = os.path.join(appdatadir,CONTAINERFOLDER, sectionid, 'sectionstate.yaml')
        if os.path.exists(sectfn):
            sect = Section.LoadSectionyaml(sectfn)
            dictinfo[sectionid] = {'sectiondict': sect.dictify(), 'sectioncondtiondict': {}}
            for containerid in os.listdir(os.path.join(appdatadir,CONTAINERFOLDER, sectionid)):
                yamlfn = os.path.join(appdatadir,CONTAINERFOLDER, sectionid, containerid, 'containerstate.yaml')
                if os.path.exists(yamlfn):
                    cont = SagaController.provideContainer(sectionid, containerid)
                    dictinfo[sectionid]['sectioncondtiondict'][containerid] = {
                        'contdict': cont.dictify(),
                        'framelist': {}
                    }
                    yamllist = glob.glob(
                        os.path.join(appdatadir,CONTAINERFOLDER, sectionid, containerid, 'Main', 'Rev*.yaml'))
                    for yamlframefn in yamllist:
                        pastframe = Frame.loadRefFramefromYaml(yamlframefn, os.path.join(appdatadir,CONTAINERFOLDER, sectionid, containerid))
                        revnum = re.findall('Rev(\d+).yaml', os.path.basename(yamlframefn))
                        revnum = int(revnum[0])
                        dictinfo[sectionid]['sectioncondtiondict'][containerid]['framelist'][
                            revnum] = pastframe.dictify()

    response=requests.post(PYTHONANYWHERE + 'MAINTENANCE/SyncToServer',
                          headers={"Authorization": 'Bearer ' + authtoken['auth_token']},
                          data={'dictinfo':json.dumps(dictinfo)})

    print(response.headers["status"])
    summary =json.loads(response.content)
    # print(summary)
    for diffheader, diffdict in summary['compare'].items():
        print(diffheader, diffdict)
    for md5 in summary['missingfiles']:
        print('sending file '+ md5)
        filepath = join(appdatadir,'Files',md5)
        filesToUpload={md5:open(filepath,'rb')}
        response = requests.post(PYTHONANYWHERE + 'FILES',
                                 headers={"Authorization": 'Bearer ' + authtoken['auth_token']},
                                 data={'md5': md5},
                                 files=filesToUpload)
        print(response.headers["status"])

    # dictinfo={}
    # for sectionid in os.listdir(os.path.join(CONTAINERFOLDER)):
    #     sectfn = os.path.join(CONTAINERFOLDER, sectionid, 'sectionstate.yaml')
    #     if os.path.exists(sectfn):
    #         sect = Section.LoadSectionyaml(sectfn)
    #         dictinfo[sectionid] = {'sectiondict': sect.dictify(), 'sectioncondtiondict': {}}
    #         for containerid in os.listdir(os.path.join(CONTAINERFOLDER, sectionid)):
    #             yamlfn = os.path.join(CONTAINERFOLDER, sectionid, containerid, 'containerstate.yaml')
    #             if os.path.exists(yamlfn):
    #                 cont = Container.LoadContainerFromYaml(yamlfn)
    #                 dictinfo[sectionid]['sectioncondtiondict'][containerid] = {
    #                     'contdict': cont.dictify(),
    #                     'framelist': {}
    #                 }
    #                 yamllist = glob.glob(
    #                     os.path.join( CONTAINERFOLDER, sectionid, containerid, 'Main', 'Rev*.yaml'))
    #                 for yamlframefn in yamllist:
    #                     pastframe = Frame.loadFramefromYaml(yamlframefn, None)
    #                     revnum = re.findall('Rev(\d+).yaml', os.path.basename(yamlframefn))
    #                     revnum = int(revnum[0])
    #                     dictinfo[sectionid]['sectioncondtiondict'][containerid]['framelist'][
    #                         revnum] = pastframe.dictify()
    #
    #     response=requests.post(PYTHONANYWHERE + 'MAINTENANCE/SyncUpSection',
    #                           headers={"Authorization": 'Bearer ' + authtoken['auth_token']},
    #                           data={'dictinfo':json.dumps(dictinfo)})


# pushToServer(authtoken)