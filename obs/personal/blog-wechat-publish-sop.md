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

## 架构总览（2026-04-12 更新）

```
本地 lysander-bond 项目
  └── src/pages/blog/{slug}.astro   写文章（.astro 格式）
  └── src/pages/blog/index.astro    更新文章列表（posts 数组）
        ↓ git push origin main
GitHub: lysanderl-glitch/lysander-bond
        ↓ GitHub Actions 自动触发
CI/CD: npm ci → npm run build → SSH deploy
        ↓
lysander.bond/blog/{slug} 上线
```

**网站项目目录**：`C:\Users\lysanderl_janusd\Claude Code\lysander-bond`
**技术栈**：Astro + Tailwind CSS
**CI/CD**：GitHub Actions → SSH deploy to 43.156.171.107
**当前状态**：全链路通畅 ✅

> **注意**：旧管线（obsidian-knowledge → 服务器 cron pull）已弃用。
> 所有博客发布通过 lysander-bond 仓库的 CI/CD 管线。

---

## 创建新文章

### Step 1: 创建 .astro 文件

在 `lysander-bond/src/pages/blog/` 下创建 `{slug}.astro`：

```astro
---
import Layout from '../../layouts/Layout.astro';
---

<Layout darkContent={true} title='文章标题 - Lysander' description='文章描述'>
  <article class="max-w-4xl mx-auto px-6 py-16">
    <header class="mb-12">
      <div class="flex items-center gap-3 mb-4">
        <time class="text-white/40 text-sm">YYYY-MM-DD</time>
        <div class="flex gap-2">
          <span class="px-2 py-0.5 bg-sky-500/20 text-sky-400 rounded text-xs">标签</span>
        </div>
      </div>
      <h1 class="text-4xl font-bold text-white">文章标题</h1>
    </header>
    <div class="prose prose-invert max-w-none space-y-8 text-white/80 leading-relaxed">
      <!-- 正文内容 -->
    </div>
    <footer class="mt-16 pt-8 border-t border-white/10">
      <a href="/blog" class="text-sky-400 hover:text-sky-300">&larr; 返回博客</a>
    </footer>
  </article>
</Layout>
```

### Step 2: 更新列表页

在 `src/pages/blog/index.astro` 的 `posts` 数组**头部**新增：

```javascript
{
  slug: '{slug}',
  title: '{标题}',
  date: '{YYYY-MM-DD}',
  description: '{描述}',
  tags: ['{标签1}', '{标签2}']
}
```

### Step 3: 推送发布

```bash
cd "C:\Users\lysanderl_janusd\Claude Code\lysander-bond"
git add src/pages/blog/{slug}.astro src/pages/blog/index.astro
git commit -m "blog: {标题}"
git push origin main
```

GitHub Actions 自动构建部署，通常 1-2 分钟上线。

### 文章发布时间线

| 动作 | 触发方式 | 预计延迟 |
|------|----------|----------|
| 创建 .astro 文件 + 更新 index | 手动或 Synapse `/daily-blog` | 立即 |
| push 到 GitHub | git push | 立即 |
| CI/CD build + deploy | GitHub Actions 自动 | 1-2 分钟 |
| 文章上线 | 自动 | push 后约 2 分钟 |

---

## Synapse 集成

Synapse 的 `/daily-blog` Skill 产出博客内容后，publishing_ops 负责：
1. Markdown 存入 `ai-team-system/obs/05-industry-knowledge/blog/`（知识沉淀）
2. 转为 .astro 格式写入 `lysander-bond/src/pages/blog/`（网站发布）
3. 更新 index.astro 列表
4. git push 触发 CI/CD

---

## 验证清单

- [ ] 博客页面已更新：https://lysander.bond/blog/
- [ ] 文章可访问：https://lysander.bond/blog/{slug}
- [ ] GitHub Actions 构建成功：https://github.com/lysanderl-glitch/lysander-bond/actions

---

## 微信发布（可选）

```bash
curl -X POST https://n8n.lysander.bond/webhook/wechat-blog-draft
```

- n8n workflow ID: `LGkeWFUdYx5X7vgP`

---

## 相关配置

- 网站仓库: `lysanderl-glitch/lysander-bond`
- CI/CD: `.github/workflows/deploy.yml`
- Synapse Skill: `ai-team-system/.claude/skills/daily-blog/SKILL.md`
- n8n 配置: `ai-team-system/agent-butler/config/n8n_integration.yaml`
