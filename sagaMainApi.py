import os
import io
from flask import Flask,flash, request, redirect, url_for,send_from_directory , send_file, make_response, safe_join
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo
import json
import gridfs
import re
from SagaApp.Files import Files
from SagaApp.FrameView import FrameView
from SagaApp.ContainerView import ContainerView
from SagaApp.ResetView import Reset
# from ServerFunctions import *
# from user_management import ConfigClass, create_app
from SagaApp import app
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy

if __name__ == "__main__":
    api = Api(app)
    rootpath = os.path.dirname(__file__)

    # api.add_resource(ContainerView, "/CONTAINERS",  methods=['GET', 'POST'], resource_class_kwargs={'rootpath': rootpath})
    api.add_resource(ContainerView, "/CONTAINERS/<command>", methods=['GET', 'POST'],
                     resource_class_kwargs={'rootpath': rootpath})
    api.add_resource(FrameView, "/FRAMES", resource_class_kwargs={'rootpath': rootpath})
    api.add_resource(Files, "/FILES", resource_class_kwargs={'rootpath': rootpath})
    api.add_resource(Reset, "/RESET", resource_class_kwargs={'rootpath': rootpath})
    app.run(debug=True)