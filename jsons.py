from flask import (Blueprint, abort, flash, jsonify, make_response, redirect,
                   render_template, request)

from app import db
from models import PostsSchema

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
