import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  resolve: { alias: { zustand: '/src/vendor/zustand.ts' } },
  plugins: [react()],
  server: { port: 5173 },
  test: { environment: 'jsdom', globals: true, setupFiles: './src/test/setup.ts' },
});
