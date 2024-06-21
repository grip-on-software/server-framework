# GROS Python server framework

[![PyPI](https://img.shields.io/pypi/v/gros-server.svg)](https://pypi.python.org/pypi/gros-server)
[![Build 
status](https://github.com/grip-on-software/server-framework/actions/workflows/server-tests.yml/badge.svg)](https://github.com/grip-on-software/server-framework/actions/workflows/server-tests.yml)
[![Coverage 
Status](https://coveralls.io/repos/github/grip-on-software/server-framework/badge.svg?branch=master)](https://coveralls.io/github/grip-on-software/server-framework?branch=master)
[![Quality Gate
Status](https://sonarcloud.io/api/project_badges/measure?project=grip-on-software_server-framework&metric=alert_status)](https://sonarcloud.io/project/overview?id=grip-on-software_server-framework)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.11580150.svg)](https://doi.org/10.5281/zenodo.11580150)

This repository contains a framework for setting up a Web application based on 
Python modules, using [CherryPy](https://cherrypy.dev/) for routing.

This framework is used for a few servers within the Grip on Software pipeline, 
namely the [deployer](https://github.com/grip-on-software/deployer) and 
[status-dashboard](https://github.com/grip-on-software/status-dashboard) 
repositories.

## Installation and building

The latest version of GROS server framework module and its dependencies can be 
installed using `pip install gros-server`.

Another option is to build the module from this repository, which allows using 
the most recent development code. Some functionality of the server framework is 
based on the [data gathering module](https://pypi.org/project/gros-gatherer/) 
and requires a proper installation of that package. It and other dependencies 
may be installed using `make setup`. The server framework itself may then be 
installed with `make install`, which places the package in your current 
environment. We recommend using a virtual environment during development.

Use `make build` in order to generate a wheel package for the framework. The 
files can then be found in the `dist` directory (and installed from there using 
`pip install <path>`).

The `Jenkinsfile` in this repository contains steps to build the package and 
upload it to a PyPi-based repository so that it may be installed from there, 
when built on a Jenkins CI server.

## Development and testing

To run tests, first install the test dependencies with `make setup_test` which 
also installs all dependencies for the server framework. Then `make coverage` 
provides test results in the output and in XML versions compatible with, e.g., 
JUnit and SonarQube available in the `test-reports/` directory. If you do not 
need XML outputs, then run `make test` to just report on test successes and 
failures or `make cover` to also have the terminal report on hits and misses in 
statements and branches.

[GitHub Actions](https://github.com/grip-on-software/server-framework/actions) 
is used to run the unit tests and report on coverage on commits and pull 
requests. This includes quality gate scans tracked by 
[SonarCloud](https://sonarcloud.io/project/overview?id=grip-on-software_server-framework) 
and [Coveralls](https://coveralls.io/github/grip-on-software/server-framework) 
for coverage history.

The Python module conforms to code style and typing standards which can be 
checked using Pylint with `make pylint` and mypy with `make mypy`, after 
installing the pylint and mypy dependencies using `make setup_analysis`; typing 
reports are XML formats compatible with JUnit and SonarQube placed in the 
`mypy-report/` directory. To also receive the HTML report, use `make mypy_html` 
instead.

We publish releases to [PyPI](https://pypi.org/project/gros-server/) using 
`make setup_release` to install dependencies and `make release` which performs 
multiple checks: unit tests, typing, lint and version number consistency. The 
release files are also published on 
[GitHub](https://github.com/grip-on-software/server-framework/releases) and 
from there are archived on 
[Zenodo](https://zenodo.org/doi/10.5281/zenodo.11580149). Noteworthy changes to 
the module are added to the [changelog](CHANGELOG.md).
