import { randomUUID } from 'node:crypto';
import * as fs from 'node:fs/promises';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { build } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import * as logfire from '@pydantic/logfire-node';
import type { BuildRequest, BuildOutput, BuildResponse } from './schema.js';

const execFileAsync = promisify(execFile);

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SERVER_ROOT = path.resolve(__dirname, '..');
const SHADCN_DIR = path.join(SERVER_ROOT, 'shadcn');

/**
 * Recursively copy a directory to a destination.
 */
async function copyDir(src: string, dest: string): Promise<void> {
  await fs.mkdir(dest, { recursive: true });
  const entries = await fs.readdir(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      await copyDir(srcPath, destPath);
    } else {
      await fs.copyFile(srcPath, destPath);
    }
  }
}

/**
 * Run biome check with auto-fix on user-provided files.
 * Returns null on success, or plain text diagnostics on failure.
 */
async function runBiomeCheck(tempDir: string, inputFiles: string[]): Promise<string | null> {
  const filesToCheck = inputFiles.filter((f) => /\.(tsx?|jsx?)$/.test(f))

  if (filesToCheck.length === 0) return null

  const biomePath = path.join(SERVER_ROOT, 'node_modules/.bin/biome')
  try {
    await execFileAsync(
      biomePath,
      [
        'check',
        '--write',
        '--config-path',
        SERVER_ROOT,
        '--vcs-use-ignore-file=false',
        ...filesToCheck.map((f) => path.join(tempDir, f)),
      ],
      { cwd: tempDir },
    )
    return null // Success - no errors
  } catch (err: unknown) {
    // Non-zero exit = errors remain after auto-fix
    // Biome outputs diagnostics to stdout, summary to stderr
    const execErr = err as { stdout?: string; stderr?: string }
    const output = [execErr.stdout, execErr.stderr].filter(Boolean).join('\n')
    return output || 'Biome check failed'
  }
}

/**
 * Read source files back from temp directory (may have been modified by biome).
 */
async function readSourceFiles(tempDir: string, inputFiles: string[]): Promise<Record<string, string>> {
  const source: Record<string, string> = {}
  for (const file of inputFiles) {
    source[file] = await fs.readFile(path.join(tempDir, file), 'utf-8')
  }
  return source
}

export async function buildProject(request: BuildRequest): Promise<BuildResponse> {
  const buildId = randomUUID();
  const tempDir = path.join(SERVER_ROOT, `tmp_build_${buildId}`);
  const distDir = path.join(tempDir, 'dist');

  return await logfire.span('buildProject', {
    attributes: { buildId },
    callback: async () => {
      // Create temp directory and write input files
      await logfire.span('write input files', {
        callback: async () => {
          await fs.mkdir(tempDir, { recursive: true });

          // Copy shadcn components and utilities to temp directory
          await copyDir(SHADCN_DIR, path.join(tempDir, 'shadcn'));

          for (const [filePath, content] of Object.entries(request.files)) {
            const fullPath = path.join(tempDir, filePath);
            await fs.mkdir(path.dirname(fullPath), { recursive: true });
            await fs.writeFile(fullPath, content, 'utf-8');
          }

          // Generate main.tsx entry point that imports App from ./app
          const mainTsx = `import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './shadcn/globals.css';
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
        },
      });

      // Run biome check with auto-fix on user-provided files
      const inputFiles = Object.keys(request.files)
      const biomeError = await logfire.span('biome check', {
        callback: async () => runBiomeCheck(tempDir, inputFiles),
      })

      // Read source files back (may have been modified by biome)
      const source = await readSourceFiles(tempDir, inputFiles)

      if (biomeError) {
        throw new Error(biomeError)
      }

      // Run Vite build programmatically
      await logfire.span('vite build', {
        callback: async () => {
          const nm = (pkg: string) => path.join(SERVER_ROOT, 'node_modules', pkg);
          await build({
            root: tempDir,
            configFile: false,
            logLevel: 'error',
            plugins: [react(), tailwindcss()],
            resolve: {
              alias: [
                // React aliases
                { find: 'react', replacement: nm('react') },
                { find: 'react-dom', replacement: nm('react-dom') },
                { find: 'react/jsx-runtime', replacement: nm('react/jsx-runtime') },
                { find: 'react/jsx-dev-runtime', replacement: nm('react/jsx-dev-runtime') },
                // Tailwind CSS
                { find: 'tailwindcss', replacement: nm('tailwindcss/index.css') },
                // shadcn path alias - maps 'shadcn/...' to temp dir
                { find: /^shadcn\/(.*)$/, replacement: `${path.join(tempDir, 'shadcn')}/$1` },
                // @ alias for user code
                { find: /^@\/(.*)$/, replacement: `${tempDir}/$1` },
                // shadcn utility dependencies
                { find: 'class-variance-authority', replacement: nm('class-variance-authority') },
                { find: 'clsx', replacement: nm('clsx') },
                { find: 'tailwind-merge', replacement: nm('tailwind-merge') },
                { find: 'lucide-react', replacement: nm('lucide-react') },
                // Radix UI primitives
                { find: '@radix-ui/react-accordion', replacement: nm('@radix-ui/react-accordion') },
                { find: '@radix-ui/react-alert-dialog', replacement: nm('@radix-ui/react-alert-dialog') },
                { find: '@radix-ui/react-avatar', replacement: nm('@radix-ui/react-avatar') },
                { find: '@radix-ui/react-checkbox', replacement: nm('@radix-ui/react-checkbox') },
                { find: '@radix-ui/react-dialog', replacement: nm('@radix-ui/react-dialog') },
                { find: '@radix-ui/react-dropdown-menu', replacement: nm('@radix-ui/react-dropdown-menu') },
                { find: '@radix-ui/react-label', replacement: nm('@radix-ui/react-label') },
                { find: '@radix-ui/react-popover', replacement: nm('@radix-ui/react-popover') },
                { find: '@radix-ui/react-progress', replacement: nm('@radix-ui/react-progress') },
                { find: '@radix-ui/react-scroll-area', replacement: nm('@radix-ui/react-scroll-area') },
                { find: '@radix-ui/react-select', replacement: nm('@radix-ui/react-select') },
                { find: '@radix-ui/react-separator', replacement: nm('@radix-ui/react-separator') },
                { find: '@radix-ui/react-slot', replacement: nm('@radix-ui/react-slot') },
                { find: '@radix-ui/react-switch', replacement: nm('@radix-ui/react-switch') },
                { find: '@radix-ui/react-tabs', replacement: nm('@radix-ui/react-tabs') },
                { find: '@radix-ui/react-tooltip', replacement: nm('@radix-ui/react-tooltip') },
              ],
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
        },
      });

      // Read output files from dist/
      const compiled: BuildOutput = await logfire.span('read output files', {
        callback: async () => {
          const result: BuildOutput = {};

          // Read index.html
          const indexHtmlPath = path.join(distDir, 'index.html');
          result['index.html'] = await fs.readFile(indexHtmlPath, 'utf-8');

          // Read assets from dist/assets/
          const assetsDir = path.join(distDir, 'assets');
          try {
            const files = await fs.readdir(assetsDir);
            for (const file of files) {
              const filePath = path.join(assetsDir, file);
              const stat = await fs.stat(filePath);
              if (stat.isFile()) {
                const content = await fs.readFile(filePath, 'utf-8');
                result[`assets/${file}`] = content;
              }
            }
          } catch (err) {
            // assets dir might not exist if build failed silently
            throw new Error('Build produced no output files');
          }

          if (Object.keys(result).length <= 1) {
            throw new Error('Build produced no output files');
          }

          return result;
        },
      });

      return { compiled, source };
    },
  });
}
