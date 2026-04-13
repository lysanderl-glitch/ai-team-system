---
name: dev-review
description: |
  代码审查（含安全）。两轮审查：CRITICAL + INFORMATIONAL，Fix-First 自动修复。
  源自 gstack /review + /cso 方法论，由 tech_lead + qa_engineer 联合执行。
  Use before merging code, creating PR, or when asked to review changes.
  Proactively suggest when the user is about to merge or land code.
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Agent
argument-hint: "[branch name or file paths]"
---

# /dev-review — 代码审查（含安全）

**执行者：tech_lead（主审）+ qa_engineer（安全审查）**

---

## Step 1: 检查分支

```bash
git branch --show-current
```

```bash
git fetch origin main --quiet 2>/dev/null && git diff origin/main --stat
```

如果在 main 分支或无变更，输出"无可审查内容"并停止。

## Step 2: 获取 Diff

```bash
git fetch origin main --quiet 2>/dev/null
git diff origin/main
```

## Step 3: Pass 1 — CRITICAL 审查（tech_lead 执行）

对 diff 进行以下关键检查：

### SQL & 数据安全
- SQL 字符串插值 → 强制参数化查询
- TOCTOU 竞态：check-then-set 应为原子 WHERE + UPDATE
- 绕过 ORM 验证的直接数据库写入
- N+1 查询：循环中缺少 eager loading

### 竞态条件 & 并发
- read-check-write 无唯一约束
- find-or-create 无唯一索引
- 状态迁移无原子 WHERE old_status 保护

### LLM 输出信任边界
- LLM 生成内容未经验证直接入库
- LLM 输出的 URL 未做 allowlist（SSRF 风险）
- LLM 代码 eval/exec 无沙箱

### Shell 注入
- subprocess + shell=True + f-string
- os.system() 拼接变量

### 枚举完整性
- 新增枚举值 → 追踪所有消费者，确认已处理

## Step 4: Pass 2 — INFORMATIONAL 审查

- 异步/同步混用检测
- 列名/字段名安全
- LLM Prompt 问题（0-index 列表、工具列表不匹配）
- 完整性缺口（80%实现但100%可达）
- 时间窗口安全
- 类型边界强转

## Step 5: Fix-First 处理

### 5a: 分类
- **AUTO-FIX**：机械性问题，直接修复
- **ASK**：有歧义的问题，批量上报

### 5b: 自动修复（GATE：逐项验证）

**GATE：每次 Edit 修复后，必须确认 Edit 工具返回成功。如果 Edit 失败，重试一次，仍失败则将该项降级为 ASK 类别，绝不可跳过失败继续下一项修复。**

每项输出：`[AUTO-FIXED] [file:line] 问题 → 修复方式`

修复完成后，验证所有修复未引入语法错误：
```bash
# 根据项目技术栈运行语法检查（如 eslint --quiet, python -m py_compile, etc.）
```
**如果语法检查失败，必须回退对应修复并将该项降级为 ASK，不可带着语法错误继续。**

### 5c: 批量上报
将所有 ASK 项合并为一次提问，附推荐方案。

## Step 6: 安全快扫（qa_engineer 执行）

- OWASP Top 10 快速扫描（聚焦 diff 涉及的代码）
- XSS 检查：dangerouslySetInnerHTML / v-html / .html_safe
- 硬编码密钥检测
- 依赖已知漏洞检查

## Step 7: 验证声明

**铁律 — 每个结论必须有证据：**
- 声称"安全" → 引用具体行号
- 声称"已有测试" → 指出测试文件和方法名
- 声称"已处理" → 读取并引用处理代码
- 禁止"可能没问题"、"大概有测试"

## Step 8: 输出审查报告

```
**代码审查报告**：N 个问题（X critical, Y informational）

**AUTO-FIXED:**
- [file:line] 问题 → 已修复

**NEEDS INPUT:**
- [file:line] 问题描述 → 推荐修复方案

**安全快扫：** 通过/发现N项
```

---

## 测试场景（强制，交付前必须通过）

### test_scenarios

#### Golden Path: 对功能分支执行完整代码审查

- **场景名称**：对有代码变更的功能分支执行两轮审查并自动修复
- **输入**：`/dev-review feature/add-auth`
- **前置条件**：
  - 当前处于非 main 分支（如 `feature/add-auth`）
  - `git diff origin/main --stat` 有输出（存在代码变更）
  - 远程 `origin/main` 可达（`git fetch` 成功）
- **预期结果**：
  - [ ] Step 1 正确检测到当前分支名和变更文件列表
  - [ ] Step 2 获取完整 diff 内容
  - [ ] Step 3 Pass 1 CRITICAL 审查覆盖所有检查项（SQL安全、竞态条件、LLM信任边界、Shell注入、枚举完整性）
  - [ ] Step 4 Pass 2 INFORMATIONAL 审查输出补充发现
  - [ ] Step 5a 发现分类为 AUTO-FIX 和 ASK 两组
  - [ ] Step 5b AUTO-FIX 项逐项修复，每次 Edit 后确认返回成功
  - [ ] Step 5b 修复后运行语法检查，失败则回退并降级为 ASK
  - [ ] Step 5c ASK 项合并为一次提问，附推荐方案
  - [ ] Step 6 安全快扫覆盖 OWASP Top 10（XSS、硬编码密钥、依赖漏洞）
  - [ ] Step 7 每个结论附证据（行号/文件名），无"可能没问题"类模糊表述
  - [ ] Step 8 输出完整审查报告，格式包含 AUTO-FIXED / NEEDS INPUT / 安全快扫
  - [ ] 工具调用链：`Bash(git branch) -> Bash(git fetch + git diff --stat) -> Bash(git diff) -> Read(变更文件) -> Edit(AUTO-FIX) -> Bash(语法检查)`

#### Edge Case 1: 在 main 分支或无变更时的降级处理

- **场景名称**：在 main 分支上执行 /dev-review 时正确终止
- **输入**：`/dev-review`
- **前置条件**：
  - 当前处于 `main` 分支，或 `git diff origin/main --stat` 无输出
- **预期结果**：
  - [ ] Step 1 检测到在 main 分支或无变更
  - [ ] 输出"无可审查内容"并停止
  - [ ] 不执行 Step 2-8 的任何操作
  - [ ] 不产生任何文件修改

#### Edge Case 2: AUTO-FIX 修复失败时的降级

- **场景名称**：Edit 修复失败时正确降级为 ASK 类别
- **输入**：`/dev-review feature/complex-refactor`
- **前置条件**：
  - 分支有代码变更
  - 某个 AUTO-FIX 项的 Edit 调用返回失败（如 old_string 不匹配）
- **预期结果**：
  - [ ] Edit 失败后重试一次
  - [ ] 重试仍失败则将该项降级为 ASK 类别
  - [ ] 不跳过失败继续下一项修复
  - [ ] 最终报告中该项出现在 NEEDS INPUT 而非 AUTO-FIXED 中
