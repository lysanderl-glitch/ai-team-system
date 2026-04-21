---
doc_type: external_request_draft
status: draft_ready
audience: Meos 产品方（具体联系人待总裁确认）
owner: Butler 团队 / pmo_coordinator
related_project: meos-energy-cde-2026-04-20
related_phase: 阶段 B（P0 深化已完成，待实跑验证）
created_date: 2026-04-21
follow_up_date: 2026-04-24
---

# 需求说明草稿 —— Meos "能耗预算配置"（BUDGET_CONFIG）直链 URL 申请

> 本文档为 **草稿**，尚未对外发送。待总裁确认产品方联系人后由 Butler 团队正式发出。

---

## 一、需求事由

Janus Digital（CDE 合作方）正在对 Meos 能源管理模块开展端到端自动化回归测试项目
（内部 project_id：`meos-energy-cde-2026-04-20`），覆盖 **六大模块、98 个测试场景**，
其中阶段 B 已沉淀 **5 个深度 spec 文件、44 个场景、约 2243 行代码**。

在 Page Object 建设过程中（`meos-e2e/pages/amc-energy.page.ts`），我们发现
**"能耗预算配置（Budget Configuration）"** 子功能当前 **没有独立的可直达 URL**，
这与能源模块内其他 9 项子功能的情况不同 —— 后者都有稳定的 URL 片段（如
`energyScope`、`sharedItem`、`costbudget`、`dynamicBudgetProject`、`energyreviewreport`
等）可供 `page.goto()` 直链访问。

### 相关测试资产（引用 BUDGET_CONFIG 的位置）

| 文件 | 引用方式 | 说明 |
|------|----------|------|
| `meos-e2e/pages/amc-energy.page.ts` | `ENERGY_URLS.BUDGET_CONFIG = '__PLACEHOLDER_BUDGET_CONFIG__'` | URL 常量占位符 |
| `meos-e2e/pages/amc-energy.page.ts` | `gotoBudgetConfig()` 方法 | 当前采用按钮点击 workaround |
| `meos-e2e/tests/energy-smoke.spec.ts` | TC-ENERGY-SMOKE 第 9 项 | 烟雾测试中仅做入口可达性断言 |
| `meos-e2e/tests/energy-10-deep.spec.ts` | 作为"路径 B 降级方案" | 阶段 A 标注"稳定性偏弱" |
| `meos-e2e/tests/energy-04*.spec.ts` | "费用预算配置"按钮可见性断言 | 当前业务入口源 |

---

## 二、当前 Workaround 及其局限

### 当前实现

```
1. 先导航到 Cost Budget 页：/amc/.../costbudget?pj=<PROJECT_ID>
2. 等待页面加载完成（waitForTimeout 3000ms）
3. 定位"费用预算配置"按钮（中文文案匹配 page.getByText('费用预算配置')）
4. 点击按钮 → 触发模态或页面跳转进入配置界面
5. 再 waitForTimeout 3000ms 等待目标页面稳定
```

### Workaround 局限

| 维度 | 局限说明 |
|------|----------|
| **稳定性** | 依赖中文文案 `费用预算配置` 精确匹配，产品方一旦调整按钮文案（如改英文/重构 i18n）即断链；代码注释中已标注"稳定性偏弱"并在 energy-10-deep 中列为降级路径。 |
| **执行效率** | 每次进入需经 Cost Budget 中转页 + 两次 3s waitForTimeout，单用例多引入约 **6–10 秒**。扩展到 P1/P2 阶段（预计 54+ 场景涉及预算配置）时将累计显著延迟。 |
| **前置耦合** | 强制串接 Cost Budget 页加载成功，若中转页接口异常，预算配置相关所有用例连带失败，归因分析成本高。 |
| **可观测性** | Playwright trace 中无法从 URL 直接辨识"用户当前在预算配置页"，定位问题时需回放 DOM 状态。 |
| **维护成本** | 任何涉及预算配置的新用例都需复制该 workaround 代码块，后续 i18n 切换或按钮重构时需批量修改。 |

---

## 三、希望产品方提供的内容

### 1. 直链 URL 规范

希望提供能直达"能耗预算配置（Budget Configuration）"页的稳定 URL 模式，参照同模块既有规范：

```
# 期望格式示例（请按产品方实际路由提供）：
/amc/energy-budget-web/<budget-config-route>?pj={PROJECT_ID}[&其他必要参数]
```

### 2. 入参格式

请明确以下参数的名称、类型、是否必需：

| 参数候选 | 是否必需 | 说明 |
|----------|----------|------|
| `pj`（Project ID） | 推测必需 | 参照同模块既有 URL 规范 |
| 能源类型参数 | 待产品方确认 | 如需选定电/水/燃气/热，默认值为何 |
| 年度/周期参数 | 待产品方确认 | 是否需要 `year` 或 `period` |
| 其他路由参数 | 待产品方确认 | 请列出所有必需与可选参数 |

### 3. 权限要求

请说明访问该 URL 所需的角色权限，与"Cost Budget 页 + 费用预算配置按钮"当前路径是否一致；
是否存在额外的功能位（function code）授权要求。

### 4. URL 稳定性承诺

请确认该 URL 是否属于 **对外稳定契约**（后续版本不随意变更路由/参数名），
以便测试资产可以长期复用该直链。

---

## 四、对测试稳定性与效率的预期收益

| 维度 | 当前 Workaround | 启用直链后 | 预期改善 |
|------|----------------|-----------|---------|
| **单用例耗时** | 约 20–25s（含 Cost Budget 中转 + 两次 3s 等待 + 按钮点击） | 约 10–12s（直接 goto + 单次等待） | **减少约 50%** |
| **断链风险点** | 2 处（中转页接口 + 按钮中文文案） | 1 处（URL 路由） | **降低 50%** |
| **i18n 影响** | 按钮文案切换即断链 | URL 不受 i18n 影响 | **完全免疫** |
| **用例代码量** | 每处需 ~15 行 workaround | `page.goto(URL)` 单行 | **大幅精简** |
| **归因效率** | 需区分中转页失败 vs 按钮失败 vs 目标页失败 | 单一失败点 | **显著提升** |

### 项目层面的收益

- 阶段 C（TC-04/05/08/09/12 五路并行扩展）中，预算配置相关场景的稳定性门槛直接达标
- 对 `janus_cde` 能力轨的"测试驱动型产品精通化"沉淀提供标准范式（URL 常量 → 稳定 POM）
- 减少后续 P1/P2 阶段因 workaround 积累的技术债

---

## 五、回复时限与后续协作

- **请求回复时限**：_待总裁确认（建议 7–10 个工作日，以便回应内容能纳入阶段 C 启动前）_
- **对接窗口**：Butler 团队 pmo_coordinator（技术细节可衔接 janus_cde）
- **后续动作**：
  1. 收到直链 URL 与入参规范后，由 `ai_systems_dev` 更新 `ENERGY_URLS.BUDGET_CONFIG` 常量并重构 `gotoBudgetConfig()` 方法
  2. `integration_qa` 对重构前后做对照回归，确保 0 用例退化
  3. 稳定性验证通过后，将 URL 规范归档到 OBS 知识库（`obs/02-domain-knowledge/meos/`）

---

## 六、附件与引用

- **Page Object 源文件**：`meos-e2e/pages/amc-energy.page.ts`（第 23–25 行注释说明、第 60–63 行常量占位、第 287–302 行 workaround 实现）
- **Smoke 测试引用**：`meos-e2e/tests/energy-smoke.spec.ts`（第 15 行注释、第 76–80 行用例）
- **Deep 测试引用**：`meos-e2e/tests/energy-10-deep.spec.ts`（第 16–20 行路径 A/B 说明、第 71–75 行降级逻辑）
- **项目背景**：`obs/04-session-snapshots/SESSION_SNAPSHOT_2026-04-20_meos-energy-cde.md`

---

*草稿由 Butler 团队 `pmo_coordinator` 起草于 2026-04-21。*
*待总裁确认产品方联系人及发送渠道（邮件 / 产品方工单系统 / 项目群）后正式发出。*
