import requests
from flask import (Blueprint, abort, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from jinja2 import TemplateNotFound

from app import (BadSignature, BadTimeSignature, SignatureExpired, db, mail,
                 serializer,cipher_suite,app)
from forms import (LoginForm, ModifyProfileForm, RegisterForm,
                   ResetPasswordForm, SearchForm)
from models import Gits, PostModel, ReplyModel, UserModel, bcrypt

from cryptography.fernet import Fernet

import os

from PIL import Image

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

    if bcrypt.check_password_hash(user.password, login.password.data) == False:
        flash("Wrong Password", 'error')
        return redirect("https://newapp.nl"+request.args.get('url'))

    if user.activated == False:
      flash("Account not activated", 'error')
    else:
      login_user(user)
      flash("You were just logged in!", 'success')

    return redirect("https://newapp.nl"+request.args.get('url'))

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

    #if register.validate_on_submit() == False:
     #   return redirect(url_for('home.home'))

    check = db.session.query(UserModel).filter_by(name=register.username.data).first()

    if check is not None:
        flash('Username taken', 'error')
        return redirect(url_for('home.home'))
    
    check = db.session.query(UserModel).filter_by(email=register.email.data).first()

    if check is not None:
        flash('Email taken', 'error')
        return redirect(url_for('home.home'))

    if register.github.data:
      git = requests.get(('https://api.github.com/users/{}').format(register.github.data))
      git_check = git.json()

      try:
        if git_check['login'] == register.github.data:
          check = db.session.query(UserModel).filter_by(github_name=register.github.data).first()

          if check is not None:
              flash('GitHub account taken', 'error')
              return redirect(url_for('home.home'))
      except KeyError:
        flash('This username doesn`t exist', 'error')
        return redirect(url_for('home.home'))

    token = serializer.dumps(register.email.data,salt='register-confirm')

    msg = Message('Confirm Email Registration', sender='contact@newapp.nl', recipients=[register.email.data])
    link = 'https://newapp.nl' + url_for('users.confirm_register',email=register.email.data ,token=token)
    msg.html = render_template('email_register.html',register=link,email='contact@newapp.nl')
    mail.send(msg)
    new_user = UserModel(
            None,
            None,
            register.username.data,
            register.realname.data,
            register.github.data,
            register.email.data,
            register.password.data,
            "https://www.component-creator.com/images/testimonials/defaultuser.png",
            None,
            None,
            None,
            False
        )
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('users.check'))

@users_pages.route('/register/confirm/<string:email>/<string:token>',  methods=['GET','POST'])
def confirm_register(email,token):
  if current_user.is_authenticated:
        return redirect(url_for('home.home'))

  try:
      email = serializer.loads(token,salt='register-confirm', max_age=300)
  except SignatureExpired:
      flash('Expired Token', 'error')
      return redirect(url_for('home.home'))
  except BadTimeSignature:
      flash('Invalid Token', 'error')
      return redirect(url_for('home.home'))
  except BadSignature:
      flash('Invalid Token', 'error')
      return redirect(url_for('home.home'))

  users = db.session.query(UserModel).filter_by(email=email).first()
  users.activated = True
  db.session.commit()

  flash('Register successfully', 'success')
  return redirect(url_for('home.home'))

@users_pages.route("/user/<string:name>/id=<int:id>")
def user(name,id):
    search = SearchForm(request.form)
    register = RegisterForm(request.form)
    loginf = LoginForm(request.form)
    reset = ResetPasswordForm(request.form)
    modify_profile = ModifyProfileForm(request.form)
    user = db.session.query(UserModel).filter_by(id=id).first()
    post_count = db.session.query(PostModel).filter_by(user=id).count()
    reply_count = db.session.query(ReplyModel).filter_by(user=id).count()
    response = requests.get(('https://api.github.com/users/{}/repos').format(user.github_name))
    login = response.json()
    repos = []
    lang = {}
    if user.github_name:
      for gits in login:
          repos.append(Gits(gits['name'],gits['svn_url'],gits['description']))
          resp = requests.get(('https://api.github.com/repos/{}/{}/languages').format(user.github_name,gits['name']))
          respond = resp.json()
          lan = []
          for key in respond.keys():
              lan.append(key)
          lang[gits['name']] = lan
    return render_template('user_page.html',user=user,repos=repos,modify_profile=modify_profile,lang=lang,post_count=post_count,reply_count=reply_count,search=search,register=register,login=loginf, reset=reset)


def save_img(form_img,user_id):
    file_name, file_ext = os.path.splitext(form_img.data)
    users = db.session.query(UserModel).filter_by(id=user_id)
    picture_fn = 'user_' + users.id + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (140, 140)
    i = Image.open(form_img)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



@users_pages.route("/user/modify_profile/id=<int:idm>", methods=['GET','POST'])
def modify_profile(idm):
    if request.method != 'POST':
        return redirect(url_for('users.user'))

    modify_prof = ModifyProfileForm(request.form)

    if modify_prof.validate_on_submit() == False:
        return redirect(url_for('users.user'))
    print(modify_prof.avatarimg.data)
    user = db.session.query(UserModel).filter_by(id=idm).first()
    user.name = modify_prof.username.data
    user.email = modify_prof.email.data
    user.real_name = modify_prof.realname.data
    user.bio = modify_prof.bio.data

    if modify_prof.avatarimg.data:
        profile_file = save_img(modify_prof.avatarimg,user.id)
        user.avatar = profile_file
    else:
        user.avatar = modify_prof.avatar.data

    user.genre = modify_prof.genre.data
    db.session.commit()
    flash('Fields updated successfully', 'success')
    return redirect(url_for('users.user',id=idm,name=user.name))

@users_pages.route('/confirm_email')
def check():
    users = db.session.query(UserModel).all()
    posts = db.session.query(PostModel).all()
    search = SearchForm(request.form)
    register = RegisterForm(request.form)
    login = LoginForm(request.form)
    reset = ResetPasswordForm(request.form)
    return render_template('confirm_email.html',users=users,posts=posts,search=search,register=register,login=login,reset=reset)

@users_pages.route('/password/reset', methods = ['GET','POST'])
def reset_password():
    reset = ResetPasswordForm(request.form)

    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    if reset.validate_on_submit() == False:
        return redirect(url_for('home.home'))

    users = db.session.query(UserModel).filter_by(email=reset.email.data).first()

    if users is None:
        flash('Invalid Email', 'error')
        return redirect(url_for('home.home'))

    token = serializer.dumps(reset.email.data,salt='email-confirm')

    msg = Message('Confirm Password Reset', sender='contact@newapp.nl', recipients=[reset.email.data])
    link = 'https://newapp.nl' + url_for('users.confirm_password',email=reset.email.data ,token=token,passw=cipher_suite.encrypt(str(reset.password.data).encode()))
    msg.html = render_template('email_password.html',password=link,email='contact@newapp.nl')
    mail.send(msg)
    return redirect(url_for('users.check'))

@users_pages.route('/password/confirm/<string:email>/<string:token>/<string:passw>', methods = ['GET'])
def confirm_password(email,token,passw):
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    try:
        email = serializer.loads(token,salt='email-confirm', max_age=300)
    except SignatureExpired:
        flash('Expired Token', 'error')
        return redirect(url_for('home.home'))
    except BadTimeSignature:
        flash('Invalid Token', 'error')
        return redirect(url_for('home.home'))
    except BadSignature:
        flash('Invalid Token', 'error')
        return redirect(url_for('home.home'))

    users = db.session.query(UserModel).filter_by(email=email).first()
    users.password = bcrypt.generate_password_hash(cipher_suite.decrypt(str(passw).encode())).decode('utf-8')
    db.session.commit()

    flash('Password successfully changed', 'success')
    return redirect(url_for('home.home'))


@users_pages.route("/git")
def get():
    response = requests.get(('https://api.github.com/users/{}/repos').format(current_user.github_name))
    login = response.json()
    return jsonify(login)

@users_pages.route('/admin')
@login_required
def admin():
    if current_user.role != 10:
      return redirect(url_for('home.home'))
    users = db.session.query(UserModel).all()
    posts = db.session.query(PostModel).all()
    search = SearchForm(request.form)
    register = RegisterForm(request.form)
    login = LoginForm(request.form)
    return render_template('admin.html',users=users,posts=posts,search=search,register=register,login=login)