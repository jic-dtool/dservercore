# Docker

This folder contains example Docker configuration files that allow running `dtool-lookup-server`.

## Development

We provide a containerized development deployment of `dtool-lookup-server`.
The containers are run using [`docker compose`](https://docs.docker.com/compose/).
The compose environment sets up Postgres and Mongo databases and starts a
[Minio](https://min.io/) (S3-compatible) object store. The startup process
pushes two example datasets to the object store. Furthermore, an LDAP server
and an LDAP-backed token generator for the `dtool-lookup-server` are launched
to allow running other components, such as the `dtool-lookup-webapp`, that
depend authentication by user credentials, against the local lookup server
deployment.

Build the compose environment with
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
docker compose -f docker/devel.yml exec dtool_lookup_server flask user token test-user
```

The LDAP allows authentification of this user with password `test-password`.

`docker/dtool.json` contains a sample dtool configuration for accessing lookup
server and token generator from localhost.

## Development dependencies

Similar to the development setup, but only provides all services the lookup
server depends on, not the lookup server itsels. Useful for playing with
different plugin constellations.

Build the compose environment with
```
docker compose -f docker/env.yml build
```
and start it with
```
docker compose -f docker/env.yml up
```
