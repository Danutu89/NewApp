import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import sqlalchemy.dialects.postgresql as sq

from app import bcrypt, db, db_engine,ma,fields
import flask_whooshalchemy

from search_engine import SearchableMixin

from flask import url_for,json

Base = declarative_base()


class UserModel(db.Model):

    __tablename__ = 'users'


    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key = True, index=True)
    join_date = db.Column(db.Date, primary_key = False, default = datetime.datetime.now)
    name = db.Column(db.String(50), primary_key = False)
    real_name = db.Column(db.String(50), primary_key = False)
    email = db.Column(db.String(50), primary_key = False)
    password = db.Column(db.String(255), primary_key = False)
    avatar = db.Column(db.String, primary_key = False)
    genre = db.Column(db.String, primary_key = False, default = 'None')
    role = db.Column(db.Integer, ForeignKey('roles.id') ,default = 0)
    bio = db.Column(db.String(250), primary_key = False, default = 'Hey i`m new here')
    activated = db.Column(db.Boolean, primary_key = False)
    is_online = db.Column(db.Boolean, primary_key = False)
    ip_address = db.Column(db.String, primary_key = False)
    browser = db.Column(db.String, primary_key = False)
    country_name = db.Column(db.String, primary_key = False)
    country_flag = db.Column(db.String, primary_key = False)
    lang = db.Column(db.String, primary_key = False, default = 'eng')
    int_tags = db.Column(sq.ARRAY(db.String),default=[], primary_key = False)
    birthday = db.Column(db.Date, primary_key = False)
    profession = db.Column(db.String, primary_key = False)
    saved_posts = db.Column(sq.ARRAY(db.Integer),default=[], primary_key = False)
    liked_posts = db.Column(sq.ARRAY(db.Integer),default=[], primary_key = False)
    follow = db.Column(sq.ARRAY(db.Integer), ForeignKey('users.id'), default=[], primary_key = False)
    followed = db.Column(sq.ARRAY(db.Integer), ForeignKey('users.id'), default=[],primary_key = False)
    cover = db.Column(db.String, primary_key = False)
    instagram = db.Column(db.String, primary_key = False)
    facebook = db.Column(db.String, primary_key = False)
    twitter = db.Column(db.String, primary_key = False)
    github = db.Column(db.String, primary_key = False)
    website = db.Column(db.String, primary_key = False)
    theme = db.Column(db.String, primary_key = False, default = 'Light')
    int_podcasts = db.Column(sq.ARRAY(db.Integer),default=[], primary_key = False)

    posts = relationship("PostModel", backref="user_in")
    replyes = relationship("ReplyModel", backref="user_in")
    likes = relationship("LikeModel", backref="user_in")
    following = db.relationship("UserModel",foreign_keys=[follow])

    def __init__(self,id,join_date,name,real_name,email,password,avatar,genre,role,bio,activated,is_online,
                    ip_address,browser,country_name,country_flag,lang,int_tags,birthday,profession,saved_posts,liked_posts,follow,followed,cover,
                    instagram,facebook,twitter,github,website,theme,int_podcasts):
        self.id = id
        self.join_date = join_date
        self.name = name
        self.real_name = real_name
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.avatar = avatar
        self.genre = genre
        self.role = role
        self.bio = bio
        self.activated = activated
        self.is_online = is_online
        self.ip_address = ip_address
        self.browser = browser
        self.country_name = country_name
        self.country_flag = country_flag
        self.lang = lang
        self.int_tags = int_tags
        self.birthday = birthday
        self.profession = profession
        self.saved_posts = saved_posts
        self.liked_posts = liked_posts
        self.follow = follow
        self.followed = followed
        self.cover = cover
        self.instagram = instagram
        self.facebook = facebook
        self.twitter = twitter
        self.github = github
        self.website = website
        self.theme = theme
        self.int_podcasts = int_podcasts

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return ('<name {}').format(self.name)

    def get_notifications(self):
        return db.session.query(Notifications_Model).filter_by(for_user=self.id).all()

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','join_date','name','real_name','email','avatar')

UsersSchema = UserSchema(many=True)

class OUserSchema(ma.Schema):
    class Meta:
        fields = ('id','join_date','name','real_name','email','genre','role','bio','avatar')

OUserSchema = OUserSchema()

class RoleModel(db.Model):

    __tablename__ = 'roles'


    id = db.Column(db.Integer, db.Sequence('role_id_seq'), primary_key = True)
    name = db.Column(db.String(30), primary_key = False)
    post_permission = db.Column(db.Boolean, primary_key = False, default = True)
    delete_post_permission = db.Column(db.Boolean, primary_key = False, default = False)
    delete_reply_permission = db.Column(db.Boolean, primary_key = False, default = False)
    edit_post_permission = db.Column(db.Boolean, primary_key = False, default = False)
    edit_reply_permission = db.Column(db.Boolean, primary_key = False, default = False)
    close_post_permission = db.Column(db.Boolean, primary_key = False, default = False)
    delete_user_permission = db.Column(db.Boolean, primary_key = False, default = False)
    modify_user_permission = db.Column(db.Boolean, primary_key = False, default = False)
    admin_panel_permission = db.Column(db.Boolean, primary_key = False, default = False)


    user = relationship("UserModel", backref="roleinfo")

    def __init__(self,id,name,post_permission,delete_post_permission,delete_reply_permission,edit_post_permission,edit_reply_permission,
                close_post_permission,delete_user_permission,modify_user_permission,admin_panel_permission):
        self.id = id
        self.name = name
        self.post_permission = post_permission
        self.delete_post_permission = delete_post_permission
        self.delete_reply_permission = delete_reply_permission
        self.edit_post_permission = edit_post_permission
        self.edit_reply_permission = edit_reply_permission
        self.close_post_permission = close_post_permission
        self.delete_user_permission = delete_user_permission
        self.modify_user_permission = modify_user_permission
        self.admin_panel_permission = admin_panel_permission

    def __repr__(self):
        return ('<name {}').format(self.name)

class PostModel(SearchableMixin, db.Model):

    __tablename__ = 'posts'

    __searchable__ = ['title']

    __analizer__ = flask_whooshalchemy.whoosh.analysis.NgramAnalyzer(minsize=2,maxsize=4)

    id = db.Column(db.Integer, db.Sequence('posts_id_seq'), primary_key = True)
    title = db.Column(db.String(100), primary_key = False)
    text = db.Column(db.String, primary_key = False)
    views = db.Column(db.Integer, primary_key = False, default=0)
    reply = db.Column(db.Integer, primary_key = False, default=0)
    user = db.Column(db.Integer, ForeignKey('users.id'))
    posted_on = db.Column(db.Date, primary_key = False, default = datetime.datetime.now)
    approved = db.Column(db.Boolean, primary_key = False)
    closed = db.Column(db.Boolean, primary_key = False)
    closed_on = db.Column(db.Date, primary_key = False)
    closed_by = db.Column(db.Integer, primary_key = False)
    lang = db.Column(db.String, primary_key = False, default = 'eng')
    thumbnail = db.Column(db.String, primary_key = False)
    likes = db.Column(db.Integer, primary_key = False, default=0)
    read_time = db.Column(db.String, primary_key = False)

    author = db.relationship("UserModel", backref = "author")

    def __init__(self,id,title,text,views,reply,user,posted_on,approved,closed,closed_on,closed_by,lang,thumbnail,likes,read_time):
        self.id = id
        self.title = title
        self.text = text
        self.views = views
        self.reply = reply
        self.user = user
        self.posted_on = posted_on
        self.approved = approved
        self.closed = closed
        self.closed_on = closed_on
        self.closed_by = closed_by
        self.lang = lang
        self.thumbnail = thumbnail
        self.likes = likes
        self.read_time = read_time

    def __repr__(self):
        return '{0}(title={1})'.format(self.__class__.__name__, self.title)

    def replies(self):
        return db.session.query(ReplyModel).filter_by(post_id=self.id).count()

    def closed_by_name(self):
        users = UserModel.query.filter_by(id=self.closed_by).first()
        return users.name

    def unique_views(self):
        return db.session.query(Analyze_Pages).filter_by(name=url_for('home.post',id=self.id, title=self.title)).count()

class PostSchema(ma.Schema):
    author = fields.Nested(UserSchema())
    class Meta:
        fields = ('id','title','text','views','posted_on','author','read_time')

PostsSchema = PostSchema(many=True)
OPostSchema = PostSchema()

class ReplyModel(db.Model):

    __tablename__ = 'replyes'

    id = db.Column(db.Integer, db.Sequence('replyes_id_seq'), primary_key = True)
    text = db.Column(db.String, primary_key = False)
    post_id = db.Column(db.Integer, primary_key = False)
    user = db.Column(db.Integer, ForeignKey('users.id'))
    posted_on = db.Column(db.Date, primary_key = False, default = datetime.datetime.now)


    def __init__(self,id,text,post_id,user,posted_on):
        self.id = id
        self.text = text
        self.post_id = post_id
        self.user = user
        self.posted_on = posted_on

    def __repr__(self):
        return ('<id {}').format(self.id)

class ReplySchema(ma.Schema):
    class Meta:
        fields = ('id','text','post_id','user')

RepliesSchema = ReplySchema(many=True)

class LikeModel(db.Model):

    __tablename__ = 'likes'


    id = db.Column(db.Integer, db.Sequence('likes_id_seq'), primary_key = True)
    post_id = db.Column(db.Integer, primary_key = False)
    user = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self,id,post_id,user):
        self.id = id
        self.post_id = post_id
        self.user = user

    def __repr__(self):
        return ('<id {}').format(self.id)

class TagModel(Base):

    __tablename__ = 'tags'

    id = db.Column(db.Integer, db.Sequence('tags_id_seq'), primary_key = True)
    name = db.Column(db.String, primary_key = False)
    post = db.Column(sq.ARRAY(db.Integer), default=[],primary_key = False)

    def __init__(self,id,name,post):
        self.id = id
        self.name = name
        self.post = post

class Analyze_Session(Base):

    __tablename__ = 'analyze_session'

    id = db.Column(db.Integer, primary_key = True)
    ip = db.Column(db.String, primary_key = False)
    continent = db.Column(db.String, primary_key = False)
    country = db.Column(db.String, primary_key = False)
    city = db.Column(db.String, primary_key = False)
    os = db.Column(db.String, primary_key = False, default="Unknown")
    browser = db.Column(db.String, primary_key = False)
    session = db.Column(db.String, primary_key = False)
    created_at = db.Column(db.Date, primary_key = False)
    bot = db.Column(db.Boolean, primary_key = False, default=False)
    lang = db.Column(db.String, primary_key = False, default = 'eng')
    referer = db.Column(db.String, primary_key = False)
    iso_code = db.Column(db.String, primary_key = False)

    def __init__(self,id,ip,continent,country,city,os,browser,session,created_at,bot,lang,referer,iso_code):
        self.id = id
        self.ip = ip
        self.continent = continent
        self.country = country
        self.city = city
        self.os = os
        self.browser = browser
        self.session = session
        self.created_at = created_at
        self.bot = bot
        self.lang = lang
        self.referer = referer
        self.iso_code = iso_code

class Analyze_Sessions_Schema(ma.Schema):
    class Meta:
        fields = ('id','ip','continent','country','city','os','browser','session','created_at','bot')

SessionsSchema = Analyze_Sessions_Schema(many=True)

class Analyze_Pages(Base):

    __tablename__ = 'analyze_pages'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, primary_key = False)
    session = db.Column(db.String, primary_key = False)
    first_visited = db.Column(db.Date, primary_key = False)
    visits = db.Column(db.Integer,default = 1)

    def __init__(self,id,name,session,first_visited,visits):
        self.id = id
        self.name = name
        self.session = session
        self.first_visited = first_visited
        self.visits = visits

    @staticmethod
    def total_views():
        return db.session.query(Analyze_Session).filter_by(bot=False).count()

    @staticmethod
    def total_users():
        return db.session.query(UserModel).count()
        
    @staticmethod
    def views_15_days():
        now = datetime.datetime.now()
        back_days = now - datetime.timedelta(days = 15)
        return db.session.query(Analyze_Pages).filter(Analyze_Pages.first_visited.between('{}-{}-{}'.format(back_days.year,back_days.month,back_days.day), '{}-{}-{}'.format(now.year,now.month,now.day))).count()

    @staticmethod
    def views_30_days():
        now = datetime.datetime.now()
        back_days = now - datetime.timedelta(days = 15)
        back_perc = back_days - datetime.timedelta(days = 15)
        return db.session.query(Analyze_Pages).filter(Analyze_Pages.first_visited.between('{}-{}-{}'.format(back_perc.year,back_perc.month,back_perc.day), '{}-{}-{}'.format(back_days.year,back_days.month,back_days.day))).count()


    @staticmethod
    def user_15_days():
        now = datetime.datetime.now()
        back_days = now - datetime.timedelta(days = 15)
        return db.session.query(UserModel).filter(UserModel.join_date.between('{}-{}-{}'.format(back_days.year,back_days.month,back_days.day), '{}-{}-{}'.format(now.year,now.month,now.day))).count()

    @staticmethod
    def user_30_days():
        now = datetime.datetime.now()
        back_days = now - datetime.timedelta(days = 15)
        back_perc = back_days - datetime.timedelta(days = 15)
        return db.session.query(UserModel).filter(UserModel.join_date.between('{}-{}-{}'.format(back_perc.year,back_perc.month,back_perc.day), '{}-{}-{}'.format(back_days.year,back_days.month,back_days.day))).count()

    @staticmethod
    def count_posts():
        return db.session.query(PostModel).count()

    @staticmethod
    def posts_15_days():
        now = datetime.datetime.now()
        back_days = now - datetime.timedelta(days = 15)
        return db.session.query(PostModel).filter(PostModel.posted_on.between('{}-{}-{}'.format(back_days.year,back_days.month,back_days.day), '{}-{}-{}'.format(now.year,now.month,now.day))).count()

    @staticmethod
    def posts_30_days():
        now = datetime.datetime.now()
        back_days = now - datetime.timedelta(days = 15)
        back_perc = back_days - datetime.timedelta(days = 15)
        return db.session.query(PostModel).filter(PostModel.posted_on.between('{}-{}-{}'.format(back_perc.year,back_perc.month,back_perc.day), '{}-{}-{}'.format(back_days.year,back_days.month,back_days.day))).count()

    @staticmethod
    def perc_posts():
        return ((Analyze_Pages.posts_30_days() - Analyze_Pages.posts_15_days()) - Analyze_Pages.posts_15_days())%100

    @staticmethod
    def perc_views():
        return ((Analyze_Pages.views_30_days() - Analyze_Pages.views_15_days()) - Analyze_Pages.views_15_days())%100

    @staticmethod
    def perc_users():
        users_15 = Analyze_Pages.user_15_days()
        users_30 = Analyze_Pages.user_30_days()
        return ((users_30 - users_15) - users_15)%100

    @staticmethod
    def count_replies():
        return db.session.query(ReplyModel).count()

class Notifications_Model(db.Model):

    __tablename__ = 'notifications'

    id = db.Column(db.Integer, db.Sequence('notifications_id_seq'), primary_key = True)
    user = db.Column(db.Integer, ForeignKey('users.id'))
    author = db.relationship("UserModel", backref = "n_author", foreign_keys=[user])
    title = db.Column(db.String, primary_key = False)
    body = db.Column(db.String, primary_key = False)
    link = db.Column(db.String, primary_key = False)
    for_user = db.Column(db.Integer, ForeignKey('users.id'))
    receiver = db.relationship("UserModel", backref = "n_receiver", foreign_keys=[for_user])
    checked = db.Column(db.Boolean, primary_key = False, default = False)
    created_on = db.Column(db.Date, primary_key = False, default = datetime.datetime.utcnow)

    def __init__(self,id,user,title,body,link,for_user,checked,created_on):
        self.id = id
        self.user = user
        self.title = title
        self.body = body
        self.link = link
        self.for_user = for_user
        self.checked = checked
        self.created_on = created_on

class Podcast_SeriesModel(Base):

    __tablename__ = 'podcast_series'

    id = db.Column(db.Integer(), db.Sequence('podcasts_series_id_seq'), primary_key=True)
    name = db.Column(db.String(), primary_key = False)
    description = db.Column(db.String(), primary_key = False)
    img = db.Column(db.String(), primary_key = False)

    def __init__(self,id,name,description,img):
        self.id = id
        self.name = name
        self.description = description
        self.img = img

class PodcastsModel(Base):

    __tablename__ = 'podcasts'

    id = db.Column(db.Integer(), db.Sequence('podcasts_id_seq'), primary_key=True)
    title = db.Column(db.String(), primary_key = False)
    body = db.Column(db.String(), primary_key = False)
    audio = db.Column(db.String(), primary_key = False)
    img = db.Column(db.String(), primary_key = False)
    series_id = db.Column(db.Integer, ForeignKey('podcast_series.id'))
    series = db.relationship("Podcast_SeriesModel", backref = "podcasts_series", foreign_keys=[series_id])
    posted_on = db.Column(db.Date, primary_key = False, default = datetime.datetime.utcnow)
    source = db.Column(db.String(), primary_key = False)

    def __init__(id,title,body,audio,img,series_id,series,posted_on,source):
        self.id = id
        self.title = title
        self.body = body
        self.audio = audio
        self.img = img
        self.series_id = series_id
        self.series = series
        self.posted_on = posted_on
        self.source = source


class Subscriber(Base):
    __tablename__ = 'subscriber'

    id = db.Column(db.Integer(), primary_key=True, default=None)
    user = db.Column(db.Integer)
    created = db.Column(db.DateTime())
    modified = db.Column(db.DateTime())
    subscription_info = db.Column(db.Text())
    is_active = db.Column(db.Boolean(), default=True)

    def __init__(self,id,user,created,modified,subscription_info,is_active):
        self.id = id
        self.user = user
        self.created = created
        self.modified = modified
        self.subscription_info = subscription_info
        self.is_active = is_active

    @property
    def subscription_info_json(self):
        return json.loads(self.subscription_info)

    @subscription_info_json.setter
    def subscription_info_json(self, value):
        self.subscription_info = json.dumps(value)

class Gits:

    def __init__(self,name,link,desc):
        self.name = name
        self.link = link
        self.desc = desc

Base.metadata.create_all(db_engine, Base.metadata.tables.values(),checkfirst=True)
