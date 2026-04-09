# 5分钟快速开始

## 第一步：Clone仓库

```bash
git clone https://github.com/lysanderl-glitch/obsidian-knowledge.git
cd obsidian-knowledge
```

## 第二步：运行安装

```bash
cd agent-system/scripts
bash setup.sh
```

安装脚本会：
1. 检查Python依赖
2. 安装Python包
3. 同步Claude Code记忆
4. 启动文件监控

## 第三步：启动Claude Code

```bash
claude
```

## 第四步：开始使用

### 基本命令

| 命令 | 说明 |
|------|------|
| `bash scripts/start-watcher.sh` | 启动文件监控 |
| `python3 agent-butler/hr_base.py sync` | 手动同步HR知识库 |
| `bash scripts/sync-all.sh` | 同步所有系统 |

### 决策体系

系统会自动判断任务类型：

- **小问题**（如"同步文件"）→ 直接执行
- **需要智囊团**（如"帮我分析"）→ 召集分析后执行
- **重大决策**（如"战略规划"）→ 上报总裁

### 示例对话

```
用户: lysander 需要做一个数字化交付方案
系统: [自动路由到Butler团队]
```

## 验证安装

```bash
# 检查watcher是否运行
pgrep -f hr_watcher.py

# 检查HR同步
cd agent-butler && python3 hr_base.py harness-stats
```

## 常见问题

### Q: hr_watcher启动失败
A: 检查Python依赖 `pip3 install -r requirements.txt`

### Q: Claude Code记忆未同步
A: 运行 `bash scripts/sync-claude-memory.sh`

### Q: 同步失败
A: 检查Git配置 `git config --global user.email "your@email.com"`

## 下一步

- 查看 [README.md](README.md) 了解完整架构
- 查看 [docs/](docs/) 目录了解更多细节
