import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  output: 'static',
  base: '/',
  build: {
    format: 'file',
  },
  integrations: [tailwind()],
});
