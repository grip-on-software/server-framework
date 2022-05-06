"""
Module that provides authentication schemes.

Copyright 2017-2020 ICTU
Copyright 2017-2022 Leiden University

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import crypt
import logging
import re
try:
    import pwd
except ImportError:
    pwd = None
try:
    import spwd
except ImportError:
    spwd = None
try:
    import ldap
except ImportError:
    ldap = None

class LoginException(RuntimeError):
    """
    Exception that indicates a login error.
    """

class Authentication:
    """
    Authentication scheme.
    """

    _auth_types = {}

    @classmethod
    def register(cls, auth_type):
        """
        Decorator method for a class that registers a certain `auth_type`.
        """

        def decorator(subject):
            """
            Decorator that registers the class `subject` to the authentication
            type.
            """

            cls._auth_types[auth_type] = subject

            return subject

        return decorator

    @classmethod
    def get_type(cls, auth_type):
        """
        Retrieve the class registered for the given `auth_type` string.
        """

        if auth_type not in cls._auth_types:
            raise RuntimeError(f'Authentication type {auth_type} is not supported')

        return cls._auth_types[auth_type]

    @classmethod
    def get_types(cls):
        """
        Retrieve the authentication type names.
        """

        return cls._auth_types.keys()

    def __init__(self, args, config):
        self.args = args
        self.config = config

    def validate(self, username, password):
        """
        Validate the login of a user with the given password.

        If this method returns a string, then it indicates the displayable name
        of the user. Any return value indicates success; an authentication
        failure results in a `LoginException`.
        """

        raise NotImplementedError('Must be implemented by subclasses')

@Authentication.register('open')
class Open(Authentication):
    """
    Open login authentication which accepts all user/password combinations.

    Only to be used in debugging environments.
    """

    def __init__(self, args, config):
        super().__init__(args, config)
        if not args.debug:
            raise RuntimeError('Open authentication must not be used outside debug environment')

    def validate(self, username, password):
        return True

class Unix(Authentication):
    """
    Authentication based on Unix password databases.
    """

    def get_crypted_password(self, username):
        """
        Retrieve the crypted password for the username from the database.

        If the password cannot be retrieved, a `LoginException` is raised.
        """

        raise NotImplementedError('Must be implemented in subclasses')

    def get_display_name(self, username):
        """
        Retrieve the display name for the username.

        If the display name is unavailable, then the username is returned.
        """

        # pylint: disable=no-self-use

        try:
            display_name = pwd.getpwnam(username).pw_gecos.split(',', 1)[0]
        except KeyError:
            return username

        if display_name == '':
            return username

        return display_name

    def validate(self, username, password):
        crypted_password = self.get_crypted_password(username)
        if crypted_password in ('', 'x', '*', '********'):
            raise LoginException(f'Password is disabled for {username}')

        if crypt.crypt(password, crypted_password) == crypted_password:
            return self.get_display_name(username)

        raise LoginException('Invalid credentials')

@Authentication.register('pwd')
class UnixPwd(Unix):
    """
    Authentication using the `/etc/passwd` database.
    """

    def __init__(self, args, config):
        super().__init__(args, config)
        if pwd is None:
            raise ImportError('pwd not available on this platform')

    def get_crypted_password(self, username):
        try:
            return pwd.getpwnam(username).pw_passwd
        except KeyError as error:
            raise LoginException(f'User {username} does not exist') from error

@Authentication.register('spwd')
class UnixSpwd(Unix):
    """
    Authentication using the `/etc/shadow` privileged database.
    """

    def __init__(self, args, config):
        super().__init__(args, config)
        if spwd is None:
            raise ImportError('spwd not available on this platform')

    def get_crypted_password(self, username):
        try:
            return spwd.getspnam(username).sp_pwd
        except KeyError as error:
            raise LoginException(f'User {username} does not exist') from error

@Authentication.register('ldap')
class LDAP(Authentication):
    """
    LDAP group-based authentication scheme.
    """

    def __init__(self, args, config):
        super().__init__(args, config)
        if ldap is None:
            raise ImportError('Unable to use LDAP; install the python-ldap package')

        self._group = self._retrieve_ldap_group()
        if config.has_option('ldap', 'whitelist'):
            self._whitelist = re.split(r'\s*(?<!\\),\s*',
                                       self.config.get('ldap', 'whitelist'))
        else:
            self._whitelist = []

    def _retrieve_ldap_group(self):
        logging.info('Retrieving LDAP group list using manager DN...')
        group_attr = self.config.get('ldap', 'group_attr')
        result = self._query_ldap(self.config.get('ldap', 'manager_dn'),
                                  self.config.get('ldap', 'manager_password'),
                                  search=self.config.get('ldap', 'group_dn'),
                                  search_attrs=[str(group_attr)])[0][1]
        return [username.decode('utf-8') for username in result[group_attr]]

    def _query_ldap(self, username, password, search=None, search_attrs=None):
        client = ldap.initialize(self.config.get('ldap', 'server'))
        # Synchronous bind
        client.set_option(ldap.OPT_REFERRALS, 0)

        try:
            client.simple_bind_s(username, password)
            if search is not None:
                return client.search_s(self.config.get('ldap', 'root_dn'),
                                       ldap.SCOPE_SUBTREE, search,
                                       search_attrs)

            return True
        except (ldap.INVALID_CREDENTIALS, ldap.UNWILLING_TO_PERFORM):
            return False
        finally:
            client.unbind()

        return True

    def _validate_ldap(self, username, password):
        # Pre-check: user in group or whitelist?
        if username not in self._group and username not in self._whitelist:
            raise LoginException(f'User {username} not in group')

        # Next check: get DN from uid
        search = self.config.get('ldap', 'search_filter').format(username)
        display_name_field = str(self.config.get('ldap', 'display_name'))
        result = self._query_ldap(self.config.get('ldap', 'manager_dn'),
                                  self.config.get('ldap', 'manager_password'),
                                  search=search,
                                  search_attrs=[display_name_field])[0]

        # Retrieve DN and display name
        login_name = result[0]
        display_name = result[1][display_name_field][0].decode('utf-8')

        # Final check: log in
        if self._query_ldap(login_name, password):
            return display_name

        raise LoginException('Credentials invalid')

    def validate(self, username, password):
        return self._validate_ldap(username, password)
