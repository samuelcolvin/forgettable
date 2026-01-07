# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A build-as-a-service Node.js server that compiles React/TypeScript applications on-demand. Accepts JSON payloads containing source files and returns bundled output files.

## Commands

```bash
pnpm dev          # Run development server with tsx
pnpm build        # Compile TypeScript to dist/
pnpm start        # Run compiled server
pnpm typecheck    # Type check without emitting

# Tests (Python/pytest)
pytest test_node_build.py           # Run all tests
pytest test_node_build.py -k test_name  # Run single test
```

Server runs on port 3000 (configurable via PORT env var). Tests require the server to be running.

## Architecture

**Tech Stack**: Hono (HTTP framework), Zod (validation), Vite (bundler for client builds)

**Source files** (`src/`):
- `index.ts` - Entry point, starts HTTP server
- `server.ts` - Hono routes: `POST /build` and `GET /health`
- `schema.ts` - Zod schemas for input validation (BuildRequestSchema, BuildOutputSchema)
- `build.ts` - Core build logic using Vite with React and Tailwind plugins

**Build Request Flow**:
1. POST to `/build` with `{ entryPoint: string, files: Record<string, string> }`
2. Validate input with Zod
3. Write files to temp directory (`/tmp/build-{uuid}`)
4. Generate index.html, run Vite build programmatically
5. Return compiled assets as JSON or error (400 status)
6. Clean up temp directory

**Key Details**:
- React/React-DOM are aliased to server's node_modules to prevent version conflicts
- Vite configured with `@vitejs/plugin-react` and `@tailwindcss/vite`
- ESM throughout (package.json `"type": "module"`)
- TypeScript strict mode enabled
