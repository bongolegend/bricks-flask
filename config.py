import os
import settings

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TWILIO_ACCOUNT_SID = os.environ.get('TEST_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TEST_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TEST_FROM_NUMBER')
    TEST_TO_NUMBER = os.environ.get('TEST_TO_NUMBER')


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('LOCAL_DB_URL')
    HOST = SQLALCHEMY_DATABASE_URI


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL')
    HOST = SQLALCHEMY_DATABASE_URI
    TESTING = True



class ProdConfig(Config):
    db_user = os.environ.get('CLOUD_SQL_USERNAME')
    db_password = os.environ.get('CLOUD_SQL_PASSWORD')
    db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
    HOST = f'/cloudsql/{os.environ.get("CLOUD_SQL_CONNECTION_NAME")}'
    SQLALCHEMY_DATABASE_URI = f'postgres:///{db_name}?host={HOST}&user={db_user}&password={db_password}&sslmode=disable'
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')