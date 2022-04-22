# works with https://github.com/jotelha/aiopenapi3/tree/auto-generation-of-operation-ids-and-authorization-via-jwt
import os
import asyncio

from aiopenapi3 import OpenAPI
from pprint import pprint

token = os.getenv("DTOOL_LOOKUP_SERVER_TOKEN")
host = os.getenv("DTOOL_LOOKUP_SERVER_URL", "http://localhost:5000")

url = f"{host}/doc/openapi.json"

async def main():
    api = await OpenAPI.load_async(url)

    class Server:
        def __init__(self, url):
            self.url = url

    server = Server(host)
    api._root.servers.append(server)
    api.authenticate(bearerAuth=token)
    ret = await api._._config_info_get()

    print(type(ret))


asyncio.run(main())
