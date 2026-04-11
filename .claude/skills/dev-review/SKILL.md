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

### 5b: 自动修复
每项输出：`[AUTO-FIXED] [file:line] 问题 → 修复方式`

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
