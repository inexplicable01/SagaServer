import yaml
import sys
# project/server/Config.py
BASE = "http://fatpanda1985.pythonanywhere.com/"
# BASE = "http://127.0.0.1:5000/"

version_num = 0.1

# http://fatpanda1985.pythonanywhere.com/static/executable/Saga.exe
# https://www.sagaversioncontrol.com/

adminlogin = {'first_name':'Default',
                   'last_name':'Lee',
                   'email':'admin@example.com',
                    'password':'Password1',
}

waichak = {'first_name':'Waichak',
                   'last_name':'Luk',
                   'email':'waichak.luk@gmail.com',
                    'password':'passwordW',
}


import os

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

if os.path.exists('localConfig.txt'):
    with open('localConfig.txt','r') as file:
        localconfig = yaml.load(file, Loader=yaml.FullLoader)
else:
    raise('Missing localConfig.txt. Abort!')

if 'APPFolder' in localconfig.keys():
    appdatadir = localconfig['APPFolder']
else:
    appdatadir = os.path.abspath(os.path.dirname(__file__))

if 'webserverdir' in localconfig.keys():
    if localconfig['webserverdir']=='here':
        webserverdir = os.path.abspath(os.path.dirname(__file__))
    else:
        webserverdir = localconfig['webserverdir']
else:
    webserverdir = os.path.abspath(os.path.dirname(__file__))

if 'port' in localconfig.keys():
    port = str(localconfig['port'])
else:
    port = str(9500)

if 'dbinitializeryamlfile' in localconfig.keys():
    dbinitializeryamlfile = localconfig['dbinitializeryamlfile']
else:
    dbinitializeryamlfile = 'sagadb.yaml'


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

    if sys.platform =='win32':
        sqlitepath = 'sqlite:///'+appdatadir
    elif sys.platform in ['linux','linux2']:
        sqlitepath = 'sqlite://' + appdatadir
    else:
        raise('have not prepared to run on this system. Currently only supporting windows and linux')
    # Flask-SQLAlchemy settings
    # SQLALCHEMY_DATABASE_URI = 'mysql://FatPanda1985:Lowlevelpw01!@FatPanda1985.mysql.pythonanywhere-services.com/base.db'  # File-based SQL database
    SQLALCHEMY_DATABASE_URI =sqlitepath+'/basic_app_test.sqlite'
    SQLALCHEMY_BINDS = {
        'filerecords': sqlitepath +'/filerecords.sqlite',
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
