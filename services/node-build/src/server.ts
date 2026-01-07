import { Hono } from 'hono';
import { BuildRequestSchema } from './schema.js';
import { buildProject } from './build.js';

const app = new Hono();

app.post('/build', async (c) => {
  let body: unknown;
  try {
    body = await c.req.json();
  } catch {
    return c.text('Invalid JSON body', 400);
  }

  const parsed = BuildRequestSchema.safeParse(body);

  if (!parsed.success) {
    return c.text(parsed.error.message, 400);
  }

  try {
    const output = await buildProject(parsed.data);
    return c.json(output, 200);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return c.text(message, 400);
  }
});

app.get('/health', (c) => {
  return c.text('OK');
});

export default app;
