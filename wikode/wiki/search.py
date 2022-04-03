
import sqlite3
import glob
import os

from flask import request

from wikode.base_page import BasePage
from wikode.indexer import Indexer
from wikode.wiki.factory import Factory as WikiFactory


class SearchPage(BasePage):
    
    URL = '/search'

    @staticmethod
    def search_post():
        search_string = request.form.get('search_string', '')

        # If no search string required, don't perform search
        # and return no results
        if not search_string:
            res = []
        else:
            res = [WikiFactory.get_wiki_object_from_url(row)
                   for row in Indexer().search(search_string)]

        return SearchPage.render_template(
            'search.html', results=res, search_query=search_string)
