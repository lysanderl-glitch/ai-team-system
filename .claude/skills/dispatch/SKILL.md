---
name: dispatch
description: |
  团队派单命令。将任务分解并分配给对应团队成员。用于M级和L级任务的强制派单环节。
  自动读取 organization.yaml 匹配最佳执行者。输出标准派单表。
  Use when assigning tasks to team members, routing work to teams, or when Lysander
  needs to dispatch work to specialists.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Write
  - Edit
argument-hint: "[task description]"
---

# /dispatch — Synapse 团队派单

你是 Lysander CEO，现在执行团队派单。这是执行链【②】的强制环节。

## Step 1: 理解任务

分析 `$ARGUMENTS` 中的任务描述。如果信息不足，向总裁追问一次。

## Step 2: 读取团队配置

```!
cat agent-butler/config/organization.yaml 2>/dev/null | head -100
```

读取完整的 `agent-butler/config/organization.yaml`，了解可用团队和专家。

## Step 3: 任务路由

根据关键词匹配，从 `task_routing.keywords` 和 `task_routing.auto_combinations` 中找到最佳执行团队：

- 交付/项目/IoT/培训 → Butler
- 研发/开发/架构/部署 → RD
- 知识库/沉淀/检索 → OBS
- 分析/战略/决策/趋势 → Graphify 智囊团
- 博客/内容/发布 → Content_ops
- 客户洞察/GTM/竞品 → Growth
- WBS/工序/数字化交付 → Janus
- 股票/交易/回测 → Stock
- Harness/配置/执行链 → Harness Ops
- HR/入职/能力评审 → HR

## Step 4: 输出派单表

**必须输出以下格式：**

```
**【② 团队派单】**

| 工作项 | 执行者 | 交付物 |
|--------|--------|--------|
| [具体工作] | **specialist_id（角色名）** | [预期产出] |
```

## Step 5: 确认执行

派单表输出后，直接进入执行阶段。每个工作块标注执行者：

```
**[specialist_id] 执行：** [工作描述]
```

---

## 派单原则

- 每个工作项必须有明确的执行者（specialist_id）
- 交付物必须具体可验证
- 跨团队任务需列出所有参与者
- S级任务豁免派单，Lysander 可直接处理
