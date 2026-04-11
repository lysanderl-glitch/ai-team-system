---
name: dev-qa
description: |
  自动化测试 + 浏览器实测。QA 完整工作流：找Bug→原子修复→回归测试→验证。
  源自 gstack /qa 方法论，由 qa_engineer 执行。
  Use when testing a feature, running QA on a site, or validating changes work correctly.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
argument-hint: "[URL or feature description]"
---

# /dev-qa — 自动化测试 + 浏览器实测

**执行者：qa_engineer（QA测试工程师）**

---

## Step 1: 测试环境确认

```bash
# 检查测试框架
ls package.json 2>/dev/null && grep -E '"test"' package.json | head -3
ls pytest.ini pyproject.toml 2>/dev/null && echo "Python test config found"
ls Gemfile 2>/dev/null && grep -E 'rspec|minitest' Gemfile | head -3
```

确认项目使用的测试框架和运行命令。

## Step 2: 运行现有测试

运行项目已有的测试套件，建立基线：

```bash
# 根据 Step 1 检测到的框架运行
# npm test / pytest / bundle exec rspec 等
```

记录：通过数 / 失败数 / 跳过数。

## Step 3: 浏览器实测（如提供 URL）

如果 `$ARGUMENTS` 包含 URL：

1. 使用 Playwright 打开目标页面
2. 按用户流程逐步测试：
   - 页面加载 → 核心交互 → 表单提交 → 导航跳转
3. 检查：
   - Console 错误
   - 网络请求失败
   - UI 布局异常
   - 响应式适配（桌面/平板/手机）
4. 截图记录关键页面状态

## Step 4: Bug 修复闭环

对每个发现的 Bug：

### 4a: 定位
- 确定 Bug 的根因（不猜测，追踪数据流）

### 4b: 原子修复
- 每个 Bug 修复为独立的 git commit
- commit message 格式：`fix: [简述问题] (file:line)`

### 4c: 生成回归测试
- 为每个修复自动创建对应的测试用例
- 测试必须：在修复前失败，修复后通过

### 4d: 验证
- 重新运行测试，确认修复有效且无回归

## Step 5: 测试覆盖分析

```bash
# 检查覆盖率（如项目配置了覆盖率工具）
# npm run test:coverage / pytest --cov 等
```

报告当前覆盖率，标注新代码的覆盖情况。

## Step 6: 输出 QA 报告

```
**QA 报告**

**测试基线：** X 通过 / Y 失败 / Z 跳过
**发现 Bug：** N 个
**已修复：** M 个（每个附 commit hash + 回归测试）
**测试变化：** 原 X 个 → 现 X+M 个（新增 M 个回归测试）
**覆盖率：** XX%

**详细发现：**
1. [Bug描述] → [修复方式] → [回归测试文件]
```
