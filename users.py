from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from jinja2 import TemplateNotFound
from flask_login import login_user, login_required, logout_user
from forms import RegisterForm,LoginForm


users_pages = Blueprint(
    'users',__name__,
    template_folder='user_templates'
)

from app import db, UserModel, bcrypt

@users_pages.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        login = LoginForm(request.form)
        if login.validate_on_submit():
            user = db.session.query(UserModel).filter_by(name=login.username.data).first()
            if user is None:
                user = db.session.query(UserModel).filter_by(email=login.username.data).first()
            if user is None:
                flash("No user with that username", 'error')
            else:
                if bcrypt.check_password_hash(user.password, login.password.data):
                    login_user(user)
                    flash("You were just logged in!", 'success')
                else:
                    flash("Wrong Password", 'error')
        
    return redirect(url_for('home.home'))

@users_pages.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        register = RegisterForm(request.form)
        if register.validate_on_submit:
            new_user = UserModel(
                None,
                None,
                register.username.data,
                register.email.data,
                register.password.data,
                None,
                None,
                None
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration completed successfully, now you can login')
            return redirect(url_for('home.home'))
    return redirect(url_for('home.home'))
    