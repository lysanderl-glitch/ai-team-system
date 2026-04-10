# 🏠 PMO Command Center

> **Page ID:** 33d3e99820c781d68099d52516c66caa
> **Parent:** 📊 PMO自动化管理体系

---

> **Janusd 项目管理指挥中心** — 实时掌握所有项目健康状态、资源负载、风险预警
> 更新频率：WF-05 每日推送 · WF-04 每周汇总 · PM 实时维护

---

## 📊 项目组合总览

> 使用下方嵌入的项目注册表「📊 项目看板」视图查看实时状态

[📁 项目注册表（看板视图）](https://www.notion.so/33c3e99820c781fcac6fc8a54e6e8ad6)

**快速操作：**
- 新建项目 → 销售填写注册表（状态选「售前中」）
- 签约触发 → 将状态改为「已签约」→ WF-01 自动初始化（5分钟内）
- 每周更新 → PM更新「健康度」「进度%」「当前里程碑」「风险摘要」

---

## 🚦 本周健康状态速览

| 颜色 | 含义 | 行动要求 |
|------|------|----------|
| 🟢 绿色 | 按计划推进，无重大风险 | 正常跟进 |
| 🟡 黄色 | 存在偏差或风险，需关注 | PM提出缓解方案，本周内解决 |
| 🔴 红色 | 严重偏差或高风险，需升级 | 立即上报，24小时内制定应对方案 |

> 🔴 高风险项目视图：[点击查看](https://www.notion.so/33c3e99820c781fcac6fc8a54e6e8ad6)

---

## ⚙️ 自动化工作流状态面板

| WF编号 | 名称 | 触发 | 状态 | 最近执行 |
|--------|------|------|------|----------|
| WF-01 | 项目初始化 | 注册表状态→已签约 | ✅ 运行中 | Exec 229（2026-04-08） |
| WF-02 | 任务变更通知 | Asana Webhook | 🔧 配置中 | — |
| WF-03 | 里程碑提醒 | 定时轮询 | 🔧 配置中 | — |
| WF-04 | 周报自动化 | 每周一 09:00 | ✅ 运行中 | Exec 169 |
| WF-05 | 逾期预警 | 每日 09:00 | ✅ 运行中 | Exec 197 |
| WF-07 | 会议纪要→任务 | Fireflies轮询 | ✅ 运行中 | Exec 202 |

---

## 📈 关键指标追踪

### 本季度目标（Q2 2026）

| 指标 | 目标 | 当前 | 状态 |
|------|------|------|------|
| PM体系评分 | ≥ 8.5/10 | 8.2/10 | 🟡 进行中 |
| WF自动化覆盖 | 6个WF上线 | 6/6 全部运行 | 🟡 进行中 |
| Notion模板库 | 41+模板 | 41+已创建 | 🟢 完成 |
| 团队成员启用 | ≥3人 | 1人（Lysander） | 🔴 待推进 |
| PM Handbook | V1.0发布 | V1.0 已发布 | 🟡 进行中 |

---

## 📋 本周行动项（PMO）

> 每周一由 WF-04 自动生成后，PM手动填写本节

- [x] WF-07 行动项归属修复（2026-04-09）
- [ ] 项目注册表权限开放给销售团队
- [ ] PPT模板手动上传至Notion（3个文件）
- [x] WF-02/WF-03 部署完成（2026-04-09）
- [x] Slack Q&A助手MVP上线（2026-04-09）

---

## 🛠️ PMO自动化工具链

| 工具 | 用途 | 调用方式 |
|------|------|----------|
| project_space_init.py | 新项目Notion空间自动生成 | CLI / n8n WF-01 |
| asana_notion_sync.py | Asana→Notion进度同步 | CLI / n8n WF-04/05 |
| wbs_formula_check.py | L3↔L4工期一致性校验（含并行组） | CLI |
| wbs_dependency_check.py | 跨流依赖完整性校验 | CLI |
| wbs_critical_path.py | 关键路径自动识别（6并行流） | CLI |
| wbs_role_workload.py | 角色负载均衡分析 | CLI |
| ai_deliverable_gen.py | AI交付物自动生成(G0-G5全18模板) | CLI / 阶段门触发 |
| ai_risk_warning.py | AI风险预警(工期/依赖/资源/复杂度) | CLI / n8n定时 |
| pmo_knowledge_loop.py | PMO知识库闭环(经验教训沉淀) | CLI / 复盘触发 |

---

## 🔗 快速导航

| 资源 | 链接 |
|------|------|
| 📁 项目注册表（全量） | [查看](https://www.notion.so/33c3e99820c781fcac6fc8a54e6e8ad6) |
| 🚦 阶段门检查清单 G0-G5 | [查看](https://www.notion.so/8f61420ca15148c092c13f67b89f6029) |
| 📚 Notion模板库 | [查看](https://www.notion.so/33c3e99820c7818baa05d67851f33cd4) |
| 🗺️ AI使用路线图 | [查看](https://www.notion.so/32e3e99820c781d2bdfdea9cfe3d8f36) |
| 📊 PM体系评估报告 | [8.2/10](https://www.notion.so/33c3e99820c781e2869cfeda9397d20a) |
| 🤖 n8n工作流管理台 | [n8n.lysander.bond](https://n8n.lysander.bond) |
| 📊 PMO周报数据库 | [查看](https://www.notion.so/2c3a7590d03b482abcf1c70ecf11c852) |
| 🚨 逾期预警日志 | [查看](https://www.notion.so/f5cf12cfb6b64664b5ce5fa3956b7174) |

---

*Command Center 建立于 2026-04-09 | Claude × Lysander 协作*

<!-- Embedded database: 📋 WBS工序数据库 Work Breakdown Structure -->
<!-- Database URL: https://www.notion.so/6714567e05f5437bad4b726202ecbb6e -->
<!-- Data source: collection://d8b55188-995b-4a5f-b257-60074438fd5b -->
