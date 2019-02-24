'''A module to initialize db and Flask() without the rest of the logic, fo ruse with cli commands'''
import os
import logging
from datetime import date
from flask import Flask, json
from flask_sqlalchemy import SQLAlchemy
from config import DevConfig, TestConfig, ProdConfig


def init_app(test=False):
    app = Flask(__name__)
    # When deployed to GAE, GAE_ENV will be set to `standard`
    if os.environ.get('GAE_ENV') == 'standard':
        app.config.from_object(ProdConfig)
    elif test:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(DevConfig)
    logging.info(f'CONNECTING TO DB VIA {app.config["HOST"]}')

    return app


def init_db(app=None):
    db = SQLAlchemy()
    if app is not None:
        db.init_app(app)
    return db


class CustomJSONEncoder(json.JSONEncoder):
    """jsonify will turn datetimes into 'yyyy-mm-dd' """

    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat().split("T")[0]
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return json.JSONEncoder.default(self, obj)