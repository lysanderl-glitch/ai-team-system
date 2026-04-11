---
title: lysander.bond 网站重构技术执行方案
date: 2026-04-11
author: Tech Lead + Frontend Dev + DevOps + 智囊团联合评审
tags: [网站, 技术方案, Astro, 部署]
decision_level: L3
status: 评审通过，待总裁审批执行
---

# 网站重构技术执行方案

## 评审结果

**均分 5.0/5.0 — 全票通过**

参与评审：strategist / decision_advisor / trend_watcher / frontend_dev / gtm_strategist

## 执行清单（8项变更）

### 变更 1：品牌色替换
**文件**：`src/styles/global.css`
**改动**：5个CSS变量值替换

```css
/* 旧 → 新 */
--color-primary:   #0ea5e9 → #028CDC  /* Janus Cyan */
--color-secondary: #8b5cf6 → #013A7D  /* Janus Deep Blue */
--color-accent:    #06b6d4 → #FCAD2A  /* Janus Gold */
--color-dark:      #0f172a → #0A1628  /* Janus Dark */
--color-light:     #f8fafc → #F7F8FA  /* Light Gray */
```

背景渐变也更新为 Janus 深蓝色调。

### 变更 2：全局布局更新
**文件**：`src/layouts/Layout.astro`
**改动**：
- 导航品牌文字："Lysander" → "Synapse"
- 导航菜单：博客/关于 → 服务/培训/博客/情报/关于
- 页脚：更新为 Janus Digital + Synapse 品牌
- SEO meta description 更新

### 变更 3：首页重写
**文件**：`src/pages/index.astro`
**改动**：完全重写
- Hero：价值主张 + CTA（预约咨询）
- 三大服务卡片
- 核心数据（10团队/49Agent/93.8分）
- 精选博客
- 底部CTA

### 变更 4：About页重写
**文件**：`src/pages/about.astro`
**改动**：从个人简介改为三段结构
- Janus Digital 公司介绍
- Synapse 体系概述（五层架构）
- 刘子杨个人简介（创始人/总裁）

### 变更 5：新增服务页
**文件**：`src/pages/services.astro`（新建）
**内容**：Assessment + Implementation + 建筑AI增值

### 变更 6：新增培训页
**文件**：`src/pages/training.astro`（新建）
**内容**：SCP课程信息 + 大纲 + 定价

### 变更 7：新增情报页
**文件**：`src/pages/intelligence.astro`（新建）
**内容**：最新情报日报展示 + 历史归档

### 变更 8：删除日记栏目
**文件**：删除 `src/pages/daily.astro` + `src/pages/daily/[date].astro`

### 不变更

- 现有11篇博客文章 → 保留不动
- package.json → 不增加新依赖
- astro.config.mjs → 不改动
- .github/workflows/deploy.yml → 不改动（CI/CD保持）
- public/ 静态资源 → 保留

## 部署流程

```
本地 clone → 执行8项变更 → git push → GitHub Actions 自动构建 → SSH 部署到服务器
```

push 到 main 即自动上线，无需手动操作。

## 风险控制

- 先 clone 到本地 worktree，确认无误后再 push
- 现有博客不触碰，零破坏风险
- 品牌色仅改CSS变量，全站自动生效
- 删除/daily 是最低风险操作（仅4篇生活日记）
