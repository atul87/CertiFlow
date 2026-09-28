import { expect, test } from "@playwright/test";

test.describe("marketing site", () => {
    test("renders the landing page and core navigation", async ({ page }, testInfo) => {
        test.skip(testInfo.project.name === "mobile", "Desktop navigation links are hidden on mobile.");
        await page.goto("/");
        await page.waitForLoadState("networkidle");

        await expect(page).toHaveTitle(/CertiFlow/i);
        await expect(
            page.getByRole("heading", {
                name: /Create hundreds of personalized certificates/i,
            }),
        ).toBeVisible();
        await expect(page.getByRole("link", { name: /Create Certificates Free/i }).first()).toBeVisible();
        await expect(page.getByRole("link", { name: /Log in/i })).toHaveAttribute("href", "/login");

        await page.getByRole("navigation", { name: "Main Navigation" }).getByRole("link", { name: "Pricing" }).click();
        await expect(page.locator("#pricing")).toBeInViewport();

        await page.getByRole("button", { name: /^Demo$/ }).click();
        await expect(page.getByRole("heading", { name: /60-Second Product Walkthrough/i })).toBeVisible();
        await page.getByRole("button", { name: "Close demo" }).click();
    });

    test("advances the interactive demo and switches recipients", async ({ page }) => {
        await page.goto("/#demo");
        await page.waitForLoadState("networkidle");

        await expect(page.getByRole("heading", { name: "Upload CSV" })).toBeVisible();
        await page.getByRole("button", { name: /Next Step/i }).click();
        await expect(page.getByRole("heading", { name: "Connect Fields" })).toBeVisible();
        await page.getByRole("button", { name: /Next Step/i }).click();
        await expect(page.getByRole("heading", { name: "Certificate Preview" })).toBeVisible();
        await page.getByRole("button", { name: "Rahul", exact: true }).click();
        await expect(page.locator("#demo").getByRole("heading", { name: "Rahul Sharma" })).toBeVisible();
    });

    test("opens and closes the mobile navigation", async ({ page }, testInfo) => {
        test.skip(testInfo.project.name !== "mobile", "Mobile navigation is only rendered at the mobile viewport.");
        await page.goto("/");
        await page.waitForLoadState("networkidle");

        await page.getByRole("button", { name: "Open menu" }).click();
        await expect(page.getByRole("link", { name: "Interactive Demo" })).toBeVisible();
        await page.locator(".fixed.inset-0").getByRole("button", { name: "Close menu" }).click();
        await expect(page.getByRole("link", { name: "Interactive Demo" })).not.toBeVisible();
    });

    test("expands an FAQ item", async ({ page }) => {
        await page.goto("/#faq");
        await page.waitForLoadState("networkidle");

        const faq = page.getByRole("button", { name: /Can I upload my own design/i });
        await expect(faq).toHaveAttribute("aria-expanded", "false");
        await faq.click();
        await expect(faq).toHaveAttribute("aria-expanded", "true");
        await expect(page.getByText(/Figma, Canva, Illustrator/i)).toBeVisible();
    });
});
