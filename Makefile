#* Variables
SHELL := /usr/bin/env bash
PYTHON := python
PWD := `pwd`

#* Docker variables
PROJECT := civit_browser
PROJECT_TITLE := civit-browser
VERSION := latest
PYINSTALLER_ENTRY := $(PROJECT)/__main__.py

#-----------------------------------------------------------------------------------------
# DEV INSTALLATION
#-----------------------------------------------------------------------------------------
.PHONY: install-poetry
install-poetry: ## Download and install Poetry
	curl -sSL https://install.python-poetry.org | $(PYTHON) -

.PHONY: uninstall-poetry
uninstall-poetry: ## Uninstall Poetry
	curl -sSL https://install.python-poetry.org | $(PYTHON) - --uninstall

.PHONY: install-pre-commit-hooks
install-pre-commit-hooks: ## Install Pre-Commit Git Hooks
	poetry run pre-commit install


#-----------------------------------------------------------------------------------------
# INSTALL/UPDATE DEPENDENCIES/REQUIREMENTS
#-----------------------------------------------------------------------------------------
.PHONY: install
install: ## Install Project Dependecies/Requirements from Poetry
	poetry lock -n && poetry export --without-hashes > requirements.txt
	poetry install -n
	-poetry run mypy --install-types --non-interactive ./

.PHONY: update-dev-deps
update-dev-deps: ## Update dev dependecies to @latest version
	poetry add --group dev  bandit@latest darglint@latest "isort[colors]@latest" mypy@latest pre-commit@latest pydocstyle@latest pylint@latest pytest@latest pyupgrade@latest safety@latest coverage@latest coverage-badge@latest pytest-html@latest pytest-cov@latest
	poetry add --group dev  --allow-prereleases black@latest


#-----------------------------------------------------------------------------------------
# ORIGINAL INSTALLATION HOOKS
#-----------------------------------------------------------------------------------------
.PHONY: poetry-download
poetry-download: install-poetry ## Download and install Poetry

.PHONY: pre-commit-install
pre-commit-install: install-pre-commit-hooks ## Install Pre-Commit Git Hooks


#-----------------------------------------------------------------------------------------
# COMMAND SCRIPTS
#-----------------------------------------------------------------------------------------
.PHONY: format
format:  format-isort format-black format-pyupgrade format-pre-commit ## Format Code

.PHONY: check
check: check-poetry check-isort check-black check-mypy check-docstrings check-security check-pre-commit ## Check Code Formatting

.PHONY: check-docstrings
check-docstrings: check-darglint check-darglint-tests ## Check Code Docstrings

.PHONY: check-security
check: check-safety check-bandit ## Check Code Security

.PHONY: lint
lint: format check ## Lint Code by Formatting and Checking

.PHONY: tests
tests: test ## Run Tests

.PHONY: test
test: test-pytest-coverage ## Check Tests

.PHONY: all
all: clear format check test

.PHONY: clear
clear:
	@clear
#-----------------------------------------------------------------------------------------
# FORMATTING
#-----------------------------------------------------------------------------------------
.PHONY: codestyle
codestyle: format ## Alias for format

.PHONY: format-pyupgrade
format-pyupgrade: ## Apply Formatting via PyUpgrade.
	@echo -e "\n\033[35m### PYUPGRADE ###\033[0m"
	@poetry run pyupgrade

.PHONY: format-isort
format-isort: ## Apply Formatting via ISort.
	@echo -e "\n\033[35m### ISORT ###\033[0m"
	@poetry run isort --settings-path pyproject.toml ./

.PHONY: format-black
format-black: ## Apply Formatting via Black.
	@echo -e "\n\033[35m### BLACK ###\033[0m"
	@poetry run black --config pyproject.toml ./

.PHONY: format-pre-commit
format-pre-commit: ## Run Pre-Commit Hooks
	@echo -e "\n\033[35m### PRE-COMMIT ###\033[0m"
	@poetry run pre-commit run --all-files


#-----------------------------------------------------------------------------------------
# CHECKS & LINTING
#-----------------------------------------------------------------------------------------
.PHONY: check-poetry
check-poetry: ## Check Poetry Configuration.
	@echo -e "\n\033[1m\033[36m### POETRY ###\033[0m"
	@poetry check

.PHONY: check-safety
check-safety: ## Check Safty via Safety.
	@echo -e "\n\033[1m\033[36m### SAFETY ###\033[0m"
	poetry run safety check --short-report

.PHONY: check-bandit
check-bandit: ## Check Securty via Bandit.
	@echo -e "\n\033[1m\033[36m### BANDIT ###\033[0m"
	@poetry run bandit -c ./pyproject.toml -ll --recursive $(PROJECT) tests

.PHONY: check-isort
check-isort: ## Check Formatting via ISort.
	@echo -e "\n\033[1m\033[36m### ISORT ###\033[0m"
	@poetry run isort --diff --check-only --settings-path pyproject.toml ./

.PHONY: check-black
check-black: ## Check Formatting via Black.
	@echo -e "\n\033[1m\033[36m### BLACK ###\033[0m"
	@poetry run black --diff --check --config pyproject.toml ./

.PHONY: check-darglint
check-darglint: ## Check Docstrings via Darglint.
	@echo -e "\n\033[1m\033[36m### DARGLINT: PROJECT ###\033[0m"
	@poetry run darglint --verbosity 2 -z full $(PROJECT)

.PHONY: check-darglint-tests
check-darglint-tests: ## Check Tests Docstrings via Darglint.
	@echo -e "\n\033[1m\033[36m### DARGLINT: TESTS ###\033[0m"
	@poetry run darglint --verbosity 2 -z long tests

.PHONY: check-mypy
check-mypy: ## Check Types via Mypy.
	@echo -e "\n\033[1m\033[36m### MYPY ###\033[0m"
	@poetry run mypy --config-file pyproject.toml ./

.PHONY: check-pre-commit
check-pre-commit: ## Check Pre-Commit Hooks
	@echo -e "\n\033[1m\033[36m### PRE-COMMIT ###\033[0m"
	@poetry run pre-commit run --all-files


#-----------------------------------------------------------------------------------------
# TESTS
#-----------------------------------------------------------------------------------------
.PHONY: test-pytest-coverage
test-pytest-coverage: ## Check Coverage via PyTest. Fails if coverage is below 90%.
	@echo -e "\n\033[1m\033[33m### PYTEST: COVERAGE ###\033[0m"
	@PWD=$(PWD) poetry run pytest -c pyproject.toml --cov-fail-under=90 --cov-report=html --cov-report=xml  --cov=app tests/
	@poetry run coverage-badge -o assets/images/coverage.svg -f
	@printf "\n"

.PHONY: test-pytest
test-pytest: ## Run Tests via PyTest.
	@echo -e "\n\033[1m\033[33m### PYTEST ###\033[0m"
	@PWD=$(PWD) poetry run pytest -c pyproject.toml --no-cov-on-fail --cov-report=html --cov-report=xml  --cov=app tests/
	@poetry run coverage-badge -o assets/images/coverage.svg -f
	@printf "\n"



#-----------------------------------------------------------------------------------------
# ALEMBIC
#-----------------------------------------------------------------------------------------
.PHONY: alembic-init
alembic-init: ## Create Alembic Revision
	@echo -e "\n\033[1m\033[33m### INIT ALEMBIC ###\033[0m"

	# Delete all existing revisions
	rm -rf ./migrations/versions/*

	poetry run alembic revision --autogenerate -m "init"

#-----------------------------------------------------------------------------------------
# BUILD PACKAGE
#-----------------------------------------------------------------------------------------
.PHONY: build-package
build-package: ## Build as Package
	poetry build

.PHONY: bump-version
bump-version: ## Bump Version
	@echo -e "\n\033[1m\033[33m### BUMP VERSION ###\033[0m"
	@poetry version patch
	@git add pyproject.toml
	@git commit -m "Bump version"

#-----------------------------------------------------------------------------------------
# DOCKER
#-----------------------------------------------------------------------------------------
# Example: make docker-build VERSION=latest
# Example: make docker-build PROJECT=some_name VERSION=0.0.1
.PHONY: docker-build
docker-build: ## Build a docker image from Dockerfile
	@echo Building docker $(PROJECT):$(VERSION) ...
	docker build \
		-t $(PROJECT):$(VERSION) . \
		-f ./docker/Dockerfile --no-cache

# Example: make docker-remove VERSION=latest
# Example: make docker-remove PROJECT=some_name VERSION=0.0.1
.PHONY: docker-remove
docker-remove: ## Remove Docker Image
	@echo Removing docker $(PROJECT):$(VERSION) ...
	docker rmi -f $(PROJECT):$(VERSION)


#-----------------------------------------------------------------------------------------
# CLEANUP
#-----------------------------------------------------------------------------------------
.PHONY: cleanup
cleanup: pycache-remove dsstore-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove ## Complete Cleanup

.PHONY: pycache-remove
pycache-remove: ## Clean PyCache
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: dsstore-remove
dsstore-remove: ## Clean .DS_Store
	find . | grep -E ".DS_Store" | xargs rm -rf

.PHONY: mypycache-remove
mypycache-remove: ## Clean .mypy_cache
	find . | grep -E ".mypy_cache" | xargs rm -rf

.PHONY: ipynbcheckpoints-remove
ipynbcheckpoints-remove: ## Clean ipynb_checkpoints
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf

.PHONY: pytestcache-remove
pytestcache-remove: ## Clean pytest_cache
	find . | grep -E ".pytest_cache" | xargs rm -rf

.PHONY: build-remove
build-remove: ## Clean Builds
	rm -rf build/
	rm -rf build_linux/
	rm -rf build_win/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +


#-----------------------------------------------------------------------------------------
# HELP
#-----------------------------------------------------------------------------------------
.PHONY: help
help: ## Self-documented Makefile
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
