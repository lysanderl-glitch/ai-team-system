#!/bin/bash
# Claude Code Memory 同步脚本
# 从 OBSidian 同步到 Claude Code 记忆目录
# 用途：使 OBSidian 成为唯一数据源，支持体系分享

set -e

# 路径配置
OBS_MEMORY_DIR="/home/ubuntu/knowledge-base/obs/00-system/claude-code-memory"
CLAUDE_MEMORY_DIR="/home/ubuntu/.claude/projects/-home-ubuntu/memory"
BACKUP_DIR="/home/ubuntu/.claude/projects/-home-ubuntu/memory-backup"

echo "=== Claude Memory 同步 ==="
echo "来源: $OBS_MEMORY_DIR"
echo "目标: $CLAUDE_MEMORY_DIR"

# 检查源目录
if [ ! -d "$OBS_MEMORY_DIR" ]; then
    echo "错误: OBSidian memory 目录不存在"
    exit 1
fi

# 创建备份
if [ -d "$CLAUDE_MEMORY_DIR" ]; then
    echo "创建备份..."
    rm -rf "$BACKUP_DIR"
    cp -r "$CLAUDE_MEMORY_DIR" "$BACKUP_DIR"
fi

# 同步文件
echo "同步文件..."

# MEMORY.md
if [ -f "$OBS_MEMORY_DIR/MEMORY.md" ]; then
    cp "$OBS_MEMORY_DIR/MEMORY.md" "$CLAUDE_MEMORY_DIR/MEMORY.md"
    echo "  ✓ MEMORY.md"
fi

# user_role.md
if [ -f "$OBS_MEMORY_DIR/user_role.md" ]; then
    cp "$OBS_MEMORY_DIR/user_role.md" "$CLAUDE_MEMORY_DIR/user_role.md"
    echo "  ✓ user_role.md"
fi

# feedback_*.md
for f in "$OBS_MEMORY_DIR"/feedback_*.md; do
    if [ -f "$f" ]; then
        filename=$(basename "$f")
        cp "$f" "$CLAUDE_MEMORY_DIR/$filename"
        echo "  ✓ $filename"
    fi
done

# project_*.md
for f in "$OBS_MEMORY_DIR"/project_*.md; do
    if [ -f "$f" ]; then
        filename=$(basename "$f")
        cp "$f" "$CLAUDE_MEMORY_DIR/$filename"
        echo "  ✓ $filename"
    fi
done

# 其他 .md 文件
for f in "$OBS_MEMORY_DIR"/*.md; do
    if [ -f "$f" ]; then
        filename=$(basename "$f")
        # 跳过已同步的
        if [[ "$filename" != "MEMORY.md" && "$filename" != "user_role.md" ]]; then
            if [[ "$filename" != feedback_*.md && "$filename" != project_*.md ]]; then
                cp "$f" "$CLAUDE_MEMORY_DIR/$filename"
                echo "  ✓ $filename"
            fi
        fi
    fi
done

echo ""
echo "同步完成!"
echo "Claude Code 将在下次启动时加载新记忆"
