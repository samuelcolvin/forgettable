import * as logfire from '@pydantic/logfire-node';

logfire.configure({
  serviceName: 'node-build',
  serviceVersion: '1.0.0',
  distributedTracing: true,
});
