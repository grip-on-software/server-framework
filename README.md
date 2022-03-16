# GROS Python server framework

This repository contains a framework for setting up a Web application based on 
Python modules, using [CherryPy](https://cherrypy.dev/) for routing.

This framework is used for a few servers within the Grip on Software pipeline, 
namely the `deployer` and `status-dashboard` repositories.

## Building

Use `python setup.py sdist` followed by `python setup.py bdist_wheel` in order 
to generate a wheel package for the framework. The files can then be found in 
the `dist` directory (and installed from there using `pip install <path>`).

The `Jenkinsfile` in this repository contains steps to build the package and 
upload it to a PyPi-based repository so that it may be installed from there, 
when built on a Jenkins CI server.
