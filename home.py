from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from jinja2 import TemplateNotFound
from sqlalchemy import desc, func

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
    post_page = request.args.get('page',1,type=int)
    if request.args.get('tag_finder'):
        tag_finder = request.args.get('tag_finder')
        tag_posts = db.session.query(TagModel).filter_by(tag=tag_finder).all()
        ids = []
        for tag in tag_posts:
            ids.append(tag.post_id)
        posts = db.session.query(PostModel).filter(PostModel.id.in_(ids)).order_by(PostModel.id.desc()).paginate(page=post_page,per_page=9)
    else:
        posts = db.session.query(PostModel).order_by(PostModel.id.desc()).paginate(page=post_page,per_page=9)

    popular_posts = db.session.query(PostModel).order_by(PostModel.views.desc()).limit(9)

    most_tags = db.session.query(TagModel.tag,
    func.count(TagModel.id).label('qty')
    ).group_by(TagModel.tag
    ).order_by(desc('qty')).limit(9)
    
    tags = db.session.query(TagModel).all()
    replyes = db.session.query(ReplyModel).all()

    if current_user.is_authenticated:
        return render_template('home.html',search=search,posts=posts,tags=tags,replyes=replyes,new_question=new_question,popular_posts=popular_posts,most_tags=most_tags)
    else:
        return render_template('home.html', login=login,register=register,search=search,posts=posts,tags=tags,replyes=replyes,popular_posts=popular_posts,most_tags=most_tags)

@home_pages.route('/post/id=<int:id>')
def post(id):
    search = SearchForm(request.form)
    reply = ReplyForm(request.form)
    posts = db.session.query(PostModel).filter_by(id=id)
    replyes = db.session.query(ReplyModel).filter_by(post_id=id)
    tags = db.session.query(TagModel).filter_by(post_id=id)
    popular_posts = db.session.query(PostModel).order_by(PostModel.views.desc()).limit(9)
    most_tags = db.session.query(TagModel.tag,
    func.count(TagModel.id).label('qty')
    ).group_by(TagModel.tag
    ).order_by(desc('qty')).limit(9)
    if current_user.is_authenticated:
        post = db.session.query(PostModel).filter_by(id=id).first()
        post.views += 1
        db.session.commit()
        return render_template('post.html', reply=reply,posts=posts,replyes=replyes,tags=tags,search=search,popular_posts=popular_posts,most_tags=most_tags)
    else:
        login = LoginForm(request.form)
        register = RegisterForm(request.form)
        return render_template('post.html', reply=reply,posts=posts,replyes=replyes,search=search,login=login,tags=tags,register=register,popular_posts=popular_posts,most_tags=most_tags)

@home_pages.route('/post/reply/id=<int:id>', methods=['POST','GET'])
def reply(id):

    if request.method != 'POST':
        return redirect(url_for('home.post',id=id))

    reply = ReplyForm(request.form)

    if reply.validate_on_submit() == False:
        return redirect(url_for('home.post',id=id))

    if current_user.is_authenticated == False:
        flash('You need to log in to reply to this post', 'error')

    new_reply = ReplyModel(
        None,
        reply.text.data,
        id,
        current_user.id
    )
    
    db.session.add(new_reply)
    db.session.commit()

    flash('New reply added successfully','success')
    return redirect(url_for('home.post',id=id))


