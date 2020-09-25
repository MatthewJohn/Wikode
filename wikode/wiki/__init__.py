
import os
import glob
import re
import random
import string

from flask import render_template, request, redirect

from wikode.config import Config
from wikode.scm import Factory as SCMFactory


class Wiki(object):

    FILE_EXTENSION = '.wikode'

    PLACEHOLDER_LETTERS = string.ascii_lowercase + string.ascii_uppercase
    PLACEHOLDER_LENGTH = 32

    RE_RELATIVE_PATH_PREFIX = re.compile(r'^\./', re.IGNORECASE)
    RE_DATA_PREFIX = re.compile(r'{0}'.format(re.escape(Config.get(Config.KEYS.DATA_DIR))))

    WIKI_RE__NEW_LINE = re.compile(r'\n')
    WIKI_RE__LINK_WIKI = re.compile(r'\[\[([a-zA-Z0-9_\-/\.]+)(?: ([^\]]+))?\]\]')
    WIKI_RE__LINK_EXTERNAL = re.compile(r'\[\[(https?\://[a-zA-Z0-9_\-/\.]+)(?: ([^\]]+))?\]\]')
    WIKI_RE__BOLD = re.compile(r'\*\*(.*?)\*\*')
    WIKI_RE__ITALICS = re.compile(r'__(.*?)__')
    WIKI_RE__DELETED = re.compile(r'~(.*?)~')
    WIKI_RE__PREFORMATTED = re.compile(r'\{\{\{(.+?)\}\}\}', re.DOTALL | re.MULTILINE)

    WIKI_RE__HEADER = re.compile(r'^(=+)([^\n]+?)( =+)?$', re.MULTILINE)

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
        html = '<a href="/">Wiki</a> :'
        url_path = ''

        for page in self.pages:
            url_path += '/{0}'.format(page)
            html += ' / <a href="{0}">{1}</a>'.format(url_path, page)
        return '<div id="breadcrumb">' + html + '</div>'

    @staticmethod
    def filename_to_url(path):
        return Wiki.RE_RELATIVE_PATH_PREFIX.sub(
            '',
            Wiki.RE_DATA_PREFIX.sub(
                '',
                path
            )
        )[:-len(Wiki.FILE_EXTENSION)]

    @property
    def children_files(self):
        if self._children_files is None:
            cs = glob.glob(self.dir_path + '/*{0}'.format(self.FILE_EXTENSION))
            self._children_files = [
                Wiki.filename_to_url(c)
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

        # PREFORMAT  - MUST BE BEFORE ANY OTHER REPLACEMENTS
        preformat_strings = {}
        def replace_preformat(m):
            random_value = (
                'WIKOD_PH_START_' +
                ''.join(
                    random.choice(Wiki.PLACEHOLDER_LETTERS)
                    for i in range(Wiki.PLACEHOLDER_LENGTH)
                ) +
                '_WIKOD_PH_END'
            )
            preformat_strings[random_value] = m.group(1)
            return random_value
        rendered = self.WIKI_RE__PREFORMATTED.sub(replace_preformat, rendered)

        def replace_link(m):
            return '<a href="{0}">{1}</a>'.format(m.group(1), m.group(2) if m.group(2) else m.group(1))
        rendered = self.WIKI_RE__LINK_WIKI.sub(replace_link, rendered)
        rendered = self.WIKI_RE__LINK_EXTERNAL.sub(replace_link, rendered)
        rendered = self.WIKI_RE__BOLD.sub(r'<b>\1</b>', rendered)
        rendered = self.WIKI_RE__ITALICS.sub(r'<i>\1</i>', rendered)
        rendered = self.WIKI_RE__DELETED.sub(r'<del>\1</del>', rendered)

        # FULL LINE REPLACEMENT - must be before NEW LINE REPLACEMENT
        def replace_header(m):
            header_size = len(m.group(1))
            return '<h{0}>{1}</h{0}>'.format(header_size, m.group(2))
        rendered = self.WIKI_RE__HEADER.sub(replace_header, rendered)


        # NEW LINE REPLACEMENT - MUST BE AFTER ALL MULTILINE REPLACENTS
        rendered = self.WIKI_RE__NEW_LINE.sub('<br />', rendered)


        # Re-add preformat placeholders - MUST BE AT END
        for preformat_placeholder in preformat_strings:
            rendered = rendered.replace(
                preformat_placeholder,
                '<pre>' + preformat_strings[preformat_placeholder] + '</pre>'
            )

        return rendered

    @property
    def is_reserved(self):
        return (os.path.isfile(self.dir_path) or
                '/.' in self.url_struct or
                '..' in self.url_struct or
                self.url_struct.startswith('.'))


class DefaultWikiPage(Wiki):

    DEFAULT_WIKI_NAME = 'index'

    def __init__(self):
        super(DefaultWikiPage, self).__init__(self.DEFAULT_WIKI_NAME)
        self.pages = []

    @property
    def file_path(self):
        return self.dir_path + self.DEFAULT_WIKI_NAME + self.FILE_EXTENSION


class Factory(object):

    @staticmethod
    def serve_wiki_page(url_struct=None):

        wiki = DefaultWikiPage() if url_struct is None else Wiki(url_struct)

        if wiki.is_reserved:
            return render_template('wiki_reserved.html', wiki=wiki)

        if request.args.get('edit', False):
            return render_template('wiki_edit.html', wiki=wiki)

        return render_template('wiki.html', wiki=wiki)

    @staticmethod
    def page_post(url_struct=None):

        wiki = DefaultWikiPage() if url_struct is None else Wiki(url_struct)

        wiki_content = request.form.get('source', None)
        if wiki_content is not None:
            wiki.save(wiki_content)

        SCMFactory.get_scm().commit(wiki)

        return redirect(wiki.absolute_url, code=302)
