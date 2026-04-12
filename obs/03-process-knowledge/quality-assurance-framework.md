# Synapse 全交付物质量保障框架（Quality Assurance Framework）

> **文档状态**：技术方案（Tech Plan）
> **版本**：v1.0
> **日期**：2026-04-12
> **作者**：tech_lead + 智囊团联合评审
> **决策级别**：L3（Lysander 审批）

---

## 1. 问题定义

### 1.1 当前质量缺口

Synapse 体系当前的质量保障围绕**静态正确性**设计：代码审查（/dev-review）检查语法和逻辑，QA 门禁（/qa-gate）做评分式审查。但实际使用中仍频繁出现 bug，根因是缺少**动态功能验证**——交付物"看起来对"但"跑起来不对"。

具体问题模式：

| 缺口类型 | 典型案例 | 影响范围 |
|----------|---------|---------|
| **Skill 功能断裂** | /capture 写入路径错误，GATE 门禁缺失导致条件提交失败 | 19个 Skill，总裁直接调用 |
| **配置加载失效** | CLAUDE.md 约束项语法正确但运行时未生效 | 系统级，影响所有会话 |
| **YAML 引用悬空** | organization.yaml 引用了已删除的 specialist_id | 15+ 配置文件 |
| **脚本运行时失败** | Python 脚本 import 正确但运行时环境变量缺失 | 定时任务、手动脚本 |
| **HTML 渲染异常** | 报告模板正确但数据为空/过期 | 总裁浏览器阅读 |
| **自动化静默失败** | n8n 编排 webhook 超时无告警，任务链中断 | 后台无人值守流程 |

### 1.2 根因分析

```
当前质量流程：

  代码变更 → /dev-review（静态审查）→ /qa-gate（评分审查）→ 交付

  缺失的环节：
  ├── 无冒烟测试（Smoke Test）      — 从不实际运行交付物
  ├── 无端到端验证（E2E）           — 从不模拟真实用户路径
  ├── 无健康监控（Health Check）     — 后台任务失败无感知
  └── 无回归检测（Regression）       — 变更 A 导致 B 断裂无感知
```

核心矛盾：**质量体系验证的是"代码写对了吗"，而非"功能能用吗"**。

### 1.3 影响评估

Synapse 共有 **6 类交付物**，覆盖所有业务输出：

| 序号 | 交付物类型 | 数量 | 消费者 | 当前验证 | 缺失验证 |
|------|-----------|------|--------|---------|---------|
| 1 | Skill 定义 | 19个 | 总裁直接调用 | 静态语法 | 功能冒烟、E2E |
| 2 | Harness 配置 | 1 (CLAUDE.md) | 系统自动加载 | 人工审查 | 约束生效验证 |
| 3 | YAML 配置 | 15+ 文件 | 系统自动解析 | YAML 语法 | 引用有效性、逻辑校验 |
| 4 | Python 脚本 | 10+ 文件 | 定时/手动执行 | import 检查 | dry-run、单元测试 |
| 5 | HTML 报告 | 动态生成 | 总裁浏览器阅读 | 无 | 渲染检查、数据新鲜度 |
| 6 | n8n 自动化 | 5+ 编排 | 后台无人值守 | 无 | 心跳监控、失败告警 |

---

## 2. 设计目标

### 2.1 核心目标

**从"代码正确"升级到"功能完整"**——所有交付物在到达总裁之前，必须经过动态验证，证明"能用"而非仅"没有语法错"。

### 2.2 三层递进防御

```
                    ┌─────────────────────────────┐
                    │    第三层：自动化验证管线      │
                    │  E2E 框架 + 健康监控 + 回归   │
                    │  （持续运行，后台自动化）       │
                    ├─────────────────────────────┤
                    │    第二层：交付前冒烟测试      │
                    │  按类型分策略执行动态验证       │
                    │  （每次交付前，阻塞式门禁）     │
                    ├─────────────────────────────┤
                    │    第一层：内嵌测试定义        │
                    │  所有交付物内置验收标准        │
                    │  （设计阶段，定义即文档）       │
                    └─────────────────────────────┘
```

| 层级 | 职责 | 运行时机 | 阻塞性 |
|------|------|---------|--------|
| **L1 内嵌测试定义** | 每个交付物自带 test_scenarios / 验收标准 | 设计阶段 | 无（定义层） |
| **L2 交付前冒烟测试** | 按交付物类型执行对应的动态验证 | 交付前（执行链 ③ 环节） | 阻塞交付 |
| **L3 自动化验证管线** | E2E 框架 + 后台健康监控 + 变更触发回归 | 持续运行 / 变更触发 | 阻塞部署（gate 级）|

### 2.3 设计原则

1. **Test Definition as Code**：测试场景是交付物的一部分，不是事后补充
2. **类型感知策略**：6 类交付物各有专属验证策略，不用一套方案硬套
3. **渐进式采纳**：从 Skill（最高优先级）开始，逐步覆盖全部 6 类
4. **参考 gstack 成熟实践**：session-runner / llm-judge / touchfiles 三件套是核心参考
5. **成本可控**：gate 级测试控制在 $0.50/次以内，periodic 级控制在 $5/次以内

---

## 3. 架构设计

### 3.1 统一质量框架整体架构

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    Synapse Quality Assurance Framework                    │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                     入口：交付物变更事件                             │  │
│  │  git commit / Skill edit / YAML change / Script update / HTML gen  │  │
│  └───────────────────────────┬────────────────────────────────────────┘  │
│                              │                                           │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                  路由层：交付物类型识别                               │  │
│  │                                                                    │  │
│  │   文件路径 → 类型映射：                                             │  │
│  │   .claude/skills/*/SKILL.md     → Skill 类                         │  │
│  │   CLAUDE.md                     → Harness 配置类                    │  │
│  │   agent-butler/config/*.yaml    → YAML 配置类                      │  │
│  │   agent-butler/*.py / scripts/* → Python 脚本类                     │  │
│  │   obs/generated-articles/*.html → HTML 报告类                       │  │
│  │   n8n_integration.yaml 引用     → n8n 自动化类                     │  │
│  └───────────────────────────┬────────────────────────────────────────┘  │
│                              │                                           │
│                  ┌───────────┼───────────┐                               │
│                  ▼           ▼           ▼                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Skill    │  │ Config   │  │ Script   │  │ Runtime  │               │
│  │ Verifier │  │ Verifier │  │ Verifier │  │ Monitor  │               │
│  │          │  │          │  │          │  │          │               │
│  │ session- │  │ harness  │  │ dry-run  │  │ health   │               │
│  │ runner   │  │ loader   │  │ + unit   │  │ check    │               │
│  │ + assert │  │ + constr │  │ test     │  │ + alert  │               │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘               │
│       │             │             │             │                       │
│       └─────────────┴─────────────┴─────────────┘                       │
│                              │                                           │
│                              ▼                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                     结果聚合层                                      │  │
│  │                                                                    │  │
│  │   ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────┐     │  │
│  │   │ 测试报告 │  │ 评分更新  │  │ 回归对比   │  │ Slack/日志通知 │     │  │
│  │   │ JSON    │  │ qa-gate  │  │ diff-based │  │ 告警         │     │  │
│  │   └─────────┘  └──────────┘  └───────────┘  └──────────────┘     │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

### 3.2 各交付物类型的验证策略详细设计

#### 3.2.1 Skill 验证策略（优先级最高）

**核心工具**：Session Runner（参考 gstack `test/helpers/session-runner.ts`）

```
Skill 验证流程：

  SKILL.md 变更 ──→ 提取 test_scenarios
                         │
                         ├── Golden Path 场景
                         │    │
                         │    ▼
                         │   Session Runner 隔离执行
                         │    │ claude -p --dangerously-skip-permissions
                         │    │ --output-format stream-json --verbose
                         │    │
                         │    ▼
                         │   NDJSON 流解析
                         │    │ 提取 toolCalls[]
                         │    │ 提取 exitReason
                         │    │ 提取 output
                         │    │
                         │    ▼
                         │   断言引擎验证
                         │    ├── 工具调用链匹配
                         │    ├── 文件变更检查
                         │    ├── 输出内容匹配
                         │    └── 退出状态检查
                         │
                         ├── Edge Case 场景
                         │    └── (同上流程，降级行为断言)
                         │
                         └── 结果 → 测试报告 JSON
```

**环境隔离方案**：

```python
# 每次 Skill 冒烟测试在临时目录执行
import tempfile, shutil, subprocess

def run_skill_smoke(skill_name: str, scenario: dict) -> dict:
    """在隔离临时目录中执行 Skill golden path"""
    work_dir = tempfile.mkdtemp(prefix=f"synapse-smoke-{skill_name}-")

    try:
        # 1. 准备前置环境（从 scenario.preconditions 复制/创建文件）
        setup_preconditions(work_dir, scenario["preconditions"])

        # 2. 复制 Skill 定义到临时目录
        skill_src = f".claude/skills/{skill_name}"
        shutil.copytree(skill_src, os.path.join(work_dir, ".claude/skills", skill_name))

        # 3. 通过 claude -p 执行 Skill
        result = subprocess.run(
            ["claude", "-p",
             "--model", "claude-sonnet-4-6",
             "--output-format", "stream-json",
             "--verbose",
             "--dangerously-skip-permissions",
             "--max-turns", str(scenario.get("max_turns", 10)),
             "--allowed-tools", "Bash", "Read", "Write", "Edit"],
            input=scenario["prompt"],
            capture_output=True, text=True,
            cwd=work_dir,
            timeout=scenario.get("timeout", 120)
        )

        # 4. 解析 NDJSON 输出
        parsed = parse_ndjson(result.stdout)

        # 5. 执行断言
        return run_assertions(parsed, scenario["expected"], work_dir)

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
```

#### 3.2.2 Harness 配置验证策略

**CLAUDE.md 约束生效验证**：

```
Harness 验证流程：

  CLAUDE.md 变更 ──→ 提取关键约束列表
                         │
                         ├── 约束场景测试（每个约束一个微会话）
                         │    │
                         │    ▼
                         │   claude -p 加载 CLAUDE.md
                         │    │ 发送触发约束的 prompt
                         │    │ 例："请直接用 Bash 执行 ls"
                         │    │
                         │    ▼
                         │   验证 Agent 行为
                         │    ├── CEO Guard：是否拒绝直接执行？
                         │    ├── 派单制度：是否输出派单表？
                         │    ├── 开场问候：是否以问候语开头？
                         │    └── 决策分级：是否正确分级？
                         │
                         └── 结果 → 约束覆盖率报告
```

**关键约束清单**（从 CLAUDE.md 提取，硬编码为验证项）：

```yaml
harness_constraints:
  - id: CEO_GUARD_NO_BASH
    description: "Lysander 不得在主对话直接调用 Bash"
    test_prompt: "请用 Bash 执行 echo hello"
    expected_behavior: "拒绝执行，提示需要通过团队派单"
    severity: P0

  - id: GREETING_REQUIRED
    description: "每次沟通必须以 Lysander 问候语开场"
    test_prompt: "你好"
    expected_behavior: "回复以'总裁您好，我是 Lysander'开头"
    severity: P0

  - id: DISPATCH_TABLE_REQUIRED
    description: "执行前必须输出团队派单表"
    test_prompt: "帮我修改 organization.yaml 添加一个新角色"
    expected_behavior: "输出包含'团队派单'的表格"
    severity: P1

  - id: L4_ESCALATION
    description: "法律/合同/100万预算决策上报总裁"
    test_prompt: "我想签一个 200 万的外包合同"
    expected_behavior: "标记为 L4 决策，请求总裁确认"
    severity: P1
```

#### 3.2.3 YAML 配置验证策略

**三级验证**：

```
YAML 验证流程（三级递进）：

  *.yaml 变更 ──→ Level 1: 格式校验（已有）
                    │  python -c "import yaml; yaml.safe_load(...)"
                    │
                    ▼
                  Level 2: Schema 校验（新增）
                    │  每个 YAML 文件对应一个 JSON Schema
                    │  验证必填字段、类型约束、枚举值
                    │
                    ▼
                  Level 3: 引用有效性校验（新增）
                    │  specialist_id 引用 → 检查 HR/personnel/ 是否存在
                    │  team_name 引用 → 检查 organization.yaml 是否存在
                    │  file_path 引用 → 检查文件系统是否存在
                    │  trigger_id 引用 → 检查远程 Agent 是否有效
                    │
                    ▼
                  结果 → 验证报告
```

**引用有效性检查脚本设计**：

```python
# yaml_reference_validator.py

REFERENCE_RULES = {
    "organization.yaml": {
        "**.specialist_id": {
            "check": "file_exists",
            "pattern": "obs/01-team-knowledge/HR/personnel/{team}/{value}.md"
        },
        "**.reports_to": {
            "check": "key_exists_in",
            "target_file": "organization.yaml",
            "target_path": "teams.*.members.*.name"
        }
    },
    "active_tasks.yaml": {
        "**.assigned_team": {
            "check": "key_exists_in",
            "target_file": "organization.yaml",
            "target_path": "teams.*.name"
        },
        "**.assigned_to": {
            "check": "file_exists",
            "pattern": "obs/01-team-knowledge/HR/personnel/**/{value}.md"
        }
    },
    "n8n_integration.yaml": {
        "**.webhook_url": {
            "check": "url_format",
            "pattern": r"https?://.+"
        },
        "**.prompt_file": {
            "check": "file_exists_relative"
        }
    }
}

def validate_yaml_references(file_path: str) -> list[dict]:
    """验证 YAML 文件中所有跨文件引用的有效性"""
    issues = []
    config = yaml.safe_load(open(file_path))
    rules = REFERENCE_RULES.get(os.path.basename(file_path), {})

    for json_path_pattern, rule in rules.items():
        values = extract_by_pattern(config, json_path_pattern)
        for path, value in values:
            if rule["check"] == "file_exists":
                target = rule["pattern"].format(value=value)
                if not glob.glob(target):
                    issues.append({
                        "file": file_path,
                        "path": path,
                        "value": value,
                        "issue": f"引用目标不存在: {target}",
                        "severity": "error"
                    })
            # ... 其他检查类型
    return issues
```

#### 3.2.4 Python 脚本验证策略

```
Python 脚本验证流程：

  *.py 变更 ──→ Level 1: 语法检查
                  │  python -m py_compile {file}
                  │
                  ▼
                Level 2: Import 检查
                  │  python -c "import {module}"
                  │  检查所有 import 是否可解析
                  │
                  ▼
                Level 3: Dry-Run 冒烟
                  │  若脚本支持 --dry-run 参数 → 执行
                  │  若有对应 test_{name}.py → 执行 pytest
                  │  否则 → 检查入口函数签名和必要环境变量
                  │
                  ▼
                结果 → 验证报告
```

**dry-run 协议**（所有 Python 脚本须遵循）：

```python
# 标准 dry-run 协议：所有脚本入口添加 --dry-run 参数
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="验证配置和依赖，不执行实际操作")
    args = parser.parse_args()

    if args.dry_run:
        # 仅验证：加载配置、检查依赖、打印执行计划
        print("[DRY-RUN] 配置加载: OK")
        print("[DRY-RUN] 依赖检查: OK")
        print(f"[DRY-RUN] 将执行: {describe_planned_actions()}")
        return 0

    # 正常执行
    execute()
```

#### 3.2.5 HTML 报告验证策略

```
HTML 报告验证流程：

  *.html 生成 ──→ Level 1: HTML 语法
                    │  python: html.parser 解析无异常
                    │
                    ▼
                  Level 2: 内容完整性
                    │  ├── 非空检查：文件 > 1KB
                    │  ├── 结构检查：包含 <html><head><body>
                    │  ├── 数据检查：无 {{placeholder}} 未替换
                    │  └── 链接检查：内部链接可达
                    │
                    ▼
                  Level 3: 数据新鲜度
                    │  ├── 日期字段 >= today - 1day
                    │  ├── 数据源文件 modified_time 检查
                    │  └── 无"暂无数据"/"数据加载失败"等占位符
                    │
                    ▼
                  结果 → 验证报告
```

**HTML 验证脚本设计**：

```python
# html_report_validator.py

from html.parser import HTMLParser
import re, os
from datetime import datetime, timedelta

class ReportValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_html = False
        self.has_body = False
        self.has_content = False
        self.unreplaced_placeholders = []
        self.text_content = []

    def handle_starttag(self, tag, attrs):
        if tag == 'html': self.has_html = True
        if tag == 'body': self.has_body = True

    def handle_data(self, data):
        self.text_content.append(data)
        placeholders = re.findall(r'\{\{[^}]+\}\}', data)
        self.unreplaced_placeholders.extend(placeholders)

def validate_html_report(file_path: str) -> dict:
    content = open(file_path, encoding='utf-8').read()
    results = {"file": file_path, "issues": []}

    # Level 1: 语法
    parser = ReportValidator()
    try:
        parser.feed(content)
    except Exception as e:
        results["issues"].append({"level": "error", "msg": f"HTML 解析失败: {e}"})
        return results

    # Level 2: 完整性
    if len(content) < 1024:
        results["issues"].append({"level": "warning", "msg": "文件过小 (<1KB)"})
    if not parser.has_html or not parser.has_body:
        results["issues"].append({"level": "error", "msg": "缺少 <html> 或 <body> 标签"})
    if parser.unreplaced_placeholders:
        results["issues"].append({"level": "error",
            "msg": f"未替换占位符: {parser.unreplaced_placeholders}"})

    # Level 3: 新鲜度
    full_text = ' '.join(parser.text_content)
    stale_markers = ["暂无数据", "数据加载失败", "No data available", "Loading..."]
    for marker in stale_markers:
        if marker in full_text:
            results["issues"].append({"level": "warning", "msg": f"疑似过期占位符: {marker}"})

    return results
```

#### 3.2.6 n8n 自动化验证策略

```
n8n 自动化验证流程：

  n8n_integration.yaml 变更
        │
        ▼
  Level 1: 配置完整性
        │  ├── 所有 webhook_url 格式正确
        │  ├── 所有 trigger_id 非空
        │  ├── schedule cron 表达式合法
        │  └── event_chains 无断裂（每个 step 的输出是下一步的输入）
        │
        ▼
  Level 2: 端点可达性（轻量 HEAD 请求）
        │  ├── webhook URL HEAD → 200/405（存在即可）
        │  └── 超时 5s → 标记 unreachable（warning, 不阻塞）
        │
        ▼
  Level 3: 心跳监控（持续运行）
        │  ├── 每个定时 Agent 应有最近 24h 内的执行记录
        │  ├── 检查 logs/n8n_executions/ 下的最新日志
        │  └── 无记录 → 告警 Slack
        │
        ▼
  结果 → 健康报告 + 告警
```

### 3.3 与现有执行链的集成点

```
执行链 v2.0 ← 质量框架集成点标注

【开场】Lysander 身份确认
        ↓
【0】目标接收与确认
        ↓
【①】智囊团分级与方案
        ↓
【②】执行团队共识与执行
        │
        │  ◆ 集成点 A：内嵌测试定义检查
        │    执行团队开始工作前，检查交付物是否已定义 test_scenarios
        │    缺失 → 团队必须先定义再执行（Definition-First 原则）
        │
        ↓
【②.5】交付前冒烟测试 ← ★ 新增环节 ★
        │
        │  ◆ 集成点 B：按类型执行冒烟
        │    执行完成后、QA 审查前，自动触发冒烟测试
        │    冒烟失败 → 退回执行团队，不进入 QA
        │    冒烟通过 → 进入 QA 审查
        │
        ↓
【③】QA + 智囊团审查
        │
        │  ◆ 集成点 C：qa-gate 新增第 6 维度评分
        │    "功能端到端完整性" 维度已纳入 qa-gate 评分
        │    评分依据：test_scenarios 定义 + 冒烟测试结果
        │
        ↓
【④】结果交付
        │
        │  ◆ 集成点 D：交付物附带测试证据
        │    L 级任务交付时，附带冒烟测试报告摘要

  ===== 交付后（持续运行）=====

        ◆ 集成点 E：后台健康监控
          n8n Agent 心跳检查（每日）
          定时任务执行状态检查
          失败 → Slack 告警 → 自动恢复尝试
```

---

## 4. Skill E2E 测试框架详细设计

### 4.1 Session Runner 实现方案

Synapse 的 Session Runner 基于 gstack 的 `test/helpers/session-runner.ts` 设计，但适配 Python + Synapse 体系。

**架构选择**：Python 实现（与 Synapse 现有 agent-butler 代码库一致），通过 `claude -p` 子进程执行。

```
Session Runner 架构：

  ┌─────────────────────────────────────────────┐
  │              synapse_test_runner.py           │
  │                                               │
  │  ┌─────────┐  ┌──────────┐  ┌────────────┐  │
  │  │ Scenario │  │ Session  │  │ Assertion  │  │
  │  │ Loader   │  │ Executor │  │ Engine     │  │
  │  │          │  │          │  │            │  │
  │  │ 从 SKILL │  │ claude-p │  │ 工具调用链 │  │
  │  │ .md 提取 │  │ 子进程   │  │ 文件变更   │  │
  │  │ 场景定义 │  │ NDJSON   │  │ 输出匹配   │  │
  │  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
  │       │             │              │          │
  │       └─────────────┼──────────────┘          │
  │                     │                          │
  │              ┌──────┴──────┐                   │
  │              │ Result Store│                   │
  │              │ JSON + diff │                   │
  │              └─────────────┘                   │
  └─────────────────────────────────────────────┘
```

**核心模块**：

```python
# agent-butler/test_runner/session_runner.py

import subprocess
import json
import tempfile
import os
import time
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ToolCall:
    tool: str
    input: dict
    output: str = ""

@dataclass
class CostEstimate:
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0
    turns_used: int = 0

@dataclass
class SkillTestResult:
    tool_calls: list[ToolCall] = field(default_factory=list)
    exit_reason: str = "unknown"
    duration: float = 0.0
    output: str = ""
    cost_estimate: CostEstimate = field(default_factory=CostEstimate)
    transcript: list[dict] = field(default_factory=list)
    model: str = ""
    errors: list[str] = field(default_factory=list)

def parse_ndjson(lines: list[str]) -> dict:
    """
    解析 NDJSON 输出流，提取工具调用链和结果。
    参考 gstack session-runner.ts 的 parseNDJSON() 函数。
    """
    transcript = []
    result_line = None
    tool_calls = []
    turn_count = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
            transcript.append(event)

            if event.get("type") == "assistant":
                turn_count += 1
                content = event.get("message", {}).get("content", [])
                for item in content:
                    if item.get("type") == "tool_use":
                        tool_calls.append(ToolCall(
                            tool=item.get("name", "unknown"),
                            input=item.get("input", {}),
                        ))

            if event.get("type") == "result":
                result_line = event
        except json.JSONDecodeError:
            continue  # 跳过格式错误行

    return {
        "transcript": transcript,
        "result_line": result_line,
        "tool_calls": tool_calls,
        "turn_count": turn_count,
    }


def run_skill_test(
    prompt: str,
    working_directory: str,
    max_turns: int = 10,
    allowed_tools: list[str] = None,
    timeout: int = 120,
    model: str = None,
) -> SkillTestResult:
    """
    在隔离环境中通过 claude -p 执行 Skill 冒烟测试。
    参考 gstack session-runner.ts 的 runSkillTest() 函数。
    """
    if allowed_tools is None:
        allowed_tools = ["Bash", "Read", "Write", "Edit", "Grep", "Glob"]
    if model is None:
        model = os.environ.get("SYNAPSE_TEST_MODEL", "claude-sonnet-4-6")

    start_time = time.time()

    # 将 prompt 写入临时文件避免 shell 转义问题（参考 gstack 做法）
    prompt_file = tempfile.mktemp(prefix="synapse-test-prompt-")
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)

    args = [
        "claude", "-p",
        "--model", model,
        "--output-format", "stream-json",
        "--verbose",
        "--dangerously-skip-permissions",
        "--max-turns", str(max_turns),
        "--allowed-tools", *allowed_tools,
    ]

    try:
        result = subprocess.run(
            args,
            stdin=open(prompt_file, "r", encoding="utf-8"),
            capture_output=True,
            text=True,
            cwd=working_directory,
            timeout=timeout,
        )
        exit_code = result.returncode
        stdout_lines = result.stdout.strip().split("\n") if result.stdout else []
    except subprocess.TimeoutExpired:
        return SkillTestResult(
            exit_reason="timeout",
            duration=time.time() - start_time,
            errors=[f"Timeout after {timeout}s"],
        )
    finally:
        try:
            os.unlink(prompt_file)
        except OSError:
            pass

    duration = time.time() - start_time

    # 解析 NDJSON
    parsed = parse_ndjson(stdout_lines)

    # 确定退出原因
    exit_reason = "unknown"
    result_line = parsed["result_line"]
    if result_line:
        subtype = result_line.get("subtype", "")
        if subtype == "success" and not result_line.get("is_error"):
            exit_reason = "success"
        elif subtype == "success" and result_line.get("is_error"):
            exit_reason = "error_api"
        elif subtype:
            exit_reason = subtype
    elif exit_code == 0:
        exit_reason = "success"
    else:
        exit_reason = f"exit_code_{exit_code}"

    # 构建 cost estimate
    cost = CostEstimate(
        input_tokens=result_line.get("usage", {}).get("input_tokens", 0) if result_line else 0,
        output_tokens=result_line.get("usage", {}).get("output_tokens", 0) if result_line else 0,
        estimated_cost=result_line.get("total_cost_usd", 0) if result_line else 0,
        turns_used=result_line.get("num_turns", 0) if result_line else 0,
    )

    return SkillTestResult(
        tool_calls=parsed["tool_calls"],
        exit_reason=exit_reason,
        duration=duration,
        output=result_line.get("result", "") if result_line else "",
        cost_estimate=cost,
        transcript=parsed["transcript"],
        model=model,
    )
```

### 4.2 test_scenarios 格式规范

已在 `obs/03-process-knowledge/skill-template.md` 定义。以下是扩展的机器可读格式，用于 Session Runner 自动提取：

```yaml
# SKILL.md 中的 test_scenarios 块（YAML 格式，嵌入 Markdown）
# Session Runner 通过正则提取 ```yaml ... ``` 代码块

test_scenarios:
  golden_path:
    - name: "正常捕获任务到 inbox"
      input: "/capture 准备明天的团队周会"
      preconditions:
        files:
          - path: "agent-butler/config/personal_tasks.yaml"
            content: |
              inbox: []
              projects: []
      max_turns: 8
      timeout: 60
      expected:
        exit_reason: "success"
        file_changes:
          - path: "agent-butler/config/personal_tasks.yaml"
            must_contain: ["准备明天的团队周会"]
            must_not_contain: ["inbox: []"]  # inbox 不应为空了
        tool_chain:
          # 有序子序列匹配：这些工具调用必须按此顺序出现（可有间隔）
          - tool: "Read"           # 先读取现有文件
          - tool: "Edit"           # 写入新条目
        output_contains: ["捕获", "inbox"]

  edge_cases:
    - name: "personal_tasks.yaml 不存在"
      input: "/capture 第一个任务"
      preconditions:
        files: []  # 不创建任何文件
      max_turns: 8
      timeout: 60
      expected:
        exit_reason: "success"
        file_changes:
          - path: "agent-butler/config/personal_tasks.yaml"
            must_exist: true
            must_contain: ["第一个任务"]
        must_not:
          - tool_call: "Error"  # 不应报错中断
```

**场景提取器**：

```python
# agent-butler/test_runner/scenario_loader.py

import re
import yaml
from pathlib import Path

def extract_test_scenarios(skill_md_path: str) -> dict | None:
    """
    从 SKILL.md 中提取 test_scenarios YAML 块。
    查找 ```yaml 代码块中包含 test_scenarios: 的部分。
    """
    content = Path(skill_md_path).read_text(encoding="utf-8")

    # 匹配包含 test_scenarios 的 YAML 代码块
    pattern = r'```yaml\s*\n(test_scenarios:.*?)```'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return None

    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def load_all_skill_scenarios(skills_dir: str = ".claude/skills") -> dict:
    """
    加载所有 Skill 的 test_scenarios。
    返回 {skill_name: scenarios_dict}。
    """
    results = {}
    skills_path = Path(skills_dir)

    for skill_dir in skills_path.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        scenarios = extract_test_scenarios(str(skill_md))
        if scenarios:
            results[skill_dir.name] = scenarios
        else:
            results[skill_dir.name] = None  # 标记为无 test_scenarios

    return results
```

### 4.3 工具调用链断言引擎

**核心能力**：验证 Skill 执行过程中的工具调用序列是否符合预期。

```python
# agent-butler/test_runner/assertion_engine.py

import re
import os
from dataclasses import dataclass

@dataclass
class AssertionResult:
    passed: bool
    assertion_type: str
    detail: str

def assert_tool_chain(
    actual_calls: list,  # ToolCall 列表
    expected_chain: list[dict],  # [{"tool": "Read"}, {"tool": "Edit"}]
) -> AssertionResult:
    """
    验证工具调用链是否包含预期的有序子序列。
    不要求完全匹配——允许中间有额外调用——但顺序必须一致。

    参考 gstack E2E 测试中的断言模式：
    - 检查 toolCalls 数组中是否按序包含预期工具
    - 支持通配符匹配（tool: "*" 匹配任意工具）
    """
    actual_idx = 0
    for expected in expected_chain:
        found = False
        while actual_idx < len(actual_calls):
            actual = actual_calls[actual_idx]
            actual_idx += 1

            tool_match = (
                expected.get("tool") == "*"
                or actual.tool == expected.get("tool")
            )
            input_match = True
            if "input_contains" in expected:
                input_str = str(actual.input)
                input_match = expected["input_contains"] in input_str

            if tool_match and input_match:
                found = True
                break

        if not found:
            return AssertionResult(
                passed=False,
                assertion_type="tool_chain",
                detail=f"未找到预期工具调用: {expected}，"
                       f"实际调用链: {[c.tool for c in actual_calls]}"
            )

    return AssertionResult(passed=True, assertion_type="tool_chain", detail="工具调用链匹配")


def assert_file_changes(
    work_dir: str,
    expected_changes: list[dict],
) -> list[AssertionResult]:
    """
    验证文件变更是否符合预期。
    检查文件是否存在、内容是否包含/不包含指定字符串。
    """
    results = []

    for change in expected_changes:
        file_path = os.path.join(work_dir, change["path"])

        # 存在性检查
        if change.get("must_exist", True):
            if not os.path.exists(file_path):
                results.append(AssertionResult(
                    passed=False,
                    assertion_type="file_exists",
                    detail=f"文件不存在: {change['path']}"
                ))
                continue

        # 内容包含检查
        if os.path.exists(file_path):
            content = open(file_path, encoding="utf-8").read()

            for keyword in change.get("must_contain", []):
                if keyword not in content:
                    results.append(AssertionResult(
                        passed=False,
                        assertion_type="file_content",
                        detail=f"{change['path']} 未包含: {keyword}"
                    ))
                else:
                    results.append(AssertionResult(
                        passed=True,
                        assertion_type="file_content",
                        detail=f"{change['path']} 包含: {keyword}"
                    ))

            for keyword in change.get("must_not_contain", []):
                if keyword in content:
                    results.append(AssertionResult(
                        passed=False,
                        assertion_type="file_content_negative",
                        detail=f"{change['path']} 不应包含但包含了: {keyword}"
                    ))

    return results


def assert_output(
    actual_output: str,
    expected: dict,
) -> list[AssertionResult]:
    """
    验证 Skill 最终输出是否符合预期。
    """
    results = []

    for keyword in expected.get("output_contains", []):
        if keyword.lower() in actual_output.lower():
            results.append(AssertionResult(
                passed=True,
                assertion_type="output_contains",
                detail=f"输出包含: {keyword}"
            ))
        else:
            results.append(AssertionResult(
                passed=False,
                assertion_type="output_contains",
                detail=f"输出未包含: {keyword}"
            ))

    return results


def run_all_assertions(
    test_result,  # SkillTestResult
    expected: dict,
    work_dir: str,
) -> dict:
    """
    执行全部断言，返回汇总结果。
    """
    all_results = []

    # 退出状态断言
    if "exit_reason" in expected:
        all_results.append(AssertionResult(
            passed=test_result.exit_reason == expected["exit_reason"],
            assertion_type="exit_reason",
            detail=f"预期={expected['exit_reason']}, 实际={test_result.exit_reason}"
        ))

    # 工具调用链断言
    if "tool_chain" in expected:
        all_results.append(assert_tool_chain(
            test_result.tool_calls,
            expected["tool_chain"]
        ))

    # 文件变更断言
    if "file_changes" in expected:
        all_results.extend(assert_file_changes(work_dir, expected["file_changes"]))

    # 输出断言
    all_results.extend(assert_output(test_result.output, expected))

    passed = all(r.passed for r in all_results)
    return {
        "passed": passed,
        "total": len(all_results),
        "passed_count": sum(1 for r in all_results if r.passed),
        "failed_count": sum(1 for r in all_results if not r.passed),
        "details": [
            {"passed": r.passed, "type": r.assertion_type, "detail": r.detail}
            for r in all_results
        ]
    }
```

### 4.4 测试结果存储和对比

**存储结构**（参考 gstack `test/helpers/eval-store.ts`）：

```
agent-butler/test_results/
├── runs/
│   ├── 2026-04-12T14-30-00/           # 每次运行一个目录
│   │   ├── summary.json               # 运行摘要
│   │   ├── capture-golden-path.json   # 单个测试结果
│   │   ├── capture-no-file.json
│   │   ├── plan-day-golden-path.json
│   │   └── progress.log               # 实时进度日志
│   └── 2026-04-12T15-00-00/
│       └── ...
├── baselines/
│   └── latest.json                    # 最近一次全量通过的结果（用于回归对比）
└── history.jsonl                      # 历史记录（append-only）
```

**运行摘要格式**（summary.json）：

```json
{
  "run_id": "2026-04-12T14-30-00",
  "started_at": "2026-04-12T14:30:00Z",
  "completed_at": "2026-04-12T14:35:22Z",
  "trigger": "manual",
  "total_tests": 12,
  "passed": 10,
  "failed": 2,
  "skipped": 3,
  "total_cost_usd": 0.42,
  "total_duration_s": 322,
  "model": "claude-sonnet-4-6",
  "tests": {
    "capture-golden-path": {"passed": true, "duration": 28.5, "cost": 0.03},
    "capture-no-file": {"passed": true, "duration": 31.2, "cost": 0.04},
    "plan-day-golden-path": {"passed": false, "duration": 45.1, "cost": 0.05,
      "failure": "文件变更断言失败: personal_tasks.yaml 未包含 'focus'"}
  }
}
```

**回归对比机制**：

```python
# agent-butler/test_runner/regression.py

def compare_runs(current: dict, baseline: dict) -> dict:
    """
    对比当前运行结果和基线，检测回归。

    回归定义：
    - 基线通过但当前失败的测试
    - 成本增加 > 50% 的测试（可能是 prompt 膨胀）
    - 时长增加 > 100% 的测试（可能是死循环）
    """
    regressions = []
    improvements = []

    for test_name, current_test in current["tests"].items():
        baseline_test = baseline.get("tests", {}).get(test_name)
        if not baseline_test:
            continue  # 新测试，无对比基线

        # 通过 → 失败 = 回归
        if baseline_test["passed"] and not current_test["passed"]:
            regressions.append({
                "test": test_name,
                "type": "functional_regression",
                "detail": current_test.get("failure", "unknown"),
            })

        # 失败 → 通过 = 改善
        if not baseline_test["passed"] and current_test["passed"]:
            improvements.append({"test": test_name, "type": "fixed"})

        # 成本膨胀检查
        if baseline_test.get("cost", 0) > 0:
            cost_ratio = current_test.get("cost", 0) / baseline_test["cost"]
            if cost_ratio > 1.5:
                regressions.append({
                    "test": test_name,
                    "type": "cost_regression",
                    "detail": f"成本从 ${baseline_test['cost']:.2f} 涨到 ${current_test['cost']:.2f} (+{(cost_ratio-1)*100:.0f}%)",
                })

    return {
        "regressions": regressions,
        "improvements": improvements,
        "has_regressions": len(regressions) > 0,
    }
```

### 4.5 Touchfile 选择性测试（参考 gstack）

**核心思路**：Skill 文件变更时才触发对应测试，避免每次运行全量。

```python
# agent-butler/test_runner/touchfiles.py

"""
Diff-based 选择性测试。
参考 gstack test/helpers/touchfiles.ts 的 selectTests() 函数。
"""

import subprocess
import fnmatch

# 每个 Skill 测试依赖的文件列表
SKILL_TOUCHFILES: dict[str, list[str]] = {
    "capture": [
        ".claude/skills/capture/SKILL.md",
        "agent-butler/config/personal_tasks.yaml",
    ],
    "plan-day": [
        ".claude/skills/plan-day/SKILL.md",
        "agent-butler/config/personal_tasks.yaml",
        "agent-butler/config/active_tasks.yaml",
        "agent-butler/config/calendar_config.yaml",
    ],
    "qa-gate": [
        ".claude/skills/qa-gate/SKILL.md",
    ],
    "dispatch": [
        ".claude/skills/dispatch/SKILL.md",
        "agent-butler/config/organization.yaml",
    ],
    "intel": [
        ".claude/skills/intel/SKILL.md",
    ],
    "daily-blog": [
        ".claude/skills/daily-blog/SKILL.md",
        "scripts/generate-article.py",
    ],
    # ... 其他 Skill
}

# 全局 touchfile：变更时触发所有测试
GLOBAL_TOUCHFILES = [
    "agent-butler/test_runner/session_runner.py",
    "agent-butler/test_runner/assertion_engine.py",
    "agent-butler/test_runner/touchfiles.py",
    "CLAUDE.md",  # Harness 变更可能影响所有 Skill 行为
]

# 测试分级：gate 阻塞交付，periodic 周期运行
SKILL_TIERS: dict[str, str] = {
    "capture": "gate",        # 总裁高频使用
    "plan-day": "gate",       # 每日必用
    "qa-gate": "gate",        # 质量基础设施
    "dispatch": "gate",       # 核心流程
    "intel": "periodic",      # 非阻塞
    "daily-blog": "periodic", # 可容忍延迟修复
    "graphify": "periodic",
    "knowledge": "periodic",
    "retro": "periodic",
    "weekly-review": "periodic",
    "dev-plan": "gate",
    "dev-review": "gate",
    "dev-qa": "gate",
    "dev-ship": "gate",
    "synapse": "gate",
    "time-block": "periodic",
    "video-tutorial": "periodic",
    "dev-secure": "periodic",
    "hr-audit": "periodic",
}


def get_changed_files(base_branch: str = "origin/main") -> list[str]:
    """获取相对于基础分支的变更文件列表。"""
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_branch}...HEAD"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0:
        return []
    return [f for f in result.stdout.strip().split("\n") if f]


def select_tests(
    changed_files: list[str],
    tier_filter: str | None = None,  # "gate" | "periodic" | None(全部)
) -> dict:
    """
    基于变更文件选择需要运行的测试。
    参考 gstack selectTests() 逻辑。
    """
    # 全局 touchfile 命中 → 运行全部
    for f in changed_files:
        for g in GLOBAL_TOUCHFILES:
            if fnmatch.fnmatch(f, g):
                all_tests = list(SKILL_TOUCHFILES.keys())
                if tier_filter:
                    all_tests = [t for t in all_tests if SKILL_TIERS.get(t) == tier_filter]
                return {
                    "selected": all_tests,
                    "skipped": [],
                    "reason": f"global touchfile: {f}",
                }

    # 逐 Skill 匹配
    selected = []
    skipped = []
    for skill_name, patterns in SKILL_TOUCHFILES.items():
        if tier_filter and SKILL_TIERS.get(skill_name) != tier_filter:
            skipped.append(skill_name)
            continue

        hit = any(
            fnmatch.fnmatch(f, p)
            for f in changed_files
            for p in patterns
        )
        (selected if hit else skipped).append(skill_name)

    return {"selected": selected, "skipped": skipped, "reason": "diff-based"}
```

### 4.6 Two-Tier 分级系统

参考 gstack 的 `E2E_TIERS`，Synapse 测试分为两级：

| 级别 | 运行时机 | 阻塞性 | 成本控制 | 适用场景 |
|------|---------|--------|---------|---------|
| **gate** | 每次交付前 | 阻塞 | <$0.50/次 | 总裁高频使用的 Skill、核心流程 |
| **periodic** | 每日定时 / 手动 | 不阻塞 | <$5/次 | 低频 Skill、质量基准、回归检测 |

**gate 级测试约束**：
- 使用 `claude-sonnet-4-6` 模型（成本低、速度快）
- max_turns <= 10
- timeout <= 60s
- 单次测试成本 < $0.10

**periodic 级测试约束**：
- 可使用 `claude-opus-4-6` 模型（质量更高）
- max_turns <= 20
- timeout <= 180s
- 支持 LLM-as-Judge 评分

---

## 5. 后台健康监控设计

### 5.1 心跳机制

```
后台健康监控架构：

  ┌────────────────────────────────────────────────────────┐
  │                  Synapse Health Monitor                  │
  │                                                          │
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
  │  │ Agent 心跳    │  │ 任务链完整性  │  │ 资源可用性    │  │
  │  │              │  │              │  │              │  │
  │  │ 检查每个定时  │  │ event_chain  │  │ webhook URL  │  │
  │  │ Agent 最近   │  │ 是否有断裂   │  │ MCP 服务     │  │
  │  │ 执行时间     │  │ （步骤跳过） │  │ git remote   │  │
  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
  │         │                 │                 │          │
  │         └─────────────────┼─────────────────┘          │
  │                           │                             │
  │                    ┌──────┴──────┐                      │
  │                    │ 告警决策器   │                      │
  │                    │             │                      │
  │                    │ P0: 立即告警 │                      │
  │                    │ P1: 汇总日报 │                      │
  │                    │ P2: 周报记录 │                      │
  │                    └──────┬──────┘                      │
  │                           │                             │
  │                    ┌──────┴──────┐                      │
  │                    │ 通知渠道    │                      │
  │                    │ Slack / Log │                      │
  │                    └─────────────┘                      │
  └────────────────────────────────────────────────────────┘
```

### 5.2 心跳检查实现

```python
# agent-butler/health_monitor.py

"""
Synapse 后台健康监控。
设计为定时 Agent 执行（每日 6:00am Dubai，在任务恢复 Agent 之后）。
"""

import os
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path

# 定时 Agent 心跳预期（从 n8n_integration.yaml 提取）
EXPECTED_AGENTS = {
    "task-auto-resume": {
        "description": "任务自动恢复 Agent",
        "schedule": "0 2 * * *",  # UTC 2:00 = Dubai 6:00am
        "max_gap_hours": 26,  # 允许 26 小时间隔（容忍 2 小时偏移）
        "severity": "P0",
    },
    "intelligence-daily": {
        "description": "情报日报 Agent",
        "schedule": "0 4 * * *",  # UTC 4:00 = Dubai 8:00am
        "max_gap_hours": 26,
        "severity": "P1",
    },
    "intelligence-action": {
        "description": "情报行动 Agent",
        "schedule": "0 6 * * *",  # UTC 6:00 = Dubai 10:00am
        "max_gap_hours": 26,
        "severity": "P1",
    },
    "daily-retro-blog": {
        "description": "每日复盘+博客 Agent",
        "schedule": "43 21 * * *",
        "max_gap_hours": 26,
        "severity": "P1",
    },
    "calendar-sync": {
        "description": "SPE 日历同步 Agent",
        "schedule": "15 2 * * *",
        "max_gap_hours": 26,
        "severity": "P1",
    },
}


def check_agent_heartbeats(log_dir: str = "logs/n8n_executions") -> list[dict]:
    """
    检查每个定时 Agent 的最近执行记录。
    从执行日志目录中查找最新的日志文件。
    """
    alerts = []
    now = datetime.utcnow()

    for agent_id, config in EXPECTED_AGENTS.items():
        # 查找该 Agent 的最新日志
        pattern = os.path.join(log_dir, f"*{agent_id}*")
        log_files = sorted(glob.glob(pattern), reverse=True)

        if not log_files:
            alerts.append({
                "agent": agent_id,
                "description": config["description"],
                "status": "NO_RECORD",
                "severity": config["severity"],
                "detail": "从未有执行记录",
            })
            continue

        # 检查最新日志的时间戳
        latest_log = log_files[0]
        mtime = datetime.fromtimestamp(os.path.getmtime(latest_log))
        gap_hours = (now - mtime).total_seconds() / 3600

        if gap_hours > config["max_gap_hours"]:
            alerts.append({
                "agent": agent_id,
                "description": config["description"],
                "status": "STALE",
                "severity": config["severity"],
                "detail": f"最近执行: {mtime.isoformat()}, 已过 {gap_hours:.1f} 小时",
                "last_run": mtime.isoformat(),
            })

        # 检查最新日志是否包含错误
        try:
            log_content = Path(latest_log).read_text(encoding="utf-8", errors="ignore")
            if "ERROR" in log_content or "FAILED" in log_content:
                alerts.append({
                    "agent": agent_id,
                    "description": config["description"],
                    "status": "ERROR_IN_LOG",
                    "severity": config["severity"],
                    "detail": f"最近日志包含错误: {latest_log}",
                })
        except Exception:
            pass

    return alerts


def check_event_chain_integrity() -> list[dict]:
    """
    检查事件链完整性：每日管线的每个步骤是否都有执行记录。
    从 active_tasks.yaml 或专用状态文件中读取。
    """
    alerts = []

    # 检查每日管线：恢复 → 情报 → 行动 → 通知
    chain_steps = [
        "task-auto-resume",
        "intelligence-daily",
        "intelligence-action",
    ]

    # 检查昨天的管线是否完整执行
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    for i, step in enumerate(chain_steps[:-1]):
        next_step = chain_steps[i + 1]
        # 如果前一步执行了但后一步没执行 → 链断裂
        # 具体实现依赖日志格式，此处为逻辑框架

    return alerts


def check_resource_availability() -> list[dict]:
    """
    检查关键资源可用性。
    """
    alerts = []
    import urllib.request

    # 检查 webhook URL 可达性
    webhook_urls = [
        ("n8n Cloud", "https://n8n.lysander.bond"),
        ("Lysander API", "https://lysander.bond"),
    ]

    for name, url in webhook_urls:
        try:
            req = urllib.request.Request(url, method="HEAD")
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            alerts.append({
                "resource": name,
                "url": url,
                "status": "UNREACHABLE",
                "severity": "P1",
                "detail": str(e)[:200],
            })

    return alerts


def run_health_check() -> dict:
    """
    执行完整健康检查，返回汇总报告。
    """
    heartbeat_alerts = check_agent_heartbeats()
    chain_alerts = check_event_chain_integrity()
    resource_alerts = check_resource_availability()

    all_alerts = heartbeat_alerts + chain_alerts + resource_alerts
    p0_alerts = [a for a in all_alerts if a.get("severity") == "P0"]

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "UNHEALTHY" if p0_alerts else ("DEGRADED" if all_alerts else "HEALTHY"),
        "total_alerts": len(all_alerts),
        "p0_count": len(p0_alerts),
        "alerts": all_alerts,
        "summary": generate_health_summary(all_alerts),
    }


def generate_health_summary(alerts: list[dict]) -> str:
    """生成人类可读的健康摘要（用于 Slack 通知）。"""
    if not alerts:
        return "All systems operational. No alerts."

    lines = [f"Health Check: {len(alerts)} alert(s) detected"]
    for a in alerts:
        icon = "!!!" if a.get("severity") == "P0" else "!"
        lines.append(f"  {icon} [{a.get('severity', '?')}] {a.get('description', a.get('agent', a.get('resource', '?')))}: {a.get('detail', '')}")
    return "\n".join(lines)
```

### 5.3 失败检测和告警

**告警分级**：

| 级别 | 触发条件 | 通知方式 | 响应时间 |
|------|---------|---------|---------|
| **P0** | 任务恢复 Agent 停止 / git push 失败 | Slack 立即推送 | <1小时 |
| **P1** | 情报管线断裂 / 博客生成失败 | Slack 日报汇总 | <24小时 |
| **P2** | 周期测试失败 / 性能下降 | 周报记录 | 下次 review |

**Slack 告警模板**：

```
[SYNAPSE HEALTH ALERT]

Status: UNHEALTHY
Time: 2026-04-12 06:05:00 UTC (Dubai 10:05am)

P0 Alerts:
  !!! task-auto-resume: 最近执行 36.2 小时前，超过 26h 阈值

P1 Alerts:
  ! intelligence-daily: 最近日志包含 ERROR
  ! n8n Cloud: webhook URL 超时

Action Required:
  - 检查 Claude Scheduled Agents: https://claude.ai/code/scheduled
  - 检查 n8n Cloud: https://n8n.lysander.bond
```

### 5.4 自动恢复策略

```
自动恢复决策树：

  Agent 心跳丢失
       │
       ▼
  检查 Claude Scheduled Agents 状态
       │
       ├── Agent 存在但暂停 → 尝试重新启用（L1 自动）
       │
       ├── Agent 存在但报错 → 检查错误日志
       │    │
       │    ├── 凭证过期 → 提醒总裁更新凭证（L4）
       │    ├── 配置错误 → 自动修复配置 → 重试（L2）
       │    └── 临时错误 → 等待下次自动执行（L1）
       │
       └── Agent 不存在 → 告警 → 需要人工重建（L3）
```

---

## 6. 执行链集成方案

### 6.1 升级后的执行链流程图

```
升级后执行链 v2.1（含质量框架集成点）

【开场】Lysander 身份确认
        ↓
【0】目标接收与确认
        ↓
【①】智囊团分级与方案
        │
        │  ★ 新增：分级时标注交付物类型
        │  （Skill/Config/YAML/Script/HTML/n8n）
        ↓
【②】执行团队共识与执行
        │
        │  ★ 新增：Definition-First 检查
        │  执行前确认：
        │  ├── Skill 类 → test_scenarios 是否已定义？
        │  ├── Script 类 → --dry-run 协议是否已实现？
        │  └── Config 类 → Schema 是否已存在？
        │  缺失 → 先定义再执行（不阻塞，但 QA 评分扣分）
        │
        ↓  ← 执行完成
        │
【②.5】交付前冒烟测试 ← ★★★ 新增环节 ★★★
        │
        │  按交付物类型自动路由：
        │  ┌─ Skill → session-runner 执行 golden path
        │  ├─ Harness 配置 → 约束场景验证
        │  ├─ YAML → 格式 + Schema + 引用有效性
        │  ├─ Python → py_compile + import + dry-run
        │  ├─ HTML → 渲染 + 完整性 + 新鲜度
        │  └─ n8n → 配置完整性 + 端点可达性
        │
        │  gate 级失败 → 退回【②】修复
        │  gate 级通过 → 进入【③】
        ↓
【③】QA + 智囊团审查（升级版）
        │
        │  /qa-gate 评分维度（6项，满分6.0）：
        │  1. 目标达成度 (0-1.0)
        │  2. 执行链完整性 (0-1.0)
        │  3. 技术质量 (0-1.0)
        │  4. 知识沉淀 (0-1.0)
        │  5. 风险控制 (0-1.0)
        │  6. 功能端到端完整性 (0-1.0) ← 已新增
        │     评分依据 = test_scenarios 定义 + 冒烟测试通过率
        │
        │  >= 4.2 → 通过
        │  < 4.2  → 退回
        ↓
【④】结果交付
        │
        │  ★ 新增：交付物附带质量证据
        │  L 级任务附带：
        │  ├── 冒烟测试报告摘要
        │  ├── QA 评分卡
        │  └── 回归对比结果（如有）

  ===== 交付后（持续运行）=====

【⑤】后台健康监控 ← ★ 新增 ★
        │
        │  每日 6:15am Dubai 自动执行：
        │  ├── Agent 心跳检查
        │  ├── 事件链完整性检查
        │  ├── 资源可用性检查
        │  └── Periodic 测试运行
        │
        │  异常 → Slack 告警
        │  正常 → 静默（不打扰总裁）
```

### 6.2 各环节的新增/变更点

| 环节 | 变更类型 | 具体内容 |
|------|---------|---------|
| 【①】分级 | 新增 | 标注交付物类型，用于路由冒烟策略 |
| 【②】执行 | 新增 | Definition-First 检查（test_scenarios / dry-run / schema） |
| 【②.5】冒烟 | **新增环节** | 交付前按类型执行冒烟测试，gate 级失败阻塞 |
| 【③】QA | 升级 | /qa-gate 新增第 6 维度"功能端到端完整性"评分 |
| 【④】交付 | 新增 | L 级任务附带质量证据（冒烟报告 + 评分卡） |
| 【⑤】监控 | **新增环节** | 后台健康监控，每日自动运行 |

### 6.3 冒烟测试集成到 /qa-gate 的具体方式

```
/qa-gate 调用冒烟测试的流程：

  /qa-gate [交付物描述]
       │
       ▼
  判断交付物类型
       │
       ├── 是 Skill？→ 读取 SKILL.md → 提取 test_scenarios
       │    │
       │    ├── 有 test_scenarios → 执行 session-runner 冒烟
       │    │    │
       │    │    ├── golden path 全通过 → 第6维度 = 1.0
       │    │    ├── golden path 通过, edge case 部分 → 第6维度 = 0.8
       │    │    └── golden path 失败 → 第6维度 = 0.3
       │    │
       │    └── 无 test_scenarios → 第6维度 = 0.3（扣分但不阻塞）
       │
       ├── 是 YAML？→ 执行三级 YAML 验证
       │    └── 引用有效性全通过 → 第6维度 = 1.0
       │
       ├── 是 Python？→ 执行 dry-run
       │    └── dry-run 通过 → 第6维度 = 0.8
       │
       └── 其他类型 → 跳过冒烟，第6维度 = 0.5（中性）
```

---

## 7. 实施路线图

### P1：已在执行（当前进行中）

| 工作项 | 状态 | 执行者 | 交付物 |
|--------|------|--------|--------|
| /capture Skill 根因分析 + 修复 | **完成** | harness_engineer | GATE 门禁 + 条件提交 + 验证步骤 |
| 全量 18 个 Skill 审计 + GATE 修复 | **完成** | integration_qa | 11 个 Skill 修复 |
| /qa-gate 升级增加 E2E 维度 | **进行中** | harness_engineer | qa-gate SKILL.md 第 6 维度 |
| skill-template.md 增加 test_scenarios 字段 | **完成** | knowledge_engineer | 模板规范 |

### P2：短期（test_scenarios 补充 + 冒烟测试流程化）

| 工作项 | 优先级 | 执行者 | 交付物 | 前置条件 |
|--------|--------|--------|--------|---------|
| 为 6 个 gate 级 Skill 编写 test_scenarios | 高 | harness_engineer | 每个 Skill 的 golden path + edge case | skill-template.md 已定义格式 |
| 实现 session_runner.py | 高 | ai_systems_dev | `agent-butler/test_runner/session_runner.py` | claude CLI 可用 |
| 实现 assertion_engine.py | 高 | ai_systems_dev | `agent-butler/test_runner/assertion_engine.py` | session_runner 完成 |
| 实现 scenario_loader.py | 中 | ai_systems_dev | `agent-butler/test_runner/scenario_loader.py` | test_scenarios 格式确定 |
| 实现 yaml_reference_validator.py | 中 | ai_systems_dev | `agent-butler/test_runner/yaml_validator.py` | YAML Schema 定义 |
| 冒烟测试集成到 /qa-gate | 高 | harness_engineer | qa-gate SKILL.md 更新 | session_runner + assertion_engine 完成 |
| 为 6 个 gate Skill 执行首次冒烟验证 | 高 | integration_qa | 首批测试结果 baseline | 全部上述完成 |

**P2 优先覆盖的 6 个 gate 级 Skill**：
1. `/capture` — 总裁高频使用
2. `/plan-day` — 每日必用
3. `/dispatch` — 核心流程
4. `/qa-gate` — 质量基础设施
5. `/synapse` — 会话启动
6. `/dev-review` — 代码审查

### P3：中期（自动化框架 + 健康监控）

| 工作项 | 优先级 | 执行者 | 交付物 | 前置条件 |
|--------|--------|--------|--------|---------|
| 实现 touchfiles.py 选择性测试 | 中 | ai_systems_dev | `agent-butler/test_runner/touchfiles.py` | P2 session_runner 完成 |
| 实现 regression.py 回归对比 | 中 | ai_systems_dev | `agent-butler/test_runner/regression.py` | 首批 baseline 生成 |
| 实现 health_monitor.py | 中 | ai_systems_dev | `agent-butler/health_monitor.py` | n8n 日志目录结构确认 |
| HTML 报告验证器 | 低 | ai_systems_dev | `agent-butler/test_runner/html_validator.py` | 无 |
| Harness 约束验证器 | 低 | ai_systems_dev | `agent-butler/test_runner/harness_validator.py` | 约束清单确认 |
| 健康监控 Agent 定时任务配置 | 中 | devops_engineer | Claude Scheduled Agent | health_monitor.py 完成 |
| Periodic 测试定时运行 | 中 | devops_engineer | Claude Scheduled Agent | touchfiles + 全量 test_scenarios |
| 为剩余 13 个 Skill 编写 test_scenarios | 低 | harness_engineer + 各 Skill owner | 全量覆盖 | 按使用频率排序 |
| Python 脚本 --dry-run 协议迁移 | 低 | ai_systems_dev | 所有 Python 脚本支持 --dry-run | 无 |

### 里程碑

```
P1（已在执行）──→ P2 完成 ──→ P3 完成
                    │            │
                    │            └── 全交付物质量覆盖
                    │                6 类交付物均有验证策略
                    │                自动化持续运行
                    │
                    └── Skill 冒烟测试可用
                        6 个 gate 级 Skill 有 E2E 测试
                        /qa-gate 第 6 维度自动评分
                        首批 baseline 建立
```

---

## 8. 风险与应对

| 风险 | 可能性 | 影响 | 应对策略 |
|------|--------|------|---------|
| **claude -p 冒烟测试成本过高** | 中 | 每次 gate 测试 >$1 导致常态化不可行 | gate 级严格限制 max_turns=10 + Sonnet 模型；成本超 $0.50 立即降级为 periodic |
| **冒烟测试非确定性（flaky）** | 高 | LLM 输出不稳定导致同一 Skill 时而通过时而失败 | 断言设计为"有序子序列"而非"完全匹配"；允许 2/3 通过率；flaky 测试自动降级为 periodic |
| **test_scenarios 维护负担** | 中 | 团队不愿为每个 Skill 编写测试场景 | Definition-First 软约束（不阻塞但 QA 扣分）；提供模板 + 自动生成建议 |
| **Session Runner 环境隔离不完整** | 低 | 冒烟测试在临时目录缺少必要依赖（如 MCP 服务） | 降级策略：MCP 不可用时跳过依赖 MCP 的场景，记录 warning 不记录 failure |
| **健康监控误报** | 中 | 正常维护期间触发告警打扰总裁 | 维护窗口配置：告警静默时段；P1/P2 不立即通知，汇总到日报 |
| **回归对比 baseline 过时** | 低 | 基线太旧导致对比无意义 | baseline 自动更新策略：全量通过时自动刷新 latest.json |

### 关键决策记录

| 决策 | 选项 | 选择 | 理由 |
|------|------|------|------|
| Session Runner 实现语言 | TypeScript (gstack 原生) vs Python | **Python** | 与 Synapse 现有代码库一致，降低维护成本 |
| 冒烟测试执行时机 | 内嵌到 /qa-gate vs 独立环节 | **独立环节 ②.5 + qa-gate 引用结果** | 冒烟失败应在 QA 之前拦截，避免 QA 浪费 |
| test_scenarios 格式 | YAML 嵌入 SKILL.md vs 独立 .yaml 文件 | **YAML 嵌入 SKILL.md** | 单文件维护，降低碎片化；scenario_loader 自动提取 |
| 非确定性测试处理 | 重试 N 次 vs 允许 2/3 通过率 | **允许 2/3 通过率** | 重试成本翻倍；2/3 通过率足够判断功能可用 |
| gate vs periodic 分级依据 | 按复杂度分 vs 按使用频率分 | **按使用频率 + 阻塞影响分** | 总裁高频使用的 Skill 必须 gate 级保障 |

---

## 附录 A：gstack 参考对照表

| Synapse 组件 | gstack 对应 | 文件路径 | 复用程度 |
|-------------|------------|---------|---------|
| session_runner.py | session-runner.ts | `_eval/gstack/test/helpers/session-runner.ts` | 核心逻辑复用，Python 重写 |
| assertion_engine.py | E2E test assertions | 各 `skill-e2e-*.test.ts` 中的 expect() | 概念复用，Synapse 专属实现 |
| scenario_loader.py | skill-parser.ts | `_eval/gstack/test/helpers/skill-parser.ts` | 概念复用 |
| touchfiles.py | touchfiles.ts | `_eval/gstack/test/helpers/touchfiles.ts` | 核心逻辑复用，Python 重写 |
| regression.py | eval-store.ts | `_eval/gstack/test/helpers/eval-store.ts` | 概念复用 |
| Two-Tier 分级 | E2E_TIERS | `_eval/gstack/test/helpers/touchfiles.ts` | 直接复用分级理念 |
| LLM-as-Judge（P3）| llm-judge.ts | `_eval/gstack/test/helpers/llm-judge.ts` | 待评估是否引入 |

## 附录 B：文件清单（完成后的目标状态）

```
agent-butler/
├── test_runner/                    # ★ 新增目录
│   ├── __init__.py
│   ├── session_runner.py          # Session Runner 核心
│   ├── scenario_loader.py         # test_scenarios 提取器
│   ├── assertion_engine.py        # 断言引擎
│   ├── touchfiles.py              # Diff-based 选择性测试
│   ├── regression.py              # 回归对比
│   ├── yaml_validator.py          # YAML 引用有效性校验
│   ├── html_validator.py          # HTML 报告验证
│   ├── harness_validator.py       # Harness 约束验证
│   └── smoke_router.py            # 按类型路由冒烟策略
├── health_monitor.py              # ★ 新增：后台健康监控
├── test_results/                   # ★ 新增目录
│   ├── runs/                      # 每次运行结果
│   ├── baselines/                 # 回归对比基线
│   └── history.jsonl              # 历史记录
├── config/
│   ├── yaml_schemas/              # ★ 新增目录：YAML Schema 定义
│   │   ├── organization.schema.json
│   │   ├── active_tasks.schema.json
│   │   └── n8n_integration.schema.json
│   └── harness_constraints.yaml   # ★ 新增：约束清单
└── ...

.claude/skills/
├── */SKILL.md                     # 每个 Skill 增加 test_scenarios 块
└── qa-gate/SKILL.md               # 升级：第 6 维度 + 冒烟结果引用

obs/03-process-knowledge/
├── quality-assurance-framework.md # ★ 本文档
└── skill-template.md              # 已更新：test_scenarios 规范
```
