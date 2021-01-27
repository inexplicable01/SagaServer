# project/server/config.py

import os
basedir = os.path.abspath(os.path.dirname(__file__))
# postgres_local_base = 'postgresql://postgres:@localhost/'
database_name = 'flask_jwt_auth'

typeInput='Input'
typeOutput='Output'
typeRequired='Required'

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
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # Avoids SQLAlchemy warning
    CONTAINERFOLDER = 'Container'

    # # Flask-User settings
    USER_APP_NAME = "Flask-User Basic App"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Enable email authentication
    USER_ENABLE_USERNAME = False  # Disable username authentication
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"

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
