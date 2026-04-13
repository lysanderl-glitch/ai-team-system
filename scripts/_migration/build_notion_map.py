# -*- coding: utf-8 -*-
"""
根据Notion搜索结果建立完整的 WBS编码 -> 真实Notion page_id 映射
只取最新导入的记录（341114fc前缀，2026-04-13）
"""
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

notion_map = {
    'S001': '341114fc-090c-8155-9dfa-e2181fc69541',
    'S002': '341114fc-090c-81c5-be42-e3834898d713',
    'S-D': '341114fc-090c-811e-91e6-e3e24173ec60',
    'D': '341114fc-090c-81a3-8e7d-f9d7a5d7977c',
    'DA': '341114fc-090c-81f9-88ec-fe12a47b99e0',
    'DA001': '341114fc-090c-81af-a7db-fa9ee3e1f976',
    'DA002': '341114fc-090c-811f-8db1-c6c30cf48693',
    'DA003': '341114fc-090c-8181-8549-f7e9533a548f',
    'DA003a': '341114fc-090c-8105-9fb3-e03adecd1232',
    'DA003b': '341114fc-090c-811f-9c32-d23edef1f238',
    'DA003c': '341114fc-090c-81f1-bcce-ff7e3ffa527d',
    'DA003d': '341114fc-090c-812a-9ac9-ec3de6e76dd1',
    'DP': '341114fc-090c-81b6-b2e5-d7d17b7ff1d9',
    'DP001': '341114fc-090c-8114-b362-fae46d160395',
    'DP002': '341114fc-090c-8189-885a-d703eaaf75b1',
    'DP003': '341114fc-090c-813e-aa9e-f8c52d1a58b3',
    'DP004': '341114fc-090c-8182-96d6-e5df937f22b7',
    'DP005': '341114fc-090c-81bf-8b79-d7694f85a0af',
    'DP006': '341114fc-090c-8105-9893-f60991336a71',
    'DO': '341114fc-090c-8147-86ad-e40cf11b3f42',
    'DO001': '341114fc-090c-814b-b65a-d556ff0587cd',
    'DO002': '341114fc-090c-810d-97ae-e95573e629dd',
    'DO003': '341114fc-090c-8184-a933-c6ebc32bd56d',
    'DO004': '341114fc-090c-81e2-83e1-e53d27395a61',
    'DC': '341114fc-090c-814e-8458-f70f0cc2c539',
    'DC001': '341114fc-090c-81da-b7d1-f4ddaa6ea9f8',
    'DC002': '341114fc-090c-81af-8547-f3b3e4869ca5',
    'DC003': '341114fc-090c-81fa-abbc-e91934877b3a',
    'DC004': '341114fc-090c-812d-bd50-ca9ca98d826f',
    'DC005': '341114fc-090c-81b3-b8ba-d439d856b640',
    'DD': '341114fc-090c-81de-989b-e30af1d3aeed',
    'DD001': '341114fc-090c-817b-8285-fd867cba8fc0',
    'DD002': '341114fc-090c-8114-a559-e9b9f4e73131',
    'DD003': '341114fc-090c-81a1-936b-d27f608b29f1',
    'DD004': '341114fc-090c-8141-a16b-c7bf3b46a832',
    'DD005': '341114fc-090c-81a8-8202-f14bdd54416e',
    'DS': '341114fc-090c-81f3-93cf-f27e74454884',
    'DS001': '341114fc-090c-81b0-8d0b-dfb726f8964d',
    'DS002': '341114fc-090c-8168-a440-edf9e41e6cc1',
    'DS003': '341114fc-090c-81d4-bd5c-dfd7cb43c89d',
    'DS004': '341114fc-090c-81df-af80-d81daffd5e0f',
    'DS005': '341114fc-090c-8107-b170-ce4f442ff2c4',
    'DS006': '341114fc-090c-81d4-bea0-d26c6f1a0f16',
    'DS007': '341114fc-090c-8143-bfb6-e5b98c00cf10',
    'DS008': '341114fc-090c-81e5-ba05-e9c6c0c6067a',
    'DS009': '341114fc-090c-810a-bd96-f04f28918c71',
    'DS010': '341114fc-090c-81f1-95d5-eb018b625448',
    'DS011': '341114fc-090c-813f-b20e-de6d44e80722',
    'DS012': '341114fc-090c-81c6-aa75-eeac9028eccd',
    'DY': '341114fc-090c-8147-bc1f-c0514e684f08',
    'DY001': '341114fc-090c-81e4-8c36-edf4c45e6eb3',
    'DY002': '341114fc-090c-81f5-b274-cfb1c2464a1e',
    'DY003': '341114fc-090c-8109-9c3d-d532ab7ab454',
    'DY004': '341114fc-090c-81c8-a71b-c5cbfa5b0102',
    'DY005': '341114fc-090c-8182-a534-fb0639bb85c8',
    'DY006': '341114fc-090c-81b1-9617-cd4f14645784',
    'DY007': '341114fc-090c-8139-b783-d9a933a73ee0',
    'DB': '341114fc-090c-8122-abb2-f8e810d2c748',
    'DB001': '341114fc-090c-81a8-8ebb-cbf9e0138f1c',
    'DB002': '341114fc-090c-8132-ace8-e809961b8963',
    'DB002a': '341114fc-090c-81b3-a306-e8c66fc2bc54',
    'DB002b': '341114fc-090c-8122-be58-ed6dd09363f1',
    'DB003': '341114fc-090c-81c1-9066-e891bde9e206',
    'DB003a': '341114fc-090c-811a-a8a9-c8d990828df0',
    'DB003b': '341114fc-090c-81b7-ac0f-c15bd7f72cd7',
    'DB003c': '341114fc-090c-81ad-80df-faf701ff2a9a',
    'DB003d': '341114fc-090c-813d-b077-de664555a9be',
    'DB003e': '341114fc-090c-8103-a779-d78be0bef07c',
    'DB004': '341114fc-090c-8123-9a21-e56b88e7ec9a',
    'DB004a': '341114fc-090c-8168-a846-c7227d255166',
    'DB004b': '341114fc-090c-812a-9c86-cdc4208c008d',
    'DB005': '341114fc-090c-81e2-950f-dd6fa45d0b88',
    'DB005a': '341114fc-090c-81bc-879a-d27bd326d571',
    'DB005b': '341114fc-090c-81d3-9ea1-d0edd8c72b4c',
    'DB005c': '341114fc-090c-8175-a610-fc623325903f',
    'DB005d': '341114fc-090c-812f-b419-efb048cd0fa6',
    'DB006': '341114fc-090c-8107-8cdd-e6119a0b992d',
    'DB006a': '341114fc-090c-814d-95a9-c97dce6eb70c',
    'DB006b': '341114fc-090c-810b-a245-fafdc75b885d',
    'DB007': '341114fc-090c-8146-8028-c8e65576f198',
    'DR': '341114fc-090c-816f-9216-d631c4970e17',
    'DR001': '341114fc-090c-810e-8f6c-c9ee37ebf1d8',
    'DR002': '341114fc-090c-8151-b6f4-dbdc718c134f',
    'DI': '341114fc-090c-81f4-bb62-ff576eab48a5',
    'DI001': '341114fc-090c-8138-bc62-df957e706d6e',
    'DI003': '341114fc-090c-8106-9cda-ed925c5a7935',
    'DI004': '341114fc-090c-81ca-b62b-e204ecb6fbbf',
    'DI004a': '341114fc-090c-81b9-a70f-fabaf9319720',
    'DI004b': '341114fc-090c-811d-aca0-c4a0a78a04c1',
    'DI004c': '341114fc-090c-8186-b289-d04a299b4ce5',
    'DI005': '341114fc-090c-8176-8ef4-def805d742b2',
    'DI005d': '341114fc-090c-8157-9209-eb698ad4c1d3',
    'DI005e': '341114fc-090c-8176-ae67-dee833d47aed',
    'DI005f': '341114fc-090c-81d0-959e-c8979296b271',
    'DI005g': '341114fc-090c-81a9-82a7-cfb300ca7d9c',
    'DI006': '341114fc-090c-812c-a0d7-faf7667b637f',
    'DT': '341114fc-090c-814e-803c-d54a8f5b8eac',
    'DT001': '341114fc-090c-81e8-b44a-e56204ea0a9c',
    'DT002': '341114fc-090c-81a9-9596-e7dcaf895543',
    'DU': '341114fc-090c-8158-949b-c15edea39f21',
    'DU001': '341114fc-090c-81c2-aef7-d64fc53fa2d2',
    'DU001a': '341114fc-090c-818c-a194-ceeb9ffd4987',
    'DU001b': '341114fc-090c-8161-88bd-d646ef5bdbd3',
    'DU002': '341114fc-090c-819f-8780-ed812a041ca5',
    'DU002a': '341114fc-090c-81cf-a3ed-f4fa971041e5',
    'DU003': '341114fc-090c-81c6-8a45-c67c8411a4db',
    'DU003a': '341114fc-090c-81bc-8215-c7366a196a59',
    'DU003b': '341114fc-090c-81b5-b165-cb73a67ec008',
    'DU004': '341114fc-090c-81a2-8d11-d3203bb0d7ee',
    'DV': '341114fc-090c-8183-8662-c09d750d0714',
    'DV001': '341114fc-090c-8104-8cc4-d11b6ff9d1fc',
    'DV002': '341114fc-090c-81db-9657-e93c8ee1222f',
    'DV003': '341114fc-090c-8186-bcd1-e45b487e19cf',
    'DV004': '341114fc-090c-81a5-80f3-d31b28af3b2c',
    'DV005': '341114fc-090c-81af-afe5-c0cbd7102a1e',
}

# 加载原始记录
data = json.load(open('wbs_records.json', encoding='utf-8'))
all_codes = [r['WBS编码'].strip() for r in data if r.get('WBS编码','').strip()]
print(f'Total WBS codes in source: {len(all_codes)}')
print(f'Total in notion_map: {len(notion_map)}')

found = [c for c in all_codes if c in notion_map]
missing = [c for c in all_codes if c not in notion_map]
print(f'Found: {len(found)}')
print(f'Missing: {len(missing)}')
if missing:
    print('Still missing:', missing)

# 加载关联关系，用notion_map替换wbs_to_page
with open('wbs_relations.json', encoding='utf-8') as f:
    relations = json.load(f)

parent_relations = relations['parent_relations']
prereq_relations = relations['prereq_relations']

# 用真实notion_map重建操作列表
parent_ops = []
prereq_ops = []
failed_parent = []
failed_prereq = []

for child_code, parent_code in parent_relations:
    child_pid = notion_map.get(child_code)
    parent_pid = notion_map.get(parent_code)
    if child_pid and parent_pid:
        parent_ops.append({
            'child_code': child_code,
            'parent_code': parent_code,
            'child_page_id': child_pid,
            'parent_page_id': parent_pid,
        })
    else:
        failed_parent.append((child_code, parent_code,
                               'missing child' if not child_pid else 'missing parent'))

for task_code, prereq_code in prereq_relations:
    task_pid = notion_map.get(task_code)
    prereq_pid = notion_map.get(prereq_code)
    if task_pid and prereq_pid:
        prereq_ops.append({
            'task_code': task_code,
            'prereq_code': prereq_code,
            'task_page_id': task_pid,
            'prereq_page_id': prereq_pid,
        })
    else:
        failed_prereq.append((task_code, prereq_code,
                               'missing task' if not task_pid else 'missing prereq'))

print(f'\nParent ops ready: {len(parent_ops)}, failed: {len(failed_parent)}')
print(f'Prereq ops ready: {len(prereq_ops)}, failed: {len(failed_prereq)}')
if failed_parent:
    print('Failed parent:', failed_parent)
if failed_prereq:
    print('Failed prereq:', failed_prereq)

# 保存
ops = {'parent_ops': parent_ops, 'prereq_ops': prereq_ops}
with open('wbs_ops_v2.json', 'w', encoding='utf-8') as f:
    json.dump(ops, f, ensure_ascii=False, indent=2)
print('\nSaved to wbs_ops_v2.json')
