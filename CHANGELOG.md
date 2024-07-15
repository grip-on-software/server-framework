# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) 
and we adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2024-07-15

### Added

- Unit tests for `application`, `authentication` base, LDAP and Open scheme, 
  `bootstrap`, `dispatcher` and `template` modules added.

### Changed

- Package is now a `pyproject.toml` project instead of using `setup.py`.

### Fixed

- Open authentication scheme now rejects login if the no username is filled in.

## [0.0.3] - 2024-06-11

### Added

- Initial release of version as used during the GROS research project. 
  Previously, versions were rolling releases based on Git commits.
- Dispatcher for host validation added.
- Bootstrap: Allow applications to set their own identifier in the cookie name.
- Authentication: Allowlist for users outside of group added.

### Fixed

- Do not provide session cookie to JavaScript.
- Increase default expiry of the cookies and add argument to alter it
- LDAP authentication scheme encode credentials input from UTF-8 for query.

### Removed

- Support for Python 2.7 dropped.

[Unreleased]: 
https://github.com/grip-on-software/server-framework/compare/v1.0.0...HEAD
[1.0.0]: 
https://github.com/grip-on-software/server-framework/compare/v0.0.3...v1.0.0
[0.0.3]: 
https://github.com/grip-on-software/server-framework/releases/tag/v0.0.3
