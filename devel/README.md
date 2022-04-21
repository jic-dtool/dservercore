# Development environment

Simple development environment.


## Setup

`setup.sh` creates a Python virtual environment within the repository's root and installs requirements specified within `requirements.txt`.


## Start

`run.sh` starts a local dtool lookup server on port 5000. Expects valid `~/.config/dtool/dtool.json` or setup via environment variables.

## Token

`source export_token.sh` generates JWT token and exports $TOKEN and $HEADER environment variables for authentification. Run after starting server.

## Environement variables

`source env.rc` sets environment variables for flask. Use to manually issue commands like `flask run`.

## openapi-generator-cli

`openapi-generator-example.sh` contains a few examples on how to use openapi-generator-cli with the dtool-lookup-server.
Different Python API generators exist. Only `python-legacy` is able to generate `asyncio`-based API. 
Running `openapi-generator-cli` will produce two auto-generated Python packages, `out/python` and `out/python-legacy`,
former `urllib3`-based, latter `asyncio`-based.

The `python*client-config.yml` files configure Python-specific behavior for openapi-generator-cli.

Use 

    export GIT_TOKEN=xyz
    cd out/python-legacy
    bash git_push.sh

to push the generated API to a remote repository if in possession of a valid token.
