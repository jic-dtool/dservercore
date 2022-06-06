"""dtool-lookup-server-search"""

from dtool_lookup_server_core.abc import SearchABC


__version__ = "0.1.0"


class Search(SearchABC):

    def search(self, query):
        return []