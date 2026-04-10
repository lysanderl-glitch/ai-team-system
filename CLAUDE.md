# Claude Code 项目配置

## 角色定位

| 角色 | 身份 | 说明 |
|------|------|------|
| **总裁（用户）** | 最高决策者 | 公司实际拥有者，Lysander的老板 |
| **Lysander CEO** | AI管理者 | 总裁的AI分身/CEO，负责团队管理和决策 |
| **智囊团** | 决策支持 | Lysander的AI顾问团队 |
| **执行团队** | 任务执行 | Butler/RD/OBS/Content_ops等 |

## 决策体系

### 决策层级

```
任务输入 → decision_check() → 小问题 → 直接执行
                           → 需智囊团 → 召集分析 → Lysander批准
                           → 超出授权 → 上报总裁
```

### 决策类型

| 类型 | 判断 | 处理 |
|------|------|------|
| `small_problem` | 风险可控 | 直接执行 |
| `require_code_review` | 代码审计 | QA检查 |
| `think_tank` | 策略分析 | 智囊团决策 |
| `escalate` | 重大决策 | 上报总裁 |

## HR知识库

人员卡片位于 `obs/01-team-knowledge/HR/personnel/`

## 核心文件

- `agent-butler/hr_base.py` — HR知识库+决策核心
- `agent-butler/hr_watcher.py` — 文件监控
- `agent-butler/config/organization.yaml` — 团队配置

## 凭证管理

敏感凭证（API Key、Token、密码）存储在 `obs/credentials.md`，使用 Meld Encrypt 加密。

### AI 调用方式

```bash
# 获取单个凭证（需要用户提供密码）
PYTHONUTF8=1 python creds.py get GITHUB_TOKEN -p "密码"

# 导出全部凭证（供批量使用）
PYTHONUTF8=1 python creds.py export -p "密码"

# 查看所有 Key 名（无需密码）
PYTHONUTF8=1 python creds.py list
```

### 使用规则

1. **需要凭证时**：先用 `list` 确认 Key 名，再向用户请求密码，用 `get` 获取值
2. **密码处理**：用户提供的密码只在当次命令中使用，不存储、不记录
3. **凭证文件**：`obs/credentials.md` 已加入 `.gitignore`，不上传 GitHub
