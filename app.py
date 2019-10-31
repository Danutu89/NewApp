from flask import Flask, flash, redirect, render_template, request, url_for, send_file, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from sqlalchemy import create_engine
from marshmallow import fields
from flask_marshmallow import Marshmallow
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature, BadSignature
from flask_mail import Mail
import os
from cryptography.fernet import Fernet
import logging
import datetime as time
from forms import SearchForm, LoginForm, RegisterForm, ResetPasswordForm
from retinasdk import FullClient
from flask_cors import CORS
import eventlet
import redis
from celery import Celery
from elasticsearch import Elasticsearch
from flask_login import logout_user
from flask_compress import Compress
from flask_mobility import Mobility
from werkzeug.wrappers import BaseRequest
from werkzeug.wsgi import responder
from werkzeug.exceptions import HTTPException, NotFound
from pywebpush import webpush, WebPushException

key_c = '\xce,CH\xc0\xd2K9\xe3\x87\xa0Z\x19\x8a\xcd\xf9\x91\x94\xddN\xff\xaf;r\xef'
key_cr = b'vgF_Yo8-IutJs-AcwWPnuNBgRSgncuVo1yfc9uqSiiU='
key_jwt = {
  "kty": "oct",
  "use": "enc",
  "kid": "1",
  "k": "mRo48tU4ebP6jIshqaoNf2HAnesrCGHm",
  "alg": "HS256"
}

app = Flask(__name__)

eventlet.monkey_patch()
ma = Marshmallow(app)
Mobility(app)
serializer = URLSafeTimedSerializer(key_c)

app.secret_key = key_c
app.config['SESSION_TYPE'] = 'filesystem'
app.config['ELASTISEARCH_URL'] = 'http://localhost:9200'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///newapp"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['WHOOSH_BASE'] = 'whoosh'
app.config['MAIL_SERVER'] = 'smtp.zoho.eu'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'contact@newapp.nl'
app.config['MAIL_PASSWORD'] = 'ACmilan89'
app.config['JWT_ALGORITHM'] = key_jwt['alg']
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_FILE_THRESHOLD'] = 100
app.config['UPLOAD_FOLDER_PROFILE'] = app.root_path + '/static/profile_pics'
app.config['UPLOAD_FOLDER_PROFILE_COVER'] = app.root_path + '/static/profile_cover'
app.config['UPLOAD_FOLDER_POST'] = app.root_path + '/static/thumbnail_post'
app.config['UPLOAD_FOLDER_IMAGES'] = app.root_path + '/static/images/posts'
app.config['UPLOAD_FOLDER_PODCAST_SERIES'] = app.root_path + '/static/images/podcast_series'
app.config['CELERY_BROKER_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = app.config['CELERY_BROKER_URL']
app.config['REDIS_URL'] = os.environ.get('REDIS_URL')
app.config['COMPRESS_MIMETYPES'] =  ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

Compress(app)
redis_sv = redis.Redis()
es = Elasticsearch(app.config['ELASTISEARCH_URL'])
celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
Session(app)
db = SQLAlchemy(app)
mail = Mail(app)
db_engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'),echo=False)
db.configure_mappers()
db.create_all()
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

translate = FullClient("7eaa96e0-be79-11e9-8f72-af685da1b20e",apiServer="http://api.cortical.io/rest", retinaName="en_associative")

login_manager.login_view = "home.home"
login_manager.session_protection = "strong"

cipher_suite = Fernet(key_cr)

@app.route('/sw.js')
def service_worker():
    return send_file(app.root_path+'/static/sw.js')

from models import UserModel, PostModel

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(UserModel).filter(UserModel.id == int(user_id)).first()

@app.errorhandler(404)
def not_found_error(error):
  users = db.session.query(UserModel).all()
  posts = db.session.query(PostModel).all()
  search = SearchForm(request.form)
  register = RegisterForm(request.form)
  login = LoginForm(request.form)
  reset = ResetPasswordForm(request.form)
  error_check = True
  return render_template('error_code.html',code=404,error='Sorry Page not found!',reset=reset,users=users,posts=posts,error_check=error_check,search=search,register=register,login=login)

@app.errorhandler(500)
def server_error(error):
  users = db.session.query(UserModel).all()
  posts = db.session.query(PostModel).all()
  search = SearchForm(request.form)
  register = RegisterForm(request.form)
  login = LoginForm(request.form)
  reset = ResetPasswordForm(request.form)
  error_check = True
  return render_template('error_code.html',code=500,error='Server error!',reset=reset,error_check=error_check,users=users,posts=posts,search=search,register=register,login=login)

@responder
def application(environ, start_response):
    request = BaseRequest(environ)
    try:
        return not_found_error(404)
    except HTTPException as e:
        return not_found_error(404)

from views.users import users_pages
from views.home import home_pages
from views.jsons import json_pages
from views.admin import admin_pages

app.register_blueprint(users_pages)
app.register_blueprint(admin_pages)
app.register_blueprint(home_pages)
app.register_blueprint(json_pages)
app.register_blueprint(admin_pages)

#flask_whooshalchemy.whoosh_index(app,PostModel)

gunicorn_error_logger = logging.getLogger('gunicorn.info')

app.logger.setLevel(logging.INFO)
app.logger.info('NewApp Launched successfully')
app.logger.info('Security keys')
app.logger.info('Session keys')
app.logger.info(key_c)
app.logger.info('Cryptography key')
app.logger.info(key_cr)
app.logger.info('JWT Key')
app.logger.info(key_jwt['k'])
app.logger.info('JWT Algorithm')
app.logger.info(key_jwt['alg'])

""" logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO) """

def make_celery(app):
  celery.conf.update(app.config)
  TaskBase = celery.Task
  class ContextTask(TaskBase):
      abstract = True
      def __call__(self, *args, **kwargs):
          with app.app_context():
              return TaskBase.__call__(self, *args, **kwargs)
  celery.Task = ContextTask
  return celery


celery = make_celery(app)

if __name__=="__main__":
    app.jinja_env.cache = {}
    socket.run(app, threading=True);
