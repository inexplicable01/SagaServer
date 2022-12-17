# import os
# from Config import appdatadir, roleInput,roleOutput
# from SagaCore.Frame import Frame
# from SagaCore.Container import Container
#
# def checkworldmapconnections():
#     flowtrackerUp2Down={}
#     flowtrackerDown2Up = {}
#     mismatch=[]
#     for containerid in os.listdir(os.path.join(appdatadir, 'Container')):
#         print('============================================')
#         print('Checking ' + containerid)
#         print('============================================')
#         curcont = Container.LoadContainerFromYaml(os.path.join(appdatadir, 'Container', containerid, 'containerstate.yaml'))
#         for fileheader, value in curcont.FileHeaders.items():
#             print(fileheader)
#             if value['type']==roleInput:
#                 flowtrackerUp2Down[fileheader+'_'+value['Container']+'_'+curcont.containerId] = [value['Container'], curcont.containerId]
#             elif value['type']==roleOutput:
#                 for downstreamcontainerid in value['Container']:
#                     flowtrackerDown2Up[fileheader+'_'+curcont.containerId+'_'+downstreamcontainerid]= [curcont.containerId,downstreamcontainerid]
#     flowtrackercheck = list(flowtrackerDown2Up.keys())
#     for flowname, idpair in flowtrackerUp2Down.items():
#         if flowname not in flowtrackercheck:
#             print(flowname)
#             mismatch.append(flowname)
#         else:
#             flowtrackercheck.remove(flowname)
#     mismatch.extend(flowtrackercheck)
#     return mismatch
#
#
# def checkallframes():
#     for containerid in os.listdir(os.path.join(appdatadir, 'Container')):
#         print('============================================')
#         print('Checking ' + containerid)
#         print('============================================')
#         for framefn in os.listdir(os.path.join(appdatadir,'Container',containerid, 'Main')):
#             frame = Frame.loadRefFramefromYaml(os.path.join(appdatadir,'Container',containerid, 'Main', framefn),os.path.join(appdatadir,'Container',containerid))
#             # print('============================================')
#             print('============================================')
#             print(frame.FrameName)
#             for fileheader, filetrack in frame.filestrack.items():
#                 # if type(filetrack.style) is str:
#                 #     print(fileheader + "  type  "  + filetrack.style)
#                 # else:
#                 #     if filetrack.connection:
#                 #         frame.filestrack[fileheader].style = filetrack.connection.connectionType.name
#                 #     else:
#                 #         frame.filestrack[fileheader].style=roleRequired
#                 if filetrack.connection:
#                     if roleOutput==filetrack.connection.connectionType.name:
#                         print(fileheader + "  type  " + filetrack.style + " " + filetrack.connection.__repr__())
#                     elif roleInput==filetrack.connection.connectionType.name:
#                         print(fileheader + "  type  " + filetrack.style+ " " + filetrack.connection.__repr__())
#             frame.writeoutFrameYaml(os.path.join(appdatadir,'Container',containerid, 'Main', framefn))
#
#
#
# print(checkworldmapconnections())