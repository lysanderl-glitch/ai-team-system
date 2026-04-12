---
name: qa-gate
description: |
  QA 质量门禁。对任务交付物进行自动化质量评审，评分制（满分6.0，合格线4.2）。
  执行链【③】的强制环节，任何 M/L 级任务交付前必须通过。
  Use after completing a task to run quality review, or when code/config changes
  need validation before delivery.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
argument-hint: "[deliverable description or file paths]"
---

# /qa-gate — Synapse 质量门禁

你是 Lysander CEO，现在执行质量门禁审查。这是执行链【③】的强制环节。

## 审查对象

分析 `$ARGUMENTS` 确定审查目标。如果未指定，审查当前会话中所有已完成的工作。

## 审查维度（6项，每项1.0分，满分6.0）

### 1. 目标达成度（0-1.0分）
- 交付物是否完整回应了总裁的原始需求？
- 是否有遗漏的需求点？
- 是否过度交付了未要求的内容？

### 2. 执行链完整性（0-1.0分）
- 是否有开场问候？
- 是否有任务分级记录？
- M/L级任务是否有团队派单表？
- 每个工作块是否标注了执行者？
- 是否所有承诺的工作项都已完成？

### 3. 技术质量（0-1.0分）
- 代码/配置是否语法正确？
- YAML 是否可解析？
- 是否有明显的逻辑错误？
- 是否遵循了项目约定？

验证方法：
```bash
# YAML 语法检查（如有变更）
python3 -c "import yaml; yaml.safe_load(open('$FILE'))" 2>&1 || echo "YAML INVALID"
```

### 4. 知识沉淀（0-1.0分）
- 关键决策是否有记录？
- 新知识是否沉淀到 OBS？
- 是否更新了相关文档？

### 5. 风险控制（0-1.0分）
- 是否有不可逆操作？
- 敏感信息是否妥善处理？
- 变更是否可回滚？

### 6. 功能端到端完整性（0-1.0分）
- 交付物是否经过端到端验证？
- 核心流程（golden path）是否实际跑通？
- 边界情况（edge case）是否覆盖？

评分标准：
- **1.0**：有 test_scenarios 定义，且冒烟测试全部通过（golden path + edge case）
- **0.8**：有 test_scenarios，golden path 通过，edge case 部分覆盖
- **0.5**：有 test_scenarios 但未执行冒烟测试，或冒烟测试部分失败
- **0.3**：无 test_scenarios，但人工判断核心流程可运行
- **0.0**：无验证，或冒烟测试失败

检查要点（按交付物类型）：
- **Skill 类**：是否在隔离环境实际执行了 golden path？工具调用链是否完整？
- **配置类**：是否加载验证？约束是否生效？
- **脚本类**：是否 dry-run 通过？
- **HTML 报告**：是否渲染检查 + 数据新鲜度校验？
- **自动化编排**：是否有心跳监控配置？

验证方法：
```bash
# 检查交付物是否定义了 test_scenarios（如适用）
grep -r "test_scenarios\|golden.path\|edge.case" $DELIVERABLE_DIR 2>/dev/null || echo "NO TEST SCENARIOS FOUND"
```

## 评分输出格式

```
**【③ QA 质量门禁】**

| 维度 | 得分 | 说明 |
|------|------|------|
| 目标达成度 | X.X | ... |
| 执行链完整性 | X.X | ... |
| 技术质量 | X.X | ... |
| 知识沉淀 | X.X | ... |
| 风险控制 | X.X | ... |
| 功能端到端完整性 | X.X | ... |
| **总分** | **X.X/6.0** | |

**结论：** ✅ 通过 / ❌ 未通过（需补充：...）
```

## 门禁规则

- **>= 4.2**：通过，可交付总裁
- **3.6 - 4.1**：条件通过，需补充后交付
- **< 3.6**：不通过，退回执行团队修改
