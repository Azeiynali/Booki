from app import db, Login_mg
from datetime import datetime
from flask_login import UserMixin


@Login_mg.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=False, nullable=False)
    coins = db.Column(db.Integer)
    password = db.Column(db.String, unique=False)
    avatar = db.Column(db.String, unique=False)
    notifictions = db.Column(db.String, unique=False)

    posts = db.relationship("Post", backref='writer', lazy=True)
    comments = db.relationship("Comment", backref='writer', lazy=True)
    images = db.relationship("Image", backref='writer', lazy=True)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id} ---> {self.username})'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime(), default=datetime.now, nullable=False, unique=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id} ---> {self.date})'


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), default=datetime.now, nullable=False, unique=False)
    content = db.Column(db.Text, nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id} ---> {self.date})'


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String)
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
    date = db.Column(db.DateTime(), default=datetime.now, nullable=False, unique=False)
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
