"""
Tests for module that provides authentication schemas.

Copyright 2017-2020 ICTU
Copyright 2017-2022 Leiden University
Copyright 2017-2024 Leon Helwerda

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

from argparse import Namespace
from configparser import RawConfigParser
import unittest
from unittest.mock import patch, MagicMock, DEFAULT
from typing import Any, Dict, List, Optional, Tuple, Union, TYPE_CHECKING
from server.authentication import Authentication, LDAP, LoginException, Open
try:
    import ldap
except ImportError:
    if not TYPE_CHECKING:
        ldap = None

_LDAPResult = List[Tuple[str, Dict[str, List[bytes]]]]
_SideEffect = Tuple[Any, ...] # Union[Literal[DEFAULT], Type[Exception]]

class AuthenticationTest(unittest.TestCase):
    """
    Tests for authentication scheme.
    """

    def test_get_type(self) -> None:
        """
        Test retrieve the class registered for a given string.
        """

        self.assertEqual(Authentication.get_type('open'), Open)
        with self.assertRaises(RuntimeError):
            Authentication.get_type('nonexistent')

    def test_get_types(self) -> None:
        """
        Test retrieving the authentication type names.
        """

        self.assertEqual(Authentication.get_types(),
                         ('open', 'pwd', 'spwd', 'ldap'))

class OpenTest(unittest.TestCase):
    """
    Test for open login authentication.
    """

    def test_validate(self) -> None:
        """
        Test validating the login of a user with a password.
        """

        args = Namespace()
        args.debug = False
        config = RawConfigParser()
        with self.assertRaises(RuntimeError):
            Open(args, config)

        args.debug = True
        auth = Open(args, config)
        self.assertTrue(auth.validate('foo', 'bar'))
        self.assertFalse(auth.validate('', 'baz'))

class LDAPTest(unittest.TestCase):
    """
    Test for LDAP group-based authentication scheme.
    """

    @unittest.skipIf(ldap is None, 'python-ldap must be installed')
    @patch('ldap.initialize')
    def test_validate(self, initialize: MagicMock) -> None:
        """
        Test validating the login of a user with a password.
        """

        args = Namespace()
        config = RawConfigParser()
        config['ldap'] = {}
        config['ldap']['server'] = 'ldap://example.test'
        config['ldap']['root_dn'] = 'dc=example,dc=test'
        config['ldap']['search_filter'] = 'uid={}'
        config['ldap']['manager_dn'] = 'cn=manager,dc=example,dc=test'
        config['ldap']['manager_password'] = 'manpass'
        config['ldap']['group_attr'] = 'memberUid'
        config['ldap']['group_dn'] = 'cn=group'
        config['ldap']['display_name'] = 'cn'

        # Set up the authentication scheme with the group search.
        client = initialize.return_value
        attrs: Dict[str, Optional[Union[_LDAPResult, _SideEffect, bool]]] = {
            'search_s.return_value': [
                ('group', {'memberUid': [b'testuser', b'other']})
            ]
        }
        client.configure_mock(**attrs)
        auth = LDAP(args, config)

        # Test logging in with a user in the group and with a valid response.
        attrs = {
            'search_s.return_value': [
                ('testuser', {'cn': [b'Test User']})
            ]
        }
        client.configure_mock(**attrs)

        self.assertEqual(auth.validate('testuser', 'testpass'), 'Test User')

        # Test logging in with a user not in the group.
        with self.assertRaisesRegex(LoginException, 'User outside not in group'):
            auth.validate('outside', 'outpass')

        # Test logging in with invalid credentials
        attrs = {
            'simple_bind_s.side_effect': (DEFAULT, ldap.INVALID_CREDENTIALS)
        }
        client.configure_mock(**attrs)
        with self.assertRaisesRegex(LoginException, 'Credentials invalid'):
            auth.validate('testuser', 'invalid')

        # Test invalid LDAP response during login.
        attrs = {
            'simple_bind_s.side_effect': None,
            'search_s.return_value': False
        }
        client.configure_mock(**attrs)
        with self.assertRaisesRegex(ValueError, 'Invalid LDAP response'):
            auth.validate('testuser', 'testpass')

        # Test invalid LDAP response for group query during setup.
        with self.assertRaisesRegex(ValueError, 'Invalid LDAP response'):
            LDAP(args, config)
