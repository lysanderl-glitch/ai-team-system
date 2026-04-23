---
title: product_ops 产品组织集成验证清单
created: 2026-04-22
purpose: Synapse体系合并后校验 product_ops 能力是否完整集成
status: pending_verification
---

# product_ops 产品组织 — 集成验证清单

> 本文档记录 2026-04-22 会话中建立的产品组织完整信息。
> Synapse 体系合并完成后，逐项核对以下清单，确认能力已完整集成。

---

## 一、新增 Agent 清单（2个）

### ✅ Agent 1：Synapse 首席产品官

| 字段 | 值 |
|------|----|
| specialist_id | `synapse_product_owner` |
| 文件路径 | `obs/01-team-knowledge/HR/personnel/product_ops/synapse_product_owner.md` |
| team | `product_ops` |
| status | `active`（capability_architect 审计 99/100） |
| 汇报对象 | Lysander CEO（L3）/ 总裁（L4 大版本验收） |
| max_concurrent_tasks | 3 |

**核心能力（必须在合并后保留）：**
- 基于 Jobs-To-Be-Done 框架的产品需求挖掘与用户场景建模
- PRD撰写（含用户故事、RICE优先级评分、验收标准定义）
- 产品路线图管理（Now-Next-Later 三层规划法 + OKR 对齐）
- 跨产品线架构协调（API契约设计、数据模型对齐、依赖管理）
- 产品度量体系设计（North Star Metric + 输入/输出指标拆解）
- 版本发布策略（灰度发布方案、回滚预案、发布清单管理）

**召唤关键词：** 产品规划、PRD、路线图、版本规划、产品委员会、需求评审、产品化

---

### ✅ Agent 2：需求分析师

| 字段 | 值 |
|------|----|
| specialist_id | `requirements_analyst` |
| 文件路径 | `obs/01-team-knowledge/HR/personnel/product_ops/requirements_analyst.md` |
| team | `product_ops` |
| status | `active`（审计 95/100） |
| 汇报对象 | synapse_product_owner |
| max_concurrent_tasks | 5 |

**核心能力（必须在合并后保留）：**
- 结构化需求捕获（5W2H框架 + 用户故事映射）
- 需求去重与聚类分析（基于语义相似度 + 业务场景分类）
- 需求价值评分（RICE模型：Reach/Impact/Confidence/Effort 计算）
- 需求依赖关系建模（前置依赖图 + 关键路径分析）
- 多源需求整合（口头需求提取、情报启发转化、用户反馈结构化）
- 需求文档版本管理（requirements_pool.yaml CRUD操作）

**召唤关键词：** 需求分析、需求池、RICE评分、需求建模、用户故事、需求捕获

---

## 二、虚拟产品组织 — Synapse 产品委员会

| 字段 | 值 |
|------|----|
| 章程文件 | `obs/02-product-knowledge/product_committee_charter.md` |
| 建立时间 | 2026-04-22 |
| 授权 | 总裁刘子杨批准 |

**成员构成：**

| 角色 | 成员 | 职责 |
|------|------|------|
| 主席 | Lysander CEO | 主持会议，L3决策 |
| 执行秘书 | synapse_product_owner | 议程准备，决议执行，路线图维护 |
| 常委 | strategy_advisor | 战略对齐评审 |
| 常委 | execution_auditor | 执行链审计 |
| 列席（轮值） | 各产品线业务代表 | 提供一线反馈 |

**决策权限矩阵：**

| 事项 | 级别 | 决策者 |
|------|------|--------|
| 日常功能评审 | L3 | Lysander + synapse_product_owner |
| 需求优先级排序 | L3 | Lysander + synapse_product_owner |
| 技术方案评审 | L2 | harness_ops 团队 |
| Bug 修复决策 | L1 | integration_qa（自动） |
| Agent 能力调整 | L3 | HR + Lysander |
| 大版本发布 | L4 | 总裁验收 |
| 战略方向 | L4 | 总裁 |

**会议召开时机：** 每个大版本启动时，由 synapse_product_owner 发起。

**总裁参与边界：** 仅参与季度战略对齐、大版本验收、L4决策。

---

## 三、配套产品基础设施文件

| 文件 | 说明 | 验证方式 |
|------|------|---------|
| `obs/02-product-knowledge/requirements_pool.yaml` | 需求池（REQ-001~009，含 RICE 评分） | 文件存在且含 REQ-001~009 |
| `obs/02-product-knowledge/prd-v200-pmo-auto.md` | PMO Auto V2.0 PRD（458行，9章节） | 文件存在且含9个章节标题 |
| `obs/02-product-knowledge/product_committee_charter.md` | 产品委员会章程 | 文件存在且含5个质量门禁节点 |
| `agent-butler/config/organization.yaml` | product_ops 团队注册（13个路由关键词） | yaml 中存在 `product_ops:` 节 |

---

## 四、组织路由关键词（organization.yaml 验证项）

合并后 `organization.yaml` 中 `product_ops` 团队必须包含以下路由关键词：

```
产品规划, PRD, 路线图, 版本规划, 产品委员会,
需求评审, 产品化, 需求分析, 需求池, RICE评分,
需求建模, 用户故事, 需求捕获
```

---

## 五、研发模式变更（重要）

| 旧模式 | 新模式 |
|--------|--------|
| 作坊式（总裁驱动，无产品规划） | 双轨制（产品轨 + 工程轨） |

**5个质量门禁节点（不可跳过）：**
1. PRD评审：synapse_product_owner + Lysander + 工程可行性确认
2. 启动会：WBS拆解 + Sprint规划
3. Alpha：集成测试通过（integration_qa）
4. Beta：E2E测试通过（qa_engineer）
5. 发布评审：总裁大版本验收

---

## 六、集成验证 Checklist

合并完成后逐项勾选：

- [ ] `synapse_product_owner.md` 文件存在，status=active
- [ ] `requirements_analyst.md` 文件存在，status=active
- [ ] `product_committee_charter.md` 文件存在
- [ ] `requirements_pool.yaml` 文件存在，含 REQ-001~009
- [ ] `prd-v200-pmo-auto.md` 文件存在
- [ ] `organization.yaml` 中 `product_ops` 团队存在，含13个路由关键词
- [ ] Lysander 能正确路由"产品规划"/"PRD"/"需求分析"类请求到 product_ops 团队
- [ ] 产品委员会章程中的决策权限矩阵在 Harness 中生效
- [ ] 双轨制研发流程已在 CLAUDE.md 或执行链中体现（若需要）
