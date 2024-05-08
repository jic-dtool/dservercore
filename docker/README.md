# Docker

The folder `docker` contains example Docker configuration files that allow
running `dserver`.

## Development deployment

We provide a containerized development deployment of `dserver`.
The containers are run using [`docker compose`](https://docs.docker.com/compose/).
The `compose` environment sets up Postgres and Mongo databases and starts a
[Minio](https://min.io/) (S3-compatible) object store. The startup process
pushes two example datasets to the object store. Furthermore, an LDAP server
and an LDAP-backed token generator for the `dserver` are launched
to allow running other components, such as the `dtool-lookup-webapp`, that
depend on authentication by user credentials, against the local lookup server
deployment.

Build the `compose` environment with
```
docker compose -f docker/devel.yml build
```
and start it with
```
docker compose -f docker/devel.yml up
```
The lookup server is then available at `https://localhost:5000`.
A single user with the name `test-user` is already registered. To generate a
token for this user, run
```
docker compose -f docker/devel.yml exec dserver flask user token test-user
```

The LDAP allows authentication of this user with password `test-password`.

`docker/dtool.json` contains a sample dtool configuration for accessing lookup
server and token generator from localhost.

## Development dependencies deployment

Similar to the development setup above, but only provides all services the
lookup server depends on, not the lookup server itself. Useful for playing with
different plugin constellations.

To share keys between containerized token generator and the host environment,
keys are generated on a bind mount when launching the composition.
Prepare an empty folder `keys` within this directory (meaning at `docker/keys`
relative to the repository root) before launching any container composition.
Otherwise, `docker compose` will not launch.

Build the `compose` environment with
```
docker compose -f docker/env.yml build
```
and start it with
```
docker compose -f docker/env.yml up -d
```

Make keys generated at container launch readable by current user on host with

    sudo chown -R ${USER}:${USER} docker/keys

## Token

The container composition provides an LDAP server and a token generator service.
When running the services locally, generate a token with

```
curl --insecure -H "Content-Type: application/json" \
   -X POST -d '{"username": "test-user", "password": "test-password" }' \
   http://localhost:5001/token
```
