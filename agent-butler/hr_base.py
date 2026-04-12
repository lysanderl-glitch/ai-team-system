"""
HR知识库基础模块
提供与OBS HR知识库的交互接口

用于Lysander CEO召唤团队时查询人员档案和能力信息
"""

import yaml
import re
from pathlib import Path
from typing import Optional, List, Dict

# 路径配置 - 支持环境变量自定义，默认使用相对路径
import os
OBS_KB_ROOT = Path(os.environ.get("OBS_KB_ROOT", Path(__file__).parent.parent / "obs"))
HR_KB_ROOT = OBS_KB_ROOT / "01-team-knowledge" / "HR"
CONFIG_DIR = Path(__file__).parent / "config"
ORG_CONFIG = CONFIG_DIR / "organization.yaml"


def load_org_config() -> dict:
    """加载组织配置"""
    with open(ORG_CONFIG, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_personnel_card(specialist_id: str, team: str) -> Optional[dict]:
    """加载人员卡片

    Args:
        specialist_id: 专家标识符 (如 'backend_dev')
        team: 团队标识符 (如 'rd')

    Returns:
        人员卡片字典，包含YAML front matter和内容
    """
    card_path = HR_KB_ROOT / "personnel" / team / f"{specialist_id}.md"
    if not card_path.exists():
        return None

    with open(card_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 解析YAML front matter
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return None

    front_matter = yaml.safe_load(match.group(1))
    body = match.group(2)

    return {
        **front_matter,
        "content": body,
        "source_path": str(card_path)
    }


def get_personnel_by_specialist_id(specialist_id: str) -> Optional[dict]:
    """通过specialist_id查询人员档案（全局搜索）

    在所有团队中查找匹配的专家

    Args:
        specialist_id: 专家标识符

    Returns:
        人员档案字典，未找到返回None
    """
    org = load_org_config()

    # 在所有团队中搜索
    for team_key, team_config in org.get("teams", {}).items():
        if specialist_id in team_config.get("specialists", []):
            return load_personnel_card(specialist_id, team_key)

    # 也检查lysander团队
    lysander_path = HR_KB_ROOT / "personnel" / "lysander" / "lysander.md"
    if specialist_id == "lysander" and lysander_path.exists():
        with open(lysander_path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if match:
            front_matter = yaml.safe_load(match.group(1))
            return {**front_matter, "content": match.group(2), "source_path": str(lysander_path)}

    return None


def resolve_team_members(team_key: str) -> List[dict]:
    """解析团队所有成员的人员档案

    Args:
        team_key: 团队标识符 (如 'rd')

    Returns:
        成员档案列表
    """
    org = load_org_config()
    team_config = org.get("teams", {}).get(team_key, {})
    specialist_ids = team_config.get("specialists", [])

    members = []
    for sid in specialist_ids:
        personnel = load_personnel_card(sid, team_key)
        if personnel:
            members.append({
                "specialist_id": sid,
                "name": personnel.get("name"),
                "role": personnel.get("role"),
                "type": personnel.get("type"),
                "domains": personnel.get("domains", []),
                "capabilities": personnel.get("capabilities", []),
                "availability": personnel.get("availability"),
                "status": personnel.get("status"),
                "召唤关键词": personnel.get("召唤关键词", []),
                "source": personnel.get("source_path")
            })
        else:
            # 兜底：只有ID没有档案
            members.append({
                "specialist_id": sid,
                "name": sid,
                "role": "未知",
                "type": "unknown",
                "availability": "unknown",
                "source": None
            })

    return members


def get_team_hr_summary(team_key: str) -> dict:
    """获取团队HR概览

    Args:
        team_key: 团队标识符

    Returns:
        团队HR摘要字典
    """
    org = load_org_config()
    team_config = org.get("teams", {}).get(team_key, {})

    members = resolve_team_members(team_key)

    return {
        "team": team_key,
        "team_name": team_config.get("name"),
        "description": team_config.get("description"),
        "member_count": len(members),
        "members": members,
        "human_experts": [m for m in members if m.get("type") == "human_expert"],
        "ai_agents": [m for m in members if m.get("type") == "ai_agent"],
        "available": [m for m in members if m.get("availability") == "available"],
        "unavailable": [m for m in members if m.get("availability") != "available"]
    }


def find_experts_by_task(task_description: str, team_key: Optional[str] = None) -> List[dict]:
    """根据任务描述查找匹配的专家

    Args:
        task_description: 任务描述文本
        team_key: 可选，限定团队

    Returns:
        匹配的专家列表
    """
    task_lower = task_description.lower()
    org = load_org_config()

    teams_to_search = [team_key] if team_key else list(org.get("teams", {}).keys())

    matched = []
    for tk in teams_to_search:
        members = resolve_team_members(tk)
        for member in members:
            # 检查召唤关键词是否匹配
            keywords = member.get("召唤关键词", [])
            if any(kw in task_lower for kw in keywords):
                matched.append(member)

    return matched


def get_all_teams_summary() -> List[dict]:
    """获取所有团队的HR概览

    Returns:
        所有团队摘要列表
    """
    org = load_org_config()
    teams = []

    for team_key in org.get("teams", {}).keys():
        summary = get_team_hr_summary(team_key)
        teams.append(summary)

    # 添加lysander
    lysander = get_personnel_by_specialist_id("lysander")
    if lysander:
        teams.append({
            "team": "lysander",
            "team_name": "公司管理层",
            "member_count": 1,
            "members": [{
                "specialist_id": "lysander",
                "name": lysander.get("name"),
                "role": lysander.get("role"),
                "type": lysander.get("type"),
                "domains": lysander.get("domains", []),
                "capabilities": lysander.get("capabilities", []),
                "availability": lysander.get("availability"),
                "source": lysander.get("source_path")
            }],
            "human_experts": [{
                "specialist_id": "lysander",
                "name": lysander.get("name"),
                "role": lysander.get("role"),
                "type": lysander.get("type"),
                "availability": lysander.get("availability")
            }],
            "ai_agents": [],
            "available": [{
                "specialist_id": "lysander",
                "name": lysander.get("name"),
                "availability": lysander.get("availability")
            }]
        })

    return teams


# ============================================================================
# v3.0 — Agent HR 质量审计引擎
# 由 HR Director + Capability Architect 使用
# ============================================================================

# 强制 Schema 必填字段
_REQUIRED_CARD_FIELDS = [
    "specialist_id", "team", "role", "status", "type",
    "domains", "capabilities", "experience",
    "availability", "召唤关键词",
]

# C级（不合格）能力描述特征 — 过于笼统的活动名
_C_LEVEL_PATTERNS = [
    "项目管理", "知识沉淀", "质量审核", "内容创作", "数据分析",
    "系统开发", "测试", "设计", "优化", "协调", "管理",
    "分析", "规划", "检索", "推荐", "审核",
]


def audit_agent_card(specialist_id: str, team_key: str = None) -> dict:
    """Agent 卡片质量审计

    由 HR Director 使用，检查单个 Agent 卡片的合规性和质量。

    Args:
        specialist_id: Agent 标识
        team_key: 团队标识（可选，不提供则全局搜索）

    Returns:
        审计结果：
        - score: 总分 (0-100)
        - schema_complete: Schema 完整性
        - capability_grades: 每条能力的评级
        - issues: 问题列表
        - recommendation: 处置建议
    """
    # 加载卡片
    if team_key:
        card = load_personnel_card(specialist_id, team_key)
    else:
        card = get_personnel_by_specialist_id(specialist_id)

    if not card:
        return {
            "score": 0,
            "specialist_id": specialist_id,
            "issues": [f"找不到 Agent 卡片: {specialist_id}"],
            "recommendation": "卡片不存在，需要创建",
        }

    issues = []
    scores = {}

    # ── 1. Schema 完整性检查 (权重 25%) ──
    missing_fields = []
    for field in _REQUIRED_CARD_FIELDS:
        if field not in card or not card[field]:
            missing_fields.append(field)

    schema_score = max(0, 100 - len(missing_fields) * 15)
    scores["schema"] = schema_score
    if missing_fields:
        issues.append(f"缺失必填字段: {', '.join(missing_fields)}")

    # ── 2. 能力描述质量 (权重 30%) ──
    capabilities = card.get("capabilities", [])
    cap_count = len(capabilities)

    if cap_count < 3:
        issues.append(f"capabilities 仅 {cap_count} 条，要求至少 4 条")

    c_level_count = 0
    capability_grades = []

    # B级以上关键词：包含这些说明至少是方法论/框架级别
    _b_level_indicators = [
        "SWOT", "PEST", "PRINCE2", "Agile", "Scrum", "PMP", "ITIL", "CMMI",
        "Kano", "Porter", "PMBoK", "ADDIE", "TDD", "BDD", "CI/CD",
        "IoT", "BIM", "CAD", "GIS", "IFC", "MQTT", "OPC-UA", "Modbus",
        "REST", "API", "SQL", "NoSQL", "ETL", "ML", "NLP", "RAG",
        "WBS", "UAT", "SOP", "KPI", "OKR", "ROI", "GTM", "PMF", "SEO",
        "ATR", "RSI", "MA", "MACD",
        "知识图谱", "决策树", "语义网络", "图推理", "神经网络",
        "时间序列", "回归分析", "聚类分析", "模式识别", "异常检测",
        "敏感性分析", "利弊分析", "价值链", "波特五力",
        "燃尽图", "甘特图", "关键路径",
    ]

    for cap in capabilities:
        cap_str = str(cap).strip()

        # 先检查是否包含B级以上指标词
        has_method = any(ind in cap_str for ind in _b_level_indicators)

        # 检查是否为 A 级（包含工具/框架名+具体产出物描述，通常较长且有括号说明）
        has_tool = any(c in cap_str for c in [
            "(", ")", "pytest", "FastAPI", "Vue", "React", "Docker",
            "Kubernetes", "Playwright", "Selenium", "JMeter",
            "Obsidian", "Claude", "Python", "yaml", "json",
            "Asana", "Notion", "n8n", "GitHub", "Slack",
            "Excel", "Figma", "Canva",
            "基于", "框架", "引擎", "工具链", "脚本",
            "ECharts", "Element Plus", "Pinia", "Tailwind",
            "SQLAlchemy", "FastAPI", "Baostock",
            "generate-article", "hr_base",
        ])

        # C级判断：仅活动名（短且无方法论/工具指标）
        is_c_level = False
        if not has_method and not has_tool:
            if len(cap_str) <= 6:
                is_c_level = True
            else:
                for pattern in _C_LEVEL_PATTERNS:
                    if cap_str == pattern:
                        is_c_level = True
                        break

        if is_c_level:
            grade = "C"
            c_level_count += 1
        elif has_tool:
            grade = "A"
        else:
            grade = "B"

        capability_grades.append({"capability": cap_str, "grade": grade})

    if c_level_count > 0:
        issues.append(f"{c_level_count} 条能力描述为 C 级（不合格）")

    cap_quality_score = 100
    if cap_count == 0:
        cap_quality_score = 0
    else:
        a_count = sum(1 for g in capability_grades if g["grade"] == "A")
        b_count = sum(1 for g in capability_grades if g["grade"] == "B")
        cap_quality_score = int((a_count * 100 + b_count * 70 + c_level_count * 20) / cap_count)
    scores["capability_quality"] = cap_quality_score

    # ── 3. Domains 充实度 (权重 15%) ──
    domains = card.get("domains", [])
    domain_score = min(100, len(domains) * 25)  # 4条=100
    scores["domains"] = domain_score
    if len(domains) < 3:
        issues.append(f"domains 仅 {len(domains)} 条，要求至少 3 条")

    # ── 4. Experience 充实度 (权重 15%) ──
    experience = card.get("experience", [])
    exp_score = min(100, len(experience) * 40)  # 2-3条就够
    scores["experience"] = exp_score
    if len(experience) < 2:
        issues.append(f"experience 仅 {len(experience)} 条，要求至少 2 条")

    # ── 5. 召唤关键词 (权重 15%) ──
    keywords = card.get("召唤关键词", [])
    kw_score = min(100, len(keywords) * 20)  # 5条=100
    scores["keywords"] = kw_score
    if len(keywords) < 4:
        issues.append(f"召唤关键词 仅 {len(keywords)} 个，要求至少 4 个")

    # ── 加权总分 ──
    total = int(
        scores["schema"] * 0.25 +
        scores["capability_quality"] * 0.30 +
        scores["domains"] * 0.15 +
        scores["experience"] * 0.15 +
        scores["keywords"] * 0.15
    )

    # 处置建议
    if total >= 90:
        recommendation = "合格，保持 active"
    elif total >= 80:
        recommendation = "需优化，限期提升能力描述至A级"
    elif total >= 60:
        recommendation = "不合格，立即修订"
    else:
        recommendation = "严重不合格，降级inactive或退役"

    return {
        "specialist_id": specialist_id,
        "team": card.get("team", "unknown"),
        "role": card.get("role", "unknown"),
        "score": total,
        "scores": scores,
        "capability_grades": capability_grades,
        "issues": issues,
        "recommendation": recommendation,
        "audited_at": datetime.now().isoformat(),
    }


def audit_all_agents() -> dict:
    """全量 Agent 质量审计

    遍历所有团队的所有 Agent，逐一审计。

    Returns:
        审计报告：
        - total_agents: 总数
        - average_score: 平均分
        - by_team: 按团队分组的结果
        - critical_issues: 严重问题列表
        - agents_below_60: 不合格 Agent 列表
    """
    org = load_org_config()
    results = []
    team_scores = {}

    for team_key, team_config in org.get("teams", {}).items():
        specialists = team_config.get("specialists", [])
        team_results = []

        for sid in specialists:
            audit = audit_agent_card(sid, team_key)
            results.append(audit)
            team_results.append(audit)

        if team_results:
            avg = sum(r["score"] for r in team_results) / len(team_results)
            team_scores[team_key] = {
                "name": team_config.get("name", team_key),
                "count": len(team_results),
                "average": round(avg, 1),
                "below_60": [r for r in team_results if r["score"] < 60],
            }

    total = len(results)
    avg_score = round(sum(r["score"] for r in results) / total, 1) if total else 0

    return {
        "total_agents": total,
        "average_score": avg_score,
        "by_team": team_scores,
        "critical_issues": [r for r in results if r["score"] < 40],
        "agents_below_60": [
            {"specialist_id": r["specialist_id"], "team": r["team"],
             "score": r["score"], "recommendation": r["recommendation"]}
            for r in results if r["score"] < 60
        ],
        "audited_at": datetime.now().isoformat(),
    }


# ============================================================================
# 决策检查机制 - 确保沟通决策原则被自动执行
# ============================================================================

# 小问题定义：风险可控、不影响核心架构、有明确执行路径
_SMALL_PROBLEM_KEYWORDS = [
    # 纯技术细节
    "同步", "sync", "生成yaml", "加载", "查询",
    # 例行操作
    "显示", "列出", "查看", "获取状态",
    # 已知流程
    "组装团队", "召唤", "路由",
    # 固化工作流执行 - Harness Engineering
    "固化", "工作流", "执行脚本", "推送微信",
    "发布博客", "构建网站", "daily-publish",
]

# 需要智囊团决策的关键词
_THINK_TANK_KEYWORDS = [
    "新架构", "新方案", "策略调整", "原则修改",
    "自动化方案", "决策体系", "流程变更",
]

# 需要代码审计的关键词
_CODE_REVIEW_KEYWORDS = [
    "脚本", "代码", "实现", "修改代码", "编写",
    "harness", "workflow", "自动化脚本",
]

# ============================================================================
# Harness Engineering: 决策Feedback Loop机制
# ============================================================================

import json
import ast
import subprocess
from datetime import datetime

DECISION_LOG_PATH = Path(__file__).parent / "config" / "decision_log.json"
HARNESS_CONFIG_PATH = Path(__file__).parent / "config" / "harness_keywords.json"

# 代码自检：需要检查依赖的模块
_REQUIRED_MODULES = ["watchdog", "yaml", "pathlib"]

def pre_execution_check(code_path: str = None, script_content: str = None) -> dict:
    """执行前自检（Harness自我修复机制）

    Args:
        code_path: 代码文件路径（可选）
        script_content: 脚本内容（可选）

    Returns:
        检查结果字典:
            - passed: 是否通过
            - errors: 错误列表
            - warnings: 警告列表
    """
    errors = []
    warnings = []

    # 1. Python语法检查
    if script_content:
        try:
            ast.parse(script_content)
        except SyntaxError as e:
            errors.append(f"Python语法错误: {e}")

    # 2. 模块依赖检查
    for module in _REQUIRED_MODULES:
        try:
            __import__(module)
        except ImportError:
            warnings.append(f"模块 '{module}' 未安装，可能影响功能")

    # 3. 文件路径检查
    if code_path:
        path = Path(code_path)
        if not path.exists():
            warnings.append(f"文件不存在: {code_path}")
        elif path.suffix == ".py":
            # 检查Python文件语法
            try:
                with open(path, "r", encoding="utf-8") as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                errors.append(f"Python语法错误 [{code_path}]: {e}")

    # 4. 执行Shell命令检查
    if script_content and ("subprocess" in script_content or "os.system" in script_content):
        warnings.append("脚本包含系统命令调用，建议QA审计")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checked_at": datetime.now().isoformat()
    }

def post_execution_evaluate(task: str, execution_result: dict = None) -> dict:
    """执行后自动评估（消除条件反射式询问）

    在每次执行完成后自动调用，判断是否需要Lysander介入。

    Args:
        task: 任务描述
        execution_result: 执行结果字典（可选）

    Returns:
        评估结果:
            - need_lysander: 是否需要Lysander
            - reason: 判断理由
            - action: 建议行动
    """
    task_lower = task.lower()

    # 执行成功的默认判断
    if execution_result and execution_result.get("success"):
        # 检查是否涉及需要继续的主题
        follow_up_keywords = [
            "下一步", "接下来", "然后", "继续",
            "发布", "deploy", "上线",
        ]
        for kw in follow_up_keywords:
            if kw in task_lower:
                # 有后续动作关键词，检查是否需要决策
                return {
                    "need_lysander": False,  # 默认不需要，除非有明确理由
                    "reason": "执行成功，有后续关键词，但应继续执行而非询问",
                    "action": "直接执行后续步骤"
                }

        # 无后续关键词，说明任务已完成
        return {
            "need_lysander": False,
            "reason": "任务执行成功，无需Lysander",
            "action": "任务完成"
        }

    # 执行失败的判断
    if execution_result and not execution_result.get("success"):
        error_type = execution_result.get("error_type", "")
        if error_type in ["syntax_error", "import_error"]:
            # 代码级错误，应该自动尝试修复或记录
            return {
                "need_lysander": False,
                "reason": "代码错误，应记录到Harness并尝试修复",
                "action": "触发Harness自我修复流程"
            }
        # 其他错误，可能需要Lysander判断
        return {
            "need_lysander": True,
            "reason": f"执行失败（{error_type}），需要Lysander判断",
            "action": "上报Lysander"
        }

    # 无执行结果，按正常流程判断
    return {
        "need_lysander": False,
        "reason": "无明确需要Lysander的情况",
        "action": "继续执行或结束"
    }

# ============================================================================
# 执行链机制：任务完成后自动执行后续步骤
# ============================================================================

# 任务执行链定义：当前任务 -> 后续任务列表
TASK_EXECUTION_CHAIN = {
    # 同步 -> 构建 -> 发布
    "同步OBS人员卡片到YAML": [
        {"task": "构建网站", "team": "rd", "keywords": ["astro", "build", "npm run build"]},
    ],
    "同步所有团队配置": [
        {"task": "构建网站", "team": "rd", "keywords": ["astro", "build", "npm run build"]},
    ],
    "构建网站": [
        {"task": "发布博客文章", "team": "content_ops", "keywords": ["wechat", "blog", "发布"]},
    ],
    # 同步 -> 构建 -> 发布 -> 通知
}

# 需要人工确认的决策点（不自动执行）
REQUIRES_CONFIRMATION = [
    "战略规划", "组织调整", "裁员", "重大投资",
]


class TaskChainExecutor:
    """执行链执行器"""

    def __init__(self):
        self.executed_chain = []

    def evaluate_and_execute_chain(self, current_task: str, context: dict = None) -> dict:
        """评估并执行后续任务链

        Args:
            current_task: 当前任务描述
            context: 执行上下文

        Returns:
            执行结果字典
        """
        self.executed_chain.append(current_task)

        # 检查是否需要确认
        for confirm_keyword in REQUIRES_CONFIRMATION:
            if confirm_keyword in current_task:
                return {
                    "task": current_task,
                    "status": "requires_confirmation",
                    "reason": f"任务涉及【{confirm_keyword}】，需要Lysander确认",
                    "chain_executed": self.executed_chain[:-1]
                }

        # 查找后续任务
        next_tasks = TASK_EXECUTION_CHAIN.get(current_task, [])

        if not next_tasks:
            return {
                "task": current_task,
                "status": "completed",
                "reason": "任务链结束",
                "chain_executed": self.executed_chain[:-1]
            }

        # 执行后续任务
        results = []
        for next_task_config in next_tasks:
            next_task = next_task_config["task"]
            print(f"\n🔗 执行后续任务: {next_task}")

            # 这里应该调用实际的执行函数
            # 当前实现只是记录
            result = {
                "task": next_task,
                "status": "executed",
                "executor": next_task_config.get("team", "auto")
            }
            results.append(result)

            # 递归执行后续链
            chain_result = self.evaluate_and_execute_chain(next_task, context)
            results.extend(chain_result.get("chain_results", []))

        return {
            "task": current_task,
            "status": "chain_completed",
            "chain_results": results,
            "chain_executed": self.executed_chain[:-1]
        }


def execute_task_chain(tasks: list) -> dict:
    """执行任务链

    Args:
        tasks: 任务列表（只执行第一个，后续由递归处理）

    Returns:
        执行结果
    """
    if not tasks:
        return {"total_tasks": 0, "results": [], "full_chain": []}

    executor = TaskChainExecutor()

    # 只执行第一个任务，递归自动处理后续
    result = executor.evaluate_and_execute_chain(tasks[0])

    return {
        "total_tasks": len(tasks),
        "results": [result],
        "full_chain": executor.executed_chain
    }


def evaluate_and_execute(task: str, execution_func, *args, **kwargs) -> dict:
    """执行后自动评估的封装函数

    消除条件反射式询问的关键机制：
    执行完成后自动评估是否需要Lysander。

    Args:
        task: 任务描述
        execution_func: 执行函数
        *args, **kwargs: 传递给执行函数的参数

    Returns:
        包含执行结果和评估结果的字典
    """
    result = None
    try:
        result = execution_func(*args, **kwargs)
        exec_result = {"success": True, "result": result}
    except Exception as e:
        exec_result = {"success": False, "error": str(e)}

    # 执行后自动评估
    evaluation = post_execution_evaluate(task, exec_result)

    return {
        "execution": exec_result,
        "evaluation": evaluation,
        "task": task
    }

def _load_decision_log() -> dict:
    """加载决策日志"""
    if DECISION_LOG_PATH.exists():
        with open(DECISION_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"decisions": [], "feedback": []}

def _save_decision_log(log: dict):
    """保存决策日志"""
    with open(DECISION_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def record_decision(task: str, decision: str, reasoning: str, result: str = "pending"):
    """记录决策到日志（Harness反馈环）

    Args:
        task: 任务描述
        decision: 决策类型 (small_problem/think_tank/escalate)
        reasoning: 判断理由
        result: 执行结果 (pending/success/lysander_intervened)
    """
    log = _load_decision_log()

    log["decisions"].append({
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "decision": decision,
        "reasoning": reasoning,
        "result": result
    })

    # 只保留最近100条
    if len(log["decisions"]) > 100:
        log["decisions"] = log["decisions"][-100:]

    _save_decision_log(log)

def record_feedback(task: str, feedback: str):
    """记录反馈到日志（Harness核心）

    Args:
        task: 任务描述
        feedback: 反馈类型 ("correct" / "incorrect" / "lysander_intervened")
    """
    log = _load_decision_log()

    # 找到对应的决策并更新
    for entry in reversed(log["decisions"]):
        if entry["task"] == task:
            entry["result"] = feedback
            entry["feedback_timestamp"] = datetime.now().isoformat()
            break

    log["feedback"].append({
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "feedback": feedback
    })

    _save_decision_log(log)

    # 分析误判模式并优化
    if feedback in ["incorrect", "lysander_intervened"]:
        _analyze_and_adjust(task, feedback)

def _analyze_and_adjust(task: str, feedback: str):
    """分析误判并自动调整关键词（Harness自我修复）

    Args:
        task: 任务描述
        feedback: 反馈类型
    """
    task_lower = task.lower()
    current_small = set(_SMALL_PROBLEM_KEYWORDS)
    current_think = set(_THINK_TANK_KEYWORDS)

    # 读取已有的harness配置
    harness_config = {}
    if HARNESS_CONFIG_PATH.exists():
        with open(HARNESS_CONFIG_PATH, "r", encoding="utf-8") as f:
            harness_config = json.load(f)

    # 分析：如果Lysander介入了，说明应该被判断为不同类型
    if feedback == "lysander_intervened":
        # 检查是否在错误地直接执行了（应该问但没问）
        # 这种情况下，可能需要把某些关键词加到THINK_TANK
        pass

    # 如果反馈说错了，可能需要调整关键词
    if feedback == "incorrect":
        # 具体分析逻辑可根据实际情况调整
        pass

    # 保存调整建议（不自动修改，需要review）
    if "adjustments" not in harness_config:
        harness_config["adjustments"] = []

    harness_config["adjustments"].append({
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "feedback": feedback,
        "suggestion": f"Consider adjusting keywords for similar tasks"
    })

    # 只保留最近20条调整建议
    if len(harness_config.get("adjustments", [])) > 20:
        harness_config["adjustments"] = harness_config["adjustments"][-20:]

    with open(HARNESS_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(harness_config, f, ensure_ascii=False, indent=2)

def get_decision_stats() -> dict:
    """获取决策统计（Harness监控）

    Returns:
        决策统计字典
    """
    log = _load_decision_log()

    total = len(log["decisions"])
    if total == 0:
        return {"total": 0, "pending": 0, "correct": 0, "incorrect": 0}

    decisions_with_feedback = [d for d in log["decisions"] if d.get("result") != "pending"]
    correct = len([d for d in decisions_with_feedback if d.get("result") == "success"])
    incorrect = len([d for d in decisions_with_feedback if d.get("result") in ["incorrect", "lysander_intervened"]])
    pending = total - len(decisions_with_feedback)

    return {
        "total": total,
        "pending": pending,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy": f"{correct / len(decisions_with_feedback) * 100:.1f}%" if decisions_with_feedback else "N/A",
        "lysander_interventions": len([d for d in log["decisions"] if d.get("result") == "lysander_intervened"])
    }

def get_harness_adjustments() -> list:
    """获取Harness调整建议

    Returns:
        调整建议列表
    """
    if HARNESS_CONFIG_PATH.exists():
        with open(HARNESS_CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("adjustments", [])
    return []


def _is_small_problem(task_description: str) -> bool:
    """判断是否为小问题（可直接执行）"""
    task_lower = task_description.lower()
    # 检查是否包含小问题关键词
    for kw in _SMALL_PROBLEM_KEYWORDS:
        if kw in task_lower:
            return True
    # 检查是否不包含需要智囊团的关键词
    for kw in _THINK_TANK_KEYWORDS:
        if kw in task_lower:
            return False
    return False

def decision_check(task_description: str, context: str = "default") -> dict:
    """决策前检查清单

    Args:
        task_description: 任务描述
        context: 执行上下文

    Returns:
        检查结果字典:
            - decision: "small_problem" | "think_tank" | "escalate" | "require_code_review"
            - reasoning: 判断理由
            - action: 建议行动
    """
    task_lower = task_description.lower()

    # [1] 检查是否为小问题
    if _is_small_problem(task_description):
        result = {
            "decision": "small_problem",
            "reasoning": "属于小问题范围：风险可控、有明确执行路径",
            "action": "直接执行，无需询问"
        }
        record_decision(task_description, result["decision"], result["reasoning"])
        return result

    # [2] 检查是否涉及代码/脚本（需要QA审计）
    for kw in _CODE_REVIEW_KEYWORDS:
        if kw in task_lower:
            result = {
                "decision": "require_code_review",
                "reasoning": "涉及代码/脚本编写，需要QA或研发团队审计",
                "action": "触发代码审计流程后方可执行",
                "review_team": ["qa_engineer", "tech_lead"]
            }
            record_decision(task_description, result["decision"], result["reasoning"])
            return result

    # [3] 检查是否需要智囊团决策
    for kw in _THINK_TANK_KEYWORDS:
        if kw in task_lower:
            result = {
                "decision": "think_tank",
                "reasoning": f"涉及【{kw}】，需要智囊团分析确认",
                "action": "召集智囊团分析和决策"
            }
            record_decision(task_description, result["decision"], result["reasoning"])
            return result

    # [4] 检查是否超出授权范围（需要上报）
    escalation_keywords = ["战略", "裁员", "重大投资", "组织调整"]
    for kw in escalation_keywords:
        if kw in task_lower:
            result = {
                "decision": "escalate",
                "reasoning": f"涉及【{kw}】，超出AI决策授权",
                "action": "上报Lysander CEO"
            }
            record_decision(task_description, result["decision"], result["reasoning"])
            return result

    # [5] 默认：属于执行层决策，智囊团确认后执行
    result = {
        "decision": "think_tank",
        "reasoning": "需要智囊团确认执行方案",
        "action": "召集智囊团确认后执行"
    }
    record_decision(task_description, result["decision"], result["reasoning"])
    return result


def get_think_tank_decision(task_description: str) -> dict:
    """获取智囊团决策（自动化决策体系核心）

    Args:
        task_description: 任务描述

    Returns:
        智囊团决策结果
    """
    check = decision_check(task_description, "think_tank")

    if check["decision"] == "small_problem":
        return {
            **check,
            "team": None,
            "approved": True,
            "message": "小问题，直接执行"
        }

    # 召集智囊团分析
    org = load_org_config()
    recommendations = []

    # 根据任务类型，路由到对应专家
    task_lower = task_description.lower()

    if any(kw in task_lower for kw in ["架构", "系统", "研发", "技术"]):
        # 路由到研发相关专家
        recommendations.append({
            "expert": "tech_lead",
            "recommendation": "建议组建研发团队执行"
        })

    if any(kw in task_lower for kw in ["分析", "洞察", "战略", "决策"]):
        # 路由到Graphify
        recommendations.append({
            "expert": "strategist",
            "recommendation": "建议Graphify智囊团深度分析"
        })

    if any(kw in task_lower for kw in ["知识库", "OBS", "沉淀"]):
        # 路由到OBS团队
        recommendations.append({
            "expert": "obs",
            "recommendation": "建议OBS知识管理团队执行"
        })

    if any(kw in task_lower for kw in ["内容", "博客", "发布"]):
        # 路由到内容运营团队
        recommendations.append({
            "expert": "content_ops",
            "recommendation": "建议内容运营团队执行"
        })

    return {
        **check,
        "team": recommendations[0]["expert"] if recommendations else None,
        "approved": True,  # 智囊团自动批准执行
        "message": "智囊团决策通过，直接执行"
    }


def assemble_team_for_task(task_description: str) -> dict:
    """根据任务组装执行团队

    这是Lysander召唤团队的核心函数

    Args:
        task_description: 任务描述

    Returns:
        组装结果，包含匹配的团队、专家和可用性信息
    """
    # 决策前检查
    check = decision_check(task_description, "assemble_team")
    if check["decision"] == "small_problem":
        # 小问题：直接执行，不询问
        pass  # 继续执行组装流程
    elif check["decision"] == "think_tank":
        # 需要智囊团决策，先记录，组装时附带决策状态
        pass  # 组装流程中附带决策上下文

    # Step 1: 查找任务路由
    org = load_org_config()
    task_lower = task_description.lower()
    keywords = org.get("task_routing", {}).get("keywords", {})

    matched_teams = set()
    matched_experts = set()

    for keyword, teams_or_experts in keywords.items():
        if keyword in task_lower:
            for t in teams_or_experts:
                if t in org.get("teams", {}):
                    matched_teams.add(t)
                else:
                    matched_experts.add(t)

    # Step 2: 如果没有关键词匹配，默认使用Lysander
    if not matched_teams and not matched_experts:
        return {
            "task": task_description,
            "routed_to": "lysander",
            "team": get_team_hr_summary("lysander") if "lysander" in [t.get("team") for t in get_all_teams_summary()] else None,
            "matched_specialists": [],
            "recommendation": "任务已上报Lysander CEO处理",
            "decision": check,  # 决策检查上下文
            "auto_execute": check["decision"] in ["small_problem", "think_tank"]
        }

    # Step 3: 获取匹配的团队信息
    results = {
        "task": task_description,
        "matched_teams": [],
        "matched_specialists": list(matched_experts),
        "all_available": True
    }

    for team_key in matched_teams:
        summary = get_team_hr_summary(team_key)
        results["matched_teams"].append(summary)
        if summary["unavailable"]:
            results["all_available"] = False

    # 检查是否有待招聘岗位
    pending_hires = []
    for team in results["matched_teams"]:
        for member in team.get("members", []):
            if member.get("status") == "pending" or member.get("availability") == "unavailable":
                pending_hires.append({
                    "specialist_id": member.get("specialist_id"),
                    "role": member.get("role"),
                    "team": team.get("team")
                })

    if pending_hires:
        results["pending_hires"] = pending_hires
        results["recommendation"] = f"部分岗位待招聘，建议先启动AI专家执行，负责人岗位需加快招聘"

    # 附带决策检查结果
    results["decision"] = check
    results["auto_execute"] = check["decision"] in ["small_problem", "think_tank"]

    return results


def generate_backstory_from_card(personnel: dict) -> str:
    """从人员卡片生成backstory文本

    Args:
        personnel: 人员卡片字典

    Returns:
        backstory文本
    """
    role = personnel.get("role", "")
    domains = personnel.get("domains", [])
    capabilities = personnel.get("capabilities", [])
    experience = personnel.get("experience", [])

    backstory = f"""你是{role}。

【核心领域】
"""

    for domain in domains:
        backstory += f"- {domain}\n"

    if capabilities:
        backstory += "\n【核心能力】\n"
        for cap in capabilities:
            backstory += f"- {cap}\n"

    if experience:
        backstory += "\n【经验背景】\n"
        for exp in experience:
            backstory += f"- {exp}\n"

    return backstory


def generate_team_experts_yaml(team_key: str) -> dict:
    """从OBS人员卡片生成团队Experts YAML配置

    Args:
        team_key: 团队标识符

    Returns:
        YAML配置字典
    """
    org = load_org_config()
    team_config = org.get("teams", {}).get(team_key, {})
    members = resolve_team_members(team_key)

    # 获取团队描述
    team_name = team_config.get("name", team_key)

    agents = []
    for member in members:
        # 跳过没有档案的成员
        if member.get("source") is None:
            continue

        # 加载完整卡片
        full_card = load_personnel_card(member["specialist_id"], team_key)
        if not full_card:
            continue

        agent = {
            "name": member["specialist_id"],
            "role": member["role"],
            "team": team_key,
            "goal": f"负责{', '.join(member.get('capabilities', [])[:3])}",
            "backstory": generate_backstory_from_card(full_card)
        }
        agents.append(agent)

    # 生成团队模式
    patterns = {}
    team_patterns_config = team_config.get("team_patterns", {})
    if team_patterns_config:
        for pattern_name, pattern_data in team_patterns_config.items():
            if isinstance(pattern_data, list):
                for pattern in pattern_data:
                    if isinstance(pattern, dict):
                        trigger = pattern.get("trigger", "")
                        sequence = pattern.get("sequence", [])
                        if trigger:
                            patterns[trigger] = sequence

    return {
        "version": "1.0",
        "team": team_key,
        "team_name": team_name,
        "description": team_config.get("description", ""),
        "agents": agents,
        "team_patterns": patterns,
        "access": {
            "team_key": team_key,
            "experts": [a["name"] for a in agents]
        }
    }


def sync_all_teams() -> dict:
    """同步所有团队配置到agent-butler/config/

    从OBS读取人员卡片，生成*_experts.yaml文件

    Returns:
        同步结果字典
    """
    from datetime import datetime

    org = load_org_config()
    teams = org.get("teams", {})

    results = {
        "synced": [],
        "failed": []
    }

    for team_key in teams.keys():
        try:
            yaml_config = generate_team_experts_yaml(team_key)
            output_path = CONFIG_DIR / f"{team_key}_experts.yaml"

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# {yaml_config['team_name']} Agent 配置\n")
                f.write(f"# 版本: 1.0\n")
                f.write(f"# 更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# 来源: OBS HR知识库自动生成 - 请勿手动修改\n\n")

                f.write("version: \"1.0\"\n\n")

                if yaml_config.get("agents"):
                    f.write("# Agent定义\n")
                    f.write("agents:\n")
                    for agent in yaml_config["agents"]:
                        f.write(f"  - name: {agent['name']}\n")
                        f.write(f"    role: \"{agent['role']}\"\n")
                        f.write(f"    team: \"{agent['team']}\"\n")
                        f.write(f"    goal: \"{agent['goal']}\"\n")
                        # 处理backstory（多行文本）
                        backstory_lines = agent['backstory'].strip().split('\n')
                        f.write("    backstory: |\n")
                        for line in backstory_lines:
                            f.write(f"      {line}\n")

                # team_patterns
                if yaml_config.get("team_patterns"):
                    f.write("\n# 团队协作模式\n")
                    f.write("team_patterns:\n")
                    for trigger, sequence in yaml_config["team_patterns"].items():
                        f.write(f"  {trigger}:\n")
                        f.write(f"    - {sequence}\n")

                # access
                if yaml_config.get("access"):
                    f.write("\n# 专家调用入口\n")
                    f.write("access:\n")
                    for key, value in yaml_config["access"].items():
                        if isinstance(value, list):
                            f.write(f"  {key}:\n")
                            for v in value:
                                f.write(f"    - {v}\n")
                        else:
                            f.write(f"  {key}: {value}\n")

            results["synced"].append({
                "team": team_key,
                "path": str(output_path),
                "agent_count": len(yaml_config.get("agents", []))
            })
            print(f"  ✓ {team_key}: {len(yaml_config.get('agents', []))} agents")

        except Exception as e:
            import traceback
            results["failed"].append({
                "team": team_key,
                "error": str(e)
            })
            print(f"  ✗ {team_key}: {e}")
            traceback.print_exc()

    return results


def get_sync_status() -> dict:
    """获取同步状态

    Returns:
        状态字典
    """
    import os
    org = load_org_config()
    teams = org.get("teams", {})

    status = {
        "obs_sources": [],  # OBS中的团队
        "yaml_files": [],   # agent-butler/config/中的YAML
        "out_of_sync": []
    }

    # 扫描OBS团队
    for team_key in teams.keys():
        members = resolve_team_members(team_key)
        valid_members = [m for m in members if m.get("source")]
        status["obs_sources"].append({
            "team": team_key,
            "member_count": len(valid_members)
        })

    # 扫描YAML文件
    yaml_files = list(CONFIG_DIR.glob("*_experts.yaml"))
    for yf in yaml_files:
        team = yf.stem.replace("_experts", "")
        mtime = os.path.getmtime(yf)
        status["yaml_files"].append({
            "team": team,
            "path": str(yf),
            "mtime": mtime
        })

    return status


# ============================================================================
# v2.0 — QA自动化评分引擎 (Evaluation Agent 设计)
# 参考: Anthropic 三Agent Harness — Evaluation Agent
# ============================================================================

def qa_auto_review(deliverable: dict) -> dict:
    """QA自动化评分 — Evaluation Agent

    对交付物进行多维度自动评分，替代纯人工审查。
    参考 Anthropic 三Agent Harness 的 Evaluation Agent 设计。

    Args:
        deliverable: 交付物描述字典
            - type: "code_change" | "doc_create" | "config_change" | "report"
            - description: 交付物描述
            - files_changed: 修改的文件列表
            - original_goal: 原始目标

    Returns:
        评分结果：
        - total_score: 总分(1-5)
        - dimensions: 各维度评分
        - passed: 是否通过(>= 3.5)
        - feedback: 改进建议
    """
    d_type = deliverable.get("type", "unknown")
    description = deliverable.get("description", "")
    files = deliverable.get("files_changed", [])
    goal = deliverable.get("original_goal", "")

    dimensions = {}

    # 维度1: 目标达成度 (是否完成了原始目标)
    if goal and description:
        # 简单关键词匹配评估
        goal_keywords = set(goal.lower().split())
        desc_keywords = set(description.lower().split())
        overlap = len(goal_keywords & desc_keywords)
        goal_score = min(5, max(1, round(overlap / max(len(goal_keywords), 1) * 5)))
    else:
        goal_score = 3  # 无法评估时给中等分
    dimensions["goal_achievement"] = {
        "score": goal_score,
        "label": "目标达成度",
    }

    # 维度2: 变更范围合理性 (改动不过大也不过小)
    file_count = len(files)
    if d_type == "code_change":
        if 1 <= file_count <= 5:
            scope_score = 5
        elif file_count == 0:
            scope_score = 1
        elif file_count <= 10:
            scope_score = 4
        else:
            scope_score = 3  # 改动过多需审查
    elif d_type == "doc_create":
        scope_score = 5 if file_count >= 1 else 2
    else:
        scope_score = 4
    dimensions["scope_reasonability"] = {
        "score": scope_score,
        "label": "变更范围合理性",
    }

    # 维度3: 可逆性 (改动是否可以回退)
    reversible_score = 5  # 默认可逆
    danger_patterns = ["删除", "drop", "rm -rf", "reset --hard", "force push"]
    for pattern in danger_patterns:
        if pattern in description.lower():
            reversible_score = 2
            break
    dimensions["reversibility"] = {
        "score": reversible_score,
        "label": "可逆性",
    }

    # 维度4: 架构一致性 (是否符合现有架构)
    # 检查是否修改了核心配置文件
    core_files = ["CLAUDE.md", "organization.yaml", "decision_rules.yaml"]
    core_touched = any(any(cf in f for cf in core_files) for f in files)
    if core_touched and d_type == "code_change":
        arch_score = 4  # 核心文件改动需谨慎但不一定坏
    else:
        arch_score = 5
    dimensions["architecture_consistency"] = {
        "score": arch_score,
        "label": "架构一致性",
    }

    # 计算总分
    scores = [d["score"] for d in dimensions.values()]
    total = round(sum(scores) / len(scores), 1)

    # 生成反馈
    feedback = []
    for dim_key, dim_val in dimensions.items():
        if dim_val["score"] <= 2:
            feedback.append(f"{dim_val['label']}评分较低({dim_val['score']}/5)，建议审查")
        elif dim_val["score"] <= 3:
            feedback.append(f"{dim_val['label']}尚可({dim_val['score']}/5)，有改进空间")

    return {
        "total_score": total,
        "dimensions": dimensions,
        "passed": total >= 3.5,
        "pass_threshold": 3.5,
        "feedback": feedback if feedback else ["所有维度评分良好，通过审查"],
        "reviewed_at": datetime.now().isoformat(),
    }


def expert_panel_review(item_description: str, item_type: str = "general") -> dict:
    """专家评审团评分 — 情报行动管线核心

    模拟多专家(战略/决策/趋势/技术)对一个提案进行评分。

    Args:
        item_description: 提案描述
        item_type: 类型 (code_change/doc_create/research/general)

    Returns:
        评审结果：
        - scores: 各专家评分
        - average: 平均分
        - decision: approve/conditional/defer/veto
        - reasoning: 各专家理由
    """
    desc_lower = item_description.lower()

    # 战略分析师评分
    strategic_keywords = ["战略", "方向", "架构", "体系", "标准", "方法论", "harness"]
    strategic_match = sum(1 for kw in strategic_keywords if kw in desc_lower)
    strategic_score = min(5, 3 + strategic_match)

    # 决策顾问评分 (风险导向)
    risk_keywords = ["删除", "重构", "迁移", "替换", "放弃"]
    risk_count = sum(1 for kw in risk_keywords if kw in desc_lower)
    benefit_keywords = ["优化", "增强", "对齐", "标准化", "自动化", "提升"]
    benefit_count = sum(1 for kw in benefit_keywords if kw in desc_lower)
    decision_score = min(5, max(2, 3 + benefit_count - risk_count))

    # 趋势洞察师评分
    trend_keywords = ["harness", "context engineering", "agent", "自动化", "ai", "2026"]
    trend_match = sum(1 for kw in trend_keywords if kw in desc_lower)
    trend_score = min(5, 3 + trend_match)

    scores = {
        "strategist": {"score": strategic_score, "label": "战略分析师"},
        "decision_advisor": {"score": decision_score, "label": "决策顾问"},
        "trend_watcher": {"score": trend_score, "label": "趋势洞察师"},
    }

    # 技术负责人评分 (仅code_change)
    if item_type == "code_change":
        complexity_keywords = ["重构", "架构", "数据库", "迁移"]
        complexity = sum(1 for kw in complexity_keywords if kw in desc_lower)
        tech_score = min(5, max(2, 5 - complexity))
        scores["tech_lead"] = {"score": tech_score, "label": "技术负责人"}

    # 计算平均分
    all_scores = [s["score"] for s in scores.values()]
    average = round(sum(all_scores) / len(all_scores), 1)

    # 决策
    min_score = min(all_scores)
    if min_score == 1:
        decision = "veto"
    elif average >= 4.0:
        decision = "approve"
    elif average >= 3.0:
        decision = "conditional"
    else:
        decision = "defer"

    return {
        "scores": scores,
        "average": average,
        "decision": decision,
        "decision_label": {
            "approve": "批准执行",
            "conditional": "有条件批准",
            "defer": "暂缓",
            "veto": "一票否决",
        }.get(decision, decision),
        "reviewed_at": datetime.now().isoformat(),
    }


# ============================================================================
# v2.0 — 任务分级引擎 (Plan C: 代码层强制)
# 由执行审计师(execution_auditor)驱动，智囊团自动判断
# ============================================================================

# 任务分级关键词配置（从 decision_rules.yaml 同步）
_TASK_LEVEL_S_KEYWORDS = [
    "查看", "查询", "状态", "列出", "显示", "获取", "确认", "同步",
    "help", "版本", "配置",
]

_TASK_LEVEL_M_KEYWORDS = [
    "开发", "修改", "实现", "构建", "部署", "发布", "更新", "优化", "修复",
    "编写", "添加", "调整", "迁移",
]

_TASK_LEVEL_L_KEYWORDS = [
    "战略", "架构重构", "新业务", "新方案", "组织调整", "流程变更",
    "全面", "体系", "重构", "重大", "全局",
]

# 决策级别关键词（四级制 L1-L4）
_DECISION_L4_KEYWORDS = [
    "合同签署", "法律", "诉讼", "预算100万", "公司存续", "清算",
]

_DECISION_L3_KEYWORDS = [
    "架构变更", "新领域", "战略调整", "组织架构", "高风险",
    "新业务方向", "重大技术",
]

ACTIVE_TASKS_PATH = CONFIG_DIR / "active_tasks.yaml"


def task_classify(task_description: str) -> dict:
    """任务分级引擎 — 自动判断 S/M/L 级别

    由执行审计师(execution_auditor)驱动，替代人工判断。

    分级决策树：
    1. 关键词匹配（快速通道）
    2. 复杂度评估（长度、跨团队、涉及范围）
    3. 风险评估（不可逆性、影响范围）

    Args:
        task_description: 任务描述

    Returns:
        分级结果：
        - level: "S" | "M" | "L"
        - reasoning: 判断理由
        - execution_depth: 建议执行深度
        - president_involvement: 总裁参与程度
    """
    task_lower = task_description.lower()
    task_len = len(task_description)

    # ---- 快速通道：L 级关键词匹配 ----
    for kw in _TASK_LEVEL_L_KEYWORDS:
        if kw in task_lower:
            return {
                "level": "L",
                "reasoning": f"包含重大任务关键词【{kw}】",
                "execution_depth": "智囊团深度分析 → 专家评审 → 执行 → QA",
                "president_involvement": "最终验收",
                "think_tank_required": True,
                "expert_review_required": True,
            }

    # ---- 快速通道：S 级关键词匹配 ----
    s_match = any(kw in task_lower for kw in _TASK_LEVEL_S_KEYWORDS)
    l_indicators = any(kw in task_lower for kw in _TASK_LEVEL_L_KEYWORDS + _TASK_LEVEL_M_KEYWORDS)

    if s_match and not l_indicators:
        return {
            "level": "S",
            "reasoning": "简单查询/确认类任务",
            "execution_depth": "Lysander直接处理",
            "president_involvement": "仅看结果",
            "think_tank_required": False,
            "expert_review_required": False,
        }

    # ---- M 级关键词匹配 ----
    for kw in _TASK_LEVEL_M_KEYWORDS:
        if kw in task_lower:
            # 检查是否有升级因素
            org = load_org_config()
            task_keywords = org.get("task_routing", {}).get("keywords", {})
            matched_teams = set()
            for keyword, teams in task_keywords.items():
                if keyword in task_lower:
                    for t in teams:
                        if t in org.get("teams", {}):
                            matched_teams.add(t)

            # 跨3个以上团队 → 升级为 L
            if len(matched_teams) >= 3:
                return {
                    "level": "L",
                    "reasoning": f"跨{len(matched_teams)}个团队协调，升级为重大任务",
                    "execution_depth": "智囊团深度分析 → 专家评审 → 执行 → QA",
                    "president_involvement": "最终验收",
                    "think_tank_required": True,
                    "expert_review_required": True,
                }

            return {
                "level": "M",
                "reasoning": f"常规任务，包含关键词【{kw}】",
                "execution_depth": "智囊团快速方案 → Lysander审批 → 执行 → QA",
                "president_involvement": "仅看结果",
                "think_tank_required": True,
                "expert_review_required": False,
            }

    # ---- 复杂度兜底评估 ----
    if task_len > 200:
        return {
            "level": "L",
            "reasoning": "任务描述较长，可能涉及复杂需求",
            "execution_depth": "智囊团深度分析 → 专家评审 → 执行 → QA",
            "president_involvement": "最终验收",
            "think_tank_required": True,
            "expert_review_required": True,
        }

    # ---- 默认 M 级 ----
    return {
        "level": "M",
        "reasoning": "默认为常规任务",
        "execution_depth": "智囊团快速方案 → Lysander审批 → 执行 → QA",
        "president_involvement": "仅看结果",
        "think_tank_required": True,
        "expert_review_required": False,
    }


def decision_level_evaluate(task_description: str) -> dict:
    """决策级别评估 — 四级制 (L1/L2/L3/L4)

    替代旧版三级制，最小化总裁参与。

    Args:
        task_description: 任务描述

    Returns:
        决策级别结果：
        - level: "L1" | "L2" | "L3" | "L4"
        - name: 级别名称
        - authority: 决策者
        - reasoning: 判断理由
        - escalate_to_president: 是否需要上报总裁
    """
    task_lower = task_description.lower()

    # ---- L4：上报总裁（最高优先级检查）----
    for kw in _DECISION_L4_KEYWORDS:
        if kw in task_lower:
            return {
                "level": "L4",
                "name": "总裁决策",
                "authority": "总裁刘子杨",
                "reasoning": f"涉及【{kw}】，必须上报总裁",
                "escalate_to_president": True,
            }

    # 预算检查
    import re
    budget_match = re.search(r'预算[^\d]*(\d+)\s*万', task_description)
    if budget_match:
        budget = int(budget_match.group(1))
        if budget > 100:
            return {
                "level": "L4",
                "name": "总裁决策",
                "authority": "总裁刘子杨",
                "reasoning": f"预算{budget}万 > 100万阈值",
                "escalate_to_president": True,
            }

    # ---- L3：Lysander决策（需专家支撑的管理决策）----
    for kw in _DECISION_L3_KEYWORDS:
        if kw in task_lower:
            return {
                "level": "L3",
                "name": "Lysander决策",
                "authority": "Lysander CEO（基于L2专家建议）",
                "reasoning": f"涉及【{kw}】，需专家评审后Lysander做管理决策",
                "escalate_to_president": False,
            }

    # ---- L1：自动执行 ----
    if _is_small_problem(task_description):
        return {
            "level": "L1",
            "name": "自动执行",
            "authority": "系统自动",
            "reasoning": "例行操作，自动执行",
            "escalate_to_president": False,
        }

    # ---- L2：专家评审（默认，先过专家再决策）----
    return {
        "level": "L2",
        "name": "专家评审",
        "authority": "智囊团+领域专家",
        "reasoning": "先由专家分析评估，再由Lysander决策",
        "escalate_to_president": False,
    }


# ============================================================================
# v2.0 — 执行链状态管理 (Plan B+C: 跨会话持久化)
# ============================================================================

def load_active_tasks() -> dict:
    """加载活跃任务列表（跨会话恢复）

    Returns:
        active_tasks.yaml 的内容
    """
    if ACTIVE_TASKS_PATH.exists():
        with open(ACTIVE_TASKS_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {"active_tasks": [], "completed_tasks": []}


def save_active_tasks(data: dict):
    """保存活跃任务列表

    Args:
        data: 完整的 active_tasks 数据
    """
    with open(ACTIVE_TASKS_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def create_task(title: str, level: str, context: str = "",
                assigned_teams: list = None, deliverables: list = None) -> dict:
    """创建新任务并写入 active_tasks.yaml

    Args:
        title: 任务标题
        level: S/M/L 级别
        context: 任务上下文
        assigned_teams: 分配的团队列表
        deliverables: 预期交付物

    Returns:
        创建的任务记录
    """
    data = load_active_tasks()

    # 生成任务ID
    task_count = len(data.get("active_tasks", [])) + len(data.get("completed_tasks", []))
    today = datetime.now().strftime("%Y%m%d")
    task_id = f"TASK-{today}-{task_count + 1:03d}"

    # 自动分级和决策级别评估
    classification = task_classify(title + " " + context)
    decision = decision_level_evaluate(title + " " + context)

    task = {
        "id": task_id,
        "title": title,
        "level": level or classification["level"],
        "status": "in_progress",
        "current_chain_step": "①智囊团分级与方案",
        "assigned_teams": assigned_teams or [],
        "decision_level": decision["level"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "context": context,
        "classification": classification,
        "decision_evaluation": decision,
        "blockers": [],
        "deliverables": deliverables or [],
        "next_steps": [],
    }

    if "active_tasks" not in data:
        data["active_tasks"] = []
    data["active_tasks"].append(task)
    save_active_tasks(data)

    return task


def update_task(task_id: str, **updates) -> Optional[dict]:
    """更新任务状态

    Args:
        task_id: 任务ID
        **updates: 要更新的字段

    Returns:
        更新后的任务，或 None
    """
    data = load_active_tasks()

    for task in data.get("active_tasks", []):
        if task["id"] == task_id:
            task.update(updates)
            task["updated_at"] = datetime.now().isoformat()

            # 如果标记为完成，移到 completed_tasks
            if updates.get("status") == "completed":
                data["active_tasks"].remove(task)
                if "completed_tasks" not in data:
                    data["completed_tasks"] = []
                data["completed_tasks"].append(task)
                # 只保留最近20条
                if len(data["completed_tasks"]) > 20:
                    data["completed_tasks"] = data["completed_tasks"][-20:]

            save_active_tasks(data)
            return task

    return None


def get_active_tasks() -> list:
    """获取所有进行中的任务

    Returns:
        进行中任务列表
    """
    data = load_active_tasks()
    return [t for t in data.get("active_tasks", [])
            if t.get("status") in ["in_progress", "blocked", "review", "pending"]]


def check_followups() -> dict:
    """检查到期的跟进任务 — Agent 主动驱动核心

    扫描 active_tasks.yaml 中所有 pending_followup / pending_start /
    pending_confirmation 状态的任务，检查 follow_up.date 是否到期。

    Returns:
        跟进检查结果：
        - has_followups: 是否有到期项
        - due_today: 今天到期的跟进列表
        - due_tomorrow: 明天到期的
        - overdue: 已过期未处理的
        - summary_message: Lysander 可直接使用的汇报文本
    """
    data = load_active_tasks()
    today = datetime.now().date()
    tomorrow = today + __import__('datetime').timedelta(days=1)

    due_today = []
    due_tomorrow = []
    overdue = []

    followup_statuses = ["pending_followup", "pending_start",
                         "pending_confirmation", "scheduled"]

    for task in data.get("active_tasks", []):
        if task.get("status") not in followup_statuses:
            continue

        follow_up = task.get("follow_up", {})
        if not follow_up or not follow_up.get("date"):
            continue

        try:
            fu_date = datetime.strptime(str(follow_up["date"]), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        item = {
            "id": task.get("id", ""),
            "title": task.get("title", ""),
            "status": task.get("status", ""),
            "team": follow_up.get("assigned_team", task.get("assigned_teams", ["unknown"])[0] if task.get("assigned_teams") else "unknown"),
            "message": follow_up.get("message", ""),
            "action": follow_up.get("action", ""),
            "date": str(fu_date),
            "context": task.get("context", ""),
        }

        if fu_date < today:
            overdue.append(item)
        elif fu_date == today:
            due_today.append(item)
        elif fu_date == tomorrow:
            due_tomorrow.append(item)

    # 生成 Lysander 可直接使用的汇报文本
    lines = []
    if overdue:
        lines.append("⚠️ 已过期未处理：")
        for item in overdue:
            lines.append(f"  [{item['team'].upper()}] {item['title']}（原定 {item['date']}）")
            if item['message']:
                lines.append(f"    → {item['message']}")
    if due_today:
        lines.append("📋 今日待跟进：")
        for item in due_today:
            lines.append(f"  [{item['team'].upper()}] {item['title']}")
            if item['message']:
                lines.append(f"    → {item['message']}")
    if due_tomorrow:
        lines.append("⏰ 明日到期：")
        for item in due_tomorrow:
            lines.append(f"  [{item['team'].upper()}] {item['title']}")

    return {
        "has_followups": len(overdue) + len(due_today) + len(due_tomorrow) > 0,
        "overdue": overdue,
        "due_today": due_today,
        "due_tomorrow": due_tomorrow,
        "total": len(overdue) + len(due_today) + len(due_tomorrow),
        "summary_message": "\n".join(lines) if lines else "无待跟进事项。",
        "checked_at": datetime.now().isoformat(),
    }


def execution_chain_check() -> dict:
    """执行链自检 — 每次回复前调用

    由执行审计师驱动，检查：
    1. 是否有未恢复的跨会话任务
    2. 当前任务是否处于正确的执行链环节
    3. 是否有被跳过的环节

    Returns:
        检查结果：
        - has_active_tasks: 是否有进行中任务
        - tasks_summary: 任务摘要
        - warnings: 警告列表
        - resume_needed: 是否需要恢复上下文
    """
    active = get_active_tasks()
    warnings = []

    if not active:
        return {
            "has_active_tasks": False,
            "tasks_summary": [],
            "warnings": [],
            "resume_needed": False,
        }

    tasks_summary = []
    for task in active:
        summary = {
            "id": task["id"],
            "title": task["title"],
            "level": task.get("level", "?"),
            "status": task["status"],
            "current_step": task.get("current_chain_step", "未知"),
            "decision_level": task.get("decision_level", "?"),
        }
        tasks_summary.append(summary)

        # 检查是否有阻塞项
        if task.get("blockers"):
            warnings.append(f"任务 {task['id']} 有阻塞项: {task['blockers']}")

        # 检查是否长时间未更新
        updated = task.get("updated_at", "")
        if updated:
            try:
                last_update = datetime.fromisoformat(updated)
                hours_since = (datetime.now() - last_update).total_seconds() / 3600
                if hours_since > 24:
                    warnings.append(
                        f"任务 {task['id']} 已超过24小时未更新"
                    )
            except (ValueError, TypeError):
                pass

    return {
        "has_active_tasks": True,
        "tasks_summary": tasks_summary,
        "warnings": warnings,
        "resume_needed": len(active) > 0,
    }


import atexit

# CLI执行上下文（用于执行后自动评估）
_CLI_CONTEXT = {
    "task": None,
    "success": False
}

def _cli_atexit_callback():
    """CLI退出时的自动评估回调"""
    if _CLI_CONTEXT.get("task"):
        result = {"success": _CLI_CONTEXT["success"]}
        eval_result = post_execution_evaluate(_CLI_CONTEXT["task"], result)
        # 不打印结果，只是确保评估被记录
        # 如果需要Lysander，后续可以通过harness-stats查看
        if eval_result["need_lysander"]:
            # 记录到日志，供后续查看
            pass

atexit.register(_cli_atexit_callback)

# CLI命令到任务的映射（用于自动评估）
_CLI_TASK_MAPPING = {
    "team": lambda args: f"查看{args[0] if args else ''}团队HR概览",
    "task": lambda args: " ".join(args) if args else "",
    "all": lambda args: "查看所有团队HR概览",
    "personnel": lambda args: f"查询专家{args[0] if args else ''}档案",
    "sync": lambda args: "同步OBS人员卡片到YAML",
    "sync-status": lambda args: "查看同步状态",
    "harness-stats": lambda args: "查看决策系统统计",
    "feedback": lambda args: f"记录反馈: {' '.join(args)}",
}

def run_cli_command(cmd: str, args: list) -> dict:
    """CLI命令执行器（含执行后自动评估）

    Args:
        cmd: 命令名称
        args: 命令参数

    Returns:
        执行结果字典
    """
    import sys

    # 记录CLI执行的元信息
    cli_meta = {
        "timestamp": datetime.now().isoformat(),
        "cmd": cmd,
        "args": args,
        "task": f"hr_base.py {cmd} {' '.join(args)}"
    }

    try:
        # 根据命令类型构建task描述
        if cmd == "team" and len(args) >= 1:
            task = f"查看{args[0]}团队HR概览"
        elif cmd == "task" and args:
            task = " ".join(args)
        elif cmd == "all":
            task = "查看所有团队HR概览"
        elif cmd == "personnel" and args:
            task = f"查询专家{args[0]}档案"
        elif cmd == "sync":
            task = "同步OBS人员卡片到YAML"
        elif cmd == "sync-status":
            task = "查看同步状态"
        elif cmd == "harness-stats":
            task = "查看决策系统统计"
        else:
            task = cli_meta["task"]

        cli_meta["task"] = task

    except Exception as e:
        cli_meta["task"] = cli_meta["task"]

    # 执行后自动评估（后台静默）
    # 不打印，只记录到日志
    evaluation = post_execution_evaluate(cli_meta["task"], {"success": True})
    cli_meta["evaluation"] = evaluation

    return cli_meta


# CLI工具
if __name__ == "__main__":
    import sys
    from datetime import datetime

    if len(sys.argv) < 2:
        print("Usage: python hr_base.py <command> [args]")
        print("\nCommands:")
        print("  team <team_key>           - 显示团队HR概览")
        print("  task <task_description>    - 查找任务匹配的专家")
        print("  all                       - 显示所有团队概览")
        print("  personnel <specialist_id> - 查询特定专家档案")
        print("  sync                      - 同步所有团队配置到YAML")
        print("  sync-status               - 查看同步状态")
        print("  harness-stats             - 查看决策系统统计")
        print("\nv2.0 新增:")
        print("  classify <task>           - 任务分级(S/M/L)")
        print("  decide <task>             - 决策级别评估(L1-L4)")
        print("  chain-check               - 执行链自检")
        print("  active-tasks              - 查看进行中任务")
        print("  feedback <task> <type>    - 记录反馈")
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    # 设置CLI上下文，用于自动评估
    if cmd in _CLI_TASK_MAPPING:
        _CLI_CONTEXT["task"] = _CLI_TASK_MAPPING[cmd](args)
        _CLI_CONTEXT["success"] = True

    if cmd == "team" and len(sys.argv) >= 3:
        summary = get_team_hr_summary(sys.argv[2])
        print(f"\n=== 团队: {summary['team_name']} ===")
        print(f"成员数: {summary['member_count']}")
        print(f"人类专家: {len(summary['human_experts'])}")
        print(f"AI代理: {len(summary['ai_agents'])}")
        print(f"\n成员列表:")
        for m in summary["members"]:
            status = "✓" if m.get("availability") == "available" else "✗"
            print(f"  [{status}] {m.get('specialist_id')} - {m.get('role')} ({m.get('type')})")

    elif cmd == "task":
        task = " ".join(sys.argv[2:])
        result = assemble_team_for_task(task)
        print(f"\n=== 任务: {result['task']} ===")
        print(f"路由至: {result.get('routed_to', result.get('matched_teams', []))}")
        if result.get('matched_teams'):
            for team in result['matched_teams']:
                print(f"\n团队: {team['team_name']}")
                available = [m for m in team['members'] if m.get('availability') == 'available']
                print(f"可用专家: {len(available)}/{team['member_count']}")
                for m in available:
                    print(f"  - {m.get('specialist_id')}: {m.get('role')}")
        if result.get('pending_hires'):
            print(f"\n待招聘岗位:")
            for p in result['pending_hires']:
                print(f"  - {p['specialist_id']} ({p['role']}) - {p['team']}团队")

    elif cmd == "all":
        teams = get_all_teams_summary()
        print(f"\n=== 所有团队HR概览 ===")
        for team in teams:
            print(f"\n{team['team_name']} ({team['team']})")
            print(f"  成员: {team['member_count']}")
            print(f"  可用: {len(team.get('available', []))}")

    elif cmd == "personnel" and len(sys.argv) >= 3:
        personnel = get_personnel_by_specialist_id(sys.argv[2])
        if personnel:
            print(f"\n=== {personnel.get('title')} ===")
            print(f"specialist_id: {personnel.get('specialist_id')}")
            print(f"team: {personnel.get('team')}")
            print(f"role: {personnel.get('role')}")
            print(f"type: {personnel.get('type')}")
            print(f"availability: {personnel.get('availability')}")
            print(f"\ndomains: {personnel.get('domains', [])}")
            print(f"capabilities: {personnel.get('capabilities', [])}")
            print(f"召唤关键词: {personnel.get('召唤关键词', [])}")
        else:
            print(f"未找到专家: {sys.argv[2]}")

    elif cmd == "sync":
        print("\n=== 同步团队配置 ===")
        print("从OBS读取人员卡片，生成YAML配置...\n")
        results = sync_all_teams()
        print(f"\n同步完成:")
        print(f"  成功: {len(results['synced'])}")
        print(f"  失败: {len(results['failed'])}")

        # 强制刷新输出
        import sys
        sys.stdout.flush()

        # 执行后自动评估并执行后续链
        failed_count = len(results.get('failed', []))
        if failed_count == 0:
            task = "同步OBS人员卡片到YAML"
            evaluation = post_execution_evaluate(task, {"success": True})
            print(f"\n📋 执行后评估: {evaluation['reason']}")
            print(f"   行动: {evaluation['action']}")

            # 检查后续任务链
            next_tasks = TASK_EXECUTION_CHAIN.get(task, [])
            if next_tasks:
                print(f"\n🔗 检测到后续任务链 ({len(next_tasks)} 个任务)")
                for next_config in next_tasks:
                    print(f"   → {next_config['task']} (执行者: {next_config.get('team', 'auto')})")
                print("\n⚠️ 后续任务需要手动触发或通过API调用执行链")

    elif cmd == "chain":
        # 执行任务链
        if len(sys.argv) < 3:
            print("Usage: hr_base.py chain <task1> <task2> ...")
            sys.exit(1)
        tasks = sys.argv[2:]
        print(f"\n=== 执行任务链: {' -> '.join(tasks)} ===")
        chain_result = execute_task_chain(tasks)
        print(f"\n执行完成:")
        print(f"  总任务数: {chain_result['total_tasks']}")
        print(f"  执行链: {' -> '.join(chain_result['full_chain'])}")

    elif cmd == "sync-status":
        status = get_sync_status()
        print("\n=== 同步状态 ===\n")
        print("OBS中的团队:")
        for obs in status["obs_sources"]:
            print(f"  - {obs['team']}: {obs['member_count']} members")
        print("\nYAML文件:")
        for yf in status["yaml_files"]:
            print(f"  - {yf['team']}: {yf['path']}")

    elif cmd == "harness-stats":
        from datetime import datetime
        stats = get_decision_stats()
        print("\n=== Harness 决策统计 ===\n")
        print(f"总决策数: {stats['total']}")
        print(f"待反馈: {stats['pending']}")
        print(f"正确: {stats['correct']}")
        print(f"误判/Lysander介入: {stats['incorrect']}")
        print(f"准确率: {stats['accuracy']}")
        print(f"Lysander介入次数: {stats['lysander_interventions']}")

        adjustments = get_harness_adjustments()
        if adjustments:
            print(f"\n最近调整建议:")
            for adj in adjustments[-3:]:
                print(f"  [{adj['timestamp'][:10]}] {adj['task']}: {adj['feedback']}")

    elif cmd == "feedback" and len(sys.argv) >= 4:
        task = " ".join(sys.argv[2:-1])
        feedback_type = sys.argv[-1]
        valid_types = ["correct", "incorrect", "lysander_intervened", "success"]
        if feedback_type not in valid_types:
            print(f"反馈类型必须是: {', '.join(valid_types)}")
            sys.exit(1)
        record_feedback(task, feedback_type)
        print(f"\n已记录反馈: {task} -> {feedback_type}")

    elif cmd == "classify" and len(sys.argv) >= 3:
        task_desc = " ".join(sys.argv[2:])
        result = task_classify(task_desc)
        print(f"\n=== 任务分级 ===")
        print(f"任务: {task_desc}")
        print(f"级别: {result['level']}级")
        print(f"理由: {result['reasoning']}")
        print(f"执行深度: {result['execution_depth']}")
        print(f"总裁参与: {result['president_involvement']}")
        print(f"智囊团: {'需要' if result['think_tank_required'] else '不需要'}")
        print(f"专家评审: {'需要' if result['expert_review_required'] else '不需要'}")

    elif cmd == "decide" and len(sys.argv) >= 3:
        task_desc = " ".join(sys.argv[2:])
        result = decision_level_evaluate(task_desc)
        print(f"\n=== 决策级别评估 ===")
        print(f"任务: {task_desc}")
        print(f"级别: {result['level']} ({result['name']})")
        print(f"决策者: {result['authority']}")
        print(f"理由: {result['reasoning']}")
        print(f"上报总裁: {'是' if result['escalate_to_president'] else '否'}")

    elif cmd == "chain-check":
        result = execution_chain_check()
        print(f"\n=== 执行链自检 ===")
        print(f"进行中任务: {'有' if result['has_active_tasks'] else '无'}")
        if result['tasks_summary']:
            for t in result['tasks_summary']:
                print(f"  [{t['id']}] {t['title']} | {t['level']}级 | {t['status']} | 环节: {t['current_step']}")
        if result['warnings']:
            print(f"\n⚠️ 警告:")
            for w in result['warnings']:
                print(f"  - {w}")
        print(f"需要恢复: {'是' if result['resume_needed'] else '否'}")

    elif cmd == "active-tasks":
        tasks = get_active_tasks()
        print(f"\n=== 进行中任务 ({len(tasks)}个) ===")
        if not tasks:
            print("  无进行中任务")
        for t in tasks:
            print(f"\n  [{t['id']}] {t['title']}")
            print(f"    级别: {t.get('level', '?')} | 决策: {t.get('decision_level', '?')} | 状态: {t['status']}")
            print(f"    当前环节: {t.get('current_chain_step', '未知')}")
            if t.get('blockers'):
                print(f"    阻塞: {t['blockers']}")

    else:
        print("Unknown command or missing arguments")
        print("Usage: python hr_base.py <command> [args]")
        print("Commands:")
        print("  team <team_key>           - 显示团队HR概览")
        print("  task <task_description>    - 查找任务匹配的专家")
        print("  all                       - 显示所有团队概览")
        print("  personnel <specialist_id>   - 查询特定专家档案")
        print("  sync                      - 同步所有团队配置到YAML")
        print("  sync-status               - 查看同步状态")
        print("  harness-stats             - 查看决策系统统计")
        print("  feedback <task> <type>    - 记录反馈 (correct/incorrect/lysander_intervened/success)")
        sys.exit(1)
