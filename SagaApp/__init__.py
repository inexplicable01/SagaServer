from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
from flask_user import UserManager
import os
from flask_restful import Api

from config import ConfigClass, basedir

db = SQLAlchemy()

def create_SagaApp(test_config=None):
    app = Flask(__name__)
    app.config.from_object(ConfigClass)
    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile("config.py", silent=True)
    # # else:
    # if test_config is not None:
    #     # load the test config if passed in
    #     app.config.update(test_config)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)

    from SagaApp.views import auth_blueprint

    with app.app_context():
        from SagaApp.UserModel import User
        db.create_all()
        ### user_manager No use right now, could be useful when we want to do API calls based on roles
        user_manager = UserManager(app, db, User)
        from SagaApp.InitBase import InitBase
        InitBase(user_manager,db)
        app.register_blueprint(auth_blueprint)
        api = Api(app)
        rootpath = basedir
        from SagaApp.FileView import FileView
        from SagaApp.FrameView import FrameView
        from SagaApp.ContainerView import ContainerView
        from SagaApp.CommitView import CommitView
        from SagaApp.ResetView import Reset
        from SagaApp.HelloView import HelloView
        api.add_resource(ContainerView, "/CONTAINERS/<command>", methods=['GET', 'POST', 'DELETE'],
                         resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(CommitView, "/COMMIT", methods=['POST'], resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(FrameView, "/FRAMES", resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(FileView, "/FILES", resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(Reset, "/RESET", resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(HelloView, "/", resource_class_kwargs={'rootpath': rootpath})

        return app


# bcrypt = Bcrypt(app)

# from UserModel import User,Role
#     # # Create 'member@example.com' user with no roles
# # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
# if not Role.query.filter(Role.name == 'Admin').first():
#     db.session.add(Role(name='Admin'))
#     db.session.add(Role(name='Agent'))
#     db.session.commit()
# db.create_all()