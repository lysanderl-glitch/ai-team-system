---
name: hr-audit
description: |
  HR Agent 审计。检查所有 Agent 人员卡片的完整性和能力描述质量。
  评分制（满分100，合格线90）。用于定期评审或新 Agent 入职审批。
  Use for agent quality audits, onboarding approval, capability assessment,
  or when checking team roster completeness.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
argument-hint: "[audit|onboard|review] [agent_id]"
disable-model-invocation: true
---

# /hr-audit — Agent HR 审计

你是 Lysander CEO，调度 HR 管理团队执行 Agent 审计。

## 模式选择

### 模式 1: `audit` — 全员审计

**hr_director 执行：**

1. 扫描所有人员卡片：

```bash
find obs/01-team-knowledge/HR/personnel/ -name "*.md" -type f 2>/dev/null | sort
```

2. 逐一检查每张卡片的 Schema 完整性：
   - 必填字段：id, name, role, team, status, capabilities, backstory
   - status 必须是：active / probation / inactive / retired
   
3. **capability_architect 执行：** 能力描述质量评级：
   - A级（优秀）："基于 pytest + Playwright 的端到端测试框架搭建与维护"
   - B级（合格）："SWOT分析、PEST分析、波特五力模型应用"
   - C级（不合格）："项目管理"、"知识沉淀" — 过于笼统

4. 输出审计报告：

```
**【HR 审计报告】**

| Agent ID | 团队 | 卡片完整性 | 能力评级 | 总分 | 状态 |
|----------|------|-----------|---------|------|------|
| ... | ... | X/50 | X/50 | X/100 | ✅/⚠️/❌ |

**合格率**：X%
**需优化**：[列表]
**严重问题**：[列表]
```

### 模式 2: `onboard` — 新 Agent 入职审批

**hr_director 执行：**

1. 检查新 Agent 提案：
   - 是否与现有角色能力重叠 >30%？
   - 能力描述是否达到 B 级？
   - Schema 是否完整？
2. 审批结果：通过 / 退回修改 / 拒绝

### 模式 3: `review` — 单人评审

对指定 `agent_id` 进行深度评审：
- 5维度评分
- 能力描述优化建议
- Prompt/Backstory 工程建议

---

## 评分标准

| 分数 | 状态 | 处理 |
|------|------|------|
| >= 90 | 合格 | 保持 active |
| 80-89 | 需优化 | 限期提升能力描述至 A 级 |
| 60-79 | 不合格 | 立即修订 |
| < 60 | 严重不合格 | 降级 inactive 或退役 |
