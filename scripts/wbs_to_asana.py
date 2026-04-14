#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Janusd PMO - WBS → Asana 任务初始化脚本  V1.1
===============================================
从 Notion WBS工序数据库读取工序模板，向已有 Asana 项目批量写入：
  L2 → Asana Task（汇总任务，带 start/due）
  L3 → L2 的 Subtask，同时加入项目（Timeline 可见）
  L4 → L3 的 Subtask（不加入项目）
  ⬡  → Gate 里程碑 Task，加入项目

数据源：Notion 数据库 c8bc3849-bb14-4b88-b6c8-28c590bad0a5
目标：  已由 WF-02 创建好的 Asana 项目（通过 --project-gid 传入）

使用:
    python wbs_to_asana.py \\
        --pat ASANA_PAT \\
        --notion-token NOTION_INTEGRATION_TOKEN \\
        --project-gid ASANA_PROJECT_GID \\
        --start-date 2026-05-01

    # 演练模式（不实际调用 API）
    python wbs_to_asana.py \\
        --pat ASANA_PAT \\
        --notion-token NOTION_INTEGRATION_TOKEN \\
        --project-gid ASANA_PROJECT_GID \\
        --start-date 2026-05-01 \\
        --dry-run
"""

import argparse
import sys
import time
import io
import requests
from datetime import date, timedelta, datetime
from collections import defaultdict, deque

# Windows 兼容：强制 stdout/stderr 使用 UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────────────────
# Asana 常量（与 create_delivery_project.py 完全一致）
# ─────────────────────────────────────────────────────────────────────────────
WORKSPACE_GID = "1213200325138682"
TEAM_GID      = "1213938170960375"

CF = {
    "任务编码":     {"gid": "1213897601825660", "type": "text",   "important": True},
    "标准工期(天)": {"gid": "1213890674565355", "type": "number", "important": True},
    "工序状态":     {"gid": "1213890696992752", "type": "enum",   "important": True,
                    "default_enum_gid": "1213890696992753"},
    "执行角色":     {"gid": "1213890629462159", "type": "text",   "important": False},
    "并行组":       {"gid": "1213890772837264", "type": "text",   "important": False},
    "前置依赖编码": {"gid": "1213890706090861", "type": "text",   "important": False},
    "关键交付物":   {"gid": "1213890706257645", "type": "text",   "important": False},
    "跨流依赖":     {"gid": "1213890696992763", "type": "enum",   "important": False,
                    "no_gid": "1213890696992764"},
}

ASANA_BASE_URL    = "https://app.asana.com/api/1.0"
NOTION_BASE_URL   = "https://api.notion.com/v1"
NOTION_VERSION    = "2022-06-28"
RATE_LIMIT_SLEEP  = 0.18          # Asana 限流间隔（秒）

# Notion WBS 数据库 ID
NOTION_WBS_DB_ID  = "c8bc3849-bb14-4b88-b6c8-28c590bad0a5"

# 跳过的阶段（售前工序不属于交付期）
SKIP_PHASES = {"S-售前"}

# 有效的阶段门标识
GATE_VALUES = {"G2", "G3", "G4", "G5"}


# ─────────────────────────────────────────────────────────────────────────────
# Asana HTTP 工具函数（完全复用 create_delivery_project.py 逻辑）
# ─────────────────────────────────────────────────────────────────────────────
def asana_headers(pat):
    return {
        "Authorization": f"Bearer {pat}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }


def asana_api(method, path, pat, **kwargs):
    """带重试、限流处理的 Asana API 调用"""
    url = ASANA_BASE_URL + path
    for attempt in range(3):
        resp = requests.request(method, url, headers=asana_headers(pat), **kwargs)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 10))
            print(f"    [Asana] 限流，等待 {wait}s ...")
            time.sleep(wait)
            continue
        if resp.status_code == 204:   # DELETE 无 body
            return {}
        if not resp.ok:
            print(f"    [Asana] HTTP {resp.status_code}: {resp.text[:500]}")
        resp.raise_for_status()
        time.sleep(RATE_LIMIT_SLEEP)
        return resp.json().get("data", resp.json())
    raise RuntimeError(f"Asana API 调用失败 {method} {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Notion HTTP 工具函数
# ─────────────────────────────────────────────────────────────────────────────
def notion_headers(token):
    return {
        "Authorization":  f"Bearer {token}",
        "Content-Type":   "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def notion_query_database(db_id, token, filter_body=None, page_size=100):
    """
    分页查询 Notion 数据库，自动翻页直到 has_more=False。
    返回所有 page 对象列表。
    """
    url     = f"{NOTION_BASE_URL}/databases/{db_id}/query"
    results = []
    cursor  = None

    while True:
        body = {"page_size": page_size}
        if filter_body:
            body["filter"] = filter_body
        # 按 序号 升序排列
        body["sorts"] = [{"property": "序号", "direction": "ascending"}]
        if cursor:
            body["start_cursor"] = cursor

        for attempt in range(3):
            resp = requests.post(url, headers=notion_headers(token), json=body)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 5))
                print(f"    [Notion] 限流，等待 {wait}s ...")
                time.sleep(wait)
                continue
            if not resp.ok:
                print(f"    [Notion] HTTP {resp.status_code}: {resp.text[:500]}")
            resp.raise_for_status()
            break

        data     = resp.json()
        results += data.get("results", [])

        if data.get("has_more"):
            cursor = data.get("next_cursor")
        else:
            break

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Notion 属性提取工具
# ─────────────────────────────────────────────────────────────────────────────
def _get_title(props, key):
    """提取 title 类型字段的纯文本"""
    items = props.get(key, {}).get("title", [])
    return "".join(t.get("plain_text", "") for t in items).strip()


def _get_text(props, key):
    """提取 rich_text 类型字段的纯文本"""
    items = props.get(key, {}).get("rich_text", [])
    return "".join(t.get("plain_text", "") for t in items).strip()


def _get_number(props, key):
    """提取 number 类型字段值，不存在返回 None"""
    val = props.get(key, {}).get("number")
    return val  # None if absent


def _get_select(props, key):
    """提取 select 类型字段的 name，不存在返回 None"""
    sel = props.get(key, {}).get("select")
    if sel:
        return sel.get("name")
    return None


def _get_multi_select(props, key):
    """提取 multi_select 类型字段的 name 列表，用逗号拼接"""
    items = props.get(key, {}).get("multi_select", [])
    return ", ".join(i.get("name", "") for i in items)


# ─────────────────────────────────────────────────────────────────────────────
# 1. 从 Notion 读取 WBS 工序
# ─────────────────────────────────────────────────────────────────────────────
def read_wbs_from_notion(notion_token):
    """
    从 Notion WBS工序数据库读取所有工序，返回结构化行列表。

    字段映射：
      WBS编码        (title)      → code
      层级           (number)     → lvl (str)
      任务名称       (text)       → name
      工期(天)       (number)     → dur
      并行组         (select)     → pg
      前置依赖       (text)       → pred  ← 已是逗号分隔WBS编码格式
      负责角色       (multi_sel)  → exec_role
      备注           (text)       → summary (旧备注字段，保留兼容)
      工作说明摘要   (text)       → summary (新字段，写入 Asana notes)
      必须提交       (checkbox)   → must_submit (True 时任务名末尾加 🏁)
      参考模板链接   (url)        → template_url (有值时追加到 notes)
      阶段门         (select)     → gate  (G0-G5，有值则为Gate记录)
      所属阶段       (select)     → phase (过滤：跳过 "S-售前")
      序号           (number)     → seq  (排序键，已由API端排序)

    Gate 处理逻辑：
      - 阶段门字段有值（G2/G3/G4/G5） → lvl="⬡", code=gate值（如"G2"）
      - 普通工序：lvl 取 层级 字段（"1"/"2"/"3"/"4"）
    """
    print(f"  正在查询 Notion 数据库 {NOTION_WBS_DB_ID} ...")
    pages = notion_query_database(NOTION_WBS_DB_ID, notion_token)
    print(f"  共获取 {len(pages)} 条记录")

    rows = []
    for page in pages:
        props = page.get("properties", {})

        # --- 基础字段 ---
        raw_code     = _get_title(props, "WBS编码")
        raw_lvl      = _get_number(props, "层级")       # int or None
        name         = _get_text(props, "任务名称")
        dur_raw      = _get_number(props, "工期(天)")
        pg           = _get_select(props, "并行组") or ""
        pred         = _get_text(props, "前置依赖") or ""
        exec_role    = _get_multi_select(props, "负责角色")
        # 工作说明摘要：优先取新字段，回退到旧备注字段
        summary      = _get_text(props, "工作说明摘要") or _get_text(props, "备注") or ""
        # 新增字段
        must_submit  = props.get("必须提交", {}).get("checkbox", False)
        template_url = props.get("参考模板链接", {}).get("url", "") or ""
        gate         = _get_select(props, "阶段门")       # None 或 "G0"~"G5"
        phase        = _get_select(props, "所属阶段")     # None 或 阶段名

        # --- 跳过售前阶段 ---
        if phase and phase in SKIP_PHASES:
            continue

        # --- 跳过完全空行 ---
        if not raw_code and not name:
            continue

        # --- 判断是否为 Gate 任务 ---
        if gate and gate in GATE_VALUES:
            lvl  = "⬡"
            code = gate   # G2 / G3 / G4 / G5
        else:
            lvl  = str(int(raw_lvl)) if raw_lvl is not None else ""
            code = raw_code

        # --- 工期处理 ---
        try:
            dur = float(dur_raw) if dur_raw is not None else 1.0
        except (TypeError, ValueError):
            dur = 1.0
        dur = max(dur, 1.0)   # 最少1天

        # deliv 字段在 Notion 版本中映射到 summary（原 Excel 的关键交付物列在 Notion 无对应）
        rows.append({
            "code":         code,
            "lvl":          lvl,
            "name":         name,
            "dur":          dur,
            "pg":           pg,
            "pred":         pred,
            "exec_role":    exec_role,
            "deliv":        "",      # Notion 数据库无"关键交付物"字段，留空
            "summary":      summary,
            "must_submit":  must_submit,
            "template_url": template_url,
        })

    print(f"  过滤后有效工序：{len(rows)} 条")
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# 2. 依赖解析 + 日期计算（完全复用 create_delivery_project.py）
# ─────────────────────────────────────────────────────────────────────────────
def parse_preds(pred_str):
    if not pred_str or str(pred_str).strip() in ("起点，无前置依赖", ""):
        return []
    return [p.strip() for p in str(pred_str).replace("，", ",").split(",") if p.strip()]


def add_business_days(from_date, n_days):
    """从 from_date 向后推 n_days 个工作日，返回 due date。
    支持小数天数：0.5天按1天处理，确保至少+1工作日。"""
    n_days_int = max(1, round(float(n_days)))  # 0.5→1, 1→1, 2→2
    d, added = from_date, 0
    while added < n_days_int:
        d += timedelta(days=1)
        if d.weekday() < 5:   # Mon-Fri
            added += 1
    return d


def calc_dates(rows, start_date):
    """拓扑排序推算 L3/L4/Gate 任务日期（完全复用原脚本逻辑）"""
    code_to_row = {r["code"]: r for r in rows if r.get("code")}
    in_scope    = set(code_to_row.keys())
    graph       = defaultdict(list)
    in_degree   = {r["code"]: 0 for r in rows if r.get("code")}

    for r in rows:
        if not r.get("code"):
            continue
        for p in parse_preds(r["pred"]):
            if p in in_scope:
                graph[p].append(r["code"])
                in_degree[r["code"]] += 1

    queue = deque([c for c, d in in_degree.items() if d == 0])
    topo  = []
    while queue:
        node = queue.popleft()
        topo.append(node)
        for succ in graph[node]:
            in_degree[succ] -= 1
            if in_degree[succ] == 0:
                queue.append(succ)

    due = {}
    for code in topo:
        row      = code_to_row[code]
        preds    = [p for p in parse_preds(row["pred"]) if p in in_scope]
        earliest = max((due[p] for p in preds), default=start_date)
        due_d    = add_business_days(earliest, row["dur"] or 1)
        due[code]        = due_d
        row["due_on"]    = due_d.isoformat()
        row["start_on"]  = earliest.isoformat()

    # 对未被拓扑覆盖的行（如孤立节点）设置默认日期
    for r in rows:
        if r.get("code") and "due_on" not in r:
            r["due_on"]   = add_business_days(start_date, r["dur"] or 1).isoformat()
            r["start_on"] = start_date.isoformat()


def calc_l2_dates(rows):
    """用 L3 子任务的 min/max 日期覆写 L2 汇总任务日期"""
    current_l2       = None
    l2_start_buckets = defaultdict(list)
    l2_due_buckets   = defaultdict(list)

    for r in rows:
        if r["lvl"] == "2" and r.get("code"):
            current_l2 = r["code"]
        elif r["lvl"] == "3" and current_l2:
            if r.get("start_on"): l2_start_buckets[current_l2].append(r["start_on"])
            if r.get("due_on"):   l2_due_buckets[current_l2].append(r["due_on"])

    for r in rows:
        code = r.get("code")
        if r["lvl"] == "2" and code:
            if l2_start_buckets[code]: r["start_on"] = min(l2_start_buckets[code])
            if l2_due_buckets[code]:   r["due_on"]   = max(l2_due_buckets[code])


# ─────────────────────────────────────────────────────────────────────────────
# 3. Asana Section 设置 + 自定义字段关联
# ─────────────────────────────────────────────────────────────────────────────
def setup_delivery_section(project_gid, pat, dry_run=False):
    """将默认 Section 重命名为"交付期"，返回 section gid"""
    if dry_run:
        print("  [DRY] Section: 交付期")
        return "DRY_SEC_交付期"

    sections    = asana_api("GET", f"/projects/{project_gid}/sections", pat)
    default_sec = sections[0] if sections else None

    if default_sec:
        asana_api("PUT", f"/sections/{default_sec['gid']}", pat,
                  json={"data": {"name": "交付期"}})
        print(f"  ✓ 默认 Section 已重命名为[交付期] (gid={default_sec['gid']})")
        return default_sec["gid"]

    result = asana_api("POST", f"/projects/{project_gid}/sections", pat,
                       json={"data": {"name": "交付期"}})
    print(f"  ✓ 创建 Section: 交付期")
    return result["gid"]


def attach_custom_fields(project_gid, pat, dry_run=False):
    """关联自定义字段到项目"""
    for name, cf in CF.items():
        if dry_run:
            print(f"  [DRY] 关联字段: {name}")
            continue
        try:
            asana_api("POST", f"/projects/{project_gid}/addCustomFieldSetting", pat,
                      json={"data": {"custom_field": cf["gid"],
                                     "is_important": cf["important"]}})
        except Exception as e:
            # 字段可能已关联，忽略重复错误
            print(f"  [WARN] 关联字段 {name} 时出错（可能已存在）: {e}")
    print(f"  ✓ 已关联 {len(CF)} 个自定义字段")


# ─────────────────────────────────────────────────────────────────────────────
# 4. 任务创建（完全复用 create_delivery_project.py 逻辑）
# ─────────────────────────────────────────────────────────────────────────────
def build_cf_payload(row):
    return {
        CF["任务编码"]["gid"]:     row.get("code") or "",
        CF["执行角色"]["gid"]:     row.get("exec_role") or "",
        CF["并行组"]["gid"]:       row.get("pg") or "",
        CF["前置依赖编码"]["gid"]: row.get("pred") or "",
        CF["关键交付物"]["gid"]:   row.get("deliv") or "",
        CF["标准工期(天)"]["gid"]: float(row["dur"]) if row.get("dur") else None,
        CF["工序状态"]["gid"]:     CF["工序状态"]["default_enum_gid"],
        CF["跨流依赖"]["gid"]:     CF["跨流依赖"]["no_gid"],
    }


def _task_payload(row, project_gid, section_gid, parent_gid):
    """组装 Asana 任务 data dict"""
    name = row.get("name") or row.get("code") or "未命名"
    if row["lvl"] == "⬡":
        name = f"🏁 {name}"
    # 升级2：must_submit → 任务名末尾加 🏁 标记（Gate里程碑已有自己的🏁前缀，不重复）
    if row.get("must_submit") and row["lvl"] != "⬡":
        name = f"{name} 🏁"

    # 升级2：构建 notes（工作说明摘要 + 参考模板链接）
    notes_parts = []
    if row.get("summary"):
        notes_parts.append(row["summary"])
    if row.get("template_url"):
        notes_parts.append(f"📎 参考模板：{row['template_url']}")
    notes = "\n\n".join(notes_parts)

    data = {
        "name":     name,
        "notes":    notes,
        "due_on":   row.get("due_on"),
        "start_on": row.get("start_on"),
    }
    if project_gid:
        data["projects"]      = [project_gid]
        data["memberships"]   = [{"project": project_gid, "section": section_gid}]
        data["custom_fields"] = build_cf_payload(row)
    if parent_gid:
        data["parent"] = parent_gid
    return data


def create_project_task(project_gid, section_gid, row, pat, dry_run=False):
    """创建入项目的 Task（L2 汇总 / Gate 里程碑）"""
    if dry_run:
        print(f"    [DRY] Task [{row['lvl']}] {row['code']!s:10s} "
              f"{str(row.get('name', ''))[:35]}")
        return f"DRY_{row['code']}"
    data = _task_payload(row, project_gid, section_gid, None)
    return asana_api("POST", "/tasks", pat, json={"data": data})["gid"]


def section_insert_task(section_gid, task_gid, insert_after_gid, pat, dry_run=False):
    """升级1：将 task_gid 加入 section，并插入到 insert_after_gid 之后（控制 Timeline 排序）。
    insert_after_gid=None 时插入到 Section 最前。"""
    if dry_run:
        return
    body = {"data": {"task": task_gid}}
    if insert_after_gid:
        body["data"]["insert_after"] = insert_after_gid
    try:
        asana_api("POST", f"/sections/{section_gid}/addTask", pat, json=body)
    except Exception as e:
        print(f"    [WARN] section_insert_task 失败 (task={task_gid}): {e}")


def create_l3_subtask(parent_gid, row, pat, dry_run=False):
    """创建 L3：作为 L2 的 Subtask，不再次加入项目（避免重复加入）"""
    if dry_run:
        print(f"      [DRY] L3-subtask {row['code']!s:10s} "
              f"{str(row.get('name', ''))[:35]}")
        return f"DRY_{row['code']}"
    data = _task_payload(row, None, None, parent_gid)
    return asana_api("POST", "/tasks", pat, json={"data": data})["gid"]


def create_l4_subtask(parent_gid, row, pat, dry_run=False):
    """创建 L4：作为 L3 的 Subtask，不加入项目"""
    if dry_run:
        print(f"        [DRY] L4-subtask {row['code']!s:10s} "
              f"{str(row.get('name', ''))[:35]}")
        return f"DRY_{row['code']}"
    data = _task_payload(row, None, None, parent_gid)
    return asana_api("POST", "/tasks", pat, json={"data": data})["gid"]


# ─────────────────────────────────────────────────────────────────────────────
# 5. 依赖链（完全复用 create_delivery_project.py）
# ─────────────────────────────────────────────────────────────────────────────
def wire_dependencies(code_to_gid, rows, pat, dry_run=False):
    """为所有有前置依赖的任务在 Asana 中建立依赖关系"""
    in_scope = set(code_to_gid.keys())
    linked   = 0
    skipped  = 0

    for row in rows:
        task_code = row.get("code")
        if not task_code or task_code not in code_to_gid:
            continue
        preds = [p for p in parse_preds(row["pred"])
                 if p in in_scope and p != task_code]
        if not preds:
            continue

        task_gid = code_to_gid[task_code]
        dep_gids = [code_to_gid[p] for p in preds]

        if dry_run:
            linked += 1
            continue
        try:
            asana_api("POST", f"/tasks/{task_gid}/addDependencies", pat,
                      json={"data": {"dependencies": dep_gids}})
            linked += 1
        except Exception as e:
            print(f"    [WARN] 依赖失败 {task_code}: {e}")
            skipped += 1

    print(f"  ✓ 依赖链：{linked} 条连接，{skipped} 条跳过")


# ─────────────────────────────────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Janusd PMO - WBS → Asana 任务初始化脚本 V1.1"
    )
    parser.add_argument("--pat",           required=True,
                        help="Asana Personal Access Token")
    parser.add_argument("--notion-token",  required=True,
                        help="Notion Internal Integration Secret (secret_xxx)")
    parser.add_argument("--project-gid",   required=True,
                        help="已由 WF-02 创建好的 Asana 项目 GID")
    parser.add_argument("--start-date",    required=True,
                        help="项目启动日期，格式 YYYY-MM-DD")
    parser.add_argument("--dry-run",       action="store_true",
                        help="演练模式，不实际调用 API")
    args = parser.parse_args()

    dry         = args.dry_run
    pat         = args.pat
    notion_tok  = args.notion_token
    project_gid = args.project_gid

    try:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    except ValueError:
        print(f"[ERROR] --start-date 格式错误，期望 YYYY-MM-DD，收到: {args.start_date}")
        sys.exit(1)

    print("=" * 65)
    print("Janusd PMO · WBS → Asana 任务初始化脚本 V1.1")
    if dry:
        print("【演练模式 - 不实际调用 API】")
    print("=" * 65)
    print(f"  Asana 项目 GID : {project_gid}")
    print(f"  项目启动日期   : {start_date}")

    # ── Step 1：从 Notion 读取 WBS ──────────────────────────────
    print("\n[1/5] 从 Notion 读取 WBS 工序模板...")
    if dry:
        # dry-run 模式下 notion_token 可能是假值，直接跳过
        print("  [DRY] 跳过 Notion API 调用，使用 mock 数据演示流程")
        rows = _mock_rows()
    else:
        rows = read_wbs_from_notion(notion_tok)

    if not rows:
        print("[ERROR] 未读取到任何工序记录，请检查 Notion 数据库和 Token。")
        sys.exit(1)

    # 统计各层级
    level_counts = defaultdict(int)
    for r in rows:
        level_counts[r["lvl"]] += 1
    print(f"  层级分布：{ {k: v for k, v in sorted(level_counts.items())} }")

    # ── Step 2：计算工期和日期 ───────────────────────────────────
    print("\n[2/5] 计算工期和日期（拓扑排序）...")
    calc_dates(rows, start_date)
    calc_l2_dates(rows)

    l2_samples = [r for r in rows if r["lvl"] == "2"][:3]
    for r in l2_samples:
        print(f"  [L2] {r['code']:10s} → {r.get('start_on')} ~ {r.get('due_on')}")

    # ── Step 3：设置 Section + 关联自定义字段 ────────────────────
    print("\n[3/5] 设置 Section + 关联自定义字段...")
    section_gid = setup_delivery_section(project_gid, pat, dry)
    attach_custom_fields(project_gid, pat, dry)

    # ── Step 4：创建任务层级 ─────────────────────────────────────
    print("\n[4/5] 创建 Task / Subtask 层级...")

    code_to_gid      = {}   # 全量 code → gid
    current_l2_gid   = None
    current_l2_code  = None
    current_l3_gid   = None
    last_inserted_gid = None  # 升级1：追踪 Section 中最后插入的 L2/Gate GID

    l2_count = l3_count = l4_count = gate_count = 0

    for r in rows:
        code = r.get("code")
        if not code:
            continue
        lvl = r["lvl"]

        if lvl == "1":
            # L1 只是顶层分组，不在 Asana 中创建任务
            continue

        elif lvl == "2":
            gid = create_project_task(project_gid, section_gid, r, pat, dry)
            # 升级1：控制 Section 中的排序，确保按 WBS 序号排列
            section_insert_task(section_gid, gid, last_inserted_gid, pat, dry)
            code_to_gid[code]    = gid
            current_l2_gid       = gid
            current_l2_code      = code
            current_l3_gid       = None
            last_inserted_gid    = gid
            l2_count            += 1
            if not dry:
                print(f"  ▶ L2 Task: {code} | {str(r.get('name', ''))[:40]}")

        elif lvl == "⬡":
            gid = create_project_task(project_gid, section_gid, r, pat, dry)
            # 升级1：Gate 里程碑也按顺序插入 Section
            section_insert_task(section_gid, gid, last_inserted_gid, pat, dry)
            code_to_gid[code]    = gid
            last_inserted_gid    = gid
            gate_count          += 1
            if not dry:
                print(f"  🏁 Gate: {code} | {r.get('name', '')}")

        elif lvl == "3":
            if not current_l2_gid:
                print(f"    [WARN] L3 {code} 无 L2 父任务，跳过")
                continue
            gid = create_l3_subtask(current_l2_gid, r, pat, dry)
            code_to_gid[code]   = gid
            current_l3_gid      = gid
            l3_count           += 1
            if not dry and l3_count % 10 == 0:
                print(f"    ... 已创建 {l3_count} 个 L3 任务")

        elif lvl == "4":
            if not current_l3_gid:
                print(f"    [WARN] L4 {code} 无 L3 父任务，跳过")
                continue
            gid = create_l4_subtask(current_l3_gid, r, pat, dry)
            code_to_gid[code]   = gid
            l4_count           += 1

        else:
            # 未识别层级，跳过
            if lvl:
                print(f"    [WARN] 未识别层级 '{lvl}'，跳过 {code}")

    print(f"\n  ✓ 完成：{l2_count} 个L2任务，{l3_count} 个L3子任务，"
          f"{l4_count} 个L4子任务，{gate_count} 个阶段门")

    # ── Step 5：建立依赖链 ───────────────────────────────────────
    print("\n[5/5] 建立 Asana 依赖链...")
    wire_dependencies(code_to_gid, rows, pat, dry)

    # ── 完成 ─────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    if dry:
        print("演练完成！以上操作在真实运行时将实际执行。")
    else:
        print("✅ 任务初始化完成！")
        print(f"\nAsana 项目链接：")
        print(f"  https://app.asana.com/0/{project_gid}")
    print("=" * 65)


# ─────────────────────────────────────────────────────────────────────────────
# Mock 数据（仅用于 --dry-run 演练，验证脚本逻辑）
# ─────────────────────────────────────────────────────────────────────────────
def _mock_rows():
    """返回少量模拟工序行，用于 dry-run 流程验证"""
    _mk = lambda **kw: {"pg": "", "pred": "", "exec_role": "", "deliv": "",
                         "summary": "", "must_submit": False, "template_url": "", **kw}
    return [
        _mk(code="D.1",     lvl="2", name="需求确认阶段",  dur=5.0,  exec_role="PM"),
        _mk(code="D.1.1",   lvl="3", name="需求调研",       dur=3.0,  exec_role="SA",
            pg="A", summary="完成需求调研"),
        _mk(code="D.1.2",   lvl="3", name="需求评审",       dur=2.0,  exec_role="PM",
            pred="D.1.1", must_submit=True),
        _mk(code="D.1.2.1", lvl="4", name="内部评审",       dur=1.0,  exec_role="SA"),
        _mk(code="D.2",     lvl="2", name="设计阶段",        dur=10.0, exec_role="SA",
            pred="D.1", template_url="https://example.com/template/design"),
        _mk(code="D.2.1",   lvl="3", name="概要设计",        dur=5.0,  exec_role="SA",
            pred="D.1.2"),
        _mk(code="D.2.1.1", lvl="3", name="0.5天小任务",    dur=0.5,  exec_role="SA",
            pred="D.1.2"),
        _mk(code="G2",      lvl="⬡", name="G2 方案评审门",  dur=0.0,  exec_role="PM",
            pred="D.2.1", summary="阶段门里程碑"),
    ]


if __name__ == "__main__":
    main()
