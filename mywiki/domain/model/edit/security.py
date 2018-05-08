from urllib.parse import urlparse

from mywiki.domain.model.edit.article import Article, ArticleRepository
from mywiki.domain.model.user.authorization import Permission


class AccessControlledArticleRepository(ArticleRepository):
    def __init__(self, article_repository: ArticleRepository, permissions: [Permission]):

        uri_list = [urlparse(permission.uri) for permission in permissions]
        uri_list = filter(lambda uri: uri.scheme == 'edit', uri_list)
        self._category_list = list(map(lambda uri: uri.path[1:], uri_list))
        self._article_repository = article_repository

    def put(self, article: Article):
        self._check_permission(article)
        self._article_repository.put(article)

    def get(self, article_id: str, revision: int = None) -> Article:
        article = self._article_repository.get(article_id, revision)
        self._check_permission(article)
        return article

    def _is_accessible(self, category: str):
        return any(map(lambda prefix: category.startswith(prefix), self._category_list))

    def _check_permission(self, article: Article):
        if not self._is_accessible(article.category):
            raise PermissionError(article.category)
