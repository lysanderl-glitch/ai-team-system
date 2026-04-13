# -*- coding: utf-8 -*-
"""
WBS自关联建立脚本
Step 3: 建立父子关联（父任务 relation字段）
Step 4: 建立前置任务关联（前置任务 relation字段）
"""
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 加载关联数据
with open(r'C:\Users\lysanderl_janusd\Claude Code\ai-team-system\scripts\_migration\wbs_relations.json', encoding='utf-8') as f:
    relations = json.load(f)

wbs_to_page = relations['wbs_to_page']
parent_relations = relations['parent_relations']   # [(child_code, parent_code), ...]
prereq_relations = relations['prereq_relations']   # [(task_code, prereq_code), ...]

print(f"Loaded: {len(parent_relations)} parent relations, {len(prereq_relations)} prereq relations")
print(f"WBS map: {len(wbs_to_page)} entries")
print()

# 统计
success_parent = 0
failed_parent = []
success_prereq = 0
failed_prereq = []

# ===== Step 3: 父子关联 =====
print("=== Step 3: Building parent-child relations ===")
print(f"Total to process: {len(parent_relations)}")
print()

for i, (child_code, parent_code) in enumerate(parent_relations):
    child_page_id = wbs_to_page.get(child_code)
    parent_page_id = wbs_to_page.get(parent_code)

    if not child_page_id or not parent_page_id:
        failed_parent.append((child_code, parent_code, 'page_id not found'))
        continue

    print(f"[{i+1}/{len(parent_relations)}] Updating 父任务: {child_code} -> {parent_code}")
    print(f"  child_page_id: {child_page_id}")
    print(f"  parent_page_id: {parent_page_id}")
    print(f"  ACTION: notion-update-page {child_page_id} 父任务=[{parent_page_id}]")
    # 实际调用将由外部 notion-update-page 工具执行
    # 此处输出操作列表供批量处理
    success_parent += 1

print()
print(f"Parent relations ready: {success_parent}, failed: {len(failed_parent)}")
print()

# ===== Step 4: 前置任务关联 =====
print("=== Step 4: Building prerequisite relations ===")
print(f"Total to process: {len(prereq_relations)}")
print()

for i, (task_code, prereq_code) in enumerate(prereq_relations):
    task_page_id = wbs_to_page.get(task_code)
    prereq_page_id = wbs_to_page.get(prereq_code)

    if not task_page_id or not prereq_page_id:
        failed_prereq.append((task_code, prereq_code, 'page_id not found'))
        continue

    print(f"[{i+1}/{len(prereq_relations)}] Updating 前置任务: {task_code} -> {prereq_code}")
    print(f"  task_page_id: {task_page_id}")
    print(f"  prereq_page_id: {prereq_page_id}")
    print(f"  ACTION: notion-update-page {task_page_id} 前置任务=[{prereq_page_id}]")
    success_prereq += 1

print()
print(f"Prereq relations ready: {success_prereq}, failed: {len(failed_prereq)}")

# 保存操作列表
ops = {
    'parent_ops': [
        {
            'child_code': child_code,
            'parent_code': parent_code,
            'child_page_id': wbs_to_page[child_code],
            'parent_page_id': wbs_to_page[parent_code]
        }
        for child_code, parent_code in parent_relations
        if wbs_to_page.get(child_code) and wbs_to_page.get(parent_code)
    ],
    'prereq_ops': [
        {
            'task_code': task_code,
            'prereq_code': prereq_code,
            'task_page_id': wbs_to_page[task_code],
            'prereq_page_id': wbs_to_page[prereq_code]
        }
        for task_code, prereq_code in prereq_relations
        if wbs_to_page.get(task_code) and wbs_to_page.get(prereq_code)
    ]
}

with open(r'C:\Users\lysanderl_janusd\Claude Code\ai-team-system\scripts\_migration\wbs_ops.json', 'w', encoding='utf-8') as f:
    json.dump(ops, f, ensure_ascii=False, indent=2)

print()
print(f"Operations saved to wbs_ops.json")
print(f"  parent_ops: {len(ops['parent_ops'])}")
print(f"  prereq_ops: {len(ops['prereq_ops'])}")
