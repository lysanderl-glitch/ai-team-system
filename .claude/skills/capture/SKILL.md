---
name: capture
description: |
  快速捕获任务/想法/行动项到 personal_tasks.yaml 的收件箱。
  支持手动输入和自动会话提取两种模式。
  Use when recording tasks, action items, or ideas during a conversation.
  Also triggered at session end to extract unrecorded items.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
argument-hint: "[task description] or 'auto' for session extraction"
---

# /capture — Synapse 快速捕获

你是 Harness Ops 团队的 harness_engineer，现在执行收件箱捕获任务。

## Step 1: 读取当前收件箱

```!
cat agent-butler/config/personal_tasks.yaml
```

读取 `agent-butler/config/personal_tasks.yaml`，了解当前 inbox 状态和已有 items。

## Step 2: 判断捕获模式

检查 `$ARGUMENTS`：

- **有具体内容**（非 `auto`、非空）→ 进入 **手动捕获模式**（Step 3A）
- **`auto` 或为空** → 进入 **自动提取模式**（Step 3B）

## Step 3A: 手动捕获模式

1. 将 `$ARGUMENTS` 作为捕获内容
2. 生成唯一 ID，格式：`CAP-YYYY-MMDD-NNN`
   - YYYY = 当前年份
   - MMDD = 当前月日
   - NNN = 当日序号（从 001 开始，基于已有同日 items 递增）
3. 构造新 item：
   ```yaml
   - id: "CAP-YYYY-MMDD-NNN"
     content: "<捕获内容>"
     source: "claude_cli"
     captured_at: "<ISO 8601 时间戳>"
     status: "pending"
     processed_to: ""
   ```
4. 跳到 Step 4

## Step 3B: 自动提取模式

1. 回顾当前会话的完整对话历史
2. 提取以下类型的未记录行动项：
   - 总裁提到要做的事（"我需要..."、"记一下..."、"回头要..."）
   - 讨论中产生的待办（"这个需要跟进"、"后续要..."）
   - 决策产生的行动项（"那就这样做"、"选方案A"）
   - 被提到但未分配的任务
3. 排除已经在 `active_tasks.yaml` 中跟踪的任务
4. 为每个提取项生成唯一 ID（同 Step 3A 规则）
5. 每个 item 的 source 设为 `claude_cli`
6. 将提取结果列表展示给用户确认，用户可以：
   - 确认全部
   - 选择性保留
   - 修改内容后保留
   - 全部放弃

## Step 4: 写入 personal_tasks.yaml

使用 Edit 工具将新 items 追加到 `inbox.items` 列表中：

- 如果 `items: []` 是空列表，替换为带有新条目的列表
- 如果已有条目，在列表末尾追加新条目
- 保持 YAML 格式一致（2 空格缩进）

## Step 5: 确认捕获结果

输出捕获确认：

```
捕获成功！

| ID | 内容 | 来源 | 状态 |
|----|------|------|------|
| CAP-YYYY-MMDD-NNN | 捕获内容摘要 | claude_cli | pending |

共捕获 N 项，已写入 personal_tasks.yaml 收件箱。
```

## Step 6: Git 提交（条件执行）

检查是否在 ai-team-system git repo 中：

```!
cd /c/Users/lysanderl_janusd/Claude\ Code/ai-team-system && git status --short agent-butler/config/personal_tasks.yaml
```

如果有变更，执行 git add + commit：

```!
cd /c/Users/lysanderl_janusd/Claude\ Code/ai-team-system && git add agent-butler/config/personal_tasks.yaml && git commit -m "capture: add inbox items via /capture"
```

---

## 捕获原则

- 宁可多捕获，不遗漏：有疑问的也先进收件箱，后续 /plan-day 时再分流
- 内容原文保留：不过度加工总裁的原话，保持上下文
- 去重检查：与已有 inbox items 和 active_tasks 对比，避免重复捕获
- 时间戳精确：captured_at 使用 ISO 8601 格式，精确到秒
