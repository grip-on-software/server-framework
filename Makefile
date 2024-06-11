MYPY=mypy
PIP=python -m pip
PYLINT=pylint
RM=rm -rf
TWINE=twine

.PHONY: all
all: mypy pylint

.PHONY: release
release: mypy pylint clean build tag push upload

.PHONY: setup
setup:
	$(PIP) install -r requirements.txt

.PHONY: setup_release
setup_release:
	$(PIP) install -r requirements-release.txt

.PHONY: setup_analysis
setup_analysis:
	$(PIP) install -r requirements-analysis.txt

.PHONY: install
install:
	python setup.py install

.PHONY: pylint
pylint:
	$(PYLINT) server setup.py --exit-zero --reports=n \
		--msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
		-d duplicate-code

.PHONY: mypy
mypy:
	$(MYPY) server setup.py \
		--cobertura-xml-report mypy-report \
		--junit-xml mypy-report/TEST-junit.xml \
		--no-incremental --show-traceback

.PHONY: get_version
get_version: get_setup_version get_init_version get_sonar_version get_citation_version
	if [ "${SETUP_VERSION}" != "${INIT_VERSION}" ] || [ "${SETUP_VERSION}" != "${SONAR_VERSION}" ] || [ "${SETUP_VERSION}" != "${CITATION_VERSION}" ]; then \
		echo "Version mismatch"; \
		exit 1; \
	fi
	$(eval VERSION=$(SETUP_VERSION))

.PHONY: get_init_version
get_init_version:
	$(eval INIT_VERSION=v$(shell grep __version__ server/__init__.py | sed -E "s/__version__ = .([0-9.]+)./\\1/"))
	$(info Version in __init__.py: $(INIT_VERSION))
	if [ -z "${INIT_VERSION}" ]; then \
		echo "Could not parse version"; \
		exit 1; \
	fi

.PHONY: get_setup_version
get_setup_version:
	$(eval SETUP_VERSION=v$(shell python setup.py --version))
	$(info Version in setup.py: $(SETUP_VERSION))

.PHONY: get_sonar_version
get_sonar_version:
	$(eval SONAR_VERSION=v$(shell grep projectVersion sonar-project.properties | cut -d= -f2))
	$(info Version in sonar-project.properties: $(SONAR_VERSION))

.PHONY: get_citation_version
get_citation_version:
	$(eval CITATION_VERSION=v$(shell grep "^version:" CITATION.cff | cut -d' ' -f2))
	$(info Version in CITATION.cff: $(CITATION_VERSION))

.PHONY: tag
tag: get_version
	git tag $(VERSION)

.PHONY: build
build:
	python setup.py sdist
	python setup.py bdist_wheel

.PHONY: push
push: get_version
	git push origin $(VERSION)

.PHONY: upload
upload:
	$(TWINE) upload dist/*

.PHONY: clean
clean:
	# Typing coverage and Pylint
	$(RM) .mypy_cache mypy-report/ pylint-report.txt
	# Pip and distribution
	$(RM) src/ build/ dist/ gros-server.egg-info/
