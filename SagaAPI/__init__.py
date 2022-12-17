from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
import os
from SagaCore.SagaUtil import DatabaseSagaYaml
db = SQLAlchemy()
import logging

from Config import ConfigClass, appdatadir, webserverdir , dbinitializeryamlfile



def createSagaApp(test_config=None):


    app = Flask(__name__, template_folder=os.path.join(webserverdir ,'templates'),
                static_folder=os.path.join(webserverdir ,'static'),
                )
    logging.info('Started')
    app.config.from_object(ConfigClass)

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        from SagaAPI.authviews import auth_blueprint  ## db tables are defined are already
        from SagaAPI.weblogic.webpages import webpages_blueprint
        from SagaAPI.weblogic.auth import auth_web_blueprint
        from SagaAPI.FileView import FileView
        from SagaAPI.FrameView import FrameView
        from SagaAPI.ContainerView import ContainerView
        from SagaAPI.SagaOpView import SagaOperationsView
        from SagaAPI.UserView import UserView
        from SagaAPI.HelloView import HelloView
        from SagaAPI.SectionView import SectionView
        from SagaAPI.MailTestView import MailTestView
        from SagaAPI.MaintenanceView import MaintenanceView
        from SagaAPI.PermissionView import PermissionsView
        from SagaAPI.GeneralView import GeneralView
        from SagaAPI.PingView import PingView
        from SagaServerOperations.SagaController import SagaController
        # from SagaAPI.FileView import FileView
        db.create_all()
        from SagaAPI.InitBase import InitBase
        sagauserdb = DatabaseSagaYaml.initiate(dbinitializeryamlfile)
        InitBase(db=db, sagauserdb = sagauserdb)
        app.register_blueprint(auth_blueprint)
        app.register_blueprint(webpages_blueprint)
        app.register_blueprint(auth_web_blueprint)
        # app.add_url_rule('/',endpoint=)
        api = Api(app)
        sagacontroller = SagaController(appdatadir)
        # appdatadir = basedir
        api.add_resource(MailTestView, "/MAILTEST/", methods=['GET', 'POST'],resource_class_kwargs={'appdatadir': appdatadir, 'sagacontroller':sagacontroller})
        api.add_resource(ContainerView, "/CONTAINERS/<command>", methods=['GET', 'POST', 'DELETE'],
                         resource_class_kwargs={'appdatadir': appdatadir, 'sagacontroller':sagacontroller})
        api.add_resource(SagaOperationsView, "/SAGAOP/<command>", methods=['POST'], resource_class_kwargs={'appdatadir': appdatadir, 'sagacontroller':sagacontroller})
        api.add_resource(FrameView, "/FRAMES", resource_class_kwargs={'appdatadir': appdatadir, 'sagacontroller':sagacontroller})
        api.add_resource(FileView, "/FILES", resource_class_kwargs={'appdatadir': appdatadir, 'sagacontroller':sagacontroller})
        api.add_resource(SectionView, "/SECTION/<command>", resource_class_kwargs={'appdatadir': appdatadir, 'sagacontroller':sagacontroller})
        # api.add_resource(Reset, "/RESET", resource_class_kwargs={'appdatadir': appdatadir})
        api.add_resource(UserView, "/USER/<command>", resource_class_kwargs={'appdatadir': appdatadir, 'sagacontroller':sagacontroller})
        api.add_resource(MaintenanceView, "/MAINTENANCE/<command>", resource_class_kwargs={'appdatadir': appdatadir, 'sagacontroller':sagacontroller})
        api.add_resource(PermissionsView, "/PERMISSIONS/<command>", methods=['GET', 'POST'],
                         resource_class_kwargs={'appdatadir': appdatadir, 'sagacontroller':sagacontroller})
        api.add_resource(GeneralView, "/GENERAL/<command>", methods=['GET', 'POST'],
                         resource_class_kwargs={'appdatadir': appdatadir, 'webserverdir':webserverdir, 'sagauserdb':sagauserdb, 'sagacontroller':sagacontroller})
        api.add_resource(PingView, "/PING/<command>", methods=['POST'],
                         resource_class_kwargs={'appdatadir': appdatadir, 'webserverdir':webserverdir, 'sagauserdb':sagauserdb, 'sagacontroller':sagacontroller})


        return app
