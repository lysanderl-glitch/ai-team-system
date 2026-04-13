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

如果 memory 行为观察文件尚未创建（SPE 初期正常现象），跳过此数据源。
在报告的"行为洞察"区块中标注："行为观察数据尚在积累中，将在使用一段时间后自动生成洞察。"

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
6. **下周焦点建议** — 基于 OKR 缺口 + 未完成任务 + 行为洞察，推荐 3-5 个焦点

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

### 5a: 更新 personal_tasks.yaml（GATE：验证写入成功）

**GATE：使用 Edit 工具更新 personal_tasks.yaml 的 weekly_review 字段。必须确认 Edit 返回成功。如果失败，重试一次，仍失败则在报告中标注"任务文件更新失败"，但不阻塞 5b。**

```yaml
weekly_review:
  last_review: "YYYY-MM-DD"
  last_week: "YYYY-Wnn"
```

### 5b: 保存报告到 OBS（GATE：验证写入成功）

**GATE：使用 Write 工具将回顾报告保存为 Markdown 文件。必须确认 Write 返回成功。如果失败，重试一次，仍失败则停止并报错，不进入 5c。**

```bash
# Write to obs/06-daily-reports/YYYY-Wnn-weekly-review.md
```

### 5c: Git commit（前置条件：至少 5a 或 5b 成功写入）

**前置检查：运行 `git diff --stat` 确认有文件变更。如果 diff 为空（5a 和 5b 均失败），不执行 git commit，向用户报告写入失败。**

```bash
cd /c/Users/lysanderl_janusd/Claude\ Code/ai-team-system
git diff --stat agent-butler/config/personal_tasks.yaml obs/06-daily-reports/
```

仅在确认有变更后执行：
```bash
cd /c/Users/lysanderl_janusd/Claude\ Code/ai-team-system
git add agent-butler/config/personal_tasks.yaml obs/06-daily-reports/YYYY-Wnn-weekly-review.md
git commit -m "weekly-review: YYYY-Wnn 周回顾报告"
```

---

## 测试场景（强制，交付前必须通过）

### test_scenarios

#### Golden Path: 本周回顾（多数据源可用）

- **场景名称**：周末调用 /weekly-review 生成完整周回顾报告
- **输入**：`/weekly-review`（无参数，默认 this-week）
- **前置条件**：
  - `agent-butler/config/active_tasks.yaml` 存在且有本周已完成任务
  - `agent-butler/config/personal_tasks.yaml` 存在且有 inbox 条目和 OKR 数据
  - `obs/04-decision-knowledge/decision-log/` 目录存在
  - Google Calendar MCP 已认证且可用
- **预期结果**：
  - [ ] Step 1：正确计算本周起止日期（周一到当天）
  - [ ] Step 2a：读取 active_tasks.yaml 提取本周 completed_tasks
  - [ ] Step 2b：读取 personal_tasks.yaml 提取 inbox 处理情况 + OKR 进度
  - [ ] Step 2c：扫描决策日志目录，筛选本周新增决策文件
  - [ ] Step 2d：调用 `gcal_list_events` 获取本周事件，统计会议时长和深度工作时间
  - [ ] Step 2e：读取 memory 行为观察文件（如存在）
  - [ ] Step 3：输出包含全部 6 个区块：本周成就 / OKR 进度 / 决策回顾 / 时间分配 / 行为洞察 / 下周焦点建议
  - [ ] Step 3：OKR 进度含趋势箭头（>=5% 上升 / <5% 持平 / 下降）
  - [ ] Step 5a GATE：Edit 更新 personal_tasks.yaml 的 weekly_review 字段，确认成功
  - [ ] Step 5b GATE：Write 保存报告到 `obs/06-daily-reports/YYYY-Wnn-weekly-review.md`，确认成功
  - [ ] Step 5c：前置检查 `git diff --stat` 确认有变更后执行 git commit
  - [ ] 工具调用链：`Bash(日期计算) -> Read(active_tasks) -> Read(personal_tasks) -> Glob(decision-log) -> MCP(gcal) -> Read(memory) -> Edit(personal_tasks) -> Write(报告) -> Bash(git commit)`

#### Edge Case 1: 无 OKR 设定时的降级

- **场景名称**：personal_tasks.yaml 中无 OKR 数据时的行为
- **输入**：`/weekly-review`
- **前置条件**：
  - `personal_tasks.yaml` 存在但无 `okr` 或 `objectives` 字段
  - 其他数据源正常
- **预期结果**：
  - [ ] 不中断整体流程
  - [ ] OKR 进度区块标注"尚未设定 OKR，建议配置后再追踪"
  - [ ] 下周焦点建议基于未完成任务和行为洞察生成（不依赖 OKR 缺口）
  - [ ] 其余 5 个区块正常输出

#### Edge Case 2: 行为观察文件不存在

- **场景名称**：SPE 初期，memory 目录下无行为观察文件
- **输入**：`/weekly-review`
- **前置条件**：
  - memory 目录下无 `user_work_rhythm.md` 等行为观察文件
  - 其他数据源正常
- **预期结果**：
  - [ ] 跳过 Step 2e 数据源，不报错
  - [ ] 行为洞察区块标注"行为观察数据尚在积累中，将在使用一段时间后自动生成洞察"
  - [ ] 其余区块正常输出

#### Edge Case 3: git diff 为空（5a 和 5b 均失败）

- **场景名称**：报告保存和任务更新均失败时不执行空 commit
- **输入**：`/weekly-review`
- **前置条件**：
  - Step 5a Edit 失败（重试后仍失败）
  - Step 5b Write 失败（重试后仍失败）
- **预期结果**：
  - [ ] `git diff --stat` 确认无变更
  - [ ] 不执行 git commit（避免空 commit）
  - [ ] 向用户报告写入失败，报告内容仍在控制台输出可见
