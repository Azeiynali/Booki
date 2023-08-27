from app import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=False, nullable=False)
    coins = db.Column(db.Integer)
    password = db.Column(db.String, unique=False)
    avatar = db.Column(db.String, unique=False)

    posts = db.relationship("Post", backref='writer', lazy=True)
    comments = db.relationship("Comment", backref='writer', lazy=True)
    images = db.relationship("Image", backref='writer', lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), default=datetime.now, nullable=False, unique=False)
    content = db.Column(db.Text, nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), default=datetime.now, nullable=False, unique=False)
    content = db.Column(db.Text, nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Columns(db.String)
    date = db.Column(db.DateTime(), default=datetime.now, nullable=False, unique=False)
    content = db.Column(db.Text, nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Medal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Columns(db.String)
    title = db.Column(db.String, nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Fallow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower = db.Column(db.Integer)
    followed = db.Column(db.Integer)
