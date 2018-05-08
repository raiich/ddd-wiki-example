import copy

from mywiki.domain.event import EventStore, DomainEventPublisher, DomainEvent, RecentEventStream
from mywiki.domain.model.user.authentication import AuthenticationService
from mywiki.domain.model.user.authorization import PolicyManager, Permission
from mywiki.domain.model.user.identification import UserRepository, User, anonymous
from mywiki.domain.model.view.article import ArticleRepository as HtmlRepository, Article as Html


class MockUserRepository(UserRepository):
    _users = {
        '1': 'admin',
        '2': 'Bob'
    }

    def find(self, user_id: str) -> User:
        username = self._users.get(user_id)
        if username:
            return User(user_id, username)
        else:
            return anonymous

    def put(self, user: User):
        raise NotImplementedError

    def remove(self, user_id: str) -> bool:
        raise NotImplementedError


class MockPasswordAuthenticationService(AuthenticationService):
    def authenticate(self, username: str, password: str) -> str:
        if username == 'admin':
            return '1'
        else:
            return '2'


class MockPolicyManager(PolicyManager):
    _table = {
        '1': ['edit://localhost/', 'view://localhost/'],
        '2': ['view://localhost/']
    }

    def user_permissions(self, user_id) -> [Permission]:
        return map(lambda p: Permission(p), self._table.get(user_id) or [])


class MockNotifyingEventStore(EventStore):
    def __init__(self, publisher: DomainEventPublisher):
        self._publisher = publisher
        self._recent: [DomainEvent] = []
        self._partitioned_streams: {str: DomainEvent} = {}

    def add_to_stream(self, events: [DomainEvent]):
        self._recent.extend(events)
        self._publisher.publish_from_event_store(self)

    def recent(self) -> RecentEventStream:
        store = self

        class MockRecentEventStream(RecentEventStream):
            def __init__(self):
                super().__init__(copy.copy(store._recent))

            def archive(self):
                if self.events:
                    event = self.events[-1]
                    store.archive(event.generator_id, event.sequence_number)
        return MockRecentEventStream()

    def archive(self, generator_id: str, sequence_number: int):
        index = self._find_index(generator_id, sequence_number)
        if index:
            for event in self._recent[:index]:
                self._move_to_partitioned_stream(event)
            self._recent = self._recent[index:]

    def _find_index(self, generator_id: str, sequence_number: int):
        for i, event in enumerate(self._recent):
            if event.generator_id == generator_id and event.sequence_number == sequence_number:
                return i + 1

    def _move_to_partitioned_stream(self, event: DomainEvent):
        if not self._partitioned_streams.get(event.generator_id):
            assert event.sequence_number == 0
            self._partitioned_streams[event.generator_id] = []

        partition = self._partitioned_streams[event.generator_id]
        if len(partition) <= event.sequence_number:
            partition.append(event)
        else:
            assert event == partition[event.sequence_number]

    def load_event_stream(self, generator_id: str, start: int = None) -> [DomainEvent]:
        def is_going(event: DomainEvent):
            return event.generator_id == generator_id and (event.sequence_number >= start if start else True)
        goings = filter(lambda ev: is_going(ev), self._recent)
        cached = self._partitioned_streams.get(generator_id)
        cached = cached[start:] if cached else []
        cached.extend(goings)
        return cached


class MockHtmlRepository(HtmlRepository):
    def __init__(self):
        self._article_dict = {}

    def list(self) -> [Html]:
        return map(lambda ls: ls[len(ls) - 1], self._article_dict.values())

    def get(self, article_id: str, revision: int) -> Html:
        revisions = self._article_dict.get(article_id)
        if not revisions:
            return None
        elif revision is not None:
            if revision < len(revisions):
                return self._article_dict[article_id][revision]
            else:
                return None
        else:
            return revisions[len(revisions) - 1]

    def delete(self, article_id: str, revision: int):
        revisions = self._article_dict[article_id]
        assert len(revisions) == revision
        del self._article_dict[article_id]

    def put(self, article: Html):
        if not self._article_dict.get(article.id):
            self._article_dict[article.id] = []
        assert len(self._article_dict[article.id]) == article.revision
        self._article_dict[article.id].append(article)
