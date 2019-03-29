import os

_HERE = os.path.abspath(os.path.dirname(__file__))


def _get_file_content(key, default=""):
    file_path = os.environ.get(key, "")
    if os.path.isfile(file_path):
        content = open(file_path).read()
    else:
        content = ""
    return content


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'SQLALCHEMY_DATABASE_URI',
        'sqlite:///{}'.format(os.path.join(_HERE, "..", 'app.db'))
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_URI = os.environ.get(
        'MONGO_URI',
        'mongodb://localhost:27017/dtool_info'
    )
    JWT_ALGORITHM = "RS256"
    JWT_TOKEN_LOCATION = "headers"
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_PRIVATE_KEY = _get_file_content("JWT_PRIVATE_KEY_FILE")
    JWT_PUBLIC_KEY = _get_file_content("JWT_PUBLIC_KEY_FILE")
    JSONIFY_PRETTYPRINT_REGULAR = True
