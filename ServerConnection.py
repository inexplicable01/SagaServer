import requests
from Config import BASE, adminlogin
import re
import glob
import json
import os
import datetime
# Sign in as admin
from SagaCore.Container import Container
from SagaCore.Section import Section
from SagaCore.Frame import Frame
Python = "http://fatpanda1985.pythonanywhere.com/"
response = requests.post(BASE + 'auth/login',
                         json={"email": adminlogin['email'],
                               "password": adminlogin['password']}
                         )
authtoken = response.json()
print('usertoken[status] ' + authtoken['status'])
with open('token.txt', 'w') as tokenfile:
    json.dump(authtoken, tokenfile)
CONTAINERFOLDER='Container'
print(authtoken)

def syncFromServer(authtoken):
    response = requests.get(BASE + 'MAINTENANCE/SyncFromServer')
                             # json={"email": adminlogin['email'],
                             #       "password": adminlogin['password']}
                             # )
    fullcontainerdict = json.loads(response.content)
    if os.path.exists('Container'):
        os.rename('Container', 'Container_'+datetime.datetime.now().strftime('%y_%m_%d_%H_%M_%S'))
        os.mkdir('Container')
    for sectionid, sectioninfo in fullcontainerdict.items():
        print(sectionid)
        os.mkdir(os.path.join('Container', sectionid))
        sect = Section.LoadSectionFromDict(sectioninfo['sectiondict'])
        sect.save(outyamlfn=os.path.join('Container', sectionid, 'sectionstate.yaml'))
        for containerid, containerdict in sectioninfo['sectioncondtiondict'].items():
            os.mkdir(os.path.join('Container', sectionid,containerid))
            cont = Container.LoadContainerFromDict(containerdict['contdict'], environ='Server',sectionid=sectionid)
            cont.save(environ='Server')
            print(sectionid,sectioninfo['sectiondict']['sectionname'],containerid)
            print(containerdict['contdict'])
            os.mkdir(os.path.join('Container', sectionid,containerid, 'Main'))
            for revnum, framdict in sectioninfo['sectioncondtiondict'][containerid]['framelist'].items():
                print(revnum)
                frame = Frame.LoadFrameFromDict(framdict)
                framefn = os.path.join('Container', sectionid, containerid, 'Main', 'Rev'+str(revnum)+'.yaml')
                frame.writeoutFrameYaml(framefn)
                for fileheader, filetrack in frame.filestrack.items():
                    if os.path.exists(os.path.join('Files',filetrack.file_id)):
                        frame.downloadInputFile(fileheader, 'FileTest')
                    else:
                        frame.downloadInputFile(fileheader, 'Files')





# syncFromServer(authtoken)

def pushToServer(authtoken):
    dictinfo = {}
    for sectionid in os.listdir(os.path.join( CONTAINERFOLDER)):
        sectfn = os.path.join( CONTAINERFOLDER, sectionid, 'sectionstate.yaml')

        if os.path.exists(sectfn):
            sect = Section.LoadSectionyaml(sectfn)

            dictinfo[sectionid] = {'sectiondict': sect.dictify(), 'sectioncondtiondict': {}}

            for containerid in os.listdir(os.path.join(CONTAINERFOLDER, sectionid)):
                yamlfn = os.path.join(CONTAINERFOLDER, sectionid, containerid, 'containerstate.yaml')
                if os.path.exists(yamlfn):
                    cont = Container.LoadContainerFromYaml(yamlfn)
                    dictinfo[sectionid]['sectioncondtiondict'][containerid] = {
                        'contdict': cont.dictify(),
                        'framelist': {}
                    }
                    # print(cont.containerId)
                    yamllist = glob.glob(
                        os.path.join( CONTAINERFOLDER, sectionid, containerid, 'Main', 'Rev*.yaml'))
                    for yamlframefn in yamllist:
                        pastframe = Frame.loadFramefromYaml(yamlframefn, None)
                        revnum = re.findall('Rev(\d+).yaml', os.path.basename(yamlframefn))
                        revnum = int(revnum[0])
                        dictinfo[sectionid]['sectioncondtiondict'][containerid]['framelist'][
                            revnum] = pastframe.dictify()