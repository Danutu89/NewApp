import requests
from flask import (Blueprint, abort, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import login_required, login_user, logout_user
from jinja2 import TemplateNotFound

from app import db
from forms import LoginForm, ModifyProfileForm, RegisterForm, SearchForm
from models import Gits, PostModel, ReplyModel, UserModel, bcrypt

users_pages = Blueprint(
    'users',__name__,
    template_folder='user_templates'
)


@users_pages.route("/login", methods=['GET','POST'])
def login():
    if request.method != 'POST':
        return redirect(url_for('home.home'))

    login = LoginForm(request.form)

    if login.validate_on_submit() == False:
        return redirect(url_for('home.home'))

    user = db.session.query(UserModel).filter_by(name=login.username.data).first()

    if user is None:
        user = db.session.query(UserModel).filter_by(email=login.username.data).first()
    if user is None:
        flash("No user with that username", 'error')
        return redirect(url_for('home.home'))

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
    if request.method != 'POST':
        return redirect(url_for('home.home'))
    
    register = RegisterForm(request.form)

    if register.validate_on_submit() == False:
        return redirect(url_for('home.home'))

    check = db.session.query(UserModel).filter_by(name=register.username.data).first()

    if check is not None:
        flash('Username taken', 'error')
        return redirect(url_for('home.home'))
    
    check = db.session.query(UserModel).filter_by(email=register.email.data).first()

    if check is not None:
        flash('Email taken', 'error')
        return redirect(url_for('home.home'))

    check = db.session.query(UserModel).filter_by(github_name=register.github.data).first()

    if check is not None:
        flash('GitHub account taken', 'error')
        return redirect(url_for('home.home'))

    git = requests.get(('https://api.github.com/users/{}').format(register.github.data))
    git_check = git.json()

    try:
        if git_check['login'] == register.github.data:
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
    except KeyError:
        flash('This username doesn`t exist', 'error')

    return redirect(url_for('home.home'))

@users_pages.route("/user/<string:name>/id=<int:id>")
def user(name,id):
    search = SearchForm(request.form)
    register = RegisterForm(request.form)
    loginf = LoginForm(request.form)
    modify_profile = ModifyProfileForm(request.form)
    user = db.session.query(UserModel).filter_by(id=id).first()
    post_count = db.session.query(PostModel).filter_by(user=id).count()
    reply_count = db.session.query(ReplyModel).filter_by(user=id).count()
    response = requests.get(('https://api.github.com/users/{}/repos').format(user.github_name))
    login = response.json()  # obtain the payload as JSON object
    repos = []
    lang = {}
    for gits in login:
        repos.append(Gits(gits['name'],gits['svn_url'],gits['description']))
        resp = requests.get(('https://api.github.com/repos/{}/{}/languages').format(user.github_name,gits['name']))
        respond = resp.json()
        lan = []
        for key in respond.keys():
            lan.append(key)
        lang[gits['name']]=lan
    return render_template('user_page.html',user=user,repos=repos,modify_profile=modify_profile,lang=lang,post_count=post_count,reply_count=reply_count,search=search,register=register,login=loginf)


@users_pages.route("/user/modify_profile/id=<int:idm>", methods=['GET','POST'])
def modify_profile(idm):
    if request.method != 'POST':
        return redirect(url_for('users.user'))

    modify_prof = ModifyProfileForm(request.form)

    if modify_prof.validate_on_submit() == False:
        return redirect(url_for('users.user'))

    user = db.session.query(UserModel).filter_by(id=idm).first()
    user.name = modify_prof.username.data
    user.email = modify_prof.email.data
    user.real_name = modify_prof.realname.data
    user.bio = modify_prof.bio.data
    user.avatar = modify_prof.avatar.data
    user.genre = modify_prof.genre.data
    db.session.commit()
    flash('Fields updated successfully', 'success')
    return redirect(url_for('users.user',id=idm,name=modify_profile.username.data))

@users_pages.route("/git")
def get():
    dany = 'Danutu89'
    response = requests.get(('https://api.github.com/users/{}/repos').format(dany))
    login = response.json()  # obtain the payload as JSON object
    return jsonify(login)
