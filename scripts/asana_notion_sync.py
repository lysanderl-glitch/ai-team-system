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
    "33c3e998-20c7-81ee-87a7-000b94b40bf7"  # 项目注册表 data source ID
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


def sync_project(notion_page):
    """同步单个项目"""
    props = notion_page.get("properties", {})
    project_name = ""
    title_prop = props.get("项目名称", {}).get("title", [])
    if title_prop:
        project_name = title_prop[0].get("text", {}).get("content", "")

    asana_link_prop = props.get("交付Asana项目链接", {})
    asana_url = asana_link_prop.get("url", "")

    if not asana_url:
        print(f"  ⚠️ {project_name}: 无Asana项目链接，跳过")
        return False

    # 从URL提取project GID
    # 格式: https://app.asana.com/0/{project_gid}/...
    parts = asana_url.rstrip("/").split("/")
    project_gid = None
    for i, part in enumerate(parts):
        if part == "0" and i + 1 < len(parts):
            project_gid = parts[i + 1]
            break

    if not project_gid:
        print(f"  ⚠️ {project_name}: 无法解析Asana项目ID，跳过")
        return False

    print(f"  📊 {project_name}: 正在同步...")
    tasks = get_asana_project_tasks(project_gid)
    progress = calculate_progress(tasks)

    print(f"     进度: {progress['progress']:.0%} | 健康: {progress['health']} | 里程碑: {progress['milestone']}")
    if progress["risk_summary"] != "无逾期风险":
        print(f"     风险: {progress['risk_summary']}")

    update_notion_project(notion_page["id"], progress)
    print(f"     ✅ Notion已更新")
    return True


def main():
    if not ASANA_TOKEN:
        print("❌ 未设置 ASANA_TOKEN 环境变量")
        print("   设置方式: export ASANA_TOKEN=your_token")
        sys.exit(1)
    if not NOTION_TOKEN:
        print("❌ 未设置 NOTION_TOKEN 环境变量")
        print("   设置方式: export NOTION_TOKEN=your_token")
        sys.exit(1)

    print("🔄 Asana → Notion 进度同步")
    print("=" * 60)

    projects = query_notion_projects()
    print(f"📁 找到 {len(projects)} 个交付中项目\n")

    synced = 0
    for project in projects:
        try:
            if sync_project(project):
                synced += 1
        except Exception as e:
            props = project.get("properties", {})
            name = ""
            title_prop = props.get("项目名称", {}).get("title", [])
            if title_prop:
                name = title_prop[0].get("text", {}).get("content", "")
            print(f"  ❌ {name}: 同步失败 - {e}")

    print(f"\n{'=' * 60}")
    print(f"同步完成。成功 {synced}/{len(projects)} 个项目。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
