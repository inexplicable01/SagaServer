from flask import Blueprint, current_app, g, render_template
from SagaServerOperations.SagaController import SagaController
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
        sectionid = g.user.currentsectionid
        containerinfolist = SagaController.getContainersBySectionid(sectionid)

    return render_template('details.html', containerinfolist=containerinfolist.keys())

@webpages_blueprint.route('/instructions', methods=('GET', 'POST'))
def instructions():
    # message = 'Welcome to Saga Version Control  download Saga here'
    # return render_template('index.html', message=message)
    # users = User.query.filter_by(email='usercemail@gmail.com')
    return render_template('instructions.html')