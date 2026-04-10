"""
WBS L4工期校验脚本
检查L3父任务工期是否与其下属L4子任务工期一致
支持并行组检测：同一并行组内的L4任务取max而非sum
由 janus_pmo_auto 负责运维
"""
import sys

from wbs_data_source import get_wbs_source


def calc_l4_effective_duration(l4_tasks):
    """
    计算L4子任务的有效工期。
    同一并行组内的任务取max，不同并行组及无并行组的任务求sum。
    """
    parallel_groups = {}
    standalone_sum = 0

    for task in l4_tasks:
        d = task["duration"]
        pg = task["parallel_group"]
        if pg:
            parallel_groups.setdefault(pg, []).append(d)
        else:
            standalone_sum += d

    group_sum = sum(max(durations) for durations in parallel_groups.values())
    return standalone_sum + group_sum


def check_wbs_formulas(filepath=None):
    source = get_wbs_source(filepath)
    raw_tasks = source.load_tasks()

    # 按序号排序以保持原始顺序（L3→L4父子关系依赖顺序）
    sorted_tasks = sorted(raw_tasks.values(), key=lambda t: t.get("wbs", ""))

    issues = []
    current_l3 = None
    l3_duration = 0
    l4_tasks = []

    def _check_l3():
        if current_l3 and l4_tasks:
            effective = calc_l4_effective_duration(l4_tasks)
            if abs(effective - l3_duration) > 0.01:
                status = "⚠️ 超出" if effective > l3_duration else "⚠️ 不足"
                issues.append({
                    "wbs": current_l3["wbs"],
                    "name": current_l3["name"],
                    "l3_duration": l3_duration,
                    "l4_effective": effective,
                    "l4_count": len(l4_tasks),
                    "status": status
                })

    for t in sorted_tasks:
        level_num = t["level"]

        if level_num == 3:
            _check_l3()
            current_l3 = {"wbs": t["wbs"], "name": t["name"]}
            l3_duration = t["duration"]
            l4_tasks = []

        elif level_num == 4 and current_l3:
            l4_tasks.append({
                "duration": t["duration"],
                "parallel_group": t["parallel_group"]
            })

    _check_l3()
    return issues, source.get_source_name()


def main():
    import os
    filepath = sys.argv[1] if len(sys.argv) > 1 else None

    if filepath and not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        sys.exit(1)

    print(f"📋 WBS L4 SUM公式校验")

    issues, source_name = check_wbs_formulas(filepath)
    print(f"   数据源: {source_name}")
    print("=" * 60)

    if not issues:
        print("✅ 所有L3任务工期与L4子任务工期之和一致，无异常。")
    else:
        print(f"发现 {len(issues)} 个工期不一致：\n")
        for i, item in enumerate(issues, 1):
            print(f"  {i}. [{item['status']}] {item['wbs']} {item['name']}")
            print(f"     L3标准工期: {item['l3_duration']}天")
            print(f"     L4有效工期: {item['l4_effective']}天 ({item['l4_count']}个子任务，并行组取max)")
            print(f"     差异: {item['l4_effective'] - item['l3_duration']:+.1f}天")
            print()

    print("=" * 60)
    print(f"校验完成。共 {len(issues)} 个问题。")
    return len(issues)


if __name__ == "__main__":
    sys.exit(0 if main() == 0 else 1)
