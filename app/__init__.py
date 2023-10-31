from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../base.db'
app.config['SECRET_KEY'] = os.urandom(23)
app.config['UPLOAD_FOLDER'] = 'app/static/pictures'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}
app.secret_key = os.urandom(24)

db = SQLAlchemy(app)
Login_mg = LoginManager(app)
Login_mg.login_view = '/'
Login_mg.login_message = ''

from app.routes import *

with app.app_context():
    db.create_all()