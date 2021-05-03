from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

from Config import ConfigClass, basedir
import os

db = SQLAlchemy()

def create_SagaApp(test_config=None):
    app = Flask(__name__, template_folder=os.path.join(basedir ,'templates'),
                static_folder=os.path.join(basedir ,'static'),
                )
    app.config.from_object(ConfigClass)

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        from SagaAPI.views import auth_blueprint  ## db tables are defined are already
        from SagaAPI.weblogic.webpages import webpages_blueprint
        from SagaAPI.weblogic.auth import auth_web_blueprint
        from SagaAPI.FileView import FileView
        from SagaAPI.FrameView import FrameView
        from SagaAPI.ContainerView import ContainerView
        from SagaAPI.SagaOpView import SagaOperationsView
        from SagaAPI.ResetView import Reset
        from SagaAPI.HelloView import HelloView
        from SagaAPI.SectionView import SectionView
        from SagaAPI.MailTestView import MailTestView
        from SagaAPI.MaintenanceView import MaintenanceView
        # from SagaAPI.FileView import FileView
        db.create_all()
        from SagaAPI.InitBase import InitBase
        InitBase(db)
        app.register_blueprint(auth_blueprint)
        app.register_blueprint(webpages_blueprint)
        app.register_blueprint(auth_web_blueprint)
        # app.add_url_rule('/',endpoint=)
        api = Api(app)
        rootpath = basedir

        api.add_resource(MailTestView, "/MAILTEST/", methods=['GET', 'POST'],resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(ContainerView, "/CONTAINERS/<command>", methods=['GET', 'POST', 'DELETE'],
                         resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(SagaOperationsView, "/SAGAOP/<command>", methods=['POST'], resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(FrameView, "/FRAMES", resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(FileView, "/FILES", resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(SectionView, "/SECTION/<command>", resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(Reset, "/RESET", resource_class_kwargs={'rootpath': rootpath})
        api.add_resource(MaintenanceView, "/MAINTENANCE/<command>", resource_class_kwargs={'rootpath': rootpath})
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