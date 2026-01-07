# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A key-value database service built with Rust, Axum, and PostgreSQL. All operations are namespaced to a "project" (UUID). Entries have a key (path), mime-type, and binary content.

## Commands

```bash
# Start PostgreSQL with Docker
make start-pg

# Create database schema (requires DATABASE_URL)
DATABASE_URL=postgresql://postgres@localhost:5432 make create-schema

# Format code (uses cargo +nightly fmt)
make format

# Lint with clippy (requires DATABASE_URL for SQLx compile-time query verification)
DATABASE_URL=postgresql://postgres@localhost:5432 make lint

# Format and lint together
DATABASE_URL=postgresql://postgres@localhost:5432 make format-lint

# Run server (default port 3001)
DATABASE_URL=postgresql://postgres@localhost:5432 cargo run

# Run integration tests (requires server running)
uv run test_service.py
```

Note: SQLx uses compile-time query verification, so DATABASE_URL must be set and the database must be accessible for `make lint` to succeed.

## Architecture

- `src/main.rs` - Entry point, initializes tracing, DB pool, and starts Axum server
- `src/config.rs` - Configuration from environment (DATABASE_URL required, PORT optional)
- `src/routes.rs` - Route definitions mapping URLs to handlers
- `src/handlers/` - Request handlers for entries
- `src/models.rs` - Data structures (Entry, KeyInfo)
- `src/error.rs` - AppError enum with automatic HTTP status mapping via IntoResponse

## API Endpoints

- `GET /project/{project}/get/{key}` - Get entry content
- `GET /project/{project}/list/{prefix}` - List entries by prefix
- `GET /project/{project}/list/` - List all entries
- `POST /project/{project}/{key}` - Store entry (auto-creates project if needed, Content-Type header sets mime-type)
- `DELETE /project/{project}/{key}` - Delete entry

Projects are auto-created on first store - just use any UUID.

## Database

Two tables: `projects` (id, created_at) and `entries` (id, project_id, key, mime_type, content, timestamps). See `schema.sql`.
