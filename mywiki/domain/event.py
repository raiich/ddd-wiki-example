from datetime import datetime


class DomainEvent(object):
    def __init__(self, generator_id: str, sequence_number: int, occurred_on: datetime = None):
        self.generator_id = generator_id
        self.sequence_number = sequence_number
        self.occurred_on = occurred_on


class EventStoreConcurrencyException(Exception):
    pass


class RecentEventStream(object):
    def __init__(self, events: [DomainEvent]):
        self.events = events

    def archive(self):
        raise NotImplementedError


class EventStore(object):
    def add_to_stream(self, events: [DomainEvent]):
        raise NotImplementedError

    def load_event_stream(self, generator_id: str, start: int = None) -> [DomainEvent]:
        raise NotImplementedError

    def recent(self) -> RecentEventStream:
        raise NotImplementedError


class DomainEventSubscriber(object):
    def handle_event(self, event: DomainEvent):
        raise NotImplementedError


class DomainEventPublisher(object):
    def __init__(self):
        self._subscribers: [DomainEventSubscriber] = []

    def register(self, subscriber: DomainEventSubscriber):
        self._subscribers.append(subscriber)

    def publish_from_event_store(self, event_store: EventStore):
        recent = event_store.recent()
        for event in recent.events:
            for s in self._subscribers:
                s.handle_event(event)
        recent.archive()
