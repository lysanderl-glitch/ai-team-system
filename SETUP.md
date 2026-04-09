# 详细安装配置指南

## 系统要求

- Python 3.8+
- Git
- Claude Code (可选，用于AI对话)

## 目录结构

```
ai-team-system/              # Git仓库根目录
├── CLAUDE.md               # Claude Code项目配置
├── README.md               # 项目说明
├── QUICKSTART.md           # 快速开始
├── SETUP.md                # 本文档
├── LICENSE                 # MIT许可证
│
├── agent-butler/           # Agent系统核心
│   ├── hr_base.py          # HR知识库+决策体系
│   ├── hr_watcher.py       # 文件监控
│   └── config/             # 配置文件
│       ├── organization.yaml   # 团队结构配置
│       ├── *_experts.yaml      # AI Agent定义
│       └── ...
│
├── scripts/                # 执行脚本
│   ├── setup.sh            # 一键安装
│   ├── sync-all.sh         # 全量同步
│   ├── sync-claude-memory.sh  # Claude记忆同步
│   └── start-watcher.sh    # 启动文件监控
│
├── obs/                    # Obsidian知识库
│   └── 01-team-knowledge/  # 团队知识
│       └── HR/             # HR知识体系
│           ├── personnel/  # 人员卡片
│           │   ├── butler/
│           │   ├── rd/
│           │   ├── obs/
│           │   ├── graphify/
│           │   ├── content_ops/
│           │   ├── stock/
│           │   └── lysander/
│           └── positions/  # 岗位定义
│
└── docs/                   # 详细文档
    ├── ARCHITECTURE.md     # 架构说明
    ├── DECISION_SYSTEM.md  # 决策体系详解
    └── CLAUDE_CODE.md      # Claude Code集成
```

## 安装步骤

### 1. 基础环境

```bash
# 检查Python版本
python3 --version

# 检查Git
git --version
```

### 2. Clone仓库

```bash
git clone https://github.com/lysanderl-glitch/ai-team-system.git
cd ai-team-system
```

### 3. 运行安装脚本

```bash
bash scripts/setup.sh
```

### 4. 手动验证

```bash
# 验证HR知识库加载
cd agent-butler
python3 -c "from hr_base import load_org_config; print('OK')"

# 验证团队配置
python3 -c "from hr_base import load_org_config; c=load_org_config(); print('Teams:', list(c['teams'].keys()))"
```

### 5. 配置Git（必需）

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## Claude Code配置

### 1. 安装Claude Code

参考: https://docs.anthropic.com/en/docs/claude-code/setup

### 2. 使用方式

```bash
claude
```

Claude Code会自动加载项目根目录的 `CLAUDE.md` 文件。

## 团队配置

### 团队列表

| 团队 | 人数 | 职责 |
|------|------|------|
| butler | 8 | 数字化交付/IoT |
| rd | 5 | 技术研发 |
| obs | 4 | 知识管理 |
| graphify | 4 | 智囊团/分析 |
| content_ops | 4 | 内容运营 |
| stock | 5 | 股票交易 |

### 添加新团队成员

1. 在 `obs/01-team-knowledge/HR/personnel/{team}/` 创建人员卡片

2. 更新 `agent-butler/config/organization.yaml`:
   ```yaml
   teams:
     {team}:
       specialists:
         - {specialist_id}
   ```

3. 创建对应的 `agent-butler/config/{team}_experts.yaml` Agent定义

### 更新决策体系

编辑 `agent-butler/config/decision_rules.yaml`

## 文件监控

### 启动监控

```bash
cd agent-butler
bash ../scripts/start-watcher.sh
```

### 监控内容

- `obs/01-team-knowledge/HR/personnel/*` → 自动同步配置

### 查看日志

```bash
tail -f agent-butler/hr_watcher.log
```

## 同步命令

| 命令 | 说明 |
|------|------|
| `bash scripts/sync-all.sh` | 全量同步 |
| `python3 agent-butler/hr_base.py sync` | 同步HR知识库 |

## 环境变量（可选）

```bash
# 自定义知识库路径（默认从 ../obs 相对路径查找）
export OBS_KB_ROOT="/path/to/obs"

# Claude API Key
export ANTHROPIC_API_KEY="sk-..."

# n8n服务器
export N8N_URL="https://n8n.example.com"
```

## 故障排查

### Python依赖安装失败

```bash
pip3 install pyyaml watchdog --break-system-packages
```

### hr_watcher无法启动

```bash
# 检查Python版本
python3 --version

# 检查watchdog
python3 -c "import watchdog; print('ok')"
```

## 技术支持

1. 查看日志: `tail -f agent-butler/hr_watcher.log`
2. 查看 GitHub Issues
3. 查看 `docs/` 目录的详细文档
