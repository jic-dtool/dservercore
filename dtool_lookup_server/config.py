import os

basedir = os.path.abspath(os.path.dirname(__file__))

_DEFAULT_SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(
    os.path.join(basedir, "..", 'app.db')
)
_DEFAULT_MONGO_URI = 'mongodb://localhost:27017/dtool_info'

if os.path.isfile(os.environ.get('JWT_PUBLIC_KEY_FILE', "")):
    _JWT_PUBLIC_KEY = open(os.environ.get('JWT_PUBLIC_KEY_FILE')).read()
else:
    _JWT_PUBLIC_KEY = ""

if os.path.isfile(os.environ.get('JWT_PRIVATE_KEY_FILE', "")):
    _JWT_PRIVATE_KEY = open(os.environ.get('JWT_PRIVATE_KEY_FILE')).read()
else:
    _JWT_PRIVATE_KEY = ""


class Config(object):
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  \
        or _DEFAULT_SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_URI = os.environ.get('MONGO_URI') or _DEFAULT_MONGO_URI
    JWT_ALGORITHM = "RS256"
    JWT_TOKEN_LOCATION = "headers"
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_PRIVATE_KEY = _JWT_PRIVATE_KEY
    JWT_PUBLIC_KEY = _JWT_PUBLIC_KEY
