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
    await expect(page.locator("h1")).toContainText("audiobook-cleaner-lab Review");
    await expect(page.locator(".badge")).toContainText("MVP");

    expect(unexpectedConsoleErrors(errors), `console errors:\n${errors.join("\n")}`).toEqual([]);
  });

  for (const path of ["/review", "/admin", "/workbench", "/preview"]) {
    test(`optional route ${path} loads without server error`, async ({ page }) => {
      const errors = trackConsoleErrors(page);
      const response = await page.goto(path);

      expect(response?.status() ?? 0).toBeLessThan(500);
      // SPA fallback：未知路由仍应渲染根应用壳
      await expect(page.locator(".app-header")).toBeVisible();

      expect(
        unexpectedConsoleErrors(errors),
        `console errors on ${path}:\n${errors.join("\n")}`,
      ).toEqual([]);
    });
  }
});
