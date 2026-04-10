---
title: Synapse Agent HR 管理体系
date: 2026-04-10
author: Graphify 智囊团 (strategist + decision_advisor)
tags: [Synapse, HR, Agent管理, 能力标准, 生命周期]
description: AI Agent 团队的人力资源管理制度，包含创建标准、能力评估、生命周期管理
---

# Synapse Agent HR 管理体系

## 一、体系定位

HR 管理体系是 Synapse 的**组织基础设施层**。没有它，Agent 想加就加、加完没人管、管了没标准。

```
HR 体系在 Synapse 中的位置：

  Synapse
  ├── 记忆层 (OBS)
  ├── 控制层 (Harness)
  ├── 执行层 (Multi-Agent)  ← HR管理的是这层的"人"
  ├── 进化层 (情报闭环)
  └── 决策层 (四级制)
       ↑
  HR 体系 = 执行层的质量保证
```

## 二、Agent Card 强制 Schema

所有 Agent 人员卡片必须包含以下字段，缺失任何必填项不得上岗。

### 必填字段

```yaml
# ── 身份信息（必填）──
specialist_id: string        # 唯一标识，snake_case，全局不重复
team: string                 # 所属团队 key
role: string                 # 中文角色名称
status: active | probation | inactive | retired  # 状态
type: ai_agent               # 类型

# ── 能力信息（必填，每项至少 3 条）──
domains:                     # 专业领域（3-6条）
  - string                   # 不得用"等"字结尾

capabilities:                # 核心能力（4-8条）
  - string                   # 必须具体到工具/方法论/框架级别
                             # 错误示例："项目管理"
                             # 正确示例："基于PRINCE2的项目治理设计"

experience:                  # 经验背景（2-5条）
  - string                   # 必须说明具体领域或技术栈

# ── 运营信息（必填）──
availability: available | busy | unavailable
workload: low | medium | high
max_concurrent_tasks: integer
召唤关键词: [string, ...]    # 至少 4 个关键词
```

### 能力描述质量标准

| 级别 | 标准 | 示例 |
|------|------|------|
| **A级（优秀）** | 具体到工具+方法论+产出物 | "基于 pytest + Playwright 的端到端测试框架搭建与维护" |
| **B级（合格）** | 具体到方法论/框架 | "SWOT分析、PEST分析、波特五力模型应用" |
| **C级（不合格）** | 仅活动名称 | "项目管理"、"知识沉淀"、"质量审核" |

**C级能力描述不得出现在任何正式卡片中。**

### 状态定义

| 状态 | 含义 | 条件 |
|------|------|------|
| `probation` | 试用期 | 新建后默认状态，需通过能力评审 |
| `active` | 正式在岗 | 通过能力评审，HR Director 批准 |
| `inactive` | 暂停 | 能力不达标或暂时不需要 |
| `retired` | 退役 | 永久移除，卡片保留归档 |

## 三、Agent 生命周期管理

```
需求提出 → 可行性评估 → 角色设计 → 能力定义 → 评审入职
    ↓                                              ↓
 Lysander                                     HR Director
 提出需要新角色                                审核卡片质量
                                                   ↓
                                              试用期(probation)
                                                   ↓
                                              能力评审(30天内)
                                                   ↓
                                         ┌─── 通过 → active
                                         └─── 不通过 → 修订 或 retired
```

### 3.1 创建流程（新增 Agent）

**Step 1：需求论证**
- Lysander 或团队负责人提出新增需求
- 说明：为什么需要新角色？现有角色无法覆盖？
- HR Director 评估是否可由现有 Agent 扩展能力替代

**Step 2：角色设计**
- Capability Architect 设计角色定位
- 明确与现有角色的边界（不能有 >30% 的能力重叠）
- 定义该角色的核心差异化价值

**Step 3：卡片撰写**
- 按强制 Schema 填写所有字段
- 能力描述必须达到 B 级或以上
- 至少 4 个召唤关键词，不得与现有 Agent 关键词重叠 >50%

**Step 4：入职评审**
- HR Director 审核卡片完整性和质量
- Capability Architect 审核能力合理性
- 通过 → status: probation → 30天后正式评审
- 不通过 → 退回修改

**Step 5：同步配置**
- 卡片存入 `HR/personnel/{team}/`
- 更新 `organization.yaml` 团队成员列表
- 更新 `*_experts.yaml` Agent 配置
- 更新路由关键词

### 3.2 定期评审（现有 Agent）

**频率**：由情报行动管线触发（当AI行业出现新技术/新工具时自动评审）

**评审维度**（每项 1-5 分）：

| 维度 | 说明 | 权重 |
|------|------|:----:|
| 能力时效性 | 技能是否过时？是否跟上行业发展？ | 30% |
| 描述质量 | 是否达到 B 级标准？是否具体可执行？ | 25% |
| 使用频率 | 是否被任务路由频繁匹配？还是长期闲置？ | 20% |
| 差异化 | 与其他 Agent 是否有清晰边界？ | 15% |
| Schema合规 | 是否包含所有必填字段？ | 10% |

**处置规则**：
- 均分 >= 4.0 → 保持 active
- 均分 3.0-3.9 → 发出能力提升通知，限期修订
- 均分 < 3.0 → 降级为 inactive，评估是否 retire
- Schema 不合规 → 立即要求修订，不合格则 inactive

### 3.3 能力进化

当以下事件发生时，HR 团队主动更新相关 Agent 的能力卡片：

| 触发事件 | 动作 |
|----------|------|
| 情报日报发现新工具/框架 | 评估哪些 Agent 应增加此能力 |
| Agent 成功完成新类型任务 | 将新能力写入卡片 |
| 行业技术栈发生重大变化 | 全面审查相关团队的技术栈描述 |
| Lysander 创建新团队 | HR 全程参与角色设计和卡片撰写 |

### 3.4 退役流程

- HR Director 提出退役建议（附理由）
- 智囊团评审确认
- status 改为 `retired`
- 从 organization.yaml 移除
- 卡片保留在 `HR/personnel/{team}/` 归档（不删除）

## 四、HR 团队职责

| 角色 | 核心职责 |
|------|----------|
| **HR Director** | 审批入职/退役、主导定期评审、管理组织架构变更 |
| **Capability Architect** | 设计能力标准、审核能力描述质量、规划能力进化路径 |

## 五、与情报闭环的联动

```
情报日报 → 发现新AI技术/工具
    ↓
行动管线 → 评估：是否需要更新 Agent 能力？
    ↓
    ├── 现有 Agent 能力升级 → capability_architect 更新卡片
    ├── 需要新 Agent → hr_director 启动创建流程
    └── 现有 Agent 过时 → hr_director 启动评审/退役
```
