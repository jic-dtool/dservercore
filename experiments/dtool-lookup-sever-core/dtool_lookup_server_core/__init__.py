"""dtool-lookup-server-core"""

import abc

__version__ = "0.1.0"


class AuthABC(abc.ABC):
    """Authentication abstract base class."""

    @abc.abstractmethod
    def has_admin_rights(self, username):
        pass