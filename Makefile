.PHONY: help
# Put it first so that "make" without argument is like "make help"
# Adapted from:
# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## List Makefile targets.
	$(info Makefile documentation)
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}'

clean: ## Remove temp build/cache files and directories.
	rm --recursive --force ./dist
	rm --recursive --force ./build
	rm --recursive --force ./*.egg-info
	rm --recursive --force ./**/__pycache__/
	rm --recursive --force .ruff_cache/
	rm --recursive --force .pytest_cache/

test: ## Run Python unit tests.
	poetry run pytest

lint: ## Run static analysis tools.
	poetry run ruff check --fix pysudoers/
	poetry run ruff check --fix tests/
	poetry run pyright pysudoers/ tests/

format: ## Autoformat code/yaml/markdown.
	poetry run ruff format ./ pysudoers/ tests/
	prettier --write .

ci: format lint test ## Run all tests required by CI to merge.
