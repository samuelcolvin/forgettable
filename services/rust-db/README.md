# rust-db

A simple key-value store backed by PostgreSQL. All operations are namespaced to projects (UUIDs), and entries store binary content with mime-types.

## Example

```bash
# Create a project
curl -X POST localhost:3001/project/new

# Store a key
curl -X POST localhost:3001/project/{project_id}/hello.txt \
  -H "Content-Type: text/plain" \
  -d "Hello, World!"

# Get a key
curl localhost:3001/project/{project_id}/get/hello.txt
```
