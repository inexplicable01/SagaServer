# project/server/Config.py
# BASE = "http://fatpanda1985.pythonanywhere.com/"
BASE = "http://127.0.0.1:5000/"

# http://fatpanda1985.pythonanywhere.com/static/executable/Saga.exe
# https://www.sagaversioncontrol.com/

adminlogin = {'first_name':'Default',
                   'last_name':'Lee',
                   'email':'admin@example.com',
                    'password':'Password1',
}

import os
basedir = os.path.abspath(os.path.dirname(__file__))
# postgres_local_base = 'postgresql://postgres:@localhost/'
database_name = 'flask_jwt_auth'

ServerOrFront = 'Server'

typeInput='Input'
typeOutput='Output'
typeRequired='Required'

changenewfile = 'New File Header Added'
changemd5 = 'MD5 Changed'
changedate = 'Date Change Only'
changeremoved = 'File Header Removed'

SECTIONNAMEHOLDER = 'SECTIONNAMEHOLDER'
SECTIONDIDHOLDER = 'SECTIONDIDHOLDER'

worldmapid = 'fc925b23-30b8-4d77-9310-289b85ef8eb0'

class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'

    # Flask-SQLAlchemy settings
    # SQLALCHEMY_DATABASE_URI = 'mysql://FatPanda1985:Lowlevelpw01!@FatPanda1985.mysql.pythonanywhere-services.com/base.db'  # File-based SQL database
    SQLALCHEMY_DATABASE_URI ='sqlite:///basic_app_test.sqlite'
    SQLALCHEMY_BINDS = {
        'filerecords': 'sqlite:///filerecords.sqlite',
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # Avoids SQLAlchemy warning
    CONTAINERFOLDER = 'Container'
    FILEFOLDER = 'Files'
    # # Flask-User settings
    USER_APP_NAME = "Flask-User Basic App"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Enable email authentication
    USER_ENABLE_USERNAME = False  # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'sagaworkflow@gmail.com'
    MAIL_PASSWORD = 'stfujimmy'
    MAIL_DEBUG= True
    MAIL_DEFAULT_SENDER = 'sagaworkflow@gmail.com'

    EXECUTABLE= "/home/FatPanda1985/mysite/static/executable"

#
# class DevelopmentConfig(BaseConfig):
#     """Development configuration."""
#     DEBUG = True
#     BCRYPT_LOG_ROUNDS = 4
#     # SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name
#
#
# class TestingConfig(BaseConfig):
#     """Testing configuration."""
#     DEBUG = True
#     TESTING = True
#     BCRYPT_LOG_ROUNDS = 4
#     # SQLALCHEMY_DATABASE_URI = postgres_local_base + database_name + '_test'
#     PRESERVE_CONTEXT_ON_EXCEPTION = False
#
#
# class ProductionConfig(BaseConfig):
#     """Production configuration."""
#     SECRET_KEY = 'my_precious'
#     DEBUG = False
#     # SQLALCHEMY_DATABASE_URI = 'postgresql:///example'
