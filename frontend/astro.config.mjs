import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import react from '@astrojs/react';

export default defineConfig({
  output: 'static',
  base: '/',
  build: {
    format: 'file',
  },
  integrations: [tailwind(), react()],
});
