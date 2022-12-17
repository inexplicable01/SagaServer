import os
import yaml

if os.path.exists('localConfig.txt'):
    with open('localConfig.txt','r') as file:
        localconfig = yaml.load(file, Loader=yaml.FullLoader)
else:
    raise('Missing localConfig.txt. Abort!')

if 'APPFolder' in localconfig.keys():
    apppath = os.getenv('appdata')
    if apppath is not None:  # this is for windows app folder.
        appdatadir = os.path.join(apppath, localconfig['APPFolder'])
    else:  # this is for pythonanywhere setting
        appdatadir = localconfig['APPFolder']
else:
    appdatadir = os.path.abspath(os.path.dirname(__file__))

if 'webserverdir' in localconfig.keys():
    if localconfig['webserverdir']=='here':
        webserverdir = os.path.abspath(os.path.dirname(__file__))
    else:
        webserverdir = localconfig['webserverdir']
else:
    webserverdir = os.path.abspath(os.path.dirname(__file__))

if 'port' in localconfig.keys():
    port = str(localconfig['port'])
else:
    port = str(9500)

if 'dbinitializeryamlfile' in localconfig.keys():
    dbinitializeryamlfile = localconfig['dbinitializeryamlfile']
else:
    dbinitializeryamlfile = 'sagadb.yaml'

print(appdatadir)

from os.path import join
CONTAINERFOLDER = 'Container'
sections = os.listdir(join(appdatadir,'Container'))
# print(sections)
# from SagaCore.Section import Section
# from SagaCore.Container import Container
# for sectionid in sections:
#     if os.path.exists(join(appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml')):
#         localsect = Section.LoadSectionyaml(join(appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml'))
#         print(localsect.sectionname)
#     else:
#         continue
#     newcont = Container.InitiateContainer(containerworkingfolder=join(appdatadir, CONTAINERFOLDER),parentid='root')
# for sectionid, sectioninfo in dictinfo.items():
#     print(sectionid)
#     #
#     localsect = Section.LoadSectionFromDict(sectioninfo['sectiondict'])
#     ### Check if section exists
#     ### Check if not create it
#     if os.path.exists(join(self.appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml')):
#         serversect = Section.LoadSectionyaml(join(self.appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml'))
#         identical, diff = recursivecompare(serversect.dictify(), sectioninfo['sectiondict'])
#         if not identical:
#             comparesummary[sectionid] = diff
#     else:
#         os.mkdir(join(self.appdatadir, CONTAINERFOLDER, sectionid))
#         localsect.save(outyamlfn=join(self.appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml'))
#
#     # sect.save(outyamlfn=join(self.appdatadir, CONTAINERFOLDER, sectionid, 'sectionstate.yaml'))
#     for containerid, containerdict in sectioninfo['sectioncondtiondict'].items():
#         # os.mkdir(join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid))
#         localcont = Container.LoadContainerFromDict(containerdict['contdict'], environ='Server',
#                                                     sectionid=sectionid)
#         if os.path.exists(join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid, 'containerstate.yaml')):
#             servercont = self.sagaop.provideContainer(sectionid, containerid)
#         else:
#             try:
#                 os.mkdir(join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid))
#                 os.mkdir(join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid, 'Main'))
#             except Exception as e:
#                 print('Directory already exists')
#             localcont.save(environ='Server')
#         identical, diff = recursivecompare(servercont.dictify(), containerdict['contdict'])
#         if not identical:
#             comparesummary[containerid] = diff
#         print(sectionid, sectioninfo['sectiondict']['sectionname'], containerid)
#         print(containerdict['contdict'])
#         # os.mkdir(join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid, 'Main'))
#         for revnum, framdict in sectioninfo['sectioncondtiondict'][containerid]['framelist'].items():
#             print(revnum)
#             localframe = Frame.LoadFrameFromDict(framdict)
#             framefn = join(self.appdatadir, CONTAINERFOLDER, sectionid, containerid, 'Main',
#                            'Rev' + str(revnum) + '.yaml')
#             if os.path.exists(framefn):
#                 serverframe = self.sagaop.provideFrame(sectionid, containerid, 'Rev' + str(revnum) + '.yaml')
#             else:
#                 localframe.writeoutFrameYaml(framefn)
#             identical, diff = recursivecompare(serverframe.dictify(), framdict)
#             if not identical:
#                 comparesummary[containerid + '_' + str(revnum)] = diff


