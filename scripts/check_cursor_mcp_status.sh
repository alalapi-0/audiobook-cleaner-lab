#!/usr/bin/env bash
# check_cursor_mcp_status.sh — CLI 层 Cursor MCP 状态检查
# 注意：本脚本结果不代表当前 Agent 对话线程已暴露工具。见 docs/cursor_tool_registry_check.md

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

warn_thread() {
  echo ""
  echo -e "${YELLOW}⚠ 重要提示${NC}"
  echo "  本脚本仅检查 CLI 层（cursor-agent）MCP 状态。"
  echo "  不代表当前 Agent 对话线程已暴露对应工具。"
  echo "  若对话中工具不可用，请完全退出 Cursor、重开仓库、新建普通前台 Agent。"
  echo "  详见: docs/cursor_tool_registry_check.md"
  echo ""
}

check_list_tools() {
  local server="$1"
  echo "── list-tools: ${server} ──"
  if cursor-agent mcp list-tools "$server" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} ${server}: list-tools 成功"
  else
    local exit_code=$?
    echo -e "${RED}✗${NC} ${server}: list-tools 失败 (exit ${exit_code})"
    echo "  可能原因: server 未加载、需要 Settings 批准、或名称路由问题"
  fi
  echo ""
}

echo "========================================"
echo " Cursor MCP Status Check (CLI layer)"
echo " Repository: audiobook-cleaner-lab"
echo "========================================"
echo ""

if ! command -v cursor-agent >/dev/null 2>&1; then
  echo -e "${YELLOW}cursor-agent 未安装或不在 PATH 中${NC}"
  echo ""
  echo "说明:"
  echo "  - 无法通过 CLI 检查 MCP 列表"
  echo "  - 请在 Cursor Settings → Tools & MCP 中手动确认 server 状态"
  echo "  - 或安装 Cursor CLI 后重试"
  warn_thread
  exit 0
fi

echo "── cursor-agent mcp list ──"
if cursor-agent mcp list; then
  echo -e "${GREEN}✓${NC} mcp list 完成"
else
  echo -e "${RED}✗${NC} mcp list 失败"
fi
echo ""

# 本仓库标准 MCP（非微信项目，不检查 wechat-chrome-session）
SERVERS=(
  chrome-devtools
  playwright
  stitch
  filesystem
  context7
  github
)

for server in "${SERVERS[@]}"; do
  check_list_tools "$server"
done

# 若 .cursor/mcp.json 含 wechat 相关配置则额外检查（本仓库默认跳过）
if [[ -f .cursor/mcp.json ]] && grep -q 'wechat' .cursor/mcp.json 2>/dev/null; then
  echo "── 检测到微信相关 MCP 配置，额外检查 ──"
  check_list_tools "wechat-chrome-session"
  check_list_tools "wechat_chrome_session"
fi

warn_thread

echo "若某 server 显示 not loaded / needs approval:"
echo "  1. Cursor Settings → Tools & MCP → 批准对应 server"
echo "  2. 完全退出 Cursor（Cmd+Q）"
echo "  3. 重新打开本仓库"
echo "  4. 新建普通前台 Agent 对话（禁用 Multitask）"
echo ""
