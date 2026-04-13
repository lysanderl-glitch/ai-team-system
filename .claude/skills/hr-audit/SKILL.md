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

---

## 测试场景（强制，交付前必须通过）

### test_scenarios

#### Golden Path: 全员审计

- **场景名称**：执行全员 Agent 审计并输出审计报告
- **输入**：`/hr-audit audit`
- **前置条件**：
  - `obs/01-team-knowledge/HR/personnel/` 目录存在且包含至少 5 张 Agent 卡片（.md 文件）
  - 卡片包含标准 YAML frontmatter（id, name, role, team, status, capabilities, backstory）
- **预期结果**：
  - [ ] 工具调用链：`Bash(find personnel/*.md) -> Read(逐张卡片)` 遍历所有卡片
  - [ ] 每张卡片检查 Schema 完整性（7 个必填字段）
  - [ ] 每张卡片评估能力描述质量等级（A/B/C）
  - [ ] 输出标准审计报告表格：Agent ID / 团队 / 卡片完整性(X/50) / 能力评级(X/50) / 总分(X/100) / 状态
  - [ ] 报告底部包含：合格率百分比 + 需优化列表 + 严重问题列表
  - [ ] 总分 >= 90 标记为合格，80-89 标记需优化，60-79 不合格，< 60 严重不合格

#### Edge Case 1: 人员卡片目录为空

- **场景名称**：无任何 Agent 卡片时的处理
- **输入**：`/hr-audit audit`
- **前置条件**：
  - `obs/01-team-knowledge/HR/personnel/` 目录为空或不存在
- **预期结果**：
  - [ ] `find` 命令返回空结果
  - [ ] 输出提示"未找到任何 Agent 人员卡片"
  - [ ] 不输出空表格，不报错崩溃

#### Edge Case 2: 新 Agent 入职审批

- **场景名称**：审批一个与现有角色部分重叠的新 Agent
- **输入**：`/hr-audit onboard new_content_writer`
- **前置条件**：
  - 新 Agent 提案卡片已存在
  - 团队中已有 `content_strategist` 角色
- **预期结果**：
  - [ ] 检查新 Agent 能力描述质量（必须 >= B 级）
  - [ ] 检查 Schema 完整性（7 个必填字段）
  - [ ] 与现有角色做能力重叠比对（尤其 content_strategist）
  - [ ] 如重叠 > 30%，给出拒绝建议并说明具体重叠项
  - [ ] 如重叠 <= 30% 且质量合格，审批通过并设 `status: probation`
