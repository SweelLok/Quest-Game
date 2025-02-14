import os
from datetime import timedelta

from flask import Flask
from flask_login import LoginManager
from flask_compress import Compress

from connection import create_tables


app = Flask(__name__)
Compress(app)
login_manager = LoginManager()
login_manager.init_app(app)

app.config["SECRET_KEY"] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
app.config['SESSION_TYPE'] = 'filesystem'
login_manager.login_view = 'get_login'
login_manager.login_message = "Please log in to access this page."

create_tables()
