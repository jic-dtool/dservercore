"""Sort feature

Introduces and parses sort parameter for blueprints.
"""
from copy import deepcopy
from functools import wraps
import http
import json
import warnings

from flask import request

import marshmallow as ma
from webargs.flaskparser import FlaskParser

from flask_smorest.utils import unpack_tuple_response


ASCENDING = 1
DESCENDING = -1


class SortParameters:
    """Holds sort arguments

    :param list of str sort: list of fields
    :param list of int order: ASCENDING (1) or DESCENDING (-1)
    """

    def __init__(self, sort, order):

        self.sort = sort
        self.order = order

    def __repr__(self):
        sort_string = ','.join(('+' if o > 0 else '-') + s for s, o in zip(self.sort, self.order))
        return (
            f"{self.__class__.__name__}"
            f"(sort={sort_string!r})"
        )


def _sort_parameters_schema_factory(def_sort, def_allowed_sort_fields):
    """Generate a SortParametersSchema"""

    class SortParametersSchema(ma.Schema):
        """Deserializes sort params into SortParameters"""

        class Meta:
            ordered = True
            unknown = ma.EXCLUDE

        sort = ma.fields.List(ma.fields.String(
            load_default=def_sort, validate=ma.validate.OneOf(
                [prefix + suffix for prefix in ['+','-',''] for suffix in def_allowed_sort_fields])
        ))

        @ma.post_load
        def make_sorter(self, data, **kwargs):
            return SortParameters(**data)

    return SortParametersSchema


class SortMixin:
    """Extend Blueprint to add Sort feature"""

    SORT_ARGUMENTS_PARSER = FlaskParser()

    # Global default sort parameters
    # Can be overridden to provide custom defaults
    DEFAULT_ALLOWED_SORT_FIELDS = []
    DEFAULT_SORT_PARAMETERS = {"sort": ""}

    def sort(self, *, sort=None, allowed_sort_fields=None):
        """Decorator adding sorting to the endpoint

        :param str sort: Default requested sort string
        :param list of str allowed_sort_fields: Allowed sort fields

        If a :class:`Page <Page>` class is provided, it is used to paginate the
        data returned by the view function, typically a lazy database cursor.

        Otherwise, pagination is handled in the view function.

        The decorated function may return a tuple including status and/or
        headers, like a typical flask view function. It may not return a
        ``Response`` object.

        See :doc:`Pagination <pagination>`.
        """
        if sort is None:
            sort = self.DEFAULT_SORT_PARAMETERS["sort"]
        if allowed_sort_fields is None:
            allowed_sort_fields = self.DEFAULT_ALLOWED_SORT_FIELDS

        sort_params_schema = _sort_parameters_schema_factory(sort, allowed_sort_fields)

        parameters = {
            "in": "query",
            "schema": _sort_parameters_schema_factory,
        }

        error_status_code = self.SORT_ARGUMENTS_PARSER.DEFAULT_VALIDATION_STATUS

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                sort_params = self.SORT_ARGUMENTS_PARSER.parse(
                    sort_params_schema, request, location="query"
                )

                # Pagination in resource code: inject page_params as kwargs
                kwargs["sort_parameters"] = sort_params

                # Execute decorated function
                result, status, headers = unpack_tuple_response(func(*args, **kwargs))

                return result, status, headers

            # Add pagination params to doc info in wrapper object
            wrapper._apidoc = deepcopy(getattr(wrapper, "_apidoc", {}))
            wrapper._apidoc["sort"] = {
                "parameters": parameters,
                "response": {
                    error_status_code: http.HTTPStatus(error_status_code).name,
                },
            }

            return wrapper

        return decorator