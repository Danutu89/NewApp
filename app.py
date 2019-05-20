from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from users import users_pages
from home import home_pages
from sqlalchemy import create_engine

app = Flask(__name__)

app.register_blueprint(users_pages)
app.register_blueprint(home_pages)

app.secret_key = '\xce,CH\xc0\xd2K9\xe3\x87\xa0Z\x19\x8a\xcd\xf9\x91\x94\xddN\xff\xaf;r\xef'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///newapp"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = "True"


db = SQLAlchemy(app)
db_engine = create_engine('postgresql:///newapp')
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "home.home"

from models import UserModel, Gits

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(UserModel).filter(UserModel.id == int(user_id)).first()

if __name__=="__main__":
    app.run(debug=True)



