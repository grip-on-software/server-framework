#!/usr/bin/env python
"""
Package setup script.

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

from setuptools import setup, find_packages

def main():
    """
    Setup the package.
    """

    setup(name='gros-server',
          version='0.0.3',
          description='Grip on Software server framework',
          long_description='''Web application framework for building
authenticated services, with templating to avoid vulnerabilities.''',
          author='Leon Helwerda',
          author_email='l.s.helwerda@liacs.leidenuniv.nl',
          url='https://github.com/grip-on-software/server-framework',
          license='Apache 2.0',
          packages=find_packages(),
          package_data={'server': ['py.typed']},
          entry_points={},
          include_package_data=True,
          install_requires=['cherrypy'],
          extras_require={
              'ldap': ['python-ldap']
          },
          dependency_links=[],
          classifiers=[
              'Development Status :: 3 - Alpha',
              'Environment :: Web Environment',
              'Intended Audience :: Developers',
              'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
              'License :: OSI Approved :: Apache Software License',
              'Operating System :: OS Independent',
              'Programming Language :: Python :: 3'
          ],
          keywords='gros server framework authentication templates')

if __name__ == '__main__':
    main()
