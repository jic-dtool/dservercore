"""Test SortMixin"""

import http

from itertools import product
from collections import namedtuple
import json

import pytest

from flask.views import MethodView
from flask_smorest import Api

from dserver.blueprint import Blueprint
from dserver.sort import (
    CommaSeparatedListFlaskParser,
    SortParameters, ASCENDING, DESCENDING
)
from dserver.sql_models import User, UserSchema

from unittest.mock import MagicMock

CUSTOM_SORT_PARAMS = (
    ["-is_admin","+username"],
    ["id", "username", "is_admin"]
)


def sort_blueprint(collection, schemas, as_method_view):
    """Return a basic API sample with sorting"""

    blp = Blueprint("test", __name__, url_prefix="/test")

    sort, allowed_sort_fields = CUSTOM_SORT_PARAMS

    if as_method_view:

        @blp.route("/")
        class Resource(MethodView):
            @blp.response(200, schemas.DocSchema(many=True))
            @blp.sort(sort=sort, allowed_sort_fields=allowed_sort_fields)
            def get(self, sort_parameters):
                order_by_args = []
                for field, order in sort_parameters.order().items():
                    if not hasattr(collection, field):
                        raise ValueError(f"Collection '{collection}' has no field '{field}'.")
                    if order == DESCENDING:
                        order_by_args.append(getattr(collection, field).desc())
                    else: # ascending
                        order_by_args.append(getattr(collection, field))
                return collection.query.order_by(*order_by_args).all()
    else:
        @blp.route("/")
        @blp.response(200, schemas.DocSchema(many=True))
        @blp.sort(sort=sort, allowed_sort_fields=allowed_sort_fields)
        def get_resources(sort_parameters):
            order_by_args = []
            print(sort_parameters)
            for field, order in sort_parameters.order().items():
                if not hasattr(collection, field):
                    raise ValueError(f"Collection '{collection}' has no field '{field}'.")
                if order == DESCENDING:
                    order_by_args.append(getattr(collection, field).desc())
                else:  # ascending
                    order_by_args.append(getattr(collection, field))
            return collection.query.order_by(*order_by_args).all()

    return blp


@pytest.fixture(params=product((True, False)))
def tmp_app_with_dummy_sort_blueprint(request, tmp_app_with_data, schemas):
    """Return an app client for each configuration

    - function / method view
    - default / custom pagination parameters
    """
    as_method_view = request.param

    blueprint = sort_blueprint(User, schemas, as_method_view)

    api = Api(tmp_app_with_data)
    api.register_blueprint(blueprint)
    # tmp_app_with_data_client.register_blueprint(blueprint)
    return tmp_app_with_data


@pytest.fixture
def tmp_app_with_dummy_sort_blueprint_client(tmp_app_with_dummy_sort_blueprint):
    return tmp_app_with_dummy_sort_blueprint.test_client()


@pytest.fixture
def schemas():
    """Provide response and query schemas for test blueprint."""
    return namedtuple("Model", ("DocSchema", "QueryArgsSchema"))(
        UserSchema, None
    )


def test_sort_parameters_repr():
    print(repr(SortParameters(["+username","-is_admin"])))
    assert (
            repr(SortParameters(["+username","-is_admin"]))
            == "SortParameters(sort='+username,-is_admin')"
    )

    assert (
            repr(SortParameters(["+username"]))
            == "SortParameters(sort='+username')"
    )

    assert (
            repr(SortParameters("+username"))
            == "SortParameters(sort='+username')"
    )


def test_sort_parameters_order():
    assert (
            SortParameters(["+username","-is_admin"]).order()
            == {
                'username': ASCENDING,
                'is_admin': DESCENDING
            }
    )

    assert (
            SortParameters(["+username"]).order()
            == {
                'username': ASCENDING
            }
    )

    assert (
            SortParameters("+username").order()
            == {
                'username': ASCENDING
            }
    )


def test_custom_flask_parser():
    request = MagicMock()

    request.args = {"sort": "id,+username,-is_admin"}
    assert (CommaSeparatedListFlaskParser().load_querystring(request, None)
            == {"sort": ["id", "+username", "-is_admin"]})

    request.args = {"sort": "id,+username,-is_admin,"}
    assert (CommaSeparatedListFlaskParser().load_querystring(request, None)
            == {"sort": ["id", "+username", "-is_admin"]})

    request.args = {"sort": ",id,+username,-is_admin,"}
    assert (CommaSeparatedListFlaskParser().load_querystring(request, None)
            == {"sort": ["id", "+username", "-is_admin"]})

    request.args = {"sort": ",,,id,,,+username,,,-is_admin,,,"}
    assert (CommaSeparatedListFlaskParser().load_querystring(request, None)
            == {"sort": ["id", "+username", "-is_admin"]})

    request.args = {"sort": "+username,-is_admin"}
    assert (CommaSeparatedListFlaskParser().load_querystring(request, None)
           == {"sort": ["+username", "-is_admin"]})

    request.args = {"sort": "+username,-is_admin,"}
    assert (CommaSeparatedListFlaskParser().load_querystring(request, None)
            == {"sort": ["+username", "-is_admin"]})

    request.args = {"sort": ",+username,-is_admin"}
    assert (CommaSeparatedListFlaskParser().load_querystring(request, None)
            == {"sort": ["+username", "-is_admin"]})

    request.args = {"sort": "+username,,-is_admin"}
    assert (CommaSeparatedListFlaskParser().load_querystring(request, None)
            == {"sort": ["+username", "-is_admin"]})

    request.args = {"sort": "+username"}
    assert (CommaSeparatedListFlaskParser().load_querystring(request, None)
            == {"sort": ["+username"]})

    request.args = {"sort": "+username,"}
    assert (CommaSeparatedListFlaskParser().load_querystring(request, None)
            == {"sort": ["+username"]})

    request.args = {"sort": ",+username,"}
    assert (CommaSeparatedListFlaskParser().load_querystring(request, None)
            == {"sort": ["+username"]})

    request.args = {"sort": "-id"}
    assert (CommaSeparatedListFlaskParser().load_querystring(request, None)
            == {"sort": ["-id"]})

    request.args = {"sort": ",,,"}
    assert (CommaSeparatedListFlaskParser().load_querystring(request, None)
            == {})


def test_sort_parameters(tmp_app_with_dummy_sort_blueprint_client):
    # order 1
    response = tmp_app_with_dummy_sort_blueprint_client.get(
        "/test/", query_string={"sort": "+username,-is_admin"}
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 3

    assert data[0] == {'id': 1, 'is_admin': False, 'username': 'grumpy'}
    assert data[1] == {'id': 2, 'is_admin': False, 'username': 'sleepy'}
    assert data[2] == {'id': 3, 'is_admin': True, 'username': 'snow-white'}

    # order 2
    response = tmp_app_with_dummy_sort_blueprint_client.get(
        "/test/", query_string={"sort": "-is_admin,+username"}
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 3

    assert data[0] == {'id': 3, 'is_admin': True, 'username': 'snow-white'}
    assert data[1] == {'id': 1, 'is_admin': False, 'username': 'grumpy'}
    assert data[2] == {'id': 2, 'is_admin': False, 'username': 'sleepy'}

    # order 3
    response = tmp_app_with_dummy_sort_blueprint_client.get(
        "/test/", query_string={"sort": "-is_admin,-username"}
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 3

    assert data[0] == {'id': 3, 'is_admin': True, 'username': 'snow-white'}
    assert data[1] == {'id': 2, 'is_admin': False, 'username': 'sleepy'}
    assert data[2] == {'id': 1, 'is_admin': False, 'username': 'grumpy'}

    # order 4
    response = tmp_app_with_dummy_sort_blueprint_client.get(
        "/test/", query_string={"sort": "+is_admin,-username"}
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 3

    assert data[0] == {'id': 2, 'is_admin': False, 'username': 'sleepy'}
    assert data[1] == {'id': 1, 'is_admin': False, 'username': 'grumpy'}
    assert data[2] == {'id': 3, 'is_admin': True, 'username': 'snow-white'}

    # order 5
    response = tmp_app_with_dummy_sort_blueprint_client.get(
        "/test/", query_string={"sort": "-id"}
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 3

    assert data[0] == {'id': 3, 'is_admin': True, 'username': 'snow-white'}
    assert data[1] == {'id': 2, 'is_admin': False, 'username': 'sleepy'}
    assert data[2] == {'id': 1, 'is_admin': False, 'username': 'grumpy'}

    # order 6 - default
    response = tmp_app_with_dummy_sort_blueprint_client.get(
        "/test/"
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 3

    assert data[0] == {'id': 3, 'is_admin': True, 'username': 'snow-white'}
    assert data[1] == {'id': 1, 'is_admin': False, 'username': 'grumpy'}
    assert data[2] == {'id': 2, 'is_admin': False, 'username': 'sleepy'}
