You're in a fresh node project using pnpm.

Your task is to build a web server, that takes files (as JSON) as input, and builds them with typescript and react,
then returns either a 200 response with the output files, or 400 with a text response of error details.

The input files should always be typescript and TSX (as well as css etc.).

You should build the react app in a local directory and delete it after the response.

You should build the library app with vite.

The only dependencies which should be available when building the react app should be react, typescript and tailwind.

The inputs will be in the form

```json
{
  "src/main.tsx": "...",
  "src/other.tsx": "...",
  ...
}
```

You should validate the inputs with zod before proceeding. The output format on success should be the same.

Plan this application, look up the docs of all the libaries, you need to confirm you have the right plan.
