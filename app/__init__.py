from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import secrets
import logging
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
)
app.logger = logging.getLogger(__name__)

file_handler = logging.FileHandler("app.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../base.db"
app.config["SECRET_KEY"] = os.urandom(23)
app.config["UPLOAD_FOLDER"] = "app/static/pictures"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg"}
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg"}
app.config["SECRET_KEY"] = secrets.token_hex(16)

app.secret_key = secrets.token_hex(16)

db = SQLAlchemy(app)
Login_mg = LoginManager(app)
Login_mg.login_view = "/"
Login_mg.login_message = ""

from app.routes import *

with app.app_context():
    db.create_all()
