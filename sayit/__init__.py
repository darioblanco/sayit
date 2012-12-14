# -*- coding: UTF-8 -*-
from flask import Flask
from flask.ext.login import LoginManager
from logbook import MonitoringFileHandler, NullHandler

from sayit.settings import DEBUG, LOG_FILE, SECRET_KEY


# Set up logs
if DEBUG:
    LEVEL = 'DEBUG'
else:
    LEVEL = 'INFO'
    null_handler = NullHandler()
    null_handler.push_application()

log_handler = MonitoringFileHandler(LOG_FILE, level=LEVEL)
log_handler.push_application()

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = "login"
login_manager.refresh_view = "reauth"

import views
