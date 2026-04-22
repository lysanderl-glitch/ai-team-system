# Synapse 产品委员会章程

**建立时间**：2026-04-22
**授权**：总裁刘子杨批准
**主席**：Lysander CEO

## 组织构成

| 角色 | 成员 | 职责 |
|------|------|------|
| 主席 | Lysander CEO | 主持会议，L3决策 |
| 执行秘书 | synapse_product_owner | 议程准备，决议执行，路线图维护 |
| 常委 | strategy_advisor | 战略对齐评审 |
| 常委 | execution_auditor | 执行链审计 |
| 列席（轮值） | 各产品线业务代表 | 提供一线反馈 |

## 决策权限

| 事项 | 级别 | 决策者 |
|------|------|--------|
| 日常功能评审 | L3 | Lysander + synapse_product_owner |
| 需求优先级排序 | L3 | Lysander + synapse_product_owner |
| 技术方案评审 | L2 | 专家评审（harness_ops团队） |
| Bug修复决策 | L1 | 自动（integration_qa） |
| Agent能力调整 | L3 | HR + Lysander |
| 大版本发布 | L4 | 总裁验收 |
| 战略方向 | L4 | 总裁 |

## 会议机制

- **产品委员会会议**：每个大版本启动时召开（不定期，由synapse_product_owner发起）
- **版本规划会**：每次大版本前，synapse_product_owner + Lysander对齐
- **季度战略对齐**：总裁参与（每季度1次，总裁主动发起）

## 产品研发双轨制流程

```
需求池 → PRD → 版本规划 → [工程轨开发] → Alpha → Beta → UAT → 总裁验收 → 发布
         ↑          ↑         ↑                 ↑       ↑      ↑
      产品委员会  产品委员会  产品轨监督        集成测试  E2E  PMO+PM
```

## 质量门禁（5个同步节点，不可跳过）

1. **PRD评审**：synapse_product_owner + Lysander + 工程可行性确认
2. **启动会**：WBS拆解 + Sprint规划
3. **Alpha**：集成测试通过（integration_qa）
4. **Beta**：E2E测试通过（qa_engineer）
5. **发布评审**：总裁大版本验收

## 总裁参与边界

总裁仅参与：
1. 季度战略对齐会
2. 大版本发布前验收（每版本1次）
3. L4决策（法律/预算>100万/公司存续）

其余所有事项由Lysander + 产品委员会全权处理。
