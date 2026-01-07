import { randomUUID } from 'node:crypto';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import type { BuildRequest, BuildOutput } from './schema.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SERVER_ROOT = path.resolve(__dirname, '..');

export async function buildProject(request: BuildRequest): Promise<BuildOutput> {
  const buildId = randomUUID();
  const tempDir = path.join(SERVER_ROOT, `tmp_build_${buildId}`);
  const distDir = path.join(tempDir, 'dist');

  {
    // Create temp directory
    await fs.mkdir(tempDir, { recursive: true });

    // Write all input files
    for (const [filePath, content] of Object.entries(request.files)) {
      const fullPath = path.join(tempDir, filePath);
      await fs.mkdir(path.dirname(fullPath), { recursive: true });
      await fs.writeFile(fullPath, content, 'utf-8');
    }

    // Generate main.tsx entry point that imports App from ./app
    const mainTsx = `import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import 'tailwindcss';
import App from './app';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
`;
    await fs.writeFile(path.join(tempDir, 'main.tsx'), mainTsx, 'utf-8');

    // Generate index.html that references main.tsx
    const indexHtml = `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Build</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/main.tsx"></script>
  </body>
</html>`;
    await fs.writeFile(path.join(tempDir, 'index.html'), indexHtml, 'utf-8');

    // Run Vite build programmatically
    await build({
      root: tempDir,
      configFile: false,
      logLevel: 'error',
      plugins: [react(), tailwindcss()],
      resolve: {
        alias: {
          react: path.join(SERVER_ROOT, 'node_modules/react'),
          'react-dom': path.join(SERVER_ROOT, 'node_modules/react-dom'),
          'react/jsx-runtime': path.join(SERVER_ROOT, 'node_modules/react/jsx-runtime'),
          'react/jsx-dev-runtime': path.join(SERVER_ROOT, 'node_modules/react/jsx-dev-runtime'),
          // Point to the CSS file directly for the @import "tailwindcss" pattern
          tailwindcss: path.join(SERVER_ROOT, 'node_modules/tailwindcss/index.css'),
        },
      },
      build: {
        outDir: 'dist',
        sourcemap: true,
        emptyOutDir: true,
        rollupOptions: {
          input: path.join(tempDir, 'index.html'),
        },
      },
      cacheDir: path.join(SERVER_ROOT, 'node_modules/.vite'),
    });

    // Read output files from dist/
    const output: BuildOutput = {};

    // Read index.html
    const indexHtmlPath = path.join(distDir, 'index.html');
    output['index.html'] = await fs.readFile(indexHtmlPath, 'utf-8');

    // Read assets from dist/assets/
    const assetsDir = path.join(distDir, 'assets');
    try {
      const files = await fs.readdir(assetsDir);
      for (const file of files) {
        const filePath = path.join(assetsDir, file);
        const stat = await fs.stat(filePath);
        if (stat.isFile()) {
          const content = await fs.readFile(filePath, 'utf-8');
          output[`assets/${file}`] = content;
        }
      }
    } catch (err) {
      // assets dir might not exist if build failed silently
      throw new Error('Build produced no output files');
    }

    if (Object.keys(output).length <= 1) {
      throw new Error('Build produced no output files');
    }

    return output;
  }
}
