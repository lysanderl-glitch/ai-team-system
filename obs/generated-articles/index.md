---
title: 生成文章归档
category: 内容归档
tags: [HTML文章, 归档]
type: 索引
---

# 生成文章归档

此目录存放由 `scripts/generate-article.py` 生成的本地 HTML 文章。

## 生成命令

```bash
python scripts/generate-article.py obs/path/to/article.md
python scripts/generate-article.py obs/path/to/article.md --open
```

## 文件规范

命名格式：`YYYY-MM-DD-{title-slug}.html`

## 使用方式

直接双击 `.html` 文件，在浏览器中打开阅读。可打印为 PDF 存档或直接发送给同事。
