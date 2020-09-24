
import os
from flask import render_template, request

from wikode.config import Config


class Wiki(object):

    @staticmethod
    def get_path(split_page):
        return os.path.join(Config.get(Config.KEYS.DATA_DIR), *split_page)

    @staticmethod
    def page_exists(split_page):
        os.path.isfile(Wiki.get_path(split_page))




    @staticmethod
    def serve_wiki_page(url_struct):
        pages = url_struct.split('/')
        exists = Wiki.page_exists(pages)
        edit_mode = request.args.get('edit', False) or not exists
        if edit_mode:
            return render_template('wiki_edit.html', exists=exists, pages=pages, post_path=url_struct)

        return render_template('wiki.html', exists=exists, pages=pages, edit_path=url_struct)