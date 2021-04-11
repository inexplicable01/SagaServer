from flask import (
    Blueprint, flash, g, redirect, render_template,
    request, session, url_for
)

from SagaAPI import db
from SagaUser.UserModel import User
import os
from config import basedir
import yaml
from flask import current_app
from SagaCore.Section import Section

CONTAINERFOLDER = current_app.config['CONTAINERFOLDER']

auth_web_blueprint = Blueprint('auth_web', __name__, url_prefix='/auth_web')


@auth_web_blueprint.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        sectionid = request.form['sectionid']

        error = None
        if not email:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif User.query.filter_by(email=email).first() is not None:
            error = 'email {} is already registered.'.format(email)

        if "NewSection"==sectionid:
            section_name = request.form['sectionname']
            description = request.form['sectiondescription']
            newsection = Section.CreateNewSection(section_name, description= description)
            sectionid = newsection.sectionid
            section_name = newsection.sectionname
        else:
            sectionyaml = os.path.join(basedir,CONTAINERFOLDER,sectionid,'sectionstate.yaml')
            cursection = Section.LoadSectionyaml(sectionyaml)
            section_name =cursection.sectionname

        if error is None:
            user = User(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                section_id=sectionid,
                section_name=section_name
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth_web.login'))
        flash(error)

    sectioninfo= {}
    for section in os.listdir(os.path.join(basedir,'Container')):
        sectionyamlfn = os.path.join(basedir,'Container',section,'sectionstate.yaml')
        with open(sectionyamlfn,'r') as yml:
            sectionyaml = yaml.load(yml, Loader=yaml.FullLoader)
        print(sectionyaml)
        sectioninfo[section]=sectionyaml

    return render_template('authpages/register.html',sectioninfo=sectioninfo)

@auth_web_blueprint.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(
            email=email
        ).first()
        if user is None:
            error = 'Incorrect username.'
        error = None
        if user and user.password == password:
            auth_token = user.encode_auth_token(user.id)
            if auth_token:
                session.clear()
                session['user_id'] = user.id
                return redirect(url_for('webpages.hello'))
        else:
            error = 'Incorrect password.'

        flash(error)

    return render_template('authpages/login.html')

@auth_web_blueprint.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user =User.query.filter_by(
            id=user_id
        ).first()

@auth_web_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('webpages.hello'))