import requests
from flask import (Blueprint, abort, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from jinja2 import TemplateNotFound

from app import (BadSignature, BadTimeSignature, SignatureExpired, db, mail,
                 serializer)
from forms import (LoginForm, ModifyProfileForm, RegisterForm,
                   ResetPasswordForm, SearchForm)
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
            flash('Registration completed successfully, now you can login', 'success')
    except KeyError:
        flash('This username doesn`t exist', 'error')

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
    for gits in login:
        repos.append(Gits(gits['name'],gits['svn_url'],gits['description']))
        resp = requests.get(('https://api.github.com/repos/{}/{}/languages').format(user.github_name,gits['name']))
        respond = resp.json()
        lan = []
        for key in respond.keys():
            lan.append(key)
        lang[gits['name']] = lan
    return render_template('user_page.html',user=user,repos=repos,modify_profile=modify_profile,lang=lang,post_count=post_count,reply_count=reply_count,search=search,register=register,login=loginf, reset=reset)


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

    msg = Message('Confirm Password Reset', sender='dany89ytro@gmail.com', recipients=[reset.email.data])
    link = 'https://newapp.nl' + url_for('users.confirm_password',email=reset.email.data ,token=token,passw=reset.password.data)
    msg.html = '''<html xmlns="http://www.w3.org/1999/xhtml"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  '''+'''<style type="text/css" rel="stylesheet" media="all">
    /* Base ------------------------------ */
    *:not(br):not(tr):not(html) {
      font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif;
      -webkit-box-sizing: border-box;
      box-sizing: border-box;
    }
    body {
      width: 100% !important;
      height: 100%;
      margin: 0;
      line-height: 1.4;
      background-color: #F5F7F9;
      color: #839197;
      -webkit-text-size-adjust: none;
    }
    a {
      color: #414EF9;
    }
    /* Layout ------------------------------ */
    .email-wrapper {
      width: 100%;
      margin: 0;
      padding: 0;
      background-color: #F5F7F9;
    }
    .email-content {
      width: 100%;
      margin: 0;
      padding: 0;
    }
    /* Masthead ----------------------- */
    .email-masthead {
      padding: 25px 0;
      text-align: center;
    }
    .email-masthead_logo {
      max-width: 400px;
      border: 0;
    }
    .email-masthead_name {
      font-size: 16px;
      font-weight: bold;
      color: #839197;
      text-decoration: none;
      text-shadow: 0 1px 0 white;
    }
    /* Body ------------------------------ */
    .email-body {
      width: 100%;
      margin: 0;
      padding: 0;
      border-top: 1px solid #E7EAEC;
      border-bottom: 1px solid #E7EAEC;
      background-color: #FFFFFF;
    }
    .email-body_inner {
      width: 570px;
      margin: 0 auto;
      padding: 0;
    }
    .email-footer {
      width: 570px;
      margin: 0 auto;
      padding: 0;
      text-align: center;
    }
    .email-footer p {
      color: #839197;
    }
    .body-action {
      width: 100%;
      margin: 30px auto;
      padding: 0;
      text-align: center;
    }
    .body-sub {
      margin-top: 25px;
      padding-top: 25px;
      border-top: 1px solid #E7EAEC;
    }
    .content-cell {
      padding: 35px;
    }
    .align-right {
      text-align: right;
    }
    /* Type ------------------------------ */
    h1 {
      margin-top: 0;
      color: #292E31;
      font-size: 19px;
      font-weight: bold;
      text-align: left;
    }
    h2 {
      margin-top: 0;
      color: #292E31;
      font-size: 16px;
      font-weight: bold;
      text-align: left;
    }
    h3 {
      margin-top: 0;
      color: #292E31;
      font-size: 14px;
      font-weight: bold;
      text-align: left;
    }
    p {
      margin-top: 0;
      color: #839197;
      font-size: 16px;
      line-height: 1.5em;
      text-align: left;
    }
    p.sub {
      font-size: 12px;
    }
    p.center {
      text-align: center;
    }
    /* Buttons ------------------------------ */
    .button {
      display: inline-block;
      width: 200px;
      background-color: #414EF9;
      border-radius: 3px;
      color: #ffffff;
      font-size: 15px;
      line-height: 45px;
      text-align: center;
      text-decoration: none;
      -webkit-text-size-adjust: none;
      mso-hide: all;
    }
    .button--green {
      background-color: #28DB67;
    }
    .button--red {
      background-color: #FF3665;
    }
    .button--blue {
        font-family: inherit;
        text-decoration: none;
        padding: 5px;
        color: white;
        background-color: #2C3E50;
    }
    /*Media Queries ------------------------------ */
    @media only screen and (max-width: 600px) {
      .email-body_inner,
      .email-footer {
        width: 100% !important;
      }
    }
    @media only screen and (max-width: 500px) {
      .button {
        width: 100% !important;
      }
    }
  </style>'''+'''
  <title>Verify your new email address</title>
</head>
<body>
  <table class="email-wrapper" width="100%" cellpadding="0" cellspacing="0">
    <tbody><tr>
      <td align="center">
        <table class="email-content" width="100%" cellpadding="0" cellspacing="0">
          <!-- Logo -->
          <tbody><tr>
            <td class="email-masthead">
              <a class="email-masthead_name">NewApp</a>
            </td>
          </tr>
          <!-- Email Body -->
          <tr>
            <td class="email-body" width="100%">
              <table class="email-body_inner" align="center" width="570" cellpadding="0" cellspacing="0">
                <!-- Body content -->
                <tbody><tr>
                  <td class="content-cell">
                    <h1>Password Reset Request</h1>
                    <p>You recently requested that we change your password. Click the link to verify this is the right email.</p>
                    <!-- Action -->
                    <table class="body-action" align="center" width="100%" cellpadding="0" cellspacing="0">
                      <tbody><tr>
                        <td align="center">
                          <div>
                            <a href="{}" class="button button--blue">Change Password</a>
                          </div>
                        </td>
                      </tr>
                    </tbody></table>
                    <p>If you didn't request a change to your password, please let us know at <a href="{}">{}</a>.</p>
                    <p>Thanks,<br>The NewApp Team</p>
                    <!-- Sub copy -->
                    <table class="body-sub">
                      <tbody><tr>
                        <td>
                          <p class="sub">If you’re having trouble clicking the button, copy and paste the URL below into your web browser.
                          </p>
                          <p class="sub"><a href="{}">{}</a></p>
                        </td>
                      </tr>
                    </tbody></table>
                  </td>
                </tr>
              </tbody></table>
            </td>
          </tr>
          <tr>
            <td>
              <table class="email-footer" align="center" width="570" cellpadding="0" cellspacing="0">
                <tbody><tr>
                  <td class="content-cell">
                    <p class="sub center">
                      NewApp, Inc.
                      <br></p>
                  </td>
                </tr>
              </tbody></table>
            </td>
          </tr>
        </tbody></table>
      </td>
    </tr>
  </tbody></table>


</body></html>'''.format(link,'dany89yt@yahoo.com','dany89yt@yahoo.com',link,link)
    mail.send(msg)

    flash('Check your email for the password reset request', 'success')
    return redirect(url_for('home.home'))

@users_pages.route('/password/confirm/<string:email>/<string:token>/<string:passw>', methods = ['GET'])
def confirm_password(email,token,passw):
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    try:
        email = serializer.loads(token,salt='email-confirm', max_age=20)
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
    users.password = bcrypt.generate_password_hash(passw).decode('utf-8')
    db.session.commit()

    flash('Pasword successfully changed', 'success')
    return redirect(url_for('home.home'))


@users_pages.route("/git")
def get():
    response = requests.get(('https://api.github.com/users/{}/repos').format(current_user.github_name))
    login = response.json()
    return jsonify(login)

@users_pages.route('/admin')
@login_required
def admin():
    users = db.session.query(UserModel).all()
    posts = db.session.query(PostModel).all()
    search = SearchForm(request.form)
    register = RegisterForm(request.form)
    login = LoginForm(request.form)
    return render_template('admin.html',users=users,posts=posts,search=search,register=register,login=login)
