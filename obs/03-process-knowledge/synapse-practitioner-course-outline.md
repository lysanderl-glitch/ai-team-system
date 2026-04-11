---
title: "Synapse Practitioner — Harness Engineering for AI Teams 课程大纲"
date: 2026-04-11
author: Training Designer + Strategist
tags: [Synapse, 培训, Harness Engineering, 课程设计, SCP认证]
description: 基于ADDIE模型设计的系统化培训课程，教授学员从零搭建AI Agent协作运营体系
---

# Synapse Practitioner 课程大纲

## 课程概述

| 项目 | 说明 |
|------|------|
| 课程名称 | Synapse Practitioner — Harness Engineering for AI Teams |
| 认证名称 | SCP（Synapse Certified Practitioner） |
| 目标学员 | 技术管理者、AI架构师、DevOps工程师、CTO/CIO |
| 课程形式 | 线上课程（4小时理论）+ 实操工作坊（4小时动手） |
| 前置要求 | 基本了解 AI/LLM 概念，有 Claude Code 或类似工具使用经验 |
| 交付成果 | 学员在课程结束时拥有一套可运行的 Synapse 体系（最小可用版） |

## 学习目标（基于Bloom认知分类法）

| 层级 | 目标 |
|------|------|
| **记忆** | 能说出 Harness Engineering 的核心公式和两大机制 |
| **理解** | 能解释 Guides 和 Sensors 的区别及协作关系 |
| **应用** | 能编写 CLAUDE.md 配置和 organization.yaml |
| **分析** | 能诊断一个现有 AI 体系的 Harness 缺陷 |
| **评估** | 能使用审计引擎评估 Agent 团队质量并提出改进建议 |
| **创造** | 能独立设计一个完整的 Multi-Agent Synapse 体系 |

---

## 课程结构（8小时，2个半天）

### Part 1：理论篇（4小时）

#### Module 1：为什么需要 Harness Engineering（45分钟）

**内容**：
- AI Agent 的现状：能力很强但不可控
- 真实案例：写了规则但没人遵守（对话实录展示）
- 行业共识：Agent = Model + Harness
- Martin Fowler / Red Hat / Anthropic 的观点解读

**教学方法**：案例导入 + 概念讲解

**核心产出**：学员理解"模型不是壁垒，Harness才是"

---

#### Module 2：Harness 的两大核心机制（60分钟）

**内容**：

**2.1 Guides（前馈控制）— 让AI做正确的事**
- CLAUDE.md：角色、规则、流程的配置文件
- organization.yaml：组织架构、路由规则
- decision_rules.yaml：决策约束体系
- HR/personnel/*.md：Agent 能力档案

**2.2 Sensors（反馈控制）— 检查AI是否做对了**
- QA自动评分：qa_auto_review()
- 执行链检查：execution_chain_check()
- 专家评审团：expert_panel_review()
- 决策日志：decision_log.json

**2.3 实战教训：Guide有了Sensor没有**
- 展示三次违规的对话实录
- 强制团队派单制度的诞生过程

**教学方法**：概念讲解 + 真实对话案例分析

---

#### Module 3：四级决策体系设计（45分钟）

**内容**：
- L1 自动执行：什么事情不需要人判断
- L2 专家评审：为什么专家要先于管理者
- L3 管理决策：CEO如何基于专家建议做判断
- L4 高管决策：什么情况才升级到最高层
- 真实纠错案例：总裁如何发现L2/L3顺序错误

**教学方法**：框架讲解 + 互动讨论（让学员设计自己公司的四级制）

---

#### Module 4：Agent HR 管理体系（45分钟）

**内容**：
- 为什么Agent也需要HR管理（审计0分的震撼案例）
- 强制Schema：Agent卡片必须包含什么
- 能力质量分级：A/B/C三级标准及示例
- 入职审批流程：8项检查清单
- 定期审计：自动化评分引擎

**真实数据展示**：从64.1分到93.8分的四轮整治过程

**教学方法**：案例讲解 + 现场审计演示

---

#### Module 5：情报闭环与自动化编排（45分钟）

**内容**：
- 每日情报管线：搜索→筛选→分析→报告
- 情报行动管线：提取→评估→评审→执行→报告
- 4专家评分制：评审规则和一票否决机制
- 自动化编排：5个定时任务的事件链设计
- 如何让AI团队自己学习和进化

**教学方法**：流程讲解 + 评审评分现场演示

---

### Part 2：实操工作坊（4小时）

#### Lab 1：搭建你的 Harness Configuration（60分钟）

**目标**：学员编写自己公司的 CLAUDE.md

**步骤**：
1. 定义角色体系（谁是老板、谁是CEO、谁是执行者）
2. 设计执行链流程（至少3个环节）
3. 配置决策规则（四级制映射到自己公司的场景）
4. 设置强制检查点（Guide + Sensor各至少1个）

**交付物**：一份可运行的 CLAUDE.md

---

#### Lab 2：创建你的AI团队（60分钟）

**目标**：学员创建 organization.yaml + 至少3个Agent卡片

**步骤**：
1. 设计团队架构（智囊团 + 执行团队）
2. 编写3个Agent的人员卡片（符合强制Schema）
3. 确保能力描述达到B级以上
4. 配置路由关键词

**质量门禁**：使用审计引擎评分，低于90分不通过

---

#### Lab 3：构建你的情报管线（60分钟）

**目标**：学员配置一个可运行的每日情报系统

**步骤**：
1. 设计情报搜索范围（针对自己的行业）
2. 定义筛选标准（什么对你有价值）
3. 配置报告模板
4. 设置定时任务

**交付物**：一个首期情报日报

---

#### Lab 4：综合演练 + 答辩（60分钟）

**目标**：学员展示自己的完整 Synapse 体系

**流程**：
1. 每组5分钟展示自己的体系设计
2. 讲师和其他学员提问
3. 使用审计引擎评分
4. 反馈和改进建议

---

## SCP 认证评估标准

| 评估维度 | 权重 | 通过标准 |
|----------|:----:|----------|
| CLAUDE.md 配置完整性 | 25% | 包含角色/执行链/决策规则/强制检查点 |
| Agent 卡片质量 | 25% | 审计引擎评分≥90 |
| 决策体系合理性 | 20% | 四级制清晰，L2专家先于L3管理 |
| 情报管线可运行 | 15% | 能生成首期报告 |
| 答辩表现 | 15% | 能解释设计决策的理由 |

**通过标准**：总分≥80分获得 SCP 认证

---

## 课程定价

| 形式 | 定价 | 包含 |
|------|------|------|
| 个人线上课程 | $500/人 | 理论课 + 实操Lab + SCP认证考试 |
| 企业内训（≤20人） | $10,000/场 | 定制化内容 + 现场Workshop + 团队SCP认证 |
| 企业内训（≤50人） | $15,000/场 | 同上 + 后续1个月咨询支持 |

---

## 课程素材清单（已有）

| 素材 | 来源 | 状态 |
|------|------|:----:|
| Synapse 完整案例（今天的对话） | 实践过程 | ✅ |
| Harness Engineering 方法论文档 | obs/03-process-knowledge/ | ✅ |
| Agent HR 管理体系文档 | obs/03-process-knowledge/ | ✅ |
| 15页分享PPT | obs/generated-articles/ | ✅ |
| hr_base.py 审计引擎 | agent-butler/ | ✅ |
| 情报日报实例 | obs/daily-intelligence/ | ✅ |
| 行动成果报告实例 | obs/daily-intelligence/ | ✅ |
| 组织架构模板 | agent-butler/config/ | ✅ |

所有核心素材已在今天的实践中产出，课程开发无需从零开始。
