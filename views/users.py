import requests
from flask import (Blueprint, abort, flash, jsonify, redirect, render_template,
                   request, url_for, session)
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from jinja2 import TemplateNotFound
from sqlalchemy import desc, func, or_
from app import (BadSignature, BadTimeSignature, SignatureExpired, db, mail,
                 serializer,cipher_suite,app)
from forms import (LoginForm, ModifyProfileForm, RegisterForm,
                   ResetPasswordForm, SearchForm)
from models import PostModel, ReplyModel, UserModel, bcrypt, Analyze_Pages, Analyze_Session, TagModel, Notifications_Model, User_DevicesModel, Ip_Coordinates
from cryptography.fernet import Fernet
import os
from PIL import Image
from datetime import datetime
import datetime as dt
from analyze import hashlib, httpagentparser
from sqlalchemy import desc
import calendar
from analyze import GetSessionId, parseVisitator, getAnalyticsData
from webptools import webplib as webp
import socket
import smtplib
import dns.resolver
import urllib
from device_detector import DeviceDetector
from sqlalchemy.schema import Sequence

users_pages = Blueprint(
    'users',__name__,
    template_folder='../user_templates'
)

@users_pages.before_request
def views():
    getAnalyticsData()
    data = [request.path, GetSessionId(), str(datetime.now().replace(microsecond=0))]
    parseVisitator(data)
        
@users_pages.route("/login", methods=['GET','POST'])
def login():
    if request.method != 'POST':
        return redirect(url_for('home.home'))

    login = LoginForm(request.form)

    #if login.validate_on_submit() == False:
    #    return redirect(url_for('home.home'))

    user = db.session.query(UserModel).filter_by(name=str(login.username.data).lower().replace(' ','')).first()

    if user is None:
        user = db.session.query(UserModel).filter_by(email=str(login.username.data).lower().replace(' ','')).first()
    if user is None:
        flash("No user with that username", 'error')
        return redirect(url_for('home.home'))

    if bcrypt.check_password_hash(user.password, login.password.data) == False:
        flash("Wrong Password", 'error')
        return redirect("https://newapp.nl"+request.args.get('url'))

    userInfo = httpagentparser.detect(request.headers.get('User-Agent'))

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        userIP = request.environ['REMOTE_ADDR']
    else:
        userIP = request.environ['HTTP_X_FORWARDED_FOR']

    ip_user = db.session.query(Ip_Coordinates).filter_by(ip=userIP).first()

    if ip_user is None:
        resp = requests.get(('https://www.iplocate.io/api/lookup/{}').format(userIP))
        userLoc = resp.json()
        iso_code = userLoc['country_code']
        country_name = userLoc['country']
        rest = False
    else:
        resp = requests.get(
            ("https://restcountries.eu/rest/v2/alpha/{}").format(ip_user.location.iso_code))
        userLoc = resp.json()
        country_name = userLoc['name']
        iso_code = ip_user.location.iso_code
        rest = True

    if rest:
        userLanguage = userLoc['languages'][0]['iso639_1']
    else:
        api_2 = requests.get(
            ("https://restcountries.eu/rest/v2/alpha/{}").format(iso_code))
        result_2 = api_2.json()
        userLanguage = result_2['languages'][0]['iso639_1']
        
    if user.activated == False:
        flash("Account not activated", 'error')
    else:

        device_info = request.headers.get('User-Agent')
        device = DeviceDetector(device_info).parse()

        user_first_device = db.session.query(User_DevicesModel).filter_by(user=user.id).first()
        user_device = db.session.query(User_DevicesModel).filter_by(user=user.id).filter_by(device_model=device.device_model()).first()

        if user_first_device is None:
            new_device = User_DevicesModel(
                None,
                user.id,
                device.device_type(),
                device.device_model(),
                device.device_brand_name(),
                dt.datetime.now(),
                True,
                [userIP]
            )
            db.session.add(new_device)
            db.session.commit()
        elif user_device is None:
            new_device = User_DevicesModel(
                None,
                user.id,
                device.device_type(),
                device.device_model(),
                device.device_brand_name(),
                dt.datetime.now(),
                True,
                [userIP]
            )
            db.session.add(new_device)
            db.session.commit()
        else:
            if userIP in list(user_device.ip_address):
                user_device.last_access = dt.datetime.now()
                db.session.commit()
            else:
                ips = list(user_device.ip_address)
                ips.append(str(userIP))
                print(userIP)
                user_device.ip_address = ips
                user_device.last_access = dt.datetime.now()
                db.session.commit()

            # if check_device is None or check_device.activated == False:
            #     new_device = User_DevicesModel(
            #         None,
            #         user.id,
            #         device.device_type(),
            #         device.device_model(),
            #         device.device_brand_name(),
            #         dt.datetime.now(),
            #         False,
            #         [userIP]
            #     )
            #     db.session.add(new_device)
            #     db.session.commit()
            #     token = serializer.dumps(user.email,salt='confirm_device')
            #     msg = Message('Confirm Device', sender='contact@newapp.nl', recipients=[user.email])
            #     link = 'https://newapp.nl' + url_for('users.confirm_device',email=user.email ,token=token,id= db.session.execute(Sequence('user_devices_id_seq'))-1)
            #     msg.html = render_template('email_device.html',link=link,email='contact@newapp.nl')
            #     mail.send(msg)
            #     return redirect(url_for('users.check'))
            # elif check_device.activated:
            #     if check_device.device_type == 'computer':
            #         if userIP in list(check_device.ip_address):
            #             check_device.last_access = datetime.datetime.now
            #         else:
            #             token = serializer.dumps(user.email,salt='confirm_device')
            #             msg = Message('Confirm Device', sender='contact@newapp.nl', recipients=[user.email])
            #             link = 'https://newapp.nl' + url_for('users.confirm_device_ip',email=user.email ,token=token,id= db.session.execute(Sequence('user_devices_id_seq'))-1,ip=userIP)
            #             msg.html = render_template('email_device.html',link=link,email='contact@newapp.nl')
            #             mail.send(msg)
            #             return redirect(url_for('users.check'))
            #     else:
            #         check_device.last_access = dt.datetime.now()

        if login.remember.data:
            if request.MOBILE:
                login_user(user,remember=login.remember.data,duration=dt.timedelta(days=30))
            else:
                login_user(user,remember=login.remember.data,duration=dt.timedelta(days=1))
        else:
            login_user(user,remember=login.remember.data,duration=dt.timedelta(hours=1))
        flash("You were just logged in!", 'success')


    user.status = 'Online'
    user.status_color = '#00c413'
    user.ip_address = userIP
    user.browser = userInfo['browser']['name']
    user.country_name = str(country_name)
    user.country_flag = str(iso_code).lower()
    user.lang = str(userLanguage).lower()

    db.session.commit()
    return redirect("https://newapp.nl"+request.args.get('url'))

@users_pages.route("/logout")
def logout():
    if current_user.is_authenticated == False:
        return redirect(url_for('home.home'))
    user = db.session.query(UserModel).filter_by(name=current_user.name).first_or_404()
    user.status = 'Offline'
    user.status_color = '#cc1616'
    db.session.commit()
    logout_user()
    flash("You were just logged out!", 'success')
    return redirect(url_for('home.home'))

@users_pages.route("/register", methods=['GET','POST'])
def register():
    if request.method != 'POST':
        return redirect(url_for('home.home'))

    register = RegisterForm(request.form)

    #if register.validate_on_submit() == False:
     #   return redirect(url_for('home.home'))

    check = db.session.query(UserModel).filter_by(name=str(register.username.data).lower()).first()

    if check is not None:
        flash('Username taken', 'error')
        return redirect(url_for('home.home'))

    check = db.session.query(UserModel).filter_by(email=str(register.email.data).lower()).first()

    if check is not None:
        flash('Email taken', 'error')
        return redirect(url_for('home.home'))

    host = socket.gethostname()
    server = smtplib.SMTP()
    server.set_debuglevel(0)
    record = dns.resolver.query('emailhippo.com','MX')
    mxRecord = record[0].exchange
    mxRecord = str(mxRecord)
    server.connect(mxRecord)
    server.helo(host)
    server.mail('contact@newapp.nl')
    code,msg = server.rcpt(str(register.email.data))

    if code != 250:
        flash("This email doesn't exist.",'error')
        return redirect(url_for('home.home'))

    token = serializer.dumps(register.email.data,salt='register-confirm')
    userInfo = httpagentparser.detect(request.headers.get('User-Agent'))

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        userIP = request.environ['REMOTE_ADDR']
    else:
        userIP = request.environ['HTTP_X_FORWARDED_FOR']

    ip_user = db.session.query(Ip_Coordinates).filter_by(ip=userIP).first()

    if ip_user is None:
        resp = requests.get(
            ('https://www.iplocate.io/api/lookup/{}').format(userIP))
        userLoc = resp.json()
        iso_code = userLoc['country_code']
        country_name = userLoc['country']
        rest = False
    else:
        resp = requests.get(
            ("https://restcountries.eu/rest/v2/alpha/{}").format(ip_user.location.iso_code))
        userLoc = resp.json()
        county_name = userLoc['name']
        iso_code = ip_user.location.iso_code
        rest = True

    if rest:
        userLanguage = userLoc['languages'][0]['iso639_1']
    else:
        api_2 = requests.get(
            ("https://restcountries.eu/rest/v2/alpha/{}").format(iso_code))
        result_2 = api_2.json()
        userLanguage = result_2['languages'][0]['iso639_1']

    msg = Message('Confirm Email Registration', sender='contact@newapp.nl', recipients=[register.email.data])
    link = 'https://newapp.nl' + url_for('users.confirm_register',email=register.email.data ,token=token)
    msg.html = render_template('email_register.html',register=link,email='contact@newapp.nl')
    mail.send(msg)
    new_user = UserModel(
            None,
            None,
            str(register.username.data).lower(),
            register.realname.data,
            str(register.email.data).lower(),
            register.password.data,
            "https://www.component-creator.com/images/testimonials/defaultuser.png",
            None,
            None,
            None,
            False,
            userIP,
            userInfo['browser']['name'],
            str(country_name),
            str(iso_code).lower(),
            str(userLanguage).lower(),
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            'Light',
            None,
            None,
            None,
            'system',
            None
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

@users_pages.route('/register/confirm/device/<string:email>/<string:token>/<int:id>',  methods=['GET','POST'])
def confirm_device(email,token,id):
  if current_user.is_authenticated:
        return redirect(url_for('home.home'))

  try:
      email = serializer.loads(token,salt='confirm_device', max_age=300)
  except SignatureExpired:
      flash('Expired Token', 'error')
      return redirect(url_for('home.home'))
  except BadTimeSignature:
      flash('Invalid Token', 'error')
      return redirect(url_for('home.home'))
  except BadSignature:
      flash('Invalid Token', 'error')
      return redirect(url_for('home.home'))

  user = db.session.query(UserModel).filter_by(email=email).first()
  device = db.session.query(User_DevicesModel).filter_by(id=id).first()
  device.activated = True

  db.session.commit()
  login_user(user)

  flash("You were just logged in!", 'success')
  return redirect(url_for('home.home'))

@users_pages.route('/register/confirm/device/<string:email>/<string:token>/<int:id>/<string:ip>',  methods=['GET','POST'])
def confirm_device_ip(email,token,id,ip):
  if current_user.is_authenticated:
        return redirect(url_for('home.home'))

  try:
      email = serializer.loads(token,salt='confirm_device', max_age=300)
  except SignatureExpired:
      flash('Expired Token', 'error')
      return redirect(url_for('home.home'))
  except BadTimeSignature:
      flash('Invalid Token', 'error')
      return redirect(url_for('home.home'))
  except BadSignature:
      flash('Invalid Token', 'error')
      return redirect(url_for('home.home'))

  user = db.session.query(UserModel).filter_by(email=email).first()
  device = db.session.query(User_DevicesModel).filter_by(id=id).first()
  ips = device.ip_address
  ips.append(ip)
  device.ip_address = ips

  db.session.commit()
  login_user(user)

  flash("You were just logged in!", 'success')
  return redirect(url_for('home.home'))

@users_pages.route("/user/<string:name>")
def user(name):
    register = RegisterForm(request.form)
    loginf = LoginForm(request.form)
    reset = ResetPasswordForm(request.form)
    user = db.session.query(UserModel).filter_by(name=name).first_or_404()
    posts = db.session.query(PostModel).filter_by(user=user.id).order_by(desc(PostModel.id)).all()
    follow = db.session.query(UserModel).filter(UserModel.id.in_(user.follow)).limit(6).all()
    tags = db.session.query(TagModel).all()
    post_count = db.session.query(PostModel).filter_by(user=user.id).count()
    reply_count = db.session.query(ReplyModel).filter_by(user=user.id).count()
    location = db.session.query(Analyze_Session).filter_by(session=session['user']).first()

    if current_user.is_authenticated:
        post_views = 0
        for post in posts:
            p = db.session.query(Analyze_Pages).filter_by(name=urllib.parse.unquote(str(url_for('home.post',title=post.title,id=post.id)))).count()
            post_views += p


    if request.args.get('notification'):
        db.session.query(Notifications_Model).filter_by(id=request.args.get('notification')).delete()
        db.session.commit()

    if current_user.is_authenticated:
        return render_template('user_page.html',post_views=post_views,post_count=post_count,reply_count=reply_count,follow=follow,tags=tags,posts=posts,user=user,register=register,login=loginf, reset=reset,location=location)

    return render_template('user_page.html',follow=follow,tags=tags,posts=posts,user=user,register=register,login=loginf, reset=reset,location=location)


def save_img(user_id,type):
    #if(form_img.data):

    if type == 'profile':
        file_name, file_ext = os.path.splitext(request.files['avatarimg'].filename)
        users = db.session.query(UserModel).filter_by(id=user_id)
        picture_fn = 'user_' + str(user_id) + str(file_ext)
        picture_path = os.path.join(app.config['UPLOAD_FOLDER_PROFILE'], picture_fn)
    elif type == 'cover':
        file_name, file_ext = os.path.splitext(request.files['coverimg'].filename)
        users = db.session.query(UserModel).filter_by(id=user_id)
        picture_fn = 'user_' + str(user_id) + str(file_ext)
        picture_path = os.path.join(app.config['UPLOAD_FOLDER_PROFILE_COVER'], picture_fn)


    if type == 'profile':
        i = Image.open(request.files['avatarimg'])
        output_size = (500, 500)
        i.thumbnail(output_size)
    elif type == 'cover':
        i = Image.open(request.files['coverimg'])

    i.save(picture_path)

    if type == 'profile':
        webp.cwebp(os.path.join(app.config['UPLOAD_FOLDER_PROFILE'], picture_fn),os.path.join(app.config['UPLOAD_FOLDER_PROFILE'], 'user_' + str(user_id) + '.webp'), "-q 80")
        os.remove(os.path.join(app.config['UPLOAD_FOLDER_PROFILE'], picture_fn))
    elif type == 'cover':
        webp.cwebp(os.path.join(app.config['UPLOAD_FOLDER_PROFILE_COVER'], picture_fn),os.path.join(app.config['UPLOAD_FOLDER_PROFILE_COVER'], 'user_' + str(user_id) + '.webp'), "-q 80")
        os.remove(os.path.join(app.config['UPLOAD_FOLDER_PROFILE_COVER'], picture_fn))

    picture_fn = 'user_' + str(user_id) + '.webp'

    return picture_fn
    #return None


@users_pages.route('/user/<string:name>/settings', methods=['GET'])
def settings(name):
    if current_user.is_authenticated == False:
        return redirect(url_for('home.home'))

    profile = ModifyProfileForm(request.form)
    user = db.session.query(UserModel).filter_by(name=name).first()
    modify_prof = ModifyProfileForm(request.form)
    modify_prof.theme.default = user.theme
    modify_prof.genre.default = user.genre
    if user.theme_mode == 'system':
        modify_prof.theme_mode.default = "checked"
    modify_prof.process()
    return render_template('user_settings.html', profile=profile, user=user,modify_prof=modify_prof)

@users_pages.route("/user/modify_profile/id=<int:idm>", methods=['GET','POST'])
def modify_profile(idm):

    user = db.session.query(UserModel).filter_by(id=idm).first()

    if request.method != 'POST':
        return redirect(url_for('users.user',id=idm,name=user.name))

    modify_prof = ModifyProfileForm(request.form)

    user.email = modify_prof.email.data
    user.real_name = modify_prof.realname.data
    user.bio = modify_prof.bio.data
    user.profession = modify_prof.profession.data
    user.instagram = modify_prof.instagram.data
    user.facebook = modify_prof.facebook.data
    user.twitter = modify_prof.twitter.data
    user.github = modify_prof.github.data
    user.website = modify_prof.website.data

    if modify_prof.theme_mode.data == False:
        user.theme = modify_prof.theme.data
        user.theme_mode = 'manual'
    else:
        user.theme_mode = 'system'

    if request.MOBILE is not True:
        if request.files['avatarimg']:
            if  request.files.get('avatarimg', None):
                profile_file = save_img(user.id,'profile')
                user.avatar = 'https://newapp.nl'+url_for('static', filename='profile_pics/{}'.format(profile_file))

        if request.files['coverimg']:
            if  request.files.get('coverimg', None):
                profile_file = save_img(user.id,'cover')
                user.cover = 'https://newapp.nl'+url_for('static', filename='profile_cover/{}'.format(profile_file))

        if modify_prof.genre.data:
            user.genre = modify_prof.genre.data

    db.session.commit()
    return redirect(url_for('users.user',id=idm,name=user.name))

@users_pages.route('/confirm_email')
def check():
    users = db.session.query(UserModel).all()
    posts = db.session.query(PostModel).all()
    register = RegisterForm(request.form)
    login = LoginForm(request.form)
    reset = ResetPasswordForm(request.form)
    return render_template('confirm_email.html',users=users,posts=posts,register=register,login=login,reset=reset)

@users_pages.route('/password/reset', methods = ['GET','POST'])
def reset_password():
    reset = ResetPasswordForm(request.form)

    if current_user.is_authenticated:
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


@users_pages.route('/notifications')
def notifications():
    if current_user.is_authenticated == False:
        flash('You have to be logged in to post.', 'error')
        return redirect(url_for('home.home'))

    return render_template('notifications.html')

@users_pages.route('/direct')
def direct():
    if current_user.is_authenticated == False:
        flash('You have to be logged in to post.', 'error')
        return redirect(url_for('home.home'))

    return render_template('direct.html')



@users_pages.route("/git")
def get():
    response = requests.get(('https://api.github.com/users/{}/repos').format(current_user.github))
    login = response.json()
    return jsonify(login)


