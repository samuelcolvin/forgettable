# Build stage
FROM golang:1.25-alpine3.23 AS builder

WORKDIR /app

# Copy dependency files for caching
COPY go.mod go.sum ./
RUN go mod download

# Copy source and build
COPY *.go *.html ./
RUN CGO_ENABLED=0 GOOS=linux go build -o go-main .

# Runtime stage
FROM alpine:3.23

RUN apk --no-cache add ca-certificates

WORKDIR /app

COPY --from=builder /app/go-main ./go-main

ENV PORT=3000

EXPOSE 3000

CMD ["./go-main"]
