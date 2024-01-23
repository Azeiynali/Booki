from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import secrets
import logging

app = Flask(__name__)

# a limiter for Limit the number of requests
limiter = Limiter(
    get_remote_address,
    app=app,
)
# a logger for log everything!
app.logger = logging.getLogger(__name__)

# set log file and log format
file_handler = logging.FileHandler("app.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

# --- app configs ----
# SQLite Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../base.db"
# secret key
app.config["SECRET_KEY"] = secrets.token_hex(16)
# set upload folder
app.config["UPLOAD_FOLDER"] = "app/static/pictures"
# allowed files to upload
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg"}

# set database variable
db = SQLAlchemy(app)

# set login manager
Login_mg = LoginManager(app)
Login_mg.login_view = "/"
Login_mg.login_message = ""

# import routes
from app.routes import *

# create database
with app.app_context():
    db.create_all()
