from collections import namedtuple

import mistune

from mywiki.domain.event import DomainEvent, DomainEventSubscriber
from mywiki.domain.model.edit.article import Article as Markdown

Article = namedtuple('Article', ('id', 'category', 'title', 'html', 'revision'))


class ArticleRepository(object):
    def put(self, article: Article):
        raise NotImplementedError

    def get(self, article_id: str, revision: int) -> Article:
        raise NotImplementedError

    def delete(self, article_id: str, revision: int):
        raise NotImplementedError

    def list(self) -> [Article]:
        raise NotImplementedError


class ArticleConverter(DomainEventSubscriber):
    def __init__(self, repository: ArticleRepository):
        self._repository = repository

    def handle_event(self, event: DomainEvent):
        article_id = event.generator_id
        revision = event.sequence_number
        if isinstance(event, Markdown.Issued):
            article = self._repository.get(article_id, revision)
            if article:
                return  # skip, already handled
            assert event.content_type == 'text/markdown; charset=UTF-8'
            md = event.content
            html = mistune.markdown(md)
            article = Article(article_id, event.category, event.title, html, revision)
            self._repository.put(article)
        elif isinstance(event, Markdown.Discarded):
            self._repository.delete(article_id, revision)


class Viewer(object):
    def __init__(self, user_id):
        self.user_id = user_id

    @staticmethod
    def view(article_repository: ArticleRepository, article_id: str, revision: int) -> Article:
        article = article_repository.get(article_id, revision)
        return article


class ViewerRepository(object):
    @staticmethod
    def find(user_id: str) -> Viewer:
        return Viewer(user_id)
