#!/usr/bin/env python
"""
Package setup script.
"""

from setuptools import setup, find_packages

def main():
    """
    Setup the package.
    """

    setup(name='gros-server',
          version='0.0.2',
          description='Grip on Software server framework',
          long_description='''Web application framework for building
authenticated services, with templating to avoid vulnerabilities.''',
          author='Leon Helwerda',
          author_email='l.s.helwerda@liacs.leidenuniv.nl',
          url='',
          license='',
          packages=find_packages(),
          entry_points={},
          include_package_data=True,
          install_requires=['cherrypy'],
          extras_require={
              'ldap': ['python-ldap']
          },
          dependency_links=[],
          classifiers=[],
          keywords=[])

if __name__ == '__main__':
    main()
