from os import path


class Config(object):
    PORT = 5500
    HOST = '0.0.0.0'
    URL_PREFIX = '/api'

    PROJECT_ROOT = path.abspath(path.dirname(__file__))
    TEMPLATE_FOLDER = path.join(PROJECT_ROOT, 'templates')
    UPLOADED_FILES = "D:/RevManager/UPLOAD_FILES"
    MYSQL_DATABASE_DB = 'db_name'
    MYSQL_DATABASE_USER = 'rev_manager'
    MYSQL_DATABASE_HOST = 'locallhost'
    MYSQL_DATABASE_PASSWORD = 'passworf'

    SECRET_KEY = 'secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'.format(MYSQL_DATABASE_USER,
                                                           MYSQL_DATABASE_PASSWORD,
                                                           MYSQL_DATABASE_HOST,
                                                           MYSQL_DATABASE_DB)