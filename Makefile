.PHONY: install clean requirements test retest coverage tox lint ruff mypy format prettier sandbox e2e bundle watch build

# Runs commands in the uv-managed .venv without needing to activate it.
RUN = uv run

default: install

install: clean requirements bundle

clean:
	find src -name '*.pyc' -delete
	find tests -name '*.pyc' -delete
	find . -name '*.egg-info' |xargs rm -rf

requirements:
	yarn install
	uv sync

test:
	$(RUN) pytest --nomigrations --reuse-db tests/

retest:
	$(RUN) pytest --nomigrations --reuse-db tests/ -vvv

coverage:
	$(RUN) pytest --nomigrations --reuse-db tests/ --cov=wagtail_tag_manager --cov-report=term-missing --cov-report=html

tox:
	uvx --with tox-uv tox

lint: ruff mypy

ruff:
	$(RUN) ruff format --check src tests e2e
	$(RUN) ruff check src tests e2e

mypy:
	$(RUN) --with mypy mypy src/ tests/

format: prettier
	$(RUN) ruff check --fix src tests e2e
	$(RUN) ruff format src tests e2e

prettier:
	yarn install
	yarn format

sandbox: requirements bundle
	uv pip install -U -r sandbox/requirements.txt
	rm -rf db.sqlite3
	$(RUN) sandbox/manage.py migrate
	$(RUN) sandbox/manage.py loaddata sandbox/exampledata/users.json
	$(RUN) sandbox/manage.py loaddata sandbox/exampledata/cms.json
	$(RUN) sandbox/manage.py loaddata sandbox/exampledata/default_tags.json
	$(RUN) sandbox/manage.py loaddata sandbox/exampledata/additional_tags.json
	$(RUN) sandbox/manage.py runserver

e2e:
	uv run --group e2e playwright install chromium
	uv run --group e2e pytest e2e -p no:randomly

bundle: prettier
	yarn install --force
	yarn build

watch:
	yarn dev
	yarn watch

build:
	uv build
