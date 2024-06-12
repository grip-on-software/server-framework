"""
Tests for host validation dispatcher.

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

import unittest
from unittest.mock import patch, MagicMock, Mock
import cherrypy
from server.dispatcher import HostDispatcher

class HostDispatcherTest(unittest.TestCase):
    """
    Tests for dispatcher that performs hostname validation.
    """

    def test_next_dispatcher(self) -> None:
        """
        Test retrieving the next dispatcher in line.
        """

        dispatcher = HostDispatcher(host='example.test', port=443)
        self.assertIsInstance(dispatcher.next_dispatcher,
                              cherrypy.dispatch.Dispatcher)

        next_dispatcher = Mock()
        prev_dispatcher = HostDispatcher(next_dispatcher=next_dispatcher)
        self.assertEqual(prev_dispatcher.next_dispatcher, next_dispatcher)

    def test_domain(self) -> None:
        """
        Test retrieving the expected domain name for the host.
        """

        self.assertEqual(HostDispatcher(host='example.test', port=80).domain,
                         'example.test')
        self.assertEqual(HostDispatcher(host='host.test', port=8080).domain,
                         'host.test:8080')
        self.assertEqual(HostDispatcher(host='ok.test:8888', port=8888).domain,
                         'ok.test:8888')
        self.assertIsNone(HostDispatcher().domain)

    @patch('cherrypy.serving.request')
    def test_call(self, request: MagicMock) -> None:
        """
        Test performing the host validation dispatcher.
        """

        next_dispatcher = Mock()
        dispatcher = HostDispatcher(next_dispatcher=next_dispatcher)
        dispatcher('/')
        next_dispatcher.assert_called_once_with('/')
        self.assertNotIsInstance(request.handler, cherrypy.HTTPError)

        next_dispatcher.reset_mock()
        dispatcher = HostDispatcher(host='example.test',
                                    next_dispatcher=next_dispatcher)
        request.configure_mock(headers={'Host': 'example.test'})
        dispatcher('/')
        next_dispatcher.assert_called_once_with('/')
        self.assertNotIsInstance(request.handler, cherrypy.HTTPError)

        next_dispatcher.reset_mock()
        dispatcher = HostDispatcher(host='example.test',
                                    next_dispatcher=next_dispatcher)
        request.configure_mock(headers={'Host': 'dns-hijack.test:1234'})
        dispatcher('/')
        next_dispatcher.assert_not_called()
        self.assertIsInstance(request.handler, cherrypy.HTTPError)
