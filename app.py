from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sitemap import Sitemap
import flask_whooshalchemyplus
from sqlalchemy import create_engine
from flask_marshmallow import Marshmallow

app = Flask(__name__)
ext = Sitemap(app=app)
ma = Marshmallow(app)

app.secret_key = '\xce,CH\xc0\xd2K9\xe3\x87\xa0Z\x19\x8a\xcd\xf9\x91\x94\xddN\xff\xaf;r\xef'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///newapp"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['WHOOSH_BASE'] = 'whoosh'
db = SQLAlchemy(app)
db_engine = create_engine('postgresql:///newapp')
db.configure_mappers()
db.create_all()
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "home.home"

from models import UserModel, PostModel

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(UserModel).filter(UserModel.id == int(user_id)).first()

from users import users_pages
from home import home_pages
from jsons import json_pages

app.register_blueprint(users_pages)
app.register_blueprint(home_pages)
app.register_blueprint(json_pages)
flask_whooshalchemyplus.whoosh_index(app,PostModel)
if __name__=="__main__":
    app.run(debug=False)



