# rust-db

A simple key-value store backed by PostgreSQL. All operations are namespaced to projects (UUIDs), and entries store binary content with mime-types.

## Example

```bash
# Store a key (project is auto-created if needed)
http :3002/project/550e8400-e29b-41d4-a716-446655440000/hello.txt Content-Type:text/plain <<< 'hello world'

# Get a key
http :3002/project/550e8400-e29b-41d4-a716-446655440000/get/hello.txt
```
