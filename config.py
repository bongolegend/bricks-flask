import os
import settings

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # for setting notifications to scheduler
    CRON_KEYS = [
        'day_of_week',
        'hour',
        'minute',
        'jitter',
        'end_date',
        'timezone',
    ]