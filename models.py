import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import sqlalchemy as sq

from app import bcrypt, db, db_engine,ma,fields
import flask_whooshalchemy

from search_engine import SearchableMixin

Base = declarative_base()


class UserModel(db.Model):

    __tablename__ = 'users'


    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key = True, index=True)
    join_date = db.Column(db.Date, primary_key = False, default = datetime.datetime.now)
    name = db.Column(db.String(50), primary_key = False)
    real_name = db.Column(db.String(50), primary_key = False)
    github_name = db.Column(db.String(50), primary_key = False)
    email = db.Column(db.String(50), primary_key = False)
    password = db.Column(db.String(255), primary_key = False)
    avatar = db.Column(db.String, primary_key = False, default = 'None')
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
    follow = db.Column(sq.ARRAY(db.Integer), default=[2], primary_key = False)
    followed = db.Column(sq.ARRAY(db.Integer), default=[], primary_key = False)

    posts = relationship("PostModel", backref="user_in")
    replyes = relationship("ReplyModel", backref="user_in")
    likes = relationship("LikeModel", backref="user_in")

    def __init__(self,id,join_date,name,real_name,github_name,email,password,avatar,genre,role,bio,activated,is_online,
                    ip_address,browser,country_name,country_flag,lang,int_tags,birthday,profession,saved_posts,liked_posts,follow,followed):
        self.id = id
        self.join_date = join_date
        self.name = name
        self.real_name = real_name
        self.github_name = github_name
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

    def get_followers(self):
        user = db.session.query(UserModel).filter_by(id=self.id).first()
        return len(user.followed)

    def get_notifications(self):
        return db.session.query(Notifications_Model).filter_by(for_user=self.id).all()

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','join_date','name','real_name','github_name','email','avatar')
    
UsersSchema = UserSchema(many=True)

class OUserSchema(ma.Schema):
    class Meta:
        fields = ('id','join_date','name','real_name','github_name','email','genre','role','bio','avatar')
    
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
    
    author = db.relationship("UserModel", backref = "author")

    def __init__(self,id,title,text,views,reply,user,posted_on,approved,closed,closed_on,closed_by,lang,thumbnail,likes):
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

    def __repr__(self):
        return '{0}(title={1})'.format(self.__class__.__name__, self.title)

    def replies(self):
        return db.session.query(ReplyModel).filter_by(post_id=self.id).count()

    def closed_by_name(self):
        users = UserModel.query.filter_by(id=self.closed_by).first()
        return users.name

    def unique_views(self):
        return db.session.query(Analyze_Pages).filter_by(name=('Post_{}').format(self.id)).count()

class PostSchema(ma.Schema):
    author = fields.Nested(UserSchema())
    class Meta:
        fields = ('id','title','text','views','posted_on','author')
    
PostsSchema = PostSchema(many=True)
OPostSchema = PostSchema()

class ReplyModel(db.Model):

    __tablename__ = 'replyes'
 
    id = db.Column(db.Integer, db.Sequence('replyes_id_seq'), primary_key = True)
    text = db.Column(db.String(250), primary_key = False)
    post_id = db.Column(db.Integer, primary_key = False)
    user = db.Column(db.Integer, ForeignKey('users.id'))

    def __init__(self,id,text,post_id,user):
        self.id = id
        self.text = text
        self.post_id = post_id
        self.user = user

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

class TagModel(db.Model):

    __tablename__ = 'post_tags'

 
    id = db.Column(db.Integer, db.Sequence('post_tags_id_seq'), primary_key = True)
    tag = db.Column(db.String(50), primary_key = False)
    post_id = db.Column(db.Integer, primary_key = False)

    def __init__(self,id,tag,post_id):
        self.id = id
        self.tag = tag
        self.post_id = post_id

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

    def __init__(self,id,ip,continent,country,city,os,browser,session,created_at,bot,lang):
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
        return db.session.query(Analyze_Session).count()

    @staticmethod
    def total_users():
        return db.session.query(UserModel).count()

    @staticmethod
    def count_posts():
        return db.session.query(PostModel).count()

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

class Gits:

    def __init__(self,name,link,desc):
        self.name = name
        self.link = link
        self.desc = desc

Base.metadata.create_all(db_engine, Base.metadata.tables.values(),checkfirst=True)
