---
name: daily-blog
description: |
  每日复盘博客生成。从当日工作中提炼对外博客文章，经 Content_ops 加工后生成精美 HTML。
  自动执行链：复盘数据收集 → 博客文章撰写 → HTML 生成 → git push。
  Use at end of day to generate a blog post from today's work, or by scheduled agent.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
argument-hint: "[topic focus or auto]"
---

# /daily-blog — 每日复盘博客生成

**执行团队：Content_ops（content_strategist + content_creator + publishing_ops）**

将当日工作成果转化为对外博客文章，沉淀知识的同时丰富官网内容。

---

## Step 1: 收集今日素材

**content_strategist 执行：**

1. 读取今日 git 活动：

```bash
git log --oneline --since="12 hours ago" 2>/dev/null | head -20
```

```bash
git diff --stat HEAD~5 2>/dev/null | tail -10
```

2. 检查是否有今日复盘报告：

```bash
ls obs/06-daily-reports/*$(date +%Y-%m-%d)* 2>/dev/null
```

3. 检查今日情报日报（如有）：

```bash
ls obs/generated-articles/*$(date +%Y-%m-%d)* 2>/dev/null
```

4. 汇总当日工作亮点、关键决策、新知识。

## Step 2: 选题与提炼

**content_strategist 执行：**

从原始素材中提炼博客主题。**选题原则：**

- 优先选择**有行业传播价值**的主题（技术洞察、方法论、工具评测）
- 避免纯内部事务（团队派单、卡片升级等细节）
- 每篇文章聚焦**一个核心观点**，不贪多
- 标题要有吸引力，面向技术决策者

**选题模板：**
- "我们从 [X] 学到了什么" — 经验提炼型
- "[X] vs [Y]：深度对比" — 评测对比型
- "如何用 [X] 实现 [Y]" — 实操指南型
- "[X] 的 N 个关键洞察" — 洞察清单型

## Step 3: 撰写博客文章

**content_creator 执行：**

使用模板文件 `.claude/skills/daily-blog/blog-template.md` 撰写文章。

**写作规范：**
- 开头：一句话核心观点（hook）
- 正文：论点 → 论据 → 实践建议，每段不超过3-4行
- 结尾：一句话总结 + 行动号召
- 语气：专业但不晦涩，有洞察力，有观点
- 长度：800-1500 字
- 必须包含：至少一个数据/事实支撑、至少一个代码或架构示例

**严禁：**
- 泄露内部敏感信息（凭证、客户名、合同金额）
- 过度 AI 味道（"让我们深入探讨"、"在当今快速发展的"）
- 空洞总结（"总之AI很重要"）

将 Markdown 文件写入：`obs/05-industry-knowledge/blog/YYYY-MM-DD-title.md`

## Step 4: 生成 HTML

**publishing_ops 执行：**

```bash
cd /c/Users/lysanderl_janusd/Claude\ Code/ai-team-system
PYTHONUTF8=1 python scripts/generate-article.py obs/05-industry-knowledge/blog/YYYY-MM-DD-title.md
```

验证生成的 HTML 文件存在：

```bash
ls obs/generated-articles/*$(date +%Y-%m-%d)* 2>/dev/null
```

## Step 5: 产出确认

输出摘要：

```
**Daily Blog Generated**

Title: [文章标题]
Topic: [主题分类]
Words: [字数]
Markdown: obs/05-industry-knowledge/blog/YYYY-MM-DD-title.md
HTML: obs/generated-articles/YYYY-MM-DD-title.html
```
