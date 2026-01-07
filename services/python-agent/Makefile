.PHONY: format
format: ## Format Python code with ruff
	uv run ruff format
	uv run ruff check --fix --fix-only

.PHONY: lint
lint: ## Lint Python code with ruff and basedpyright
	uv run ruff format --check
	uv run ruff check
	uv run basedpyright

.PHONY: test
test: ## Run tests with QUICK mode (uses Sonnet 4.5 for speed, skips validation endpoint)
	QUICK=1 SKIP_VALIDATION=1 uv run uvicorn src.server:app --host 127.0.0.1 --port 8000 & \
	SERVER_PID=$$!; \
	sleep 2; \
	uv run pytest test_python_agent.py -v; \
	TEST_EXIT=$$?; \
	kill $$SERVER_PID 2>/dev/null; \
	exit $$TEST_EXIT
