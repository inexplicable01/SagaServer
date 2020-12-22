from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_user import current_user, login_required, roles_required, UserManager
import datetime

class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///basic_app.sqlite'  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = "Flask-User Basic App"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Enable email authentication
    USER_ENABLE_USERNAME = False  # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"
    # app.config[
    #     "MONGO_URI"] = "mongodb+srv://fatpanda:5WvwwkfDfUm2nqbd@cluster0.pg93y.mongodb.net/blog?retryWrites=true&w=majority"



app = Flask(__name__)
app.config.from_object(ConfigClass)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///basic_app_test.sqlite'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# from UserModel import User,Role
#     # # Create 'member@example.com' user with no roles
# # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
# if not Role.query.filter(Role.name == 'Admin').first():
#     db.session.add(Role(name='Admin'))
#     db.session.add(Role(name='Agent'))
#     db.session.commit()
# db.create_all()
from SagaApp.views import auth_blueprint
from UserModel import User,UserRoles, Role
db.create_all()

### user_manager No use right now, could be useful when we want to do API calls based on roles
user_manager = UserManager(app, db, User)

from SagaApp.InitBase import InitBase

InitBase(user_manager,db)

app.register_blueprint(auth_blueprint)