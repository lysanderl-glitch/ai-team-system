# 详细安装配置指南

## 系统要求

- Python 3.8+
- Git
- Claude Code (可选，用于AI对话)

## 目录结构

```
obsidian-knowledge/          # Git仓库根目录
├── agent-system/           # Agent系统
│   ├── agent-butler/       # 核心代码
│   │   ├── hr_base.py      # HR知识库+决策体系
│   │   ├── hr_watcher.py   # 文件监控
│   │   └── config/         # 配置文件
│   └── scripts/            # 执行脚本
├── obs/                    # OBSidian知识库（Git管理）
│   ├── 00-system/           # 系统配置
│   │   └── claude-code-memory/  # Claude Code记忆
│   └── 01-team-knowledge/  # 团队知识
│       └── HR/             # HR知识体系
└── docs/                   # 文档
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
git clone https://github.com/lysanderl-glitch/obsidian-knowledge.git
cd obsidian-knowledge
```

### 3. 运行安装脚本

```bash
cd agent-system/scripts
bash setup.sh
```

### 4. 手动验证

```bash
# 验证HR知识库同步
cd ../../agent-butler
python3 hr_base.py sync

# 验证Claude Code记忆
bash ../scripts/sync-claude-memory.sh
```

### 5. 配置Git（必需）

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## Claude Code配置

### 1. 安装Claude Code

参考: https://docs.anthropic.com/en/docs/claude-code/setup

### 2. 配置项目记忆

系统会自动同步OBSidian中的记忆到Claude Code：
- 位置: `obs/00-system/claude-code-memory/`
- 目标: `~/.claude/projects/-home-ubuntu/memory/`

### 3. 使用方式

```bash
claude
```

系统会自动加载记忆文件，包含角色定位和决策体系。

## 团队配置

### 添加新团队成员

1. 在OBSidian中创建人员卡片:
   ```
   obs/01-team-knowledge/HR/personnel/{team}/{specialist_id}.md
   ```

2. 更新organization.yaml:
   ```yaml
   teams:
     {team}:
       specialists:
         - {specialist_id}
   ```

3. 系统自动同步（hr_watcher监控中）

### 更新决策体系

编辑 `obs/00-system/claude-code-memory/` 中的记忆文件，系统自动同步。

## 文件监控

### 启动监控

```bash
cd agent-system/agent-butler
bash ../scripts/start-watcher.sh
```

### 监控内容

- `obs/01-team-knowledge/HR/personnel/*` → 自动同步到YAML
- `obs/00-system/claude-code-memory/*` → 自动同步到.claude/

### 查看日志

```bash
tail -f agent-system/agent-butler/hr_watcher.log
```

## 同步命令

| 命令 | 说明 |
|------|------|
| `bash scripts/sync-all.sh` | 同步所有（HR+YAML+记忆+Git） |
| `python3 hr_base.py sync` | 仅同步HR知识库 |
| `bash scripts/sync-claude-memory.sh` | 仅同步Claude记忆 |

## 博客发布

```bash
bash agent-system/scripts/daily-publish.sh
```

或使用完整发布流程:
```bash
cd agent-butler
python3 hr_base.py sync  # 同步
npm run build            # 构建网站（需在website目录）
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

### Git推送失败

```bash
# 检查远程仓库
git remote -v

# 重新设置（如果需要）
git remote set-url origin https://github.com/lysanderl-glitch/obsidian-knowledge.git
```

## 目录权限

确保以下目录有写权限：
- `agent-butler/config/` - 写入YAML配置
- `~/.claude/` - 写入记忆文件
- `obs/` - Git操作

## 环境变量（可选）

```bash
# Claude API Key
export ANTHROPIC_API_KEY="sk-..."

# n8n服务器
export N8N_URL="https://n8n.lysander.bond"
```

## 技术支持

1. 查看日志: `tail -f agent-butler/hr_watcher.log`
2. 查看GitHub Issues
3. 查看 `docs/` 目录的详细文档
