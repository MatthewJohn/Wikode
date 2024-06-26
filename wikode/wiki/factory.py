
import os
import glob

from flask import request, redirect

from wikode.base_page import BasePage
from wikode.config import Config
from wikode.wiki import Wiki, DefaultWikiPage, IndexPage
from wikode.scm import Factory as SCMFactory


class Factory(BasePage):

    @classmethod
    def get_wiki_object_from_url(cls, url_struct):
        if not url_struct:
            return DefaultWikiPage(cls)
        elif url_struct.lower() == 'index':
            return IndexPage(cls)
        return Wiki(cls, url_struct)

    @classmethod
    def get_wiki_object_from_file(cls, path):
        if path is None:
            path = ''
        url_struct = Wiki.filename_to_url_struct(Wiki.strip_relative_path(path))
        return Factory.get_wiki_object_from_url(url_struct)

    @staticmethod
    def serve_wiki_page(url_struct=None):

        wiki = Factory.get_wiki_object_from_url(url_struct)

        if wiki.is_reserved:
            return Factory.render_template('wiki_reserved.html', wiki=wiki)

        if request.args.get('edit', False):
            return Factory.render_template('wiki_edit.html', wiki=wiki)

        return Factory.render_template('wiki.html', wiki=wiki)

    @staticmethod
    def page_post(url_struct=None):

        wiki = Factory.get_wiki_object_from_url(url_struct)

        wiki_content = request.form.get('source', None)
        if wiki_content is not None:
            wiki.save(wiki_content)
            SCMFactory.get_scm().commit(wiki)

        return redirect(wiki.absolute_url, code=302)

    @staticmethod
    def reindex_all_files():
        for f in glob.glob(os.path.join(
                    Config.get(Config.KEYS.DATA_DIR),
                    '**/*' + Wiki.FILE_EXTENSION),
                recursive=True):
            wiki = Factory.get_wiki_object_from_file(f)
            wiki.index()
