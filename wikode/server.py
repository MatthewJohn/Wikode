

from flask import Flask

from wikode.config import Config
from wikode.scm import Factory as SCMFactory
from wikode.wiki import Factory as WikiFactory
from wikode.admin import Admin as AdminPage


class Server(object):

    def __init__(self):
        """Create server object"""
        self._flask = Flask(__name__)

        self._register_flask_components()

    def run(self):
        SCMFactory.initialise()
        self._flask.run(
            host=Config.get(Config.KEYS.LISTEN_HOST),
            port=Config.get(Config.KEYS.LISTEN_PORT)
        )

    def _register_flask_components(self):
        self._flask.route('/', methods=['GET'])(WikiFactory.serve_wiki_page)
        self._flask.route('/', methods=['POST'])(WikiFactory.page_post)

        self._flask.route(AdminPage.URL, methods=['GET', 'POST'])(AdminPage.serve_page)
        
        self._flask.route('/<path:url_struct>', methods=['GET'])(WikiFactory.serve_wiki_page)
        self._flask.route('/<path:url_struct>', methods=['POST'])(WikiFactory.page_post)
