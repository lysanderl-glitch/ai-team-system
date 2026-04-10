"""
WBS交付风险自动识别与预警脚本
基于WBS主表数据，从工期、依赖、资源、复杂度四个维度分析交付风险，
自动识别高/中/低风险项并生成结构化预警报告。
支持6条并行执行流(P-EX1~EX6)和5个角色(PM/DE/SA/CDE/Sales)的风险分析。
由 janus_pmo_auto 负责运维
"""
import sys
import os
from collections import defaultdict

from wbs_data_source import get_wbs_source, STAGE_ROLE_MAP, get_roles_for_task

# ── 并行执行流定义 ─────────────────────────────────────────────────────
PARALLEL_FLOWS = {
    "P-EX1": {"name": "项目管理主线", "prefixes": ["S", "DA", "DP", "DO", "DC", "DT", "DU", "DV"]},
    "P-EX2": {"name": "软件部署", "prefixes": ["DD"]},
    "P-EX3": {"name": "静态数字化", "prefixes": ["DS"]},
    "P-EX4": {"name": "动态数字化", "prefixes": ["DY"]},
    "P-EX5": {"name": "业务调研→RCC→初始化", "prefixes": ["DB", "DR", "DI"]},
    "P-EX6": {"name": "外立面视觉", "prefixes": ["DS007", "DS008"]},
}


# ══════════════════════════════════════════════════════════════════════
#  数据加载与基础计算
# ══════════════════════════════════════════════════════════════════════

def load_wbs_tasks(filepath=None):
    """从WBS数据源加载所有任务，并附加关键路径计算字段"""
    source = get_wbs_source(filepath)
    raw_tasks = source.load_tasks()

    tasks = {}
    for code, t in raw_tasks.items():
        tasks[code] = {
            **t,
            "es": 0,
            "ef": 0,
            "ls": 0,
            "lf": 0,
            "float": 0,
        }

    return tasks, source.get_source_name()


def build_successors(tasks):
    """构建后继任务映射"""
    successors = defaultdict(list)
    for code, task in tasks.items():
        for dep in task["deps"]:
            if dep in tasks:
                successors[dep].append(code)
    return successors


def topological_sort(tasks):
    """拓扑排序（Kahn算法）"""
    in_degree = {code: 0 for code in tasks}
    successors = build_successors(tasks)

    for code, task in tasks.items():
        for dep in task["deps"]:
            if dep in tasks:
                in_degree[code] += 1

    queue = [code for code, deg in in_degree.items() if deg == 0]
    order = []

    while queue:
        queue.sort()
        node = queue.pop(0)
        order.append(node)
        for succ in successors[node]:
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)

    return order


def forward_pass(tasks, order):
    """正向推算：计算最早开始/结束时间"""
    for code in order:
        task = tasks[code]
        if task["deps"]:
            task["es"] = max(
                tasks[dep]["ef"]
                for dep in task["deps"]
                if dep in tasks
            )
        else:
            task["es"] = 0
        task["ef"] = task["es"] + task["duration"]


def backward_pass(tasks, order, successors):
    """逆向推算：计算最晚开始/结束时间"""
    project_end = max(task["ef"] for task in tasks.values())

    for task in tasks.values():
        task["lf"] = project_end

    for code in reversed(order):
        task = tasks[code]
        succs = successors[code]
        if succs:
            task["lf"] = min(tasks[s]["ls"] for s in succs if s in tasks)
        task["ls"] = task["lf"] - task["duration"]
        task["float"] = task["ls"] - task["es"]


def compute_critical_path(tasks):
    """执行完整的关键路径计算，返回 (拓扑序, 后继映射, 关键路径编码集合)"""
    order = topological_sort(tasks)
    forward_pass(tasks, order)
    successors = build_successors(tasks)
    backward_pass(tasks, order, successors)

    critical_set = set(
        code for code in order
        if abs(tasks[code]["float"]) < 0.01 and tasks[code]["duration"] > 0
    )
    return order, successors, critical_set


def get_flow_for_task(wbs_code):
    """判定任务所属的并行执行流"""
    # P-EX6 用精确前缀匹配（DS007/DS008优先于DS）
    for flow_id, flow_def in sorted(PARALLEL_FLOWS.items(),
                                     key=lambda x: -max(len(p) for p in x[1]["prefixes"])):
        for prefix in flow_def["prefixes"]:
            if wbs_code == prefix:
                return flow_id
            if wbs_code.startswith(prefix) and (
                len(wbs_code) == len(prefix)
                or not wbs_code[len(prefix):][0].isalpha()
                or wbs_code[len(prefix):][0].islower()
            ):
                return flow_id
    return None


# ══════════════════════════════════════════════════════════════════════
#  风险分析引擎
# ══════════════════════════════════════════════════════════════════════

class RiskItem:
    """单条风险"""
    HIGH = "🔴 高"
    MEDIUM = "🟡 中"
    LOW = "🟢 低"

    def __init__(self, severity, category, wbs_code, task_name, description):
        self.severity = severity
        self.category = category
        self.wbs_code = wbs_code
        self.task_name = task_name
        self.description = description


def analyze_schedule_risks(tasks, critical_set):
    """工期风险分析"""
    risks = []

    for code, t in tasks.items():
        if t["duration"] <= 0:
            continue

        # L3任务工期 > 15天
        if t["level"] == 3 and t["duration"] > 15:
            risks.append(RiskItem(
                RiskItem.HIGH, "工期风险", code, t["name"],
                f"L3任务工期过长({t['duration']:.0f}天 > 15天阈值)，建议拆分为更小的可交付物"
            ))

        # 关键路径任务工期 > 10天
        if code in critical_set and t["duration"] > 10:
            risks.append(RiskItem(
                RiskItem.HIGH, "工期风险", code, t["name"],
                f"关键路径任务工期偏长({t['duration']:.0f}天 > 10天阈值)，零浮动无缓冲，延误直接影响项目总工期"
            ))

        # 识别压缩机会：非关键路径且浮动充足的长任务
        if code not in critical_set and t["duration"] > 10 and t["float"] > 5:
            risks.append(RiskItem(
                RiskItem.LOW, "工期风险", code, t["name"],
                f"存在工期压缩机会：工期{t['duration']:.0f}天，浮动{t['float']:.0f}天，"
                f"可抽调资源支援关键路径"
            ))

    return risks


def analyze_dependency_risks(tasks, order, successors):
    """依赖风险分析"""
    risks = []

    # 1) 汇聚点：2个以上前置依赖的任务
    for code, t in tasks.items():
        valid_deps = [d for d in t["deps"] if d in tasks]
        if len(valid_deps) >= 2:
            severity = RiskItem.HIGH if len(valid_deps) >= 3 else RiskItem.MEDIUM
            dep_names = ", ".join(valid_deps[:5])
            risks.append(RiskItem(
                severity, "依赖风险", code, t["name"],
                f"依赖汇聚点：{len(valid_deps)}个前置任务({dep_names})，"
                f"任一延误都会阻塞本任务"
            ))

    # 2) 长依赖链 > 5个顺序任务
    def _chain_length(code, visited=None):
        """递归计算从code开始的最长后继链长度"""
        if visited is None:
            visited = set()
        if code in visited:
            return 0
        visited.add(code)
        succs = successors.get(code, [])
        if not succs:
            return 1
        return 1 + max(_chain_length(s, visited) for s in succs)

    # 从没有前置依赖的任务开始，计算最长链
    roots = [code for code in order if not tasks[code]["deps"] and tasks[code]["duration"] > 0]
    checked_chains = set()
    for root in roots:
        chain_len = _chain_length(root)
        if chain_len > 5 and root not in checked_chains:
            checked_chains.add(root)
            risks.append(RiskItem(
                RiskItem.MEDIUM, "依赖风险", root, tasks[root]["name"],
                f"长依赖链起点：从此任务出发有{chain_len}层顺序依赖，"
                f"链条越长延误传播风险越大"
            ))

    # 3) 跨执行流依赖
    for code, t in tasks.items():
        task_flow = get_flow_for_task(code)
        if task_flow is None:
            continue
        for dep in t["deps"]:
            if dep not in tasks:
                continue
            dep_flow = get_flow_for_task(dep)
            if dep_flow is not None and dep_flow != task_flow:
                flow_name = PARALLEL_FLOWS[task_flow]["name"]
                dep_flow_name = PARALLEL_FLOWS[dep_flow]["name"]
                risks.append(RiskItem(
                    RiskItem.MEDIUM, "依赖风险", code, t["name"],
                    f"跨执行流依赖：{flow_name}({task_flow}) 依赖 "
                    f"{dep_flow_name}({dep_flow})的 {dep}，"
                    f"跨流协调增加沟通与同步成本"
                ))

    return risks


def analyze_resource_risks(tasks, critical_set):
    """资源风险分析"""
    risks = []

    # 构建角色→任务时间段映射（用ES/EF近似并行窗口）
    role_timeline = defaultdict(list)  # role -> [(es, ef, wbs_code, name)]

    for code, t in tasks.items():
        if t["duration"] <= 0:
            continue
        roles = get_roles_for_task(code)
        for role in roles:
            role_timeline[role].append((t["es"], t["ef"], code, t["name"]))

    # 1) 检测角色并行任务重叠
    for role, intervals in role_timeline.items():
        intervals.sort(key=lambda x: x[0])
        # 扫描线法计算最大并发数
        events = []
        for es, ef, code, name in intervals:
            events.append((es, +1, code, name))
            events.append((ef, -1, code, name))
        events.sort(key=lambda x: (x[0], x[1]))

        concurrent = 0
        max_concurrent = 0
        peak_tasks = []
        active = []
        for time_pt, delta, code, name in events:
            if delta == +1:
                concurrent += 1
                active.append((code, name))
            else:
                concurrent -= 1
                active = [(c, n) for c, n in active if c != code]
            if concurrent > max_concurrent:
                max_concurrent = concurrent
                peak_tasks = list(active)

        if max_concurrent >= 3:
            task_refs = ", ".join(f"{c}" for c, n in peak_tasks[:4])
            severity = RiskItem.HIGH if max_concurrent >= 4 else RiskItem.MEDIUM
            risks.append(RiskItem(
                severity, "资源风险", f"[{role}]", f"角色并发负载",
                f"{role}角色峰值并发{max_concurrent}个任务({task_refs})，"
                f"超载风险高，建议评估是否需要增援或错峰安排"
            ))

    # 2) 关键路径上的单点角色
    critical_role_count = defaultdict(int)
    for code in critical_set:
        roles = get_roles_for_task(code)
        for role in roles:
            critical_role_count[role] += 1

    for role, count in sorted(critical_role_count.items(), key=lambda x: -x[1]):
        if count >= 3:
            risks.append(RiskItem(
                RiskItem.HIGH, "资源风险", f"[{role}]", f"关键路径单点故障",
                f"{role}角色承担{count}个关键路径任务，"
                f"该角色不可用将直接导致项目延期（单点故障风险）"
            ))
        elif count >= 2:
            risks.append(RiskItem(
                RiskItem.MEDIUM, "资源风险", f"[{role}]", f"关键路径暴露",
                f"{role}角色承担{count}个关键路径任务，建议制定备份方案"
            ))

    return risks


def analyze_complexity_risks(tasks):
    """复杂度风险分析"""
    risks = []

    # 构建L3→L4子任务映射（通过WBS编码前缀关系）
    l3_tasks = {code: t for code, t in tasks.items() if t["level"] == 3}
    l4_tasks = {code: t for code, t in tasks.items() if t["level"] == 4}

    # 构建阶段→L4子任务映射
    l3_subtasks = defaultdict(list)  # l3_code -> [l4_tasks]
    for l4_code, l4_task in l4_tasks.items():
        # 找到最匹配的L3父任务（WBS编码前缀最长匹配）
        best_parent = None
        best_len = 0
        for l3_code in l3_tasks:
            if l4_code.startswith(l3_code) and len(l3_code) > best_len:
                best_parent = l3_code
                best_len = len(l3_code)
        if best_parent:
            l3_subtasks[best_parent].append(l4_task)

    # 1) 阶段(L2)下L4子任务过多（>10）
    l2_l4_count = defaultdict(list)  # stage_prefix -> [l4_codes]
    for l4_code, l4_task in l4_tasks.items():
        # 提取L2阶段前缀
        stage = ""
        for i, ch in enumerate(l4_code):
            if ch.isdigit():
                stage = l4_code[:i]
                break
        if stage:
            l2_l4_count[stage].append(l4_code)

    for stage, l4_codes in l2_l4_count.items():
        if len(l4_codes) > 10:
            severity = RiskItem.HIGH if len(l4_codes) > 20 else RiskItem.MEDIUM
            risks.append(RiskItem(
                severity, "复杂度风险", f"[{stage}阶段]", f"阶段子任务密集",
                f"{stage}阶段含{len(l4_codes)}个L4子任务(> 10阈值)，"
                f"管理复杂度高，建议加强过程检查点"
            ))

    # 2) L3任务下同时含并行和顺序L4子任务
    for l3_code, subtasks in l3_subtasks.items():
        if len(subtasks) < 2:
            continue

        has_parallel = False
        has_sequential = False
        pg_set = set()

        for st in subtasks:
            pg = st.get("parallel_group")
            if pg:
                pg_set.add(pg)

        # 检查是否有依赖关系（顺序）
        subtask_codes = set(st["wbs"] for st in subtasks)
        for st in subtasks:
            for dep in st["deps"]:
                if dep in subtask_codes:
                    has_sequential = True
                    break

        # 检查是否有共享并行组（并行）
        if len(pg_set) >= 1:
            # 同一并行组内有多个子任务 = 并行
            pg_members = defaultdict(int)
            for st in subtasks:
                pg = st.get("parallel_group")
                if pg:
                    pg_members[pg] += 1
            if any(count >= 2 for count in pg_members.values()):
                has_parallel = True

        # 没有依赖也没有明确并行组的多子任务，也可能隐含并行
        if not has_sequential and len(subtasks) >= 2:
            has_parallel = True

        if has_parallel and has_sequential:
            l3_name = l3_tasks[l3_code]["name"]
            risks.append(RiskItem(
                RiskItem.MEDIUM, "复杂度风险", l3_code, l3_name,
                f"L3任务下混合编排：同时含并行和顺序L4子任务({len(subtasks)}个)，"
                f"执行协调复杂度较高"
            ))

    return risks


# ══════════════════════════════════════════════════════════════════════
#  报告输出
# ══════════════════════════════════════════════════════════════════════

def print_report(all_risks, tasks, critical_set):
    """输出结构化风险预警报告"""
    project_end = max((t["ef"] for t in tasks.values()), default=0)

    print(f"\n{'═' * 72}")
    print(f"  ⚠️  WBS交付风险预警报告")
    print(f"{'═' * 72}")
    print(f"  项目总工期: {project_end:.0f} 天 | 任务总数: {len(tasks)}")
    print(f"  关键路径任务: {len(critical_set)} 个")
    print(f"{'═' * 72}")

    # 按类别分组
    categories = ["工期风险", "依赖风险", "资源风险", "复杂度风险"]
    categorized = defaultdict(list)
    for r in all_risks:
        categorized[r.category].append(r)

    # 各类别内按严重程度排序
    severity_order = {RiskItem.HIGH: 0, RiskItem.MEDIUM: 1, RiskItem.LOW: 2}

    for cat in categories:
        cat_risks = categorized.get(cat, [])
        cat_risks.sort(key=lambda r: severity_order.get(r.severity, 9))

        high_count = sum(1 for r in cat_risks if r.severity == RiskItem.HIGH)
        med_count = sum(1 for r in cat_risks if r.severity == RiskItem.MEDIUM)
        low_count = sum(1 for r in cat_risks if r.severity == RiskItem.LOW)

        print(f"\n{'─' * 72}")
        print(f"  📋 {cat}  (🔴{high_count} 🟡{med_count} 🟢{low_count})")
        print(f"{'─' * 72}")

        if not cat_risks:
            print(f"  ✅ 未检测到{cat}项")
            continue

        for r in cat_risks:
            print(f"\n  {r.severity}  [{r.wbs_code}] {r.task_name}")
            print(f"        {r.description}")

    # ── 风险汇总 ──
    total_high = sum(1 for r in all_risks if r.severity == RiskItem.HIGH)
    total_med = sum(1 for r in all_risks if r.severity == RiskItem.MEDIUM)
    total_low = sum(1 for r in all_risks if r.severity == RiskItem.LOW)
    total = len(all_risks)

    print(f"\n{'═' * 72}")
    print(f"  📊 风险汇总")
    print(f"{'═' * 72}")
    print(f"  总计: {total} 项风险")
    print(f"    🔴 高风险: {total_high} 项  — 需立即制定缓解措施")
    print(f"    🟡 中风险: {total_med} 项  — 需关注并制定应对预案")
    print(f"    🟢 低风险: {total_low} 项  — 作为优化机会跟踪")

    if total_high > 0:
        print(f"\n  ⚠️ 建议：存在 {total_high} 项高风险，建议在下次项目例会中重点讨论。")

    print(f"\n{'═' * 72}")
    print(f"  报告结束 | 由 janus_pmo_auto 自动生成")
    print(f"{'═' * 72}")


# ══════════════════════════════════════════════════════════════════════
#  主程序入口
# ══════════════════════════════════════════════════════════════════════

def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else None

    if filepath and not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        sys.exit(1)

    print(f"🔍 WBS交付风险自动分析")

    # 加载数据
    tasks, source_name = load_wbs_tasks(filepath)
    print(f"   数据源: {source_name}")
    print(f"   加载 {len(tasks)} 个WBS任务")

    # 关键路径计算
    order, successors, critical_set = compute_critical_path(tasks)

    # 四维风险分析
    all_risks = []
    all_risks.extend(analyze_schedule_risks(tasks, critical_set))
    all_risks.extend(analyze_dependency_risks(tasks, order, successors))
    all_risks.extend(analyze_resource_risks(tasks, critical_set))
    all_risks.extend(analyze_complexity_risks(tasks))

    # 输出报告
    print_report(all_risks, tasks, critical_set)

    return 0


if __name__ == "__main__":
    sys.exit(main())
