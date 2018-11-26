import os
import settings

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    # SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    SQLALCHEMY_DATABASE_URI = os.environ['DB_URL']
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

class ProdConfig(Config):
    # further sqlalchemy config options: http://flask-sqlalchemy.pocoo.org/2.3/config/
    db_user = os.environ.get('CLOUD_SQL_USERNAME')
    db_password = os.environ.get('CLOUD_SQL_PASSWORD')
    db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
    host = f'cloudsql/{os.environ.get('CLOUD_SQL_CONNECTION_NAME')}'
    SQLALCHEMY_DATABASE_URI = f'postgres://{db_user}:{db_password}@{host}/{db_name}'
