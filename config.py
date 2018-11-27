import os
import settings

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    # SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    SQLALCHEMY_DATABASE_URI = os.environ.get('LOCAL_DB_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HOST = 'local'
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
    db_user = os.environ.get('CLOUD_SQL_USERNAME')
    db_password = os.environ.get('CLOUD_SQL_PASSWORD')
    db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
    HOST = f'/cloudsql/{os.environ.get("CLOUD_SQL_CONNECTION_NAME")}'
    SQLALCHEMY_DATABASE_URI = f'postgres:///{db_name}?host={HOST}&user={db_user}&password={db_password}&sslmode=disable'