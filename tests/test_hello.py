import pytest
import json

from flask import g
from flask import session

def test_hello(client):
    response = client.get("/")
    resp = json.loads(response.data)
    assert "Hello World" == resp['response']
