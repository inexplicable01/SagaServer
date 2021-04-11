
import tempfile

import pytest
import shutil

from SagaAPI import create_SagaApp
import os

# # read in SQL for populating test data
# with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
#     _data_sql = f.read().decode("utf8")


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    # sagaapp.config['TESTING'] = True
    sagaapp = create_SagaApp({'TESTING': True,
                              'SQLALCHEMY_DATABASE_URI': 'sqlite:///basic_app_contest.sqlite',
                              'TESTSDIR':'tests/stuff',
                              'CONTAINERFOLDER' : 'Containertest',
                              'FILEFOLDER' : 'Filestest'})
    if not os.path.exists('Containertest'):
        os.mkdir('Containertest')
    if not os.path.exists('Filestest'):
        os.mkdir('Filestest')
    if not os.path.exists('frontendtest'):
        os.mkdir('frontendtest')
    # with app.app_context():
    #     # print('here')
    #     init_db()
    #     get_db().executescript(_data_sql)

    yield sagaapp


    # close and remove the temporary database
    os.close(db_fd)
    os.unlink('SagaAPI/basic_app_contest.sqlite')
    # os.rmdir('Containertest')
    # shutil.rmtree('Containertest')
    # shutil.rmtree('Filestest')
    # shutil.rmtree('frontendtest')



@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, email='usercemail@gmail.com', password="passwordC"):

        return self._client.post(
            "/auth/login",
            json={"email": email, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
