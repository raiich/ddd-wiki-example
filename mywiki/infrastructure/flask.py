from mywiki.domain.model.user.identification import User, UserIdentificationService, UserRepository, anonymous


class SessionUserIdentificationService(UserIdentificationService):
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def identify(self, session) -> User:
        user_id = session.get('user_id')
        return self._user_repository.find(user_id) or anonymous
