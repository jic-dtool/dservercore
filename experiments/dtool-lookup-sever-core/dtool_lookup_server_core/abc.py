import abc


class AuthABC(abc.ABC):
    """Authentication abstract base class."""

    @abc.abstractmethod
    def has_admin_rights(self, username):
        pass


class SearchABC(abc.ABC):
    """Search abstract base class."""

    @abc.abstractmethod
    def search(self, query):
        pass