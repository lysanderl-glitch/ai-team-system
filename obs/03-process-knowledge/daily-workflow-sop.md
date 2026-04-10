---
title: 日常工作流 SOP
category: 流程知识
tags: [SOP, 日常工作流, AI团队, 工作记录]
created: 2026-04-10
author: Lysander
version: 0.3
type: SOP
---

# 日常工作流 SOP v0.3

## 工作环境

| 工具 | 用途 |
|------|------|
| **Claude Code** (ai-team-system) | AI 团队协作、任务执行 |
| **Obsidian** (ai-team-system vault) | 团队知识库、工作记录、第二大脑 |

---

## 每日流程

### 开启新会话

在 Claude Code 中打开 `ai-team-system` 目录，Lysander 自动问候：

> 总裁您好，我是 Lysander，Multi-Agents 团队为您服务！

**目标同步**：向 Lysander 说明今天的业务目标或当前阶段重点。

---

### 执行链（每项任务必须遵守）

```
【开场】Lysander 问候
   ↓
【0】目标同步 — 总裁说明目标，Lysander 确认对齐
   ↓
【①】智囊团共识 — 分析目标，制定策略
   ↓
【②】方案确认 — 总裁批准后执行
   ↓
【③】执行团队共识 — 说明目标/需求/验收标准
   ↓
【④】执行
   ↓
【⑤】QA 审查 — 审查通过才推进
   ↓
【⑥】决策上报（如需）
```

---

### 工作记录

每次工作会话结束后，在 `00-daily-work/` 下创建当日工作记录。

**文件命名：** `YYYY-MM-DD-work-record.md`

**使用模板：** [[工作记录模板]]

---

### 知识沉淀

工作中产生的重要知识，存入对应分类：

| 知识类型 | 存放位置 |
|----------|----------|
| 团队协作、人员、角色 | `01-team-knowledge/` |
| 项目进展、需求、技术方案 | `02-project-knowledge/` |
| 流程、SOP、操作规范 | `03-process-knowledge/` |
| 决策记录、选型分析 | `04-decision-knowledge/` |
| 行业分析、竞品、趋势 | `05-industry-knowledge/` |

---

### 收尾

- obsidian-git 每 5 分钟自动推送到 GitHub，无需手动操作
- 如有重要凭证更新，在 Obsidian 打开 `credentials.mdenc` 维护

---

## 工作原则

- **不以时间切割任务**：只说"A完成后做B"，不说"今天做A明天做B"
- **紧盯目标持续执行**：未达成目标不停止，不因换会话中断
- **未完成必须跟进**：每次 QA 审查时检查遗留项，有则继续

---

## 相关文档

- [[工作记录模板]]
- [[OBS第二大脑2.0系统说明]]
- [[凭证管理说明]]
