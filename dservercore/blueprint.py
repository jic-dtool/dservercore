"""Custom dserver Blueprint"""
from flask_smorest.blueprint import Blueprint as FlaskSmorestBlueprint
from dservercore.sort import SortMixin


class Blueprint(FlaskSmorestBlueprint, SortMixin):
    """Bring together flask-smorest blueprint and custom sort mixin."""

    def __init__(self, *args, **kwargs):
        self.description = kwargs.pop("description", "")

        super().__init__(*args, **kwargs)

        self._prepare_doc_cbks.append(self._prepare_sort_doc)

