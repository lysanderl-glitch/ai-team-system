import json, os

BASE = r"C:\Users\lysanderl_janusd\Claude Code\ai-team-system\scripts\_migration\templates"

# manifest data
manifest = {
    "exported_at": "2026-04-10",
    "source": "Notion Template Library (模板库)",
    "root_page_id": "33c3e99820c7818baa05d67851f33cd4",
    "folders": [],
    "pages": []
}

files = {}

# === ROOT PAGE ===
files["00_模板库根页面/模板库.md"] = """# 📚 模板库

Janusd 项目交付管理**全量标准模板库**，Notion 原生管理，覆盖项目全生命周期。所有模板均可在 Notion 中直接查阅使用，本地文件路径作为备份参考。

> **使用说明**：打开对应子页面查看模板内容；文档类模板可直接复制页面到项目空间使用；Excel 类工具在子页面中提供下载说明。

---

## 目录

- 🧪 **测试管理** — UAT/SIT 测试计划 · 测试用例模板 · 缺陷跟踪表
- 📝 **SOP 标准操作流程** — 项目启动 · 变更管理 · 项目验收

---

*最后更新：2026-04-08 | 由 Janusd PMO 维护*
"""

manifest["folders"].append({"name": "00_模板库根页面", "page_id": "33c3e99820c7818baa05d67851f33cd4", "title": "📚 模板库", "parent_id": None})

# === 模板使用指南 ===
files["01_模板使用指南/模板使用指南 Quick Start.md"] = r"""# 📖 模板使用指南 Quick Start

> 本指南适用于 Janusd 全体项目团队成员。阅读时间：**5 分钟**。

---

## 一、模板库概览

本模板库包含 **41+ 个**标准 PM 模板，按项目生命周期展开：

| 阶段 | 主要模板 | 谁使用 |
|------|----------|--------|
| 📁 00_售前 | 成本评估表、现场调研模板 | 售前团队 |
| 📁 01_项目启动 | 项目章程（自动生成）、干系人登记册 | PM |
| 📁 02_项目规划 | 策划总表、甘特图、WBS、风险册等 | PM |
| 📁 03_项目执行 | 施工日报、UAT测试用例、验收方案 | 工程师/测试工程师 |
| 📁 04_项目监控 | 周报、状态报告、变更请求表等 | PM |
| 📁 05_项目收尾 | 经验教训总结 | PM + 团队 |
| 💰 财务工具 | EVM仪表板、结算模板 | PM + 财务 |

---

## 二、模板使用流程

### 新项目启动对照清单

- [ ] 售前阶段：填写 JDG-PRE-LOG-002 **售前成本评估表**
- [ ] 客户签约后：销售在项目注册表填写客户信息，状态设为「已签约」
- [ ] WF-01 自动生成：**项目章程** + **Asana项目** + **Slack通知**
- [ ] PM填写 JDG-INI-ORG-002 **干系人登记册**
- [ ] PM完善 JDG-PLN-PLN-001 **项目策划总表**
- [ ] PM制定甘特图 JDG-PLN-PLN-005

### 每周循环操作

- [ ] 周一：填写 JDG-MON-STS-013 **项目周报**
- [ ] 周五：检查风险登记册 JDG-MON-RSK-015
- [ ] 如有变更：提交 JDG-MON-CHG-011 **变更请求表**
- [ ] 如有问题：记录到 JDG-MON-LOG-012 **问题日志**

### 每月监控

- [ ] 更新 JDG-MON-FIN-016 **成本监控台账**
- [ ] 发布 JDG-MON-STS-010 **项目状态报告**
- [ ] 更新 EVM 挣值管理仪表板

### 项目收尾

- [ ] 完成 JDG-ACP-RXD-001 **项目验收策划方案**
- [ ] 客户签署 JDG-CAR-RXD-001 **竣工验收报告**
- [ ] 结算核算：项目结算/利润核算模板
- [ ] 完成 JDG-CLO-RXD-001 **经验教训总结**

---

## 三、模板命名规范

```
JDG - [STAGE] - [TYPE] - [SEQ] _ 名称 _ 模板/项目具体 _ V版本号
```

| 阶段代码 | 含义 |
|----------|------|
| PRE | 售前 |
| INI | 项目启动 |
| PLN | 项目规划 |
| EXE | 项目执行 |
| MON | 项目监控 |
| CLO | 项目收尾 |
| ACP | 验收 |
| CAR | 竣工 |
| FIN | 财务 |

| 文件类型代码 | 含义 |
|-------------|------|
| CHG | 变更 |
| COM | 沟通 |
| FIN | 财务 |
| LOG | 日志/清单 |
| MTG | 会议 |
| ORG | 组织 |
| PLN | 计划 |
| PRO | 采购/协议 |
| QTY | 质量 |
| RES | 资源 |
| RSK | 风险 |
| RXD | 成果/报告 |
| SCP | 范围 |
| SPC | 方案 |
| STD | 标准 |
| STS | 状态报告 |
| TRN | 培训 |
| WBS | WBS |

---

## 四、自动化工具读取指南

| 自动化功能 | 操作方式 |
|-----------|----------|
| 项目章程自动生成 | 在项目注册表将状态改为「已签约」，WF-01 自动处理 |
| 周报自动生成 | 每周一 09:00 WF-04 自动推送至 Slack |
| 逐期预警 | 每日 09:00 WF-05 检查逐期任务自动报警 |
| 会议纪要自动化 | Fireflies 转录 + WF-07 自动生成行动项 |

---

## 五、常见问题

**Q: 模板更新了怎么办？**
A: 在对应模板页面编辑内容，更新模板页面顶部的版本号，通知 PMO。

**Q: 需要下载 Excel/Word 新版本怎么操作？**
A: 在模板页面底部查看本地文件路径，从对应目录获取。

**Q: 提交 CR 需要多久审批？**
A: C1 小变更 ≤ 1 天；C2 中变更 ≤ 3 天；C3 重大变更 ≤ 5 天（见 SOP-PM-02）。

**Q: 模板内容有错误/需要补充怎么办？**
A: 将 Notion 页面链接发到 Slack #pmo-templates 频道，@ PMO。

---

*版本：V1.0 | 发布日期：2026-04-08 | 维护人：Lysander | Janusd PMO*
"""

manifest["folders"].append({"name": "01_模板使用指南", "page_id": "33c3e99820c78198b76fd70530f27b2e", "title": "📖 模板使用指南 Quick Start", "parent_id": "33c3e99820c7818baa05d67851f33cd4"})
manifest["pages"].append({"file": "01_模板使用指南/模板使用指南 Quick Start.md", "page_id": "33c3e99820c78198b76fd70530f27b2e", "title": "📖 模板使用指南 Quick Start", "parent_id": "33c3e99820c7818baa05d67851f33cd4", "parent_title": "📚 模板库"})

print("Script structure created, writing remaining content...")
