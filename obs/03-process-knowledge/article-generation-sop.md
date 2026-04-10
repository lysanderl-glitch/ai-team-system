---
title: 文章 HTML 化生成 SOP
category: 流程知识
tags: [SOP, HTML生成, 内容沉淀, 内容团队]
created: 2026-04-10
author: Lysander
version: 1.0
type: SOP
---

# 文章 HTML 化生成 SOP v1.0

> 将工作会话、项目经验、知识沉淀转化为精美 HTML 文章，本地归档，内部分发。  
> 零服务器依赖，即写即出，秒级生成。

---

## 架构

```
Obsidian / Claude Code 产生知识
  └── 内容团队整理为 Markdown（含 front-matter）
        ↓ 一条命令
python scripts/generate-article.py obs/path/to/article.md
        ↓
obs/generated-articles/YYYY-MM-DD-title.html
  └── 自包含 HTML，科技蓝主题，可直接发送/打印/归档
        ↓ obsidian-git 自动推送
GitHub 长期归档
```

---

## 第一步：写文章

在 Obsidian 或通过 Claude Code 创建 Markdown 文件，存放在 `obs/` 任意目录。

**必须包含 front-matter：**

```yaml
---
title: 文章标题
date: 2026-04-10
author: Lysander
tags: [AI, 技术分享]
description: 一句话摘要
---
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | ✅ | 影响输出文件名和文章头部 |
| `date` | ✅ | `YYYY-MM-DD` 格式，影响文件名排序 |
| `author` | 建议 | 显示在文章 meta 区 |
| `tags` | 建议 | `[标签1, 标签2]`，生成蓝色标签 |
| `description` | 可选 | HTML `<meta>` 描述 |

---

## 第二步：生成 HTML

在 `ai-team-system` 目录下运行：

```bash
# 基本生成
python scripts/generate-article.py obs/path/to/article.md

# 生成并立即在浏览器预览
python scripts/generate-article.py obs/path/to/article.md --open

# 指定输出目录（如共享文件夹）
python scripts/generate-article.py obs/path/to/article.md --output D:/shared/
```

成功输出示例：

```
✅ Generated : C:\...\obs\generated-articles\2026-04-10-ai-team-intro.html
   Title    : AI 团队协作入门
   Size     : 42 KB
```

---

## 第三步：检查

用浏览器打开生成的 HTML，确认：

- [ ] 标题、日期、标签显示正确
- [ ] H2 标题有左侧蓝色竖线
- [ ] 代码块为深色背景，语法高亮正常
- [ ] 表格有蓝色表头

---

## 第四步：分发与归档

| 场景 | 操作 |
|------|------|
| 发给同事 | 直接发送 `.html` 文件，对方双击即可在浏览器查看 |
| 打印存档 | 浏览器 → 打印 → 另存 PDF |
| GitHub 归档 | obsidian-git 自动推送，5 分钟内完成 |
| 共享文件夹 | `--output D:/team-share/` 直接生成到共享目录 |

---

## 适用内容类型

| 内容 | 说明 |
|------|------|
| 工作会话总结 | Claude Code 会话结束后，提炼为文章 |
| 项目复盘报告 | 从 `02-project-knowledge/` 提炼 |
| 技术方案文档 | RD 团队输出的技术分析 |
| 智囊团分析报告 | Graphify 分析结果文章化 |
| 决策记录 | 重要决策背景 + 结论 |
| SOP 可读版 | 将 SOP.md 生成 HTML 方便阅读和打印 |

---

## 常见问题

| 问题 | 解决 |
|------|------|
| `ModuleNotFoundError: markdown` | `pip install markdown pygments` |
| 代码块无高亮 | `pip install pygments`（可选增强） |
| front-matter 未识别 | 确认 `---` 在文件第一行，无多余空格 |

---

## 相关

- `scripts/generate-article.py` — 生成脚本
- `obs/generated-articles/` — 输出目录
- [[daily-workflow-sop]]
