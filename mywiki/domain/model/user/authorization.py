from collections import namedtuple

Policy = namedtuple('Policy', ('role_id', 'permissions'))
Role = namedtuple('Role', ('id', 'role_name'))
Permission = namedtuple('Permission', 'uri')


class PolicyManager(object):
    def user_permissions(self, user_id: str) -> [Permission]:
        raise NotImplementedError


class RoleBasedPolicyRepository(object):
    def put_role(self, role: Role):
        raise NotImplementedError

    def get_role(self, role_id: str) -> Role:
        raise NotImplementedError

    def delete_role(self, role_id: str):
        raise NotImplementedError

    def roles(self) -> [Role]:
        raise NotImplementedError

    def put_policy(self, policy: Policy):
        raise NotImplementedError

    def get_policy(self, role_id: str) -> Policy:
        raise NotImplementedError

    def delete_policy(self, role_id: str):
        raise NotImplementedError

    def put_user_role(self, user_id, role_id):
        raise NotImplementedError

    def get_user_roles(self, user_id) -> [Role]:
        raise NotImplementedError
