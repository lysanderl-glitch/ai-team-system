"""
WBS关键路径自动识别脚本
基于WBS主表的前置依赖(F列)和工期(D列)，执行正向/逆向推算，
识别零浮动任务组成的关键路径，并输出6条并行流各自的关键路径。
由 janus_pmo_auto 负责运维
"""
import sys
import io
import os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import openpyxl
except ImportError:
    print("需要安装 openpyxl: pip install openpyxl")
    sys.exit(1)


def load_wbs_tasks(filepath):
    """从WBS主表加载所有任务及其依赖关系"""
    wb = openpyxl.load_workbook(filepath)
    ws = wb["① WBS主表"]

    tasks = {}
    for row in ws.iter_rows(min_row=4, values_only=False):
        wbs_code = row[0].value
        level = row[1].value
        name = row[2].value
        duration = row[3].value
        parallel_group = row[4].value
        dependency = row[5].value

        if wbs_code is None or level is None:
            continue

        try:
            level_num = float(level)
            dur = float(duration) if duration else 0
        except (ValueError, TypeError):
            continue

        deps = []
        if dependency:
            deps = [d.strip() for d in str(dependency).split(",")]

        tasks[wbs_code] = {
            "wbs": wbs_code,
            "level": level_num,
            "name": str(name).strip() if name else "",
            "duration": dur,
            "parallel_group": str(parallel_group).strip() if parallel_group else None,
            "deps": deps,
            "es": 0,   # earliest start
            "ef": 0,   # earliest finish
            "ls": 0,   # latest start
            "lf": 0,   # latest finish
            "float": 0, # total float
        }

    return tasks


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
        # 按WBS编码排序保证稳定输出
        queue.sort()
        node = queue.pop(0)
        order.append(node)
        for succ in successors[node]:
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)

    if len(order) != len(tasks):
        missing = set(tasks.keys()) - set(order)
        print(f"  ⚠️ 检测到循环依赖，涉及: {missing}")

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
    # 找到项目总工期
    project_end = max(task["ef"] for task in tasks.values())

    # 初始化所有任务的最晚结束时间
    for task in tasks.values():
        task["lf"] = project_end

    # 逆序遍历
    for code in reversed(order):
        task = tasks[code]
        succs = successors[code]
        if succs:
            task["lf"] = min(tasks[s]["ls"] for s in succs if s in tasks)
        task["ls"] = task["lf"] - task["duration"]
        task["float"] = task["ls"] - task["es"]


def find_critical_path(tasks, order):
    """识别关键路径（零浮动任务）"""
    return [code for code in order if abs(tasks[code]["float"]) < 0.01 and tasks[code]["duration"] > 0]


def identify_parallel_flows(tasks):
    """识别6条并行执行流"""
    flows = {
        "P-EX1 项目管理主线": ["S", "DA", "DP", "DO", "DC", "DT", "DU", "DV"],
        "P-EX2 软件部署": ["DD"],
        "P-EX3 静态数字化": ["DS"],
        "P-EX4 动态数字化": ["DY"],
        "P-EX5 业务调研→RCC→初始化": ["DB", "DR", "DI"],
        "P-EX6 外立面视觉": ["DS007", "DS008"],
    }

    result = {}
    for flow_name, prefixes in flows.items():
        flow_tasks = []
        for code, task in tasks.items():
            for prefix in prefixes:
                if code == prefix or code.startswith(prefix) and (
                    len(code) == len(prefix) or not code[len(prefix):][0].isalpha()
                    or code[len(prefix):][0].islower()
                ):
                    flow_tasks.append(code)
                    break
        result[flow_name] = flow_tasks
    return result


def main():
    default_path = os.path.join(
        os.path.expanduser("~"),
        "Downloads",
        "Janusd_WBS_交付_审查版 (2).xlsx"
    )
    filepath = sys.argv[1] if len(sys.argv) > 1 else default_path

    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        sys.exit(1)

    print(f"🔍 WBS关键路径分析")
    print(f"   文件: {os.path.basename(filepath)}")
    print("=" * 70)

    tasks = load_wbs_tasks(filepath)
    print(f"\n📊 加载 {len(tasks)} 个WBS任务")

    # 拓扑排序
    order = topological_sort(tasks)

    # 正向推算
    forward_pass(tasks, order)

    # 逆向推算
    successors = build_successors(tasks)
    backward_pass(tasks, order, successors)

    # 关键路径
    critical = find_critical_path(tasks, order)

    project_end = max(task["ef"] for task in tasks.values())
    print(f"📅 项目总工期: {project_end} 天")
    print(f"🔴 关键路径任务数: {len(critical)}")

    print(f"\n{'─' * 70}")
    print("🔴 关键路径（Critical Path）:")
    print(f"{'─' * 70}")
    print(f"{'WBS':<10} {'任务名称':<35} {'工期':>5} {'ES':>6} {'EF':>6} {'浮动':>5}")
    print(f"{'─' * 70}")
    for code in critical:
        t = tasks[code]
        name = t["name"][:30] + "..." if len(t["name"]) > 30 else t["name"]
        print(f"{code:<10} {name:<35} {t['duration']:>5.0f} {t['es']:>6.0f} {t['ef']:>6.0f} {t['float']:>5.1f}")

    # 并行流分析
    flows = identify_parallel_flows(tasks)
    print(f"\n{'=' * 70}")
    print("📊 六条并行执行流分析:")
    print(f"{'=' * 70}")

    for flow_name, flow_codes in flows.items():
        flow_critical = [c for c in flow_codes if c in critical and c in tasks]
        if flow_codes:
            flow_duration = max(
                (tasks[c]["ef"] for c in flow_codes if c in tasks), default=0
            ) - min(
                (tasks[c]["es"] for c in flow_codes if c in tasks), default=0
            )
        else:
            flow_duration = 0
        is_on_critical = "🔴 关键" if flow_critical else "🟢 非关键"
        print(f"\n  {flow_name} [{is_on_critical}]")
        print(f"    任务数: {len(flow_codes)} | 流程工期: {flow_duration:.0f}天 | 关键任务: {len(flow_critical)}个")
        if flow_critical:
            for c in flow_critical[:5]:
                t = tasks[c]
                print(f"      → {c} {t['name'][:40]} ({t['duration']:.0f}天)")

    # 非关键路径中浮动最小的任务（准关键路径）
    print(f"\n{'=' * 70}")
    print("⚠️ 准关键路径（浮动 ≤ 10天的非关键任务）:")
    print(f"{'─' * 70}")
    near_critical = [
        (code, tasks[code]) for code in order
        if 0.01 < tasks[code]["float"] <= 10 and tasks[code]["duration"] > 0
    ]
    near_critical.sort(key=lambda x: x[1]["float"])
    for code, t in near_critical[:15]:
        name = t["name"][:35] + "..." if len(t["name"]) > 35 else t["name"]
        print(f"  {code:<10} {name:<38} 浮动={t['float']:.0f}天 工期={t['duration']:.0f}天")

    if not near_critical:
        print("  无准关键路径任务。")

    print(f"\n{'=' * 70}")
    print(f"分析完成。项目总工期 {project_end:.0f} 天，关键路径 {len(critical)} 个任务。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
