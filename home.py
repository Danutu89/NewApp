import datetime

from flask import (Blueprint, flash, make_response, redirect, render_template,
                   request, url_for, session)
from flask_login import current_user
from jinja2 import TemplateNotFound
from sqlalchemy import desc, func, or_

from app import db, translate
from forms import (LoginForm, NewQuestionForm, RegisterForm, ReplyForm,
                   ResetPasswordForm, SearchForm)
from models import PostModel, ReplyModel, TagModel, UserModel, Analyze_Session, Notifications_Model

from analyze import parseVisitator, sessionID, GetSessionId
from celery_worker import cleanup_sessions, verify_post

home_pages = Blueprint(
    'home',__name__,
    template_folder='home_templates'
)

@home_pages.before_request
def views():
    data = ['NewApp', GetSessionId(), str(datetime.datetime.now().replace(microsecond=0))]
    parseVisitator(data)

@home_pages.route("/", methods=['GET','POST'])
def home():
    cleanup_sessions.delay()
    login = LoginForm(request.form)
    register = RegisterForm(request.form)
    search_post = SearchForm(request.form)
    new_question = NewQuestionForm(request.form)
    reset = ResetPasswordForm(request.form)

    location = db.session.query(Analyze_Session).filter_by(session=session['user']).first()

    if request.method == 'POST':
        if new_question.validate_on_submit():
            
            lang = translate.getLanguageForText(new_question.text.data)
            new_post = PostModel(
                None,
                new_question.title.data,
                new_question.text.data,
                None,
                None,
                current_user.id,
                None,
                True,
                False,
                None,
                None,
                str(lang.iso_tag).lower(),
                None,
                None
            )

            db.session.add(new_post)
            db.session.commit()

            index = db.session.query(PostModel).order_by(PostModel.id.desc())
            tags = []
            tag_p = new_question.tag.data.lower()
            tag = tag_p.replace(" ", "")
            tags = tag.split(",")
            for t in tags:
                tag = TagModel(
                    None,
                    t,
                    index[0].id
                )
                db.session.add(tag)
                db.session.commit()
            verify_post.delay(index[0].id)
            #print(index[0].id)
            for user in current_user.followed:
                notify = Notifications_Model(
                    None,
                    current_user.id,
                    'New post',
                    'New post from {}'.format(current_user.name),
                    str(url_for('home.post',id=index[0].id,title=new_question.title.data)),
                    user.id,
                    None,
                    None
                )
                db.session.add(notify)
            db.session.commit()
            flash('New question posted successfully', 'success')
            
    post_page = request.args.get('page',1,type=int)
    if request.args.get('search'):
        if current_user.is_authenticated:
            posts, total = PostModel.search_post(request.args.get('search'),post_page,99,current_user.lang)
            #posts = PostModel.query.whoosh_search(request.args.get('search')).filter(or_(PostModel.lang.like(current_user.lang),PostModel.lang.like('en'))).order_by(PostModel.id.desc()).paginate(page=post_page,per_page=9)
        else:
            get_lang = db.session.query(Analyze_Session).filter_by(session=session['user']).first()
            posts, total = PostModel.search_post(request.args.get('search'),post_page,99,get_lang)
            #posts = PostModel.query.whoosh_search(request.args.get('search')).filter(or_(PostModel.lang.like(get_lang.lang),PostModel.lang.like('en'))).order_by(PostModel.id.desc()).paginate(page=post_page,per_page=9)
    elif request.args.get('tag_finder'):
        tag_finder = request.args.get('tag_finder')
        tag_posts = db.session.query(TagModel).filter_by(tag=tag_finder).all()
        ids = []
        for tag in tag_posts:
            ids.append(tag.post_id)
        if current_user.is_authenticated:
            posts = PostModel.query.filter(PostModel.id.in_(ids)).order_by(PostModel.id.desc()).filter(or_(PostModel.lang.like(current_user.lang),PostModel.lang.like('en'))).all()#.paginate(page=post_page,per_page=9)
        else:
            get_lang = db.session.query(Analyze_Session).filter_by(session=session['user']).first()
            posts = PostModel.query.filter(PostModel.id.in_(ids)).order_by(PostModel.id.desc()).filter(or_(PostModel.lang.like(get_lang.lang),PostModel.lang.like('en'))).all()#.paginate(page=post_page,per_page=9)
        #posts = db.session.query(PostModel).paginate(page=post_page,per_page=9)
    elif request.args.get('saved'):
        if current_user.is_authenticated == False:
            return redirect(url_for('home.home'))
        posts = PostModel.query.filter(or_(PostModel.lang.like(current_user.lang),PostModel.lang.like('en'))).filter(PostModel.id.in_(current_user.saved_posts)).order_by(PostModel.id.desc()).all()#.paginate(page=post_page,per_page=9)
    else:
        if current_user.is_authenticated:
            if len(current_user.int_tags) > 0:
                tg = db.session.query(TagModel).filter(TagModel.tag.in_(current_user.int_tags)).all()
                tgi = []
                for t in tg:
                    tgi.append(t.post_id)
                posts = PostModel.query.filter(or_(PostModel.lang.like(current_user.lang),PostModel.lang.like('en'))).filter(PostModel.id.in_(tgi)).order_by(PostModel.id.desc()).all()#.paginate(page=post_page,per_page=9)
            else:
                posts = PostModel.query.filter(or_(PostModel.lang.like(current_user.lang),PostModel.lang.like('en'))).order_by(PostModel.id.desc()).all()#.paginate(page=post_page,per_page=9)
        else:
            get_lang = db.session.query(Analyze_Session).filter_by(session=session['user']).first()
            posts = PostModel.query.filter(or_(PostModel.lang.like(get_lang.lang),PostModel.lang.like('en'))).order_by(PostModel.id.desc()).all()#.paginate(page=post_page,per_page=9)
        #posts = db.session.query(PostModel).order_by(PostModel.id.desc()).paginate(page=post_page,per_page=9)

    popular_posts = db.session.query(PostModel).order_by(PostModel.views.desc()).limit(9)

    most_tags = db.session.query(TagModel.tag,
    func.count(TagModel.id).label('qty')
    ).group_by(TagModel.tag
    ).order_by(desc('qty')).limit(9)
    tagi = db.session.query(TagModel.tag,func.count(TagModel.id).label('qty')).group_by(TagModel.tag).order_by(desc('qty'))
    tags = db.session.query(TagModel).all()
    replyes = db.session.query(ReplyModel).all()

    if current_user.is_authenticated:
        return render_template('home.html',tagi=tagi ,reset=reset,search=search_post,posts=posts,tags=tags,replyes=replyes,new_question=new_question,popular_posts=popular_posts,most_tags=most_tags,location=location)
    else:
        return render_template('home.html', tagi=tagi,reset=reset,login=login,register=register,search=search_post,posts=posts,tags=tags,replyes=replyes,popular_posts=popular_posts,most_tags=most_tags,location=location)



@home_pages.route('/post/<string:title>/id=<int:id>')
def post(title,id):
    search = SearchForm(request.form)
    reply = ReplyForm(request.form)
    reset = ResetPasswordForm(request.form)
    posts = db.session.query(PostModel).filter_by(id=id).first_or_404()
    replyes = db.session.query(ReplyModel).filter_by(post_id=id)
    tags = db.session.query(TagModel).filter_by(post_id=id)
    tags_all = db.session.query(TagModel).all()
    post_from_user = db.session.query(PostModel).filter_by(user=posts.user_in.id).all()
    popular_posts = db.session.query(PostModel).order_by(PostModel.views.desc()).limit(9)
    most_tags = db.session.query(TagModel.tag,
    func.count(TagModel.id).label('qty')
    ).group_by(TagModel.tag
    ).order_by(desc('qty')).limit(9)

    data = [('Post_{}').format(posts.id), GetSessionId(), str(datetime.datetime.now().replace(microsecond=0))]
    parseVisitator(data)

    location = db.session.query(Analyze_Session).filter_by(session=session['user']).first()

    if current_user.is_authenticated:
        post = db.session.query(PostModel).filter_by(id=id).first_or_404()
        post.views += 1
        db.session.commit()
        return render_template('post.html',tags_all=tags_all,post_from_user=post_from_user ,reset=reset, reply=reply,posts=posts,replyes=replyes,tags=tags,search=search,popular_posts=popular_posts,most_tags=most_tags,location=location)
    else:
        login = LoginForm(request.form)
        register = RegisterForm(request.form)
        return render_template('post.html',tags_all=tags_all,post_from_user=post_from_user, reset=reset, reply=reply,posts=posts,replyes=replyes,search=search,login=login,tags=tags,register=register,popular_posts=popular_posts,most_tags=most_tags,location=location)

@home_pages.route('/post/reply/id=<int:id>/<string:title>', methods=['POST','GET'])
def reply(id,title):

    if request.method != 'POST':
        return redirect(url_for('home.post',id=id,title=title))

    reply = ReplyForm(request.form)

    if reply.validate_on_submit() == False:
        return redirect(url_for('home.post',id=id,title=title))

    if current_user.is_authenticated == False:
        flash('You need to log in to reply to this post', 'error')

    posts = db.session.query(PostModel).filter_by(id=id).first()

    if posts.closed:
        flash('This post is closed you can`t reply', 'error')
        return redirect(url_for('home.post',title=title,id=id))

    new_reply = ReplyModel(
        None,
        reply.text.data,
        id,
        current_user.id
    )
    
    db.session.add(new_reply)
    db.session.commit()

    flash('New reply added successfully','success')
    return redirect(url_for('home.post',id=id,title=title))

@home_pages.route("/sitemap")
def sitemap():

    posts = db.session.query(PostModel).all()
    users = db.session.query(UserModel).all()

    sitemap_xml = render_template('sitemap.xml',posts=posts,users=users)
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = "application/xml"

    return response

@home_pages.route('/opensearch')
def opensearch():
    opensearch_xml = render_template('opensearch.xml')
    response = make_response(opensearch_xml)
    response.headers['Content-Type'] = "application/xml"

    return response

@home_pages.route('/delete/post/<int:id>')
def delete_post(id):
    posts = db.session.query(PostModel).filter_by(id=id).first()

    if current_user.is_authenticated == False:
        return redirect(url_for('home.home'))

    if current_user.id != posts.user_in.id:
        return redirect(url_for('home.home'))
    if current_user.roleinfo.delete_post_permission == False:
        return redirect(url_for('home.home'))

    db.session.query(PostModel).filter_by(id=id).delete()
    db.session.query(ReplyModel).filter_by(post_id=id).delete()
    db.session.query(TagModel).filter_by(post_id=id).delete()
    db.session.commit()
    flash('Post successfully deleted', 'success')
    return redirect(url_for('home.home'))

@home_pages.route('/close/post/<int:id>')
def close_post(id):
    posts = db.session.query(PostModel).filter_by(id=id).first()

    if current_user.is_authenticated == False:
        return redirect(url_for('home.home'))

    if current_user.roleinfo.close_post_permission:
        posts.closed = True
        posts.closed_on = datetime.datetime.now()
        posts.closed_by = current_user.id
        db.session.commit()
        flash('Post successfully closed', 'success')
    return redirect(url_for('home.home'))

@home_pages.route('/feed')
def rss_feed():
    tags = db.session.query(TagModel).filter_by(tag='tutorial').all()
    ids = []
    for t in tags:
        ids.append(i.post_id)
    posts = db.session.query(PostModel).filter(PostModel.id.in_(ids)).filter_by(lang='en').order_by(PostModel.id.desc()).limit(5)
    newsfeed_rss = render_template('newsfeed.xml', posts=posts)
    response = make_response(newsfeed_rss)
    response.headers['Content-Type'] = "application/xml"

    return response



