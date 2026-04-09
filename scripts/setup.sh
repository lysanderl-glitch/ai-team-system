#!/bin/bash
# ============================================================================
# Agent System 一键安装脚本
# 用于新同事快速搭建开发环境
# ============================================================================

set -e

echo "=========================================="
echo "  Agent System 安装脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查命令
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}错误: $1 未安装${NC}"
        return 1
    fi
    echo -e "${GREEN}✓${NC} $1"
}

# 步骤1: 检查基础依赖
echo "【步骤1/5】检查基础依赖..."
echo ""

check_command git
check_command python3
check_command pip3

echo ""
echo -e "${GREEN}基础依赖检查完成${NC}"
echo ""

# 步骤2: 安装Python依赖
echo "【步骤2/5】安装Python依赖..."
echo ""

cd "$(dirname "$0")/../agent-butler"
pip3 install -r requirements.txt --break-system-packages

echo ""
echo -e "${GREEN}Python依赖安装完成${NC}"
echo ""

# 步骤3: 安装Claude Code
echo "【步骤3/5】检查Claude Code..."
echo ""

if command -v claude &> /dev/null; then
    echo -e "${GREEN}✓ Claude Code已安装${NC}"
else
    echo -e "${YELLOW}⚠ Claude Code未安装${NC}"
    echo "  安装参考: https://docs.anthropic.com/en/docs/claude-code/setup"
fi

echo ""

# 步骤4: 链接Claude Code记忆
echo "【步骤4/5】同步Claude Code记忆..."
echo ""

OBS_MEMORY_DIR="$(dirname "$0")/../obs/00-system/claude-code-memory"
CLAUDE_MEMORY_DIR="$HOME/.claude/projects/-home-ubuntu/memory"

if [ -d "$OBS_MEMORY_DIR" ]; then
    # 创建Claude内存目录
    mkdir -p "$CLAUDE_MEMORY_DIR"

    # 同步文件
    echo "  复制记忆文件..."
    cp "$OBS_MEMORY_DIR"/*.md "$CLAUDE_MEMORY_DIR/" 2>/dev/null || true
    echo -e "${GREEN}✓ Claude Code记忆已同步${NC}"
else
    echo -e "${YELLOW}⚠ OBSidian记忆目录不存在，跳过${NC}"
fi

echo ""

# 步骤5: 启动文件监控
echo "【步骤5/5】启动文件监控..."
echo ""

# 检查是否已有watcher运行
if pgrep -f "hr_watcher.py" > /dev/null; then
    echo -e "${YELLOW}⚠ hr_watcher已在运行${NC}"
else
    nohup python3 hr_watcher.py > hr_watcher.log 2>&1 &
    sleep 1
    if pgrep -f "hr_watcher.py" > /dev/null; then
        echo -e "${GREEN}✓ hr_watcher已启动 (PID: $(pgrep -f 'hr_watcher.py'))${NC}"
    else
        echo -e "${RED}✗ hr_watcher启动失败${NC}"
    fi
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  安装完成！${NC}"
echo "=========================================="
echo ""
echo "下一步："
echo "  1. 启动Claude Code: claude"
echo "  2. 查看帮助: cat README.md"
echo "  3. 查看决策体系: cat docs/DECISION_SYSTEM.md"
echo ""
