# Synapse — AI 协作运营体系

> **Synapse** 是 Janus Digital 的 AI 协作运营体系。  
> 突触（Synapse）是神经元之间传递信号的关键节点 —  
> 知识(OBS) ←突触→ 决策(Harness) ←突触→ 执行(Agents)，一切信息流转的核心枢纽。

---

## 体系架构

```
┌─────────────────────────────────────────────────────────────┐
│                 总裁 刘子杨 — 提目标 + 最终验收               │
└─────────────────────────────────────────────────────────────┘
                              ↑ L4决策才上报
┌─────────────────────────────────────────────────────────────┐
│              Lysander CEO — 全权统筹执行                     │
│         （Harness配置 + 执行链 + 四级决策体系）               │
└─────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────┐
│              Graphify 智囊团 — 第二大脑                      │
│    分析/洞察/趋势/决策支持/执行审计/AI情报                    │
└─────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────┐
│  执行团队：Butler / Janus / Harness Ops / RD                │
│           OBS / 内容团队 / 增长团队 / Stock                  │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 1. Clone 仓库

```bash
git clone https://github.com/lysanderl-glitch/ai-team-system.git
cd ai-team-system
```

### 2. 安装依赖

```bash
pip install pyyaml watchdog markdown pygments
```

### 3. 打开 Claude Code

在 `ai-team-system` 目录下启动 Claude Code，系统自动加载 `CLAUDE.md`（Synapse Harness 配置），Lysander 立即就位。

## 团队

| 团队 | 专家数 | 职责 |
|------|--------|------|
| Graphify 智囊团 | 6 | 战略分析/决策支持/执行审计/AI情报 |
| Butler | 7 | 项目交付管理/IoT/PMO/UAT |
| Janus | 6 | 建筑数字化交付/BIM/WBS |
| Harness Ops | 4 | Synapse 体系维护/自动化开发/QA |
| RD 研发 | 5 | 系统开发/架构/DevOps |
| OBS 知识管理 | 4 | 知识沉淀/检索/质量 |
| 内容团队 | 4 | 文章生成/报告/文档/HTML导出 |
| 增长团队 | 2 | 客户洞察/GTM策略 |
| Stock | 5 | A股量化交易系统 |

## 目录结构

```
ai-team-system/              ← Synapse 根目录
├── CLAUDE.md                # Synapse Harness 配置（执行链+决策体系）
├── README.md                # 本文件
├── COLLEAGUE_GUIDE.md       # 同事使用指南
├── FIRST_PROMPT.md          # 首次使用引导词
├── creds.py                 # 凭证管理（Meld Encrypt）
│
├── agent-butler/            # Harness 核心
│   ├── hr_base.py           # HR知识库+决策引擎
│   ├── hr_watcher.py        # 文件监控
│   └── config/              # 配置文件
│       ├── organization.yaml
│       └── n8n_integration.yaml
│
├── scripts/                 # 工具脚本
│   ├── generate-article.py  # Markdown → HTML 文章生成
│   ├── setup.sh / setup.bat
│   └── sync-all.sh
│
├── obs/                     # Obsidian 知识库（第二大脑）
│   ├── 00-daily-work/
│   ├── 01-team-knowledge/HR/personnel/  # 人员卡片
│   ├── 02-project-knowledge/
│   ├── 03-process-knowledge/            # SOP
│   ├── 04-decision-knowledge/
│   ├── 05-industry-knowledge/
│   ├── generated-articles/              # HTML 文章归档
│   └── credentials.mdenc               # 加密凭证（不上传）
│
└── docs/                    # 架构文档
```

## 文档

- [COLLEAGUE_GUIDE.md](COLLEAGUE_GUIDE.md) — 同事使用指南
- [FIRST_PROMPT.md](FIRST_PROMPT.md) — 首次引导词
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 完整架构

## 问题支持

提交 Issue：https://github.com/lysanderl-glitch/ai-team-system/issues
