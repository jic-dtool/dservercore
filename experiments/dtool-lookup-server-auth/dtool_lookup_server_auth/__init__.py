"""dtool-lookup-server-auth"""

import dtool_lookup_server_core as dls_core


__version__ = "0.1.0"


class Auth(dls_core.AuthABC):

    def has_admin_rights(self, username):
        return False