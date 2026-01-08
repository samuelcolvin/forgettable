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
User Browser → Go Main (port 3000)
                    ↓
              /{uuid}/create or /{uuid}/edit
                    ↓
              Python Agent (port 3001)
                    ↓
              Pydantic-AI agent (Claude)
              Uses tools: create_file, edit_file, delete_file
                    ↓
              Validates via Node Build (port 3002)
                    ↓
              Returns to Go Main
                    ↓
              Stores in Rust DB (port 3003)
                    ↓
              Serves app at /{uuid}/view
```

The Go Main service is the user-facing entry point. It forwards generation requests to Python Agent, stores results in Rust DB, and serves the generated apps.

## Common Commands

### Go Main (`services/go-main`)
```bash
go run .            # Run the server (port 3000)
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
pnpm dev            # Run dev server with tsx (includes logfire instrumentation)
pnpm build          # Compile TypeScript
pnpm start          # Run compiled server
pnpm typecheck      # Type check without emitting
pytest test_node_build.py              # Run all tests
pytest test_node_build.py -k test_name # Run single test
```

### Rust DB (`services/rust-db`)
```bash
make start-pg       # Start PostgreSQL with Docker
DATABASE_URL=postgresql://postgres@localhost:5432 make create-schema  # Create DB schema
make format         # Format with cargo +nightly fmt
DATABASE_URL=postgresql://postgres@localhost:5432 make lint  # Lint with clippy (requires DB for SQLx verification)
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
- Port 3000, main user-facing web application
- Endpoints:
  - `GET /` - Redirect to `/{uuid}` (new project)
  - `GET /{uuid}` - Main app page (TODO: React chat UI)
  - `GET /{uuid}/view` - Serve generated app
  - `GET /{uuid}/view/assets/*` - Serve compiled assets
  - `POST /{uuid}/create` - Create app via Python Agent, store in Rust DB
  - `POST /{uuid}/edit` - Edit app via Python Agent, update Rust DB
  - `GET /health` - Health check
- Uses Chi router, stores files with `source/` and `compiled/` key prefixes in Rust DB
- Observability via OpenTelemetry to logfire (requires `LOGFIRE_TOKEN`)
- Environment: `PORT`, `PYTHON_AGENT_URL`, `RUST_DB_URL`, `LOGFIRE_TOKEN`

### Python Agent
- Port 3001, endpoints: `POST /apps` (create), `POST /apps/edit` (edit)
- Uses Claude Sonnet 4.5 via pydantic-ai-slim
- Agent tools operate on in-memory file dict, not filesystem
- Python 3.14+, strict type checking with basedpyright
- Observability via logfire

### Node Build
- Port 3002, endpoints: `POST /build`, `GET /health`
- Tech stack: Express 5 (HTTP), Zod (validation), Vite (bundler)
- Source files: `index.ts` (entry), `server.ts` (routes), `schema.ts` (Zod schemas), `build.ts` (Vite build logic), `instrumentation.ts` (logfire)
- Build flow: POST files dict → write to temp dir → run Vite build → return compiled assets
- React/React-DOM aliased to server's node_modules to prevent version conflicts
- ESM throughout, TypeScript strict mode

### Rust DB
- Port 3003, PostgreSQL backend with SQLx compile-time query verification
- Tech stack: Axum 0.8, SQLx, logfire (OpenTelemetry)
- Source files: `main.rs` (entry), `config.rs` (env config), `routes.rs` (URL mapping), `handlers/entries.rs` (request handlers), `models.rs` (data structs), `error.rs` (AppError)
- Endpoints namespaced by project UUID: `/project/{project}/get/{key}`, `/project/{project}/list/`, `POST /project/{project}/{key}`, `DELETE /project/{project}/{key}`
- Database: Two tables - `projects` (id, created_at) and `entries` (id, project_id, key, mime_type, content, timestamps)
- Projects auto-created on first entry store

## Code Standards

- **Go**: Chi router, golangci-lint v2, gofmt formatting
- **Python**: Line length 120, single quotes inline, double quotes multiline, strict typing
- **TypeScript**: Strict mode, ES2022, ESM modules only
- **Rust**: Edition 2024, clippy pedantic with some allowances
