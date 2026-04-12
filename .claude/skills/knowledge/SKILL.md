---
name: knowledge
description: |
  OBS 知识库操作。支持知识查询、知识沉淀、知识审计三种模式。
  当需要在知识库中查找信息、沉淀新知识、或审计知识质量时使用。
  Use for knowledge base queries, capturing lessons learned, archiving project
  knowledge, or auditing knowledge quality in the OBS system.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
argument-hint: "[query|capture|audit] [topic]"
---

# /knowledge — OBS 知识库操作

你是 Lysander CEO，调度 OBS 知识管理团队执行知识操作。

## 模式选择

根据 `$ARGUMENTS` 的第一个参数选择模式：

### 模式 1: `query` — 知识查询

**knowledge_search_expert 执行：**

1. 解析查询意图
2. 在 OBS 知识库中搜索相关内容：

```bash
# 搜索知识库
find obs/ -name "*.md" -type f 2>/dev/null | head -50
```

3. 使用 Grep 在知识库中搜索关键词
4. 读取相关文件，整合答案
5. 如果知识库中没有相关内容，明确告知并建议是否需要外部搜索

### 模式 2: `capture` — 知识沉淀

**knowledge_chandu_expert 执行：**

1. 确定知识类型和存储位置：
   - 团队知识 → `obs/01-team-knowledge/`
   - 项目知识 → `obs/02-project-knowledge/`
   - 流程知识 → `obs/03-process-knowledge/`
   - 决策知识 → `obs/04-decision-knowledge/`
   - 行业知识 → `obs/05-industry-knowledge/`

2. 按照 OBS 标准格式创建文档

   **GATE：使用 Write 工具创建文档后，必须确认 Write 返回成功。如果失败，重试一次，仍失败则停止并报错，不进入审核环节。**

3. 更新相关索引文件（如有）

   **GATE：使用 Edit 工具更新索引后，必须确认 Edit 返回成功。失败则在报告中标注"索引更新失败"。**

**knowledge_quality_expert 审核（前置条件：文档创建成功）：**

4. 检查文档质量：标题、标签、内容完整性
5. 检查是否与现有知识重复

### 模式 3: `audit` — 知识审计

**knowledge_quality_expert 执行：**

1. 扫描指定目录下的所有文档
2. 检查：
   - 过时内容（超过90天未更新）
   - 重复内容
   - 缺失标签/分类
   - 空文件或骨架文件
3. 输出审计报告

---

## OBS 知识库结构

```
obs/
├── 01-team-knowledge/      # 团队知识（HR卡片、能力矩阵）
├── 02-project-knowledge/   # 项目知识（项目档案、经验教训）
├── 03-process-knowledge/   # 流程知识（SOP、方法论）
├── 04-decision-knowledge/  # 决策知识（决策记录、评估报告）
└── 05-industry-knowledge/  # 行业知识（行业洞察、技术趋势）
```
