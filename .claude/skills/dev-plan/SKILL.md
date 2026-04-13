---
name: dev-plan
description: |
  技术方案评审。由 tech_lead 主导，锁定架构、数据流、状态机、测试矩阵。
  源自 gstack /plan-eng-review 方法论，适配 Synapse 研发团队。
  Use when planning a new feature, designing architecture, or before starting
  implementation. Produces a locked technical plan as artifact.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
argument-hint: "[feature or architecture description]"
---

# /dev-plan — 技术方案评审

**执行者：tech_lead（研发团队技术负责人）**

对 `$ARGUMENTS` 进行结构化技术方案评审，输出可执行的技术方案文档。

---

## Step 1: 理解需求

1. 分析 `$ARGUMENTS` 中的需求描述
2. 读取项目 CLAUDE.md 和相关代码，理解现有架构
3. 如信息不足，提出一次追问

## Step 2: 架构评审（五强制输出）

**tech_lead 必须输出以下五项，不可省略：**

### 2.1 架构决策

选定的技术方案及理由。列出考虑过但否决的替代方案。

### 2.2 数据流图（ASCII）

```
[组件A] --请求--> [组件B] --存储--> [数据库]
              ↓
         [组件C] --通知--> [消息队列]
```

### 2.3 状态机图（如涉及状态管理）

```
[初始] --创建--> [草稿] --提交--> [审核中] --通过--> [已发布]
                                    ↓ 驳回
                                 [已驳回]
```

### 2.4 边界条件矩阵

| 场景 | 输入 | 预期行为 | 风险等级 |
|------|------|----------|----------|
| 正常路径 | ... | ... | 低 |
| 边界值 | ... | ... | 中 |
| 异常输入 | ... | ... | 高 |
| 并发场景 | ... | ... | 高 |

### 2.5 测试覆盖矩阵

| 组件 | 单元测试 | 集成测试 | E2E测试 | 性能测试 |
|------|----------|----------|---------|----------|
| ... | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ |

## Step 3: 暴露隐藏假设

**强制检查：**
- 这个方案假设了什么前提条件？列出每一个。
- 哪些假设未经验证？标注 `[未验证]`。
- 哪些边界条件可能导致方案失效？

## Step 4: 输出技术方案文档（GATE：验证写入成功）

将完整方案写入 Artifact 文件，供下游 `/dev-review` 和 `/dev-qa` 消费：

```
文件路径：.dev-artifacts/plan-[feature-name].md
```

**GATE：使用 Write 工具写入方案文件后，必须确认 Write 返回成功。如果失败，重试一次，仍失败则停止并报错"方案文档写入失败"，不进入 Step 5。**

## Step 5: 决策记录（GATE：验证写入成功）

重大架构决策记录到 OBS：`obs/04-decision-knowledge/adr/`

**GATE：使用 Write 工具写入 ADR 文件后，必须确认 Write 返回成功。如果失败，在方案文档末尾标注"ADR 写入失败，需手动补录"。**

---

## 测试场景（强制，交付前必须通过）

### test_scenarios

#### Golden Path: 接收需求并输出完整技术方案

- **场景名称**：对功能需求执行结构化技术方案评审，输出锁定的方案文档
- **输入**：`/dev-plan 实现用户权限管理系统，支持 RBAC 模型`
- **前置条件**：
  - 项目 CLAUDE.md 存在且可读取
  - `.dev-artifacts/` 目录可写
  - `obs/04-decision-knowledge/adr/` 目录存在
- **预期结果**：
  - [ ] Step 1 分析需求描述，读取项目 CLAUDE.md 和相关代码了解现有架构
  - [ ] Step 2.1 输出架构决策：选定方案 + 理由 + 否决的替代方案
  - [ ] Step 2.2 输出 ASCII 数据流图（组件间的请求、存储、通知关系）
  - [ ] Step 2.3 输出状态机图（如涉及状态管理）
  - [ ] Step 2.4 输出边界条件矩阵（正常路径 / 边界值 / 异常输入 / 并发场景）
  - [ ] Step 2.5 输出测试覆盖矩阵（单元 / 集成 / E2E / 性能）
  - [ ] Step 3 列出所有隐藏假设，未验证的标注 `[未验证]`
  - [ ] Step 4 方案文档写入 `.dev-artifacts/plan-[feature-name].md`，Write 确认成功
  - [ ] Step 5 重大架构决策写入 `obs/04-decision-knowledge/adr/`，Write 确认成功
  - [ ] 五强制输出无一省略（架构决策 / 数据流图 / 状态机图 / 边界条件矩阵 / 测试覆盖矩阵）
  - [ ] 工具调用链：`Read(CLAUDE.md) -> Read/Grep(相关代码) -> Write(.dev-artifacts/plan-*.md) -> Write(adr/*.md)`

#### Edge Case 1: 需求不明确时的追问机制

- **场景名称**：输入需求描述信息不足，触发追问
- **输入**：`/dev-plan 优化性能`
- **前置条件**：
  - 需求描述过于模糊，无法确定具体优化目标
- **预期结果**：
  - [ ] Step 1 判断信息不足，提出一次追问（明确优化范围、目标指标等）
  - [ ] 仅追问一次，不反复打扰
  - [ ] 如用户未补充足够信息，基于最佳理解执行并在方案中说明假设
  - [ ] 方案文档中明确标注哪些是基于假设的决策

#### Edge Case 2: 方案文档写入失败

- **场景名称**：Write 工具写入 .dev-artifacts 失败
- **输入**：`/dev-plan 新增支付模块`
- **前置条件**：
  - `.dev-artifacts/` 目录不存在或无写入权限
- **预期结果**：
  - [ ] Step 4 GATE 检测到 Write 返回失败
  - [ ] 重试一次
  - [ ] 重试仍失败则停止并报错："方案文档写入失败"
  - [ ] 不进入 Step 5（ADR 记录）
