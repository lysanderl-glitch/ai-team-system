#!/bin/bash
# CEO Guard Hook 安装脚本
# 将 CEO Guard hooks 配置合并到项目级 .claude/settings.json
#
# 用法: bash scripts/install-ceo-guard.sh
#
# 说明：
# - 在 ai-team-system/.claude/settings.json 中安装 PreToolUse/PostToolUse/SessionStart hooks
# - 如果文件已存在，会保留已有配置并合并 hooks
# - 如果文件不存在，会创建新文件

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$PROJECT_DIR/.claude"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
HOOK_TEMPLATE="$SCRIPT_DIR/ceo-guard-settings.json"

echo "=== CEO Guard Hook 安装程序 ==="
echo ""
echo "项目目录: $PROJECT_DIR"
echo "配置目标: $SETTINGS_FILE"
echo "Hook 模板: $HOOK_TEMPLATE"
echo ""

# 检查模板文件是否存在
if [ ! -f "$HOOK_TEMPLATE" ]; then
    echo "[ERROR] Hook 模板文件不存在: $HOOK_TEMPLATE"
    exit 1
fi

# 确保 .claude 目录存在
mkdir -p "$CLAUDE_DIR"

# 确保 logs 目录存在
mkdir -p "$PROJECT_DIR/logs"

if [ -f "$SETTINGS_FILE" ]; then
    echo "[INFO] 发现已有配置文件，将合并 hooks..."

    # 检查是否有 node（用于 JSON 合并）
    if command -v node &> /dev/null; then
        # 将 MSYS/Git Bash 路径转为 Windows 路径供 node 使用
        WIN_SETTINGS=$(cygpath -w "$SETTINGS_FILE" 2>/dev/null || echo "$SETTINGS_FILE")
        WIN_TEMPLATE=$(cygpath -w "$HOOK_TEMPLATE" 2>/dev/null || echo "$HOOK_TEMPLATE")
        node -e "
const fs = require('fs');
const existing = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
const hooks = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const merged = { ...existing, hooks: hooks.hooks };
fs.writeFileSync(process.argv[1], JSON.stringify(merged, null, 2) + '\n');
console.log('[OK] 配置已合并');
" "$WIN_SETTINGS" "$WIN_TEMPLATE"
    else
        echo "[WARN] node 不可用，将直接覆盖 hooks 配置"
        cp "$HOOK_TEMPLATE" "$SETTINGS_FILE"
        echo "[OK] 配置已写入（覆盖模式）"
    fi
else
    echo "[INFO] 创建新配置文件..."
    cp "$HOOK_TEMPLATE" "$SETTINGS_FILE"
    echo "[OK] 配置文件已创建"
fi

echo ""
echo "=== 安装完成 ==="
echo ""
echo "已安装的 hooks："
echo "  - SessionStart: CEO Guard 初始化提醒"
echo "  - PreToolUse (Bash|Edit|Write): 审计日志 + 执行权限提醒"
echo "  - PostToolUse (Bash|Edit|Write): 异步审计日志记录"
echo ""
echo "审计日志路径: $PROJECT_DIR/logs/ceo-guard-audit.log"
echo ""
echo "注意: 请重新打开 Claude Code 会话，新的 hooks 配置才会生效。"
echo "如需查看/编辑 hooks，在 Claude Code 中输入 /hooks"
