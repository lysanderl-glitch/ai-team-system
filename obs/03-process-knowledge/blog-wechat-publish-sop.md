---
title: 博客+微信发布 SOP
category: 流程知识
tags: [SOP, 博客, 微信, n8n, 发布]
created: 2026-04-10
author: Lysander
version: 0.4
type: SOP
---

# 博客 + 微信发布 SOP v0.4

## 架构总览

```
本地 obsidian-knowledge
  └── 📝-Articles/ 写文章
        ↓ obsidian-git 每5分钟自动 push
GitHub: lysanderl-glitch/obsidian-knowledge
        ↓ 服务器 cron 每小时 git pull
服务器 /home/ubuntu/knowledge-base/📝-Articles/
        ↓ 22:30 迪拜时间 harness-daily-publish.sh
Astro 构建 → lysander.bond/blog/
        ↓ 22:45 迪拜时间 n8n workflow LGkeWFUdYx5X7vgP
微信公众号草稿箱
```

**当前状态**：全链路通畅 ✅（最新文章 2026-04-09 已在线）

---

## 创建新文章

### 文章格式（.astro.html 或 .md）

放入 `obsidian-knowledge/📝-Articles/` 目录。

**METADATA 格式**（.astro.html 文章必须包含）：

```html
<!-- METADATA:{"title":"文章标题","date":"2026-04-10","tags":["AI","标签2"],"description":"文章描述"} -->
```

注意：标题中如有引号必须转义为 `\"`

### 文章发布时间线

| 动作 | 触发方式 | 预计延迟 |
|------|----------|----------|
| 本地写完文章 | 手动保存 | 立即 |
| 推送到 GitHub | obsidian-git 自动 | ≤5分钟 |
| 服务器拉取 | cron 每小时 | ≤60分钟 |
| 博客发布 | cron 22:30 迪拜 | 当日 22:30 |
| 微信草稿 | n8n 22:45 迪拜 | 当日 22:45 |

---

## 手动触发（跳过等待）

```bash
# 触发 n8n 微信草稿发布
curl -X POST https://n8n.lysander.bond/webhook/wechat-blog-draft
```

服务器端手动触发博客构建：需 SSH 到服务器执行 `bash /home/ubuntu/scripts/harness-daily-publish.sh`（当前无 SSH 访问，等待 cron 即可）

---

## 验证清单

- [ ] GitHub 上 obsidian-knowledge 有最新文章：https://github.com/lysanderl-glitch/obsidian-knowledge
- [ ] 博客页面已更新：https://lysander.bond/blog/
- [ ] 微信公众号草稿箱有新草稿：https://mp.weixin.qq.com/draft

---

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 博客未更新 | 服务器尚未拉取 / cron 未触发 | 等下一个小时周期 |
| 微信草稿未出现 | n8n workflow 未执行 | 检查 n8n.lysander.bond 执行历史 |
| JSON 解析失败 | METADATA 中含中文引号 | 改用 `\"` 转义 |
| 文章重复发布 | 同名文件改过 METADATA | harness-daily-publish.sh 会去重 |

---

## 相关配置

- n8n workflow ID: `LGkeWFUdYx5X7vgP`
- webhook: `https://n8n.lysander.bond/webhook/wechat-blog-draft`
- 配置文件: `agent-butler/config/n8n_integration.yaml`
- 服务器发布脚本: `/home/ubuntu/scripts/harness-daily-publish.sh`
