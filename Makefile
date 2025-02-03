.PHONY: all test run lint clean

### Default target(s)
all: run

### Perform static analysis
lint:
	uv run ruff check --select I --fix .
	uv run ruff format .
	uv run ruff check . --fix

### Run the project
run: lint
	@echo "\n#\n# Stat\n#"
	uv run pbcli stat
	@echo "\n#\n# Tags\n#"
	uv run pbcli tags
	@echo "\n#\n# Recent\n#"
	uv run pbcli recent -c 2
	@echo "\n#\n# ls\n#"
	uv run pbcli ls --tag=cheatsheet
	@echo "\n#\n# All notes\n#"
	uv run pbcli notes

### Run unit tests
test: lint
	uv run pytest -s -v

### Clean up generated files
clean:
	uv clean
	rm -fr .ruff_cache .venv

### Install this tool locally
install:
	uv tool install --upgrade .
