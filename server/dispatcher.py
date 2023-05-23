"""
Host validation dispatcher.

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

from typing import Callable, Optional
import cherrypy

Dispatcher = Callable[[str], None]

class HostDispatcher:
    """
    Dispatcher that performs hostname validation.
    """

    def __init__(self, host: Optional[str] = None, port: int = 80,
                  next_dispatcher: Optional[Dispatcher] = None):
        if next_dispatcher is None:
            next_dispatcher = cherrypy.dispatch.Dispatcher()
        self._next_dispatcher = next_dispatcher

        self._domain: Optional[str] = None
        if host is not None and ':' not in host and port != 80:
            self._domain = f'{host}:{port}'
        elif host is not None:
            self._domain = host

    @property
    def next_dispatcher(self) -> Dispatcher:
        """
        Retrieve the next dispatcher in line to be used if the host validation
        succeeds.
        """

        return self._next_dispatcher

    @property
    def domain(self) -> Optional[str]:
        """
        Retrieve the expected domain name for the host.
        """

        return self._domain

    def __call__(self, path_info: str) -> None:
        if self._domain is None:
            return self._next_dispatcher(path_info)

        request = cherrypy.serving.request
        host = request.headers.get('Host', '')
        if host == self._domain:
            return self._next_dispatcher(path_info)

        request.config = cherrypy.config.copy()
        request.handler = cherrypy.HTTPError(403, 'Invalid Host header')
        return None
