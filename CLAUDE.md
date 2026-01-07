# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Forgettable is a multi-service system for AI-assisted React application generation. It consists of four services that work together:

1. **Go Main** (`services/go-main`) - Main web application that coordinates all services, serves the UI, and stores generated apps
2. **Python Agent** (`services/python-agent`) - FastAPI server with Pydantic-AI agent that uses Claude to generate React apps
3. **Node Build** (`services/node-build`) - Build-as-a-service that compiles React/TypeScript apps using Vite
4. **Rust DB** (`services/rust-db`) - Key-value store backed by PostgreSQL with project-based namespacing

## Architecture Flow

```
User Browser → Go Main (port 3002)
                    ↓
              /{uuid}/create or /{uuid}/edit
                    ↓
              Python Agent (port 8000)
                    ↓
              Pydantic-AI agent (Claude)
              Uses tools: create_file, edit_file, delete_file
                    ↓
              Validates via Node Build (port 3000)
                    ↓
              Returns to Go Main
                    ↓
              Stores in Rust DB (port 3001)
                    ↓
              Serves app at /{uuid}/view
```

The Go Main service is the user-facing entry point. It forwards generation requests to Python Agent, stores results in Rust DB, and serves the generated apps.

## Common Commands

### Go Main (`services/go-main`)
```bash
go run .            # Run the server (port 3002)
make lint           # Lint with golangci-lint v2
make format         # Format with gofmt + go mod tidy
pytest test_service.py  # Integration tests
```

### Python Agent (`services/python-agent`)
```bash
make format         # Format with ruff
make lint           # Lint with ruff & basedpyright
make test           # Run tests (auto-starts server, uses SKIP_VALIDATION=1)
```

### Node Build (`services/node-build`)
```bash
pnpm dev            # Run dev server with tsx
pnpm build          # Compile TypeScript
pnpm typecheck      # Type check without emitting
pytest test_node_build.py              # Run all tests
pytest test_node_build.py -k test_name # Run single test
```

### Rust DB (`services/rust-db`)
```bash
make start-pg       # Start PostgreSQL with Docker
make format         # Format with cargo +nightly fmt
make lint           # Lint with clippy
uv run test_service.py  # Integration tests
```

### Root Makefile
```bash
make lint           # Lint all services (py, rs, ts, go)
make format         # Format all services
make lint-go        # Lint Go code only
make format-go      # Format Go code only
```

## Service Details

### Go Main
- Port 3002, main user-facing web application
- Endpoints:
  - `GET /` - Redirect to `/{uuid}` (new project)
  - `GET /{uuid}` - Main app page (TODO: React chat UI)
  - `GET /{uuid}/view` - Serve generated app
  - `GET /{uuid}/view/assets/*` - Serve compiled assets
  - `POST /{uuid}/create` - Create app via Python Agent, store in Rust DB
  - `POST /{uuid}/edit` - Edit app via Python Agent, update Rust DB
  - `GET /health` - Health check
- Uses Chi router, stores files with `source/` and `compiled/` key prefixes in Rust DB
- Environment: `PORT`, `PYTHON_AGENT_URL`, `RUST_DB_URL`

### Python Agent
- Port 8000, endpoints: `POST /apps` (create), `POST /apps/edit` (edit)
- Uses Claude Sonnet 4.5
- Agent tools operate on in-memory file dict, not filesystem
- Python 3.14+, strict type checking with basedpyright

### Node Build
- Port 3000, endpoints: `POST /build`, `GET /health`
- Accepts files dict, creates temp directory, runs Vite build, returns compiled assets
- React/React-DOM aliased to prevent version conflicts

### Rust DB
- Port 3001, PostgreSQL backend with SQLx compile-time query verification
- Endpoints namespaced by project UUID: `/project/{project}/get/{key}`, `/project/{project}/list/`, `POST /project/{project}/{key}`, `DELETE /project/{project}/{key}`
- Projects auto-created on first entry store

## Code Standards

- **Go**: Chi router, golangci-lint v2, gofmt formatting
- **Python**: Line length 120, single quotes inline, double quotes multiline, strict typing
- **TypeScript**: Strict mode, ES2022, ESM modules only
- **Rust**: Edition 2024, clippy pedantic with some allowances
