from mywiki.domain.model.user.authorization import PolicyManager
from mywiki.domain.model.user.identification import User
from mywiki.domain.model.view.article import ArticleRepository, ViewerRepository, Viewer, Article
from mywiki.domain.model.view.security import AccessControlledArticleRepository


class AccessController(object):
    def __init__(self, article_repository: ArticleRepository, policy_manager: PolicyManager):
        self._article_repository = article_repository
        self._policy_manager = policy_manager

    def get_repository_for(self, user: User):
        permissions = self._policy_manager.user_permissions(user.id)
        return AccessControlledArticleRepository(self._article_repository, permissions)


class ArticleViewService(object):
    def __init__(self, viewers: ViewerRepository, access_controller: AccessController):
        self._viewers = viewers
        self._access_controller = access_controller

    def get_article_list(self, user: User) -> [Article]:
        repository = self._access_controller.get_repository_for(user)
        return repository.list()

    def view(self, user: User, article_id: str, revision: int = None) -> Article:
        viewer: Viewer = self._viewers.find(user.id)
        repository = self._access_controller.get_repository_for(user)
        return viewer.view(repository, article_id, revision)
