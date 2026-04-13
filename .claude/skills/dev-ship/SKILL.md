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

## Step 4: 推送并创建 PR（前置条件：Step 2 测试通过）

**前置检查：仅当 Step 2 测试通过（或仅主分支已有的失败）时才继续。如果有本分支引入的测试失败，禁止推送。**

**GATE：执行 `git push` 前，先运行 `git diff --stat origin/main` 确认有变更要推送。如果 diff 为空，停止并提示"无变更可推送"。**

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

---

## 测试场景（强制，交付前必须通过）

### test_scenarios

#### Golden Path: 完整发布流程（同步 + 测试 + 推送 + PR）

- **场景名称**：功能分支代码就绪，执行完整一键发布工作流
- **输入**：`/dev-ship feature/user-auth`
- **前置条件**：
  - 当前处于功能分支（非 main）
  - 远程 `origin/main` 可达
  - 项目有可运行的测试套件
  - `gh` CLI 已配置并可用
  - `git diff --stat origin/main` 有变更输出
- **预期结果**：
  - [ ] Step 0 检查 .dev-artifacts/ 下是否有 review/qa 产出，输出对应状态
  - [ ] Step 1 执行 `git fetch origin main` 并 merge，无冲突时正常继续
  - [ ] Step 2 运行项目测试命令，记录通过/失败/跳过数
  - [ ] Step 3 运行覆盖率检查并报告
  - [ ] Step 4 前置检查：确认 Step 2 测试通过后才执行 push
  - [ ] Step 4 GATE 检查：`git diff --stat origin/main` 确认有变更
  - [ ] Step 4 执行 `git push origin HEAD -u`
  - [ ] Step 4 使用 `gh pr create` 创建 PR（标题 < 70 字符，Body 含变更摘要 + 测试状态）
  - [ ] Step 5 检查部署配置并执行对应验证（如有）
  - [ ] Step 6 输出完整发布报告，格式包含：分支 / 测试 / 覆盖率 / PR / 审查状态 / 部署
  - [ ] 工具调用链：`Bash(ls .dev-artifacts) -> Bash(git fetch + merge) -> Bash(测试) -> Bash(覆盖率) -> Bash(git diff --stat) -> Bash(git push) -> Bash(gh pr create)`

#### Edge Case 1: 测试失败时的中止流程

- **场景名称**：本分支引入的测试失败导致发布中止
- **输入**：`/dev-ship feature/broken-feature`
- **前置条件**：
  - 功能分支有代码变更
  - 项目测试套件运行后有本分支引入的失败用例
- **预期结果**：
  - [ ] Step 2 运行测试发现失败
  - [ ] 区分"本分支引入的失败"和"主分支已有的失败"
  - [ ] 本分支引入的失败 → 停止发布流程，不执行 Step 4 push
  - [ ] 输出明确提示："测试失败，必须修复后再发布"，列出失败用例
  - [ ] 不执行 git push，不创建 PR

#### Edge Case 2: 合并冲突时的处理

- **场景名称**：与主分支合并产生冲突
- **输入**：`/dev-ship feature/conflicting-changes`
- **前置条件**：
  - 功能分支与 origin/main 在同一文件有冲突修改
- **预期结果**：
  - [ ] Step 1 `git merge origin/main` 产生冲突
  - [ ] 简单冲突（VERSION/CHANGELOG）尝试自动解决
  - [ ] 复杂冲突停止并展示冲突文件列表
  - [ ] 不强行继续后续步骤
