from extra.lib.homeplate import HomeplateException
from extra.rpc import rpc

class UserDict(dict):
    backend = None

    @property
    def id(self):
        return self['user_ref']

    def is_authenticated(self):
        return True

    def save(self, *a, **kw):
        pass


class RemoteAccount(object):
    """
    Checks RPC connection to HP for user base.
    """
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        try:
            return UserDict(rpc.authentication.checkPassword(username, password))
        except HomeplateException:
            return None

    def get_user(self, user_id):
        try:
            return UserDict(rpc.manage.getUser(user_id))
        except HomeplateException:
            return None

    def has_perm(self, user_obj, perm):
        return rpc.authentication.checkRole(user_obj['user_ref'], perm)
