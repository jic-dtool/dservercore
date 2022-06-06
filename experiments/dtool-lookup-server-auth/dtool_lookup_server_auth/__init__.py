"""dtool-lookup-server-auth"""

from dtool_lookup_server_core.abc import AuthABC


__version__ = "0.1.0"


class Auth(AuthABC):

    def has_admin_rights(self, username):
        return False