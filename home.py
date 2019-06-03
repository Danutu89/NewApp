from flask import Blueprint, flash, render_template, request
from flask_login import current_user
from jinja2 import TemplateNotFound

from app import db
from forms import (LoginForm, NewQuestionForm, RegisterForm, ReplyForm,
                   SearchForm)
from models import PostModel, ReplyModel, TagModel

home_pages = Blueprint(
    'home',__name__,
    template_folder='home_templates'
)


@home_pages.route("/", methods=['GET','POST'])
def home():
    login = LoginForm(request.form)
    register = RegisterForm(request.form)
    search = SearchForm(request.form)
    new_question = NewQuestionForm(request.form)
    
    if request.method == 'POST':
        if new_question.validate_on_submit():
            
            new_post = PostModel(
                None,
                new_question.title.data,
                new_question.text.data,
                None,
                None,
                current_user.id,
                None
            )

            db.session.add(new_post)
            db.session.commit()

            index = db.session.query(PostModel).order_by(PostModel.id.desc())
            tags = []
            tags = new_question.tag.data.split(", ")
            for t in tags:
                tag = TagModel(
                    None,
                    t,
                    index[0].id
                )
                print(t)
                db.session.add(tag)
                db.session.commit()

            flash('New question posted successfully', 'success')

   # if request.args.get('search'):
    #posts = db.session.query(PostModel).whoosh_search(request.args.get('search')).all()
   # else:
    posts = db.session.query(PostModel).order_by(PostModel.id.desc()).all()

    tags = db.session.query(TagModel).all()
    replyes = db.session.query(ReplyModel).all()

    if current_user.is_authenticated:
        return render_template('home.html',search=search,posts=posts,tags=tags,replyes=replyes,new_question=new_question)
    else:
        return render_template('home.html', login=login,register=register,search=search,posts=posts,tags=tags,replyes=replyes)

@home_pages.route('/post/id=<int:id>')
def post(id):
    search = SearchForm(request.form)
    reply = ReplyForm(request.form)
    posts = db.session.query(PostModel).filter_by(id=id)
    replyes = db.session.query(ReplyModel).filter_by(post_id=id)
    tags = db.session.query(TagModel).filter_by(post_id=id)
    if current_user.is_authenticated:
        return render_template('post.html', reply=reply,posts=posts,replyes=replyes,tags=tags,search=search)
    else:
        login = LoginForm(request.form)
        register = RegisterForm(request.form)
        return render_template('post.html', reply=reply,posts=posts,replyes=replyes,search=search,login=login,tags=tags,register=register)
