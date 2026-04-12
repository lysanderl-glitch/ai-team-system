#!/bin/bash
# CEO Guard Audit Logger
# 记录所有 Bash/Edit/Write 工具调用，供执行审计师事后审查
# 日志路径: ai-team-system/logs/ceo-guard-audit.log

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/ceo-guard-audit.log"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 从 stdin 读取 hook input JSON
INPUT=$(cat)

# 提取工具名称和输入
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null)

# 提取关键信息（不记录完整内容，只记录操作摘要）
case "$TOOL_NAME" in
  "Bash")
    SUMMARY=$(echo "$INPUT" | jq -r '.tool_input.command // "unknown"' 2>/dev/null | head -c 200)
    ;;
  "Edit")
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // "unknown"' 2>/dev/null)
    SUMMARY="Edit: $FILE_PATH"
    ;;
  "Write")
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // "unknown"' 2>/dev/null)
    SUMMARY="Write: $FILE_PATH"
    ;;
  *)
    SUMMARY="$TOOL_NAME call"
    ;;
esac

# 写入审计日志
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] session=$SESSION_ID tool=$TOOL_NAME summary=\"$SUMMARY\"" >> "$LOG_FILE"

# 正常继续，不阻断（审计层只记录不拦截）
echo '{"continue": true, "suppressOutput": true}'
