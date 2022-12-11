from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, BLOB, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin

db = SQLAlchemy()

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer,  primary_key = True, nullable = False)
    email = Column(String, nullable=False, unique = True)
    username = Column(String, nullable=False)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)
    profile_pic = Column(BLOB, nullable=False)
    mimetype = Column(String, nullable=False)
    status = Column(Boolean, nullable=False)
    created_at = Column(DateTime, server_default = func.now(), nullable=False)
    updated_at = Column(DateTime, server_default = func.now(), server_onupdate = func.now(), nullable=False)

    # can have many posts
    poster = db.relationship('Posts', backref=backref('poster'), cascade = 'all, delete')
    reporter = db.relationship('Reports', backref=backref('reporter'), cascade = 'all, delete')
    bookmarker = db.relationship('Bookmarks', backref=backref('bookmarker'), cascade = 'all, delete')
    notifier = db.relationship('Notifications', backref=backref('notifier'), cascade = 'all, delete')


class Posts(db.Model):
    id = Column(Integer, primary_key = True)
    poster_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type_id = Column(Integer, ForeignKey('types.id'), nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, server_default = func.now(), nullable=False)
    updated_at = Column(DateTime, server_default = func.now(), server_onupdate = func.now(), nullable=False)
    
    article = db.relationship('News', backref=backref('article'), cascade = "all, delete")
    post = db.relationship('Reports', backref=backref('post'), cascade = "all, delete")
    comment_post = db.relationship('Comments', backref=backref('comment_post'), cascade = "all, delete")

class News(db.Model):
    id = Column(Integer, primary_key = True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    title = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    image = Column(BLOB, nullable=False)
    mimetype = Column(String, nullable=False)

    commented_news = db.relationship('Comments', backref = backref('commented_news'), cascade = "all, delete")

class Comments(db.Model):
    id = Column(Integer, primary_key = True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable = False)
    news_id = Column(Integer, ForeignKey('news.id'), nullable = False)

class Types(db.Model):
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable=False)
    type = db.relationship('Posts', backref=backref('type'))

class Categories(db.Model):
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable=False)
    category = db.relationship('News', backref=backref('category'))


class Roles(db.Model):
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable=False)


class Followers(db.Model):
    id = Column(Integer, primary_key = True)
    follow_by = Column(Integer, nullable=False)
    follow_to = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default = func.now(), nullable=False)


class Reports(db.Model):
    id = Column(Integer, primary_key = True)
    reporter_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, server_default = func.now(), nullable=False)

class Bookmarks(db.Model):
    id = Column(Integer, primary_key = True)
    bookmarker_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    news_id = Column(Integer, ForeignKey('news.id'), nullable = False)

    news = db.relationship('News', backref=db.backref('news', uselist=False))

class Notifications(db.Model):
    id = Column(Integer, primary_key = True)
    notifier_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    activity = Column(String, nullable = False)
    link = Column(String, nullable = True)
    created_at = Column(DateTime, server_default = func.now(), nullable=False)