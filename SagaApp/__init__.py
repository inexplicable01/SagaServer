from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
from flask_restful import Api

from config import ConfigClass, basedir
import os

db = SQLAlchemy()

def create_SagaApp(test_config=None):
    app = Flask(__name__, template_folder=os.path.join(basedir ,'templates'),
                static_folder=os.path.join(basedir ,'static'),
                )
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


    # @app.route("/")
    # def index():
    #     return "hello world"
    #
    # api.add_resource(HelloView, "/", resource_class_kwargs={'rootpath': rootpath})

    with app.app_context():
        from SagaApp.views import auth_blueprint
        from SagaApp.weblogic.webpages import webpages_blueprint
        from SagaApp.weblogic.auth import auth_web_blueprint
        from SagaApp.UserModel import User
        db.create_all()
        from SagaApp.InitBase import InitBase
        InitBase(db)
        app.register_blueprint(auth_blueprint)
        app.register_blueprint(webpages_blueprint)
        app.register_blueprint(auth_web_blueprint)
        # app.add_url_rule('/',endpoint=)
        api = Api(app)
        rootpath = basedir
        from SagaApp.FileView import FileView
        from SagaApp.FrameView import FrameView
        from SagaApp.ContainerView import ContainerView
        from SagaApp.CommitView import CommitView
        from SagaApp.ResetView import Reset
        from SagaApp.HelloView import HelloView
        from SagaApp.SectionView import SectionView
        api.add_resource(ContainerView, "/CONTAINERS/<command>", methods=['GET', 'POST', 'DELETE'],
                         resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(CommitView, "/COMMIT", methods=['POST'], resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(FrameView, "/FRAMES", resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(FileView, "/FILES", resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(SectionView, "/SECTION", resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(Reset, "/RESET", resource_class_kwargs={'rootpath': rootpath})
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