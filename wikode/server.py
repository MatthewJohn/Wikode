

from flask import Flask
from wikode.scm import SCM
from wikode.wiki import Wiki


class Server(object):

    def __init__(self, host, port):
        """Create server object"""
        self._flask = Flask(__name__)
        self._host = host
        self._port = port

        self._register_flask_components()

    def run(self):
        SCM.Initialise()
        self._flask.run(self._host, self._port)

    def _register_flask_components(self):
        self._flask.route('/<path:url_struct>')(Wiki.serve_wiki_page)

