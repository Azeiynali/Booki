from app import db, Login_mg
from datetime import datetime
from flask_login import UserMixin
import re
import random

@Login_mg.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# models

# users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    gems = db.Column(db.Integer, default=0)
    password = db.Column(db.String, unique=False)
    avatar = db.Column(db.String, unique=False)
    date = db.Column(db.DateTime, default=datetime.now, nullable=False, unique=False)
    registered = db.Column(db.Boolean, unique=False, default=False)
    country = db.Column(db.String, unique=False)
    city = db.Column(db.String, unique=False)
    tags = db.Column(db.String, unique=False)
    salt = db.Column(db.String, unique=False)
    bio = db.Column(db.String, unique=False, default="")
    # man, woman
    gender = db.Column(db.String, unique=False)

    posts = db.relationship("Post", backref="writer", lazy=True)
    messages = db.relationship("Message", backref="writer", lazy=True)
    notifications = db.relationship("Notification", backref="user", lazy=True)
    # recovery codes
    rec_codes = db.relationship("RecoveryCode", backref="user", lazy=True)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id} ---> {self.username})"


# notifications
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, unique=False, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now, nullable=False, unique=False)
    seened = db.Column(db.Boolean, default=False, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id} ---> {self.content[:20]})"


# posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.now, nullable=False, unique=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String, unique=False)
    description = db.Column(db.String, unique=False)
    group = db.Column(db.String, unique=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id} ---> {self.date})"


# messages
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(
        db.String(),
        default=str(re.findall(r"(\d+:\d+):\d+", str(datetime.now()))[0]),
        nullable=False,
        unique=False,
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id} ---> {self.date})"


# Follows
class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower = db.Column(db.Integer)
    followed = db.Column(db.Integer)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.follower} ---> {self.followed})"


# likes
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    liker = db.Column(db.Integer)
    liked = db.Column(db.Integer)


# RecoveryCodes
class RecoveryCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now, nullable=False, unique=False)
    code = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False, unique=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
