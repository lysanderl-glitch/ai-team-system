# Claude Code Hooks 配置指南

## SessionEnd Hook：会话结束自动任务捕获

`capture_session_tasks.py` 在每次 Claude Code 会话结束时自动运行，从对话记录中提取未捕获的行动项，写入 `personal_tasks.yaml` 收件箱。

### 工作原理

1. Claude Code 会话结束时触发 SessionEnd hook
2. 脚本从 stdin 接收 JSON 输入（含 `transcript_path` 和 `session_id`）
3. 读取 JSONL 格式的对话记录
4. 用关键词匹配提取候选行动项（中文/英文关键词 + checkbox 模式）
5. 与 `personal_tasks.yaml` 已有条目去重
6. 新项追加到 inbox，自动 git commit

### 配置方法

将以下配置加入 Claude Code 的 `settings.json` 文件。

**配置文件位置**（二选一）：
- 全局配置：`~/.claude/settings.json`
- 项目级配置：`<project>/.claude/settings.json`

**配置内容**：

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "PYTHONUTF8=1 python3 \"/c/Users/lysanderl_janusd/Claude Code/ai-team-system/scripts/capture_session_tasks.py\"",
            "timeout": 30000
          }
        ]
      }
    ]
  }
}
```

> **注意**：如果 `settings.json` 中已有其他 hooks 配置，将 `SessionEnd` 数组合并到现有 `hooks` 对象中，不要覆盖已有的 hook 配置。

### 手动测试

可以手动模拟 hook 触发来验证脚本：

```bash
# 方法 1：直接运行（无 transcript，应输出 "0"）
echo '{}' | PYTHONUTF8=1 python3 "/c/Users/lysanderl_janusd/Claude Code/ai-team-system/scripts/capture_session_tasks.py"

# 方法 2：提供 transcript 路径（用实际的 JSONL 文件测试）
echo '{"transcript_path": "/path/to/transcript.jsonl", "session_id": "test-001"}' | \
  PYTHONUTF8=1 python3 "/c/Users/lysanderl_janusd/Claude Code/ai-team-system/scripts/capture_session_tasks.py"
```

成功时输出捕获的行动项数量（如 `3`），无内容时输出 `0`。

### 匹配的关键词

**中文**：需要、记一下、回头、待办、后续、跟进、别忘了、提醒我

**英文**：TODO、action item、follow up、remind me、need to

**特殊模式**：`- [ ]` 开头的 checkbox 行

### 注意事项

- **Windows 路径**：路径中含空格时必须用引号包裹。配置中的路径使用 Unix 风格（`/c/...`）
- **编码**：环境变量 `PYTHONUTF8=1` 确保 Python 使用 UTF-8 编码，避免 Windows 下中文乱码
- **超时**：`timeout: 30000`（30秒），正常执行耗时远低于此值
- **无依赖**：脚本仅使用 Python 标准库，无需额外安装包
- **安全性**：脚本只读取对话记录、写入 personal_tasks.yaml、执行 git commit，不发送任何网络请求
- **错误处理**：所有异常被捕获，不会阻塞 Claude Code 正常退出
- **settings.json 不自动修改**：出于安全考虑，本脚本不自动修改 settings.json，需用户手动配置
