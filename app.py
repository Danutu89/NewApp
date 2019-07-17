from flask import Flask, flash, redirect, render_template, request, url_for,send_from_directory, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import flask_whooshalchemy
from sqlalchemy import create_engine
from marshmallow import fields
from flask_marshmallow import Marshmallow
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature, BadSignature
from flask_mail import Mail
import os
from cryptography.fernet import Fernet


key_c = #Key
key_cr = #Key

key_jwt = {
  "kty": "oct",
  "use": "enc",
  "kid": "1",
  "k": #Key
  "alg": #Algorithm
}

app = Flask(__name__)
ma = Marshmallow(app)
serializer = URLSafeTimedSerializer(key_c)


app.secret_key = key_c
app.config['SQLALCHEMY_DATABASE_URI'] = #Database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['WHOOSH_BASE'] = 'whoosh'
app.config['MAIL_SERVER'] = #Server
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = #Email
app.config['MAIL_PASSWORD'] = #Pass
app.config['JWT_ALGORITHM'] = #Algorithm
db = SQLAlchemy(app)
mail = Mail(app)
db_engine = create_engine(#Database)
db.configure_mappers()
db.create_all()
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "home.home"

cipher_suite = Fernet(key_cr)

from models import UserModel, PostModel

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(UserModel).filter(UserModel.id == int(user_id)).first()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path,
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

from users import users_pages
from home import home_pages
from jsons import json_pages

app.register_blueprint(users_pages)
app.register_blueprint(home_pages)
app.register_blueprint(json_pages)

flask_whooshalchemy.whoosh_index(app,PostModel)

def Launched():
    print ('NewApp Launched successfully')
    print ('Security keys')
    print ('Session keys')
    print (key_c)
    print ('Cryptography key')
    print (key_cr)

if __name__=="__main__":
    Launched()
    app.run(debug=False)



