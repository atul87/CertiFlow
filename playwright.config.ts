import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
    testDir: "./tests",
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    workers: 2,
    reporter: "list",
    use: {
        baseURL: "http://127.0.0.1:3000",
        trace: "on-first-retry",
    },
    projects: [
        {
            name: "unit",
            testMatch: /tests\/unit\/.*\.spec\.ts/,
        },
        {
            name: "chromium",
            testMatch: /tests\/e2e\/.*\.spec\.ts/,
            use: { ...devices["Desktop Chrome"] },
        },
        {
            name: "mobile",
            testMatch: /tests\/e2e\/.*\.spec\.ts/,
            use: {
                ...devices["Desktop Chrome"],
                viewport: { width: 390, height: 844 },
                isMobile: true,
                hasTouch: true,
            },
        },
    ],
    webServer: {
        command: "npm run dev -- --hostname 127.0.0.1",
        url: "http://127.0.0.1:3000",
        reuseExistingServer: !process.env.CI,
    },
});
