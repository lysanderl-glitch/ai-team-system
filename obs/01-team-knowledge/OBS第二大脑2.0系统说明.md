---
title: OBS第二大脑2.0系统说明
category: 系统架构
tags: [OBS, 第二大脑, Software2.0, Graphify]
created: 2026-04-08
author: Lysander
version: 1.0
type: 文档
---

# OBS第二大脑2.0

## 系统定位

基于Karpathy Software 2.0理念和Graphify策略构建的AI增强知识管理系统。

## 核心理念

### Software 2.0 vs Software 1.0

| 维度 | Software 1.0（传统） | Software 2.0（AI增强） |
|------|---------------------|----------------------|
| 标签管理 | 人工定义 | AI从使用模式学习 |
| 链接创建 | 手动[[双向链接]] | AI发现隐性关联 |
| 知识组织 | 预设文件夹结构 | AI发现使用模式动态优化 |
| 搜索发现 | 精确关键词匹配 | 语义搜索 |

### Graphify三层架构

```
Layer 3: Emergent Knowledge (涌现知识)
  └─ AI从交互模式中发现的新关联

Layer 2: AI Discovery (AI发现层)
  └─ 隐性关联识别、语义嵌入、关系发现

Layer 1: Human Editing (人工编辑层)
  └─ 传统笔记、标签、手动链接
```

## 知识分类

- `01-team-knowledge` - 团队知识
- `02-project-knowledge` - 项目知识
- `03-process-knowledge` - 流程知识
- `04-decision-knowledge` - 决策知识
- `05-industry-knowledge` - 行业知识

## 自动化工作流

1. **OBS Knowledge Intake** - 每日新笔记扫描
2. **OBS Second Brain 2.0 Orchestrator** - 周健康报告

## 使用指南

1. 在对应分类目录下创建.md笔记
2. 使用YAML front matter添加元数据
3. 使用`[[双向链接]]`建立知识关联
4. AI将自动发现潜在关联并建议

## 相关知识

- [[知识沉淀流程]]
- [[知识检索方案]]
- [[质量标准体系]]
