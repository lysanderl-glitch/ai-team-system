# AI团队协作体系

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

## 快速开始

### 1. Clone仓库

```bash
git clone https://github.com/lysanderl-glitch/ai-team-system.git
cd ai-team-system
```

### 2. 运行安装脚本

```bash
bash scripts/setup.sh
```

### 3. 启动文件监控（可选）

```bash
cd agent-butler
nohup python3 hr_watcher.py > hr_watcher.log 2>&1 &
```

## 核心功能

### 1. HR知识库自动化

Obsidian修改人员卡片 → 自动同步到YAML配置

### 2. 决策体系

```
任务 → decision_check() → 小问题 → 直接执行
                     → 需智囊团 → 召集分析
                     → 超出授权 → 上报总裁
```

### 3. Harness Engineering

错误自动记录 → 模式分析 → 自我修复

## 团队

| 团队 | 专家数 | 职责 |
|------|--------|------|
| Graphify | 5 | 智囊团/第二大脑/执行审计 |
| Butler | 7 | 项目交付管理 |
| Janus | 6 | 建筑数字化交付 |
| RD | 5 | 技术研发 |
| OBS | 4 | 知识管理 |
| 内容团队 | 3 | 文档/报告/提案内容 |
| 增长团队 | 2 | 市场洞察/GTM策略 |
| Stock | 5 | 股票交易系统 |

## 目录结构

```
ai-team-system/
├── CLAUDE.md              # Claude Code项目配置
├── README.md              # 本文件
├── SETUP.md               # 详细安装指南
├── QUICKSTART.md          # 快速开始
│
├── agent-butler/          # Agent系统核心
│   ├── hr_base.py         # HR知识库+决策体系
│   ├── hr_watcher.py      # 文件监控
│   └── config/            # 配置文件
│
├── scripts/               # 执行脚本
│   ├── setup.sh           # 一键安装
│   ├── sync-all.sh        # 全量同步
│   └── start-watcher.sh   # 启动监控
│
├── obs/                   # Obsidian知识库
│   └── 01-team-knowledge/
│       └── HR/           # HR知识体系
│           ├── personnel/ # 人员卡片（29人）
│           └── positions/ # 岗位定义
│
└── docs/                  # 详细文档
    ├── ARCHITECTURE.md
    ├── DECISION_SYSTEM.md
    └── CLAUDE_CODE.md
```

## 文档

- [SETUP.md](SETUP.md) - 详细安装配置
- [QUICKSTART.md](QUICKSTART.md) - 5分钟快速开始
- [docs/](docs/) - 完整架构文档

## 问题支持

如有问题，请查看：
1. `hr_watcher.log` - 同步日志
2. `docs/DECISION_SYSTEM.md` - 决策体系说明
3. 提交Issue到GitHub仓库
