---
name: dev-ship
description: |
  一键发布工作流。同步主分支→跑测试→审查→推送→开PR→部署→验证。
  源自 gstack /ship + /land-and-deploy 方法论，由 devops_engineer 主导。
  Use when code is ready to ship, create a PR, deploy, or push changes.
  Proactively suggest when the user says code is ready or wants to deploy.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
argument-hint: "[branch or PR description]"
---

# /dev-ship — 一键发布工作流

**执行者：devops_engineer（主导）+ qa_engineer（测试门禁）**

---

## Step 0: 发布前审查仪表盘

检查是否已运行前置审查：

```bash
# 检查是否有 dev-review 产出
ls .dev-artifacts/review-*.md 2>/dev/null
# 检查是否有 dev-qa 产出
ls .dev-artifacts/qa-*.md 2>/dev/null
```

- /dev-review 已运行 → 记录 ✅
- /dev-review 未运行 → 提示："建议先运行 /dev-review，但不阻塞发布"
- /dev-qa 已运行 → 记录 ✅

## Step 1: 同步主分支

```bash
git fetch origin main --quiet
git merge origin/main --no-edit
```

如有合并冲突：简单冲突（VERSION/CHANGELOG）尝试自动解决，复杂冲突停止并展示。

## Step 2: 运行测试

```bash
# 检测并运行项目测试命令
```

根据项目配置运行全量测试。

**测试失败处理：**
- 本分支引入的失败 → 停止，必须修复
- 主分支已有的失败 → 记录但不阻塞

## Step 3: 覆盖率审计

```bash
# 运行覆盖率检查
```

报告整体覆盖率和本次变更的覆盖情况。

## Step 4: 推送并创建 PR

```bash
git push origin HEAD -u
```

使用 `gh pr create` 创建 PR：
- 标题：简洁描述变更（< 70字符）
- Body：变更摘要 + 测试状态 + 审查状态

## Step 5: 部署验证（如配置了部署）

检查项目是否有部署配置：

```bash
ls .github/workflows/ 2>/dev/null | grep -iE 'deploy|release'
ls vercel.json netlify.toml 2>/dev/null
```

如有自动部署：
1. 等待 CI 完成
2. 验证部署页面可访问
3. 快速冒烟测试核心功能

## Step 6: 输出发布报告

```
**发布报告**

**分支：** feature/xxx → main
**测试：** X 通过 / Y 失败
**覆盖率：** XX%
**PR：** #NNN (URL)
**审查状态：** /dev-review ✅/未运行
**部署：** ✅ 已部署 / ⏳ 等待 CI / ❌ 无自动部署

**变更摘要：**
- [文件变更统计]
```
