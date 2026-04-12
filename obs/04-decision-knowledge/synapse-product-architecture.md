---
title: Synapse 产品化架构方案 — Core/Ops 分离 + 订阅升级模型
date: 2026-04-12
author: Graphify 智囊团 + Growth 团队 + RD 团队
tags: [Synapse, 产品化, 架构, 商业模式, 版本管理]
decision_level: L3
---

# Synapse 产品化架构方案

## 一、商业模式

```
免费：初始化同步一次 Synapse Core → 永久使用 → 不收费
付费：持续订阅 Synapse Evolution → 每天/每周同步最新版 → $XX/月

总裁环境（上游）             用户环境（下游）
├── 每天自动进化              ├── 初始化 clone 一次
├── 情报+牛人+GAP分析         │   → 免费用户到此为止
├── 能力融合+Agent升级         │
├── 体系持续优化              ├── 订阅升级
└── 发布新版 Synapse Core     │   → 每天/每周同步最新Core
                              │   → 享受总裁团队的进化成果
                              └── 用户自己的私有数据不受影响
```

## 二、架构分层

### 三层分离

```
┌─────────────────────────────────────────────┐
│  Layer 1: Synapse Core（可分发，跟着仓库走）   │
│  ├── CLAUDE.md          Harness 核心配置      │
│  ├── organization.yaml  团队架构模板          │
│  ├── decision_rules.yaml 决策规则             │
│  ├── HR/personnel/*.md  Agent 能力卡片        │
│  ├── *_experts.yaml     专家配置              │
│  ├── hr_base.py         管理引擎              │
│  ├── scripts/*.py       工具脚本              │
│  └── 方法论文档          知识资产              │
│  → 版本化管理，每次进化都有版本号              │
│  → 免费用户拿走初始版，付费用户持续同步        │
├─────────────────────────────────────────────┤
│  Layer 2: Synapse Templates（Prompt模板）      │
│  ├── daily-intelligence-prompt.md             │
│  ├── intelligence-action-prompt.md            │
│  └── 其他流程Prompt模板                       │
│  → 随Core一起分发                             │
│  → 用户可以按自己的行业定制                    │
├─────────────────────────────────────────────┤
│  Layer 3: User Private（用户私有，不分发）      │
│  ├── obs/00-daily-work/     个人工作记录       │
│  ├── obs/personal/          个人文件           │
│  ├── obs/daily-intelligence/ 情报输出          │
│  ├── obs/generated-articles/ 生成的内容        │
│  ├── active_tasks.yaml      当前任务           │
│  ├── credentials.mdenc      凭证              │
│  └── 远程定时任务配置        个人自动化        │
│  → 永远不进分发包                             │
│  → 每个用户自己产生和管理                      │
└─────────────────────────────────────────────┘
```

### 文件归属分类

| 文件/目录 | 层级 | 分发 | 升级时覆盖 |
|-----------|:----:|:----:|:----------:|
| CLAUDE.md | Core | ✅ | ✅ 覆盖（核心配置） |
| organization.yaml | Core | ✅ | ✅ 覆盖 |
| decision_rules.yaml | Core | ✅ | ✅ 覆盖 |
| HR/personnel/**/*.md | Core | ✅ | ✅ 覆盖（能力进化） |
| *_experts.yaml | Core | ✅ | ✅ 覆盖 |
| hr_base.py | Core | ✅ | ✅ 覆盖 |
| scripts/*.py | Core | ✅ | ✅ 覆盖 |
| obs/03-process-knowledge/ | Core | ✅ | ✅ 覆盖（方法论更新） |
| evolution-log/changelog.yaml | Core | ✅ | ✅ 覆盖（进化记录） |
| daily-intelligence-prompt.md | Template | ✅ | ⚠️ 合并（用户可能已定制） |
| intelligence-action-prompt.md | Template | ✅ | ⚠️ 合并 |
| n8n_integration.yaml | Template | ✅ | ❌ 不覆盖（环境绑定） |
| active_tasks.yaml | Private | ❌ | ❌ 不碰 |
| obs/00-daily-work/ | Private | ❌ | ❌ 不碰 |
| obs/personal/ | Private | ❌ | ❌ 不碰 |
| obs/daily-intelligence/ | Private | ❌ | ❌ 不碰 |
| credentials.mdenc | Private | ❌ | ❌ 不碰 |
| 远程触发器配置 | Private | ❌ | ❌ 用户自建 |

## 三、版本管理机制

### 版本号规则

```
Synapse v{MAJOR}.{MINOR}.{PATCH}

MAJOR: 架构级变更（执行链重构、决策体系变更）
MINOR: 能力进化（新Agent、能力升级、新方法论）
PATCH: 小修复（描述优化、Bug修复）

示例：
v1.0.0 — 初始发布（当前状态）
v1.1.0 — 新增 evolution_engine + 牛人追踪
v1.2.0 — 3个Agent能力升级（从情报发现的新技术）
v1.2.1 — 修复审计引擎C级检测精度
v2.0.0 — 执行链v3.0（如果有重大重构）
```

### 版本文件

在仓库根目录增加 `VERSION` 文件：
```
1.0.0
```

每次 Core 变更时更新版本号。

### 变更日志

`CHANGELOG.md` 记录每个版本的变化：
```markdown
# Synapse Changelog

## v1.1.0 (2026-04-12)
### New
- evolution_engine Agent (Graphify) — 自成长闭环协调
- 能力变更日志系统 (evolution-log/changelog.yaml)
- 情报日报升级：牛人追踪 + GAP分析

### Enhanced
- daily-intelligence-prompt.md — 新增5位专家追踪 + 能力差距分析

## v1.0.0 (2026-04-10)
### Initial Release
- 10 teams, 50 agents
- Execution chain v2.0
- 4-level decision system
- HR management with auto-audit
- Daily intelligence pipeline
- Intelligence action pipeline
```

## 四、用户升级流程

### 免费用户（初始化一次）

```
Step 1: clone 仓库
  git clone https://github.com/lysanderl-glitch/synapse-core.git

Step 2: 个人化配置（3分钟）
  打开 CLAUDE.md，按顶部说明替换3个名字

Step 3: 打开 Claude Code
  Synapse 立即生效

完毕。永久免费使用 v1.0.0。
```

### 付费用户（持续同步）

```
方式A: 一句话升级（推荐）
  在 Claude Code 中对 CEO 说："升级 Synapse"
  CEO 自动执行：
  1. 检查远程仓库最新版本号
  2. 拉取 Core 层文件更新
  3. 保留用户 Private 层不动
  4. 运行 HR 审计确认升级后体系健康
  5. 报告升级了什么

方式B: 手动同步
  git fetch upstream
  git merge upstream/main --no-commit
  # 检查冲突，保留自己的私有配置
  git commit

方式C: 自动同步（高级）
  设置定时任务每天检查新版本
  有新版 → 自动拉取 Core 层 → 审计 → 通知用户
```

### 升级安全机制

```
升级前自动检查：
├── 备份当前 Core 文件
├── 拉取新版 Core
├── 运行 audit_all_agents() — 确认新版分数 ≥ 90
├── 检查 CLAUDE.md 用户自定义部分是否被覆盖
│   → 如果是：回滚，通知用户手动合并
├── 通过 → 完成升级，输出变更摘要
└── 失败 → 自动回滚到备份版本
```

## 五、仓库结构设计

### 当前仓库改造

```
ai-team-system/                    ← 总裁的完整环境（上游）
├── VERSION                        ← 新增：版本号文件
├── CHANGELOG.md                   ← 新增：变更日志
├── CLAUDE.md                      ← Core（顶部有个人化配置区）
├── QUICKSTART.md                  ← 已有：快速开始指南
├── agent-butler/                  ← Core：引擎+配置
│   ├── config/
│   │   ├── organization.yaml
│   │   ├── decision_rules.yaml
│   │   ├── *_experts.yaml
│   │   ├── active_tasks.yaml      ← Private（.gitignore排除或模板化）
│   │   └── ...
│   ├── hr_base.py
│   └── hr_watcher.py
├── scripts/                       ← Core：工具脚本
├── obs/
│   ├── 01-team-knowledge/HR/      ← Core：Agent卡片（进化的核心）
│   ├── 03-process-knowledge/      ← Core：方法论
│   ├── 04-decision-knowledge/     ← Core：决策知识
│   ├── 05-industry-knowledge/     ← Core：行业知识
│   ├── 00-daily-work/             ← Private
│   ├── daily-intelligence/        ← Private
│   ├── generated-articles/        ← Private
│   └── personal/                  ← Private
└── .gitignore                     ← 排除 Private 层
```

### 分发仓库（给用户）

选项A：同一个仓库，用 .gitignore 管理
选项B：单独的 synapse-core 仓库（只含 Core 层）← 推荐

```
synapse-core/                      ← 公开/付费仓库（只有Core）
├── VERSION
├── CHANGELOG.md
├── CLAUDE.md
├── QUICKSTART.md
├── agent-butler/
│   ├── config/  (不含 active_tasks.yaml)
│   ├── hr_base.py
│   └── hr_watcher.py
├── scripts/
├── obs/
│   ├── 01-team-knowledge/HR/
│   ├── 03-process-knowledge/
│   └── 04-decision-knowledge/
└── templates/                     ← 新增：模板目录
    ├── active_tasks.yaml.template
    ├── n8n_integration.yaml.template
    └── daily-intelligence/        ← 示例报告
```

## 六、收费模型

| 层级 | 内容 | 价格 |
|------|------|------|
| **Free** | 初始化同步 v1.0.0，永久使用 | $0 |
| **Evolution** | 持续同步最新 Core + 每周成长报告 | $99/月 |
| **Evolution Pro** | 上述 + 定制行业情报 + 优先新功能 | $299/月 |
| **Enterprise** | 上述 + 专属支持 + 定制Agent团队 | $999/月 |

### 价值阶梯

```
Free 用户获得：
├── Synapse Core v1.0.0 完整体系
├── CLAUDE.md + 50个Agent + 执行链 + 决策链 + HR审计
├── 所有工具脚本
└── 方法论文档

Evolution 用户额外获得：
├── 每天/每周的 Core 更新（Agent能力进化）
├── 每周成长报告（本周新增了什么）
├── 新Agent发布（总裁团队发现并验证的新角色）
├── 方法论更新（新的行业最佳实践）
└── 一句话升级能力

Enterprise 用户额外获得：
├── 定制行业Agent（建筑/金融/零售等）
├── 1对1 Synapse 咨询
├── 优先获得新功能
└── 专属 Slack 支持频道
```

## 七、实施路径

### 立即做

1. 创建 `VERSION` 文件（v1.0.0）
2. 创建 `CHANGELOG.md`
3. 确保 CLAUDE.md 顶部的"个人化配置区"完整可用
4. 验证：新用户 clone → 改3个名字 → 打开 Claude Code → 体系生效

### 近期做

5. 创建 `synapse-core` 分发仓库（只含 Core 层）
6. 编写升级脚本（synapse upgrade 命令）
7. 设计付费验证机制（如何区分免费/付费用户）

### 后续做

8. 建立自动化发布流程（总裁环境进化 → 自动发布到 synapse-core）
9. 上线订阅支付（Stripe/LemonSqueezy）
10. 建立用户社区

## 八、评审

| 专家 | 评分 | 意见 |
|------|:----:|------|
| strategist | 5 | 免费+订阅是SaaS行业验证最好的模型 |
| gtm_strategist | 5 | "免费初始化"降低获客门槛，"进化订阅"创造持续收入 |
| decision_advisor | 5 | Core/Ops/Private 三层分离风险可控 |
| tech_lead | 5 | 版本管理+升级脚本技术完全可行 |
| customer_insights_manager | 5 | 用户旅程清晰：clone→改名→用，极低门槛 |

**均分 5.0 → 推荐执行**
