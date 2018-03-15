SRC_PATH := $(CURDIR)/pyxus
MODULE_PATH := $(SRC_PATH)/pyxus
PACKAGE :=pyxus

REQ_FILE_PATH := $(SRC_PATH)/requirements.txt
TEST_REQ_FILE_PATH := $(SRC_PATH)/requirements_extension_tests.txt
VIRTUAL_ENV := $(CURDIR)/venv
DIST := $(CURDIR)/dist
PIP := $(VIRTUAL_ENV)/bin/pip
PYTHON := $(VIRTUAL_ENV)/bin/python
MANAGE := $(PYTHON) $(SRC_PATH)/manage.py
PIP_CACHE := $(CURDIR)/pip-cache
DOC_REQ_FILE_PATH := $(MODULE_PATH)/requirements_documentation.txt
DOC_PATH := $(CURDIR)/docs
DOC_SOURCE_PATH := $(DOC_PATH)/source
DOC_BUILD_PATH := $(DOC_PATH)/build


.PHONY: clean help install lint migrate package run test test-install virtualenv

define HELPTEXT
Makefile usage
 Targets:
 	clean           delete all generated artifacts
 	help            this help
	install         install the dependencies
	lint            lint the code
	migrate         create the migration scripts and run them
	package         package the sources in an installable dist directory
	run             run the server
	test            run the tests
	test-install    install the tests dependencies
	virtualenv      create a virtual env
	doc             generate documentation

endef

export HELPTEXT
help:
	@echo "$$HELPTEXT"

clean:
	-rm -rf $(VIRTUAL_ENV)
	-rm pylint.txt
	-rm -rf $(DIST)
	-rm -rf $(SRC_PATH)/*.egg-info
	-rm -rf $(SRC_PATH)/dist
	-rm -rf $(SRC_PATH)/build

ifdef GITLAB_CACHING
virtualenv_caching_option := --always-copy
pip_caching_option := --cache-dir $(PIP_CACHE)
endif

# Generate `.env` file from sample
.env:
	cp .env.sample .env

install: virtualenv $(REQ_FILE_PATH) .env
	$(PIP) install $(pip_caching_option) -r $(REQ_FILE_PATH)

lint: test-install
	$(VIRTUAL_ENV)/bin/pylint $(MODULE_PATH) -r y

test: install test-install
	$(MANAGE) test $(MODULE_PATH)
	cd $(SRC_PATH) && $(PYTHON) -m unittest discover

test-install: virtualenv $(TEST_REQ_FILE_PATH)
	$(PIP) install $(pip_caching_option) -r $(TEST_REQ_FILE_PATH)

virtualenv:
	test -d $(VIRTUAL_ENV) || virtualenv $(VIRTUAL_ENV) $(virtualenv_caching_option)

doc: install doc-install
	$(MANAGE) test $(MODULE_PATH)
	$(VIRTUAL_ENV)/bin/sphinx-build -b html $(DOC_SOURCE_PATH) $(DOC_BUILD_PATH)

doc-install: virtualenv $(DOC_REQ_FILE_PATH)
	$(PIP) install $(pip_caching_option) -r $(DOC_REQ_FILE_PATH)

package:
	cd $(SRC_PATH) && python setup.py sdist
	cd $(SRC_PATH) && python setup.py bdist_wheel

