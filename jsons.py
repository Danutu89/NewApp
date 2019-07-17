from flask import Blueprint, jsonify, make_response, abort, request
import requests
from app import db, app, key_jwt
from models import (OPostSchema, OUserSchema, PostModel, PostsSchema,
                    RepliesSchema, ReplyModel, TagModel, UserModel,
                    UsersSchema, bcrypt)

from users import login_user

import datetime

from functools import wraps

import json

import jwt

json_pages = Blueprint(
    'jsons',__name__,
    template_folder='json_templates'
)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.json
        
        if not token:
            return jsonify({"message": "Token is missing!"})
        try:
            data = jwt.decode(token['token'],
            key_jwt['k'],algorithms=['HS256'])
            print (data['user'])
        except Exception as e:
            print(str(e))
            print(token)
            return jsonify({"message": str(e)})
        return f(*args, **kwargs)
    return decorated

@json_pages.route('/api/posts', methods=['POST'])
@token_required
def posts():
    
    posts = db.session.query(PostModel).all()
    result = PostsSchema.dump(posts)
    response = make_response(jsonify(result.data),200)
    response.mimetype = 'application/json'
    return response

@json_pages.route('/api/post/<int:id>')
def post(id):
    posts = db.session.query(PostModel).filter_by(id=id).first()
    result = OPostSchema.dump(posts)
    response = make_response(jsonify(result.data),200)
    response.mimetype = 'application/json'
    return response

@json_pages.route('/api/replies/<int:id>')
def replies(id):
    reply = db.session.query(ReplyModel).filter_by(post_id=id).all()
    result = RepliesSchema.dump(reply)
    response = make_response(jsonify(result.data),200)
    response.mimetype = 'application/json'
    return response

@json_pages.route('/api/users')
def users():
    users = db.session.query(UserModel).all()
    result = UsersSchema.dump(users)
    response = make_response(jsonify(result.data),200)
    response.mimetype = 'application/json'
    return response

@json_pages.route('/api/user/<int:id>')
def user(id):
    users = db.session.query(UserModel).filter_by(id=id).first()
    result = OUserSchema.dump(users)
    response = make_response(jsonify(result.data),200)
    response.mimetype = 'application/json'
    return response

@json_pages.route('/api/delete/post/<int:id>', methods=['DELETE'])
def delete_post(id):
    if requests.method == 'DELETE':
        db.session.query(PostModel).filter_by(id=id).delete()
        db.session.query(ReplyModel).filter_by(post_id=id).delete()
        db.session.query(TagModel).filter_by(post_id=id).delete()
        db.session.commit()
        return jsonify({'operation': 'success'})
    return jsonify({'operation': 'invalid_method'})

@json_pages.route('/api/login/<string:name>/<string:password>')
def login(name, password):
    user = db.session.query(UserModel).filter_by(name=name).first()

    if user is None:
        user = db.session.query(UserModel).filter_by(email=name).first()
    if user is None:
        return jsonify({'login': 'no_user'})

    if bcrypt.check_password_hash(user.password, password):
        return jsonify({'login': 'success'})
    else:
        return jsonify({'login': 'wrong_pass'})

@json_pages.route("/api/login", methods=['POST'])
def login_app():
    if request.method != 'POST':
        return redirect(url_for('home.home'))

    if not request.json:
        abort(404)

    data = request.json

    print(data)

    user = db.session.query(UserModel).filter_by(name=data['user']).first()

    if user is None:
        user = db.session.query(UserModel).filter_by(email=data['user']).first()
    if user is None:
        return jsonify({"login": "No user"})

    if bcrypt.check_password_hash(user.password, data['password']) == False:
        return jsonify({"login": "Incorrect password"})

    if user.activated == False:
      return jsonify({"login": "Account not activated"})

    else:
        payload = {'user': data['user'], 'user_id': user.id,'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}
        token = jwt.encode(payload,key_jwt['k']).decode('utf-8')
        return jsonify({"login": 'success', 'token': token})

@json_pages.route('/api/register',  methods=['POST'])
def register_app():

    if request.method != 'POST':
        abord(404)

    data = request.json

    check = db.session.query(UserModel).filter_by(name=data['username']).first()

    if check is not None:
        return jsonify({'register': 'Username taken'})
    
    check = db.session.query(UserModel).filter_by(email=data['email']).first()

    if check is not None:
        return jsonify({'register': 'Email taken'})

    if data['github']:
      git = requests.get(('https://api.github.com/users/{}').format(data['github']))
      git_check = git.json()

      try:
        if git_check['login'] == data['github']:
          check = db.session.query(UserModel).filter_by(github_name=data['github']).first()

          if check is not None:
              return jsonify({'register': 'GitHub account taken'})
      except KeyError:
        return jsonify({'register': 'No GitHub user'})

    token = serializer.dumps(data['email'],salt='register-confirm')

    msg = Message('Confirm Email Registration', sender='contact@newapp.nl', recipients=[data['email']])
    link = 'https://newapp.nl' + url_for('users.confirm_register',email=data['email'] ,token=token)
    msg.html = render_template('email_register.html',register=link,email='contact@newapp.nl')
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
            False
        )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'register': 'success'})
