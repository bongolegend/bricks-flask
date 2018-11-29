'''A module to initialize db and Flask() without the rest of the logic, fo ruse with cli commands'''
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config, ProdConfig


def init_app():
    app = Flask(__name__)
    # When deployed to GAE, GAE_ENV will be set to `standard`
    if os.environ.get('GAE_ENV') == 'standard':
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(Config)
    logging.info(f'CONNECTING TO DB VIA {app.config["HOST"]}')

    return app


def init_db(app=None):
    db = SQLAlchemy()
    if app is not None:
        db.init_app(app)
    return db

def init_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.start()
    return scheduler