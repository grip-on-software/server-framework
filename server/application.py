"""
Authenticated Web application framework.

Copyright 2017-2020 ICTU
Copyright 2017-2022 Leiden University
Copyright 2017-2023 Leon Helwerda

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
import logging
from typing import Any, Optional
from urllib.parse import quote
import cherrypy
from .authentication import LoginException, Authentication

class Authenticated_Application:
    # pylint: disable=no-self-use
    """
    A Web application that requires authentication.
    """

    def __init__(self, args: Namespace, config: RawConfigParser):
        auth_type = Authentication.get_type(args.auth)
        self.authentication = auth_type(args, config)

    @cherrypy.expose
    def index(self, page: str = 'list', params: str = '') -> str:
        """
        Login form.
        """

        raise NotImplementedError("Must be implemented by subclasses")

    @cherrypy.expose
    def logout(self) -> str:
        """
        Log out the user.
        """

        cherrypy.session.pop('authenticated', None)
        cherrypy.lib.sessions.expire()

        raise cherrypy.HTTPRedirect('index')

    def validate_page(self, page: str) -> None:
        """
        Validate a page identifier. Raises an `HTTPError` if the page is
        not an existing exposed route.
        """

        try:
            getattr(self, page).exposed
        except AttributeError as error:
            # Invalid method or not exposed
            raise cherrypy.HTTPError(400, 'Page must be valid') from error

    def _perform_login(self, username: str, password: str) -> bool:
        try:
            result = self.authentication.validate(username, password)
            logging.info('Authenticated as %s', username)
            if isinstance(result, str):
                cherrypy.session['authenticated'] = result
            else:
                cherrypy.session['authenticated'] = username

            return True
        except LoginException as error:
            logging.info(str(error))
            return False

    def validate_login(self, username: Optional[str] = None,
                       password: Optional[str] = None,
                       page: Optional[str] = None,
                       params: Optional[str] = None) -> None:
        """
        Validate a login request with the `username` and `password`. Raises an
        `HTTPError` if the login is not accepted, possibly being redirected to
        the index with the `page` and the `params` as query string.
        """

        if page is None:
            page = cherrypy.request.path_info.strip('/')

        if params is None:
            params = quote(cherrypy.request.query_string)

        # Redirect on login failure
        redirect = f'index?page={page}'
        if params != '' and page != '':
            redirect += '&params={params}'

        if (username is not None or password is not None) and \
            cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError(400, 'POST only allowed for username and password')

        if username is not None and password is not None and \
            not self._perform_login(username, password):
            raise cherrypy.HTTPRedirect(redirect)

        if 'authenticated' not in cherrypy.session:
            logging.info('No credentials or session found')
            raise cherrypy.HTTPRedirect(redirect)

    @cherrypy.expose
    def login(self, username: Optional[str] = None,
              password: Optional[str] = None, page: str = 'list',
              params: str = '') -> str:
        """
        Log in the user with the given `username` and `password`. Upon success,
        a redirect to the `page` with the `params` in the query string is made.
        """

        self.validate_login(username=username, password=password, page=page,
                            params=params)

        # Validate the target page only after logging in
        self.validate_page(page)

        if params != '':
            page += f'?{params}'
        raise cherrypy.HTTPRedirect(page)

    @cherrypy.expose
    def default(self, *args: Any, **kwargs: Any) -> str:
        # pylint: disable=unused-argument
        """
        Default handler for nonexistent pages. These are redirected to the
        index page when not logged in.
        """

        if 'authenticated' not in cherrypy.session:
            raise cherrypy.HTTPRedirect('index')

        raise cherrypy.NotFound()
