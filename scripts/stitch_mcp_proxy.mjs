#!/usr/bin/env node
/**
 * Stitch MCP 本地 stdio proxy — 从环境变量读取 STITCH_API_KEY，不打印密钥。
 * 依赖：@google/stitch-sdk、@modelcontextprotocol/sdk（见根 package.json devDependencies）
 */

import { StitchProxy } from "@google/stitch-sdk";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const apiKey = process.env.STITCH_API_KEY;

if (!apiKey || !apiKey.trim()) {
  console.error(
    "STITCH_API_KEY is not set. Copy .env.example to .env and set your key, " +
      "or export STITCH_API_KEY in your shell / Cursor MCP env."
  );
  process.exit(1);
}

const proxy = new StitchProxy({ apiKey: apiKey.trim() });
const transport = new StdioServerTransport();

await proxy.start(transport);
