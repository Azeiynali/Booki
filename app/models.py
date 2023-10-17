from app import db, Login_mg
from datetime import datetime
from flask_login import UserMixin
import re


@Login_mg.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=False, nullable=False)
    coins = db.Column(db.Integer, default=0)
    password = db.Column(db.String, unique=False)
    avatar = db.Column(db.String, unique=False)
    notifictions = db.Column(db.String, unique=False, default="[]")

    posts = db.relationship("Post", backref='writer', lazy=True)
    messages = db.relationship("Message", backref='writer', lazy=True)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id} ---> {self.username})'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String)
    date = db.Column(db.DateTime(), default=datetime.now, nullable=False, unique=False)
    content = db.Column(db.Text, nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id} ---> {self.date})'

class Medal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String, unique=False)
    title = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id} ---> {self.title})'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(), default= str(re.findall(r"(\d+:\d+):\d+", str(datetime.now()))[0]), nullable=False, unique=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id} ---> {self.date})'


class Fallow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower = db.Column(db.Integer)
    followed = db.Column(db.Integer)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.follower} ---> {self.followed})'
