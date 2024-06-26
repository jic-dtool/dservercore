"""Sort feature

Introduces and parses sort parameter for blueprints.
"""
from copy import deepcopy
from functools import wraps
import http
import json
import re

from flask import request

import marshmallow as ma
from webargs.flaskparser import FlaskParser

from flask_smorest.utils import unpack_tuple_response


ASCENDING = 1
DESCENDING = -1


class CommaSeparatedListFlaskParser(FlaskParser):
    """Parses nested query args

    This parser handles sort arguments of the comma-separated list format
        ?sort=+username,-is_admin
    or similar.

    For example, the URL query params `?sort=+username,-is_admin
    will yield the following dict:

        {
            'sort': ['+username', '-is_admin']
        }
    """

    def load_querystring(self, req, schema):
        return _structure_dict(req.args)


def _structure_dict(dict_):
    def key_value_list_pair(r, key, value):
        m = re.match(r"([^,]*),(.*)", value)
        if m:
            if m.group(1) is not None and len(m.group(1)) > 0 and key in r:
                r[key].append(m.group(1))
            elif m.group(1) is not None and len(m.group(1)) > 0:
                r[key] = [m.group(1)]
            key_value_list_pair(r, key, m.group(2))
        else:
            if len(value) > 0 and key not in r:
                r[key] = [value]
            elif len(value) > 0:
                r[key].append(value)

    r = {}

    for k, v in dict_.items():
        key_value_list_pair(r, k, v)
    return r


class SortParameters:
    """Holds sort arguments

    :param list of str sort: list of fields
    :param list of int order: ASCENDING (1) or DESCENDING (-1)
    """

    def __init__(self, sort):

        if isinstance(sort, str):
            self._sort = [sort]
        else:
            self._sort = sort

    def __repr__(self):
        sort_string = ','.join(self._sort)
        return (
            f"{self.__class__.__name__}"
            f"(sort={sort_string!r})"
        )

    @property
    def order(self):
        d = {}
        for field in self._sort:
            if field.startswith('-'):
                d[field[1:]] = DESCENDING
            elif field.startswith('+'):
                d[field[1:]] = ASCENDING
            else:
                d[field] = ASCENDING

        return d


def _sort_parameters_schema_factory(def_sort, def_allowed_sort_fields):
    """Generate a SortParametersSchema"""

    class SortParametersSchema(ma.Schema):
        """Deserializes sort params into SortParameters"""

        class Meta:
            ordered = True
            unknown = ma.EXCLUDE

        sort = ma.fields.List(
            ma.fields.String(
                validate=ma.validate.OneOf(
                    [prefix + suffix for prefix in ['+','-',''] for suffix in def_allowed_sort_fields]),
                ),
            load_default=def_sort
            )

        @ma.post_load
        def make_sorter(self, data, **kwargs):
            return SortParameters(**data)

    return SortParametersSchema


class SortMetadataSchema(ma.Schema):
    """Sort metadata schema

    Used to serialize sort metadata.
    Its main purpose is to document the sort metadata.
    """

    sort = ma.fields.Dict(keys=ma.fields.String(), values=ma.fields.Integer())

    class Meta:
        ordered = True


SORT_HEADER = {
    "description": "Sort metadata",
    "schema": SortMetadataSchema,
}


class SortMixin:
    """Extend Blueprint to add Sort feature"""

    SORT_ARGUMENTS_PARSER = CommaSeparatedListFlaskParser()

    # Name of field to use for sort metadata response header
    # Can be overridden. If None, no sort header is returned.
    SORT_HEADER_NAME = "X-Sort"

    # Global default sort parameters
    # Can be overridden to provide custom defaults
    DEFAULT_ALLOWED_SORT_FIELDS = []
    DEFAULT_SORT_PARAMETERS = {"sort": []}

    def sort(self, *, sort=None, allowed_sort_fields=None):
        """Decorator adding sorting to the endpoint

        :param str sort: Default requested sort string
        :param list of str allowed_sort_fields: Allowed sort fields

        The decorated function may return a tuple including status and/or
        headers, like a typical flask view function. It may not return a
        ``Response`` object.
        """
        if sort is None:
            sort = self.DEFAULT_SORT_PARAMETERS["sort"]
        if allowed_sort_fields is None:
            allowed_sort_fields = self.DEFAULT_ALLOWED_SORT_FIELDS

        sort_params_schema = _sort_parameters_schema_factory(
            sort, allowed_sort_fields)

        parameters = {
            "in": "query",
            "schema": sort_params_schema,
        }

        error_status_code = self.SORT_ARGUMENTS_PARSER.DEFAULT_VALIDATION_STATUS

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                sort_params = self.SORT_ARGUMENTS_PARSER.parse(
                    sort_params_schema, request, location="query"
                )

                # sort in resource code: inject sort_params as kwargs
                kwargs["sort_parameters"] = sort_params

                # Execute decorated function
                result, status, headers = unpack_tuple_response(func(*args, **kwargs))

                # Set sort metadata in response
                if self.SORT_HEADER_NAME is not None:
                    result, headers = self._set_sort_metadata(
                            sort_params, result, headers
                        )

                return result, status, headers

            # Add sort params to doc info in wrapper object
            wrapper._apidoc = deepcopy(getattr(wrapper, "_apidoc", {}))
            wrapper._apidoc["sort"] = {
                "parameters": parameters,
                "response": {
                    error_status_code: http.HTTPStatus(error_status_code).name,
                },
            }

            return wrapper

        return decorator

    @staticmethod
    def _make_sort_metadata(sort):
        """Build sort metadata from sort

        Override this to use another sort metadata structure
        """
        sort_metadata = {}
        sort_metadata["sort"] = sort

        return SortMetadataSchema().dump(sort_metadata)

    def _set_sort_metadata(self, sort_params, result, headers):
        """Add sort metadata to headers

        Override this to set sort data another way
        """
        if headers is None:
            headers = {}
        headers[self.SORT_HEADER_NAME] = json.dumps(
            self._make_sort_metadata(sort_params.order)
        )
        return result, headers

    def _document_sort_metadata(self, spec, resp_doc):
        """Document sort metadata header

        Override this to document custom sort metadata
        """
        resp_doc.setdefault("headers", {}).update(
            {
                self.SORT_HEADER_NAME: SORT_HEADER
            }
        )

    def _prepare_sort_doc(self, doc, doc_info, *, spec, **kwargs):
        operation = doc_info.get("sort")
        if operation:
            doc.setdefault("parameters", []).append(operation["parameters"])
            doc.setdefault("responses", {}).update(operation["response"])
            success_status_codes = doc_info.get("success_status_codes", [])
            for success_status_code in success_status_codes:
                self._document_sort_metadata(
                    spec, doc["responses"][success_status_code]
                )
        return doc