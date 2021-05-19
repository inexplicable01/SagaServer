
from SagaAPI import db
from Config import ConfigClass, SECTIONNAMEHOLDER, SECTIONDIDHOLDER
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from flask_user import UserMixin
# from sqlalchemy.dialects.postgresql import UUID
import uuid

# db = SQLAlchemy()

class User(db.Model,UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')

    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

    # section_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    currentsectionid = db.Column(db.String(100))

    # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='user_roles')
    sections = db.relationship('Section', secondary='user_sections')

    def __init__(self, email, password, sectionname=SECTIONNAMEHOLDER,
                 sectionid=SECTIONDIDHOLDER, first_name='default',
                 last_name='Lee',admin=False,role='Agent'):
        self.email = email
        self.password = password
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        self.first_name = first_name
        self.last_name = last_name
        # self.section_name = section_name
        # self.sectionid = sectionid
        agentrole = Role.query.filter(Role.name == role).first()
        if agentrole:
            self.roles.append(agentrole)
        else:
            role=Role(name=role)
            self.roles.append(role)
            db.session.add(role)
            db.session.commit()

        usersection = Section.query.filter(Section.sectionid == sectionid).first()
        if usersection:
            self.sections.append(usersection)
            self.currentsectionid=usersection.sectionid
        else:
            section = Section(
                sectionid=sectionid,
                sectionname=sectionname,
            )
            self.sections.append(section)
            self.currentsectionid = section.sectionid
            db.session.add(section)
            db.session.commit()
            # d

    def printinfo(self):
        return {
        'email': self.email,
        'first_name': self.first_name,
        'last_name': self.last_name
        }

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            exp=datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=36000)
            payload = {
                'exp': exp,
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                ConfigClass.SECRET_KEY,
                algorithm='HS256'
            ), exp.timestamp()
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, ConfigClass.SECRET_KEY, algorithms='HS256')
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

    # Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

# Define the UserSections association table
class UserSections(db.Model):
    __tablename__ = 'user_sections'
    user_sectionid = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    section_id = db.Column(db.Integer(), db.ForeignKey('sections.id', ondelete='CASCADE'))

class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer(), primary_key=True)
    # children = db.relationship("User")
    sectionid = db.Column(db.String(100), unique=True)
    sectionname = db.Column(db.String(500), unique=True)

class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False
