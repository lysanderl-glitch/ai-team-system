#!/bin/bash
# Claude Code Memory 同步脚本（env 驱动，跨环境）
# 默认把记忆同步到仓库内 `.claude/memory/`，如需同步到 Claude 全局记忆目录，请设置：
#   CLAUDE_MEMORY_DIR=/path/to/.claude/projects/<project>/memory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

OBS_MEMORY_DIR="${OBS_MEMORY_DIR:-$REPO_ROOT/obs/00-system/claude-code-memory}"
CLAUDE_MEMORY_DIR="${CLAUDE_MEMORY_DIR:-$REPO_ROOT/.claude/memory}"
BACKUP_DIR="${BACKUP_DIR:-$REPO_ROOT/.claude/memory-backup}"

echo "=== Claude Memory 同步 ==="
echo "来源: $OBS_MEMORY_DIR"
echo "目标: $CLAUDE_MEMORY_DIR"

auto_mkdir() {
  if [ ! -d "$1" ]; then
    mkdir -p "$1"
  fi
}

if [ ! -d "$OBS_MEMORY_DIR" ]; then
    echo "跳过：OBS memory 目录不存在：$OBS_MEMORY_DIR"
    exit 0
fi

auto_mkdir "$CLAUDE_MEMORY_DIR"

if [ -d "$CLAUDE_MEMORY_DIR" ]; then
    echo "创建备份..."
    rm -rf "$BACKUP_DIR"
    cp -r "$CLAUDE_MEMORY_DIR" "$BACKUP_DIR" || true
fi

echo "同步文件..."

copy_if_exists() {
  src="$1"
  dst="$2"
  if [ -f "$src" ]; then
    cp "$src" "$dst"
    echo "  ✓ $(basename "$src")"
  fi
}

copy_if_exists "$OBS_MEMORY_DIR/MEMORY.md" "$CLAUDE_MEMORY_DIR/MEMORY.md"
copy_if_exists "$OBS_MEMORY_DIR/user_role.md" "$CLAUDE_MEMORY_DIR/user_role.md"

for f in "$OBS_MEMORY_DIR"/feedback_*.md; do
    if [ -f "$f" ]; then
        filename=$(basename "$f")
        cp "$f" "$CLAUDE_MEMORY_DIR/$filename"
        echo "  ✓ $filename"
    fi
done

for f in "$OBS_MEMORY_DIR"/project_*.md; do
    if [ -f "$f" ]; then
        filename=$(basename "$f")
        cp "$f" "$CLAUDE_MEMORY_DIR/$filename"
        echo "  ✓ $filename"
    fi
done

for f in "$OBS_MEMORY_DIR"/*.md; do
    if [ -f "$f" ]; then
        filename=$(basename "$f")
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
