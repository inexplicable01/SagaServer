from flask.views import MethodView
from flask import Blueprint, current_app, g, request, make_response, jsonify, render_template, safe_join
import os
from config import ConfigClass, basedir
from SagaApp import db
from glob import glob
from SagaApp.Container import Container
# from SagaApp.db import get_db
from SagaApp.UserModel import User ,BlacklistToken
# from SagaApp.ContainerView import ContainerView

webpages_blueprint = Blueprint('webpages', __name__)
CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']
FILEFOLDER = current_app.config['FILEFOLDER']

@webpages_blueprint.route('/', methods=('GET', 'POST'))
def hello():
    # message = 'Welcome to Saga Version Control  download Saga here'
    # return render_template('index.html', message=message)
    # users = User.query.filter_by(email='usercemail@gmail.com')
    return render_template('landingPage.html')

@webpages_blueprint.route('/details', methods=('GET', 'POST'))
def details():
    # message = 'Welcome to Saga Version Control  download Saga here'
    # return render_template('index.html', message=message)
    # users = User.query.filter_by(email='usercemail@gmail.com')
    containerinfolist = {}
    if g.user is not None:
        gid = g.user.section_id
        for containerid in os.listdir(safe_join(basedir, CONTAINERFOLDER, gid)):
            containerfn = safe_join(basedir, CONTAINERFOLDER, gid, containerid, 'containerstate.yaml')
            if os.path.exists(containerfn):
                curcont = Container.LoadContainerFromYaml(containerfn)
                containerinfolist[containerid] = {'ContainerDescription': curcont.containerName,
                                                  'branches': []}
                for branch in os.listdir(safe_join(basedir, CONTAINERFOLDER, gid, containerid)):
                    if os.path.isdir(safe_join(basedir, CONTAINERFOLDER, gid, containerid, branch)):
                        containerinfolist[containerid]['branches'].append({'name': branch,
                                                                           'revcount': len(glob(
                                                                               safe_join(basedir, CONTAINERFOLDER, gid,
                                                                                         containerid, branch, '*')))})

    return render_template('details.html', containerinfolist=containerinfolist.keys())

@webpages_blueprint.route('/instructions', methods=('GET', 'POST'))
def instructions():
    # message = 'Welcome to Saga Version Control  download Saga here'
    # return render_template('index.html', message=message)
    # users = User.query.filter_by(email='usercemail@gmail.com')
    return render_template('instructions.html')