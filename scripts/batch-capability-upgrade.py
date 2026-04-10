#!/usr/bin/env python3
"""
batch-capability-upgrade.py — Agent卡片批量能力升级工具

capability_architect 提供的领域知识映射 + 自动补全experience字段
"""

import re
import yaml
from pathlib import Path

HR_ROOT = Path(__file__).parent.parent / "obs" / "01-team-knowledge" / "HR" / "personnel"

# ── capability_architect 提供的C级→B级升级映射 ──────────────────────────

CAPABILITY_UPGRADES = {
    # Butler 团队通用
    "项目全生命周期管理": "基于PMP/PRINCE2的项目全生命周期管理（启动→策划→执行→监控→收尾）",
    "跨地域团队协调": "跨地域/跨时区团队协调（多文化项目管理、远程协作工具链）",
    "交付质量把控": "基于阶段门(Gate Review)的交付质量把控与里程碑验收",
    "培训体系设计": "基于ADDIE模型的企业培训体系设计与课程开发",
    "培训课程开发": "基于Kirkpatrick四级评估的培训课程开发与效果评估",
    "培训效果评估": "基于柯氏四级(反应/学习/行为/结果)的培训效果评估体系",
    "在线培训平台管理": "在线培训平台选型与运营管理（LMS系统/直播/录播/工作坊）",
    "IoT施工规划": "基于端-边-云架构的IoT施工规划与设备选型",
    "现场勘测": "IoT现场勘测方法论（信号覆盖/设备点位/线缆路由评估）",
    "设备安装调试": "IoT设备安装调试与联调（传感器/执行器/网关配置）",
    "网络设计": "IoT混合组网设计（有线Modbus/无线ZigBee+LoRa+BLE组合方案）",
    "IoT数据采集": "基于MQTT/OPC-UA协议的IoT数据采集架构设计",
    "传感器数据绑定": "多类型传感器数据绑定（温度/湿度/流量/压力/能耗，含阈值校验）",
    "数据验证与校准": "IoT数据质量验证（阈值检查/异常检测/数据清洗/时序连续性校验）",
    "数字化建模交付": "基于BIM(Revit/ArchiCAD)的建筑数字化建模与交付",
    "建筑数字化建模": "建筑数字化建模全流程（CAD→BIM→数字孪生，含IFC/COBie标准）",
    "BIM模型创建": "BIM模型创建与审核（Revit/ArchiCAD/Navisworks，含LOD300+精度标准）",
    "3D可视化": "建筑3D可视化与数字孪生展示（WebGL/Three.js/Cesium）",
    "数据集成": "建筑数据集成（GIS+BIM+IoT多源数据融合与标准化）",
    "PMO体系搭建": "基于PMBoK/PRINCE2的PMO体系搭建（战略型/控制型/支持型选型）",
    "项目标准化制定": "项目管理标准化制定（模板库/评审机制/升级流程/决策矩阵）",
    "项目组合管理": "项目组合管理与优先级排序（基于加权评分/战略对齐度）",
    "PMO绩效指标设计": "PMO绩效指标设计（项目成功率/工期偏差/成本偏差/客户满意度）",
    "UAT测试计划设计": "基于业务场景的UAT测试计划设计（端到端流程验证+数据验证）",
    "缺陷跟踪管理": "缺陷生命周期管理（Jira/Asana缺陷跟踪，含严重度分级+回归验证）",
    "测试用例设计": "基于等价类/边界值/场景法的测试用例设计与评审",
    "验收标准制定": "基于需求追溯矩阵的验收标准制定（功能/数据/性能三维度）",

    # RD 团队
    "测试策略制定": "基于风险驱动的测试策略制定（单元/集成/系统/回归四层覆盖）",
    "测试用例编写": "基于pytest的测试用例编写（参数化/fixture/mark分层标记）",
    "自动化测试框架搭建": "基于pytest+Playwright的端到端自动化测试框架搭建",
    "性能测试": "基于JMeter/Locust的性能测试（负载/压力/稳定性测试+瓶颈定位）",
    "测试报告编写": "自动化测试报告生成（Allure报告/覆盖率统计/趋势分析）",
    "技术架构设计": "基于微服务/事件驱动的技术架构设计（含DDD领域建模）",
    "AI Agent系统设计": "基于CrewAI/LangChain的Multi-Agent系统架构设计",
    "团队技术管理": "技术团队管理（Code Review流程/技术债管理/架构决策记录ADR）",
    "研发效率优化": "研发效率优化（CI/CD流水线/自动化部署/开发环境标准化）",
    "代码质量审查": "基于ESLint/Pylint/SonarQube的代码质量审查与技术债管理",
    "响应式设计": "响应式Web设计（Mobile-First/CSS Grid/Flexbox/媒体查询断点策略）",
    "状态管理": "前端状态管理方案设计（Pinia/Redux/Context API，按复杂度选型）",
    "容器化部署": "基于Docker/Kubernetes的容器化部署（Dockerfile优化/Helm Charts）",
    "监控告警": "基于Prometheus+Grafana的监控告警体系搭建（指标采集/Dashboard/告警规则）",

    # Stock 团队
    "项目计划管理": "基于Asana的项目计划管理（里程碑/Sprint/燃尽图追踪）",
    "团队协调": "跨职能团队协调（交易员+量化+开发的敏捷协作模式）",
    "需求管理": "产品需求管理与优先级排序（MoSCoW方法/用户故事映射）",
    "进度跟踪": "项目进度跟踪与风险预警（EVM挣值管理/偏差分析）",
    "数据清洗": "基于pandas的A股数据清洗（复权处理/停牌填充/异常值检测）",
    "特征工程": "量化交易特征工程（技术指标衍生/因子构建/时序特征提取）",
    "策略开发": "基于《炒股的智慧》的趋势交易策略开发（MA20/MA60趋势过滤+ATR止损）",
    "回测分析": "基于Backtrader/自研引擎的策略回测分析（夏普比率/最大回撤/胜率统计）",
    "交易信号生成": "基于多指标融合(MA+RSI+ATR+成交量)的交易信号生成与验证",
    "仓位管理": "基于《炒股的智慧》的分阶段建仓策略（试探→加码→满仓→减码）",
    "止损管理": "动态止损管理（ATR跟踪止损/百分比止损/时间止损三重机制）",
    "交易复盘": "每日交易复盘（持仓盈亏分析/策略信号回顾/市场环境评估）",

    # Graphify 团队
    "趋势识别": "基于时间序列分析(ARIMA/指数平滑)的趋势识别与预测",
    "模式发现": "基于聚类分析(K-means/DBSCAN)的行为模式发现",
    "异常检测": "基于统计方法(Z-score/IQR)+上下文分析的异常检测",
    "预测分析": "基于场景推演(蒙特卡洛模拟/敏感性分析)的预测分析",
    "数据可视化": "基于Mermaid/ECharts的数据可视化与趋势报告生成",
    "复杂问题拆解": "基于MECE原则(相互独立/完全穷尽)的复杂问题结构化拆解",
    "战略路径设计": "基于OKR/战略地图的战略路径设计与里程碑规划",
    "风险识别与应对": "基于概率-影响矩阵的风险识别、评估与应对策略设计",
    "资源优化配置": "基于约束理论(TOC)的资源优化配置与瓶颈分析",
    "多选项评估": "基于加权决策矩阵(Pugh Matrix)的多选项量化评估",
    "行动建议生成": "基于决策树+期望值分析的行动建议生成与优先级排序",
    "隐性关联发现": "基于知识图谱(Neo4j/NetworkX)的隐性关联发现与路径推理",
    "跨领域知识链接": "跨领域知识链接与语义网络分析（实体识别→关系抽取→图构建）",
    "语义网络分析": "基于图算法(PageRank/社区检测)的语义网络分析",

    # ── 第二轮补充（覆盖剩余42种C级）──

    # Butler 补充
    "培训体系搭建": "基于Kirkpatrick四级评估模型的企业培训体系搭建（需求分析→课程设计→交付→评估）",
    "培训交付": "多形式培训交付（线上直播/录播课程/工作坊/沙盘演练）",
    "效果评估": "基于柯氏四级(反应→学习→行为→结果)的培训效果评估与改进",
    "项目治理": "基于PRINCE2的项目治理架构设计（评审机制/升级流程/决策矩阵/RACI）",
    "施工进度管理": "基于关键路径法(CPM)+挣值管理(EVM)的IoT施工进度管理",
    "时序数据分析": "基于InfluxDB/TimescaleDB的IoT时序数据分析（趋势/季节性/异常检测）",
    "测试报告编制": "基于Allure/自定义模板的测试报告编制（用例覆盖率/缺陷分布/回归结果）",

    # RD 补充
    "技术难题攻关": "复杂技术问题诊断与攻关（根因分析/性能瓶颈定位/架构级解决方案）",
    "代码评审": "基于PR Review+SonarQube的代码评审流程管理（编码规范/安全扫描/复杂度控制）",
    "团队技术指导": "技术团队Mentoring与能力建设（Tech Talk/架构决策记录ADR/技术雷达）",
    "性能优化": "全栈性能优化（数据库索引/查询优化/缓存策略/CDN/代码热点分析）",
    "研发流程优化": "基于DevOps最佳实践的研发流程优化（CI/CD/自动化测试/发布策略）",
    "前端性能优化": "前端性能优化（代码分割/懒加载/虚拟列表/Web Vitals指标达标）",
    "组件库开发": "基于Vue3/React的可复用组件库开发（Storybook文档化/单元测试覆盖）",
    "监控告警系统": "基于Prometheus+Grafana+AlertManager的全链路监控告警系统",
    "自动化运维": "基于Ansible/Terraform的基础设施即代码(IaC)自动化运维",
    "安全测试基础": "Web安全测试（OWASP Top 10检测/SQL注入/XSS/CSRF防护验证）",

    # OBS 补充
    "知识分类优化": "基于Obsidian MOC(Map of Content)的知识分类优化与导航结构设计",
    "链接结构分析": "基于Obsidian Graph View的双向链接结构分析与孤立页面检测",

    # Content_ops 补充
    "内容策略制定": "基于内容矩阵(主题×形式×渠道)的内容策略制定与排期规划",
    "内容排期规划": "基于编辑日历的内容排期规划（发布频率/主题轮换/时效性平衡）",
    "传播潜力评估": "基于社交媒体数据+SEO关键词热度的内容传播潜力评估",
    "排版优化": "基于微信/博客双平台的排版优化（科技蓝#013A7D主题/14-16px字号/1.8行高）",
    "视觉风格统一": "基于Janus Digital品牌视觉规范的内容视觉风格统一（色板/字体/间距标准）",

    # Harness_ops 补充
    "变更影响分析": "基于依赖图谱的配置变更影响分析（CLAUDE.md→experts.yaml→路由规则级联评估）",
    "回归测试执行": "基于Python ast.parse+yaml.safe_load+功能验证的三层回归测试执行",

    # Stock 补充
    "项目计划制定": "基于Asana+Sprint的项目计划制定（里程碑分解/迭代规划/验收标准）",
    "进度跟踪管理": "基于Asana看板+燃尽图的进度跟踪管理（偏差预警/资源调配）",
    "风险管理": "基于概率-影响矩阵的项目风险管理（识别→评估→应对→监控）",
    "跨团队协调": "量化交易项目跨职能协调（交易员+量化+开发的敏捷Scrum协作）",
    "交易信号识别": "基于多指标融合(MA角度+RSI超买超卖+成交量放大)的趋势交易信号识别",
    "每日盈亏复盘": "每日交易复盘（持仓盈亏P&L分析/策略信号回顾/市场环境Beta评估）",
    "仓位管理策略": "基于《炒股的智慧》的分阶段仓位管理（试探25%→加码50%→满仓→减码）",
    "止损监控": "多机制动态止损监控（ATR跟踪止损/百分比硬止损/时间止损+实时预警）",
    "量化指标设计": "A股量化指标设计与开发（MA/RSI/ATR/MACD/布林带+自定义复合因子）",
    "回测系统开发": "基于Backtrader框架的策略回测系统开发（含滑点/手续费/分红复权模拟）",
    "数据分析": "基于pandas/numpy的A股数据分析（复权处理/行业对比/因子有效性检验）",
    "策略优化": "基于网格搜索+Walk-Forward的量化策略参数优化与过拟合控制",
    "因子研究": "A股多因子研究（价值/动量/波动率因子构建+IC/IR有效性评估）",
    "股票K线图": "基于ECharts的股票K线图组件开发（含MA叠加/成交量/技术指标面板）",
    "交易界面开发": "基于Vue3+Element Plus的交易操作界面开发（下单/持仓/策略配置）",
    "数据看板": "基于ECharts+Pinia的实时数据看板开发（收益曲线/仓位分布/风险指标）",

    # OBS 团队
    "知识架构设计": "基于PARA/Johnny Decimal的Obsidian知识架构设计与标签体系规划",
    "标签体系规划": "基于分面分类法的标签体系规划（主题/类型/状态/优先级多维标签）",
    "知识模板设计": "Obsidian知识模板设计（含YAML frontmatter标准、Dataview查询优化）",
    "项目知识沉淀": "基于复盘四步法(回顾目标/评估结果/分析原因/总结经验)的项目知识沉淀",
    "经验萃取和总结": "经验萃取方法论（关键事件法/最佳实践提炼/失败模式记录）",
    "SOP文档编写": "基于流程图+检查清单的SOP文档编写（含版本管理与评审机制）",
    "复盘会议主持": "基于AAR(After Action Review)的复盘会议主持与知识产出",
    "知识去重": "基于标题/标签/内容相似度的知识去重策略与自动化检测",
}

# ── experience 补全映射（按团队）──────────────────────────────────

EXPERIENCE_ADDITIONS = {
    "content_strategist": [
        "B2B SaaS 内容策略规划与执行",
        "建筑科技/PropTech行业内容矩阵设计",
    ],
    "visual_designer": [
        "科技蓝品牌视觉设计体系管理",
        "Markdown/HTML内容排版与样式优化",
    ],
    "publishing_ops": [
        "Astro静态网站生成与博客发布管理",
        "n8n自动化工作流运维（微信/博客发布链路）",
    ],
    "knowledge_chandu_expert": [
        "Obsidian知识库经验沉淀实践",
        "项目复盘方法论应用与知识产出",
    ],
}


def parse_frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---\n(.*)', text, re.DOTALL)
    if not m:
        return {}, text
    fm = yaml.safe_load(m.group(1))
    return fm or {}, m.group(2)


def dump_frontmatter(fm, body):
    lines = ["---"]
    for key, val in fm.items():
        if isinstance(val, list):
            lines.append(f"{key}:")
            for item in val:
                lines.append(f"  - {item}")
        else:
            if isinstance(val, str) and any(c in str(val) for c in [':', '#', '{', '}']):
                lines.append(f'{key}: "{val}"')
            else:
                lines.append(f"{key}: {val}")
    lines.append("---")
    return "\n".join(lines) + "\n" + body


def upgrade_card(filepath):
    text = filepath.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    changed = False
    sid = fm.get("specialist_id", filepath.stem)

    # 1. 升级capabilities
    caps = fm.get("capabilities", [])
    new_caps = []
    for cap in caps:
        cap_str = str(cap).strip()
        if cap_str in CAPABILITY_UPGRADES:
            new_caps.append(CAPABILITY_UPGRADES[cap_str])
            changed = True
        else:
            new_caps.append(cap_str)
    if new_caps:
        fm["capabilities"] = new_caps

    # 2. 补充experience
    if sid in EXPERIENCE_ADDITIONS:
        existing = fm.get("experience", [])
        if not existing or len(existing) < 2:
            fm["experience"] = EXPERIENCE_ADDITIONS[sid]
            changed = True

    # 3. 确保必填字段
    if "workload" not in fm:
        fm["workload"] = "medium"
        changed = True
    if "max_concurrent_tasks" not in fm:
        fm["max_concurrent_tasks"] = 5
        changed = True

    if changed:
        new_text = dump_frontmatter(fm, body)
        filepath.write_text(new_text, encoding="utf-8")
        return True
    return False


def main():
    teams = ["butler", "rd", "obs", "content_ops", "graphify", "stock", "harness_ops"]
    total_upgraded = 0

    for team in teams:
        team_dir = HR_ROOT / team
        if not team_dir.exists():
            continue
        for card in team_dir.glob("*.md"):
            if upgrade_card(card):
                total_upgraded += 1
                print(f"  upgraded: {card.stem} ({team})")

    print(f"\nTotal upgraded: {total_upgraded} agents")


if __name__ == "__main__":
    main()
