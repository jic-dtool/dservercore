"""Test verification of the "aud" and "iss" claims of JWTs.

The dserver token generator plugins issue tokens with audience and issuer
"dserver". dserver verifies both by default, so that tokens signed with the
same key for another purpose are not accepted. Setting JWT_DECODE_AUDIENCE or
JWT_DECODE_ISSUER to an empty value disables the respective check.
"""

import datetime
import importlib
import os
import random
import string

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa



TEST_MONGO_URI = os.environ.get("TEST_MONGO_URI", "mongodb://localhost:27017/")


def _random_string(size=9, prefix="test_"):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return prefix + ''.join(random.choice(chars) for _ in range(size))


@pytest.fixture(scope="module")
def key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537,
                                           key_size=2048)
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


def _token(private_pem, **claims):
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": "grumpy",
        "iat": now,
        "nbf": now,
        "exp": now + datetime.timedelta(minutes=5),
        "type": "access",
        "fresh": False,
    }
    payload.update(claims)
    payload = {k: v for k, v in payload.items() if v is not None}
    return jwt.encode(payload, private_pem, algorithm="RS256")


def _make_app(request, public_pem, audience, issuer, private_pem=None):
    from flask import current_app

    from dservercore import create_app, sql_db
    from dservercore.utils import register_users

    tmp_mongo_db_name = _random_string()
    app = create_app({
        "CONFIG_SECRETS_TO_OBFUSCATE": [],
        "API_TITLE": "dservercore API",
        "API_VERSION": "v1",
        "OPENAPI_VERSION": "3.0.2",
        "SECRET_KEY": "secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "RETRIEVE_MONGO_URI": TEST_MONGO_URI,
        "RETRIEVE_MONGO_DB": tmp_mongo_db_name,
        "RETRIEVE_MONGO_COLLECTION": "datasets",
        "SEARCH_MONGO_URI": TEST_MONGO_URI,
        "SEARCH_MONGO_DB": tmp_mongo_db_name,
        "SEARCH_MONGO_COLLECTION": "datasets",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_ALGORITHM": "RS256",
        "JWT_PUBLIC_KEY": public_pem,
        "JWT_TOKEN_LOCATION": "headers",
        "JWT_HEADER_NAME": "Authorization",
        "JWT_HEADER_TYPE": "Bearer",
        "JWT_DECODE_AUDIENCE": audience,
        "JWT_DECODE_ISSUER": issuer,
        "JWT_ENCODE_AUDIENCE": audience,
        "JWT_ENCODE_ISSUER": issuer,
        "JWT_PRIVATE_KEY": private_pem,
        "MONGO_URI": TEST_MONGO_URI,
        "MONGO_DB": tmp_mongo_db_name,
        "MONGO_COLLECTION": "dependencies",
    })
    app.app_context().push()
    sql_db.Model.metadata.create_all(sql_db.engine)
    register_users([dict(username="grumpy")])

    @request.addfinalizer
    def teardown():
        current_app.retrieve.client.drop_database(tmp_mongo_db_name)
        current_app.search.client.drop_database(tmp_mongo_db_name)
        sql_db.session.remove()

    return app


def _make_client(request, public_pem, audience, issuer):
    return _make_app(request, public_pem, audience, issuer).test_client()


def _get_me(client, token):
    return client.get("/me", headers={"Authorization": f"Bearer {token}"})


@pytest.fixture
def reload_config(monkeypatch):
    """Return a function that re-evaluates dservercore.config with an env."""
    import dservercore.config

    def reload(**env):
        for key in ("JWT_DECODE_AUDIENCE", "JWT_DECODE_ISSUER"):
            monkeypatch.delenv(key, raising=False)
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        return importlib.reload(dservercore.config).Config

    yield reload

    monkeypatch.undo()
    importlib.reload(dservercore.config)


def test_config_requires_dserver_audience_and_issuer_by_default(reload_config):  # NOQA
    config = reload_config()
    assert config.JWT_DECODE_AUDIENCE == "dserver"
    assert config.JWT_DECODE_ISSUER == "dserver"


def test_config_audience_and_issuer_from_environment(reload_config):
    config = reload_config(
        JWT_DECODE_AUDIENCE="my-dserver", JWT_DECODE_ISSUER="my-idp")
    assert config.JWT_DECODE_AUDIENCE == "my-dserver"
    assert config.JWT_DECODE_ISSUER == "my-idp"


def test_config_empty_value_disables_check(reload_config):
    config = reload_config(JWT_DECODE_AUDIENCE="", JWT_DECODE_ISSUER="")
    assert config.JWT_DECODE_AUDIENCE is None
    assert config.JWT_DECODE_ISSUER is None
    assert config.JWT_ENCODE_AUDIENCE is None
    assert config.JWT_ENCODE_ISSUER is None


@pytest.mark.parametrize("env", [
    {},
    dict(JWT_DECODE_AUDIENCE="my-dserver", JWT_DECODE_ISSUER="my-idp"),
])
def test_config_issues_tokens_with_required_claims(reload_config, env):
    """Tokens issued by dserver itself (flask user token) must carry the
    audience and issuer dserver requires, or dserver rejects its own
    tokens."""
    config = reload_config(**env)
    assert config.JWT_ENCODE_AUDIENCE == config.JWT_DECODE_AUDIENCE
    assert config.JWT_ENCODE_ISSUER == config.JWT_DECODE_ISSUER


def test_token_from_flask_user_token_is_accepted(request, key_pair):
    private_pem, public_pem = key_pair
    app = _make_app(request, public_pem, "dserver", "dserver",
                    private_pem=private_pem)
    from dservercore.cli import generate_token
    result = app.test_cli_runner().invoke(generate_token, ["grumpy"])
    assert result.exit_code == 0, result.output
    token = result.output.strip()

    claims = jwt.decode(token, options={"verify_signature": False})
    assert claims["aud"] == "dserver"
    assert claims["iss"] == "dserver"
    response = _get_me(app.test_client(), token)
    assert response.status_code == 200, response.get_data(as_text=True)


def test_token_with_dserver_audience_and_issuer_is_accepted(request, key_pair):  # NOQA
    private_pem, public_pem = key_pair
    client = _make_client(request, public_pem, "dserver", "dserver")
    response = _get_me(client, _token(private_pem, aud="dserver",
                                      iss="dserver"))
    assert response.status_code == 200, response.get_data(as_text=True)


@pytest.mark.parametrize("claims", [
    dict(aud=None, iss="dserver"),
    dict(aud="other", iss="dserver"),
    dict(aud="dserver", iss=None),
    dict(aud="dserver", iss="other"),
])
def test_token_without_matching_audience_or_issuer_is_rejected(
        request, key_pair, claims):
    private_pem, public_pem = key_pair
    client = _make_client(request, public_pem, "dserver", "dserver")
    response = _get_me(client, _token(private_pem, **claims))
    assert response.status_code in (401, 422), \
        response.get_data(as_text=True)


def test_checks_can_be_disabled(request, key_pair):
    """With the checks disabled, tokens without the claims are accepted."""
    private_pem, public_pem = key_pair
    client = _make_client(request, public_pem, None, None)
    response = _get_me(client, _token(private_pem))
    assert response.status_code == 200, response.get_data(as_text=True)


def test_environment_without_override_is_unaffected():
    """Guard: the tests above must not leak environment changes."""
    assert "JWT_DECODE_AUDIENCE" not in os.environ
    assert "JWT_DECODE_ISSUER" not in os.environ
