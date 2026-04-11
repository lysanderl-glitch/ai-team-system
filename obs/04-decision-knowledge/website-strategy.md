---
title: lysander.bond 网站战略重构方案
date: 2026-04-11
author: Graphify 智囊团 + Growth 团队 + RD 团队联合制定
tags: [网站, 战略, Synapse, 商业化, 内容运营]
decision_level: L3
status: 待执行
---

# lysander.bond 网站战略重构方案

## 一、战略定位

### 从"个人博客"到"商业平台"

| 维度 | 现状 | 目标 |
|------|------|------|
| 定位 | Lysander 的个人 AI 学习笔记 | Synapse by Janus Digital — AI Agent 运营体系 |
| 受众 | 同好/粉丝 | 企业管理者/技术负责人/AI架构师 |
| 目的 | 记录分享 | 获客+引流+品牌+内容资产 |
| 调性 | 随笔风格 | 专业+实践+有温度 |
| 变现 | 无 | 咨询获客入口+培训报名+品牌建设 |

### 网站使命

```
lysander.bond = Synapse 的对外窗口

它要完成三件事：
1. 让潜在客户了解 Synapse 是什么、能解决什么问题
2. 通过专业内容建立行业影响力（Harness Engineering 先行者）
3. 将流量转化为咨询预约和培训报名
```

## 二、信息架构（栏目结构）

```
lysander.bond/
├── / (首页)
│   ├── Hero：核心价值主张
│   │   "用 Harness Engineering 构建可靠的 AI Agent 团队"
│   ├── 三大服务卡片
│   ├── 精选案例/数据
│   ├── 最新博客文章
│   └── CTA：预约咨询 / 了解培训
│
├── /about
│   ├── Janus Digital 公司介绍
│   ├── Synapse 体系概述（五层架构图）
│   ├── 刘子杨个人简介（创始人/总裁）
│   └── 联系方式
│
├── /services
│   ├── Synapse Assessment（$5K-$10K，2天诊断）
│   ├── Synapse Implementation（$30K-$80K，2-4周落地）
│   ├── Janus 建筑AI增值服务
│   └── CTA：预约咨询
│
├── /training
│   ├── Synapse Practitioner (SCP) 课程介绍
│   ├── 课程大纲概要
│   ├── 认证说明
│   ├── 定价
│   └── CTA：报名 / 咨询
│
├── /blog (保留并升级)
│   ├── [方法论] — Harness Engineering / Context Engineering / Synapse
│   ├── [技术指南] — Claude Code / MCP / n8n / Obsidian
│   ├── [案例] — 实践案例 / 客户故事
│   └── [行业洞察] — AI趋势 / 市场分析
│
├── /intelligence (新增)
│   ├── 最新一期 AI 情报日报（公开版）
│   ├── 历史情报归档
│   └── 订阅入口（引流到咨询）
│
└── 404 / 通用页脚
    ├── Janus Digital 品牌
    ├── 社交媒体链接
    ├── 联系邮箱
    └── Synapse 简述
```

## 三、内容策略

### 现有内容处置

| 内容 | 决定 | 理由 |
|------|------|------|
| 9篇技术博客 | **保留** | 高质量技术内容，加标签重分类 |
| 4篇日记 | **删除** | 生活日记与商业定位不符 |
| /daily 栏目 | **删除** | 用 /intelligence 替代 |

### 现有博客重分类

| 文章 | 新分类 |
|------|--------|
| Harness Engineering 入门 | 方法论 |
| Claude Code 知识提取实战 | 技术指南 |
| Claude Code 错误自愈系统 | 技术指南 |
| AI团队协作Obsidian自动化 | 案例 |
| AI决策系统自动化笔记 | 方法论 |
| Claude Code 微信接入 | 技术指南 |
| Claude Code MCP 配置指南 | 技术指南 |
| n8n 节点执行策略 | 技术指南 |
| Asana + Slack + n8n 自动化 | 技术指南 |

### 待发布的新内容

| 内容 | 分类 | 状态 |
|------|------|:----:|
| Harness Engineering 实战手记 | 方法论 | ✅ 已完成 |
| Synapse 咨询服务 One-Pager | 服务页面 | ✅ 已完成 |
| SCP 培训课程大纲 | 培训页面 | ✅ 已完成 |
| 每日 AI 情报日报 | 情报 | ✅ 每日自动生成 |
| Synapse 方法论完整文档 | 方法论 | ✅ 已有 |

### 内容发布节奏

```
每日：AI 情报日报（自动发布到 /intelligence）
每周：1篇深度博客（方法论 或 案例 或 技术指南）
每月：1篇行业洞察报告
```

## 四、品牌视觉规范

### 色彩方案

延续 Janus Digital 品牌色系（已从 janusd.com Logo SVG 提取）：

| 色彩 | Hex | 用途 |
|------|-----|------|
| Gold | #FCAD2A | 品牌主色、CTA按钮、强调 |
| Deep Blue | #013A7D | 标题、导航、专业感 |
| Cyan | #028CDC | 链接、辅助强调、科技感 |
| Dark BG | #0A1628 | 页头/页脚深色背景 |
| White | #FFFFFF | 主内容区背景 |
| Light Gray | #F7F8FA | 卡片/分区背景 |

### 字体

- 英文：Inter（已在报告模板中使用）
- 中文：PingFang SC / Microsoft YaHei

### 设计原则

- 极简、专业、大量留白（参考 janusd.com 风格）
- 深色页头/页脚 + 白色内容区
- 卡片式布局（服务/博客/案例统一用卡片）
- 响应式（移动端优先）

## 五、技术方案

### 技术栈

```
保持不变：
├── Astro（静态站点生成器）
├── Tailwind CSS（样式框架）
├── 服务器：43.156.171.107
└── 部署：定时构建（已有harness-daily-publish.sh）

需要修改：
├── 页面结构：增加 /services /training /intelligence
├── 导航组件：更新菜单项
├── 品牌色：替换为 Janus 品牌色
├── 页头/页脚：更新为 Synapse + Janus Digital 品牌
├── 博客分类：增加 tag 筛选功能
└── 情报页面：对接 daily-intelligence HTML 输出
```

### 部署流程

```
本地编辑 → git push → 服务器 git pull → Astro build → 静态文件部署
情报日报 → 远程Agent生成 → git push → 同步到 /intelligence
```

## 六、SEO 策略

### 核心关键词

| 关键词 | 搜索意图 | 目标页面 |
|--------|----------|----------|
| Harness Engineering | 学习方法论 | /blog 方法论文章 |
| AI Agent 团队管理 | 寻找解决方案 | /services |
| Multi-Agent 框架 | 技术选型 | /blog 技术指南 |
| AI 咨询服务 | 购买意向 | /services |
| Synapse AI | 品牌搜索 | / 首页 |

### 技术 SEO

- 每个页面添加 meta title + description + og:image
- 博客文章添加 schema.org 结构化数据
- sitemap.xml 自动生成
- robots.txt 配置

## 七、执行计划

### Phase 1：框架重构（需SSH访问后执行）

1. 备份现有网站
2. 更新 Astro 项目结构（增加新页面）
3. 替换品牌色和页头/页脚
4. 创建 /services /training /intelligence 页面
5. 更新 /about 为公司+Synapse介绍
6. 删除 /daily 栏目
7. 博客重分类（加标签）
8. 部署并验证

### Phase 2：内容填充

1. 发布 Harness Engineering 实战博客
2. 上线服务页面内容
3. 上线培训课程信息
4. 配置情报日报自动发布到 /intelligence

### Phase 3：持续运营

1. 每日情报自动发布
2. 每周博客更新
3. SEO 监控和优化
4. 转化率追踪
