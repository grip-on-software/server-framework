"""
Tests for authenticated Web application framework.

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
from datetime import datetime
from http.cookies import SimpleCookie
from unittest.mock import patch
import cherrypy
from cherrypy.test import helper
from server.application import Authenticated_Application
from server.authentication import Open

class TestServer(Authenticated_Application):
    """
    Test server.
    """

    @cherrypy.expose
    def index(self, page: str = 'list', params: str = '') -> str:
        return "Index page"

    @cherrypy.expose
    def list(self) -> str:
        """
        Authenticated target page after login.
        """

        self.validate_login()

        return f"List page for {cherrypy.session['authenticated']}"

class AuthenticatedApplicationTest(helper.CPWebCase):
    """
    Tests for Web application that requires authentication.
    """

    @staticmethod
    def setup_server() -> None:
        """"
        Set up the application server.
        """

        args = Namespace()
        args.auth = 'open'
        args.debug = True

        config = RawConfigParser()

        cherrypy.tree.mount(TestServer(args, config), '/', {
            '/': {
                'tools.sessions.on': True,
                'tools.sessions.httponly': True,
            }
        })

    def test_index(self) -> None:
        """
        Test the index page.
        """

        self.getPage("/")
        self.assertStatus('200 OK')
        self.assertBody('Index page')

    def test_list(self) -> None:
        """
        Test the list page.
        """

        self.getPage("/list")
        self.assertIn('/index?page=list', self.assertHeader('Location'))

        self.getPage("/login", method="POST", body='username=foo&password=bar')
        header = self.assertHeader('Set-Cookie')
        cookie = SimpleCookie()
        cookie.load(header)

        session_id = cookie["session_id"].value
        self.getPage("/list", headers=[('Cookie', f'session_id={session_id}')])
        self.assertStatus('200 OK')
        self.assertInBody('List page')

        with patch.object(Open, 'validate', return_value='Test User'):
            self.getPage("/login", method="POST",
                         body='username=testuser&password=testpass')
            header = self.assertHeader('Set-Cookie')
            cookie = SimpleCookie()
            cookie.load(header)

            session_id = cookie["session_id"].value
            self.getPage("/list",
                         headers=[('Cookie', f'session_id={session_id}')])
            self.assertStatus('200 OK')
            self.assertBody('List page for Test User')

    def test_login(self) -> None:
        """
        Test the login page.
        """

        self.getPage("/login")
        self.assertIn('/index?page=list', self.assertHeader('Location'))

        self.getPage("/login?page=list&params=foo=bar")
        self.assertIn('/index?page=list&params=foo=bar',
                      self.assertHeader('Location'))

        # Invalid credentials are rejected and user returned to the index.
        self.getPage("/login", method="POST", body='username=&password=invalid')
        self.assertIn('/index?page=list', self.assertHeader('Location'))

        self.getPage("/login", method="POST", body='username=foo&password=bar')
        self.assertIn('/list', self.assertHeader('Location'))
        self.assertHeader('Set-Cookie')

        self.getPage("/login?page=list&params=foo=bar", method="POST",
                     body='username=foo&password=bar')
        self.assertIn('/list?foo=bar', self.assertHeader('Location'))
        self.assertHeader('Set-Cookie')

        self.getPage("/login?page=nonexistent", method="POST",
                     body='username=foo&password=bar')
        self.assertStatus('400 Bad Request')
        self.assertInBody('Page must be valid')

        self.getPage("/login?username=foo&password=oops", method="GET")
        self.assertStatus('400 Bad Request')
        self.assertInBody('POST only allowed for username and password')

    def test_logout(self) -> None:
        """
        Test the logout page.
        """

        self.getPage("/logout")
        self.assertIn('/index', self.assertHeader('Location'))

        # Check that the provided cookie is set to expire.
        header = self.assertHeader('Set-Cookie')
        cookie = SimpleCookie()
        cookie.load(header)
        expires = datetime.strptime(cookie['session_id']['expires'],
                                    '%a, %d %b %Y %H:%M:%S %Z')
        self.assertLessEqual(expires, datetime.now())

    def test_default(self) -> None:
        """
        Test nonexistent pages.
        """

        self.getPage("/nonexistent")
        self.assertIn('/index', self.assertHeader('Location'))

        self.getPage("/login", method="POST", body='username=foo&password=bar')
        header = self.assertHeader('Set-Cookie')
        cookie = SimpleCookie()
        cookie.load(header)

        session_id = cookie["session_id"].value
        self.getPage("/nonexistent",
                     headers=[('Cookie', f'session_id={session_id}')])
        self.assertStatus('404 Not Found')
