#!/bin/bash
# ============================================================================
# 同步所有系统
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_BUTLER_DIR="$(dirname "$SCRIPT_DIR")/agent-butler"
OBS_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  同步所有系统"
echo "=========================================="
echo ""

# 1. 同步HR知识库到YAML
echo "【1/3】同步HR知识库..."
cd "$AGENT_BUTLER_DIR"
python3 hr_base.py sync
echo ""

# 2. 同步Claude Code记忆
echo "【2/3】同步Claude Code记忆..."
bash "$SCRIPT_DIR/sync-claude-memory.sh"
echo ""

# 3. 同步到GitHub
echo "【3/3】同步到GitHub..."
cd "$OBS_DIR"
git add -A
git commit -m "同步更新 $(date '+%Y-%m-%d %H:%M:%S')" || echo "无变更"
git push origin master
echo ""

echo "=========================================="
echo "  同步完成"
echo "=========================================="
