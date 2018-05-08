from urllib.parse import urlparse

from mywiki.domain.model.user.authorization import Permission
from mywiki.domain.model.view.article import ArticleRepository, Article


class AccessControlledArticleRepository(ArticleRepository):
    def __init__(self, article_repository: ArticleRepository, permissions: [Permission]):
        uri_list = [urlparse(permission.uri) for permission in permissions]
        uri_list = filter(lambda uri: uri.scheme == 'view', uri_list)
        self._prefix_list = list(map(lambda uri: uri.path[1:], uri_list))
        self._article_repository = article_repository

    def list(self) -> [Article]:
        return list(filter(lambda article: self._has_permission(article.category), self._article_repository.list()))

    def get(self, article_id: str, revision: int) -> Article:
        article = self._article_repository.get(article_id, revision)
        if not article:
            return None
        self._check_permission(article)
        return article

    def delete(self, article_id: str, revision: int):
        article = self._article_repository.get(article_id, revision)
        self._check_permission(article)
        return self._article_repository.delete(article_id, revision)

    def put(self, article: Article):
        self._check_permission(article)
        return self._article_repository.put(article)

    def _check_permission(self, article: Article):
        if not self._has_permission(article.category):
            raise PermissionError

    def _has_permission(self, category: str):
        return any(map(lambda prefix: category.startswith(prefix), self._prefix_list))
