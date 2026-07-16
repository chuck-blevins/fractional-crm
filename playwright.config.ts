import { defineConfig } from '@playwright/test'

/** Playwright e2e config. Tests live in `e2e/`; assume the app on :3000. */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  use: { baseURL: 'http://localhost:3000' },
})
