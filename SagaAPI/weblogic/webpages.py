from flask import Blueprint, current_app, g, render_template, safe_join
import os
from Config import basedir
from glob import glob
from SagaCore.Container import Container
# from SagaApp.db import get_db
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
        sectionid = g.user.sectionid
        for containerid in os.listdir(safe_join(basedir, CONTAINERFOLDER, sectionid)):
            containerfn = safe_join(basedir, CONTAINERFOLDER, sectionid, containerid, 'containerstate.yaml')
            if os.path.exists(containerfn):
                curcont = Container.LoadContainerFromYaml(containerfn)
                containerinfolist[containerid] = {'ContainerDescription': curcont.containerName,
                                                  'branches': []}
                for branch in os.listdir(safe_join(basedir, CONTAINERFOLDER, sectionid, containerid)):
                    if os.path.isdir(safe_join(basedir, CONTAINERFOLDER, sectionid, containerid, branch)):
                        containerinfolist[containerid]['branches'].append({'name': branch,
                                                                           'revcount': len(glob(
                                                                               safe_join(basedir, CONTAINERFOLDER, sectionid,
                                                                                         containerid, branch, '*')))})

    return render_template('details.html', containerinfolist=containerinfolist.keys())

@webpages_blueprint.route('/instructions', methods=('GET', 'POST'))
def instructions():
    # message = 'Welcome to Saga Version Control  download Saga here'
    # return render_template('index.html', message=message)
    # users = User.query.filter_by(email='usercemail@gmail.com')
    return render_template('instructions.html')