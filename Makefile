.PHONY: format
format: format-py format-rs format-go ## Format all code

.PHONY: lint
lint: lint-py lint-rs lint-ts lint-go ## Lint all code

.PHONY: format-py
format-py: ## Format Python code with ruff
	uv run ruff format
	uv run ruff check --fix --fix-only

.PHONY: lint-py
lint-py: ## Lint Python code with ruff and basedpyright
	uv run ruff format --check
	uv run ruff check
	uv run basedpyright

.PHONY: format-rs
format-rs: ## Format Rust code with fmt
	@cargo +nightly fmt --version
	cargo +nightly fmt --manifest-path services/rust-db/Cargo.toml --all

.PHONY: lint-rs
lint-rs: ## Lint Rust code with clippy
	@cargo clippy --version
	SQLX_OFFLINE=true cargo clippy --manifest-path services/rust-db/Cargo.toml -- -D warnings -A incomplete_features

# TypeScript targets
.PHONY: lint-ts
lint-ts: ## Lint TypeScript code with tsc
	pnpm --dir services/node-build typecheck

.PHONY: format-go
format-go: ## Format Go code with gofmt
	gofmt -w services/go-main/
	cd services/go-main && go mod tidy

.PHONY: lint-go
lint-go: ## Lint Go code with golangci-lint
	cd services/go-main && go mod tidy -diff
	cd services/go-main && golangci-lint run

.PHONY: create-schema
create-schema: ## Create database schema (requires DATABASE_URL)
	psql $(DATABASE_URL) -f services/rust-db/schema.sql

.PHONY: test
test: ## Run all integration tests against docker-compose (requires services running)
	uv run pytest services

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
