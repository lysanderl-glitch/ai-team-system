# Synapse 体系构建文档

> **本文档双重用途：**
> - 人类同事：了解每步在做什么，知道何时需要手动操作
> - Claude Code：按本文档逐步完成全自动构建
>
> **同事只需将以下一句话发给 Claude Code：**
> ```
> 请从 https://raw.githubusercontent.com/lysanderl-glitch/ai-team-system/master/SYNAPSE_SETUP.md 获取安装文档，按文档完成 Synapse 体系构建。
> ```

---

## Claude Code 执行指令

以下是给 Claude Code 的完整构建步骤，请严格按顺序执行。每步完成后打印状态，遇到错误立即报告并等待用户确认后继续。

---

### STEP 1：环境检测

检测以下工具是否已安装，输出检测报告：

```
检测项：
- Git：运行 git --version
- Python：运行 python --version 或 python3 --version
- pip：运行 pip --version
- Obsidian：检查 C:\Users\{用户名}\AppData\Local\Obsidian\Obsidian.exe 是否存在
- winget：运行 winget --version
```

输出格式示例：
```
[STEP 1] 环境检测
✅ Git        已安装 (git version 2.44.0)
❌ Python     未安装
✅ Obsidian   已安装
✅ winget     已安装 (v1.7.10582)
```

---

### STEP 2：安装缺失工具

**注意：安装过程中 Windows 会弹出 UAC 权限确认框，请点击"是"。**

根据 STEP 1 的检测结果，仅安装缺失的工具：

```bash
# 安装 Git（如未安装）
winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements

# 安装 Python 3（如未安装）
winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements

# 安装 Obsidian（如未安装）
winget install --id Obsidian.Obsidian -e --source winget --accept-package-agreements --accept-source-agreements
```

安装完成后，重新运行 STEP 1 的检测命令确认全部通过。

**如果 winget 不可用：**
提示用户手动下载：
- Git：https://git-scm.com/download/win
- Python：https://www.python.org/downloads/windows/（安装时勾选"Add to PATH"）
- Obsidian：https://obsidian.md/download

---

### STEP 3：克隆 Synapse 仓库

将仓库克隆到用户文档目录：

```bash
# 创建目标目录（如不存在）
mkdir -p "$HOME/Documents/Synapse"

# 克隆仓库
git clone https://github.com/lysanderl-glitch/ai-team-system.git "$HOME/Documents/Synapse/ai-team-system"
```

克隆成功后输出：
```
[STEP 3] 仓库克隆
✅ 已克隆到：C:\Users\{用户名}\Documents\Synapse\ai-team-system
```

**如果目录已存在（已克隆过）：**
```bash
cd "$HOME/Documents/Synapse/ai-team-system"
git pull origin master
```

---

### STEP 4：安装 Python 依赖

```bash
cd "$HOME/Documents/Synapse/ai-team-system"
pip install -r agent-butler/requirements.txt
```

依赖列表（供参考）：
- `pyyaml` — HR 知识库解析
- `watchdog` — 文件监控
- `markdown` — Markdown 转 HTML
- `pygments` — 代码语法高亮

安装完成后验证：
```bash
python -c "import yaml, markdown, pygments; print('依赖验证通过')"
```

---

### STEP 5：配置 Obsidian Vault

将 Synapse 知识库注册到 Obsidian：

读取当前 Obsidian 配置文件：
```
路径：C:\Users\{用户名}\AppData\Roaming\obsidian\obsidian.json
```

在 `vaults` 字段中添加新条目：
```json
{
  "path": "C:\\Users\\{用户名}\\Documents\\Synapse\\ai-team-system\\obs",
  "ts": {当前时间戳毫秒},
  "open": true
}
```

**注意：** obsidian.json 中的 vault key 为随机16位hex字符串，生成一个新的唯一 key 添加即可。

---

### STEP 6：验证安装

运行以下验证命令，确认体系完整：

```bash
cd "$HOME/Documents/Synapse/ai-team-system"

# 验证 HR 知识库加载
python -c "
import sys
sys.path.insert(0, 'agent-butler')
from hr_base import load_org_config
config = load_org_config()
teams = list(config['teams'].keys())
print(f'✅ HR知识库加载成功，团队数：{len(teams)}')
print(f'   团队列表：{teams}')
"

# 验证文章生成脚本
python scripts/generate-article.py obs/03-process-knowledge/daily-workflow-sop.md
```

输出示例：
```
[STEP 6] 安装验证
✅ HR知识库加载成功，团队数：8
   团队列表：['butler', 'janus', 'harness_ops', 'rd', 'obs', 'content_ops', 'growth', 'stock']
✅ 文章生成脚本正常
   Generated: obs/generated-articles/2026-04-10-日常工作流-sop.html
```

---

### STEP 7：完成报告 + 下一步引导

构建完成后，输出以下内容：

```
╔══════════════════════════════════════════════════════════╗
║         Synapse 体系构建完成！                           ║
╚══════════════════════════════════════════════════════════╝

安装位置：C:\Users\{用户名}\Documents\Synapse\ai-team-system

✅ Git          已就绪
✅ Python       已就绪
✅ Obsidian     已就绪
✅ Python依赖   已安装
✅ HR知识库     加载正常（8个团队）
✅ Obsidian库   已注册

════════════════════════════════════════════════════════════
下一步：开始使用 Synapse
════════════════════════════════════════════════════════════

1. 在 Claude Code 中打开文件夹：
   C:\Users\{用户名}\Documents\Synapse\ai-team-system

2. 发送以下引导词开始使用：
   "你好，请以 Lysander 身份问候我，并介绍当前 Synapse 团队。"

3. 打开 Obsidian，选择 Synapse vault 查看知识库结构。

详细使用指南见：COLLEAGUE_GUIDE.md
首次引导词见：FIRST_PROMPT.md
```

---

## 故障排除

| 错误 | 原因 | 解决 |
|------|------|------|
| `winget` 无法识别 | Windows 版本过旧 | 手动下载安装，见 STEP 2 |
| `git clone` 失败 | 网络/代理问题 | 检查网络，或使用 GitHub Desktop 克隆 |
| `pip install` 失败 | Python 未加入 PATH | 重装 Python，勾选 "Add to PATH" |
| `ModuleNotFoundError` | 依赖未安装 | 重新运行 STEP 4 |
| Obsidian 未显示 Synapse vault | obsidian.json 写入失败 | 手动打开 Obsidian → Open folder as vault → 选择 `obs/` 目录 |
| Claude Code 未加载 CLAUDE.md | 打开了错误目录 | 确认打开的是 `ai-team-system/` 根目录 |

---

## 手动安装备选（完全不用命令行）

如果同事不熟悉终端，Claude Code 可引导完成以下手动步骤：

1. 浏览器访问 https://github.com/lysanderl-glitch/ai-team-system → 点 **Code** → **Download ZIP** → 解压到 `文档/Synapse/`
2. 双击运行 `scripts/setup.bat`（自动安装 Python 依赖）
3. 打开 Obsidian → Open folder as vault → 选择 `obs/` 文件夹
4. 打开 Claude Code → Open Folder → 选择 `ai-team-system/` 文件夹
5. 发送引导词开始使用

---

*Synapse — Janus Digital AI 协作运营体系*  
*文档版本：v1.0 · 2026-04-10*
