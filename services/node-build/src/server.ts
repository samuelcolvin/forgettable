import express, { Express, NextFunction, Request, Response } from 'express';
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
    res.status(400).send(parsed.error.message);
    return;
  }

  try {
    const output = await buildProject(parsed.data);
    res.status(200).json(output);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    res.status(400).send(message);
  }
});

app.get('/health', (_req: Request, res: Response) => {
  res.send('OK');
});

export default app;
