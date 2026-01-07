# Build stage - using nightly for edition 2024 support
FROM rustlang/rust:nightly-bookworm AS builder

WORKDIR /app

# Copy dependency files first for caching
COPY Cargo.toml Cargo.lock ./

# Create dummy src to build dependencies
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
RUN rm -rf src

# Copy actual source and SQLx offline files
COPY src ./src
COPY .sqlx ./.sqlx

# Build with SQLx offline mode
ENV SQLX_OFFLINE=true
RUN touch src/main.rs && cargo build --release

# Runtime stage
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/target/release/rust-db ./rust-db

ENV PORT=3000

EXPOSE 3000

CMD ["./rust-db"]
