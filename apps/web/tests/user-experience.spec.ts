import { test, expect } from "@playwright/test";

test.describe("user experience", () => {
  test("homepage has demo chapter navigation and import guide", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText("audiobook-cleaner-lab");
    await expect(page.getByRole("button", { name: "打开演示章节" })).toBeVisible();
    await expect(page.locator(".step-bar .step.active")).toContainText("Review");
    await expect(page.locator(".import-guide")).toBeVisible();
    await expect(page.locator(".import-guide")).toContainText("import_manifest.py");
  });

  test("export step shows CLI commands", async ({ page }) => {
    await page.goto("/?project_id=book_001&chapter_id=chapter_001");
    await page.getByRole("button", { name: "导出" }).click();
    await expect(page.locator(".export-guide")).toBeVisible();
    await expect(page.locator(".export-cmd").first()).toContainText("run_export.py");
  });

  test("review page loads without WaveSurfer init error", async ({ page }) => {
    await page.goto("/?project_id=book_001&chapter_id=chapter_001");
    await expect(page.getByRole("button", { name: "保存 Review & cut_plan" })).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.locator(".waveform-editor")).toBeVisible();
    await expect(page.locator(".waveform-editor .status.error")).toHaveCount(0);
    await expect(page.getByText("WaveSurfer is not initialized")).toHaveCount(0);
  });

  test("invalid project shows friendly error without absolute path", async ({ page }) => {
    await page.goto("/?project_id=nonexistent&chapter_id=chapter_001");
    await expect(page.locator(".error-panel")).toBeVisible({ timeout: 10_000 });
    const text = await page.locator(".error-panel").innerText();
    expect(text).not.toMatch(/\/Users\//);
    expect(text).not.toMatch(/PycharmProjects/);
    expect(text).toContain("未找到项目或章节");
    await expect(
      page.getByRole("button", { name: "打开演示章节 book_001 / chapter_001" }),
    ).toBeVisible();
  });

  test("save review shows export guidance", async ({ page }) => {
    await page.goto("/?project_id=book_001&chapter_id=chapter_001");
    await expect(page.getByRole("button", { name: "保存 Review & cut_plan" })).toBeVisible({
      timeout: 15_000,
    });
    await page.getByRole("button", { name: "确认保留" }).click();
    await page.getByRole("button", { name: "保存 Review & cut_plan" }).click();
    await expect(page.locator(".save-msg")).toContainText("已保存 cut_plan", { timeout: 10_000 });
    await expect(page.locator(".export-hint")).toBeVisible();
    await expect(page.locator(".export-cmd")).toContainText("run_export.py");
  });

  test("mobile viewport remains usable", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/?project_id=book_001&chapter_id=chapter_001");
    await expect(page.getByRole("button", { name: "保存 Review & cut_plan" })).toBeVisible({
      timeout: 15_000,
    });
    await expect(page.locator(".review-columns")).toBeVisible();
    await expect(page.locator(".waveform-editor")).toBeVisible();
  });
});
