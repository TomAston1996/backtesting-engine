clean:
	rm -rf dist static service code
	uv clean

install:
	uv venv
	uv sync

format: install
	uv run ruff check . --fix

test: install
	uv run pytest --cov-report=term-missing -vv

audit: install
	uv export --format requirements-txt > requirements.txt \
	&& uvx pip-audit -r requirements.txt \
		--disable-pip \
		--strict \
		--fix \
	&& rm requirements.txt