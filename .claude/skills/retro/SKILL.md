---
name: retro
description: |
  复盘总结。回顾当前会话或指定时间段的工作，提取经验教训，沉淀到知识库。
  适用于项目复盘、周复盘、任务完成后的反思。
  Use after completing major tasks, at end of sprint/week, or when the user wants
  to review what was accomplished and capture lessons learned.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
argument-hint: "[session|week|project] [topic]"
---

# /retro — Synapse 复盘总结

你是 Lysander CEO，执行复盘总结。

## 复盘范围

根据 `$ARGUMENTS` 确定范围：
- **`session`（默认）**：当前会话完成的工作
- **`week`**：本周的 git 提交和变更
- **`project [name]`**：指定项目的整体复盘

## 复盘流程

### Step 1: 收集事实

```bash
# 最近的 git 活动
git log --oneline --since="7 days ago" 2>/dev/null | head -30
```

```bash
# 文件变更统计
git diff --stat HEAD~10 2>/dev/null | tail -5
```

回顾当前会话中完成的所有任务和交付物。

### Step 2: 四维度复盘

**strategist 分析：**

| 维度 | 问题 |
|------|------|
| **做得好** | 哪些做法效果突出，值得固化为标准流程？ |
| **做得不好** | 哪些地方出了问题或效率低下？根因是什么？ |
| **学到的** | 有哪些新发现、新知识、新模式？ |
| **下一步** | 基于以上分析，接下来应该做什么？ |

### Step 3: 输出复盘报告

```
**【复盘报告】** [日期/范围]

## 完成的工作
- [工作项1]
- [工作项2]

## 做得好
- [亮点1 — 原因分析]

## 需改进
- [问题1 — 根因 → 改进方案]

## 学到的
- [经验1]

## 下一步行动
- [ ] [Action Item 1]
- [ ] [Action Item 2]

## 执行链健康度
- 派单完整性：X%
- QA 通过率：X%
- 知识沉淀率：X%
```

### Step 4: 知识沉淀（GATE：验证写入成功）

将有价值的经验教训写入 `obs/02-project-knowledge/retro/` 目录。
将可复用的流程改进写入 `obs/03-process-knowledge/`。

**GATE：每次 Write 工具调用后，必须确认返回成功。如果失败，重试一次，仍失败则在复盘报告中标注"知识沉淀写入失败：[文件路径]"，不可静默跳过。**

### Step 5: 更新任务状态（GATE：验证编辑成功）

检查并更新 `agent-butler/config/active_tasks.yaml`：
- 已完成的任务标记为 done
- 新发现的待办写入

**GATE：使用 Edit 工具更新 active_tasks.yaml 后，必须确认 Edit 返回成功。如果失败，重试一次，仍失败则提示用户手动更新任务状态。**

---

## 测试场景（强制，交付前必须通过）

### test_scenarios

#### Golden Path: 当前会话复盘

- **场景名称**：会话中完成实质工作后执行默认范围复盘
- **输入**：`/retro`（无参数，默认 session 范围）
- **前置条件**：
  - 当前会话中已完成若干任务（有 git commit 记录）
  - `agent-butler/config/active_tasks.yaml` 存在
  - `obs/02-project-knowledge/retro/` 目录存在
- **预期结果**：
  - [ ] Step 1：执行 `git log --oneline --since="7 days ago"` 和 `git diff --stat` 收集事实
  - [ ] Step 2：输出四维度复盘：做得好 / 做得不好 / 学到的 / 下一步
  - [ ] Step 3：输出完整复盘报告格式，包含执行链健康度（派单完整性 / QA 通过率 / 知识沉淀率）
  - [ ] Step 4：将经验教训写入 `obs/02-project-knowledge/retro/`
  - [ ] Step 4 GATE：Write 返回成功确认，失败则重试，仍失败则标注"知识沉淀写入失败：[路径]"
  - [ ] Step 5：更新 `active_tasks.yaml` 中已完成任务标记为 done
  - [ ] Step 5 GATE：Edit 返回成功确认，失败则提示用户手动更新
  - [ ] 工具调用链：`Bash(git log) -> Bash(git diff) -> Write(retro文档) -> Edit(active_tasks.yaml)`

#### Edge Case 1: 会话无实质工作内容

- **场景名称**：会话仅有简短对话、无任务执行时执行复盘
- **输入**：`/retro`
- **前置条件**：
  - 当前会话中未执行任何任务
  - `git log --since="7 days ago"` 返回空（或仅有自动备份提交）
  - `git diff --stat` 无变更
- **预期结果**：
  - [ ] 不生成空洞复盘报告
  - [ ] 向用户报告"本次会话无实质性工作记录可复盘"
  - [ ] 跳过 Step 4 知识沉淀（无有价值内容）
  - [ ] 不产生空 commit
  - [ ] 可选：建议使用 `/retro week` 查看更长时间范围

#### Edge Case 2: week 范围复盘

- **场景名称**：用户指定 week 范围进行周维度复盘
- **输入**：`/retro week`
- **前置条件**：
  - 本周有 git 提交记录
- **预期结果**：
  - [ ] git log 使用 `--since="7 days ago"` 获取本周提交
  - [ ] git diff 统计本周所有文件变更
  - [ ] 复盘报告范围标注为本周日期区间
  - [ ] 如果同时有会话工作和历史提交，合并分析
