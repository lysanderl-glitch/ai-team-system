"""
WBS角色负载分析工具
基于WBS主表分析各角色(PM/DE/SA/CDE/Sales)的任务分布、工期负载、
关键路径暴露度，识别瓶颈角色和资源冲突风险。
由 janus_pmo_auto 负责运维
"""
import sys
import os
from collections import defaultdict

from wbs_data_source import get_wbs_source, get_roles_for_task


def load_tasks(filepath=None):
    """加载WBS任务（L3+L4执行任务）"""
    source = get_wbs_source(filepath)
    raw_tasks = source.load_tasks()

    tasks = []
    for code, t in raw_tasks.items():
        if t["level"] >= 3:
            roles = get_roles_for_task(code)
            tasks.append({
                "wbs": code,
                "level": t["level"],
                "name": t["name"],
                "duration": t["duration"],
                "roles": roles,
            })

    return tasks, source


def load_team_config(source):
    """加载项目团队配置"""
    config = source.load_team_config()
    team = {}
    for item in config:
        if item.get("role") and item.get("person"):
            team[item["role"]] = item["person"]
    return team


def analyze_workload(tasks):
    """分析各角色工作负载"""
    role_stats = defaultdict(lambda: {
        "task_count": 0,
        "total_duration": 0,
        "l3_tasks": [],
        "l4_tasks": [],
        "stages": set(),
        "peak_concurrent": 0,
    })

    for task in tasks:
        for role in task["roles"]:
            stats = role_stats[role]
            stats["task_count"] += 1
            stats["total_duration"] += task["duration"]
            if task["level"] == 3:
                stats["l3_tasks"].append(task)
            else:
                stats["l4_tasks"].append(task)

            # 提取阶段
            stage = ""
            for i, ch in enumerate(task["wbs"]):
                if ch.isdigit():
                    stage = task["wbs"][:i]
                    break
            if stage:
                stats["stages"].add(stage)

    return dict(role_stats)


def main():
    filepath = sys.argv[1] if len(sys.argv) > 1 else None

    if filepath and not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        sys.exit(1)

    print(f"👥 WBS角色负载分析")

    tasks, source = load_tasks(filepath)
    print(f"   数据源: {source.get_source_name()}")
    print("=" * 70)

    team = load_team_config(source)
    workload = analyze_workload(tasks)

    print(f"\n📊 总计 {len(tasks)} 个执行任务（L3+L4）")

    if team:
        print(f"\n👤 项目团队配置:")
        for role, person in team.items():
            print(f"    {role}: {person}")

    # 角色负载总览
    print(f"\n{'=' * 70}")
    print("📊 角色负载总览:")
    print(f"{'─' * 70}")
    print(f"{'角色':<8} {'人员':<12} {'任务数':>6} {'总工期(天)':>10} {'L3':>4} {'L4':>4} {'覆盖阶段':>10}")
    print(f"{'─' * 70}")

    sorted_roles = sorted(workload.items(), key=lambda x: x[1]["total_duration"], reverse=True)
    for role, stats in sorted_roles:
        person = team.get(role, "—")
        stages = ",".join(sorted(stats["stages"]))
        print(f"{role:<8} {person:<12} {stats['task_count']:>6} {stats['total_duration']:>10.0f} "
              f"{len(stats['l3_tasks']):>4} {len(stats['l4_tasks']):>4} {stages:>10}")

    # 负载均衡分析
    print(f"\n{'=' * 70}")
    print("⚖️ 负载均衡分析:")
    print(f"{'─' * 70}")

    durations = [s["total_duration"] for s in workload.values()]
    avg_duration = sum(durations) / len(durations) if durations else 0
    max_duration = max(durations) if durations else 0
    min_duration = min(durations) if durations else 0

    print(f"  平均工期负载: {avg_duration:.0f} 天")
    print(f"  最高工期负载: {max_duration:.0f} 天")
    print(f"  最低工期负载: {min_duration:.0f} 天")
    print(f"  负载差异比: {max_duration/min_duration:.1f}x" if min_duration > 0 else "")

    # 瓶颈识别
    print(f"\n{'=' * 70}")
    print("🔴 瓶颈与风险识别:")
    print(f"{'─' * 70}")

    for role, stats in sorted_roles:
        issues = []
        if stats["total_duration"] > avg_duration * 1.5:
            issues.append(f"工期负载超均值50%+（{stats['total_duration']:.0f} vs 均值{avg_duration:.0f}）")
        if len(stats["stages"]) >= 5:
            issues.append(f"跨{len(stats['stages'])}个阶段，上下文切换成本高")
        if stats["task_count"] > 30:
            issues.append(f"任务数过多（{stats['task_count']}个），管理幅度偏大")

        if issues:
            person = team.get(role, "—")
            print(f"\n  🔴 {role} ({person}):")
            for issue in issues:
                print(f"     → {issue}")

    # 阶段-角色热力图
    print(f"\n{'=' * 70}")
    print("🗺️ 阶段-角色参与矩阵:")
    print(f"{'─' * 70}")

    all_stages = sorted(set(s for stats in workload.values() for s in stats["stages"]))
    all_roles = [r for r, _ in sorted_roles]

    header = f"{'阶段':<6}" + "".join(f"{r:>8}" for r in all_roles)
    print(header)
    print(f"{'─' * 70}")

    for stage in all_stages:
        row = f"{stage:<6}"
        for role in all_roles:
            stage_tasks = [
                t for t in tasks
                if role in t["roles"] and any(
                    t["wbs"].startswith(stage) and (
                        len(t["wbs"]) == len(stage) or t["wbs"][len(stage)].isdigit()
                    )
                    for _ in [1]
                )
            ]
            count = len(stage_tasks)
            if count == 0:
                row += f"{'·':>8}"
            elif count <= 3:
                row += f"{'▪'+str(count):>8}"
            elif count <= 8:
                row += f"{'▪▪'+str(count):>8}"
            else:
                row += f"{'▪▪▪'+str(count):>8}"
        print(row)

    print(f"\n{'=' * 70}")
    print(f"分析完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
