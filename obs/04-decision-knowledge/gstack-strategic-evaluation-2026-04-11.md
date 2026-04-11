# gstack 战略评估报告

> **评估日期**：2026-04-11
> **评估级别**：L级（战略）
> **执行团队**：Graphify 智囊团全员 + Harness Ops 团队
> **决策者**：Lysander CEO → 总裁验收

---

## 一、项目概况

| 项 | 详情 |
|----|------|
| 名称 | gstack |
| 作者 | Garry Tan（Y Combinator 总裁兼 CEO） |
| 发布日期 | 2026-03-12 |
| 许可证 | MIT |
| GitHub Stars | 69.7k（30天内） |
| Forks | 9.8k |
| 定位 | Claude Code 的 Skills Pack，让一个人像20人团队一样 Ship 产品 |
| 自述成果 | 60天内 600,000+ 行生产代码，每周 10,000-20,000 行 |

---

## 二、gstack 技术架构

### 核心组成

```
gstack/
├── 30+ Slash Commands (Skills)     — 每个 = 一个专家角色的结构化 Prompt
│   ├── 规划类：/office-hours, /plan-ceo-review, /plan-eng-review, /plan-design-review
│   ├── 设计类：/design-shotgun, /design-html, /design-consultation
│   ├── 审查类：/review, /cso, /codex (跨模型)
│   ├── 测试类：/qa, /qa-only, /benchmark, /canary
│   ├── 发布类：/ship, /land-and-deploy, /document-release
│   ├── 安全类：/careful, /freeze, /guard
│   └── 工具类：/browse, /learn, /retro, /investigate
│
├── CLAUDE.md 注入                   — 全局行为规则
├── Artifact Chaining               — 上游输出自动传递给下游
├── ~/.gstack/ 全局状态              — 跨项目持久化
├── Playwright 浏览器自动化          — /browse, /qa 实际测试
├── Hook 系统                        — PreToolUse 钩子实现安全护栏
├── 多 AI 平台适配                   — Claude/Codex/Cursor/Kiro/Factory 等8家
└── Telemetry + Learning            — 使用分析 + 项目级学习记忆
```

### 完整工作流

```
Think → Plan → Build → Review → Test → Ship → Reflect
  │        │       │        │        │       │       │
  ▼        ▼       ▼        ▼        ▼       ▼       ▼
office   plan-*   design   review   qa     ship    retro
hours    系列      系列     + cso   +bench  +land   
                           +codex  +canary  +doc
```

### 关键设计模式

1. **Artifact Chaining**：/office-hours 写设计文档 → /plan-ceo-review 读取 → /plan-eng-review 引用。零手动搬运。
2. **Hook 安全护栏**：/careful 通过 PreToolUse Hook 拦截破坏性命令，不靠 Prompt 约束。
3. **角色隔离**：每个 Skill 有独立的 Persona + 方法论 + 输出格式。
4. **跨模型二审**：/codex 调用 OpenAI Codex 对同一 PR 做独立审查。
5. **Smart Routing**：自动检测变更类型，推荐适合的 Review Skill。

---

## 三、gstack vs Synapse 全维度对比

| 维度 | gstack | Synapse | 判定 |
|------|--------|---------|------|
| 定位 | 个人开发者虚拟工程团队 | 企业级 AI 协作运营体系 | 不同赛道 |
| 角色体系 | 30+ Skills（隐式角色） | 44人显式组织架构（10团队） | Synapse 更完整 |
| 工作流 | Think→Plan→Build→Review→Test→Ship→Reflect | 目标→分级→派单→执行→QA→交付 | 各有优势 |
| **Artifact 传递** | ✅ 自动链式传递 | ❌ 靠对话上下文 | **gstack 领先** |
| **Slash Commands** | ✅ 30+ 即开即用 | ❌ 无自定义 Skill | **gstack 领先** |
| **浏览器自动化** | ✅ Playwright 集成 | ❌ 无 | **gstack 领先** |
| **安全护栏 Hook** | ✅ PreToolUse 拦截 | ❌ 仅靠 Prompt | **gstack 领先** |
| **多模型协作** | ✅ Claude + Codex | ❌ 仅 Claude | **gstack 领先** |
| 决策体系 | ❌ 无 | ✅ 四级决策制 L1-L4 | **Synapse 领先** |
| 组织治理 | ❌ 无 | ✅ HR全生命周期+执行审计 | **Synapse 领先** |
| 知识管理 | 简单 /learn 记忆 | ✅ OBS知识库5层架构 | **Synapse 领先** |
| 跨团队协调 | ❌ 单人场景 | ✅ 智囊团+派单+路由 | **Synapse 领先** |
| 自动化编排 | ❌ 手动触发 | ✅ 定时+事件+状态触发 | **Synapse 领先** |
| 质量门禁 | 隐含在 Skills 中 | ✅ QA 自动评分 | Synapse 更显式 |
| 业务适用 | 纯软件开发 | 多行业多领域 | **Synapse 更广** |
| 安装部署 | 30秒一键 | 手动配置 | **gstack 领先** |
| 开源生态 | 69.7k Stars | 内部使用 | **gstack 领先** |

---

## 四、核心洞察

### 关联发现（relation_discovery）

> gstack 和 Synapse 是**互补关系**，不是竞争关系：
> - gstack = **执行引擎**（怎么高效写代码、测试、部署）
> - Synapse = **管理操作系统**（怎么组织团队、做决策、管知识）
> - **gstack 缺的正是 Synapse 有的，Synapse 缺的正是 gstack 有的**

### 趋势判断（trend_watcher）

1. **"一人公司"模式被技术验证** — YC 总裁亲自背书
2. **AI Coding 从"代码生成"进化到"全流程编排"** — Think/Plan/Build/Review/Test/Ship/Reflect
3. **Skill Pack 将成为新一代"包管理器"** — AI Skills 像插件一样共享和组合
4. **多模型协作已成现实** — Claude + Codex 交叉审查

---

## 五、战略方案：分阶段吸收融合

### 阶段一：源码研读与模式提取（已完成）

- ✅ 克隆到隔离目录 `_eval/gstack/`
- ✅ 安全审计 setup 脚本（结论：不运行 setup，避免全局污染）
- ✅ 分析核心 Skill 设计模式（office-hours, review, ship, careful, freeze）
- ✅ 提取5大可借鉴模式

### 阶段二：选择性吸收（下一步）

| 优先级 | 吸收项 | 价值 | 落地方式 |
|--------|--------|------|----------|
| P0 | **Slash Commands 体系** | Synapse 最大短板 | 在 `.claude/commands/` 为每个团队创建 Skill |
| P0 | **Artifact Chaining** | 消灭手动搬运 | 设计标准 Artifact 格式和传递协议 |
| P1 | **Hook 安全护栏** | 从 Prompt 约束升级到代码拦截 | 移植 /careful 的 PreToolUse Hook |
| P1 | **浏览器自动化** | QA 实测能力从0到1 | 集成 Playwright |
| P2 | **多模型二审** | 提升审查质量 | 集成 Codex 作为独立审查人 |

### 阶段三：Synapse 2.0

- 管理 OS + 执行引擎合一
- 差异化定位：gstack 是个人工具，Synapse 是 AI 团队操作系统
- 考虑开源核心模块

---

## 六、Setup 安全审计结论

| 影响项 | 风险 | 决策 |
|--------|------|------|
| `~/.claude/skills/gstack/` 全局安装 | 中 — 影响所有会话 | ❌ 不安装 |
| `--team` 修改 CLAUDE.md | 高 — 改我们的核心配置 | ❌ 不运行 |
| `~/.gstack/` 全局状态 | 低 | 暂不创建 |
| 隔离目录研读 | 零 | ✅ 已执行 |

**总结：在隔离目录中研读源码、提取设计模式，不做任何全局安装。**

---

## 七、QA 评分

- 执行链完整性：✅ 全流程
- 团队派单记录：✅ 完整
- 信息源：GitHub / TechCrunch / Augment Code / Medium 等多源交叉
- 对比维度：16项
- 方案可落地性：✅ 三阶段 + 优先级

**综合评分：4.2/5.0**
