---
knowledge_id: K-2026-0421-001
category: process-knowledge / test-engineering
created: 2026-04-21
source_incident: INC-2026-0421-001
applies_to: "E2E 测试项目（Playwright / Selenium / Cypress）对生产系统或共享测试环境的只读实跑场景"
maturity: battle-tested（事件驱动沉淀，等待一次完整应用验证后升级为 validated）
owner: knowledge_engineer
reviewers: [test_case_designer, qa_engineer, harness_engineer, integration_qa]
tags: [testing, e2e, safety, circuit-breaker, playwright, readonly]
---

# 经验卡片：测试实跑只读熔断机制

## 核心教训

> **E2E 测试 spec 作者交付时，每条用例必须标注 `side_effect` 分类；
> `qa_engineer` 实跑前必须执行只读扫描，发现写操作即立即熔断上报，
> 绝不"带着未分类的 spec 直接启动实跑"。**

一句话版：**"没有 side_effect 标注的 spec，不允许进入实跑；没有只读扫描的实跑，不允许启动。"**

---

## 何时应用

本规则**强制适用于**以下场景：
- 对客户生产系统做实跑（最高风险）
- 对客户共享测试/沙箱环境做实跑（数据可能被其他角色观察）
- 总裁 / 产品方 / 合同明确要求"只读"或"不改数据"的验证
- 使用的测试账号有写权限但本轮不应行使（权限范围 ≠ 本轮授权范围）
- CDE 精通化、产品认证、第三方审计类测试任务

**豁免场景**（可不触发熔断，但仍需标注）：
- 一次性搭建的本地沙箱（可随时 teardown）
- 明确为"写路径测试"的专项用例（需单独审批 + 独立数据库实例）

---

## 实施机制（五层防御模型）

### 第一层：用例标注（最前端）

`test_case_designer` 在交付每个 spec 时，每个 `test()` 上方必须加副作用注释：

```typescript
// side_effect: readonly
test('TC-10.1 读取预算配置并断言字段结构', async ({ page }) => {
  const val = await page.locator('#budget-input').inputValue();
  expect(val).toMatch(/^\d+$/);
});

// side_effect: write
test('TC-10.3 尝试修改预算配置（写路径）', async ({ page }) => {
  await page.locator('#budget-input').fill('10000');
  await page.locator('#save-btn').click();
});

// side_effect: destructive
test('TC-10.7 尝试删除预算配置（破坏路径）', async ({ page }) => {
  await page.locator('#delete-btn').click();
});
```

**三类定义**：
- `readonly` — 只读页面、只读 API、只读数据库查询（SELECT / GET）；只能用 `expect` 断言，不得 `fill/click(save|submit|delete)`
- `write` — 改动数据但可逆（更新字段、新增记录）；`fill + submit`、`POST/PUT`
- `destructive` — 不可逆或高风险（删除、批准、发送邮件、支付等）；`DELETE`、confirm 对话框的 ok 操作

### 第二层：派单模板强制（执行链【②】前置）

`/dispatch` skill 派单 `qa_engineer` 做实跑时，prompt 模板**必须包含**以下铁律块：

```
【只读熔断铁律】（不可省略）
1. 登录前先做只读扫描：
   - grep -E "saveBtn|submitBtn|deleteBtn|\.click.*\(save|\.click.*\(submit|fill.*\+.*click" tests/**/*.spec.ts
   - 以及检查每个 test() 上方的 // side_effect: 注释
2. 如发现 write / destructive 用例未被过滤，立即熔断：
   - 不启动 Playwright
   - 向 Lysander 报告违规清单
   - 等待派单方决策（过滤 / 重构 / 授权）
3. 绝不采用"异步后台跑 + Agent 退出"模式；必须同步等待或使用可中断的长驻 Agent
```

### 第三层：`--grep-invert` / tag 过滤（运行时保护）

命令行运行时**不依赖人为记忆**，用机制保证：

```bash
# Playwright
npx playwright test --grep-invert "@write|@destructive"

# 或使用 side_effect 标签约定
npx playwright test --grep "@readonly"
```

配合 spec 中 `test.describe('@write', () => {...})` 或 `test('...', { tag: '@write' }, async () => {...})` 做标记。

### 第四层：页面路由拦截（运行时兜底）

即便上三层都漏了，在 Playwright 层面拦截所有写请求：

```typescript
// tests/fixtures/readonly-guard.ts
import { test as base } from '@playwright/test';

export const test = base.extend({
  page: async ({ page }, use) => {
    // 在 @readonly 上下文中，拦截所有写请求
    await page.route('**/*', (route) => {
      const method = route.request().method();
      if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
        console.error(`[READONLY-GUARD] 拦截到写请求: ${method} ${route.request().url()}`);
        return route.abort('blockedbyclient');
      }
      return route.continue();
    });
    await use(page);
  },
});
```

只在 `@readonly` 测试套件中引入此 fixture，`@write` 套件正常放行。

### 第五层：事后审计（闭环回流）

`integration_qa` 在【③】QA 审查时，必须检查：
- Playwright trace / HAR 文件中是否出现 `POST/PUT/DELETE` 请求
- 测试日志中是否出现 `saveBtn.click`、`fill` 后紧接 `submit` 等关键字
- 发现违规 → 记录到 `obs/04-decision-knowledge/decision-log/` + 触发事件归档流程

---

## 反模式（禁止）

| 反模式 | 具体表现 | 为什么禁止 |
|--------|----------|-----------|
| 乐观假设 | "这些用例应该没事吧，直接跑" | 假设不等于保证，必须用扫描证明 |
| 异步退出模式 | `nohup playwright test & ; exit` | Agent 退出后无法汇总结果、无法中途熔断 |
| 未标注混合 spec | 一个 spec 文件里混杂 readonly + write 且无 side_effect 注释 | 下游过滤器无法识别，必错 |
| `.env` 明文凭证 | `USER=...` `PASS=...` 明文写在 .env | 即便 gitignore 排除，也可能通过日志、Agent 上下文泄露 |
| 效率借口 | "只读扫描耽误时间，直接跑更快" | 本事件根因之一；不可接受 |
| 共享账号带写权限跑只读用例 | 账号权限 ⊃ 本轮授权 | 权限集合与本轮授权必须对齐 |

---

## 可复用代码片段

### A. 只读扫描 Bash 脚本

```bash
#!/usr/bin/env bash
# scripts/readonly-scan.sh — 在启动实跑前强制调用
set -euo pipefail

SPEC_DIR="${1:-tests}"
VIOLATIONS=0

echo "[READONLY-SCAN] 扫描 $SPEC_DIR ..."

# 1. 检查是否存在未标注的 test()
UNTAGGED=$(grep -rn "^\s*test(" "$SPEC_DIR" --include="*.spec.ts" \
  | while IFS=: read -r file line content; do
      prev_line=$((line - 1))
      prev_content=$(sed -n "${prev_line}p" "$file" || echo "")
      if ! echo "$prev_content" | grep -qE "// side_effect: (readonly|write|destructive)"; then
        echo "$file:$line"
      fi
    done)

if [[ -n "$UNTAGGED" ]]; then
  echo "[VIOLATION] 未标注 side_effect 的 test():"
  echo "$UNTAGGED"
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# 2. 检查是否有 write 用例未被过滤
WRITE_HITS=$(grep -rn -E "saveBtn|submitBtn|deleteBtn|\.fill\(.*\).*\.click\(" "$SPEC_DIR" --include="*.spec.ts" || true)
if [[ -n "$WRITE_HITS" ]]; then
  echo "[WARNING] 检测到疑似写操作，请确认已正确标注 // side_effect: write:"
  echo "$WRITE_HITS"
fi

if [[ $VIOLATIONS -gt 0 ]]; then
  echo "[CIRCUIT-BREAKER] 扫描未通过，熔断。请先补齐 side_effect 标注。"
  exit 1
fi

echo "[READONLY-SCAN] 通过。"
```

### B. Playwright Readonly Guard Fixture（推荐默认装载）

```typescript
// tests/fixtures/readonly-guard.ts
import { test as base, expect } from '@playwright/test';

type ReadonlyOptions = { readonly: boolean };

export const test = base.extend<ReadonlyOptions>({
  readonly: [true, { option: true }],
  page: async ({ page, readonly }, use) => {
    if (readonly) {
      await page.route('**/*', (route) => {
        const method = route.request().method();
        if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
          const url = route.request().url();
          console.error(`[READONLY-GUARD] BLOCKED ${method} ${url}`);
          throw new Error(`Readonly guard triggered: ${method} ${url}`);
        }
        return route.continue();
      });
    }
    await use(page);
  },
});

export { expect };
```

使用：
```typescript
// tests/energy-10-readonly.spec.ts
import { test, expect } from './fixtures/readonly-guard';

test.use({ readonly: true });

// side_effect: readonly
test('TC-10.1 读取预算配置', async ({ page }) => {
  await page.goto('/budget');
  const val = await page.locator('#budget-input').inputValue();
  expect(val).toBeTruthy();
});
```

### C. 派单 Prompt 模板片段（供 `/dispatch` skill 使用）

```
## 【只读熔断铁律】（强制，不可省略）

本次 qa_engineer 派单为【只读实跑】任务，你必须：

1. **登录前强制做只读扫描**：
   - 运行 `bash scripts/readonly-scan.sh tests/` 确认无未标注 test()、无未过滤写操作
   - 如扫描失败，立即熔断 → 向 Lysander 报告 → 等待决策
2. **运行命令必须包含过滤**：
   - `npx playwright test --grep "@readonly" --grep-invert "@write|@destructive"`
   - 或通过 fixture 强制 readonly=true
3. **禁止异步退出模式**：
   - 必须同步等待 Playwright 完成
   - 不得使用 `nohup ... &` + Agent 退出
4. **发现任何异常立即熔断**：
   - 网络请求中出现 POST/PUT/DELETE
   - 日志中出现 saveBtn.click / submitBtn.click / deleteBtn.click
   - 立即 Ctrl+C 并向 Lysander 报告

违反本铁律视为执行链【②】断裂，进决策日志，记录 incident。
```

---

## 度量指标（纳入 integration_qa 审查）

| 指标 | 目标值 | 如何检测 |
|------|--------|----------|
| side_effect 标注覆盖率 | 100% | readonly-scan.sh 扫描 |
| 只读实跑中的写请求数 | 0 | Playwright HAR 分析 |
| 熔断响应时间 | < 2 min | 扫描到告警的时间戳差 |
| 相同事件复发率 | 0 次/季 | incident 归档搜索 |

---

## 本卡片的更新机制

- 每次发生相关 incident → `knowledge_engineer` 追加案例到"引用事件"节
- 每季度由 `integration_qa` 审计一次五层防御的落地情况
- 反模式清单遇新违规模式实时追加

---

## 引用事件

- **INC-2026-0421-001** — Meos 实跑只读铁律破坏（已熔断）
  - 详见：`obs/04-session-snapshots/INCIDENT_2026-04-21_meos-readonly-breach.md`
  - 核心启示：异步后台跑 + 未做只读扫描 = 熔断失效；需从派单 prompt 源头强制

---

## 关联知识

- `obs/03-process-knowledge/quality-assurance-framework.md` — QA 总框架
- `obs/03-process-knowledge/harness-engineering-methodology.md` — Harness Constraints 层约束设计
- `obs/03-process-knowledge/agent-hr-management-system.md` — qa_engineer / test_case_designer 能力描述更新依据
