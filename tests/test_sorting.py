"""Test SortMixin"""

import http

from itertools import product
from collections import namedtuple
import json

import pytest

from apispec.utils import build_reference

from flask.views import MethodView
from flask_smorest import Api

from dservercore.blueprint import Blueprint
from dservercore.sort import (
    CommaSeparatedListFlaskParser,
    SortParameters, ASCENDING, DESCENDING
)
from dservercore.sql_models import User, UserSchema

from unittest.mock import MagicMock

CUSTOM_SORT_PARAMS = (
    ["-is_admin","+username"],
    ["id", "username", "is_admin"]
)


def build_ref(spec, component_type, obj):
    return build_reference(component_type, spec.openapi_version.major, obj)

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
                for field, order in sort_parameters.order.items():
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
            for field, order in sort_parameters.order.items():
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
    # tmp_app_client.register_blueprint(blueprint)
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
            SortParameters(["+username","-is_admin"]).order
            == {
                'username': ASCENDING,
                'is_admin': DESCENDING
            }
    )

    assert (
            SortParameters(["+username"]).order
            == {
                'username': ASCENDING
            }
    )

    assert (
            SortParameters("+username").order
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

    assert data[0] == {'is_admin': False, 'username': 'grumpy'}
    assert data[1] == {'is_admin': False, 'username': 'sleepy'}
    assert data[2] == {'is_admin': True, 'username': 'snow-white'}

    # order 2
    response = tmp_app_with_dummy_sort_blueprint_client.get(
        "/test/", query_string={"sort": "-is_admin,+username"}
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 3

    assert data[0] == {'is_admin': True, 'username': 'snow-white'}
    assert data[1] == {'is_admin': False, 'username': 'grumpy'}
    assert data[2] == {'is_admin': False, 'username': 'sleepy'}

    # order 3
    response = tmp_app_with_dummy_sort_blueprint_client.get(
        "/test/", query_string={"sort": "-is_admin,-username"}
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 3

    assert data[0] == {'is_admin': True, 'username': 'snow-white'}
    assert data[1] == {'is_admin': False, 'username': 'sleepy'}
    assert data[2] == {'is_admin': False, 'username': 'grumpy'}

    # order 4
    response = tmp_app_with_dummy_sort_blueprint_client.get(
        "/test/", query_string={"sort": "+is_admin,-username"}
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 3

    assert data[0] == {'is_admin': False, 'username': 'sleepy'}
    assert data[1] == {'is_admin': False, 'username': 'grumpy'}
    assert data[2] == {'is_admin': True, 'username': 'snow-white'}

    # order 6 - default
    response = tmp_app_with_dummy_sort_blueprint_client.get(
        "/test/"
    )

    assert response.status_code == 200
    data = response.json

    assert len(data) == 3

    assert data[0] == {'is_admin': True, 'username': 'snow-white'}
    assert data[1] == {'is_admin': False, 'username': 'grumpy'}
    assert data[2] == {'is_admin': False, 'username': 'sleepy'}


@pytest.mark.parametrize("header_name", ("X-Dummy-Name", None))
def test_sort_custom_header_field_name(tmp_app, header_name):
    """Test PAGINATION_HEADER_NAME overriding"""
    api = Api(tmp_app)

    class CustomBlueprint(Blueprint):
        SORT_HEADER_NAME = header_name

    blp = CustomBlueprint("test", __name__, url_prefix="/test")

    @blp.route("/")
    @blp.response(200)
    @blp.sort(sort=["-is_admin","+username"])
    def func(sort_parameters):
        return

    api.register_blueprint(blp)
    client = tmp_app.test_client()
    response = client.get("/test/")
    assert response.status_code == 200
    assert "X-Sort" not in response.headers
    if header_name is not None:
        assert json.loads(response.headers[header_name]) == (
            {"sort": {"is_admin": -1, "username": 1}}
        )
        # Also check there is only one pagination header
        assert len(response.headers.getlist(header_name)) == 1


@pytest.mark.parametrize("openapi_version", ("2.0", "3.0.2"))
def test_sort_is_documented(tmp_app, schemas, openapi_version):
    tmp_app.config["OPENAPI_VERSION"] = openapi_version
    api = Api(tmp_app)
    blp = Blueprint("test", __name__, url_prefix="/test")

    @blp.route("/")
    @blp.sort(sort=["-is_admin","+username"], allowed_sort_fields=["id", "username", "is_admin"])
    def func():
        """Dummy view func"""

    api.register_blueprint(blp)
    spec = api.spec.to_dict()

    # Check parameters are documented
    parameters = spec["paths"]["/test/"]["get"]["parameters"]

    if openapi_version == '2.0':
        expected_parameters = [
            {
                'collectionFormat': 'multi',
                'default': ['-is_admin', '+username'],
                'in': 'query',
                'items': {'enum': ['+id',
                                   '+username',
                                   '+is_admin',
                                   '-id',
                                   '-username',
                                   '-is_admin',
                                   'id',
                                   'username',
                                   'is_admin'],
                          'type': 'string'},
                'name': 'sort',
                'required': False,
                'type': 'array'}]
    else:
        expected_parameters = [
            {
                'explode': True,
                'in': 'query',
                'name': 'sort',
                'required': False,
                'schema': {'default': ['-is_admin', '+username'],
                           'items': {'enum': ['+id',
                                              '+username',
                                              '+is_admin',
                                              '-id',
                                              '-username',
                                              '-is_admin',
                                              'id',
                                              'username',
                                              'is_admin'],
                                     'type': 'string'},
                           'type': 'array'},
                'style': 'form'}]

    assert parameters == expected_parameters

    # Query string parameters


# Non-regression test for https://github.com/marshmallow-code/flask-smorest/issues/578 # noqa: E501
@pytest.mark.parametrize("openapi_version", ("2.0", "3.0.2"))
def test_sort_doc_preserves_other_headers_doc(tmp_app, openapi_version):
    tmp_app.config["OPENAPI_VERSION"] = openapi_version
    api = Api(tmp_app)
    blp = Blueprint("test", __name__, url_prefix="/test")

    @blp.route("/")
    @blp.response(
        200, headers={"X-Version": {"description": "Version of this API endpoint."}}
    )
    @blp.sort(sort=["-is_admin","+username"], allowed_sort_fields=["id", "username", "is_admin"])
    def func():
        """Dummy view func"""

    api.register_blueprint(blp)
    spec = api.spec.to_dict()

    # Check both headers are properly documented
    headers = spec["paths"]["/test/"]["get"]["responses"]["200"]["headers"]
    assert "X-Version" in headers
    assert headers["X-Version"] == {"description": "Version of this API endpoint."}
    assert "X-Sort" in headers
    if openapi_version == "2.0":
        assert headers["X-Sort"] == {
            "description": "Sort metadata",
            "schema": {"$ref": "#/definitions/SortMetadata"},
        }
    else:
        assert headers["X-Sort"] == {
            "description": "Sort metadata",
            "schema": {"$ref": "#/components/schemas/SortMetadata"}
        }

@pytest.mark.parametrize("error_code", (400, 422))
@pytest.mark.parametrize("openapi_version", ("2.0", "3.0.2"))
def test_sort_documents_error_response(tmp_app, openapi_version, error_code):
    tmp_app.config["OPENAPI_VERSION"] = openapi_version
    api = Api(tmp_app)
    blp = Blueprint("test", __name__, url_prefix="/test")
    blp.SORT_ARGUMENTS_PARSER.DEFAULT_VALIDATION_STATUS = error_code

    @blp.route("/")
    @blp.sort(sort=["-is_admin","+username"], allowed_sort_fields=["id", "username", "is_admin"])
    def func():
        """Dummy view func"""

    api.register_blueprint(blp)
    spec = api.spec.to_dict()
    assert spec["paths"]["/test/"]["get"]["responses"][
        str(error_code)
    ] == build_ref(api.spec, "response", http.HTTPStatus(error_code).name)