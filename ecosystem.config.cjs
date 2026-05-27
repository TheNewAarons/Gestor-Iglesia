const path = require('path');
const ROOT = __dirname;

module.exports = {
  apps: [
    {
      name: 'iglesia-backend',
      script: path.join(ROOT, 'scripts/start-backend.sh'),
      interpreter: '/bin/bash',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: path.join(ROOT, 'logs/backend-error.log'),
      out_file: path.join(ROOT, 'logs/backend-out.log'),
    },
    {
      name: 'iglesia-whatsapp',
      cwd: path.join(ROOT, 'whatsapp-service'),
      script: 'src/index.js',
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      error_file: path.join(ROOT, 'logs/whatsapp-error.log'),
      out_file: path.join(ROOT, 'logs/whatsapp-out.log'),
    },
    {
      name: 'iglesia-frontend',
      cwd: path.join(ROOT, 'frontend'),
      script: path.join(ROOT, 'frontend/node_modules/.bin/astro'),
      args: 'preview --host --port 4321',
      autorestart: true,
      watch: false,
      error_file: path.join(ROOT, 'logs/frontend-error.log'),
      out_file: path.join(ROOT, 'logs/frontend-out.log'),
    },
  ],
};
