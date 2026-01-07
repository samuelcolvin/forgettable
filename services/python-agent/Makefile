
.PHONY: format
format: ## Format Python code with ruff
	uv run ruff format
	uv run ruff check --fix --fix-only

.PHONY: lint
lint: ## Lint Python code with ruff and basedpyright
	uv run ruff format --check
	uv run ruff check
	uv run basedpyright
