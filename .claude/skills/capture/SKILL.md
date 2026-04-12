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

## Step 4: 写入 personal_tasks.yaml（强制门禁）

**GATE：此步骤是强制门禁。必须确认 Edit 工具调用成功返回后才可继续。如果 Edit 失败，重试一次，仍失败则停止并报错，绝不可跳过。**

使用 Edit 工具将新 items 追加到 `agent-butler/config/personal_tasks.yaml` 的 `inbox.items` 列表中。

**情况 A — inbox 为空列表 `items: []`：**
- `old_string` 匹配：`items: []`
- `new_string` 替换为完整的条目列表，例如：
  ```
  items:
      - id: "CAP-2026-0412-001"
        content: "捕获内容"
        source: "claude_cli"
        captured_at: "2026-04-12T14:30:00+04:00"
        status: "pending"
        processed_to: ""
  ```

**情况 B — inbox 已有条目：**
- `old_string` 匹配最后一个条目的完整内容（从 `- id:` 到 `processed_to: "..."`）
- `new_string` 为该最后条目原文 + 换行 + 新条目（保持相同缩进）

**关键要求：**
- 保持 YAML 格式一致（2 空格缩进，items 下 4 空格缩进）
- Edit 工具必须返回成功（确认文件已修改）
- **未完成 Edit 不得进入 Step 4.5 或 Step 5，执行链在此阻塞直到写入成功**

## Step 4.5: 验证写入成功（第二道保险）

用 git diff 检查文件是否确实被修改：

```!
cd /c/Users/lysanderl_janusd/Claude\ Code/ai-team-system && git diff --stat agent-butler/config/personal_tasks.yaml
```

- **diff 有输出**（文件已变更）→ 继续进入 Step 5
- **diff 为空**（文件未变更）→ Step 4 写入失败，**必须回到 Step 4 重试一次**。如果重试后 diff 仍为空，停止执行并向用户报错："personal_tasks.yaml 写入失败，请检查文件格式或手动添加。"

**绝不可在 diff 为空时继续后续步骤。**

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

使用 `git diff --quiet` 检查文件是否有实际变更，只有变更存在时才提交：

```!
cd /c/Users/lysanderl_janusd/Claude\ Code/ai-team-system && git diff --quiet agent-butler/config/personal_tasks.yaml || (git add agent-butler/config/personal_tasks.yaml && git commit -m "capture: add inbox items via /capture")
```

- **文件有变更**：`git diff --quiet` 返回非零，触发 `||` 后的 add + commit
- **文件无变更**：`git diff --quiet` 返回零，跳过提交，输出以下警告：

```
⚠️ 警告：personal_tasks.yaml 无变更，跳过 git commit。
这可能意味着 Step 4 的写入未生效，请检查捕获流程是否正常完成。
```

---

## 捕获原则

- 宁可多捕获，不遗漏：有疑问的也先进收件箱，后续 /plan-day 时再分流
- 内容原文保留：不过度加工总裁的原话，保持上下文
- 去重检查：与已有 inbox items 和 active_tasks 对比，避免重复捕获
- 时间戳精确：captured_at 使用 ISO 8601 格式，精确到秒

---

## 测试场景（强制，交付前必须通过）

### test_scenarios

#### Golden Path: 手动捕获单条任务

- **场景名称**：用户通过 `/capture` 手动添加一条任务到收件箱
- **输入**：`/capture 调研 Claude Code MCP 最新文档`
- **前置条件**：
  - `agent-butler/config/personal_tasks.yaml` 已存在
  - inbox.items 已有至少 1 条现有条目
- **预期结果**：
  - [ ] 文件变更：`agent-butler/config/personal_tasks.yaml`
  - [ ] 新条目 ID 格式匹配：`CAP-\d{4}-\d{4}-\d{3}`
  - [ ] 新条目 content 包含：`调研 Claude Code MCP 最新文档`
  - [ ] 新条目 source 为：`claude_cli`
  - [ ] 新条目 status 为：`pending`
  - [ ] captured_at 为 ISO 8601 格式（含时区）
  - [ ] 工具调用链：`Read(personal_tasks.yaml) -> Edit(追加条目) -> Bash(git diff --stat) -> Bash(git commit)`
  - [ ] git commit 消息包含：`capture`
  - [ ] 最终输出包含表格：ID / 内容 / 来源 / 状态

#### Edge Case 1: inbox 为空列表时的首次捕获

- **场景名称**：inbox.items 为空数组 `[]` 时捕获第一条任务
- **输入**：`/capture 第一条测试任务`
- **前置条件**：
  - `personal_tasks.yaml` 存在
  - inbox 区块为 `items: []`（空列表）
- **预期结果**：
  - [ ] Edit 的 old_string 匹配 `items: []`，替换为包含新条目的完整列表
  - [ ] 新条目 ID 序号为 `001`（当日首条）
  - [ ] Step 4.5 git diff 有输出（确认写入成功）
  - [ ] 不应产生空 commit

#### Edge Case 2: 自动提取模式（无参数）

- **场景名称**：无参数调用时自动扫描会话历史提取行动项
- **输入**：`/capture`（无参数）或 `/capture auto`
- **前置条件**：
  - 当前会话中存在未记录的行动项（如总裁说过"回头要..."）
  - `active_tasks.yaml` 已存在（用于去重）
- **预期结果**：
  - [ ] 进入自动提取模式（Step 3B）
  - [ ] 提取结果列表展示给用户确认后再写入
  - [ ] 与 active_tasks.yaml 中已有任务去重
  - [ ] 如果会话中无可提取项，输出"未发现未记录的行动项"，不产生空写入
