# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Forgettable is a multi-service system for AI-assisted React application generation. It consists of three services that work together:

1. **Python Agent** (`services/python-agent`) - FastAPI server with Pydantic-AI agent that uses Claude to generate React apps
2. **Node Build** (`services/node-build`) - Build-as-a-service that compiles React/TypeScript apps using Vite
3. **Rust DB** (`services/rust-db`) - Key-value store backed by PostgreSQL with project-based namespacing

## Architecture Flow

```
User Request → Python Agent (port 8000)
                    ↓
              Pydantic-AI agent (Claude)
              Uses tools: create_file, edit_file, delete_file
                    ↓
              Validates via Node Build (port 3000)
                    ↓
              Returns source files + compiled assets
```

The Python agent receives prompts, orchestrates file generation through Claude, validates builds via the Node service, and returns both source and compiled output.

## Common Commands

### Python Agent (`services/python-agent`)
```bash
make format         # Format with ruff
make lint           # Lint with ruff & basedpyright
make test           # Run tests (auto-starts server, uses QUICK=1 SKIP_VALIDATION=1)
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

## Service Details

### Python Agent
- Port 8000, endpoints: `POST /apps` (create), `POST /apps/edit` (edit)
- Uses Claude Opus 4.5 (or Sonnet 4.5 with QUICK env var)
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

- **Python**: Line length 120, single quotes inline, double quotes multiline, strict typing
- **TypeScript**: Strict mode, ES2022, ESM modules only
- **Rust**: Edition 2024, clippy pedantic with some allowances
