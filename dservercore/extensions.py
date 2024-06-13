"""Flask extensions"""
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager

sql_db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()