import { test, expect } from "@playwright/test";

/** 收集 console.error；过滤后端未启动时的 /api 代理 500（smoke 不测真实 API） */
function trackConsoleErrors(page: import("@playwright/test").Page): string[] {
  const errors: string[] = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      errors.push(msg.text());
    }
  });
  return errors;
}

function unexpectedConsoleErrors(errors: string[]): string[] {
  return errors.filter(
    (e) =>
      !/Failed to load resource: the server responded with a status of 500/.test(e),
  );
}

test.describe("smoke", () => {
  test("homepage loads without console errors", async ({ page }) => {
    const errors = trackConsoleErrors(page);

    await page.goto("/");
    await expect(page.locator("h1")).toContainText("audiobook-cleaner-lab");
    await expect(page.locator(".badge")).toContainText("Review");

    expect(unexpectedConsoleErrors(errors), `console errors:\n${errors.join("\n")}`).toEqual([]);
  });

  test("review alias route loads review home", async ({ page }) => {
    const errors = trackConsoleErrors(page);
    const response = await page.goto("/review");

    expect(response?.status() ?? 0).toBeLessThan(500);
    await expect(page.locator(".import-guide")).toBeVisible();
    await expect(page.getByRole("button", { name: "保存 Review & cut_plan" })).toBeVisible({
      timeout: 15_000,
    });

    expect(unexpectedConsoleErrors(errors), `console errors:\n${errors.join("\n")}`).toEqual([]);
  });

  for (const path of ["/admin", "/workbench", "/preview"]) {
    test(`planned route ${path} shows planning notice`, async ({ page }) => {
      const errors = trackConsoleErrors(page);
      const response = await page.goto(path);

      expect(response?.status() ?? 0).toBeLessThan(500);
      await expect(page.locator(".planned-page")).toBeVisible();
      await expect(page.locator(".planned-badge")).toContainText("规划中");

      expect(
        unexpectedConsoleErrors(errors),
        `console errors on ${path}:\n${errors.join("\n")}`,
      ).toEqual([]);
    });
  }

  test("unknown route shows 404 notice", async ({ page }) => {
    await page.goto("/does-not-exist");
    await expect(page.locator(".planned-page")).toBeVisible();
    await expect(page.locator(".planned-badge")).toContainText("404");
  });
});
