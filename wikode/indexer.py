
import sqlite3

from wikode.config import Config


class DatabaseFactory(object):
    """Provide interfaces to obtain connections to database."""

    CONNECTION = None

    @classmethod
    def get_connection(cls):
        """Create and return singleton connection to sqlite database."""
        if cls.CONNECTION is None:
            cls.CONNECTION = sqlite3.connect(Config.get(Config.KEYS.SQLITE_PATH))
        return cls.CONNECTION

    @classmethod
    def get_curosor(cls):
        """Return database cursor."""
        return cls.get_connection().cursor()


