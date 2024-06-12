"""
Tests for generic Web service bootstrapper.

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

from argparse import ArgumentParser
from configparser import RawConfigParser
from typing import Any, Dict
import unittest
from unittest.mock import patch
from gatherer.config import Configuration
from server.bootstrap import Bootstrap

class TestSetup(Bootstrap):
    """
    Example implementation of the server setup procedure.
    """

    @property
    def application_id(self) -> str:
        return 'test'

    @property
    def description(self) -> str:
        return 'Test'

    def add_args(self, parser: ArgumentParser) -> None:
        pass

    def mount(self, conf: Dict[str, Dict[str, Any]]) -> None:
        pass

class BootstrapTest(unittest.TestCase):
    """
    Tests for server setup procedure.
    """

    def setUp(self) -> None:
        logging_patcher = patch('logging.config.dictConfig')
        self.logging = logging_patcher.start()
        self.addCleanup(logging_patcher.stop)

        daemon_patcher = patch('cherrypy.daemon.start')
        self.daemon = daemon_patcher.start()
        self.addCleanup(daemon_patcher.stop)

        config = RawConfigParser()
        config['deploy'] = {}
        config['deploy']['auth'] = 'open'
        config_patcher = patch.object(Configuration, 'get_settings',
                                      return_value=config)
        config_patcher.start()
        self.addCleanup(config_patcher.stop)

        argv_patcher = patch('sys.argv', new=['test.py'])
        argv_patcher.start()
        self.addCleanup(argv_patcher.stop)

        self.bootstrap = TestSetup()

    def test_args(self) -> None:
        """
        Test retrieving the arguments.
        """

        with self.assertRaises(RuntimeError):
            args = self.bootstrap.args

        self.bootstrap.bootstrap()
        args = self.bootstrap.args
        self.assertEqual(args.auth, 'open')

    def test_bootstrap(self) -> None:
        """
        Test starting the server.
        """

        self.bootstrap.bootstrap()
        self.daemon.assert_called_once()
