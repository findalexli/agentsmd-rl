import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['code/core/src/**/*.test.ts'],
    environment: 'node',
    testTimeout: 30000,
    silent: false,
    clearMocks: true,
    mockReset: true,
    restoreMocks: true,
  },
});
