
from wikode.base_page import BasePage
from wikode.indexer import Indexer
from wikode.wiki.factory import Factory as WikiFactory


class TagsPage(BasePage):
    
    URL = '/tags'

    @staticmethod
    def list_tags_get():
        tags = Indexer().get_all_tags()

        return TagsPage.render_template(
            'tags.html', tags=tags)

    @staticmethod
    def tag_wikis_get(tag):
        res = [WikiFactory.get_wiki_object_from_url(row)
               for row in Indexer().wikis_by_tag(tag)]

        return TagsPage.render_template(
            'tag_results.html', results=res, tag=tag)
