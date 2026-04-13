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

---

## 测试场景（强制，交付前必须通过）

### test_scenarios

#### Golden Path 1: 知识查询模式

- **场景名称**：用户通过 query 模式在 OBS 中查找已有知识
- **输入**：`/knowledge query SSH配置`
- **前置条件**：
  - `obs/` 目录存在且包含 Markdown 文件
  - 知识库中存在包含"SSH"关键词的文档
- **预期结果**：
  - [ ] 解析查询意图为关键词搜索
  - [ ] 使用 Grep 在 `obs/` 中搜索关键词
  - [ ] 读取匹配文件，整合为结构化答案
  - [ ] 输出包含来源文件路径
  - [ ] 不修改任何文件（纯查询操作）
  - [ ] 工具调用链：`Grep(obs/) -> Read(匹配文件) -> 输出答案`

#### Golden Path 2: 知识沉淀模式

- **场景名称**：用户通过 capture 模式沉淀新知识到 OBS
- **输入**：`/knowledge capture MCP集成最佳实践：配置步骤和注意事项...`
- **前置条件**：
  - `obs/03-process-knowledge/` 目录存在
- **预期结果**：
  - [ ] 根据内容类型自动判定存储目录（流程知识 → `obs/03-process-knowledge/`）
  - [ ] 使用 Write 创建标准格式 Markdown 文档
  - [ ] GATE：Write 返回成功确认，失败则重试一次，仍失败则停止并报错
  - [ ] 如有索引文件，使用 Edit 更新索引
  - [ ] GATE：Edit 返回成功确认，失败则标注"索引更新失败"
  - [ ] knowledge_quality_expert 审核：检查标题、标签、内容完整性
  - [ ] 审核包含去重检查（与现有知识对比）
  - [ ] 工具调用链：`Glob(obs/) -> Write(新文档) -> Edit(索引) -> Grep(去重检查)`

#### Edge Case 1: 查询无结果时的处理

- **场景名称**：查询关键词在 OBS 知识库中完全无匹配
- **输入**：`/knowledge query 量子计算编程框架`
- **前置条件**：
  - `obs/` 目录存在但不包含相关内容
- **预期结果**：
  - [ ] Grep 搜索返回空结果
  - [ ] 明确告知用户"知识库中未找到相关内容"
  - [ ] 建议是否需要外部搜索（提示可使用 `/intel`）
  - [ ] 不生成虚构内容
  - [ ] 不修改任何文件

#### Edge Case 2: audit 模式扫描发现问题

- **场景名称**：审计指定目录时发现质量问题
- **输入**：`/knowledge audit obs/03-process-knowledge/`
- **前置条件**：
  - 目标目录存在且包含文档
  - 部分文档超过 90 天未更新或缺少标签
- **预期结果**：
  - [ ] 扫描目录下所有 `.md` 文件
  - [ ] 检查四项指标：过时内容 / 重复内容 / 缺失标签 / 空文件
  - [ ] 输出结构化审计报告，列出具体问题文件和改进建议
  - [ ] 不自动修改文件（仅报告，修改需额外指令）
