from SagaAPI import db
from Config import ConfigClass, SECTIONNAMEHOLDER, SECTIONDIDHOLDER
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from flask_user import UserMixin

class FileRecord(db.Model,UserMixin):
    __tablename__ = 'filerecords'
    __bind_key__ = 'filerecords'

    md5 = db.Column(db.String(100), primary_key=True)
    # active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    #
    # # User authentication information. The collation='NOCASE' is required
    # # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    # # email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    # # email_confirmed_at = db.Column(db.DateTime())
    # # password = db.Column(db.String(255), nullable=False, server_default='')
    #
    # committedon = db.Column(db.DateTime, nullable=False)
    filename = db.Column(db.String(100, collation='NOCASE'), nullable=False, default=False)

    # User information
    revnum = db.Column(db.Integer, nullable=False, server_default='')
    containerid = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    containername = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

    # # section_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    # # sectionid = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    #
    # # Define the relationship to Role via UserRoles
    # roles = db.relationship('Role', secondary='user_roles')
    # sections = db.relationship('Section', secondary='user_sections')

    def __init__(self, md5, filename,revnum,containerid,containername):
        self.md5 = md5
        self.filename = filename
        self.revnum = revnum
        self.containerid = containerid
        self.containername = containername
        # self.registered_on = datetime.datetime.utcnow()
        # self.admin = admin
        # self.first_name = first_name
        # self.last_name = last_name
        # self.section_name = section_name
        # self.sectionid = sectionid
        # db.session.add(role)
        # db.session.commit()

