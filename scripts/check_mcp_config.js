#!/usr/bin/env node
/**
 * 轻量 MCP 配置检查 — 验证 .cursor/mcp.json 格式、6 个必需 server、
 * 文档与 .env.example 完整性及安全规则。不打印任何敏感值。
 */

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const MCP_PATH = path.join(ROOT, ".cursor", "mcp.json");
const ENV_EXAMPLE_PATH = path.join(ROOT, ".env.example");
const DOC_SETUP = path.join(ROOT, "docs", "MCP_SETUP.md");
const DOC_TROUBLESHOOTING = path.join(ROOT, "docs", "MCP_TROUBLESHOOTING.md");

const REQUIRED_SERVERS = [
  "chrome-devtools",
  "context7",
  "filesystem",
  "github",
  "playwright",
  "stitch",
];

const REQUIRED_ENV_VARS = [
  "GITHUB_TOKEN",
  "GITHUB_PERSONAL_ACCESS_TOKEN",
  "STITCH_API_KEY",
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
const TOKEN_LIKE =
  /^(ghp_[a-zA-Z0-9]{20,}|github_pat_[a-zA-Z0-9_]{20,}|gho_[a-zA-Z0-9]{20,}|ghu_[a-zA-Z0-9]{20,}|ghs_[a-zA-Z0-9]{20,}|ghr_[a-zA-Z0-9]{20,})$/;

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
  const warnings = [];
  const fsCfg = servers.filesystem;
  if (!fsCfg || typeof fsCfg !== "object") {
    return { issues, warnings };
  }

  const args = fsCfg.args;
  if (!Array.isArray(args)) {
    return { issues: ["filesystem.args 必须是数组"], warnings };
  }

  const pathArgs = args.filter(
    (a) => typeof a === "string" || typeof a === "number"
  );
  if (pathArgs.length === 0) {
    issues.push("filesystem 未指定授权目录");
    return { issues, warnings };
  }

  let hasSafeScope = false;

  for (const raw of pathArgs) {
    const str = String(raw);
    if (SAFE_WORKSPACE_PLACEHOLDERS.some((ph) => str.includes(ph))) {
      hasSafeScope = true;
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

    // 绝对路径：检查是否包含当前仓库根
    if (path.isAbsolute(str)) {
      const resolved = path.resolve(str);
      const rel = path.relative(resolved, ROOT);
      if (rel === "" || (!rel.startsWith("..") && !path.isAbsolute(rel))) {
        hasSafeScope = true;
      } else {
        warnings.push(
          `filesystem 绝对路径 "${str}" 与当前仓库 ${ROOT} 不一致，新机器复用时需更新`
        );
      }
    }

    for (const frag of DANGEROUS_PATH_FRAGMENTS) {
      if (frag === "/") continue;
      if (
        norm.includes(frag) &&
        (norm.endsWith(frag.replace(/\/$/, "")) || norm === frag)
      ) {
        issues.push(`filesystem 可能授权过宽: "${str}"`);
      }
    }
  }

  if (!hasSafeScope && pathArgs.length > 0) {
    warnings.push(
      "filesystem 未使用 ${workspaceFolder} 且未检测到当前仓库绝对路径，请确认授权范围"
    );
  }

  return { issues, warnings };
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

function checkStitchConfig(servers) {
  const warnings = [];
  const stitch = servers.stitch;
  if (!stitch || typeof stitch !== "object") {
    return warnings;
  }

  const cmd = stitch.command;
  const args = Array.isArray(stitch.args) ? stitch.args : [];
  const hasProxy =
    cmd === "node" && args.some((a) => String(a).includes("stitch_mcp_proxy"));
  const hasEnvKey =
    stitch.env &&
    typeof stitch.env === "object" &&
    "STITCH_API_KEY" in stitch.env;

  if (!hasProxy && !args.length) {
    warnings.push(
      "stitch 启动命令未确认，请在 docs/MCP_SETUP.md 中补充或配置 stitch_mcp_proxy"
    );
  }
  if (!hasEnvKey) {
    warnings.push("stitch 未配置 STITCH_API_KEY 环境变量映射");
  }

  const proxyPath = path.join(ROOT, "scripts", "stitch_mcp_proxy.mjs");
  if (hasProxy && !fs.existsSync(proxyPath)) {
    warnings.push(`stitch proxy 脚本缺失: ${path.relative(ROOT, proxyPath)}`);
  }

  return warnings;
}

function checkGithubEnv(servers) {
  const warnings = [];
  const gh = servers.github;
  if (!gh || typeof gh !== "object") return warnings;

  const env = gh.env;
  if (!env || typeof env !== "object") {
    warnings.push("github 未配置 env 块，运行时需要 GITHUB_PERSONAL_ACCESS_TOKEN");
    return warnings;
  }

  const tokenVal = env.GITHUB_PERSONAL_ACCESS_TOKEN;
  if (tokenVal && !ENV_PLACEHOLDER.test(String(tokenVal).trim())) {
    warnings.push(
      "github.env.GITHUB_PERSONAL_ACCESS_TOKEN 应使用 ${env:...} 占位符而非字面量"
    );
  }

  return warnings;
}

function checkEnvExample() {
  const issues = [];
  if (!fs.existsSync(ENV_EXAMPLE_PATH)) {
    issues.push("缺失: .env.example");
    return issues;
  }

  let content;
  try {
    content = fs.readFileSync(ENV_EXAMPLE_PATH, "utf8");
  } catch (err) {
    issues.push(`无法读取 .env.example: ${err.message}`);
    return issues;
  }

  for (const varName of REQUIRED_ENV_VARS) {
    const pattern = new RegExp(`^${varName}=`, "m");
    if (!pattern.test(content)) {
      issues.push(`.env.example 缺少变量: ${varName}`);
    }
  }

  return issues;
}

function checkDocs() {
  const issues = [];
  if (!fs.existsSync(DOC_SETUP)) {
    issues.push("缺失: docs/MCP_SETUP.md");
  }
  if (!fs.existsSync(DOC_TROUBLESHOOTING)) {
    issues.push("缺失: docs/MCP_TROUBLESHOOTING.md");
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
    const envNote = envKeys.length ? `, env: [${envKeys.join(", ")}]` : "";
    const tokenNote = ["github", "stitch"].includes(name)
      ? " ⚠ 需要 token"
      : "";
    console.log(`  - ${name}: ${cmd} ${argPreview}${envNote}${tokenNote}`);
  }
}

function main() {
  console.log("=".repeat(50));
  console.log("MCP 配置检查 — audiobook-cleaner-lab");
  console.log(`仓库路径: ${ROOT}`);
  console.log("=".repeat(50));

  const { data, issues: loadIssues } = loadMcpConfig();
  if (data === null) {
    console.log("\n检查未通过:");
    for (const issue of loadIssues) {
      console.log(`  ✗ ${issue}`);
    }
    process.exit(1);
  }

  const servers = data.mcpServers ?? {};
  const issues = [...loadIssues];
  const warnings = [];

  if (typeof servers !== "object" || servers === null) {
    console.log("  ✗ mcpServers 无效");
    process.exit(1);
  }

  issues.push(...checkRequiredServers(servers));
  const fsResult = checkFilesystemScope(servers);
  issues.push(...fsResult.issues);
  warnings.push(...fsResult.warnings);
  issues.push(...checkTokenLeak(servers));
  warnings.push(...checkStitchConfig(servers));
  warnings.push(...checkGithubEnv(servers));
  issues.push(...checkEnvExample());
  issues.push(...checkDocs());

  summarizeServers(servers);

  if (warnings.length > 0) {
    console.log("\n警告（不阻塞通过）:");
    for (const w of warnings) {
      console.log(`  ⚠ ${w}`);
    }
  }

  if (issues.length > 0) {
    console.log("\n检查未通过:");
    for (const issue of issues) {
      console.log(`  ✗ ${issue}`);
    }
    process.exit(1);
  }

  console.log("\n✓ MCP 配置检查通过");
  console.log("  修改 .cursor/mcp.json 后请完全退出 Cursor 并重新打开仓库");
  console.log("  人工步骤: node scripts/print_mcp_manual_steps.js");
  process.exit(0);
}

main();
