# rust-db

A simple key-value store backed by PostgreSQL. All operations are namespaced to projects (UUIDs), and entries store binary content with mime-types.

## Example

```bash
# Store a key (project is auto-created if needed)
curl -X POST http://localhost:3002/project/550e8400-e29b-41d4-a716-446655440000/hello.txt \
  -H "Content-Type: text/plain" \
  -d "Hello, World!"

# Get a key
curl http://localhost:3002/project/550e8400-e29b-41d4-a716-446655440000/get/hello.txt
```
