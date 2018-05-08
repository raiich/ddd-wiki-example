import uuid

from mywiki.domain.event import DomainEvent, EventStore, EventStoreConcurrencyException


class Article(object):
    # TODO divide into Issued / CategoryChanged / ..
    class Issued(DomainEvent):
        def __init__(self, article_id, category, title, content, editor_id, revision,
                     content_type='text/markdown; charset=UTF-8', occurred_on=None, sequence=None):
            super().__init__(article_id, revision, occurred_on)
            self.category = category
            self.title = title
            self.content = content
            self.editor_id = editor_id
            self.content_type = content_type
            self.sequence = sequence

    class Discarded(DomainEvent):
        def __init__(self, article_id, editor_id, revision, occurred_on=None,
                     sequence=None):
            super().__init__(article_id, revision, occurred_on)
            self.editor_id = editor_id
            self.occurred_on = occurred_on
            self.sequence = sequence

    @classmethod
    def create(cls, article_id: str, category: str, title: str, content: str, editor_id: str, revision=0):
        event = Article.Issued(
            article_id=article_id,
            category=category,
            title=title,
            content=content,
            editor_id=editor_id,
            occurred_on=None,
            sequence=None,
            revision=revision
        )
        return Article([event])

    def __init__(self, events: [DomainEvent]):
        self.events: [DomainEvent] = events

    def update(self, category, title, content, editor_id):
        assert not self._is_discarded
        event = Article.Issued(
            article_id=self.id,
            category=category,
            title=title,
            content=content,
            editor_id=editor_id,
            revision=self.revision + 1,
            occurred_on=None,
            sequence=None
        )
        self.events.append(event)
        return self

    def discard(self, editor_id):
        assert not self._is_discarded
        event = Article.Discarded(
            article_id=self.id,
            editor_id=editor_id,
            revision=self.revision + 1,
            occurred_on=None,
            sequence=None
        )
        self.events.append(event)
        return self

    @property
    def _is_discarded(self):
        return isinstance(self.events[-1], Article.Discarded)

    @property
    def _last(self) -> DomainEvent:
        return self.events[-1]

    def _find(self, attr):
        for i in reversed(self.events):
            if hasattr(i, attr):
                return getattr(i, attr)

    @property
    def id(self):
        return self._last.generator_id

    @property
    def revision(self):
        return self._last.sequence_number

    @property
    def category(self):
        return self._find('category')

    @property
    def title(self):
        return self._find('title')

    @property
    def content(self):
        return self._find('content')


class ArticleRepository(object):
    def put(self, article: Article):
        raise NotImplementedError

    def get(self, article_id: str, revision: int = None) -> Article:
        raise NotImplementedError


class NaiveArticleRepository(ArticleRepository):
    def __init__(self, event_store: EventStore):
        self._event_store = event_store

    def put(self, article: Article):
        if self._event_store.load_event_stream(article.id, article.revision):
            raise EventStoreConcurrencyException
        self._event_store.add_to_stream(article.events)

    def get(self, article_id: str, revision: int = None) -> Article:
        events = self._event_store.load_event_stream(article_id, revision)
        return Article(events)


def new_id():
    return str(uuid.uuid1())


class Editor(object):
    def __init__(self, user_id):
        self.user_id = user_id

    def create(self, article_repository: ArticleRepository, category: str, title: str, content: str) -> str:
        article_id = new_id()
        article = Article.create(article_id, category, title, content, self.user_id)
        article_repository.put(article)
        return article_id

    @staticmethod
    def read(article_repository: ArticleRepository, article_id: str, revision: int) -> Article:
        return article_repository.get(article_id, revision)

    def update(self, article_repository: ArticleRepository, article_id: str, category: str, title: str, content: str,
               revision: int):
        article = article_repository.get(article_id, revision)
        article.update(category, title, content, self.user_id)
        article_repository.put(article)

    def delete(self, article_repository: ArticleRepository, article_id: str, revision: int):
        article = article_repository.get(article_id, revision)
        article.discard(self.user_id)
        article_repository.put(article)


class EditorRepository(object):
    @staticmethod
    def find(user_id: str) -> Editor:
        return Editor(user_id)
