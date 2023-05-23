"""
Generic Web service bootstrapper.

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

from argparse import ArgumentParser, Namespace
import logging.config
from pathlib import Path
from typing import Any, Dict, Optional, Union
import cherrypy
import cherrypy.daemon
from gatherer.config import Configuration
from gatherer.log import Log_Setup
from .authentication import Authentication
from .dispatcher import HostDispatcher

class Bootstrap:
    """
    Server setup procedure.
    """

    def __init__(self) -> None:
        self.config = Configuration.get_settings()
        self._args: Optional[Namespace] = None

    @property
    def application_id(self) -> str:
        """
        Retrieve a short identifier for the application.

        The application ID is used in session cookies.
        """

        return ''

    @property
    def description(self) -> str:
        """
        Retrieve a descriptive message of the server to be used in command-line
        help text.
        """

        raise NotImplementedError('Must be overridden by subclasses')

    @property
    def args(self) -> Namespace:
        """
        Retrieve the arguments. If the setup has not been bootstrapped, this
        raises a `RuntimeError`.
        """

        if self._args is None:
            raise RuntimeError('Not yet bootstrapped')

        return self._args

    def _parse_args(self) -> Namespace:
        """
        Parse command line arguments.
        """

        # Default authentication scheme
        auth: Optional[str] = self.config.get('deploy', 'auth')
        if not Configuration.has_value(auth):
            auth = 'ldap'

        parser = ArgumentParser(description=self.description)
        Log_Setup.add_argument(parser, default='INFO')
        parser.add_argument('--debug', action='store_true', default=False,
                            help='Display logging in terminal and traces on web')
        parser.add_argument('--log-path', dest='log_path', default='.',
                            help='Path to store logs at in production')
        parser.add_argument('--auth', choices=Authentication.get_types(),
                            default=auth, help='Authentication scheme')
        parser.add_argument('--host', default=None,
                            help='Hostname to validate before allowing access')
        parser.add_argument('--port', type=int, default=8080,
                            help='Port for the server to listen on')
        parser.add_argument('--daemonize', action='store_true', default=False,
                            help='Run the server as a daemon')
        parser.add_argument('--pidfile', help='Store process ID in file')
        parser.add_argument('--expiry', type=int, default=12 * 60,
                            help='Number of minutes that session cookies are valid')

        server = parser.add_mutually_exclusive_group()
        server.add_argument('--fastcgi', action='store_true', default=False,
                            help='Start a FastCGI server instead of HTTP')
        server.add_argument('--scgi', action='store_true', default=False,
                            help='Start a SCGI server instead of HTTP')
        server.add_argument('--cgi', action='store_true', default=False,
                            help='Start a CGI server instead of the HTTP')

        self.add_args(parser)
        return parser.parse_args()

    def add_args(self, parser: ArgumentParser) -> None:
        """
        Register additional arguments to the argument parser.
        """

        raise NotImplementedError('Must be overridden by subclasses')

    def _build_log_file_handler(self, filename: str) \
        -> Dict[str, Union[str, int]]:
        return {
            'level': str(self.args.log),
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(Path(self.args.log_path) / filename),
            'formatter': 'void',
            'maxBytes': 10485760,
            'backupCount': 20,
            'encoding': 'utf8'
        }

    def _setup_log(self) -> None:
        """
        Setup logging.
        """

        stream_handler = {
            'level': str(self.args.log),
            'class':'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        }

        config = {
            'version': 1,
            'formatters': {
                'void': {
                    'format': ''
                },
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
            },
            'handlers': {
                'default': stream_handler.copy(),
                'cherrypy_console': stream_handler.copy(),
                'cherrypy_access': self._build_log_file_handler('access.log'),
                'cherrypy_error': self._build_log_file_handler('error.log'),
                'python': self._build_log_file_handler('python.log')
            },
            'loggers': {
                '': {
                    'handlers': ['default' if self.args.debug else 'python'],
                    'level': self.args.log
                },
                'cherrypy.access': {
                    'handlers': ['cherrypy_console' if self.args.debug else 'cherrypy_access'],
                    'level': str(self.args.log),
                    'propagate': False
                },
                'cherrypy.error': {
                    'handlers': ['cherrypy_console' if self.args.debug else 'cherrypy_error'],
                    'level': str(self.args.log),
                    'propagate': False
                },
            }
        }
        logging.config.dictConfig(config)

    def mount(self, conf: Dict[str, Dict[str, Any]]) -> None:
        """
        Mount the application on the server. `conf` is a dictionary of cherrypy
        configuration sections with which the application can be configured.
        """

        raise NotImplementedError('Must be implemented by subclasses')

    def bootstrap(self) -> None:
        """
        Start the WSGI server.
        """

        # Setup arguments and configuration
        self._args = self._parse_args()
        self._setup_log()
        conf = {
            'global': {
                'request.show_tracebacks': self.args.debug
            },
            '/': {
                'tools.sessions.on': True,
                'tools.sessions.name': f'{self.application_id}_session',
                'tools.sessions.httponly': True,
                'tools.sessions.expiry': self.args.expiry,
                'request.dispatch': HostDispatcher(host=self.args.host,
                                                   port=self.args.port)
            }
        }
        cherrypy.config.update({'server.socket_port': self.args.port})

        # Start the application and server daemon.
        self.mount(conf)
        cherrypy.daemon.start(daemonize=self.args.daemonize,
                              pidfile=self.args.pidfile,
                              fastcgi=self.args.fastcgi,
                              scgi=self.args.scgi,
                              cgi=self.args.cgi)
