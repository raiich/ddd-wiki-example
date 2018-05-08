from mywiki.domain.model.edit.article import Article, ArticleRepository, Editor, EditorRepository
from mywiki.domain.model.edit.security import AccessControlledArticleRepository
from mywiki.domain.model.user.authorization import PolicyManager
from mywiki.domain.model.user.identification import User


class AccessController(object):
    def __init__(self, article_repository: ArticleRepository, policy_manager: PolicyManager):
        self._article_repository = article_repository
        self._policy_manager = policy_manager

    def get_publisher_for(self, user: User) -> ArticleRepository:
        permissions = self._policy_manager.user_permissions(user.id)
        return AccessControlledArticleRepository(self._article_repository, permissions)


class ArticleEditService(object):
    def __init__(self, editor_repository: EditorRepository, access_controller: AccessController):
        self._editor_repository = editor_repository
        self._access_controller = access_controller

    def _context(self, user: User) -> (Editor, ArticleRepository):
        return self._editor_repository.find(user.id), self._access_controller.get_publisher_for(user)

    def create(self, user: User, category: str, title: str, content: str):
        editor, article_repository = self._context(user)
        editor.create(article_repository, category, title, content)

    def read(self, user: User, article_id: str, revision: int) -> Article:
        editor, article_repository = self._context(user)
        return editor.read(article_repository, article_id, revision)

    def update(self, user: User, article_id: str, category: str, title: str, content: str, revision: int):
        editor, article_repository = self._context(user)
        editor.update(article_repository, article_id, category, title, content, revision)

    def delete(self, user: User, article_id: str, revision: int):
        editor, article_repository = self._context(user)
        editor.delete(article_repository, article_id, revision)
