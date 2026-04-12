#!/usr/bin/env node
// CEO Guard - PreToolUse Hook
// 记录审计日志 + 注入执行权限提醒
// 从 stdin 读取 hook input JSON

const fs = require('fs');
const path = require('path');

const PROJECT_DIR = path.resolve(__dirname, '..');
const LOG_DIR = path.join(PROJECT_DIR, 'logs');
const LOG_FILE = path.join(LOG_DIR, 'ceo-guard-audit.log');

// 确保日志目录存在
try { fs.mkdirSync(LOG_DIR, { recursive: true }); } catch(e) {}

// 从 stdin 读取输入
let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  let toolName = 'unknown';
  let sessionId = 'unknown';
  let summary = '';

  try {
    const data = JSON.parse(input);
    toolName = data.tool_name || 'unknown';
    sessionId = data.session_id || 'unknown';

    if (toolName === 'Bash') {
      summary = (data.tool_input?.command || '').substring(0, 200);
    } else if (toolName === 'Edit') {
      summary = 'Edit: ' + (data.tool_input?.file_path || 'unknown');
    } else if (toolName === 'Write') {
      summary = 'Write: ' + (data.tool_input?.file_path || 'unknown');
    } else {
      summary = toolName;
    }
  } catch(e) {
    summary = 'parse-error';
  }

  // 写入审计日志
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
  const logLine = `[${timestamp}] PRE session=${sessionId} tool=${toolName} summary="${summary}"\n`;
  try { fs.appendFileSync(LOG_FILE, logLine); } catch(e) {}

  // 输出 hook response - 注入提醒到模型上下文
  const response = {
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      additionalContext: "[CEO-GUARD-REMINDER] 你正在调用执行工具。如果你是 Lysander CEO 主对话，请确认：1) 已输出团队派单表 2) 当前操作标注了执行者身份（如 harness_engineer 执行）。如果你是子 Agent 团队成员，请忽略此提醒。违规模式包括：直接执行、贴标签冒充、先斩后奏、伪派单。"
    }
  };

  process.stdout.write(JSON.stringify(response));
});
