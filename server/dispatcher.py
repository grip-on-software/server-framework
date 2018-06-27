"""
Host validation dispatcher.
"""

import cherrypy

class HostDispatcher(object):
    """
    Dispatcher that performs hostname validation.
    """

    def __init__(self, host=None, port=80, next_dispatcher=None):
        if next_dispatcher is None:
            next_dispatcher = cherrypy.dispatch.Dispatcher()
        self._next_dispatcher = next_dispatcher

        if host is not None and ':' not in host and port != 80:
            self._domain = '{}:{}'.format(host, port)
        elif host is not None:
            self._domain = host
        else:
            self._domain = None

    @property
    def next_dispatcher(self):
        """
        Retrieve the next dispatcher in line to be used if the host validation
        succeeds.
        """

        return self._next_dispatcher

    @property
    def domain(self):
        """
        Retrieve the expected domain name for the host.
        """

        return self._domain

    def __call__(self, path_info):
        if self._domain is None:
            return self._next_dispatcher(path_info)

        request = cherrypy.serving.request
        host = request.headers.get('Host', '')
        if host == self._domain:
            return self._next_dispatcher(path_info)

        request.config = cherrypy.config.copy()
        request.handler = cherrypy.HTTPError(403, 'Invalid Host header')
        return request.handler
