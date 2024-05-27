"""Create dserver wsgi debug app.

Environment variable

  - DUMP_HTTP_REQUESTS=True
      dumps all http requests.
  - LOGLEVEL=DEBUG
      dumps all debug messages
"""
import logging
import os
import pprint
from dtool_lookup_server import create_app


LOGLEVELS_STR = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
LOGLEVELS_INT = [getattr(logging, level) for level in LOGLEVELS_STR]

loglevel = os.getenv("LOGLEVEL", 'ERROR').upper()
if loglevel in LOGLEVELS_STR:
    print(f"Select loglevel by keyword {loglevel}.")
    loglevel = getattr(logging, loglevel)
elif int(loglevel) in LOGLEVELS_INT:
    print(f"Select loglevel by value {loglevel}.")
    loglevel = int(loglevel)
else:
    print(f"Select default loglevel.")
    loglevel = None

if loglevel is not None:
    print(f"Set loglevel={loglevel}.")
    logging.basicConfig(level=loglevel)
    logger = logging.getLogger()
    logger.setLevel(loglevel) # modify root logger as well in case it's been set up already elsewhere

app = create_app()

# wrap logging middleware if DUMP_HTTP_REQUESTS set true
if os.getenv("DUMP_HTTP_REQUESTS", 'False').lower() in ('true', '1', 't'):
    class LoggingMiddleware:
        """Wrap wsgi app and dump all requests."""

        def __init__(self, app):
            self._app = app

        def __call__(self, env, resp):
            errorlog = env['wsgi.errors']
            pprint.pprint(('REQUEST', env), stream=errorlog)

            def log_response(status, headers, *args):
                pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
                return resp(status, headers, *args)
            return self._app(env, log_response)
    app = LoggingMiddleware(app)
