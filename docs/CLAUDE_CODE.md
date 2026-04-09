# Claude Code 集成说明

## 角色定位

Claude Code 是 Lysander CEO 的 AI 助手/分身，不是 Lysander 本人。

| 角色 | 说明 |
|------|------|
| 总裁（用户） | 最高决策者，Lysander的老板 |
| Lysander CEO | AI分身，Claude Code的管理对象 |
| Claude Code | Lysander的AI助手，执行具体任务 |

## 记忆系统

### 记忆存储位置

Claude Code 记忆存储在 OBSidian 中：
```
obs/00-system/claude-code-memory/
├── MEMORY.md           # 索引
├── user_role.md        # 角色定位
├── feedback_*.md       # 经验教训
└── project_*.md       # 项目状态
```

### 同步机制

文件变化 → hr_watcher检测 → sync-claude-memory.sh同步 → .claude/

### 手动同步

```bash
bash agent-system/scripts/sync-claude-memory.sh
```

## 决策体系集成

Claude Code 加载后自动识别：

### 决策流程

```
用户输入 → decision_check() → 判断类型
                              ↓
           ┌─────────────────┼─────────────────┐
           ↓                 ↓                 ↓
      小问题          需智囊团           超出授权
           ↓                 ↓                 ↓
      直接执行       召集分析后执行      上报总裁
```

### 决策类型

| 类型 | 说明 | 处理 |
|------|------|------|
| `small_problem` | 风险可控 | 直接执行 |
| `require_code_review` | 代码审计 | QA检查 |
| `think_tank` | 策略分析 | 智囊团决策 |
| `escalate` | 重大决策 | 上报总裁 |

## 使用示例

### 1. 查看团队状态

```
用户: lysander 查看RD团队状态
Claude: [自动路由] → assemble_team_for_task() → 返回团队信息
```

### 2. 同步HR知识库

```
用户: lysander 同步HR知识库
Claude: decision_check("同步HR知识库") → small_problem → 直接执行 sync
```

### 3. 需要分析

```
用户: lysander 帮我分析这个项目的风险
Claude: decision_check() → think_tank → 召集智囊团分析
```

## CLAUDE.md 配置

项目根目录的 `CLAUDE.md` 包含：

- 角色定位定义
- 决策体系说明
- 工作流程
- 日记系统配置

## 记忆文件说明

### user_role.md

```yaml
---
name: user_role
type: user
---
## 角色定位

- 总裁（用户）= 最高决策者
- Lysander CEO = AI分身
- Claude Code = Lysander的AI助手
```

### feedback_*.md

Harness Engineering 经验教训：
- 错误模式
- 解决方案
- 预防措施

### project_*.md

项目状态和上下文：
- 当前工作
- 技术栈
- 团队成员

## 故障排查

### 记忆未同步

```bash
# 手动同步
bash agent-system/scripts/sync-claude-memory.sh

# 检查日志
tail -f agent-system/agent-butler/hr_watcher.log
```

### Claude Code未加载记忆

1. 重启Claude Code
2. 检查记忆目录: `ls ~/.claude/projects/-home-ubuntu/memory/`
3. 重新同步: `bash scripts/sync-claude-memory.sh`

## 环境变量

```bash
# Claude API Key
export ANTHROPIC_API_KEY="sk-..."

# 项目路径（自动检测）
```

## 下一步

- 查看 [SETUP.md](../SETUP.md) - 完整安装指南
- 查看 [DECISION_SYSTEM.md](DECISION_SYSTEM.md) - 决策体系详解
- 查看 [ARCHITECTURE.md](ARCHITECTURE.md) - 架构说明
