// @ts-check
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
    testDir: './tests/e2e',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: [['list'], ['html', { open: 'never' }]],
    use: {
        baseURL: 'http://127.0.0.1:8000',
        locale: 'en-US',
        timezoneId: 'UTC',
        trace: 'on-first-retry',
    },
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
        {
            name: 'firefox',
            use: { ...devices['Desktop Firefox'] },
        },
        {
            name: 'msedge',
            use: { ...devices['Desktop Edge'], channel: 'msedge' },
        },
    ],
    webServer: {
        command:
            'rm -f db_e2e.sqlite3 && uv run python manage.py migrate && uv run python manage.py buildfixtures && uv run python manage.py runserver --noreload 127.0.0.1:8000',
        url: 'http://127.0.0.1:8000/en/',
        reuseExistingServer: false,
        timeout: 120_000,
        env: {
            DJANGO_SETTINGS_MODULE: 'apps.guide.settings.e2e',
        },
    },
});
