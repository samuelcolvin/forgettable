.PHONY: format
format:  ## Format Rust code with fmt
	@cargo +nightly fmt --version
	cargo +nightly fmt --all

.PHONY: lint
lint:  ## Lint Rust code with clippy
	@cargo clippy --version
	cargo clippy -- -D warnings -A incomplete_features

.PHONY: format-lint
format-lint: format lint ## Format and lint Rust code with fmt and clippy

.PHONY: create-schema
create-schema: ## Create database schema (requires DATABASE_URL)
	psql $(DATABASE_URL) -f schema.sql

.PHONY: start-pg
start-pg: ## Start a PostgreSQL server with docker
	docker run -e POSTGRES_HOST_AUTH_METHOD=trust --rm -it --name pg -p 5432:5432 -d postgres
