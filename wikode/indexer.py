
import sqlite3
import glob
from flask import request, render_template

from wikode.config import Config
from wikode.wiki import Wiki


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
    def get_cursor(cls):
        """Return database cursor."""
        return cls.get_connection().cursor()


class Indexer(object):

    TABLE_NAME = 'wikis'

    def initialise_database(self):
        c = DatabaseFactory.get_cursor().execute(
            """
            SELECT name FROM sqlite_master WHERE type='table' AND name=?;
            """,
            (Indexer.TABLE_NAME,)
        )
        if not c.rowcount:
            DatabaseFactory.get_cursor().execute("""
                CREATE VIRTUAL TABLE wiki
                USING FTS5(url, file, content);
            """)

    def search(self, search_string):
        r = DatabaseFactory.get_cursor().execute(
            """SELECT url FROM wiki WHERE wiki MATCH ?""",
            (search_string,))
        return [i['url'] for i in r]

    def index_file(self, wiki):
        c = DatabaseFactory.get_cursor()
        c.execute("""DELETE FROM wiki WHERE file= ?""", (wiki.file_path,))
        c.execute(
            """INSERT INTO wiki(file, url, content) VALUES(?, ?, ?)""",
            (wiki.file_path, wiki.url_struct, wiki.rendered))
        c.commit()

    def reindex_all_files(self):
        for f in glob.glob(
                Config.get(Config.KEYS.DATA_DIR),
                '**/*' + Wiki.FILE_EXTENSION, recursive=True):
            wiki = Wiki(Wiki.filename_to_url(f))
            self.index_file(wiki)


class SearchPage(object):
    
    URL = '/search'

    @staticmethod
    def search_post():
        search_string = request.form.get('search_string', '')
        res = Indexer().search(search_string)
        return render_template('search.html', results=res)
