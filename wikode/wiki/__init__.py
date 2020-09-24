
import os
from flask import render_template, request, redirect

from wikode.config import Config
from wikode.scm import SCM


class Wiki(object):

    FILE_EXTENSION = '.wikode'

    def __init__(self, url_struct):
        self.url_struct = url_struct
        self.pages = url_struct.split('/')
        self._source = None
        self._exists = None
        self._path = None

    @property
    def path(self):
        if self._path is None:
            self._path = os.path.join(Config.get(Config.KEYS.DATA_DIR), *self.pages)
        return self._path

    @property
    def exists(self):

        if self._exists is None:
            self._exists = os.path.isfile(self.path)
        return self._exists

    @property
    def absolute_url(self):
        return '/' + '/'.join(self.pages)

    def save(self, content):
        parent_path = Config.get(Config.KEYS.DATA_DIR)

        # Create parent directories
        for dir_name in self.pages[:-1]:
            parent_path = os.path.join(parent_path, dir_name)
            if not os.path.isdir(parent_path):
                os.mkdir(parent_path)

        # Write file
        with open(self.path, 'w') as fh:
            fh.write(content)

    @property
    def source(self):
        if self._source is None:
            if self.exists:
                with open(self.path, 'r') as fh:
                    self._source = fh.read()
            else:
                self._source = ''
        return self._source

    @property
    def rendered(self):
        return self.source

    @staticmethod
    def serve_wiki_page(url_struct):
        wiki = Wiki(url_struct)

        edit_mode = request.args.get('edit', False) or not wiki.exists
        if edit_mode:
            return render_template('wiki_edit.html', wiki=wiki)

        return render_template('wiki.html', wiki=wiki)

    @staticmethod
    def page_post(url_struct):
        wiki = Wiki(url_struct)
        wiki_content = request.form.get('source', None)
        if wiki_content is not None:
            wiki.save(wiki_content)

        if SCM.is_set():
            SCM.commit(wiki)

        return redirect(wiki.absolute_url, code=302)
