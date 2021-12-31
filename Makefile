#* Installation
.PHONY: install
install:
	poetry lock -n && poetry export --without-hashes > requirements.txt
	poetry install -n

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit install

#* Formatters
.PHONY: codestyle
codestyle:
	poetry run pyupgrade --exit-zero-even-if-changed --py38-plus **/*.py
	poetry run isort --settings-path pyproject.toml ./
	poetry run black --config pyproject.toml ./

.PHONY: formatting
formatting: codestyle

.PHONY: pre-commit
pre-commit:
	poetry run pre-commit run --all-files


.PHONY: check-codestyle
check-codestyle:
	poetry run isort --diff --check-only --settings-path pyproject.toml ./
	poetry run black --diff --check --config pyproject.toml ./

check-formatting: check-codestyle

.PHONY: tests
tests:
	poetry run pytest --cov-report term-missing --cov=gurun tests/

.PHONY: lint
lint: tests check-codestyle

#* Cleaning
.PHONY: remove-pycache
remove-pycache:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: remove-build
remove-build:
	rm -rf build/

.PHONY: clean
clean: pycache-remove build-remove
