---
name: weekly-review
description: |
  每周回顾命令。综合本周任务完成情况、OKR 进度、决策质量、时间分配，
  生成结构化的周回顾报告。自动识别行为模式并给出下周建议。
  Use at the end of each week (Friday/Saturday) or when reviewing weekly progress.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
argument-hint: "[this-week|last-week|YYYY-Wnn]"
---

# /weekly-review — 每周回顾

## Step 1: 确定回顾周期

根据 $ARGUMENTS 确定回顾的时间范围：
- 默认（无参数或 `this-week`）：本周一到当天
- `last-week`：上周一到上周日
- `YYYY-Wnn`：指定 ISO 周

用 Bash 计算周的起止日期：
```bash
# 根据参数计算 week_start 和 week_end
# 默认本周
```

## Step 2: 数据收集（5 个来源）

### (a) 团队任务完成情况
读取 `agent-butler/config/active_tasks.yaml`，提取本周 completed_tasks：
```bash
# Read active_tasks.yaml
```

### (b) 个人任务 + OKR 进度
读取 `agent-butler/config/personal_tasks.yaml`：
- inbox 处理情况（本周新增 vs 已处理）
- OKR 各 KR 的当前进度

### (c) 决策日志
扫描 `obs/04-decision-knowledge/decision-log/` 目录：
- 本周新增的决策文件（按文件名日期筛选 D-YYYY-MMDD-NNN.md）
- 检查是否有决策到了 30 天回顾期

```bash
# Glob for decision files matching this week's dates
```

### (d) 日历时间分配
调用 Google Calendar MCP 获取本周事件：
- 统计会议数量和总时长
- 计算深度工作时间（time-block 中 category=deep_work 的事件）
- 计算空闲率

使用 `mcp__claude_ai_Google_Calendar__gcal_list_events` 工具获取本周事件列表。

### (e) 行为模式观察
读取 memory 目录下的行为观察文件：
- `memory/user_work_rhythm.md`
- `memory/user_decision_style.md`
- `memory/user_task_preferences.md`
- `memory/user_communication_style.md`

提取本周新增的观察记录。

## Step 3: 分析与生成报告

按 `agent-butler/config/spe_intelligence.yaml` 中的 `weekly_review.sections` 配置生成各节内容：

1. **本周成就** — 完成任务数（团队 + 个人）、关键交付物列表
2. **OKR 进度** — 每个 KR 的当前进度 vs 目标，计算趋势（与上周对比）：
   - 进步 >=5% → 上升箭头
   - 变化 <5% → 持平箭头
   - 下降 → 下降箭头
3. **决策回顾** — 本周新增决策摘要 + 到期回顾提醒
4. **时间分配** — 会议 / 深度工作 / 空闲 百分比
5. **行为模式洞察** — 本周发现的新行为模式
6. **下周焦点推荐** — 基于 OKR 缺口 + 未完成任务 + 行为洞察，推荐 3-5 个焦点

## Step 4: 输出格式

将报告以以下格式输出到控制台：

```
━━━━━━━━━ YYYY-Wnn 周回顾 ━━━━━━━━━

本周概况
  完成任务: N 项（团队 X + 个人 Y）
  决策记录: N 条
  OKR 总体进度: XX%

本周成就
  · 成就1
  · 成就2

OKR 进度
  O1: 目标名称
    KR1: XX% (+5%) 描述
    KR2: XX% (持平) 描述

决策回顾
  · D-YYYY-MMDD-NNN: 决策标题 — 状态
  到期回顾: D-YYYY-MMDD-NNN（30天已到）

时间分配
  会议: XX%  |  深度工作: XX%  |  空闲: XX%

行为洞察
  · 本周发现的新模式

下周焦点建议
  1. 建议1（理由）
  2. 建议2（理由）
```

## Step 5: 保存与更新

### 5a: 更新 personal_tasks.yaml
在 personal_tasks.yaml 中更新 weekly_review 字段：
```yaml
weekly_review:
  last_review: "YYYY-MM-DD"
  last_week: "YYYY-Wnn"
```

### 5b: 保存报告到 OBS
将回顾报告保存为 Markdown 文件：
```bash
# Write to obs/06-daily-reports/YYYY-Wnn-weekly-review.md
```

### 5c: Git commit
```bash
cd /c/Users/lysanderl_janusd/Claude\ Code/ai-team-system
git add agent-butler/config/personal_tasks.yaml obs/06-daily-reports/YYYY-Wnn-weekly-review.md
git commit -m "weekly-review: YYYY-Wnn 周回顾报告"
```
