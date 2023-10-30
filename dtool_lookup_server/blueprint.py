from flask_smorest.blueprint import Blueprint as FlaskSmorestBlueprint
from dtool_lookup_server.sort import SortMixin


class Blueprint(FlaskSmorestBlueprint, SortMixin):
    pass

