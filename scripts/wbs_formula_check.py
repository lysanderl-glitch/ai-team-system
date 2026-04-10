"""
WBS L4工期校验脚本
检查L3父任务工期是否与其下属L4子任务工期一致
支持并行组检测：同一并行组内的L4任务取max而非sum
由 janus_pmo_auto 负责运维
"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import openpyxl
except ImportError:
    print("需要安装 openpyxl: pip install openpyxl")
    sys.exit(1)


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


def check_wbs_formulas(filepath):
    wb = openpyxl.load_workbook(filepath)
    ws = wb["① WBS主表"]

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

    for row in ws.iter_rows(min_row=4, values_only=False):
        wbs_code = row[0].value      # A列: WBS编码
        level = row[1].value         # B列: 层级
        name = row[2].value          # C列: 任务名称
        duration = row[3].value      # D列: 工期
        parallel_group = row[4].value  # E列: 并行组

        if level is None or wbs_code is None:
            continue

        try:
            level_num = float(level)
        except (ValueError, TypeError):
            continue

        if level_num == 3:
            _check_l3()
            current_l3 = {"wbs": wbs_code, "name": name}
            try:
                l3_duration = float(duration) if duration else 0
            except (ValueError, TypeError):
                l3_duration = 0
            l4_tasks = []

        elif level_num == 4 and current_l3:
            try:
                d = float(duration) if duration else 0
            except (ValueError, TypeError):
                d = 0
            l4_tasks.append({
                "duration": d,
                "parallel_group": parallel_group.strip() if isinstance(parallel_group, str) else parallel_group
            })

    _check_l3()
    return issues


def main():
    import os
    # 默认路径，可通过参数覆盖
    default_path = os.path.join(
        os.path.expanduser("~"),
        "Downloads",
        "Janusd_WBS_交付_审查版 (2).xlsx"
    )
    filepath = sys.argv[1] if len(sys.argv) > 1 else default_path

    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        sys.exit(1)

    print(f"📋 WBS L4 SUM公式校验")
    print(f"   文件: {os.path.basename(filepath)}")
    print("=" * 60)

    issues = check_wbs_formulas(filepath)

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
