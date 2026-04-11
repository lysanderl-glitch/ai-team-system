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

## Step 4: 输出技术方案文档

将完整方案写入 Artifact 文件，供下游 `/dev-review` 和 `/dev-qa` 消费：

```
文件路径：.dev-artifacts/plan-[feature-name].md
```

## Step 5: 决策记录

重大架构决策记录到 OBS：`obs/04-decision-knowledge/adr/`
