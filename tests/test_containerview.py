import pytest
import json
import os
import io
#
#
# from flask import g
# from flask import session
#
# from SagaApp import db
from SagaApp.Container import Container

def test_getcontainer_withInvalidID(client, app):
    containerId = 'randomblah'
    response = client.get("/CONTAINERS/containerID",
                          data={'containerID': containerId}
                           )
    resp = json.loads(response.data)
    print(resp)
    assert resp['response']=='Invalid Container ID'


def test_addcontainer(client, app, auth):
    payload = {
        'containerdictjson': '{"containerId": "specialsauce2", "containerName": "specialsauce2", "FileHeaders": {"goma1": {"Container": "here", "type":"required"},"goma2": {"Container": "here", "type":"required"}}, "allowedUser": ["usercemail@gmail.com", "admin@example.com", "member@example.com"]}',
        'framedictjson': '{"parentContainerId": "specialsauce2", "FrameName": "Rev1", "FrameInstanceId": "5f5051835f77438e1133da2c", "commitMessage": "ss2", "inlinks": null, "outlinks": null, "AttachedFiles": null, "commitUTCdatetime": 1599113667.076219, "localfilepath": "", "filestrack": [{"FileHeader": "goma1", "file_name": "goma1.jpg", "lastEdited": 1604900773.659827, "committedby": "waichak", "md5": "somemd5", "style": "required", "file_id": "goma1.jpg", "commitUTCdatetime": 1604901789.912327, "connection": null, "persist": true}, {"FileHeader": "goma2", "file_name": "goma2.jpg", "lastEdited": 1604900820.0940084, "committedby": "waichak", "md5": "somemd5", "style": "required", "file_id": "goma2.jpg", "commitUTCdatetime": 1604901789.912327, "connection": null, "persist": true}]}'}

    data = {key: str(value) for key, value in payload.items()}
    with open('testfiles/goma1.jpg', 'rb') as f:
        data['goma1.jpg'] = (io.BytesIO(f.read()), 'goma1.jpg')
    with open('testfiles/goma2.jpg', 'rb') as f:
        data['goma2.jpg'] = (io.BytesIO(f.read()), 'goma2.jpg')
    response = auth.login()
    resp = json.loads(response.data)
    auth_token = resp['auth_token']
    headers = {'Authorization': 'Bearer ' + auth_token}
    response = client.post("/FILES",
                          data=data,
                           content_type='multipart/form-data',
                           headers=headers
                           )
    resp = json.loads(response.data)
    print(resp)
    # assert resp['response']=='Invalid Container ID'




# def test_containerget(client, app):
#     containerId = 'ContainerC'
#     response = client.get("/CONTAINERS/containerID",
#                           data={'containerID': containerId}
#                            )
#     resp = json.loads(response.data)
#     print(resp)
#     assert resp['response']=='Invalid Container ID'
#     # refpath = app.config['TESTSDIR']
#     # # assert refpath == 'tests/stuff'
#     # if not os.path.exists(refpath):
#     #     os.mkdir(refpath)
#     # if not os.path.exists(os.path.join(refpath, containerId)):
#     #     os.mkdir(os.path.join(refpath, containerId))
#     # print('revnum ' + response.headers['suckonthis'])
#     # print('con ' + str(response.data))
#     # assert response.headers['branch']=='Main'
#
#     # open(os.path.join(refpath, containerId, 'containerstate.yaml'), 'wb').write(response.data)
#     # contc = Container.LoadContainerFromYaml(os.path.join(refpath, containerId, 'containerstate.yaml'))
#     # assert contc.containerId == 'ContainerC'
#     # assert isinstance(response.headers['revnum'], str)


# def test_containerget(client, app):
#     # test that viewing the page renders without template errors
#     # assert client.get("/auth/register").status_code == 200
#     # # test that successful registration redirects to the login page
#     containerId = 'ContainerC'
#     response = client.get("/CONTAINERS/containerID",
#                           data={'containerID': containerId}
#                            )
#     refpath = app.config['TESTSDIR']
#     # assert refpath == 'tests/stuff'
#     if not os.path.exists(refpath):
#         os.mkdir(refpath)
#     if not os.path.exists(os.path.join(refpath, containerId)):
#         os.mkdir(os.path.join(refpath, containerId))
#     # print('revnum ' + response.headers['suckonthis'])
#     # print('con ' + str(response.data))
#     # assert response.headers['branch']=='Main'
#
#     open(os.path.join(refpath, containerId, 'containerstate.yaml'), 'wb').write(response.data)
#     contc = Container.LoadContainerFromYaml(os.path.join(refpath, containerId, 'containerstate.yaml'))
#     assert contc.containerId == 'ContainerC'
