---
title: 人力资源知识库
description: 公司AI Agent团队、人员、岗位、能力管理体系
type: HR-index
version: "1.0"
created: 2026-04-09
---

# 人力资源知识库

公司AI Agent团队、人员、岗位、能力管理的核心知识库。OBS作为单一数据源，为Lysander CEO提供团队召唤能力。

## 重要说明

**全员AI团队**：所有团队成员均为AI Agent，由总裁刘子杨通过Lysander(AI CEO)统一管理。

---

## 团队架构

```
┌─────────────────────────────────────────────────────────────┐
│                  总裁 刘子杨 (最高决策者)                     │
│                    ↓ Lysander (AI CEO)                       │
└─────────────────────────────────────────────────────────────┘
                              ↑
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ↓                    ↓                    ↓
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Butler团队    │    │ RD团队        │    │ Graphify智囊团 │
│ (7 AI Agents) │    │ (5 AI Agents) │    │ (4 AI Agents) │
├───────────────┤    ├───────────────┤    ├───────────────┤
│ delivery_expert│   │ tech_lead    │    │ strategist    │
│ training_expert│   │ backend_dev  │    │ relation_discov│
│ pmo_expert    │    │ frontend_dev │    │ trend_watcher │
│ iot_expert    │    │ devops_eng   │    │ decision_adviso│
│ digital_modeling│   │ qa_engineer  │    └───────────────┘
│ iot_data_expert│   └───────────────┘            ↑
│ uat_test_expert│           ↑                  │ 深度分析
└───────────────┘            │ 执行层         ┌───────────────┐
         ↑                   └─────────────→  │ OBS知识团队  │
         │                                       │ (4 AI Agents) │
┌───────────────┐    ┌───────────────┐    ├───────────────┤
│Content_ops团队│    │ 协同层        │    │obs_architecture│
│ (4 AI Agents) │    │              │    │knowledge_chandu│
├───────────────┤    └───────────────┘    │knowledge_search│
│content_strateg│               ↑         │knowledge_quality│
│content_creator│               │         └───────────────┘
│visual_designer│               │              ↑
│publishing_ops │               └──────────────┘
└───────────────┘                         知识层
         ↑
┌───────────────┐
│ Stock项目团队  │  ★独立项目团队
│ (5 AI Agents) │
├───────────────┤
│project_manager│
│trader        │
│quant_research│
│frontend_dev  │
│backend_dev   │
└───────────────┘
```

---

## 目录结构

```
HR/
├── personnel/           # 人员档案库
│   ├── lysander/       # CEO (人类)
│   ├── butler/         # Butler团队 (7 AI Agents)
│   ├── rd/            # 研发团队 (5 AI Agents)
│   ├── graphify/       # Graphify智囊团 (4 AI Agents)
│   ├── stock/          # 股票交易系统项目 (5 AI Agents) ★新增
│   ├── obs/            # OBS知识管理团队 (4 AI Agents)
│   └── content_ops/    # 内容运营团队 (4 AI Agents)
└── positions/          # 岗位定义库
    ├── lysander/
    ├── rd/
    └── graphify/
```

## 团队概览

| 团队 | 成员数 | 定位 | 服务对象 |
|------|--------|------|----------|
| lysander | 1 | AI CEO | 总裁刘子杨 |
| **graphify** | **5** | **智慧层/第二大脑+执行审计** | **Lysander + 总裁刘子杨** |
| **stock** | **5** | **独立项目** | **股票交易系统** |
| butler | 7 | 执行层 | 业务交付 |
| rd | 5 | 执行层 | 技术研发 |
| obs | 4 | 知识层 | 知识管理 |
| content_ops | 4 | 执行层 | 内容运营 |

---

## Graphify智囊团

Graphify是**第二大脑核心引擎**，直接服务于Lysander CEO和总裁刘子杨。

### 核心定位

```
┌─────────────────────────────────────────────────────────────┐
│                    Graphify 智囊团                          │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ 战略分析师  │  │ 关联发现专家 │  │ 趋势洞察师  │        │
│  │strategist  │  │relation_disc│  │trend_watcher│        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                              │
│  ┌─────────────┐                                            │
│  │ 决策顾问    │                                            │
│  │decision_adv │                                            │
│  └─────────────┘                                            │
│                                                              │
│  核心能力：                                                 │
│  ✦ 深度分析 - 从现象看本质                                  │
│  ✦ 关联发现 - 找到隐性知识连接 (Graphify核心)               │
│  ✦ 趋势洞察 - 发现模式预测未来                              │
│  ✦ 决策支持 - 量化利弊给出建议                             │
└─────────────────────────────────────────────────────────────┘
```

### 与Lysander的协同

```
你 → Graphify: "帮我分析这个项目有什么风险"
         ↓
Graphify → 战略分析 + 关联发现 + 趋势洞察
         ↓
你 ← Graphify: 完整分析报告 + 决策建议
```

### 与OBS的协同

```
Graphify ← OBS知识库
    │ (读取历史知识)
    │ (构建知识图谱)
    │ (发现隐性关联)
    ↓
用户洞察 ← 分析结果
```

---

## 召唤规则

| 任务关键词 | 路由团队 | 路由专家 |
|-----------|----------|----------|
| 分析、洞察 | graphify | - |
| 战略、规划 | graphify | strategist |
| 关联、图谱 | graphify | relation_discovery |
| 趋势、预测 | graphify | trend_watcher |
| 决策、建议 | graphify | decision_advisor |
| 股票、炒股 | stock | - |
| 交易、持仓、止损 | stock | trader |
| 量化、指标 | stock | quant_researcher |
| 交付、项目、IoT | butler | - |
| 知识库、OBS | obs | - |
| 内容、博客、微信 | content_ops | - |
| 研发、开发、架构 | rd | - |

---

## 专家调用流程

```
用户需求
    ↓
Lysander接收 → 分析 → 路由到对应团队
    ↓
┌─────────────────────────────────────┐
│ 执行层：Butler / RD / Content_ops    │
│ 智慧层：Graphify（深度分析洞察）      │
│ 知识层：OBS（知识存储检索）           │
│ 项目层：Stock（独立项目团队）         │
└─────────────────────────────────────┘
    ↓
结果汇报 → Lysander汇总 → 用户
```

---

## Stock股票交易系统项目

Stock是**独立项目团队**，专注股票交易系统开发，不并入RD团队。

### 项目概述

股票交易系统（趋势智选）- A股趋势交易指导系统，基于《炒股的智慧》策略。

### 技术栈

- 后端：FastAPI + SQLAlchemy + SQLite
- 前端：Vue3 + Pinia + Element Plus
- 数据：Baostock API

### 系统URL

- 系统：http://stock.lysander.bond/
- 后端API：http://localhost:8000/docs

### 核心功能

| 模块 | 功能 |
|-----|------|
| 回测 | 历史信号回测分析 |
| 模拟交易 | 100万资金模拟实盘 |
| 仓位策略 | 《炒股的智慧》分阶段建仓 |
| 知识库 | 书籍核心知识录入 |
| 自动化 | 每日自动选股 |
| 止损监控 | 动态止损管理 |
| 趋势过滤 | MA20/MA60趋势判断 |

---

## 更新日志

- 2026-04-09: 新增Stock股票交易系统项目团队
