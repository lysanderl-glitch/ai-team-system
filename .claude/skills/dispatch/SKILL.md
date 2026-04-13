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

---

## 测试场景（强制，交付前必须通过）

### test_scenarios

#### Golden Path: 标准任务派单

- **场景名称**：明确任务描述派单到正确团队
- **输入**：`/dispatch 优化 hr_base.py 中的 audit_all_agents 函数性能`
- **前置条件**：
  - `agent-butler/config/organization.yaml` 已存在且包含 Harness Ops 团队配置
  - organization.yaml 中 `task_routing` 节包含关键词路由规则
- **预期结果**：
  - [ ] 工具调用链：`Bash(cat organization.yaml) -> Read(organization.yaml)`
  - [ ] 关键词"代码/开发"命中 Harness Ops 或 RD 团队
  - [ ] 输出标准派单表格式：`**【② 团队派单】**` + 三列表格（工作项 / 执行者 / 交付物）
  - [ ] 执行者字段包含 specialist_id（如 `ai_systems_dev`）
  - [ ] 交付物字段具体可验证（如"优化后的函数 + 性能对比"）
  - [ ] 派单表后有执行者标注的工作块标题（如 `**ai_systems_dev 执行：**`）

#### Edge Case 1: 任务描述无法明确匹配团队

- **场景名称**：模糊任务描述的路由处理
- **输入**：`/dispatch 把那个东西弄好一点`
- **前置条件**：
  - `agent-butler/config/organization.yaml` 正常存在
- **预期结果**：
  - [ ] 不直接猜测团队，而是向总裁追问一次以明确任务范围
  - [ ] 追问内容包含"请补充具体任务内容"或类似提示
  - [ ] 追问中可列出常见团队方向供选择
  - [ ] 不输出不完整的派单表

#### Edge Case 2: 跨团队任务

- **场景名称**：任务涉及多个团队协作
- **输入**：`/dispatch 开发新的情报收集功能并沉淀到知识库`
- **前置条件**：
  - organization.yaml 包含 RD 团队和 OBS 团队
- **预期结果**：
  - [ ] 派单表包含多个工作项，分属不同团队
  - [ ] 至少包含 RD 团队成员（开发）和 OBS 团队成员（知识沉淀）
  - [ ] 工作项之间有明确的依赖关系说明（如"A完成后做B"）
