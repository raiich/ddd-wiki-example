from collections import namedtuple

User = namedtuple('User', ('id', 'username'))
anonymous = User(-1, None)


class UserIdentificationService(object):
    def identify(self, *args, **kwargs) -> User:
        raise NotImplementedError


class UserRepository(object):
    def put(self, user: User):
        raise NotImplementedError

    def find(self, user_id: str) -> User:
        raise NotImplementedError

    def remove(self, user_id: str) -> bool:
        raise NotImplementedError
