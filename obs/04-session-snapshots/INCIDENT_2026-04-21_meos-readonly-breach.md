---
incident_id: INC-2026-0421-001
incident_date: 2026-04-21
severity: P1
project_id: meos-energy-cde-2026-04-20
status: contained（已控制，总裁决定不回滚）
owner: Lysander CEO + qa_engineer + test_case_designer + Butler
archived_date: 2026-04-21
archived_by: knowledge_engineer
related_decision_level: L4（已上报总裁并获批示）
tags: [incident, readonly-breach, e2e-testing, meos, circuit-breaker]
---

# 事件：Meos 实跑只读铁律破坏（已熔断）

## 一、事件摘要

2026-04-21 约 18:13，项目 `meos-energy-cde-2026-04-20` 阶段 B P0 实跑环节，上一轮
`qa_engineer` 子 Agent（agentId: `ad0fa4fc181112a1f`）**未执行只读扫描**即异步启动
Playwright 运行 `energy-10-deep` 测试，对 Keppel 项目的预算配置页面（BUDGET_CONFIG）
执行了 7+ 次写入尝试（fill 10000 / 0 / 9e15 / -100 / 5000 / 8888 + `saveBtn.click`），
使用的是 `.env` 中残留的旧账号 `18881956318`。

本轮 `qa_engineer` 子 Agent（agentId: `ac0fb6917a4b4ce7e`）按标准流程先做只读扫描，
识别出 `energy-10-deep` 包含写操作后**正确熔断**，向 Lysander 报告，避免了二次污染。
Lysander 按 L4 标准上报总裁，总裁批示"数据没问题，不回滚"，并指示重构 10-deep、
过滤越界用例跑安全子集、清理 `.env`。事件已控制，整改动作已派单执行。

---

## 二、时间线

| 时间（Dubai） | 事件 | 执行者 |
|---------------|------|--------|
| 2026-04-21 ~18:13 | 上一轮 `qa_engineer` 子 Agent（ad0fa4fc181112a1f）启动 | Lysander 派单 |
| 18:13 – 18:32 | **未做只读扫描**，异步后台启动 `energy-10-deep` 跑测，Agent 未等待结果即退出 | 上一轮 qa_engineer Agent |
| 期间 | Playwright 对 BUDGET_CONFIG 页面执行 7+ 次 fill + saveBtn.click 写入尝试 | 测试脚本自身 |
| ~18:32 之后 | 本轮 `qa_engineer` 子 Agent（ac0fb6917a4b4ce7e）接手，执行只读扫描 | 本轮 qa_engineer Agent |
| 扫描完成 | 识别 `energy-10-deep` 为写操作脚本 → **熔断** → 向 Lysander 告警 | 本轮 qa_engineer Agent |
| 随后 | Lysander 按 L4 标准上报总裁（凭证暴露 + 写操作外溢） | Lysander CEO |
| 总裁批示 | "数据没问题，不回滚"；指示重构 10-deep、过滤越界用例跑安全子集、清理 .env | 总裁刘子杨 |
| 派单 | qa_engineer 跑安全子集 + test_case_designer 重构 10-deep + Butler 清理 .env + knowledge_engineer 归档 | Lysander 派单 |

---

## 三、影响评估

| 维度 | 评估结果 |
|------|----------|
| **实际数据写入** | 未逐条确认；总裁肉眼观察 Keppel 项目预算配置页面后认为"数据没问题"，不回滚 |
| **凭证暴露** | 旧账号 `18881956318` 仍有效（密码 `***`，未泄露于文档） → 建议总裁考虑改密（L3 建议项） |
| **项目进度影响** | 阶段 B P0 延后一轮（需重构 10-deep + 安全子集实跑） |
| **范围外扩散** | 无；仅 Keppel 项目 BUDGET_CONFIG 页面受影响 |
| **合规/法律风险** | 低；内部测试环境，非客户生产系统触发条款 |
| **对下游 TC 的污染** | 无；TC-04/05/08/09/12 未启动 |

---

## 四、根因分析（Five Whys）

| # | 问题 | 答案 |
|---|------|------|
| 1 | 为什么会发生写入？ | `energy-10-deep` 测试用例本身包含 `fill + saveBtn.click` 的写操作组合 |
| 2 | 为什么 Agent 跑了这些用例？ | 启动实跑前未做只读扫描，直接把 spec 文件全部扔给 Playwright |
| 3 | 为什么未做只读扫描？ | Lysander 第一轮派单 prompt 没有强制植入"只读扫描 + 熔断"子检查项 |
| 4 | 为什么派单 prompt 未强制？ | 阶段 B P0 快照文档虽然列出 "44 场景"，但没有按"只读 / 写 / 破坏"三类做 side_effect 标注 |
| 5 | 为什么快照没做标注？ | spec 交付者（`test_case_designer`）在产出 deep spec 时未遵循"副作用分类"的交付标准（该标准此前未在 Synapse 流程中明确沉淀） |

**根本根因**：
- **流程盲区**：Synapse 体系此前未沉淀"E2E 测试副作用分类 + 只读熔断"这一 SOP
- **派单模板缺项**：`/dispatch` skill 模板中没有强制"只读扫描"检查子项
- **交付标准模糊**：`test_case_designer` 的交付 schema 未要求 `// side_effect:` 标注

---

## 五、责任分析

| 责任方 | 角色 | 责任类型 | 说明 |
|--------|------|----------|------|
| **Lysander CEO** | 派单方 | **首要责任** | 派单约束不够硬，未植入"只读扫描+熔断"前置条件；未审核 spec 副作用分类是否完备 |
| **test_case_designer** | spec 交付者 | **次要责任** | 交付 deep spec 时未对每条 test() 做 side_effect 标注，导致下游无法按副作用过滤 |
| **上一轮 qa_engineer Agent**（ad0fa4fc181112a1f） | 直接执行者 | **直接责任** | 未做尽职调查（pre-flight check）即启动实跑；采用异步+退出模式，丧失熔断可能 |
| **.env 管理** | 流程责任 | **系统性隐患** | 旧凭证 `18881956318` 以明文形式残留在 .env，即便 .env 在 .gitignore 中也属隐患 |
| **本轮 qa_engineer Agent**（ac0fb6917a4b4ce7e） | 熔断者 | **正面贡献** | 按标准只读扫描识别风险并熔断，阻止了二次污染 |

---

## 六、整改动作（总裁已批准）

| # | 动作 | 执行者 | 状态 |
|---|------|--------|------|
| 1 | 重构 `energy-10-deep` 为"只读断言版"（移除 fill/save，改为读取+断言配置值） | test_case_designer | 已派单 |
| 2 | 用 `--grep-invert` 过滤 9 条越界用例，跑安全子集实跑 | qa_engineer | 已派单 |
| 3 | 清理 `.env` 中旧凭证 `18881956318` 的明文残留（改用凭证库 + 运行时注入） | Butler | 已派单 |
| 4 | 归档事件（本文档）+ 沉淀"只读熔断"经验卡片 | knowledge_engineer | 已完成 |

---

## 七、后续待办

| # | 事项 | 决策级别 | 责任方 | 状态 |
|---|------|----------|--------|------|
| 1 | 账号 `18881956318` 是否改密 | L3 建议项 | 总裁决策 | 待定 |
| 2 | 安全子集实跑结果汇报 | 例行交付 | qa_engineer | 待交付 |
| 3 | `energy-10-deep` 重构版交付 | 例行交付 | test_case_designer | 待交付 |
| 4 | 执行链【②】派单模板是否强制加入"只读扫描"子检查项 | **L2 决策** | harness_engineer（主） + integration_qa（评审） | 已完成（harness_engineer 已落地到 dispatch skill） |
| 5 | 是否对所有新增测试 spec 强制要求 `// side_effect:` 标注 | **L2 决策** | test_case_designer（主） + knowledge_engineer（评审） | 待评审 |

---

## 八、经验卡片交叉引用

- **K-2026-0421-001**：`obs/03-process-knowledge/readonly-test-circuit-breaker-lesson.md` — 测试实跑只读熔断机制（五层防御模型）

---

## 九、附注

- 本事件未导致客户系统故障、合规违规、财务损失。
- 本事件首次在 Synapse 体系中暴露 "E2E 测试副作用分类" 的流程盲区，知识卡片已沉淀。
- 本事件凸显"异步后台跑+Agent 退出"的执行模式风险，建议在 qa_engineer 标准动作集中禁用。
- 凭证号码 `18881956318` 在文档中保留（号码本身不构成安全凭据）；密码已用 `***` 替代。

---

## 十、收口

- **收口时间**：2026-04-21（阶段 B P0 收口）
- **收口条件**：第六节所有整改动作完成 + 第七节 L2 决策全部落地
- **收口签署**：Lysander CEO + knowledge_engineer + harness_engineer
