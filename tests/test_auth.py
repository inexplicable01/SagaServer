import pytest
import json
#
#
# from flask import g
# from flask import session
#
# from SagaApp import db


def test_register_twice(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200
    # # test that successful registration redirects to the login page
    response = client.post("/auth/register", json={"email": "random@email.com",
                                       "password": "superman",
                                                   "first_name": "Clark",
                                                   "last_name": "Kent"},
                           )
    assert response.status_code == 201
    resp = json.loads(response.data)
    assert resp['message'] == 'Successfully registered.'

    response = client.post("/auth/register", json={"email": "random@email.com",
                                       "password": "superman",
                                                   "first_name": "Clark",
                                                   "last_name": "Kent"},
                           )
    assert response.status_code == 202
    resp = json.loads(response.data)
    assert resp['message'] == 'User already exists. Please Log in.'



def test_register_justonce(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200
    # # test that successful registration redirects to the login page
    response = client.post("/auth/register", json={"email": "random@email.com",
                                       "password": "superman",
                                                   "first_name": "Clark",
                                                   "last_name": "Kent"},
                           )
    assert response.status_code == 201
    resp = json.loads(response.data)
    assert resp['message'] == 'Successfully registered.'

def test_login(client, auth):
    response = auth.login()
    resp = json.loads(response.data)
    print(resp)
    assert resp['status']=="success"
# @pytest.mark.parametrize(
#     ("username", "password", "message"),
#     (
#         ("", "", b"Username is required."),
#         ("a", "", b"Password is required."),
#         ("test", "test", b"already registered"),
#     ),
# )
# def test_register_validate_input(client, username, password, message):
#     response = client.post(
#         "/auth/register", data={"username": username, "password": password}
#     )
#     assert message in response.data
#
#
# def test_login(client, auth):
#     # test that viewing the page renders without template errors
#     assert client.get("/auth/login").status_code == 200
#
#     # test that successful login redirects to the index page
#     response = auth.login()
#     assert response.headers["Location"] == "http://localhost/"
#
#     # login request set the user_id in the session
#     # check that the user is loaded from the session
#     with client:
#         client.get("/")
#         assert session["user_id"] == 1
#         assert g.user["username"] == "test"
#
#
# @pytest.mark.parametrize(
#     ("username", "password", "message"),
#     (("a", "test", b"Incorrect username."), ("test", "a", b"Incorrect password.")),
# )
# def test_login_validate_input(auth, username, password, message):
#     response = auth.login(username, password)
#     assert message in response.data
#
#
# def test_logout(client, auth):
#     auth.login()
#
#     with client:
#         auth.logout()
#         assert "user_id" not in session
