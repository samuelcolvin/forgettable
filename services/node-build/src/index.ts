import * as logfire from '@pydantic/logfire-node';
import app from './server.js';

const port = Number(process.env.PORT) || 3000;

app.listen(port, () => {
  logfire.info('node-build server running on {port}', { port, url: `http://localhost:${port}` });
});
