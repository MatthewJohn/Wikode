
import sqlite3
import glob
import os

from flask import request, render_template

from wikode.indexer import Indexer
from wikode.wiki.factory import Factory as WikiFactory


class TagsPage(object):
    
    URL = '/tags'

    @staticmethod
    def tags_list_get():
        tags = Indexer().get_all_tags()

        return render_template(
            'tags.html', tags=tags)
