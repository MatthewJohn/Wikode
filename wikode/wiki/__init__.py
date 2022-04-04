
import os
import glob
import re
import random
import string

from wikode.config import Config
from wikode.indexer import Indexer


class Wiki(object):

    FILE_EXTENSION = '.wikode'

    CAN_EDIT = True
    SHOW_WIKI = True

    PLACEHOLDER_LETTERS = string.ascii_lowercase + string.ascii_uppercase
    PLACEHOLDER_LENGTH = 32

    RE_RELATIVE_PATH_PREFIX = re.compile(r'^\.?/', re.IGNORECASE)
    RE_DATA_PREFIX = re.compile(
        r'{0}'.format(re.escape(Config.get(Config.KEYS.DATA_DIR))))

    WIKI_RE__NEW_LINE = re.compile(r'\n')
    WIKI_RE__LINK_WIKI = re.compile(r'\[([a-zA-Z0-9_\-/\.]+)(?: ([^\]]+))?\]')
    WIKI_RE__LINK_EXTERNAL = re.compile(r'\[(https?\://[a-zA-Z0-9_\-/\.]+)(?: ([^\]]+))?\]')
    WIKI_RE__BOLD = re.compile(r'\*\*(.*?)\*\*')
    WIKI_RE__ITALICS = re.compile(r'__(.*?)__')
    WIKI_RE__DELETED = re.compile(r'~(.*?)~')
    WIKI_RE__PREFORMATTED = re.compile(r'\{\{\{(.+?)\}\}\}',
                                       re.DOTALL | re.MULTILINE)
    WIKI_RE__BULLET = re.compile(
        r'((?:^ *\*+ [^\n]+$\n)+)',
        re.DOTALL | re.MULTILINE)

    WIKI_RE__LIST = re.compile(
        r'((?:^ *1\. [^\n]+$\n)+)',
        re.DOTALL | re.MULTILINE)

    WIKI_RE__MACRO = re.compile(r'\[\[([A-Za-z]+)\(([^\)]*)\)\]\]')

    WIKI_RE__HEADER = re.compile(r'^(=+)([^\n]+?)( =+)?$', re.MULTILINE)
    WIKI_RE__MD_HEADER = re.compile(r'^(#+)([^\n]+?)( #+)?$', re.MULTILINE)

    def __init__(self, factory, url_struct):
        self._factory = factory
        # Remove trailing slashes from LHS of URL
        self.url_struct = re.sub('/+', '/', url_struct.strip('/'))

        self.pages = self.url_struct.split('/')
        self._source = None
        self._exists = None
        self._dir_path = None
        self._children_wiki = None
        self._created = False
        self._tags = []

    @property
    def name(self):
        return self.url_struct[-1]

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
    def strip_relative_path(path):
        """Strip ./ from path"""
        return Wiki.RE_RELATIVE_PATH_PREFIX.sub(
            '',
            Wiki.RE_DATA_PREFIX.sub(
                '',
                path
            )
        )

    @staticmethod
    def filename_to_url_struct(path):
        if path.endswith(Wiki.FILE_EXTENSION):
            path = path[:-len(Wiki.FILE_EXTENSION)]

        # Check if index
        if path == 'index':
            path = ''

        return path

    @property
    def children_files(self):
        return glob.glob(self.dir_path + '/*')

    @property
    def child_wikis(self):
        if self._children_wiki is None:
            # List all files in dir
            cs = self.children_files
            url_list = []
            for c in cs:
                c = Wiki.strip_relative_path(c)
                # Remove file if not a directory or doesn't a valid
                # wiki extension.
                if not c.endswith(Wiki.FILE_EXTENSION) and os.path.isdir(c):
                    continue

                # Convert file path to URL
                url = Wiki.filename_to_url_struct(c)

                # Skip, if self
                if url == self.url_struct:
                    continue

                # If not already in the list, add it
                if url not in url_list:
                    url_list.append(url)

            # Sort list of children
            self._child_wikis = [Wiki(self._factory, url) for url in sorted(url_list)]

        return self._child_wikis

    @property
    def has_children(self):
        return len(self.child_wikis)

    @property
    def children_html(self):
        return '<ul>' + ''.join(['<li><a href="{0}">{0}</a></li>'.format(fn.absolute_url) for fn in self.child_wikis]) + '</ul>'

    @property
    def tags(self):
        """Return list of tags for wiki"""
        # Return deduplicated list
        return list(dict.fromkeys(self._tags))

    def save(self, content):
        parent_path = Config.get(Config.KEYS.DATA_DIR)

        # Create parent directories
        for dir_name in self.pages[:-1]:
            parent_path = os.path.join(parent_path, dir_name)
            if not os.path.isdir(parent_path):
                os.mkdir(parent_path)

        # If file did not previously exist, mark that
        # the file has been created
        if not self.exists:
            self._created = True

        # Write file
        with open(self.file_path, 'w') as fh:
            fh.write(content)

        # Re-index file
        self.index()

    @property
    def created(self):
        return self._created

    def index(self):
        """Add/re-add file to search index."""
        # Render template before indexing
        self.rendered
        Indexer.index_file(self)

    @property
    def source(self):
        if self._source is None:
            if self.exists:
                with open(self.file_path, 'r') as fh:
                    self._source = fh.read()
            else:
                self._source = ''
        return self._source

    @staticmethod
    def generate_placeholder():
        return (
            ''.join(
                random.choice(Wiki.PLACEHOLDER_LETTERS)
                for i in range(Wiki.PLACEHOLDER_LENGTH)
            )
        )

    @staticmethod
    def escaspe_html_characters(input):
        """Replace HTML interpreted chracters with entities."""
        # Replace all entities, starting with &, as this will be used in all replacements.
        for replacements in [('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;'), ('\'', '&#39;'), ('"', '&#34;')]:
            input = input.replace(replacements[0], replacements[1])
        return input

    @property
    def rendered(self):
        rendered = self.source

        # Clear tags
        self._tags = []

        # PREFORMAT  - MUST BE BEFORE ANY OTHER REPLACEMENTS
        preformat_strings = {}
        def replace_preformat(m):
            random_value = self.generate_placeholder()
            preformatted_value = m.group(1)
            preformat_strings[random_value] = self.escaspe_html_characters(m.group(1))
            return random_value
        rendered = self.WIKI_RE__PREFORMATTED.sub(replace_preformat, rendered)

        # MACROS - MUST BE BEFORE LINK
        def process_macro(m):

            macro_name = m.group(1)
            if macro_name == 'Tags':
                self._tags += [t.strip() for t in m.group(2).split(',')]
                # Remove entire macro
                return ''
            else:
                return '[Unknown macro: {0}]'.format(macro_name)

        rendered = self.WIKI_RE__MACRO.sub(process_macro, rendered)

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
        rendered = self.WIKI_RE__MD_HEADER.sub(replace_header, rendered)

        def count_bullets(line, current_level):
            points = re.match(r'^([\s\*]+)', line)

            new_level = 0
            if points:
                new_level = points.group(0).count('*')

            if new_level > current_level:
                return ['<ul>' * (new_level - current_level)], new_level
            elif new_level < current_level:
                return ['</ul>' * (current_level - new_level)], new_level

            return [], current_level

        def replace_bullet(m):
            lines = []
            current_level = 0
            # Iterate through lines
            for line in m.group(1).split('\n'):
                new_lines, current_level = count_bullets(line, current_level)
                lines += new_lines
                line = re.sub(r'^\s*\*+', '<li>', line)
                line = re.sub(r'$', '</li>', line)
                lines.append(line)

            new_lines, current_level = count_bullets('', current_level)
            lines += new_lines

            return ''.join(lines)

        rendered = self.WIKI_RE__BULLET.sub(replace_bullet, rendered)

        def replace_list(m):
            lines = []
            for line in m.group(1).split('\n'):
                line = re.sub(r'^\s*1\.', '<li>', line)
                line = re.sub(r'$', '</li>', line)
                lines.append(line)

            return '<ol>' + ''.join(lines) + '</ol>'
        rendered = self.WIKI_RE__LIST.sub(replace_list, rendered)

        # Replace pipes with placeholders
        pipe_placeholder = self.generate_placeholder()
        rendered = rendered.replace('||', pipe_placeholder)
        def replace_table(m):
            lines = []
            for line in m.group(1).replace(pipe_placeholder, '||').split('\n'):
                cols = []
                for col in line.split('||')[1:-1]:
                    cols.append('<td>' + col + '</td>')
                lines.append('<tr>' + ''.join(cols) + '</tr>')

            return '<table>' + ''.join(lines) + '</table>'
        wiki_match = re.compile(r'((?:^' + re.escape(pipe_placeholder) + r'.+$\n)+)', re.MULTILINE)
        rendered = wiki_match.sub(replace_table, rendered)

        # NEW LINE REPLACEMENT - MUST BE AFTER ALL MULTILINE REPLACENTS
        rendered = self.WIKI_RE__NEW_LINE.sub('<br />\n', rendered)

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
                self.url_struct.startswith('.') or
                self.url_struct == 'search')


class DefaultWikiPage(Wiki):

    DEFAULT_WIKI_NAME = 'index'

    def __init__(self, factory):
        super(DefaultWikiPage, self).__init__(factory, self.DEFAULT_WIKI_NAME)
        self.pages = []
        self.url_struct = ''

    @property
    def name(self):
        return 'index'

    @property
    def file_path(self):
        return os.path.join(self.dir_path, self.DEFAULT_WIKI_NAME + self.FILE_EXTENSION)


class IndexPage(Wiki):

    INDEX_PAGE_NAME = 'Index'
    CAN_EDIT = False
    SHOW_WIKI = False

    def __init__(self, factory):
        super(IndexPage, self).__init__(factory, self.INDEX_PAGE_NAME)
        self.pages = []

    def save(self):
        raise NotImplementedError

    @property
    def children_files(self):
        """Return list of children files."""
        return glob.glob(self.dir_path + '/*') + glob.glob(self.dir_path + '/**/*')

    @property
    def child_wikis(self):
        return list(filter(lambda x: x.exists, super(IndexPage, self).child_wikis))
