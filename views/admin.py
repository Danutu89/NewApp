import calendar
import datetime as dt
import os
from datetime import datetime
import collections
import requests
from cryptography.fernet import Fernet
from flask import (Blueprint, abort, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import desc, func, or_

from analyze import hashlib, httpagentparser
from app import  cipher_suite, db,app
from models import (Analyze_Pages, Analyze_Session, PostModel,
                    ReplyModel, TagModel, UserModel, bcrypt, Podcast_SeriesModel)
from sqlalchemy.schema import Sequence
from PIL import Image
from webptools import webplib as webp

admin_pages = Blueprint(
    'admin',__name__,
    template_folder='../admin_templates'
)

class CustomDict(dict):

    def __init__(self): 
        self = dict() 

    def add(self, key, value): 
        self[key] = value 

    def __missing__(self, key):
        value = self[key] = type(self)() # retain local pointer to value
        return value 

@admin_pages.route('/admin/main')
@login_required
def main():
    if current_user.roleinfo.admin_panel_permission == False:
      return redirect(url_for('home.home'))
      
    users = db.session.query(UserModel).all()
    posts = db.session.query(PostModel).all()
    sessions = db.session.query(Analyze_Session).order_by(Analyze_Session.id).all()
    now = datetime.now()
    sess = {}
    sess_old = {}
    label_days = []
    referer = CustomDict()
    country = CustomDict()
    countries = CustomDict()
    shares = {'old': 0, 'new': 0, 'perc': 0}
    per_devices = {'mobile': 0, 'computer': 0}
    devices_now = {'Mobile' : 0, 'Computer': 0}
    devices_old = {'Mobile' : 0, 'Computer': 0}
    months = {
        '01' : 'Junuary',
        '02' : 'February',
        '03' : 'March',
        '04' : 'April',
        '05' : 'May',
        '06' : 'June',
        '07' : 'July',
        '08' : 'August',
        '09' : 'September',
        '10' : 'October',
        '11' : 'November',
        '12' : 'December'
        }

    back_days = now - dt.timedelta(days = 15)
    back_perc = back_days - dt.timedelta(days = 15)
    pages = db.session.query(Analyze_Pages.name,func.count(Analyze_Pages.name).label('views')).filter(Analyze_Pages.first_visited.between('{}-{}-{}'.format(back_days.year,back_days.month,back_days.day), '{}-{}-{}'.format(now.year,now.month,now.day))).group_by(Analyze_Pages.name).order_by(
    func.count(Analyze_Pages.name).desc()).limit(10).all()
    label_days.clear()
    for session in sessions:
        if session.referer is not None:
            year, month, day = str(session.created_at).split("-")
            date = dt.datetime(int(year),int(month),int(day))
            if int(year) == int(now.year):
                if date <= now and date >= back_days and session.bot == True:
                    if str(session.browser) == 'TwitterBot' or str(session.browser) == 'FacebookExternalHit':
                        shares['new'] += 1
                if date <= back_days and date >= back_perc and session.bot == True:
                    if str(session.browser) == 'TwitterBot' or str(session.browser) == 'FacebookExternalHit':
                        shares['old'] += 1

                if date <= now and date >= back_days and session.bot == False:
                    if str(session.os).lower() == 'android' or str(session.os).lower() == 'ios':
                        devices_now['Mobile'] += 1
                    else:
                        devices_now['Computer'] += 1
                    try:
                        sess[calendar.day_name[int(calendar.weekday(int(year),int(month),int(day)))]+' '+str(day)] += 1
                    except:
                        sess.__setitem__(calendar.day_name[int(calendar.weekday(int(year),int(month),int(day)))]+' '+str(day),1)

                    if str(day) not in label_days and str(months[str(month)]+' '+day) not in label_days:
                        if int(day) == 1:
                            label_days.append(months[str(month)]+' '+day)
                        else:
                            label_days.append(str(day))

                    if str(session.referer) != 'None':
                        try:
                            if int(day) == 1:
                                referer[str(session.referer)][months[str(month)]+' '+day] += 1
                            else:
                                referer[str(session.referer)][str(day)] += 1
                        except:
                            if int(day) == 1:
                                referer[str(session.referer)][months[str(month)]+' '+day] = 1
                            else:
                                referer[str(session.referer)][str(day)] = 1
                    
                    if str(session.iso_code) != 'None':
                        try:
                            country[str(session.iso_code)] += 1
                        except:
                            country[str(session.iso_code)] = 1
                        countries[str(session.iso_code)] = str(session.country)
                    

                if date <= back_days and date >= back_perc and session.bot == False:
                    if str(session.os).lower() == 'android' or str(session.os).lower() == 'ios':
                        devices_old['Mobile'] += 1
                    else:
                        devices_old['Computer'] += 1
                    try:
                        sess_old[calendar.day_name[int(calendar.weekday(int(year),int(month),int(day)))]+' '+str(day)] += 1
                    except:
                        sess_old.__setitem__(calendar.day_name[int(calendar.weekday(int(year),int(month),int(day)))]+' '+str(day),1)
    
    per_devices['mobile'] = ((devices_old['Mobile'] - devices_now['Mobile']) - devices_old['Mobile']) % 100
    per_devices['computer'] = ((devices_old['Computer'] - devices_now['Computer']) - devices_old['Computer']) % 100
    shares['perc'] = ((shares['old'] - shares['new']) - shares['old']) % 100

    return render_template('main.html',shares=shares,countries=countries,country=country,referer=referer,label_days=label_days,users=users,posts=posts,pages=pages,sessions=sessions,analyze=Analyze_Pages,data=sess,devices=devices_now,devices_old=devices_old,sess_old=sess_old,per_devices=per_devices)

@admin_pages.route('/admin/sessions')
@login_required
def sessions():
    post_page = request.args.get('page',1,type=int)
    sessions = db.session.query(Analyze_Session).order_by(desc(Analyze_Session.id)).paginate(page=post_page,per_page=20)

    return render_template('sessions.html', sessions=sessions)


@admin_pages.route('/admin/users')
@login_required
def users():
    post_page = request.args.get('page',1,type=int)
    users = db.session.query(UserModel).order_by(desc(UserModel.id)).paginate(page=post_page,per_page=20)

    return render_template('users.html', users=users)


@admin_pages.route('/admin/podcasts', methods=['POST','GET'])
@login_required
def podcasts():

    if request.method == 'POST':
        file_name, file_ext = os.path.splitext(request.files['image'].filename)
        picture_fn = 'p_series_' + str(db.session.execute(Sequence('podcasts_series_id_seq')) + 1) + file_ext
        picture_path = os.path.join(app.config['UPLOAD_FOLDER_PODCAST_SERIES'], picture_fn)
        
        i = Image.open(request.files['image'])
        i.save(picture_path)
        webp.cwebp(os.path.join(app.config['UPLOAD_FOLDER_PODCAST_SERIES'], picture_fn),os.path.join(app.config['UPLOAD_FOLDER_PODCAST_SERIES'], 'p_series_' + str(db.session.execute(Sequence('podcasts_series_id_seq')) + 1) + '.webp'), "-q 80")
        os.remove(os.path.join(app.config['UPLOAD_FOLDER_PODCAST_SERIES'], picture_fn))

        picture_fn = 'p_series_' + str(db.session.execute(Sequence('podcasts_series_id_seq')) + 1) + '.webp'

        new_series = Podcast_SeriesModel(
            None,
            request.form.get('title'),
            request.form.get('description'),
            picture_fn
        )

        db.session.add(new_series)
        db.session.commit()

    podcast_series = db.session.query(Podcast_SeriesModel).all()

    return render_template('podcast.html', series=podcast_series)
