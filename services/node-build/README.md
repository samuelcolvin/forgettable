# node-build

A build-as-a-service server that compiles React/TypeScript applications on-demand using Vite. Send source files as JSON, get bundled output back.

## Example

```bash
cat > request.json << 'EOF'
{
  "entryPoint": "src/main.tsx",
  "files": {
    "src/main.tsx": "import ReactDOM from \"react-dom/client\";\nfunction App() { return <div>Hello World</div>; }\nReactDOM.createRoot(document.getElementById(\"root\")!).render(<App />);"
  }
}
EOF

curl -X POST http://localhost:3000/build -H "Content-Type: application/json" -d @request.json
```
