#!/usr/bin/env node
/**
 * 轻量 MCP 配置检查 — 验证 .cursor/mcp.json 格式、5 个必需 server 与安全规则。
 * 不打印任何敏感值。
 */

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const MCP_PATH = path.join(ROOT, ".cursor", "mcp.json");

const REQUIRED_SERVERS = [
  "chrome-devtools",
  "context7",
  "filesystem",
  "github",
  "playwright",
];

const SAFE_WORKSPACE_PLACEHOLDERS = ["${workspaceFolder}", "${workspaceRoot}"];

const DANGEROUS_PATH_FRAGMENTS = [
  "c:\\",
  "c:/",
  "~",
  "$home",
  "%userprofile%",
  "/users/",
  "/home/",
  "/volumes/",
];

/** GitHub / 通用 token 疑似硬编码模式（值非 env 占位符时告警） */
const TOKEN_LIKE = /^(ghp_[a-zA-Z0-9]{20,}|github_pat_[a-zA-Z0-9_]{20,}|gho_[a-zA-Z0-9]{20,}|ghu_[a-zA-Z0-9]{20,}|ghs_[a-zA-Z0-9]{20,}|ghr_[a-zA-Z0-9]{20,})$/;

const ENV_PLACEHOLDER = /^\$\{env:[^}]+\}$|^\$\{[A-Z_][A-Z0-9_]*\}$/;

function loadMcpConfig() {
  const issues = [];
  if (!fs.existsSync(MCP_PATH)) {
    return { data: null, issues: [`缺失: ${path.relative(ROOT, MCP_PATH)}`] };
  }

  let raw;
  try {
    raw = fs.readFileSync(MCP_PATH, "utf8");
  } catch (err) {
    return { data: null, issues: [`无法读取 mcp.json: ${err.message}`] };
  }

  let data;
  try {
    data = JSON.parse(raw);
  } catch (err) {
    return { data: null, issues: [`JSON 无法解析: ${err.message}`] };
  }

  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    return { data: null, issues: ["根对象必须是 JSON object"] };
  }

  if (typeof data.mcpServers !== "object" || data.mcpServers === null) {
    issues.push("缺少或无效的 mcpServers 对象");
  }

  return { data, issues };
}

function checkRequiredServers(servers) {
  const issues = [];
  for (const name of REQUIRED_SERVERS) {
    if (!(name in servers)) {
      issues.push(`缺少 MCP server: ${name}`);
    }
  }
  return issues;
}

function checkFilesystemScope(servers) {
  const issues = [];
  const fsCfg = servers.filesystem;
  if (!fsCfg || typeof fsCfg !== "object") {
    return issues;
  }

  const args = fsCfg.args;
  if (!Array.isArray(args)) {
    return ["filesystem.args 必须是数组"];
  }

  const pathArgs = args.filter((a) => typeof a === "string" || typeof a === "number");
  if (pathArgs.length === 0) {
    issues.push("filesystem 未指定授权目录");
    return issues;
  }

  for (const raw of pathArgs) {
    const str = String(raw);
    if (SAFE_WORKSPACE_PLACEHOLDERS.some((ph) => str.includes(ph))) {
      continue;
    }

    const norm = str.trim().toLowerCase().replace(/\\/g, "/");
    if (norm === "/" || norm === "c:/" || norm === "c:\\") {
      issues.push(`filesystem 授权范围过宽: "${str}"`);
      continue;
    }
    if (norm === "~" || norm.startsWith("~/")) {
      issues.push(`filesystem 指向用户主目录: "${str}"`);
      continue;
    }
    for (const frag of DANGEROUS_PATH_FRAGMENTS) {
      if (frag === "/") continue;
      if (norm.includes(frag) && (norm.endsWith(frag.replace(/\/$/, "")) || norm === frag)) {
        issues.push(`filesystem 可能授权过宽: "${str}"`);
      }
    }
  }

  return issues;
}

function checkTokenLeak(servers) {
  const issues = [];
  const walk = (obj, pathParts) => {
    if (obj === null || obj === undefined) return;
    if (typeof obj === "string") {
      if (ENV_PLACEHOLDER.test(obj.trim())) return;
      if (TOKEN_LIKE.test(obj.trim())) {
        issues.push(`疑似硬编码 token: ${pathParts.join(".")}`);
      }
      return;
    }
    if (typeof obj !== "object") return;
    for (const [key, val] of Object.entries(obj)) {
      walk(val, [...pathParts, key]);
    }
  };

  for (const [name, cfg] of Object.entries(servers)) {
    if (cfg && typeof cfg === "object") {
      walk(cfg, [name]);
    }
  }
  return issues;
}

function summarizeServers(servers) {
  console.log("\nMCP 配置摘要:");
  for (const name of Object.keys(servers).sort()) {
    const cfg = servers[name];
    if (!cfg || typeof cfg !== "object") {
      console.log(`  - ${name}: (无效配置)`);
      continue;
    }
    const cmd = cfg.command ?? "?";
    const args = Array.isArray(cfg.args) ? cfg.args : [];
    let argPreview = args.slice(0, 4).map(String).join(" ");
    if (args.length > 4) argPreview += " ...";
    const envKeys =
      cfg.env && typeof cfg.env === "object" ? Object.keys(cfg.env) : [];
    const envNote = envKeys.length ? `, env keys: [${envKeys.join(", ")}]` : "";
    console.log(`  - ${name}: ${cmd} ${argPreview}${envNote}`);
  }
}

function main() {
  console.log("=".repeat(50));
  console.log("MCP 配置检查 — audiobook-cleaner-lab");
  console.log("=".repeat(50));

  const { data, issues: loadIssues } = loadMcpConfig();
  if (data === null) {
    for (const issue of loadIssues) {
      console.log(`  ✗ ${issue}`);
    }
    process.exit(1);
  }

  const servers = data.mcpServers ?? {};
  const issues = [...loadIssues];

  if (typeof servers !== "object" || servers === null) {
    console.log("  ✗ mcpServers 无效");
    process.exit(1);
  }

  issues.push(...checkRequiredServers(servers));
  issues.push(...checkFilesystemScope(servers));
  issues.push(...checkTokenLeak(servers));

  summarizeServers(servers);

  if (issues.length > 0) {
    console.log("\n检查未通过:");
    for (const issue of issues) {
      console.log(`  ✗ ${issue}`);
    }
    process.exit(1);
  }

  console.log("\n✓ MCP 配置检查通过");
  console.log("  修改 .cursor/mcp.json 后请重启 Cursor 或 Reload Window");
  process.exit(0);
}

main();
