---
title: Synapse Agent 主动驱动协作模式设计方案
date: 2026-04-12
author: Graphify 智囊团全员
tags: [Synapse, 协作模式, 主动驱动, 服务模式, 架构]
decision_level: L3
status: 方案制定完成，待总裁确认
priority: P0 — 影响总裁与AI团队的核心交互方式
---

# Synapse Agent 主动驱动协作模式

## 一、问题定义

### 当前模式（被动响应）

```
总裁发话 ───→ Lysander 响应 ───→ 团队执行
总裁沉默 ───→ 全体静默 ───→ 什么都不发生

问题：
├── 团队不会主动找总裁 — 即使有到期的待办事项
├── 总裁必须自己记住所有事情 — "下周三要问RD那个方案"
├── 信息是单向的 — 总裁→团队，从来不是团队→总裁
└── 团队像"被叫才动的工具"，不像"主动工作的团队"
```

### 目标模式（主动驱动）

```
总裁交代任务 → Lysander 执行/归档 → 团队记住
                                        ↓
                                   到了该跟进的时间
                                        ↓
                              团队 → Lysander → 主动联系总裁
                              "总裁，RD团队上周归档的公众号方案，
                               今天是约定的跟进日，是否启动执行？"

核心原则：
├── 总裁不需要记任何待办 — 团队记
├── Lysander 是唯一沟通渠道 — 团队不直接找总裁
├── 团队在合适的时间主动行动 — 不需要总裁触发
└── 像一个真正的职业团队 — 主动汇报、适时请示、定期跟进
```

## 二、架构设计

### 三个基础设施

#### 1. 团队待办系统（Task Backlog）

扩展 active_tasks.yaml，增加新的任务状态：

```yaml
# 任务状态扩展
task_statuses:
  in_progress: 正在执行
  blocked: 阻塞等待
  review: 审查中
  completed: 已完成
  # === 新增 ===
  pending_start: 待启动（等待总裁确认后执行）
  pending_followup: 待跟进（到期后主动询问总裁）
  pending_confirmation: 待确认（需要总裁决策的悬置项）
  scheduled: 已排期（确定执行时间但尚未开始）

# 跟进信息（新增字段）
follow_up:
  date: "2026-04-16"          # 跟进日期
  time: "14:00"               # 跟进时间（默认下午2点）
  action: "ask_president"     # 跟进动作
  message: "RD团队上周归档的微信公众号方案，是否启动执行？"
  assigned_team: "rd"         # 负责团队
  channel: "slack"            # 通知渠道（slack/session/both）
```

#### 2. 时间触发引擎（Proactive Trigger）

两个触发渠道：

```
渠道A：Slack 即时通知（不依赖总裁打开 Claude Code）
  ├── 定时任务每天早上检查 active_tasks.yaml
  ├── 有到期的跟进项 → 通过 Slack 发送提醒
  ├── 消息格式：Lysander 口吻，附带上下文
  └── 示例："总裁，RD团队有一个待确认事项到期：
             微信公众号抓取方案（4月16日约定跟进）。
             是否启动执行？回复Y启动/N推迟/打开Claude Code详谈。"

渠道B：Claude Code 会话提醒（深度沟通）
  ├── 每次新会话开始，Lysander 读取 active_tasks.yaml
  ├── 检查是否有到期或即将到期的跟进项
  ├── 如果有 → 在开场问候后立即提醒
  └── 示例："总裁，有2项待跟进事项：
             1. [RD] 微信公众号方案 — 约定今天跟进，是否启动？
             2. [Growth] 客户A回访 — 明天到期，需要准备吗？"
```

#### 3. 统一出口（Lysander 代理层）

```
规则：
├── 所有团队对总裁的主动联系，必须通过 Lysander 代理
├── RD团队不会直接发 Slack 给总裁 — 是 Lysander 发
├── Lysander 会汇总多个团队的待办 — 不是每个团队各发一条
├── 消息口吻统一 — Lysander 的风格，不是各团队各自的风格
└── 总裁回复也是对 Lysander — 由 Lysander 转达给团队
```

### 完整工作流

```
Step 1: 任务归档时标记跟进
  总裁："这个方案归档，下周三下午再看"
  Lysander：
    → 方案归档到 obs/
    → 在 active_tasks.yaml 写入：
      status: pending_followup
      follow_up: { date: "2026-04-16", time: "14:00", action: "ask_president" }
      assigned_team: "rd"
    → 确认："已归档，RD团队将在下周三下午主动询问您。"

Step 2: 日常检查（每天自动）
  定时任务（早上）：
    → 读取 active_tasks.yaml
    → 扫描所有 pending_followup / pending_start / pending_confirmation
    → 检查 follow_up.date 是否 <= 今天
    → 如果有到期项 → 汇总 → 通过 Slack 发送给总裁

Step 3: 新会话检查（每次对话）
  Lysander 开场后：
    → 读取 active_tasks.yaml
    → 如果有到期/即将到期的跟进项
    → 在问候后立即汇报

Step 4: 总裁响应
  总裁看到提醒后：
    → 回复"执行" → Lysander 把 pending_start 改为 in_progress → 团队开始干活
    → 回复"推迟到下周" → Lysander 更新 follow_up.date
    → 回复"取消" → Lysander 把任务状态改为 cancelled
    → 来 Claude Code 详谈 → Lysander 提供完整上下文
```

## 三、与现有体系的整合

### 执行链扩展

```
现有：开场 → 目标 → 分级 → 派单 → 执行 → QA → 交付
新增：                                              ↓
                                               跟进管理
                                               ├── 完成 → 归档
                                               ├── 待跟进 → 写入follow_up → 到期提醒
                                               ├── 待确认 → 写入confirmation → 到期询问
                                               └── 待启动 → 写入start_date → 到期触发
```

### 新增定时任务

```
现有：
  6am  任务恢复
  8am  情报日报+进化分析
  10am 行动管线
  周一  HR审计
  周五  成长周报

新增：
  每天 9am — 待办跟进检查Agent
             → 扫描到期跟进项 → 汇总 → Slack通知总裁
```

### CLAUDE.md 增加的规则

```
任务归档时的强制行为：
当总裁说"以后再做"/"先归档"/"下次再说"时，
Lysander 必须：
1. 归档方案到对应目录
2. 主动询问："需要我在什么时候提醒您？"
3. 将跟进时间写入 active_tasks.yaml
4. 确认："已归档。[团队名]将在[日期]主动向您汇报。"

如果总裁没有指定跟进时间，默认设为3天后。
绝对不能归档后就忘了 — 每个归档都必须有跟进日期。
```

## 四、消息设计

### Slack 每日跟进消息模板

```
总裁早上好，以下是今日待跟进事项：

📋 待确认（需要您决策）：
  1. [RD] 微信公众号抓取方案 — 4月16日约定跟进
     上下文：Docker部署We-MP-RSS到服务器，预计2小时完成
     → 回复"执行"启动 / "推迟X天" / "取消"

⏰ 即将到期（明天）：
  2. [Growth] 首批客户拜访计划 — 4月17日跟进
     → 是否需要提前准备？

📊 本周还有：
  3. [Harness Ops] Synapse Core 分发仓库创建 — 4月19日
  4. [Content_ops] Harness Engineering 博客发布 — 4月20日

无需回复 = 按原计划。如需调整请回复对应编号。
```

### Claude Code 会话内提醒模板

```
总裁您好，我是 Lysander，Multi-Agents 团队为您服务！

📋 今日有 2 项待跟进事项：

1. [RD团队] 微信公众号抓取方案
   状态：待确认
   归档日：4月12日 | 约定跟进：今天下午
   方案摘要：Docker部署We-MP-RSS，对接n8n+Claude做内容摘要
   文档：obs/02-project-knowledge/wechat-article-scraper-plan.md
   → 是否启动执行？

2. [Growth团队] 首批客户拜访计划
   状态：待启动
   到期：明天
   → 是否需要团队准备材料？

请总裁指示，或直接下达今天的工作目标。
```

## 五、技术实现

### 需要修改的文件

| 文件 | 变更 | 说明 |
|------|------|------|
| active_tasks.yaml | 增加 follow_up 字段和新状态 | 数据结构扩展 |
| CLAUDE.md | 增加"归档必须设跟进日期"规则 | 行为约束 |
| hr_base.py | 增加 check_followups() 函数 | 扫描到期跟进项 |
| 新增定时任务 | 每日9am跟进检查Agent | Slack通知 |

### 需要新增的 Agent

不需要新增 Agent。由 execution_auditor（执行审计师）扩展职责 — 在执行链尾部增加"跟进管理"检查。

## 六、更广泛的服务模式思考

这个方案解决的不只是"下周三提醒一下"的问题，而是定义了 **Synapse 团队的服务姿态**：

```
被动服务（当前）：
  总裁说 → 我做
  总裁不说 → 我等

主动服务（目标）：
  总裁说 → 我做 → 做完告诉你
  总裁不说 → 我检查有没有该做的 → 有就提醒
  总裁归档了一个事 → 我记住 → 到时间我主动问
  我发现了重要信息 → 我主动汇报（不等你问）
  我完成了阶段工作 → 我主动交付（不等你催）

类比：
  被动 = 外包团队（给需求才动）
  主动 = 内部团队（自己管自己，定期汇报，适时请示）
```

## 七、评审

| 专家 | 评分 | 意见 |
|------|:----:|------|
| strategist | 5 | 这是 Synapse 从"工具"升级为"团队"的关键一步 |
| decision_advisor | 5 | Slack + 会话双渠道覆盖所有场景，风险低 |
| execution_auditor | 5 | 与执行链的整合自然，扩展尾部即可 |
| trend_watcher | 5 | Hermes Agent 等自进化系统都在走主动服务路线 |
| gtm_strategist | 5 | 对商业化有价值 — "AI团队主动服务"是差异化卖点 |

**均分 5.0 → 强烈推荐执行**
