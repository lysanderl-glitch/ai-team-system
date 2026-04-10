"""
Asana↔Notion 进度看板同步脚本
将Asana项目任务进度同步到Notion项目注册表，用于PMO Command Center看板展示。
可由n8n定时调用（建议集成到WF-04周报自动化或WF-05逾期预警中）。

同步方向：Asana → Notion（单向，Asana为执行真相源）
同步内容：
  - 项目整体进度% = 已完成任务数 / 总任务数
  - 当前里程碑 = 最近未完成的L2阶段名称
  - 健康度 = 基于逾期任务比例自动判定（绿/黄/红）
  - 风险摘要 = 逾期任务top3摘要

调用模式：
  --mode payload（推荐/默认）：
    - 从Notion查询项目列表（由n8n先行查询并传入，或使用NOTION_TOKEN查询）
    - 从Asana拉取进度数据
    - 输出 Notion 更新 payload JSON，由 n8n HTTP Request 节点执行更新
    - ASANA_TOKEN 仍需设置，Notion写操作由n8n完成

  --mode execute：脚本同时负责读写Notion（需 NOTION_TOKEN + ASANA_TOKEN）

由 janus_pmo_auto 负责运维
"""
import sys
import io
import os
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import requests
except ImportError:
    print("需要安装 requests: pip install requests")
    sys.exit(1)

# 环境变量配置
ASANA_TOKEN = os.environ.get("ASANA_TOKEN", "")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_PROJECT_DB_ID = os.environ.get(
    "NOTION_PROJECT_DB_ID",
    "29aba1e3-ddcf-4e72-9680-2e19c290befc"  # 项目注册表 data source ID (新workspace lysanderl@janusd.io)
)

ASANA_HEADERS = {
    "Authorization": f"Bearer {ASANA_TOKEN}",
    "Accept": "application/json",
}
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

ASANA_BASE = "https://app.asana.com/api/1.0"


def get_asana_project_tasks(project_gid):
    """获取Asana项目的所有任务"""
    url = f"{ASANA_BASE}/projects/{project_gid}/tasks"
    params = {
        "opt_fields": "name,completed,due_on,completed_at,assignee.name,memberships.section.name",
        "limit": 100,
    }
    tasks = []
    while url:
        resp = requests.get(url, headers=ASANA_HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        tasks.extend(data.get("data", []))
        next_page = data.get("next_page")
        url = next_page.get("uri") if next_page else None
        params = {}
    return tasks


def calculate_progress(tasks):
    """计算项目进度和健康状态"""
    total = len(tasks)
    if total == 0:
        return {"progress": 0, "health": "🟢 绿色", "milestone": "无任务", "risk_summary": ""}

    completed = sum(1 for t in tasks if t.get("completed"))
    progress = completed / total

    # 逾期任务
    from datetime import date
    today = date.today().isoformat()
    overdue = [
        t for t in tasks
        if not t.get("completed") and t.get("due_on") and t["due_on"] < today
    ]
    overdue_ratio = len(overdue) / total if total else 0

    # 健康度判定
    if overdue_ratio > 0.15:
        health = "🔴 红色"
    elif overdue_ratio > 0.05:
        health = "🟡 黄色"
    else:
        health = "🟢 绿色"

    # 当前里程碑（最近的未完成section）
    sections = set()
    for t in tasks:
        if not t.get("completed"):
            for m in t.get("memberships", []):
                section = m.get("section", {})
                if section.get("name"):
                    sections.add(section["name"])
    milestone = next(iter(sorted(sections)), "进行中") if sections else "已完成"

    # 风险摘要（逾期top3）
    overdue.sort(key=lambda t: t.get("due_on", ""))
    risk_items = [
        f"[逾期] {t['name'][:30]} (截止{t['due_on']})"
        for t in overdue[:3]
    ]
    risk_summary = "; ".join(risk_items) if risk_items else "无逾期风险"

    return {
        "progress": progress,
        "health": health,
        "milestone": milestone,
        "risk_summary": risk_summary,
    }


def update_notion_project(page_id, progress_data):
    """更新Notion项目注册表中的项目进度"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "进度%": {"number": round(progress_data["progress"], 2)},
            "健康度": {"select": {"name": progress_data["health"]}},
            "当前里程碑": {"rich_text": [{"text": {"content": progress_data["milestone"][:100]}}]},
            "风险摘要": {"rich_text": [{"text": {"content": progress_data["risk_summary"][:200]}}]},
        }
    }
    resp = requests.patch(url, headers=NOTION_HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()


def query_notion_projects():
    """查询Notion项目注册表中所有交付中的项目"""
    url = f"https://api.notion.com/v1/databases/{NOTION_PROJECT_DB_ID}/query"
    payload = {
        "filter": {
            "property": "状态",
            "select": {"equals": "交付中"}
        }
    }
    resp = requests.post(url, headers=NOTION_HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json().get("results", [])


def build_notion_update_payload(page_id: str, progress_data: dict) -> dict:
    """构建 Notion 页面更新 payload（不调用 API）"""
    return {
        "notion_api_url": f"https://api.notion.com/v1/pages/{page_id}",
        "notion_api_method": "PATCH",
        "body": {
            "properties": {
                "进度%": {"number": round(progress_data["progress"], 2)},
                "健康度": {"select": {"name": progress_data["health"]}},
                "当前里程碑": {"rich_text": [{"text": {"content": progress_data["milestone"][:100]}}]},
                "风险摘要": {"rich_text": [{"text": {"content": progress_data["risk_summary"][:200]}}]},
            }
        },
    }


def process_project(notion_page: dict) -> dict:
    """
    处理单个项目：从Asana拉取进度，返回结果（不执行Notion更新）。
    返回 {"page_id": ..., "project_name": ..., "progress": ..., "notion_payload": ...}
    """
    props = notion_page.get("properties", {})
    project_name = ""
    title_prop = props.get("项目名称", {}).get("title", [])
    if title_prop:
        project_name = title_prop[0].get("text", {}).get("content", "")

    asana_link_prop = props.get("交付Asana项目链接", {})
    asana_url = asana_link_prop.get("url", "")

    if not asana_url:
        return {"project_name": project_name, "skipped": True, "reason": "无Asana项目链接"}

    parts = asana_url.rstrip("/").split("/")
    project_gid = None
    for i, part in enumerate(parts):
        if part == "0" and i + 1 < len(parts):
            project_gid = parts[i + 1]
            break

    if not project_gid:
        return {"project_name": project_name, "skipped": True, "reason": "无法解析Asana项目ID"}

    tasks = get_asana_project_tasks(project_gid)
    progress = calculate_progress(tasks)
    notion_payload = build_notion_update_payload(notion_page["id"], progress)

    return {
        "page_id": notion_page["id"],
        "project_name": project_name,
        "progress": progress,
        "notion_payload": notion_payload,
        "skipped": False,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Asana → Notion 进度同步")
    parser.add_argument(
        "--mode", choices=["payload", "execute"], default="payload",
        help="payload: 输出Notion更新payload供n8n执行（默认）; execute: 脚本直接更新Notion（需NOTION_TOKEN）",
    )
    # payload模式可接收n8n传入的Notion项目列表JSON（避免脚本查询Notion）
    parser.add_argument("--projects-json", help="JSON字符串：Notion项目列表（payload模式可选，不传则自动查询）")
    args = parser.parse_args()

    if not ASANA_TOKEN:
        print(json.dumps({"success": False, "error": "未设置 ASANA_TOKEN 环境变量"}, ensure_ascii=False))
        sys.exit(1)

    if args.mode == "execute" and not NOTION_TOKEN:
        print(json.dumps({"success": False, "error": "execute模式需要 NOTION_TOKEN 环境变量"}, ensure_ascii=False))
        sys.exit(1)

    # 获取项目列表
    if args.projects_json:
        projects = json.loads(args.projects_json)
    else:
        if not NOTION_TOKEN:
            print(json.dumps({
                "success": False,
                "error": "未提供 --projects-json 且 NOTION_TOKEN 未设置，无法查询项目列表"
            }, ensure_ascii=False))
            sys.exit(1)
        projects = query_notion_projects()

    results = []
    for project in projects:
        try:
            result = process_project(project)
            results.append(result)
        except Exception as e:
            props = project.get("properties", {})
            name = ""
            title_prop = props.get("项目名称", {}).get("title", [])
            if title_prop:
                name = title_prop[0].get("text", {}).get("content", "")
            results.append({"project_name": name, "skipped": True, "reason": str(e)})

    if args.mode == "payload":
        # 输出 payload 列表供 n8n 执行
        notion_updates = [r["notion_payload"] for r in results if not r.get("skipped")]
        output = {
            "success": True,
            "mode": "payload",
            "total": len(projects),
            "to_update": len(notion_updates),
            "skipped": len(projects) - len(notion_updates),
            "notion_updates": notion_updates,  # n8n 遍历此列表执行 HTTP Request
            "summary": [
                {"project": r["project_name"], "skipped": r.get("skipped", False),
                 "progress": r.get("progress", {}).get("progress", 0) if not r.get("skipped") else None}
                for r in results
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    # execute 模式：直接更新 Notion
    synced = 0
    for result in results:
        if result.get("skipped"):
            print(f"  ⚠️ {result['project_name']}: {result.get('reason', '跳过')}")
            continue
        try:
            update_notion_project(result["page_id"], result["progress"])
            print(f"  ✅ {result['project_name']}: 进度{result['progress']['progress']:.0%} 已同步")
            synced += 1
        except Exception as e:
            print(f"  ❌ {result['project_name']}: Notion更新失败 - {e}")

    print(json.dumps({
        "success": True,
        "mode": "execute",
        "synced": synced,
        "total": len(projects),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
