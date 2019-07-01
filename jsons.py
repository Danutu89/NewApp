from flask import Blueprint, jsonify, make_response
import requests
from app import db
from models import (OPostSchema, OUserSchema, PostModel, PostsSchema,
                    RepliesSchema, ReplyModel, TagModel, UserModel,
                    UsersSchema, bcrypt)

json_pages = Blueprint(
    'jsons',__name__,
    template_folder='json_templates'
)

@json_pages.route('/api/posts')
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
