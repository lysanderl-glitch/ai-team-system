# -*- coding: utf-8 -*-
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\lysanderl_janusd\Claude Code\ai-team-system\scripts\_migration\wbs_records.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total records: {len(data)}")
print(f"Fields: {list(data[0].keys())}")
print()

# 建立 WBS编码 -> page_id 映射
wbs_to_page = {}
for r in data:
    code = r.get('WBS编码', '').strip()
    pid = r.get('page_id', '').strip()
    if code and pid:
        wbs_to_page[code] = pid

print(f"WBS codes with page_id: {len(wbs_to_page)}")
print()

# 分析层级关系（推断父级编码）
def get_parent_code(code):
    """从WBS编码推断父级编码"""
    parts = code.split('.')
    if len(parts) <= 1:
        # 如 DS001 -> DS，或 DS -> None
        # 检查是否有数字后缀
        import re
        m = re.match(r'^([A-Za-z]+)(\d+)$', code)
        if m:
            return m.group(1)  # DS001 -> DS
        return None
    else:
        # DS001.1.1 -> DS001.1
        return '.'.join(parts[:-1])

# 提取前置依赖
parent_relations = []  # (child_code, parent_code)
prereq_relations = []  # (task_code, prereq_code)
no_parent = []
no_page_id = []

for r in data:
    code = r.get('WBS编码', '').strip()
    prereq = r.get('前置依赖', '')
    page_id = r.get('page_id', '').strip()

    if not page_id:
        no_page_id.append(code)
        continue

    # 父子关系
    parent = get_parent_code(code)
    if parent:
        if parent in wbs_to_page:
            parent_relations.append((code, parent))
        else:
            no_parent.append((code, parent, '父级不在映射表'))

    # 前置依赖
    if prereq and str(prereq).strip() and str(prereq).strip() not in ['-', 'nan', 'None', '']:
        prereq_str = str(prereq).strip()
        # 可能有多个前置，用逗号或分号分隔
        for p in prereq_str.replace('；', ';').replace('，', ',').split(','):
            p = p.strip().replace(';', '').strip()
            if p and p in wbs_to_page:
                prereq_relations.append((code, p))
            elif p:
                prereq_relations.append((code, f'MISSING:{p}'))

print(f"Parent-child relations found: {len(parent_relations)}")
print(f"Records with missing parent in map: {len(no_parent)}")
print(f"Records with no page_id: {len(no_page_id)}")
print(f"Prerequisite relations found: {len([x for x in prereq_relations if not x[1].startswith('MISSING:')])}")
print(f"Prerequisite relations with missing target: {len([x for x in prereq_relations if x[1].startswith('MISSING:')])}")
print()

# 输出前15条父子关系
print("=== Sample parent-child relations ===")
for child, parent in parent_relations[:15]:
    print(f"  {child} -> parent: {parent}")

print()
print("=== Missing parents ===")
for code, parent, reason in no_parent[:20]:
    print(f"  {code} -> {parent} ({reason})")

print()
print("=== Sample prereq relations ===")
for task, prereq in prereq_relations[:20]:
    print(f"  {task} -> prereq: {prereq}")

# 保存结果为JSON供后续步骤使用
output = {
    'wbs_to_page': wbs_to_page,
    'parent_relations': parent_relations,
    'prereq_relations': [x for x in prereq_relations if not x[1].startswith('MISSING:')],
    'missing_prereqs': [x for x in prereq_relations if x[1].startswith('MISSING:')],
    'no_parent': no_parent,
    'no_page_id': no_page_id
}

with open(r'C:\Users\lysanderl_janusd\Claude Code\ai-team-system\scripts\_migration\wbs_relations.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print()
print("Relations saved to wbs_relations.json")
