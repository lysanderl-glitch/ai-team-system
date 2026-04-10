"""
WBS 跨流依赖完整性校验脚本
检查前置依赖链是否存在断链（依赖的WBS编码不存在）
由 janus_pmo_auto 负责运维
"""
import sys

from wbs_data_source import get_wbs_source


def check_dependencies(filepath=None):
    source = get_wbs_source(filepath)
    raw_tasks = source.load_tasks()

    all_codes = set(raw_tasks.keys())
    tasks_with_deps = []

    for code, t in raw_tasks.items():
        if t["deps"]:
            tasks_with_deps.append({
                "wbs": code,
                "name": t["name"],
                "deps": t["deps"],
            })

    # 校验依赖是否存在
    broken = []
    for task in tasks_with_deps:
        for dep in task["deps"]:
            if dep and dep not in all_codes:
                broken.append({
                    "wbs": task["wbs"],
                    "name": task["name"],
                    "missing_dep": dep,
                })

    # 跨流依赖标记
    cross_flow_raw = source.load_cross_flow_deps()
    cross_flow = []
    for item in cross_flow_raw:
        cross_flow.append({
            "wbs": item["wbs"],
            "description": item.get("description", ""),
            "dependency_detail": item.get("detail", ""),
        })

    return broken, cross_flow, len(all_codes), len(tasks_with_deps), source.get_source_name()


def main():
    import os
    filepath = sys.argv[1] if len(sys.argv) > 1 else None

    if filepath and not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        sys.exit(1)

    print(f"🔗 WBS 跨流依赖完整性校验")

    broken, cross_flow, total_codes, total_with_deps, source_name = check_dependencies(filepath)
    print(f"   数据源: {source_name}")
    print("=" * 60)

    print(f"📊 统计: {total_codes} 个WBS编码, {total_with_deps} 个有前置依赖\n")

    if not broken:
        print("✅ 所有前置依赖引用均有效，无断链。")
    else:
        print(f"❌ 发现 {len(broken)} 个断链依赖：\n")
        for i, item in enumerate(broken, 1):
            print(f"  {i}. {item['wbs']} ({item['name']})")
            print(f"     → 依赖 [{item['missing_dep']}] 不存在于WBS编码表")
            print()

    if cross_flow:
        print(f"\n📌 跨流依赖标记 ({len(cross_flow)} 个)：\n")
        for item in cross_flow:
            print(f"  {item['wbs']} {item['description']}")
            print(f"     {item['dependency_detail']}")
            print()

    print("=" * 60)
    print(f"校验完成。断链: {len(broken)}, 跨流依赖: {len(cross_flow)}")
    return len(broken)


if __name__ == "__main__":
    sys.exit(0 if main() == 0 else 1)
