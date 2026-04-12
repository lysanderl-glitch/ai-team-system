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
