from mywiki import presentation
from mywiki.application.edit import ArticleEditService, AccessController as EditSecurityManager
from mywiki.application.view import ArticleViewService, AccessController as ViewSecurityManager
from mywiki.domain.event import DomainEventPublisher
from mywiki.domain.model.edit.article import EditorRepository, NaiveArticleRepository
from mywiki.domain.model.view.article import ViewerRepository, ArticleConverter
from mywiki.infrastructure.flask import SessionUserIdentificationService
from mywiki.infrastructure.mock import (
    MockUserRepository, MockHtmlRepository, MockPasswordAuthenticationService, MockPolicyManager,
    MockNotifyingEventStore)


def main():
    user_repository = MockUserRepository()
    presentation.identification_service = SessionUserIdentificationService(user_repository)
    presentation.authenticator = MockPasswordAuthenticationService()
    policy_manager = MockPolicyManager()

    html_repository = MockHtmlRepository()
    view_security_manager = ViewSecurityManager(html_repository, policy_manager)
    presentation.view_service = ArticleViewService(ViewerRepository(), view_security_manager)

    event_publisher = DomainEventPublisher()
    event_publisher.register(ArticleConverter(html_repository))

    event_store = MockNotifyingEventStore(event_publisher)
    markdown_repository = NaiveArticleRepository(event_store)
    edit_security_manager = EditSecurityManager(markdown_repository, policy_manager)
    presentation.edit_service = ArticleEditService(EditorRepository(), edit_security_manager)

    presentation.run()
