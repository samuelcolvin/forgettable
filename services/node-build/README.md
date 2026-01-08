# node-build

A build-as-a-service server that compiles React/TypeScript applications on-demand using Vite. Send source files as JSON, get bundled output back.

## Example

```bash
http POST :3003/build Content-Type:application/json < services/node-build/example_request.json
```
