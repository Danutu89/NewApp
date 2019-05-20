from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, jsonify
from jinja2 import TemplateNotFound
from flask_login import login_user, login_required, logout_user
from forms import RegisterForm,LoginForm,ModifyProfileForm
import requests


users_pages = Blueprint(
    'users',__name__,
    template_folder='user_templates'
)

from app import db, UserModel, bcrypt, Gits

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

@users_pages.route("/logout")
def logout():
    logout_user()
    flash("You were just logged out in!", 'success')
    return redirect(url_for('home.home'))

@users_pages.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        register = RegisterForm(request.form)
        if register.validate_on_submit:
            check = db.session.query(UserModel).filter_by(name=register.username.data).first()
            if  check is not None:
                flash('Username taken', 'error')
            else:
                check = db.session.query(UserModel).filter_by(email=register.email.data).first()
                if check is not None:
                    flash('Email taken', 'error')
                else:
                    new_user = UserModel(
                        None,
                        None,
                        register.username.data,
                        register.realname.data,
                        register.github.data,
                        register.email.data,
                        register.password.data,
                        None,
                        None,
                        None,
                        None
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    flash('Registration completed successfully, now you can login','success')
    return redirect(url_for('home.home'))

@users_pages.route("/user/<string:name>/id=<int:id>")
def user(name,id):
    modify_profile = ModifyProfileForm(request.form)
    user = db.session.query(UserModel).filter_by(id=id).first()
    response = requests.get(('https://api.github.com/users/{}/repos').format(user.github_name))
    login = response.json()  # obtain the payload as JSON object
    repos = []
    for gits in login:
        repos.append(Gits(gits['name'],gits['svn_url'],gits['language'],gits['description']))
    return render_template('user_page.html',user=user,repos=repos,modify_profile=modify_profile)


@users_pages.route("/user/modify_profile/id=<int:idm>", methods=['GET','POST'])
def modify_profile(idm):
    if request.method == 'POST':
        modify_profile = ModifyProfileForm(request.form)
        if modify_profile.validate_on_submit:
            user = db.session.query(UserModel).filter_by(id=idm).first()
            user.name = modify_profile.username.data
            user.email = modify_profile.email.data
            user.real_name = modify_profile.realname.data
            user.bio = modify_profile.bio.data
            user.avatar = modify_profile.avatar.data
            user.genre = modify_profile.genre.data
            db.session.commit()
            flash('Fields updated successfully', 'success')
    return redirect(url_for('users.user',id=idm,name=modify_profile.username.data))

@users_pages.route("/git")
def get():
        dany = 'Danutu89'
        response = requests.get(('https://api.github.com/users/{}/repos').format(dany))
        login = response.json()  # obtain the payload as JSON object
        print(dany)
        return jsonify(login)