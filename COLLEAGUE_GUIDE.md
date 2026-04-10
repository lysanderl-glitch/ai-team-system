# 同事使用指南 — AI团队协作体系

> 本指南帮助你在 5 分钟内完成初始化，开始使用 AI 团队协作体系。

---

## 一、你将获得什么

- **29 个 AI 专家**随时待命，覆盖交付/研发/知识管理/内容运营/智囊团/股票项目
- **自动任务路由**：说出需求，系统自动分派给对应专家团队
- **决策体系**：小事直接执行，大事上报决策，不乱来
- **Obsidian 第二大脑**：团队知识结构化沉淀

---

## 二、前提条件

| 工具 | 用途 | 下载 |
|------|------|------|
| **Python 3.8+** | 驱动 HR 知识库 | python.org |
| **Git** | 拉取代码 | git-scm.com |
| **Claude Code** | AI 对话入口 | 参考下方说明 |
| **Obsidian**（可选） | 查看/编辑人员卡片 | obsidian.md |

### 安装 Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

安装后需要用 Anthropic 账号登录（首次运行 `claude` 会引导）。

---

## 三、快速初始化（一次性）

### 第 1 步：获取代码

```bash
git clone https://github.com/lysanderl-glitch/ai-team-system.git
cd ai-team-system
```

### 第 2 步：安装依赖

**Windows 双击运行：**
```
scripts\setup.bat
```

**或手动安装：**
```bash
pip install pyyaml watchdog
```

### 第 3 步：验证

```bash
cd agent-butler
python -c "from hr_base import load_org_config; c=load_org_config(); print('OK - Teams:', list(c['teams'].keys()))"
```

输出 `OK - Teams: ['butler', 'rd', 'obs', ...]` 即成功。

### 第 4 步：（可选）用 Obsidian 打开知识库

打开 Obsidian → 选择 **"Open folder as vault"** → 选择仓库内的 `obs\` 文件夹。

即可看到所有 AI 团队人员卡片，可直接浏览和编辑。

---

## 四、开始使用

在 `ai-team-system` 目录启动 Claude Code：

```bash
claude
```

Claude Code 会自动加载 `CLAUDE.md`，激活完整的 AI 团队体系。

---

## 五、对话示例

| 你说 | 系统行为 |
|------|----------|
| `lysander 帮我做一个数字化交付方案` | 路由到 Butler 团队 |
| `lysander 分析一下这个技术架构` | 召集 Graphify 智囊团 |
| `lysander 研发团队状态如何` | 调取 RD 团队摘要 |
| `lysander 需要沉淀本次项目知识` | 路由到 OBS 知识管理团队 |
| `lysander 帮我写一篇博客` | 路由到 Content_ops 内容运营团队 |

---

## 六、团队一览

| 团队 | 人数 | 核心职责 |
|------|------|----------|
| **Butler** | 7 人 | 项目交付、IoT、PMO、UAT |
| **RD 研发** | 5 人 | 系统开发、架构、DevOps |
| **OBS 知识管理** | 4 人 | 知识沉淀、检索、质量审核 |
| **Graphify 智囊团** | 4 人 | 战略分析、决策支持、趋势洞察 |
| **Content_ops 内容运营** | 4 人 | 博客写作、微信运营、视觉设计 |
| **Stock 股票项目** | 5 人 | 量化策略、交易系统 |

---

## 七、常见问题

**Q: `python` 命令找不到？**  
A: 确认 Python 安装时勾选了"Add to PATH"，或使用 `python3`。

**Q: `claude` 命令找不到？**  
A: 重新打开终端，或执行 `npm install -g @anthropic-ai/claude-code`。

**Q: 想修改某个 AI 专家的能力？**  
A: 编辑 `obs/01-team-knowledge/HR/personnel/{团队}/{专家}.md`，或在 Obsidian 中直接修改。

**Q: 想新增一个 AI 专家？**  
A: 参考 `SETUP.md` → "添加新团队成员" 章节。

---

## 八、技术支持

- 查看架构文档：`docs/ARCHITECTURE.md`
- 查看决策体系：`docs/DECISION_SYSTEM.md`
- 查看 GitHub Issues
