# Agent 智能体系 - 开箱即用包

> 新同事clone后即可使用的完整AI团队协作体系

## 体系架构

```
┌─────────────────────────────────────────────────────────────┐
│                    总裁（用户）— 最高决策者                   │
└─────────────────────────────────────────────────────────────┘
                              ↑
                    战略/重大决策
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Lysander CEO — AI分身                      │
│              （HR知识库 + 决策体系 + 自动化）                 │
└─────────────────────────────────────────────────────────────┘
                              ↑
                    日常管理/方案审批
                              │
┌─────────────────────────────────────────────────────────────┐
│                       智囊团 Graphify                        │
│              （分析/洞察/趋势/决策支持）                     │
└─────────────────────────────────────────────────────────────┘
                              ↑
                      任务执行/专业支持
                              │
┌─────────────────────────────────────────────────────────────┐
│  执行团队：Butler / RD / OBS / Content_ops / Stock          │
│  （HR知识库人员卡片定义，自动化同步）                       │
└─────────────────────────────────────────────────────────────┘
```

## 目录结构

```
agent-system/
├── README.md              ← 本文件
├── SETUP.md              ← 详细安装指南
├── QUICKSTART.md         ← 快速开始
│
├── scripts/              ← 执行脚本
│   ├── setup.sh          ← 一键安装脚本
│   ├── sync-all.sh       ← 同步所有
│   ├── start-watcher.sh  ← 启动文件监控
│   └── daily-publish.sh  ← 博客发布
│
├── agent-butler/          ← Agent Butler核心
│   ├── hr_base.py        ← HR知识库+决策体系
│   ├── hr_watcher.py     ← 文件监控自动同步
│   ├── requirements.txt   ← Python依赖
│   └── config/           ← 配置文件
│
└── docs/                  ← 文档
    ├── ARCHITECTURE.md   ← 架构说明
    ├── DECISION_SYSTEM.md← 决策体系说明
    └── CLAUDE_CODE.md    ← Claude Code集成
```

## 快速开始

### 1. Clone仓库

```bash
git clone https://github.com/lysanderl-glitch/obsidian-knowledge.git
cd obsidian-knowledge
```

### 2. 运行安装脚本

```bash
bash agent-system/scripts/setup.sh
```

### 3. 启动文件监控（后台运行）

```bash
cd agent-system/agent-butler
nohup python3 hr_watcher.py > hr_watcher.log 2>&1 &
```

## 核心功能

### 1. HR知识库自动化

OBSidian修改人员卡片 → 自动同步到YAML配置

### 2. 决策体系

```
任务 → decision_check() → 小问题 → 直接执行
                     → 需智囊团 → 召集分析
                     → 超出授权 → 上报总裁
```

### 3. Claude Code记忆同步

OBSidian修改记忆 → 自动同步到.claude/

### 4. Harness Engineering

错误自动记录 → 模式分析 → 自我修复

## 团队

| 团队 | 专家数 | 职责 |
|------|--------|------|
| Graphify | 4 | 智囊团/第二大脑 |
| Butler | 7 | 项目交付管理 |
| RD | 5 | 技术研发 |
| OBS | 4 | 知识管理 |
| Content_ops | 4 | 内容运营 |
| Stock | 5 | 股票交易系统 |

## 文档

- [SETUP.md](SETUP.md) - 详细安装配置
- [QUICKSTART.md](QUICKSTART.md) - 5分钟快速开始
- [docs/](docs/) - 完整架构文档

## 问题支持

如有问题，请查看：
1. `hr_watcher.log` - 同步日志
2. `docs/DECISION_SYSTEM.md` - 决策体系说明
3. 提交Issue到GitHub仓库
