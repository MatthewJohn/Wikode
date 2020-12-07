
import sqlite3
import glob
import os

from flask import request, render_template

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
    def sql_connect(cls):
        return sqlite3.connect(Config.get(Config.KEYS.SQLITE_PATH))

    @classmethod
    def get_cursor(cls):
        """Return database cursor."""
        return cls.get_connection().cursor()


class Indexer(object):

    TABLE_NAME = 'wiki'

    def initialise_database(self):
        with DatabaseFactory.sql_connect() as db:
            c = db.cursor()
            r = c.execute(
                """
                SELECT name FROM sqlite_master WHERE type='table' AND name=?;
                """,
                (Indexer.TABLE_NAME,)
            )
            if not len(r.fetchall()):
                c.execute("""
                    CREATE VIRTUAL TABLE wiki
                    USING FTS5(url, file, content);
                """)
                return True
        return False

    def search(self, search_string):
        """Perform search for wiki pages based on given search string."""
        # Replace dashes, as sqlite requires alphanumeric characters
        # for parameters (although underscores and other characters appear to work)
        # as per https://stackoverflow.com/a/28195529
        search_string = search_string.replace('-', ' ')

        with DatabaseFactory.sql_connect() as db:
            c = db.cursor()
            r = c.execute(
                """SELECT url FROM wiki WHERE wiki MATCH ?""",
                (search_string,)).fetchall()
            return [i[0] for i in r]

    @staticmethod
    def index_file(wiki):
        print('Indexing file: {0}'.format(wiki.url_struct))
        with DatabaseFactory.sql_connect() as db:
            c = db.cursor()
            c.execute("""DELETE FROM wiki WHERE file= ?""", (wiki.file_path,))
            c.execute(
                """INSERT INTO wiki(file, url, content) VALUES(?, ?, ?)""",
                (wiki.file_path, wiki.url_struct, wiki.rendered.replace('-', ' ')))
            db.commit()
