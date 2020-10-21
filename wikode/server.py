

from flask import Flask

from wikode.config import Config
from wikode.scm import Factory as SCMFactory
from wikode.wiki.factory import Factory as WikiFactory
from wikode.admin import Admin as AdminPage
from wikode.indexer import Indexer
from wikode.wiki.search import SearchPage


class Server(object):

    def __init__(self):
        """Create server object"""
        self._flask = Flask(__name__)

        self._register_flask_components()

    def run(self):
        if Indexer().initialise_database():
            WikiFactory.reindex_all_files()
        SCMFactory.initialise()
        self._flask.run(
            host=Config.get(Config.KEYS.LISTEN_HOST),
            port=Config.get(Config.KEYS.LISTEN_PORT)
        )

    def _register_flask_components(self):
        self._flask.route('/', methods=['GET'])(WikiFactory.serve_wiki_page)
        self._flask.route('/', methods=['POST'])(WikiFactory.page_post)

        self._flask.route(AdminPage.URL, methods=['GET'])(AdminPage.admin_get)
        self._flask.route(AdminPage.URL, methods=['POST'])(AdminPage.admin_post)

        self._flask.route(SearchPage.URL, methods=['POST'])(SearchPage.search_post)

        self._flask.route('/<path:url_struct>', methods=['GET'])(WikiFactory.serve_wiki_page)
        self._flask.route('/<path:url_struct>', methods=['POST'])(WikiFactory.page_post)
