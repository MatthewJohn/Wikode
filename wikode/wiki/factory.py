
from flask import render_template, request, redirect

from wikode.wiki import Wiki, DefaultWikiPage
from wikode.scm import Factory as SCMFactory


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
