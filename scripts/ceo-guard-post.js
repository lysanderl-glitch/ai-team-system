#!/usr/bin/env node
// CEO Guard - PostToolUse Hook
// 异步记录执行完成审计日志

const fs = require('fs');
const path = require('path');

const PROJECT_DIR = path.resolve(__dirname, '..');
const LOG_DIR = path.join(PROJECT_DIR, 'logs');
const LOG_FILE = path.join(LOG_DIR, 'ceo-guard-audit.log');

try { fs.mkdirSync(LOG_DIR, { recursive: true }); } catch(e) {}

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  let toolName = 'unknown';
  let sessionId = 'unknown';

  try {
    const data = JSON.parse(input);
    toolName = data.tool_name || 'unknown';
    sessionId = data.session_id || 'unknown';
  } catch(e) {}

  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
  const logLine = `[${timestamp}] POST session=${sessionId} tool=${toolName}\n`;
  try { fs.appendFileSync(LOG_FILE, logLine); } catch(e) {}

  // 静默完成，不干扰输出
  process.stdout.write('{"suppressOutput": true}');
});
