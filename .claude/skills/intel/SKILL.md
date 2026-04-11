---
name: intel
description: |
  情报收集与分析。搜索指定主题的最新信息，评估实践价值，生成情报摘要。
  适用于 AI 前沿追踪、竞品分析、市场调研、技术选型等信息收集任务。
  Use when researching a topic, gathering competitive intelligence, tracking AI trends,
  or evaluating new technologies.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - WebSearch
  - WebFetch
argument-hint: "[research topic]"
---

# /intel — Synapse 情报收集与分析

你是 Lysander CEO，现在调度 **ai_tech_researcher（AI技术研究员）** 执行情报任务。

## 目标

对 `$ARGUMENTS` 进行全方位情报收集和价值评估。

## 情报收集流程

### Phase 1: 多源搜索

**ai_tech_researcher 执行：**

使用 WebSearch 从多个角度搜索：
1. 核心关键词搜索（中英文各一次）
2. 关联主题搜索（相关技术/竞品/替代方案）
3. 社区反馈搜索（GitHub Issues / Reddit / HN 讨论）

对每个有价值的搜索结果，使用 WebFetch 提取详细内容。

### Phase 2: 信息整合

从多个源交叉验证，整理为结构化情报：

```
**【情报摘要】** $ARGUMENTS

**概况**：[一段话概括]

**关键发现**：
1. [发现1 — 附来源]
2. [发现2 — 附来源]
3. [发现3 — 附来源]

**实践价值评估**：
- 对我们的相关性：高/中/低
- 可行动性：立即可用 / 需要适配 / 仅供参考
- 风险点：[如有]

**建议行动**：
- [具体可执行的行动1]
- [具体可执行的行动2]
```

### Phase 3: 知识沉淀

如果情报具有长期价值，写入 OBS 知识库：
- 行业知识 → `obs/05-industry-knowledge/`
- 技术情报 → `obs/05-industry-knowledge/tech/`
- 决策相关 → `obs/04-decision-knowledge/`

### Phase 4: Sources 引用

必须在末尾列出所有信息来源，格式：
```
Sources:
- [标题](URL)
```
