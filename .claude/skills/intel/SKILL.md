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

### Phase 3: 知识沉淀（GATE：验证写入成功）

如果情报具有长期价值，写入 OBS 知识库：
- 行业知识 → `obs/05-industry-knowledge/`
- 技术情报 → `obs/05-industry-knowledge/tech/`
- 决策相关 → `obs/04-decision-knowledge/`

**GATE：使用 Write 工具写入文件后，必须确认 Write 返回成功。如果写入失败，重试一次，仍失败则在情报报告末尾标注"知识沉淀写入失败，需手动处理"，不可静默跳过。**

### Phase 4: Sources 引用

必须在末尾列出所有信息来源，格式：
```
Sources:
- [标题](URL)
```

---

## 测试场景（强制，交付前必须通过）

### test_scenarios

#### Golden Path: 指定主题情报收集与分析

- **场景名称**：用户对指定主题执行完整情报收集流程
- **输入**：`/intel AI Agent 测试方法论`
- **前置条件**：
  - WebSearch / WebFetch 工具可用
  - `obs/05-industry-knowledge/` 目录存在
- **预期结果**：
  - [ ] Phase 1：至少执行 2 次 WebSearch（中英文各一次）
  - [ ] Phase 1：对有价值结果调用 WebFetch 提取详细内容
  - [ ] Phase 2：输出包含完整结构化格式：概况 / 关键发现（附来源） / 实践价值评估 / 建议行动
  - [ ] Phase 2：实践价值评估包含三个维度：相关性、可行动性、风险点
  - [ ] Phase 3：情报具有长期价值时写入 `obs/05-industry-knowledge/tech/` 或对应目录
  - [ ] Phase 3 GATE：Write 工具返回成功，否则重试一次，仍失败则报告末尾标注"知识沉淀写入失败"
  - [ ] Phase 4：末尾包含 Sources 列表，每条含标题和 URL
  - [ ] 工具调用链：`WebSearch(中文) -> WebSearch(英文) -> WebFetch(详情) -> Write(OBS沉淀)`

#### Edge Case 1: 搜索无结果时的降级处理

- **场景名称**：WebSearch 返回空结果或极少结果时的行为
- **输入**：`/intel 某个极小众且不存在的虚构技术名称XYZ12345`
- **前置条件**：
  - WebSearch 工具可用但搜索主题无匹配结果
- **预期结果**：
  - [ ] 不中断流程、不抛错退出
  - [ ] 尝试关联主题搜索（调整关键词、扩大范围）
  - [ ] 如果多次搜索均无结果，明确告知用户"未找到相关情报"
  - [ ] 不生成虚构内容填充报告
  - [ ] 跳过 Phase 3 知识沉淀（无有价值内容可沉淀）
  - [ ] 建议行动改为建议替代搜索方向或关键词

#### Edge Case 2: WebFetch 失败时的降级处理

- **场景名称**：WebSearch 有结果但 WebFetch 无法提取详细内容
- **输入**：`/intel 某个正常主题`
- **前置条件**：
  - WebSearch 返回正常结果
  - WebFetch 对目标 URL 返回错误（403/超时等）
- **预期结果**：
  - [ ] 基于 WebSearch 摘要信息完成情报整合，不中断流程
  - [ ] 关键发现来源标注为搜索摘要（非全文提取）
  - [ ] 报告中注明部分来源未能获取全文
