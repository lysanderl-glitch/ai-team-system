---
name: plan-day
description: |
  每日规划命令。综合 Google Calendar、Slack、active_tasks 和 personal_tasks 四大信息源，
  生成总裁今日焦点计划。包含日程概览、空闲时段、任务推荐、决策队列。
  Use at the start of each day, or when the president asks "plan my day" / "今天做什么".
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
argument-hint: "[today|tomorrow|YYYY-MM-DD]"
---

# /plan-day — Synapse Personal Engine 每日规划

**执行团队：Butler（personal_assistant）+ Graphify 智囊团（strategist）**

综合四大信息源，生成总裁每日焦点计划。每日启动仪式的核心 Skill。

---

## Step 1: 确定目标日期

根据 `$ARGUMENTS` 确定规划日期：

- **无参数 / `today`**：今天
- **`tomorrow`**：明天
- **`YYYY-MM-DD`**：指定日期

时区固定为 **Asia/Dubai (UTC+4)**。

```bash
# 获取当前日期（Dubai 时区）
TZ="Asia/Dubai" date +%Y-%m-%d
```

将目标日期存入变量 `TARGET_DATE`，后续步骤均以此日期为准。

---

## Step 2: 读取四大信息源

### (a) Google Calendar（通过 MCP 工具）

**personal_assistant 执行：**

调用 MCP 工具获取日历数据。如果 MCP 工具不可用（认证过期、服务不可达），跳过此源并在最终输出中标注"日历数据不可用"，不中断流程。

**获取当日事件：**

调用 `mcp__claude_ai_Google_Calendar__gcal_list_events`：
- `calendarId`: `"primary"`
- `timeMin`: `"{TARGET_DATE}T00:00:00+04:00"`
- `timeMax`: `"{TARGET_DATE}T23:59:59+04:00"`
- `timeZone`: `"Asia/Dubai"`

**获取空闲时段：**

调用 `mcp__claude_ai_Google_Calendar__gcal_find_my_free_time`：
- `calendarIds`: `["primary"]`
- `timeMin`: `"{TARGET_DATE}T08:00:00+04:00"`
- `timeMax`: `"{TARGET_DATE}T20:00:00+04:00"`
- `timeZone`: `"Asia/Dubai"`
- `minDuration`: `30`

提取所有事件的：标题、开始/结束时间、位置/会议链接、出席状态。
提取所有空闲时段的：开始时间、结束时间、时长（分钟）。

### (b) 团队任务状态

**personal_assistant 执行：**

读取 `agent-butler/config/active_tasks.yaml`。

从中提取与总裁相关的节点：
- `status: blocked` 且阻塞原因包含"总裁"/"president"/"刘子杨" → 等待总裁解除阻塞
- `status: review` 或 `requires_review: true` → 需要总裁验收
- `priority: high` 或 `priority: critical` → 高优先级任务进展

对每项提取：任务名、当前状态、阻塞原因（如有）、负责团队。

### (c) 个人任务

**personal_assistant 执行：**

读取 `agent-butler/config/personal_tasks.yaml`。

提取以下数据：
- **inbox**：未处理的新条目（捕获后尚未分类的）
- **today_focus**：已计划的今日焦点项（如果已有之前的规划）
- **personal_okrs**：OKR 进度数据，计算对齐度百分比
- **habits / routines**：日常习惯追踪项（如有）

### (d) Slack 消息（通过 MCP 工具，可选）

**personal_assistant 执行：**

尝试调用 MCP 工具读取 Slack。如果 MCP 不可用，静默跳过，在最终输出中标注"Slack 数据不可用"。

尝试调用 `mcp__claude_ai_Slack__slack_read_channel`：
- 读取 inbox / general 等关键频道
- 提取最近 24 小时内未处理的消息
- 识别 @提及、action items、待回复消息

对每项提取：来源频道、发送者、内容摘要、时间戳。

---

## Step 3: 智能分析与任务推荐

**strategist 执行：**

### 3a: Eisenhower + 10x 分类

将从四大信息源收集到的所有待办项，按 Eisenhower 矩阵 + 10x 测试分类：

| 分类 | 标准 | 处理方式 |
|------|------|----------|
| 🔴 紧急+重要 | 今日必须完成，直接影响关键目标或有截止期限 | 列入 big_rocks，匹配时间块 |
| 🟡 重要+不紧急 | 推动 OKR 进展、长期价值高，但无立即截止 | 建议安排专注时间块 |
| 🟢 紧急+不重要 | 有截止但价值有限，可由团队代劳 | 建议委派团队，自动生成派单建议 |
| ⚪ 不紧急+不重要 | 无截止且价值有限 | 建议稍后处理或从列表移除 |

**10x 测试**：对每个任务追问 "这件事做了，对目标的贡献是 1x 还是 10x？" — 10x 项优先。

### 3b: 任务-时段匹配

将分类后的任务匹配到空闲时段：

- **S级任务**（信息查询、快速决策、简单回复）→ 30 分钟以下的短时段
- **M级任务**（常规工作、会议准备、文档审阅）→ 60-120 分钟的中等时段
- **L级任务**（深度思考、战略规划、复杂决策）→ 120 分钟以上的大块时段

匹配原则：
- 上午精力高峰（08:00-12:00）优先安排 🔴 big_rocks 和 L级深度工作
- 午后（13:00-15:00）安排会议和协作任务
- 下午（15:00-18:00）安排 M级常规任务
- 傍晚（18:00-20:00）安排轻量级 S级任务和复盘

---

## Step 4: 输出标准格式

**personal_assistant 执行：**

按以下格式输出总裁日程概览（严格遵守排版）：

```
━━━━━━━━━ {TARGET_DATE} 总裁日程概览 ━━━━━━━━━

📅 今日日程（N 项）
  HH:MM-HH:MM  事件标题 (位置/会议链接)
  HH:MM-HH:MM  事件标题 (位置/会议链接)
  ...

⏰ 可用时间块
  HH:MM-HH:MM  [XXmin] ← 推荐: 任务名
  HH:MM-HH:MM  [XXmin] ← 推荐: 任务名
  ...

🔴 必须今日完成（Big Rocks）
  1. 任务描述（来源: xxx | 预估: S/M/L级）
  2. 任务描述（来源: xxx | 预估: S/M/L级）
  ...

🟡 需要您决策
  1. 决策描述（选项概要 | 截止: YYYY-MM-DD）
  2. 决策描述（选项概要 | 截止: YYYY-MM-DD）
  ...

🟢 团队进展（无需操作）
  · 任务简述 → 当前状态
  · 任务简述 → 当前状态
  ...

📥 收件箱未处理（N 项）
  · 来源: 内容摘要 (捕获时间)
  · 来源: 内容摘要 (捕获时间)
  ...

📊 本周 OKR 对齐度: XX%
  ⚠️ 落后项提醒（如有）

💡 AI 建议
  · 基于日程密度和精力分配的优化建议
  · 风险预警（如：连续会议超过3小时未留休息、关键截止日临近等）
  · 委派建议（🟢 类任务的具体派单方向）
```

**格式注意事项：**
- 如某个信息源不可用，对应区域显示 `(数据源不可用，已跳过)` 而非留空
- 如某个分类无内容（如无需决策的项），整块省略不显示
- 时间统一使用 24 小时制，Dubai 本地时间
- 每个区域之间留一空行，保持可读性

---

## Step 5: 更新 personal_tasks.yaml（GATE：验证写入成功）

**personal_assistant 执行：**

将 Plan My Day 的结果写回 `agent-butler/config/personal_tasks.yaml`：

1. 更新 `today_focus` 字段为今日 big_rocks 和推荐任务列表
2. 更新 `last_planned` 为当前日期时间
3. 保留 inbox 中未处理的项目（不删除，仅标注已纳入计划的）
4. 不覆盖其他字段（personal_okrs、habits 等保持不变）

写入时使用 Edit 工具精确更新对应字段，避免覆盖整个文件。

**GATE：每次 Edit 调用后，必须确认 Edit 返回成功。如果失败，重试一次，仍失败则在输出中标注"任务文件更新失败，日程概览仅供参考，未持久化"，不中断整体流程但不可静默跳过。**

---

## 降级策略（Graceful Degradation）

当某个信息源不可用时，不中断整体流程：

| 信息源 | 不可用时的处理 |
|--------|---------------|
| Google Calendar | 跳过日程和空闲时段，提示"请手动告知今日日程" |
| active_tasks.yaml | 文件不存在时跳过，提示"无团队任务数据" |
| personal_tasks.yaml | 文件不存在时跳过，仅基于日历和Slack规划 |
| Slack MCP | 静默跳过，不提示错误，在输出中标注"Slack 不可用" |

最终输出至少包含 AI 建议区块——即使所有信息源都不可用，也基于日期（工作日/周末）给出通用建议。

---

## Step 6: 时间块创建建议（可选交互）

**personal_assistant 执行：**

在呈现完日程概览后，向总裁提供交互选项：

> 是否需要为以上推荐的任务创建日历时间块？
> - 输入 `yes` 或 `确认` → 为所有 🔴 big_rocks 自动创建时间块
> - 输入任务编号（如 `1,3`）→ 只为指定任务创建
> - 输入 `no` 或 `不用` → 跳过

如果总裁确认，调用 `mcp__claude_ai_Google_Calendar__gcal_create_event` 为每个选中的任务创建事件：
- 使用 Step 3 中匹配的时段
- 使用颜色编码体系（参考 /time-block Skill 的颜色规则）：

| colorId | 颜色 | 用途 | summary 前缀 |
|---------|------|------|--------------|
| 7 | Peacock 蓝绿 | 深度工作/Focus Time | 🔒 |
| 9 | Blueberry 蓝 | 会议相关准备 | 📋 |
| 5 | Banana 黄 | 待办/普通任务 | ✅ |
| 11 | Tomato 红 | Deadline/紧急 | ⚠️ |
| 2 | Sage 绿 | 个人/学习 | 📚 |
| 6 | Tangerine 橙 | L级重大任务 | 🔴 |

- summary 格式：`{前缀} 任务标题`
- description 包含：任务来源、级别、关键步骤
- reminders: popup 提前 10 分钟
- sendUpdates: "none"

创建完成后输出确认清单：

```
📅 已创建时间块：
  ✓ 09:00-10:00 🔒 深度工作: 审阅Janus方案 (colorId:7)
  ✓ 15:00-15:30 ✅ 处理邮件回复 (colorId:5)
```

如果 Google Calendar MCP 不可用，提示"日历写入服务不可用，已跳过时间块创建"，不中断整体流程。

---

## 执行约束

- 本 Skill 由 personal_assistant 主执行，strategist 负责分析层
- 输出语言：中文
- Step 1-5 为只读操作（读取日历、任务等信息源）
- Step 6 为可选写入操作：仅在总裁明确确认后才创建日历事件
- 除更新 personal_tasks.yaml 和创建日历事件（经确认）外，不修改任何其他文件
