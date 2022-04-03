
import sqlite3
import glob
import os

from flask import request, render_template

from wikode.indexer import Indexer
from wikode.wiki.factory import Factory as WikiFactory


class TagsPage(object):
    
    URL = '/tags'

    @staticmethod
    def list_tags_get():
        tags = Indexer().get_all_tags()

        return render_template(
            'tags.html', tags=tags)

    @staticmethod
    def tag_wikis_get(tag):
        res = [WikiFactory.get_wiki_object_from_url(row)
               for row in Indexer().wikis_by_tag(tag)]

        return render_template(
            'tag_results.html', results=res, tag=tag)
