import { sentryVitePlugin } from '@sentry/vite-plugin';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig(({ command }) => {
  const isBuild = command === 'build';
  const hasSentryAuthToken = Boolean(process.env.SENTRY_AUTH_TOKEN);

  return {
    plugins: [
      react(),
      // Only upload sourcemaps during CI/production builds.
      ...(isBuild && hasSentryAuthToken
        ? [
            sentryVitePlugin({
              org: process.env.SENTRY_ORG,
              project: process.env.SENTRY_PROJECT,
              telemetry: false,
            }),
          ]
        : []),
    ],
    build: {
      sourcemap: true,
    },
  };
});