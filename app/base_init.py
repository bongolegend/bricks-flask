'''A module to initialize db and Flask() without the rest of the logic, fo ruse with cli commands'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config


def init_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    return app


def init_db():
    return SQLAlchemy()


def init_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.start()
    return scheduler