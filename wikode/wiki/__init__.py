
import os
import glob
import re

from flask import render_template, request, redirect

from wikode.config import Config
from wikode.scm import Factory as SCMFactory


class Wiki(object):

    FILE_EXTENSION = '.wikode'
    RE_RELATIVE_PATH_PREFIX = re.compile(r"^\./", re.IGNORECASE)
    RE_DATA_PREFIX = re.compile(r"{0}".format(re.escape(Config.get(Config.KEYS.DATA_DIR))))

    WIKI_RE__NEW_LINE = re.compile(r'\n')
    WIKI_RE__LINK_WIKI = re.compile(r'\{\{\s+([a-zA-Z0-9_\-/]+)\s+\}\}')

    def __init__(self, url_struct):
        self.url_struct = url_struct
        self.pages = url_struct.split('/')
        self._source = None
        self._exists = None
        self._dir_path = None
        self._children_files = None

    @property
    def dir_path(self):
        if self._dir_path is None:
            self._dir_path = os.path.join(Config.get(Config.KEYS.DATA_DIR), *self.pages)
        return self._dir_path

    @property
    def file_path(self):
        return self.dir_path + self.FILE_EXTENSION

    @property
    def exists(self):
        if self._exists is None:
            self._exists = os.path.exists(self.file_path)
        return self._exists

    @property
    def absolute_url(self):
        return '/' + '/'.join(self.pages)

    @property
    def edit_button_text(self):
        return 'Edit' if self.exists else 'Create'

    @property
    def breadcrumb_html(self):
        html = ''
        url_path = ''

        for page in self.pages:
            url_path += '/{0}'.format(page)
            html += '/ <a href="{0}">{1}</a>'.format(url_path, page)
        return html

    @property
    def children_files(self):
        if self._children_files is None:
            cs = glob.glob(self.dir_path + '/*{0}'.format(self.FILE_EXTENSION))
            self._children_files = [
                self.RE_RELATIVE_PATH_PREFIX.sub(
                    '',
                    self.RE_DATA_PREFIX.sub(
                        '',
                        c
                    )
                )[:-len(self.FILE_EXTENSION)]
                for c in glob.glob(self.dir_path + '/*{0}'.format(self.FILE_EXTENSION))
            ]
        return self._children_files

    @property
    def has_children(self):
        return len(self.children_files)

    @property
    def children_html(self):
        return '<ul>' + ''.join(['<li><a href="{0}">{0}</a></li>'.format(fn) for fn in self.children_files]) + '</ul>'

    def save(self, content):
        parent_path = Config.get(Config.KEYS.DATA_DIR)

        # Create parent directories
        for dir_name in self.pages[:-1]:
            parent_path = os.path.join(parent_path, dir_name)
            if not os.path.isdir(parent_path):
                os.mkdir(parent_path)

        # Write file
        with open(self.file_path, 'w') as fh:
            fh.write(content)

    @property
    def source(self):
        if self._source is None:
            if self.exists:
                with open(self.file_path, 'r') as fh:
                    self._source = fh.read()
            else:
                self._source = ''
        return self._source

    @property
    def rendered(self):
        rendered = self.source
        rendered = self.WIKI_RE__NEW_LINE.sub('<br />', rendered)
        rendered = self.WIKI_RE__LINK_WIKI.sub(r'<a href="\1">\1</a>', rendered)
        return rendered

    @property
    def is_reserved(self):
        return os.path.isfile(self.dir_path) or '/.' in self.url_struct or '..' in self.url_struct

    @staticmethod
    def serve_wiki_page(url_struct):
        wiki = Wiki(url_struct)

        if wiki.is_reserved:
            return render_template('wiki_reserved.html', wiki=wiki)

        if request.args.get('edit', False):
            return render_template('wiki_edit.html', wiki=wiki)

        return render_template('wiki.html', wiki=wiki)

    @staticmethod
    def page_post(url_struct):
        wiki = Wiki(url_struct)
        wiki_content = request.form.get('source', None)
        if wiki_content is not None:
            wiki.save(wiki_content)

        SCMFactory.get_scm().commit(wiki)

        return redirect(wiki.absolute_url, code=302)
