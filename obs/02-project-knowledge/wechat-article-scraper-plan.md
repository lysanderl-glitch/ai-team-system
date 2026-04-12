---
title: 微信公众号文章自动抓取方案
date: 2026-04-12
author: ai_tech_researcher + tech_lead
tags: [微信, 公众号, RSS, 内容抓取, 待执行]
status: archived_pending
assigned_team: rd
follow_up_date: "2026-04-16"
follow_up_action: "RD团队主动询问总裁是否启动执行"
---

# 微信公众号文章自动抓取方案

## 需求

总裁希望每天自动抓取关注的公众号最新文章，完成核心内容提取，推送摘要。

## 问题诊断

WebFetch/WebSearch 无法读取微信公众号文章内容。原因：微信文章是 JavaScript 动态渲染，内容不在原始 HTML 中。WebFetch 只能读静态 HTML，拿到的是空壳。**不是反爬拦截，是技术架构限制。**

## 推荐方案：We-MP-RSS + n8n + Claude

```
We-MP-RSS（Docker部署到服务器）
  → 订阅公众号 → 自动抓取新文章 → 输出RSS/Webhook
  → n8n 监听 → 触发 Claude API → 提取核心内容 → 推送总裁
```

### 方案对比

| 方案 | 原理 | 复杂度 | 推荐 |
|------|------|:------:|:----:|
| We-MP-RSS | 独立服务模拟浏览器抓取→RSS | 中 | ✅ 推荐 |
| WeWe-RSS | 基于微信读书API | 低 | ⚠️ 有配额限制 |
| MCP WeChat Tools | MCP服务端处理 | 低 | ⚠️ 需要MCP配置 |

### 部署需求

- 服务器：43.156.171.107（已有）
- Docker 环境
- SSH 访问权限

### 参考资源

- [We-MP-RSS GitHub](https://github.com/rachelos/we-mp-rss)
- [WeWe-RSS GitHub](https://github.com/cooderl/wewe-rss)
- [WeChat Article Tools MCP](https://mcpmarket.com/server/wechat-article-tools)

## 待总裁确认

1. 部署到哪个服务器
2. 关注哪些公众号
3. 摘要推送方式（Slack/微信/邮件）
