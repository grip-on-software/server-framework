from .ldapobject import LDAPObject

SCOPE_SUBTREE: int = ...
OPT_REFERRALS: int = ...

class Error(Exception):
    pass
class INVALID_CREDENTIALS(Error):
    pass
class UNWILLING_TO_PERFORM(Error):
    pass

def initialize(server: str) -> LDAPObject: ...
