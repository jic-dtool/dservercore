# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

`dservercore` is the core Flask application for `dserver`, a web API for registering, looking up, and searching dtool dataset metadata. It provides a pluggable framework where the actual storage and search backends are delegated to separately-installed plugins.

## Commands

**Install for development:**
```bash
pip install -e ".[test]"
```

**Run tests** (requires a running MongoDB on localhost:27017):
```bash
pytest -sv
```

If MongoDB requires authentication, pass credentials via `MONGO_URI`:
```bash
MONGO_URI="mongodb://user:password@localhost:27017/" pytest -sv
```

**Run a single test file:**
```bash
pytest -sv tests/test_uri_routes.py
```

**Run a single test:**
```bash
pytest -sv tests/test_uri_routes.py::test_name
```

**Lint:**
```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

**Run the app locally:**
```bash
export FLASK_APP=dservercore
flask run
```

**DB migrations** (after changing SQL models):
```bash
flask db init
flask db migrate
flask db upgrade
```

## Architecture

### Plugin system

`dservercore` does not store or search dataset descriptive content itself — that is fully delegated to two required plugins and any number of optional extension plugins, discovered at runtime via Python entry points:

- **`dservercore.search`** — exactly one search plugin must be installed (e.g. `dserver-search-plugin-mongo`). Must subclass `SearchABC` and implement `search()` and `register_dataset()`.
- **`dservercore.retrieve`** — exactly one retrieve plugin must be installed (e.g. `dserver-retrieve-plugin-mongo`). Must subclass `RetrieveABC` and implement `get_readme()`, `get_manifest()`, `get_annotations()`, `get_tags()`.
- **`dservercore.extension`** — zero or more optional extensions, subclassing `ExtensionABC`. Must implement `get_blueprint()` and `register_dataset()`.

All plugin ABCs are defined in `dservercore/__init__.py`. Plugins are loaded in `create_app()` and attached to the Flask `app` object as `app.search`, `app.retrieve`, and `app.custom_extensions`. Routes access them via `current_app.search` / `current_app.retrieve`.

### Dual data stores

Dataset metadata is stored in two places simultaneously:

1. **SQL database** (SQLAlchemy, default SQLite) — stores admin metadata (URI, UUID, name, creator, timestamps, size). Models: `User`, `BaseURI`, `Dataset` in `sql_models.py`. This is the authoritative source for listing datasets and permission checks.
2. **Plugin backends** — the search and retrieve plugins each maintain their own store (e.g. MongoDB) for full descriptive metadata (readme, manifest, annotations, tags).

`register_dataset()` in `utils.py` writes to both. The SQL side is the source for `list_datasets_by_user()` (no query) while the search plugin is used for `search_datasets_by_user()` (with query).

### Authorization model

- **JWT authentication** (RS256, asymmetric key) via `flask-jwt-extended`. The identity extracted from the token is the username.
- `utils_auth.py` provides `jwt_required()` and `get_jwt_identity()` wrappers that can be disabled for testing via `DISABLE_JWT_AUTHORISATION=True` config flag (returns `DEFAULT_USER` instead).
- Permissions are stored in SQL: users have `search_permissions` and `register_permissions` on specific `BaseURI` entries (many-to-many via association tables in `sql_models.py`).
- Admins (`is_admin=True`) bypass base URI permission checks in admin-only routes.

### Routes

Each resource has its own route module (`*_routes.py`) registering a `flask-smorest` Blueprint. All blueprints use the custom `dservercore.blueprint.Blueprint` (which is `FlaskSmorestBlueprint + SortMixin`) to support the `?sort=+field,-other` query parameter convention. Blueprints are registered in `create_app()`.

Route modules:
- `uri_routes.py` — `GET/POST/PUT/DELETE /uris/` for dataset search, registration, and deletion
- `uuid_routes.py` — `GET /uuids/<uuid>` to look up all URIs for a UUID
- `base_uri_routes.py` — admin management of base URIs
- `user_routes.py` — admin management of users and permissions
- `me_routes.py` — self-service route for the authenticated user
- `manifest_routes.py`, `readme_routes.py`, `annotations_routes.py`, `tags_routes.py` — retrieve plugin pass-through routes

### URI encoding in URL paths

Dataset URIs contain `://` which cannot appear directly in URL paths. `utils.py` provides `url_suffix_to_uri()` and `uri_to_url_suffix()` to convert between `s3://bucket/uuid` and the URL-safe form `s3/bucket/uuid` used in route paths like `GET /uris/s3/bucket/uuid`.

### Sorting

`sort.py` implements a custom sort feature on top of `flask-smorest`. Sort parameters are passed as `?sort=+field,-other` (comma-separated, `+`/`-` prefix for direction). `SortMixin` and the custom `Blueprint` class inject a `sort_parameters: SortParameters` kwarg into route handlers and add an `X-Sort` response header. `_dataset_order_by_args()` in `utils.py` translates `SortParameters` to SQLAlchemy `order_by` args.

### Testing

Tests require a real MongoDB instance on `localhost:27017` (no mocking). The `conftest.py` creates temporary MongoDB databases with randomised names and tears them down after each test. The main fixtures are:
- `tmp_app` — bare app, no users
- `tmp_app_with_users` — app with a pre-registered set of users and permissions
- `tmp_app_with_data` — app with users, base URIs, and dataset entries registered
- `tmp_cli_runner` — Flask test CLI runner

Pre-signed JWT tokens for test users (`snow-white`, `grumpy`, `dopey`, `sleepy`, `noone`) are hardcoded in `conftest.py` and validated against a hardcoded RSA public key.

## Key configuration variables

| Variable | Purpose |
|---|---|
| `FLASK_APP` | Must be set to `dservercore` |
| `SQLALCHEMY_DATABASE_URI` | SQL backend (default: SQLite `app.db`) |
| `JWT_PUBLIC_KEY` / `JWT_PUBLIC_KEY_FILE` | RSA public key for token verification |
| `JWT_PRIVATE_KEY_FILE` | RSA private key (only needed to issue tokens) |
| `DISABLE_JWT_AUTHORISATION` | Bypass auth for dev/testing |
| `DEFAULT_USER` | Username used when JWT auth is disabled |
| `OPENAPI_URL_PREFIX` | Path prefix for OpenAPI docs (default `/doc`) |
