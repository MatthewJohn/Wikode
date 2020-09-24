
import os
import glob

from flask import render_template, request, redirect

from wikode.config import Config
from wikode.scm import Factory as SCMFactory


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
            self._exists = os.path.exists(self.path)
        return self._exists

    @property
    def is_dir(self):
        return os.path.isdir(self.path)

    @property
    def absolute_url(self):
        return '/' + '/'.join(self.pages)

    @property
    def breadcrumb_html(self):
        html = ''
        url_path = ''

        for page in self.pages:
            url_path += '/{0}'.format(page)
            html += '/ <a href="{0}">{1}</a>'.format(url_path, page)
        return html

    def get_children(self):
        return glob.glob(self.path + '/*')

    @property
    def children_html(self):
        return '<ul>' + ''.join(['<li><a href="{0}/{1}"></a>{1}</li>'.format(self.path, fn) for fn in self.get_children()]) + '</ul>'

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

        if SCMFactory.get_scm().is_set():
            SCMFactory.get_scm().commit(wiki)

        return redirect(wiki.absolute_url, code=302)
