"""
AI交付物自动生成脚本
基于WBS阶段门和项目信息，在Notion中自动创建对应阶段的交付物模板初稿。
支持按阶段门批量生成或单独生成指定交付物。

调用方式：
  python ai_deliverable_gen.py --project "项目名称" --gate G2 [--all]
  n8n: 阶段门通过后自动触发

由 janus_pmo_auto 负责运维
"""
import sys
import io
import os
import json
import argparse
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import requests
except ImportError:
    print("需要安装 requests: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 阶段门→交付物映射定义
# ---------------------------------------------------------------------------

GATE_DELIVERABLES = {
    "G0": [
        {
            "code": "DEL-G0-001",
            "name": "项目章程",
            "template": "project_charter",
            "role": "PM",
            "auto": True,
            "description": "由WF-01自动生成初稿，PM审核后发布",
        },
        {
            "code": "DEL-G0-002",
            "name": "干系人登记册",
            "template": "stakeholder_register",
            "role": "PM",
            "auto": False,
            "description": "识别项目关键干系人及其影响力/利益矩阵",
        },
    ],
    "G1": [
        {
            "code": "DEL-G1-001",
            "name": "售前→交付移交清单",
            "template": "handover_checklist",
            "role": "SA",
            "auto": False,
            "description": "售前团队向交付团队移交的完整信息清单",
        },
        {
            "code": "DEL-G1-002",
            "name": "风险评估报告",
            "template": "risk_assessment",
            "role": "PM",
            "auto": True,
            "description": "基于合同范围和客户情况的初始风险评估",
        },
    ],
    "G2": [
        {
            "code": "DEL-G2-001",
            "name": "项目管理综合策划书",
            "template": "management_plan",
            "role": "PM",
            "auto": True,
            "description": "涵盖范围、进度、质量、风险、沟通、采购的综合管理策划",
        },
        {
            "code": "DEL-G2-002",
            "name": "数字化交付策划",
            "template": "digital_delivery_plan",
            "role": "DE",
            "auto": True,
            "description": "图纸整理计划、建模方案、IoT绑点策略",
        },
        {
            "code": "DEL-G2-003",
            "name": "业务调研策划",
            "template": "business_survey_plan",
            "role": "CDE",
            "auto": True,
            "description": "6大业务领域调研计划和时间安排",
        },
        {
            "code": "DEL-G2-004",
            "name": "启动会PPT",
            "template": "kickoff_ppt",
            "role": "PM",
            "auto": False,
            "description": "外部启动会演示材料",
        },
    ],
    "G3": [
        {
            "code": "DEL-G3-001",
            "name": "施工方案",
            "template": "construction_plan",
            "role": "PM",
            "auto": True,
            "description": "现场施工方案，含设备安装、布线、调试计划",
        },
        {
            "code": "DEL-G3-002",
            "name": "业务调研报告",
            "template": "business_survey_report",
            "role": "CDE",
            "auto": True,
            "description": "6大业务领域调研成果汇总",
        },
        {
            "code": "DEL-G3-003",
            "name": "数字化内验报告",
            "template": "digital_validation",
            "role": "DE",
            "auto": True,
            "description": "静态/动态数字化交付的内部验收报告",
        },
    ],
    "G4": [
        {
            "code": "DEL-G4-001",
            "name": "UAT测试报告",
            "template": "uat_report",
            "role": "QA",
            "auto": True,
            "description": "UAT测试方案、用例执行结果、缺陷统计",
        },
        {
            "code": "DEL-G4-002",
            "name": "培训材料及执行记录",
            "template": "training_materials",
            "role": "CDE",
            "auto": False,
            "description": "培训PPT、操作手册、培训签到表",
        },
        {
            "code": "DEL-G4-003",
            "name": "试运行方案",
            "template": "trial_run_plan",
            "role": "PM",
            "auto": True,
            "description": "试运行目标、范围、评估标准、问题处理流程",
        },
        {
            "code": "DEL-G4-004",
            "name": "验收报告",
            "template": "acceptance_report",
            "role": "PM",
            "auto": True,
            "description": "项目交付验收报告，含交付成果清单和客户签字区",
        },
    ],
    "G5": [
        {
            "code": "DEL-G5-001",
            "name": "运维交接清单",
            "template": "ops_handover",
            "role": "PM",
            "auto": True,
            "description": "系统账号、文档、知识库、SLA协议的完整交接清单",
        },
        {
            "code": "DEL-G5-002",
            "name": "项目复盘报告",
            "template": "retrospective",
            "role": "PM",
            "auto": True,
            "description": "项目经验教训总结，含成功因素和改进建议",
        },
        {
            "code": "DEL-G5-003",
            "name": "价值分析报告",
            "template": "value_analysis",
            "role": "CDE",
            "auto": True,
            "description": "项目交付价值量化分析（能耗节省、效率提升等）",
        },
    ],
}

# ---------------------------------------------------------------------------
# 交付物模板内容生成
# ---------------------------------------------------------------------------

TEMPLATE_GENERATORS = {
    "project_charter": lambda ctx: f"""## 项目章程 — {ctx['project']}

### 1. 项目概述
- **项目名称**: {ctx['project']}
- **项目经理**: {ctx.get('pm', '待定')}
- **创建日期**: {ctx['date']}

### 2. 项目背景与目标
> 请在此描述项目背景、业务目标和预期成果

### 3. 项目范围
#### 3.1 范围内
- 待填写

#### 3.2 范围外
- 待填写

### 4. 关键里程碑
| 里程碑 | 目标日期 | 负责人 |
|--------|----------|--------|
| G1 售前评审 | - | PM+Sales |
| G2 策划完成 | - | PM |
| G3 执行准备 | - | PM+SA |
| G4 交付验收 | - | PM+CDE |
| G5 运维交接 | - | PM |

### 5. 项目团队
| 角色 | 人员 | 职责 |
|------|------|------|
| PM | {ctx.get('pm', '-')} | 项目全生命周期管控 |
| DE | - | 数字化交付 |
| SA | - | 技术方案 |
| CDE | - | 业务咨询交付 |

### 6. 风险与假设
> 待项目启动后补充

---
*由 Janus PMO 自动化系统生成 | {ctx['date']}*
""",

    "risk_assessment": lambda ctx: f"""## 风险评估报告 — {ctx['project']}

### 评估信息
- **项目**: {ctx['project']}
- **评估人**: {ctx.get('pm', '待定')}
- **评估日期**: {ctx['date']}

### 风险登记表
| 编号 | 风险描述 | 类别 | 影响 | 概率 | 等级 | 应对措施 | 责任人 | 状态 |
|------|----------|------|------|------|------|----------|--------|------|
| R001 | 客户需求变更频繁 | 范围 | 高 | 中 | 🟡 | 变更管理流程 | PM | 监控中 |
| R002 | 关键资源不足 | 资源 | 高 | 低 | 🟢 | 提前规划备选 | PM | 监控中 |
| R003 | 第三方系统集成延迟 | 技术 | 中 | 中 | 🟡 | 预留缓冲时间 | SA | 监控中 |
| R004 | 现场施工条件不满足 | 外部 | 高 | 低 | 🟢 | 提前勘察确认 | PM | 监控中 |
| R005 | IoT设备兼容性问题 | 技术 | 中 | 中 | 🟡 | 协议预测试 | DE | 监控中 |

### 风险矩阵
```
影响↑  高 | 🟢R002  🟡R001  🔴___
      中 | 🟢___   🟡R003  🟡___
      低 | 🟢___   🟢___   🟢___
         ─────────────────────→ 概率
           低       中       高
```

### 风险应对策略
> 请根据实际项目情况更新上述风险项

---
*由 Janus PMO 自动化系统生成 | {ctx['date']}*
""",

    "management_plan": lambda ctx: f"""## 项目管理综合策划书 — {ctx['project']}

### 文档信息
| 项目 | {ctx['project']} |
|------|------|
| 编制人 | {ctx.get('pm', '-')} |
| 日期 | {ctx['date']} |
| 版本 | V1.0 |

### 1. 范围管理
#### 1.1 WBS工作分解
- 参考WBS主表（Excel/Asana）
- 4级分解：阶段(L1) → 类别(L2) → 任务(L3) → 子任务(L4)
- 6条并行执行流

#### 1.2 范围变更控制
- 变更申请 → PM评估 → 客户确认 → 执行 → 验证

### 2. 进度管理
- 工具：Asana（任务跟踪）+ Notion（进度看板）
- 关键路径：DS(静态数字化) → DY(动态数字化) → DI(业务初始化)
- 逾期预警：WF-05每日自动检查

### 3. 质量管理
- 内验标准：10%随机抽验，100%合格率
- 阶段门评审：G0-G5共6个检查点
- UAT标准：P0问题清零，P1/P2有解决计划

### 4. 风险管理
- 风险识别：项目启动时全量评估
- 风险监控：每周例会review
- 风险预警：AI自动分析（ai_risk_warning.py）

### 5. 沟通管理
| 沟通方式 | 频率 | 参与者 | 工具 |
|----------|------|--------|------|
| 项目周会 | 每周 | 全团队 | Teams/Zoom |
| 进度报告 | 每周 | PM→客户 | WF-04自动生成 |
| 逾期预警 | 每日 | PM | WF-05 Slack推送 |
| 阶段门评审 | 按需 | PM+相关角色 | Notion检查清单 |

### 6. 采购管理
> 请根据项目实际填写硬件/软件/服务采购计划

---
*由 Janus PMO 自动化系统生成 | {ctx['date']}*
""",

    "digital_delivery_plan": lambda ctx: f"""## 数字化交付策划 — {ctx['project']}

### 1. 图纸整理计划
| 项目 | 说明 |
|------|------|
| 图纸来源 | 待收资确认 |
| 整理标准 | 按楼层/系统分类，统一命名 |
| 预计工期 | 参考WBS DA003 |

### 2. BIM建模方案
#### 2.1 土建建模 (DS001)
- 建模范围：待确认
- 建模标准：LOD 300
- 核查标准：空间对象数量自检

#### 2.2 机电建模 (DS004)
- 建模范围：HVAC/电气/给排水
- 与土建并行执行

#### 2.3 外立面视觉模型 (DS007, 按需)
- 是否需要：待确认

### 3. 台账管理方案
- 空间台账：Notion DB (JDG-INI-DAT-004)
- 设备台账：Notion DB (JDG-INI-DAT-005)
- IoT点位清单：Notion DB (JDG-INI-DAT-006)

### 4. IoT绑点策略
- 协议测试 (DY002)：预留15天
- 数据绑点 (DY004)：依赖DS005完成
- OPS数据核查 (DY005)：表底数连续性、负载能耗偏差

### 5. 质量内验标准
- 每系统随机抽验10%对象关系
- 合格率要求：100%
- OPS数据：连续性、负载能耗偏差≤5%

---
*由 Janus PMO 自动化系统生成 | {ctx['date']}*
""",

    "business_survey_plan": lambda ctx: f"""## 业务调研策划 — {ctx['project']}

### 调研范围（6大领域）

| 序号 | 领域 | WBS编码 | 负责人 | 关键产出 |
|------|------|---------|--------|----------|
| 1 | 基础调研 | DB001 | CDE | 客户组织架构、业务流程 |
| 2 | 资产管理 | DB002 | CDE | 设备/空间分类树、台账表头 |
| 3 | 资产风险 | DB003 | CDE | 报警规则、工单流程、响应时长 |
| 4 | 自主运行 | DB004 | CDE | 系统图、工作历 |
| 5 | 能源与碳 | DB005 | CDE | 电价、能耗预算、碳核算方式 |
| 6 | 综合数据 | DB006 | CDE | 合规报表、IoT分析模板 |

### 调研方法
- 访谈：客户关键干系人一对一
- 文档：收集客户现有管理制度和规范
- 现场：设备和系统实地调研

### 产出物
- 各领域调研记录表
- 关键材料签确清单 (DB007)
- 业务需求规格说明书

---
*由 Janus PMO 自动化系统生成 | {ctx['date']}*
""",

    "uat_report": lambda ctx: f"""## UAT测试报告 — {ctx['project']}

### 测试概况
| 项目 | 值 |
|------|------|
| 项目名称 | {ctx['project']} |
| 测试周期 | 待填写 |
| 测试负责人 | QA |
| 报告日期 | {ctx['date']} |

### 测试结果汇总
| 指标 | 数值 |
|------|------|
| 测试用例总数 | - |
| 通过 | - |
| 失败 | - |
| 阻塞 | - |
| 通过率 | - |

### 缺陷统计
| 等级 | 数量 | 已关闭 | 未关闭 |
|------|------|--------|--------|
| P0 致命 | - | - | - |
| P1 严重 | - | - | - |
| P2 一般 | - | - | - |
| P3 轻微 | - | - | - |

### 测试结论
> 待测试完成后填写

### 遗留问题
> P0必须清零方可通过G4阶段门

---
*由 Janus PMO 自动化系统生成 | {ctx['date']}*
""",

    "trial_run_plan": lambda ctx: f"""## 试运行方案 — {ctx['project']}

### 1. 试运行目标
- 验证系统在实际业务场景下的稳定性
- 收集用户使用反馈
- 建立运维知识库

### 2. 试运行范围
> 待填写具体系统和业务模块

### 3. 试运行周期
- 计划工期：40天（参考WBS DU003）
- 问题跟进：并行处理

### 4. 评估标准
| 维度 | 标准 | 达标条件 |
|------|------|----------|
| 系统稳定性 | 可用率 | ≥99% |
| 数据准确性 | 偏差率 | ≤5% |
| 用户满意度 | 评分 | ≥4/5 |
| 问题解决率 | 关闭率 | P0=100%, P1≥90% |

### 5. 问题处理流程
用户报告 → PM分发 → 团队处理 → 验证关闭 → 燃尽统计

---
*由 Janus PMO 自动化系统生成 | {ctx['date']}*
""",

    "acceptance_report": lambda ctx: f"""## 验收报告 — {ctx['project']}

### 项目信息
| 项目名称 | {ctx['project']} |
|----------|------|
| 验收日期 | {ctx['date']} |
| PM | {ctx.get('pm', '-')} |

### 交付成果确认
| 序号 | 交付物 | 状态 | 备注 |
|------|--------|------|------|
| 1 | 数字化平台部署 | ☐ | |
| 2 | BIM模型交付 | ☐ | |
| 3 | IoT数据绑点 | ☐ | |
| 4 | 业务初始化配置 | ☐ | |
| 5 | 用户培训 | ☐ | |
| 6 | 技术文档 | ☐ | |
| 7 | 试运行报告 | ☐ | |

### 验收结论
- ☐ 验收通过
- ☐ 有条件通过（附整改计划）
- ☐ 验收不通过

### 签字
| | 签名 | 日期 |
|------|------|------|
| 客户代表 | | |
| 项目经理 | | |

---
*由 Janus PMO 自动化系统生成 | {ctx['date']}*
""",

    "retrospective": lambda ctx: f"""## 项目复盘报告 — {ctx['project']}

### 1. 项目概述
- **项目名称**: {ctx['project']}
- **复盘日期**: {ctx['date']}
- **参与人员**: 全项目团队

### 2. 目标达成情况
| 目标 | 计划 | 实际 | 达成 |
|------|------|------|------|
| 项目工期 | - | - | ☐ |
| 交付质量 | - | - | ☐ |
| 客户满意度 | - | - | ☐ |
| 预算控制 | - | - | ☐ |

### 3. 做得好的（Keep）
> 列举项目中的成功实践和值得推广的经验

### 4. 需要改进的（Improve）
> 列举项目中的问题和改进建议

### 5. 经验教训
| 编号 | 经验/教训 | 类别 | 建议措施 |
|------|-----------|------|----------|
| L001 | | | |
| L002 | | | |

### 6. 对PMO体系的反馈
> 对标准流程、工具、模板的改进建议，将反馈至PMO知识库

---
*由 Janus PMO 自动化系统生成 | {ctx['date']}*
""",

    "value_analysis": lambda ctx: f"""## 价值分析报告 — {ctx['project']}

### 1. 分析概述
- **项目**: {ctx['project']}
- **分析日期**: {ctx['date']}
- **分析人**: CDE

### 2. 量化价值
| 维度 | 基线值 | 实现值 | 改善率 |
|------|--------|--------|--------|
| 能耗 (kWh) | - | - | - |
| 碳排放 (tCO2) | - | - | - |
| 运维工时 (h/月) | - | - | - |
| 故障响应时间 (min) | - | - | - |
| 设备可用率 (%) | - | - | - |

### 3. 定性价值
> 管理可视化、决策效率、合规达标等

### 4. ROI估算
> 基于量化数据的投资回报分析

---
*由 Janus PMO 自动化系统生成 | {ctx['date']}*
""",

    "ops_handover": lambda ctx: f"""## 运维交接清单 — {ctx['project']}

### 交接信息
| 项目 | {ctx['project']} |
|------|------|
| 交接日期 | {ctx['date']} |
| 交付方 | 项目团队 |
| 接收方 | 运维团队 |

### 交接项目
| 类别 | 项目 | 状态 | 备注 |
|------|------|------|------|
| 账号 | 管理员账号 | ☐ | |
| 账号 | API密钥 | ☐ | |
| 文档 | 技术架构文档 | ☐ | |
| 文档 | 操作手册 | ☐ | |
| 文档 | FAQ常见问题 | ☐ | |
| 知识 | RCC知识库 | ☐ | |
| 知识 | 故障处理指南 | ☐ | |
| 协议 | SLA服务协议 | ☐ | |
| 协议 | 升级处理流程 | ☐ | |
| 数据 | 数据备份确认 | ☐ | |

### 确认签字
| | 签名 | 日期 |
|------|------|------|
| 项目团队 | | |
| 运维团队 | | |

---
*由 Janus PMO 自动化系统生成 | {ctx['date']}*
""",
}

# 未定义模板的通用生成器
def _default_template(ctx, deliverable):
    return f"""## {deliverable['name']} — {ctx['project']}

### 文档信息
| 项目 | {ctx['project']} |
|------|------|
| 负责人 | {deliverable['role']} |
| 日期 | {ctx['date']} |

### 内容
> 请根据项目实际情况填写本交付物内容

---
*由 Janus PMO 自动化系统生成 | {ctx['date']}*
"""


# ---------------------------------------------------------------------------
# Notion API
# ---------------------------------------------------------------------------

NOTION_BASE = "https://api.notion.com/v1"


def notion_headers():
    token = os.environ.get("NOTION_TOKEN", "")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }


def create_notion_page(parent_id, title, markdown_content, icon="📄"):
    """创建Notion页面（简化版，使用paragraph块）"""
    # 将markdown分段转为Notion块
    children = []
    for line in markdown_content.strip().split("\n"):
        if line.startswith("## "):
            children.append({
                "object": "block", "type": "heading_2",
                "heading_2": {"rich_text": [{"text": {"content": line[3:]}}]}
            })
        elif line.startswith("### "):
            children.append({
                "object": "block", "type": "heading_3",
                "heading_3": {"rich_text": [{"text": {"content": line[4:]}}]}
            })
        elif line.startswith("- "):
            children.append({
                "object": "block", "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"text": {"content": line[2:]}}]}
            })
        elif line.startswith("> "):
            children.append({
                "object": "block", "type": "callout",
                "callout": {
                    "rich_text": [{"text": {"content": line[2:]}}],
                    "icon": {"type": "emoji", "emoji": "💡"}
                }
            })
        elif line.strip() == "---":
            children.append({"object": "block", "type": "divider", "divider": {}})
        elif line.strip():
            children.append({
                "object": "block", "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": line}}]}
            })

    # 限制100块
    children = children[:100]

    payload = {
        "parent": {"page_id": parent_id},
        "icon": {"type": "emoji", "emoji": icon},
        "properties": {"title": [{"text": {"content": title}}]},
        "children": children,
    }

    resp = requests.post(
        f"{NOTION_BASE}/pages",
        headers=notion_headers(),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def generate_deliverables(project_name, gate, pm_name="", parent_page_id="", dry_run=False):
    """为指定阶段门生成交付物"""
    if gate not in GATE_DELIVERABLES:
        print(f"❌ 未知阶段门: {gate}")
        return []

    deliverables = GATE_DELIVERABLES[gate]
    ctx = {
        "project": project_name,
        "pm": pm_name,
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

    results = []
    for d in deliverables:
        template_key = d["template"]
        generator = TEMPLATE_GENERATORS.get(template_key)
        if generator:
            content = generator(ctx)
        else:
            content = _default_template(ctx, d)

        title = f"[{d['code']}] {d['name']}"
        auto_tag = "🤖" if d["auto"] else "✋"

        if dry_run:
            print(f"  {auto_tag} {title} ({d['role']})")
            print(f"     → {d['description']}")
            results.append({"code": d["code"], "name": d["name"], "status": "dry_run"})
        else:
            if not parent_page_id:
                print(f"  ⚠️ 未指定parent_page_id，跳过Notion创建")
                results.append({"code": d["code"], "name": d["name"], "status": "skipped"})
                continue

            try:
                page = create_notion_page(parent_page_id, title, content)
                url = page.get("url", "")
                print(f"  ✅ {auto_tag} {title} → {url}")
                results.append({
                    "code": d["code"],
                    "name": d["name"],
                    "status": "created",
                    "url": url,
                })
            except Exception as e:
                print(f"  ❌ {title}: {e}")
                results.append({"code": d["code"], "name": d["name"], "status": "error", "error": str(e)})

    return results


def main():
    parser = argparse.ArgumentParser(description="AI交付物自动生成工具")
    parser.add_argument("--project", "-p", required=True, help="项目名称")
    parser.add_argument("--gate", "-g", help="阶段门 (G0-G5)")
    parser.add_argument("--all", action="store_true", help="生成所有阶段门的交付物")
    parser.add_argument("--pm", default="", help="项目经理姓名")
    parser.add_argument("--parent", default="", help="Notion父页面ID")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不创建")
    args = parser.parse_args()

    print(f"📦 AI交付物自动生成")
    print(f"   项目: {args.project}")
    print("=" * 60)

    gates = list(GATE_DELIVERABLES.keys()) if args.all else [args.gate] if args.gate else []
    if not gates:
        print("❌ 请指定 --gate G2 或 --all")
        # 显示可用阶段门
        for gate, items in GATE_DELIVERABLES.items():
            print(f"\n  {gate}: {len(items)}个交付物")
            for d in items:
                auto_tag = "🤖" if d["auto"] else "✋"
                print(f"    {auto_tag} {d['code']} {d['name']} ({d['role']})")
        sys.exit(1)

    all_results = {}
    for gate in gates:
        print(f"\n{'─' * 60}")
        print(f"📋 {gate} 阶段门交付物:")
        print(f"{'─' * 60}")
        results = generate_deliverables(
            args.project, gate, args.pm, args.parent, args.dry_run
        )
        all_results[gate] = results

    # 汇总
    total = sum(len(r) for r in all_results.values())
    created = sum(1 for r in all_results.values() for d in r if d["status"] == "created")
    print(f"\n{'=' * 60}")
    mode = "预览" if args.dry_run else "生成"
    print(f"{mode}完成。共 {total} 个交付物。")
    if not args.dry_run:
        print(f"成功创建: {created}/{total}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
