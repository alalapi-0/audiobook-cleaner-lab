#!/usr/bin/env node
/**
 * Stitch MCP 配置轻量检查 — 不打印任何真实 API Key。
 */

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const MCP_PATH = path.join(ROOT, ".cursor", "mcp.json");
const ENV_EXAMPLE = path.join(ROOT, ".env.example");
const GITIGNORE = path.join(ROOT, ".gitignore");
const STITCH_DOCS = path.join(ROOT, "docs", "design", "stitch");
const PROXY_SCRIPT = path.join(ROOT, "scripts", "stitch_mcp_proxy.mjs");

/** 疑似真实 API Key（非占位符） */
const KEY_LIKE =
  /^(AIza[0-9A-Za-z_-]{20,}|sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,})$/;

const PLACEHOLDER =
  /your_stitch_api_key_here|your[_-]?key|changeme|xxx|<[^>]+>|\$\{env:/i;

const ENV_PLACEHOLDER = /^\$\{env:[^}]+\}$|^\$\{[A-Z_][A-Z0-9_]*\}$/;

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (err) {
    return { error: err.message };
  }
}

function walkStrings(obj, parts, hits) {
  if (obj === null || obj === undefined) return;
  if (typeof obj === "string") {
    const s = obj.trim();
    if (ENV_PLACEHOLDER.test(s)) return;
    if (PLACEHOLDER.test(s)) return;
    if (KEY_LIKE.test(s)) {
      hits.push(parts.join("."));
    }
    return;
  }
  if (typeof obj !== "object") return;
  for (const [k, v] of Object.entries(obj)) {
    walkStrings(v, [...parts, k], hits);
  }
}

function main() {
  console.log("=".repeat(50));
  console.log("Stitch 配置检查 — audiobook-cleaner-lab");
  console.log("=".repeat(50));

  const issues = [];
  const ok = [];

  // 1. mcp.json
  if (!fs.existsSync(MCP_PATH)) {
    issues.push("缺失 .cursor/mcp.json");
  } else {
    const cfg = readJson(MCP_PATH);
    if (cfg.error) {
      issues.push(`mcp.json 解析失败: ${cfg.error}`);
    } else {
      ok.push("mcp.json 存在且 JSON 有效");
      const stitch = cfg.mcpServers?.stitch;
      if (!stitch) {
        issues.push("mcp.json 缺少 stitch server");
      } else {
        ok.push("已配置 stitch MCP server");
        const leaks = [];
        walkStrings(stitch, ["stitch"], leaks);
        if (leaks.length) {
          issues.push(`stitch 配置疑似硬编码 API Key: ${leaks.join(", ")}`);
        } else {
          ok.push("stitch 配置未发现硬编码 key");
        }
      }
    }
  }

  // 2. proxy 脚本
  if (!fs.existsSync(PROXY_SCRIPT)) {
    issues.push("缺失 scripts/stitch_mcp_proxy.mjs");
  } else {
    ok.push("stitch_mcp_proxy.mjs 存在");
  }

  // 3. .env.example
  if (!fs.existsSync(ENV_EXAMPLE)) {
    issues.push("缺失 .env.example");
  } else {
    const envText = fs.readFileSync(ENV_EXAMPLE, "utf8");
    if (!envText.includes("STITCH_API_KEY")) {
      issues.push(".env.example 未包含 STITCH_API_KEY");
    } else {
      ok.push(".env.example 包含 STITCH_API_KEY");
    }
  }

  // 4. .gitignore
  if (!fs.existsSync(GITIGNORE)) {
    issues.push("缺失 .gitignore");
  } else {
    const gi = fs.readFileSync(GITIGNORE, "utf8");
    if (!gi.includes(".env")) {
      issues.push(".gitignore 未忽略 .env");
    } else {
      ok.push(".gitignore 忽略 .env");
    }
  }

  // 5. docs/design/stitch/
  if (!fs.existsSync(STITCH_DOCS)) {
    issues.push("缺失 docs/design/stitch/");
  } else {
    ok.push("docs/design/stitch/ 存在");
    for (const sub of ["exports", "screenshots", "prompts", "reviews"]) {
      const p = path.join(STITCH_DOCS, sub);
      if (!fs.existsSync(p)) {
        issues.push(`缺失 docs/design/stitch/${sub}/`);
      }
    }
  }

  console.log("\n通过项:");
  for (const item of ok) {
    console.log(`  ✓ ${item}`);
  }

  if (issues.length) {
    console.log("\n未通过项:");
    for (const item of issues) {
      console.log(`  ✗ ${item}`);
    }
    process.exit(1);
  }

  console.log("\n✓ Stitch 配置检查通过");
  console.log("  请在本机设置 STITCH_API_KEY 并重启 Cursor 后验证 MCP 连接");
  process.exit(0);
}

main();
