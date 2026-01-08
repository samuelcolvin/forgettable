# Build stage
FROM rust:1.92-alpine3.23 AS builder

RUN apk add --no-cache musl-dev openssl-dev openssl-libs-static pkgconfig

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
FROM alpine:3.23

RUN apk add --no-cache ca-certificates

WORKDIR /app

COPY --from=builder /app/target/release/rust-db ./rust-db

ENV PORT=3001

EXPOSE 3001

CMD ["./rust-db"]
