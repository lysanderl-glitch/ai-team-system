#!/bin/bash
# ============================================================================
# 启动文件监控（后台运行）
# ============================================================================

AGENT_BUTLER_DIR="$(cd "$(dirname "$0")/../agent-butler" && pwd)"

cd "$AGENT_BUTLER_DIR"

# 检查是否已有watcher运行
if pgrep -f "hr_watcher.py" > /dev/null; then
    echo "hr_watcher已在运行 (PID: $(pgrep -f 'hr_watcher.py'))"
    exit 0
fi

# 启动watcher
nohup python3 hr_watcher.py > hr_watcher.log 2>&1 &
WATCHER_PID=$!

sleep 1

if ps -p $WATCHER_PID > /dev/null; then
    echo "hr_watcher已启动 (PID: $WATCHER_PID)"
    echo "日志文件: $AGENT_BUTLER_DIR/hr_watcher.log"
    echo ""
    echo "停止命令: pkill -f hr_watcher.py"
else
    echo "启动失败，请检查日志"
    cat hr_watcher.log
    exit 1
fi
