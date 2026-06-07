#!/usr/bin/env node
/**
 * 打印 MCP 人工启用步骤 — 供用户在 Cursor UI 中完成批准与重启。
 */

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const MCP_PATH = path.join(ROOT, ".cursor", "mcp.json");

const SERVERS = [
  "filesystem",
  "playwright",
  "chrome-devtools",
  "context7",
  "github",
  "stitch",
];

const TOKEN_SERVERS = {
  github: ["GITHUB_TOKEN", "GITHUB_PERSONAL_ACCESS_TOKEN"],
  stitch: ["STITCH_API_KEY"],
};

function listConfiguredServers() {
  if (!fs.existsSync(MCP_PATH)) {
    return SERVERS;
  }
  try {
    const data = JSON.parse(fs.readFileSync(MCP_PATH, "utf8"));
    const keys = Object.keys(data.mcpServers ?? {}).sort();
    return keys.length ? keys : SERVERS;
  } catch {
    return SERVERS;
  }
}

function main() {
  const servers = listConfiguredServers();

  console.log("=".repeat(60));
  console.log("Cursor MCP 人工启用步骤");
  console.log("=".repeat(60));
  console.log(`\n仓库路径: ${ROOT}`);
  console.log(`配置文件: ${path.relative(ROOT, MCP_PATH)}`);
  console.log(`\n已配置 server (${servers.length}): ${servers.join(", ")}`);

  console.log("\n── 必须完成的 UI 步骤 ──\n");
  const steps = [
    "打开 Cursor Settings",
    "进入 Tools & MCP",
    "找到当前仓库配置的 MCP server",
    `对 ${servers.join(" / ")} 逐一批准`,
    "若 github 或 stitch 需要密钥，先配置环境变量或在 Cursor 支持的位置填写",
    "完全退出 Cursor（不只是关闭窗口）",
    "重新打开当前仓库",
    "新建普通前台 Agent 对话",
    "不要使用 Multitask 模式测试 MCP",
    "在新对话中让 Agent 检查当前线程暴露的工具列表",
  ];
  steps.forEach((s, i) => console.log(`  ${i + 1}. ${s}`));

  console.log("\n── 需要 Token 的 server ──\n");
  for (const [name, vars] of Object.entries(TOKEN_SERVERS)) {
    if (servers.includes(name)) {
      console.log(`  • ${name}: ${vars.join(" 或 ")}`);
    }
  }

  console.log("\n── 不需要 Token 的 server ──\n");
  const noToken = servers.filter((s) => !(s in TOKEN_SERVERS));
  console.log(`  • ${noToken.join("\n  • ") || "(无)"}`);

  console.log("\n── 验证命令 ──\n");
  console.log("  npm run check:mcp");
  console.log("  npm run check:stitch   # stitch 专项");
  console.log("\n注意: 上述检查仅验证仓库配置，不代表当前 Agent 线程已加载 MCP。");
  console.log("=".repeat(60));
}

main();
