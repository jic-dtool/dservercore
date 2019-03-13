import os
basedir = os.path.abspath(os.path.dirname(__file__))

_DEFAULT_SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(
    os.path.join(basedir, "..", 'app.db')
)
_DEFAULT_MONGO_URI = 'mongodb://localhost:27017/dtool_info'


class Config(object):
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  \
        or _DEFAULT_SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_URI = os.environ.get('MONGO_URI') or _DEFAULT_MONGO_URI
