---
name: time-block
description: |
  为任务创建 Google Calendar 时间块。支持自动查找空闲时段并创建事件。
  可指定任务名、时长、日期，AI 自动匹配最佳时段。
  Use when the president wants to block time for a task, schedule focus time,
  or create deadline reminders on the calendar.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
argument-hint: "[task description] [duration: 30m/1h/2h] [date: today/tomorrow/YYYY-MM-DD]"
---

# /time-block — Synapse Personal Engine 日历时间块创建

**执行团队：Butler（personal_assistant）**

为指定任务在 Google Calendar 上创建时间块（Time Block），支持自动查找空闲时段、颜色编码、提醒设置。

---

## 颜色编码体系

| colorId | 颜色 | 用途 | summary 前缀 |
|---------|------|------|--------------|
| 7 | Peacock 蓝绿 | 深度工作/Focus Time | 🔒 |
| 9 | Blueberry 蓝 | 会议相关准备 | 📋 |
| 5 | Banana 黄 | 待办/普通任务 | ✅ |
| 11 | Tomato 红 | Deadline/紧急 | ⚠️ |
| 2 | Sage 绿 | 个人/学习 | 📚 |
| 6 | Tangerine 橙 | L级重大任务 | 🔴 |

**选择规则：**
- 包含 "focus"/"深度"/"专注"/"deep work" → colorId 7
- 包含 "deadline"/"截止"/"紧急"/"urgent" → colorId 11
- 包含 "会议"/"准备"/"review"/"评审"/"审阅"/"审查"/"检查" → colorId 9
- 包含 "学习"/"阅读"/"个人"/"personal" → colorId 2
- L级任务 → colorId 6
- 默认 → colorId 5

完整关键词列表参见 `agent-butler/config/calendar_config.yaml` 的 `color_coding` 节。

---

## Step 1: 解析参数

**personal_assistant 执行：**

从 `$ARGUMENTS` 提取以下信息：

- **任务描述**：主要文本内容（去掉时长和日期标识后的部分）
- **时长**：匹配 `30m`/`1h`/`2h`/`90m` 等格式，默认 60 分钟
- **日期**：匹配 `today`/`tomorrow`/`YYYY-MM-DD`，默认今天

时区固定 **Asia/Dubai (UTC+4)**。

```bash
# 获取当前日期（Dubai 时区）
TZ="Asia/Dubai" date +%Y-%m-%d
```

**快捷模式解析：**
- `/time-block focus 2h tomorrow` → 任务="深度工作", 时长=120分钟, 日期=明天
- `/time-block "审阅Janus方案" 1h` → 任务="审阅Janus方案", 时长=60分钟, 日期=今天
- `/time-block deadline "合同截止" 2026-04-15` → 任务="合同截止", 日期=2026-04-15, 全天 deadline 提醒

---

## Step 2: 查找空闲时段

**personal_assistant 执行：**

调用 `mcp__claude_ai_Google_Calendar__gcal_find_my_free_time`：
- `calendarIds`: `["primary"]`
- `timeMin`: `"{TARGET_DATE}T08:00:00+04:00"`
- `timeMax`: `"{TARGET_DATE}T20:00:00+04:00"`
- `timeZone`: `"Asia/Dubai"`
- `minDuration`: 请求的时长（分钟数）

解析返回结果，列出所有满足时长要求的空闲时段：

```
可用时段：
  1. 08:00-10:00 [120min]
  2. 11:30-12:30 [60min]
  3. 14:00-17:00 [180min]
```

如果没有满足时长要求的空闲时段，提示总裁：
> 今日没有足够长的空闲时段（需要 Xmin），是否缩短时长或选择其他日期？

---

## Step 3: 确定时段

**personal_assistant 执行：**

### 情况 A：参数中指定了具体时间

如果 `$ARGUMENTS` 包含具体时间（如 `09:00`、`14:30`），直接使用该时间作为开始时间。

### 情况 B：未指定时间，自动推荐

根据精力分配规则匹配最佳时段（参考 `calendar_config.yaml` 的 `energy_rules`）：

| 任务类型 | 推荐时段 | 原因 |
|----------|----------|------|
| L级深度工作 / focus | 08:00-12:00 | 上午精力高峰 |
| 会议准备 / review | 13:00-15:00 | 午后协作时间 |
| M级常规任务 | 15:00-18:00 | 下午常规时间 |
| S级轻量任务 | 18:00-20:00 | 傍晚低精力时段 |

从 Step 2 的空闲时段中，选择**最早匹配推荐时段的空闲区间**，截取所需时长作为事件时间。

向总裁展示推荐：
```
推荐时段：09:00-10:00（上午精力高峰，适合深度工作）
确认创建？(yes/选择其他时段编号)
```

---

## Step 4: 创建日历事件

**personal_assistant 执行：**

### 标准事件创建

调用 `mcp__claude_ai_Google_Calendar__gcal_create_event`：
- `calendarId`: `"primary"`
- `event`:
  - `summary`: `"{前缀} {任务标题}"`（前缀根据颜色编码体系选择）
  - `description`: 包含以下信息：
    ```
    任务来源：SPE /time-block
    任务级别：S/M/L
    关键步骤：（如有）
    创建时间：{当前时间}
    ```
  - `start`: `{ "dateTime": "{TARGET_DATE}T{START_TIME}:00+04:00", "timeZone": "Asia/Dubai" }`
  - `end`: `{ "dateTime": "{TARGET_DATE}T{END_TIME}:00+04:00", "timeZone": "Asia/Dubai" }`
  - `colorId`: 根据颜色编码体系选择（见上方规则）
  - `reminders`: `{ "useDefault": false, "overrides": [{ "method": "popup", "minutes": 10 }] }`
- `sendUpdates`: `"none"`

### Deadline 特殊处理

如果是 deadline 类型（参数包含 "deadline"/"截止"）：
- 创建**全天事件**：使用 `date` 而非 `dateTime`
  - `start`: `{ "date": "{TARGET_DATE}" }`
  - `end`: `{ "date": "{TARGET_DATE}" }`
- colorId 固定为 `11`（Tomato 红）
- reminders 使用加强提醒：
  ```json
  {
    "useDefault": false,
    "overrides": [
      { "method": "popup", "minutes": 1440 },
      { "method": "popup", "minutes": 60 }
    ]
  }
  ```

---

## Step 5: 确认结果

**personal_assistant 执行：**

输出创建确认：

```
📅 时间块已创建：
  日期：{TARGET_DATE}
  时间：{START_TIME}-{END_TIME}
  标题：{前缀} {任务标题}
  颜色：{颜色名称} (colorId:{N})
  提醒：提前10分钟弹窗

🔗 日历事件链接：{event_link}（如 API 返回了链接）
```

### 联动更新 personal_tasks.yaml（可选）

如果任务来源于 `personal_tasks.yaml` 中的已有任务（通过标题匹配），读取文件并更新该任务状态：
- 添加 `calendar_blocked: true`
- 添加 `blocked_time: "{TARGET_DATE} {START_TIME}-{END_TIME}"`

使用 Edit 工具精确更新，不覆盖其他内容。

---

## 降级策略

| 情况 | 处理 |
|------|------|
| Google Calendar MCP 不可用 | 提示"日历服务不可用，请稍后重试或手动创建事件" |
| 无空闲时段 | 列出已有事件，建议调整或选择其他日期 |
| 参数解析失败 | 提示正确的使用格式和示例 |

---

## 执行约束

- 本 Skill 由 personal_assistant 主执行
- 输出语言：中文
- 创建事件前必须获得总裁确认（展示推荐时段后等待确认）
- 除更新 personal_tasks.yaml 的 calendar_blocked 字段外，不修改任何其他文件
- 时区固定 Asia/Dubai，不支持其他时区
