from app import db, db_engine
import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app import bcrypt
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserModel(Base):

    __tablename__ = 'users'

    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key = True)
    join_date = db.Column(db.Date, primary_key = False, default = datetime.datetime.now)
    name = db.Column(db.String(50), primary_key = False)
    email = db.Column(db.String(50), primary_key = False)
    password = db.Column(db.String(255), primary_key = False)
    avatar = db.Column(db.String, primary_key = False, default = 'None')
    genre = db.Column(db.String, primary_key = False, default = 'None')
    role = db.Column(db.Integer, ForeignKey('roles.id') ,default = 0)

    def __init__(self,id,join_date,name,email,password,avatar,genre,role):
        self.id = id
        self.join_date = join_date
        self.name = name
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.avatar = avatar
        self.genre = genre
        self.role = role

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return ('<name {}').format(self.name)

class RoleModel(Base):

    __tablename__ = 'roles'

    id = db.Column(db.Integer, db.Sequence('role_id_seq'), primary_key = True)
    name = db.Column(db.String(30), primary_key = False)

    user = relationship("UserModel", backref="roleinfo")

    def __init__(self,id,name):
        self.id = id
        self.name = name

    def __repr__(self):
        return ('<name {}').format(self.name)

Base.metadata.create_all(db_engine, Base.metadata.tables.values(),checkfirst=True)