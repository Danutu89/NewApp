import json
from functools import wraps

import jwt
import requests
from flask import (Blueprint, abort, jsonify, make_response, render_template,
                   request, url_for, redirect, flash)

from app import app, db, key_jwt, time, geolocator
from models import (OPostSchema, OUserSchema, PostModel, PostsSchema,
                    RepliesSchema, ReplyModel, TagModel, UserModel,
                    UsersSchema, SessionsSchema, Analyze_Session, bcrypt, Analyze_Pages, Subscriber, Notifications_Model, TagModel, Ip_Coordinates, Coordinates_Location)
from views.users import (BadSignature, BadTimeSignature, Message, SignatureExpired,
                         cipher_suite, login_user, mail, serializer)

from flask_login import current_user
import datetime as dt
from sqlalchemy import desc
from sqlalchemy.schema import Sequence
from datetime import datetime
import os
from urllib.parse import unquote
from PIL import Image
from webptools import webplib as webp
from geopy.exc import GeocoderTimedOut

from flask_jwt_extended import create_access_token

json_pages = Blueprint(
    'jsons', __name__,
    template_folder='json_templates'
)


@json_pages.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@json_pages.route('/app/register',  methods=['POST'])
def register_app():
    data = request.json

    check = db.session.query(UserModel).filter_by(
        name=data['username']).first()

    if check is not None:
        return jsonify({'register': 'Username taken'})

    check = db.session.query(UserModel).filter_by(email=data['email']).first()

    if check is not None:
        return jsonify({'register': 'Email taken'})

    token = serializer.dumps(data['email'], salt='register-confirm')

    msg = Message('Confirm Email Registration',
                  sender='contact@newapp.nl', recipients=[data['email']])
    link = 'https://newapp.nl' + \
        url_for('users.confirm_register', email=data['email'], token=token)
    msg.html = render_template(
        'email_register.html', register=link, email='contact@newapp.nl')
    mail.send(msg)
    new_user = UserModel(
        None,
        None,
        data['username'],
        data['real_name'],
        data['github'],
        data['email'],
        data['password'],
        "https://www.component-creator.com/images/testimonials/defaultuser.png",
        None,
        None,
        None,
        False,
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
        None,
        None,
        None,
        None,
        None,
        'Light',
        None,
        None,
        None
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'register': 'success'})


@json_pages.route('/save-post/<int:id>')
def save_post(id):

    posts = list(current_user.saved_posts)

    if posts is not None:
        if id in posts:
            posts.remove(id)
            response = jsonify({'operation': 'deleted'})
        else:
            response = jsonify({'operation': 'saved'})
            posts.append(id)
    else:
        response = jsonify({'operation': 'saved'})
        posts.append(id)

    current_user.saved_posts = posts
    db.session.commit()

    return response


@json_pages.route('/like-post/<int:id>')
def like_post(id):

    like = list(current_user.liked_posts)
    post = db.session.query(PostModel).filter_by(id=id).first()

    if like is not None:
        if id in like:
            like.remove(id)
            response = jsonify({'operation': 'unliked'})
            post.likes = post.likes - 1
            notify = Notifications_Model(
                None,
                current_user.id,
                '{} unliked your post'.format(current_user.name),
                post.title,
                url_for('home.post', id=post.id, title=post.title),
                post.user_in.id,
                False,
                None,
                'unlike'
            )
            not_check = db.session.query(Notifications_Model).filter_by(
                title='{} unliked your post'.format(current_user.name)).filter_by(body=str(post.title)).first()
        else:
            response = jsonify({'operation': 'liked'})
            post.likes = post.likes + 1
            like.append(id)
            notify = Notifications_Model(
                None,
                current_user.id,
                '{} liked your post'.format(current_user.name),
                post.title,
                url_for('home.post', id=post.id, title=post.title),
                post.user_in.id,
                False,
                None,
                'like'
            )
            not_check = db.session.query(Notifications_Model).filter_by(
                title='{} liked your post'.format(current_user.name)).filter_by(body=post.title).first()
    else:
        response = jsonify({'operation': 'liked'})
        post.likes = post.likes + 1
        like.append(id)
        notify = Notifications_Model(
            None,
            current_user.id,
            '{} liked your post'.format(current_user.name),
            post.title,
            url_for('home.post', id=post.id, title=post.title),
            post.user_in.id,
            False,
            None,
            'like'
        )
        not_check = db.session.query(Notifications_Model).filter_by(
            title='{} liked your post'.format(current_user.name)).filter_by(body=post.title).first()

    if not_check is not None:
        not_check.checked = False
    else:
        db.session.add(notify)

    current_user.liked_posts = like
    db.session.commit()

    return response


@json_pages.route('/follow-tag/<string:tag>')
def follow_tag(tag):

    int_tags = list(current_user.int_tags)

    if int_tags is not None:
        if tag in int_tags:
            int_tags.remove(tag)
            response = jsonify({'operation': 'unfollowed'})
        else:
            response = jsonify({'operation': 'followed'})
            int_tags.append(tag)
    else:
        response = jsonify({'operation': 'followed'})
        int_tags.append(tag)

    current_user.int_tags = int_tags
    db.session.commit()

    return response


@json_pages.route('/follow-user/<int:id>')
def follow_user(id):

    follow = list(current_user.follow)
    followed = db.session.query(UserModel).filter_by(id=id).first()
    user_followed = list(followed.followed)
    if follow is not None:
        if id in follow:
            follow.remove(id)
            user_followed.remove(current_user.id)
            response = jsonify({'operation': 'unfollowed'})
            notify = Notifications_Model(
                None,
                current_user.id,
                '{} unfolowed you'.format(current_user.name),
                current_user.name,
                url_for('users.user', id=current_user.id,
                        name=current_user.name),
                id,
                False,
                None,
                'unfollow'
            )
        else:
            follow.append(id)
            user_followed.append(current_user.id)
            response = jsonify({'operation': 'followed'})
            notify = Notifications_Model(
                None,
                current_user.id,
                '{} started folowing you'.format(current_user.name),
                current_user.name,
                url_for('users.user', id=current_user.id,
                        name=current_user.name),
                id,
                False,
                None,
                'follow'
            )
    else:
        follow.append(id)
        user_followed.append(current_user.id)
        response = jsonify({'operation': 'followed'})
        notify = Notifications_Model(
            None,
            current_user.id,
            '{} started folowing you'.format(current_user.name),
            current_user.name,
            url_for('users.user', id=current_user.id, name=current_user.name),
            id,
            False,
            None,
            'follow'
        )

    db.session.add(notify)
    current_user.follow = follow
    followed.followed = user_followed
    db.session.commit()

    return response


def getItemForKey(value):
    return value['post']['trending_value']


@json_pages.route('/api/trending', methods=['GET'])
def trending():

    now = dt.datetime.now()
    back_days = now - dt.timedelta(days=2)

    posts = db.session.query(PostModel).order_by(
        desc(PostModel.posted_on)).filter_by(approved=True).all()
    analyze_posts = db.session.query(Analyze_Pages).filter(Analyze_Pages.first_visited.between('{}-{}-{}'.format(back_days.year, back_days.month, back_days.day), '{}-{}-{}'.format(now.year, now.month, now.day))).all()

    data = []
    temp = {}
    analyze_json = []
    today = dt.datetime.today()
    today_date = dt.date.today()

    for post in posts:
        published_on = post.posted_on

        total_days = (today - published_on).days - 1

        day_1 = 0
        day_0 = 0

        for analyze in analyze_posts:
            if analyze.name == '/post/{post.title}/id={post.id}':
                if (today_date-analyze.first_visited).days < 2:
                    day_1 += analyze.visits
                if (today_date-analyze.first_visited).days < 1:
                    day_0 += analyze.visits

        total = (day_1 + day_0)/2
        temp['post'] = {'trending_value': total, 'id': post.id, 'title': post.title, 'lurl': url_for('home.post', id=post.id, title=post.title),
                        'author': {'id': post.user_in.id, 'name': post.user_in.name, 'avatar': post.user_in.avatar}}
        data.append(temp.copy())
        day_1 = 0
        day_0 = 0

    data.sort(key=getItemForKey, reverse=True)

    resp = jsonify(data)
    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp


@json_pages.route("/sitemap")
def sitemap():

    posts = db.session.query(PostModel).all()
    users = db.session.query(UserModel).all()

    sitemap_xml = render_template('sitemap.xml', posts=posts, users=users)
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = "application/xml"

    return response


@json_pages.route('/opensearch')
def opensearch():
    opensearch_xml = render_template('opensearch.xml')
    response = make_response(opensearch_xml)
    response.headers['Content-Type'] = "application/xml"

    return response


@json_pages.route('/delete/post/<int:id>')
def delete_post(id):
    posts = db.session.query(PostModel).filter_by(id=id).first()

    if current_user.is_authenticated == False:
        return redirect(url_for('home.home'))

    if current_user.id != posts.user_in.id and current_user.roleinfo.delete_post_permission == False:
        return redirect(url_for('home.home'))

    if posts.thumbnail:
        try:
            picture_fn = 'post_' + str(id) + '.jpeg'
            os.remove(os.path.join(
                app.config['UPLOAD_FOLDER_POST'], picture_fn))
        except:
            pass

    db.session.query(PostModel).filter_by(id=id).delete()
    db.session.query(ReplyModel).filter_by(post_id=id).delete()
    tags = db.session.query(TagModel).filter(
        TagModel.post.contains([id])).all()
    for t in tags:
        x = list(t.post)
        x.remove(id)
        t.post = x

    db.session.commit()
    flash('Post successfully deleted', 'success')
    return redirect(url_for('home.home'))


@json_pages.route('/close/post/<int:id>')
def close_post(id):
    posts = db.session.query(PostModel).filter_by(id=id).first()

    if current_user.is_authenticated == False:
        return redirect(url_for('home.home'))

    if current_user.roleinfo.close_post_permission:
        posts.closed = True
        posts.closed_on = datetime.now()
        posts.closed_by = current_user.id
        db.session.commit()
        flash('Post successfully closed', 'success')
    return redirect(url_for('home.home'))


@json_pages.route('/feed')
def rss_feed():
    tags = db.session.query(TagModel).filter_by(name='discuss').all()
    ids = []
    for t in tags:
        ids.extend(t.post)
    posts = db.session.query(PostModel).filter(PostModel.id.in_(ids)).filter_by(
        lang='en').order_by(PostModel.id.desc()).limit(5)
    newsfeed_rss = render_template('newsfeed.xml', posts=posts)
    response = make_response(newsfeed_rss)
    response.headers['Content-Type'] = "application/xml"

    return response


@app.route('/api/subscribe')
def subscribe():
    subscription_info = request.json.get('subscription_info')
    # if is_active=False == unsubscribe
    is_active = request.json.get('is_active')
    user = request.json.get('user')

    # we assume subscription_info shall be the same
    item = db.session.query(Subscriber).filter(
        Subscriber.subscription_info == subscription_info).first()
    if not item:
        item = Subscriber()
        item.created = datetime.datetime.utcnow()
        item.subscription_info = subscription_info
        item.user = user

    item.is_active = is_active
    item.modified = datetime.datetime.utcnow()
    db.session.add(item)
    db.session.commit()

    return jsonify({id: item.id})


@json_pages.route('/delete/reply/<int:id>')
def delete_reply(id):
    reply = db.session.query(ReplyModel).filter_by(id=id).first()

    if current_user.is_authenticated == False:
        return redirect(url_for('home.home'))

    if current_user.id != reply.user_in.id:
        if current_user.roleinfo.delete_reply_permission == False:
            return redirect(url_for('home.home'))

    db.session.query(ReplyModel).filter_by(id=id).delete()

    db.session.commit()
    flash('Reply successfully deleted', 'success')
    return redirect(url_for('home.home'))


@json_pages.route('/.well-known/assetlinks.json')
def deeplink():
    response = make_response(render_template('assertlinks.json'), 200)
    response.mimetype = 'application/json'
    return response


@json_pages.route('/api/upload_post', methods=['POST'])
def upload():
    if request.method != 'POST':
        return jsonify({'image': 'error'})

    file_name, file_ext = os.path.splitext(request.files['image'].filename)
    picture_fn = file_name + file_ext
    picture_path = os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], picture_fn)

    i = Image.open(request.files['image'])
    i.save(picture_path)
    webp.cwebp(os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], picture_fn), os.path.join(
        app.config['UPLOAD_FOLDER_IMAGES'], file_name + '.webp'), "-q 80")

    os.remove(os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], picture_fn))

    picture_fn = file_name + '.webp'

    return jsonify({'image': '/static/images/posts/'+picture_fn})


@json_pages.route("/api/set_user_offline/<int:id>")
def set_offline(id):
    user = db.session.query(UserModel).filter_by(id=id).first()
    user.status = 'Offline'
    user.status_color = '#cc1616'
    db.session.commit()

    return jsonify({'operation': 'success'})


@json_pages.route("/api/set_user_online/<int:id>")
def set_online(id):
    user = db.session.query(UserModel).filter_by(id=id).first()
    user.status = 'Online'
    user.status_color = '#00c413'
    db.session.commit()

    return jsonify({'operation': 'success'})


@json_pages.route("/api/set_user_away/<int:id>")
def set_away(id):
    user = db.session.query(UserModel).filter_by(id=id).first()
    user.status = 'Away'
    user.status_color = '#ffe81b'
    db.session.commit()

    return jsonify({'operation': 'success'})


@json_pages.route("/api/install/<int:id>")
def install_pwa(id):

    user = db.query(UserModel).filter_by(id=id).first()
    user.installed = True
    db.commit()

    return jsonify({'operation': 'success'})

def GetLocation(coords):
    try:
        return geolocator.reverse(coords)
    except GeocoderTimedOut:
        return GetLocation(coords)

@json_pages.route("/api/set_location/<string:lat>/<string:lon>")
def set_loc(lat, lon):

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        userIP = request.environ['REMOTE_ADDR']
    else:
        userIP = request.environ['HTTP_X_FORWARDED_FOR']

    ip = db.session.query(Ip_Coordinates).filter_by(ip=userIP).first()

    if ip is None:

        ip_new = Ip_Coordinates(
            None,
            userIP,
            lon,
            lat
        )

        db.session.add(ip_new)
        index = db.session.execute(Sequence('ip_coordinates_code_seq')) + 1
    else:
        ip.longitude = float(lon)
        ip.latitude = float(lat)
        index = ip.code

    coordinates = db.session.query(Coordinates_Location).filter_by(code_ip=index).first()

    location = GetLocation([float(lat), float(lon)])
    api_2 = requests.get(
        ("https://restcountries.eu/rest/v2/alpha/{}").format(location.raw['address']['country_code']))
    api_2 = api_2.json()

    try:
        city = location.raw['address']['town']
    except:
        city = location.raw['address']['city']


    if coordinates is None:
        new_coordinates = Coordinates_Location(
            index,
            api_2['region'],
            location.raw['address']['country'],
            location.raw['address']['county'],
            city,
            location.raw['address']['country_code']
        )

        db.session.add(new_coordinates)
    else:
        coordinates.continent = api_2['region']
        coordinates.country = location.raw['address']['country']
        coordinates.county = location.raw['address']['county']
        coordinates.city = city
        coordinates.iso_code = location.raw['address']['country_code']

    db.session.commit()

    return jsonify({'opration': 'success'})

@json_pages.route('/short/<string:short>')
def short_url(short):

    link = cipher_suite.decrypt(str(short).encode())

    return redirect(link)