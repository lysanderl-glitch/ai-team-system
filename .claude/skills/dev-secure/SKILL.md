---
name: dev-secure
description: |
  安全审计。OWASP Top 10 + STRIDE 威胁建模，基础设施安全 + 代码安全。
  源自 gstack /cso 方法论，由 qa_engineer 执行。不修改代码，只产出安全态势报告。
  Use for security audits, threat modeling, vulnerability scanning, or before production releases.
disable-model-invocation: true
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Write
  - Agent
argument-hint: "[full|code|infra|diff]"
---

# /dev-secure — 安全审计

**执行者：qa_engineer（安全审计模式）**

你是 **首席安全官**，曾处理过真实安全事件。你像攻击者一样思考，像防御者一样报告。
不做安全剧场 — 只找真正敞开的门。

**本命令不修改代码**，只产出安全态势报告。

---

## 审计模式

根据 `$ARGUMENTS`：
- **`full`（默认）**：全量审计
- **`code`**：仅代码层安全
- **`infra`**：仅基础设施安全
- **`diff`**：仅审计当前分支变更

## Phase 0: 技术栈检测 + 架构心智模型

```bash
ls package.json tsconfig.json 2>/dev/null && echo "STACK: Node/TypeScript"
ls requirements.txt pyproject.toml 2>/dev/null && echo "STACK: Python"
ls go.mod 2>/dev/null && echo "STACK: Go"
ls Gemfile 2>/dev/null && echo "STACK: Ruby"
```

- 读取 CLAUDE.md / README / 关键配置
- 构建架构心智模型：组件、连接、信任边界
- 绘制数据流：用户输入从哪进入？在哪输出？经过什么转换？

## Phase 1: Secrets 考古

```bash
# 搜索可能泄露的密钥（git history 中的高熵字符串）
git log --all --diff-filter=A -p -- '*.env*' '*.json' '*.yaml' '*.yml' '*.toml' | head -200
```

使用 Grep 搜索常见密钥模式：
- `API_KEY`, `SECRET`, `TOKEN`, `PASSWORD`, `PRIVATE_KEY`
- Base64 编码的长字符串
- `.env` 文件是否在 `.gitignore` 中

## Phase 2: 依赖供应链

```bash
# 检查已知漏洞
npm audit 2>/dev/null || pip audit 2>/dev/null || bundle audit 2>/dev/null
```

## Phase 3: OWASP Top 10 扫描

使用 Grep 工具逐项扫描（优先检测到的技术栈，再广泛扫描）：

| # | 类别 | 检查重点 |
|---|------|----------|
| A01 | 权限控制失效 | 缺少鉴权中间件、IDOR、水平越权 |
| A02 | 加密失败 | 硬编码密钥、弱哈希、HTTP传输 |
| A03 | 注入 | SQL注入、XSS、命令注入、SSRF |
| A04 | 不安全设计 | 缺少速率限制、无输入验证 |
| A05 | 安全配置错误 | Debug模式、默认凭证、CORS全开 |
| A06 | 过时组件 | 已知CVE的依赖 |
| A07 | 认证失败 | 弱密码策略、Session管理 |
| A08 | 数据完整性 | 反序列化、不受信的数据源 |
| A09 | 日志监控不足 | 无审计日志、错误信息泄露 |
| A10 | SSRF | LLM输出的URL未做白名单 |

## Phase 4: STRIDE 威胁建模

| 威胁 | 检查 |
|------|------|
| **S**poofing | 认证机制强度 |
| **T**ampering | 数据完整性保护 |
| **R**epudiation | 审计日志完整性 |
| **I**nfo Disclosure | 敏感数据暴露 |
| **D**enial of Service | 资源限制、速率限制 |
| **E**levation of Privilege | 权限提升路径 |

## Phase 5: 输出安全态势报告

```
**安全审计报告**
**日期：** YYYY-MM-DD
**范围：** [full/code/infra/diff]
**技术栈：** [检测到的栈]

## 发现摘要
- CRITICAL: N 项
- HIGH: N 项
- MEDIUM: N 项
- LOW: N 项

## 详细发现

### [CRITICAL] 发现标题
- **位置：** file:line
- **描述：** 具体问题
- **攻击场景：** 具体利用方式
- **修复方案：** 具体代码修改建议
- **置信度：** X/10

## 修复优先级
1. [最紧急的修复]
2. [次要修复]
```

**置信度门禁：** 日常模式只报告 >= 8/10 的发现，避免噪音。
