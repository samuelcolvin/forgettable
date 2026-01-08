import express, { Express, NextFunction, Request, Response } from 'express';
import * as logfire from '@pydantic/logfire-node';
import { BuildRequestSchema } from './schema.js';
import { buildProject } from './build.js';

const app: Express = express();

app.use(express.json());

// Handle JSON parse errors
app.use((err: Error, _req: Request, res: Response, next: NextFunction) => {
  if (err instanceof SyntaxError && 'body' in err) {
    res.status(400).send('Invalid JSON body');
    return;
  }
  next(err);
});

app.post('/build', async (req: Request, res: Response) => {
  const parsed = BuildRequestSchema.safeParse(req.body);

  if (!parsed.success) {
    logfire.warning('Invalid build request', { error: parsed.error.message });
    res.status(400).send(parsed.error.message);
    return;
  }

  const fileCount = Object.keys(parsed.data.files).length;
  logfire.info('Build request received for {fileCount} files', { fileCount });

  try {
    const output = await buildProject(parsed.data);
    const outputFileCount = Object.keys(output).length;
    logfire.info('Build succeeded, generated {outputFileCount} files', { outputFileCount });
    res.status(200).json(output);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    logfire.error('Build failed: {message}', { message });
    res.status(400).send(message);
  }
});

app.get('/health', (_req: Request, res: Response) => {
  res.send('OK');
});

export default app;
