
import os
import glob

from flask import render_template, request, redirect

from wikode.config import Config
from wikode.wiki import Wiki, DefaultWikiPage, IndexPage
from wikode.scm import Factory as SCMFactory


class Factory(object):

    @classmethod
    def get_wiki_object_from_url(cls, url_struct):
        if url_struct is None:
            return DefaultWikiPage(cls)
        elif url_struct.lower() == 'index':
            return IndexPage(cls)
        return Wiki(cls, url_struct)

    @classmethod
    def get_wiki_object_from_file(cls, path):
        url_struct = Wiki.strip_relative_path(path)
        if path is None or url_struct == '':
            return DefaultWikiPage()
        elif url_struct.lower() == 'index':
            return IndexPage()
        return Wiki(cls, url_struct)


    @staticmethod
    def serve_wiki_page(url_struct=None):

        wiki = Factory.get_wiki_object_from_url(url_struct)

        if wiki.is_reserved:
            return render_template('wiki_reserved.html', wiki=wiki)

        if request.args.get('edit', False):
            return render_template('wiki_edit.html', wiki=wiki)

        return render_template('wiki.html', wiki=wiki)

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
            wiki = self.get_wiki_object_from_file(f)
            wiki.index()
