"""Custom dserver Blueprint"""
from flask_smorest.blueprint import Blueprint as FlaskSmorestBlueprint
from dserver.sort import SortMixin


class Blueprint(FlaskSmorestBlueprint, SortMixin):
    """Bring together flask-smorest blueprint and custom sort mixin."""
    pass

