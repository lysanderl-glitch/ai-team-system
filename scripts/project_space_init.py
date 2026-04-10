"""
Notion 项目空间自动生成脚本
为 Janus Digital 新项目在 Notion 中创建完整的项目空间结构。

功能说明：
  - 在 PMO自动化管理体系 页面下创建项目主页
  - 自动生成项目概览、阶段门追踪、台账链接、交付物清单、风险日志等板块
  - 动态查找关联的4个台账数据库并生成链接
  - 输出创建的页面 URL 供 n8n 工作流 WF-01 捕获

调用方式：
  命令行：python project_space_init.py --name "项目名" --code "PRJ-001" --client "客户" --pm "张三" --type "数字化交付"
  n8n：通过 Execute Command 节点调用，解析 stdout 中的 JSON 输出

由 janus_pmo_auto 负责运维
"""

import sys
import io
import os
import json
import argparse
import logging
from datetime import datetime
from typing import Optional

# Windows UTF-8 输出支持
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import requests
except ImportError:
    print(json.dumps({"success": False, "error": "需要安装 requests: pip install requests"}, ensure_ascii=False))
    sys.exit(1)

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

NOTION_API_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"
PMO_PARENT_PAGE_ID = "33e114fc090c812dad23d802c0c71dc9"  # 新workspace: 📊 PMO自动化管理体系

# 台账数据库名称（用于动态查找）
LEDGER_DB_NAMES = {
    "supplementary_collection": "补充收资清单",
    "space_ledger": "空间台账",
    "device_ledger": "设备台账",
    "iot_point_list": "IoT点位清单",
}

# 阶段门定义
STAGE_GATES = [
    ("G0", "项目启动", "立项审批、项目章程"),
    ("G1", "需求确认", "业务调研、需求规格"),
    ("G2", "方案评审", "技术方案、实施计划"),
    ("G3", "开发完成", "系统开发、集成测试"),
    ("G4", "验收交付", "UAT测试、培训交付"),
    ("G5", "项目关闭", "运维移交、项目复盘"),
]

# ---------------------------------------------------------------------------
# 日志
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("project_space_init")

# ---------------------------------------------------------------------------
# Notion API 封装
# ---------------------------------------------------------------------------


class NotionClient:
    """Notion API 客户端封装"""

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_API_VERSION,
        }

    def _request(self, method: str, endpoint: str, payload: Optional[dict] = None) -> dict:
        """发送 Notion API 请求，带重试和错误处理"""
        url = f"{NOTION_BASE_URL}/{endpoint}"
        max_retries = 3

        for attempt in range(max_retries):
            try:
                resp = requests.request(
                    method,
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30,
                )

                if resp.status_code == 429:
                    # 速率限制，等待后重试
                    retry_after = int(resp.headers.get("Retry-After", 2))
                    logger.warning(f"速率限制，{retry_after}秒后重试 (第{attempt + 1}次)")
                    import time
                    time.sleep(retry_after)
                    continue

                if resp.status_code >= 400:
                    error_body = resp.json() if resp.text else {}
                    error_msg = error_body.get("message", resp.text)
                    raise NotionAPIError(
                        f"Notion API 错误 [{resp.status_code}]: {error_msg}",
                        status_code=resp.status_code,
                        body=error_body,
                    )

                return resp.json()

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    logger.warning(f"请求超时，重试中 (第{attempt + 1}次)")
                    continue
                raise NotionAPIError("Notion API 请求超时，已重试3次")

            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"连接失败，重试中 (第{attempt + 1}次)")
                    continue
                raise NotionAPIError(f"无法连接 Notion API: {e}")

        raise NotionAPIError("超过最大重试次数")

    def search(self, query: str, filter_type: Optional[str] = None) -> list:
        """搜索 Notion 对象"""
        payload = {"query": query, "page_size": 20}
        if filter_type:
            payload["filter"] = {"value": filter_type, "property": "object"}
        result = self._request("POST", "search", payload)
        return result.get("results", [])

    def create_page(self, parent_id: str, title: str, children: list, icon: Optional[str] = None) -> dict:
        """创建 Notion 页面"""
        payload = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": [{"text": {"content": title}}]
            },
            "children": children,
        }
        if icon:
            payload["icon"] = {"type": "emoji", "emoji": icon}
        return self._request("POST", "pages", payload)


class NotionAPIError(Exception):
    """Notion API 异常"""

    def __init__(self, message: str, status_code: int = 0, body: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body or {}


# ---------------------------------------------------------------------------
# 页面内容构建
# ---------------------------------------------------------------------------


def _heading(level: int, text: str, color: str = "default") -> dict:
    """创建标题块"""
    block_type = f"heading_{level}"
    return {
        "object": "block",
        "type": block_type,
        block_type: {
            "rich_text": [{"type": "text", "text": {"content": text}, "annotations": {"color": color}}],
        },
    }


def _paragraph(text: str, bold: bool = False, color: str = "default") -> dict:
    """创建段落块"""
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text},
                    "annotations": {"bold": bold, "color": color},
                }
            ],
        },
    }


def _rich_text_paragraph(segments: list) -> dict:
    """创建富文本段落块，segments 为 (text, bold, color) 元组列表"""
    rich_text = []
    for text, bold, color in segments:
        rich_text.append({
            "type": "text",
            "text": {"content": text},
            "annotations": {"bold": bold, "color": color},
        })
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": rich_text},
    }


def _divider() -> dict:
    """创建分隔线"""
    return {"object": "block", "type": "divider", "divider": {}}


def _callout(text: str, icon: str = "📌", color: str = "gray_background") -> dict:
    """创建标注块"""
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "icon": {"type": "emoji", "emoji": icon},
            "color": color,
        },
    }


def _bulleted_list_item(text: str, bold_prefix: str = "", link: str = "") -> dict:
    """创建无序列表项"""
    rich_text = []
    if bold_prefix:
        rich_text.append({
            "type": "text",
            "text": {"content": bold_prefix},
            "annotations": {"bold": True},
        })
    text_obj = {"content": text}
    if link:
        text_obj["link"] = {"url": link}
    rich_text.append({
        "type": "text",
        "text": text_obj,
    })
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": rich_text},
    }


def _table_row(cells: list) -> dict:
    """创建表格行，cells 为字符串列表"""
    return {
        "object": "block",
        "type": "table_row",
        "table_row": {
            "cells": [
                [{"type": "text", "text": {"content": cell}}] for cell in cells
            ]
        },
    }


def _table(width: int, has_header: bool, rows: list) -> dict:
    """创建表格块"""
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": width,
            "has_column_header": has_header,
            "has_row_header": False,
            "children": rows,
        },
    }


def _toggle(text: str, children: list) -> dict:
    """创建折叠块"""
    return {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": text}, "annotations": {"bold": True}}],
            "children": children,
        },
    }


# ---------------------------------------------------------------------------
# 台账查找
# ---------------------------------------------------------------------------


def find_ledger_databases(client: NotionClient, project_name: str) -> dict:
    """
    动态查找项目关联的4个台账数据库。
    搜索策略：先按项目名+台账名搜索，找不到则仅按台账名搜索。
    返回 {key: {"id": db_id, "url": url, "title": title}} 字典。
    """
    found = {}
    for key, db_name in LEDGER_DB_NAMES.items():
        # 尝试按项目名+台账名精确搜索
        search_queries = [
            f"{project_name} {db_name}",
            db_name,
        ]
        for query in search_queries:
            results = client.search(query, filter_type="database")
            for r in results:
                title_parts = r.get("title", [])
                title = "".join(t.get("plain_text", "") for t in title_parts)
                if db_name in title:
                    found[key] = {
                        "id": r["id"],
                        "url": r.get("url", ""),
                        "title": title,
                    }
                    logger.info(f"找到台账: {db_name} -> {title}")
                    break
            if key in found:
                break

        if key not in found:
            logger.warning(f"未找到台账数据库: {db_name}，将使用占位链接")
            found[key] = {"id": "", "url": "", "title": f"{db_name}（待创建）"}

    return found


# ---------------------------------------------------------------------------
# 项目主页构建
# ---------------------------------------------------------------------------


def build_project_page_children(
    project_name: str,
    project_code: str,
    client_name: str,
    pm_name: str,
    project_type: str,
    ledger_dbs: dict,
) -> list:
    """构建项目主页的所有子块内容"""
    today = datetime.now().strftime("%Y-%m-%d")
    children = []

    # ======= 项目概览 =======
    children.append(_heading(1, "项目概览"))
    children.append(
        _callout(
            f"项目编号: {project_code} | 客户: {client_name} | 项目经理: {pm_name} | 类型: {project_type}",
            icon="📋",
            color="blue_background",
        )
    )
    children.append(
        _table(
            width=2,
            has_header=True,
            rows=[
                _table_row(["属性", "值"]),
                _table_row(["项目名称", project_name]),
                _table_row(["项目编号", project_code]),
                _table_row(["客户名称", client_name]),
                _table_row(["项目经理", pm_name]),
                _table_row(["项目类型", project_type]),
                _table_row(["创建日期", today]),
                _table_row(["当前阶段", "G0 项目启动"]),
                _table_row(["项目状态", "进行中"]),
            ],
        )
    )
    children.append(_divider())

    # ======= 阶段门状态追踪 =======
    children.append(_heading(1, "阶段门状态追踪"))
    children.append(
        _callout(
            "阶段门（Stage Gate）是项目交付的关键质量检查点。每个阶段门需完成规定的交付物并通过评审后方可进入下一阶段。",
            icon="🚦",
            color="yellow_background",
        )
    )

    gate_rows = [_table_row(["阶段门", "阶段名称", "关键交付物", "状态", "通过日期"])]
    for code, name, deliverables in STAGE_GATES:
        status = "🔵 进行中" if code == "G0" else "⚪ 未开始"
        gate_rows.append(_table_row([code, name, deliverables, status, "-"]))
    children.append(_table(width=5, has_header=True, rows=gate_rows))
    children.append(_divider())

    # ======= 关键台账链接 =======
    children.append(_heading(1, "关键台账链接"))
    children.append(
        _callout(
            "以下为本项目关联的4个核心台账数据库，点击可直接跳转。",
            icon="🔗",
            color="green_background",
        )
    )
    for key, db_info in ledger_dbs.items():
        display_name = LEDGER_DB_NAMES.get(key, key)
        url = db_info.get("url", "")
        title = db_info.get("title", display_name)
        if url:
            children.append(_bulleted_list_item(title, bold_prefix=f"{display_name}: ", link=url))
        else:
            children.append(_bulleted_list_item(f"{title}", bold_prefix=f"{display_name}: "))
    children.append(_divider())

    # ======= 交付物清单 =======
    children.append(_heading(1, "交付物清单"))
    children.append(
        _callout("记录项目各阶段需要交付的文档和成果物，确保交付完整性。", icon="📦", color="purple_background")
    )
    deliverable_rows = [_table_row(["序号", "交付物名称", "所属阶段", "负责人", "状态", "备注"])]
    default_deliverables = [
        ("1", "项目章程", "G0", pm_name, "✅ 已完成", "由WF-01自动创建"),
        ("2", "业务调研报告", "G1", "-", "⚪ 未开始", ""),
        ("3", "需求规格说明书", "G1", "-", "⚪ 未开始", ""),
        ("4", "技术方案", "G2", "-", "⚪ 未开始", ""),
        ("5", "WBS工作分解", "G2", "-", "⚪ 未开始", ""),
        ("6", "实施计划", "G2", "-", "⚪ 未开始", ""),
        ("7", "测试报告", "G3", "-", "⚪ 未开始", ""),
        ("8", "培训材料", "G4", "-", "⚪ 未开始", ""),
        ("9", "验收报告", "G4", "-", "⚪ 未开始", ""),
        ("10", "项目复盘报告", "G5", "-", "⚪ 未开始", ""),
    ]
    for d in default_deliverables:
        deliverable_rows.append(_table_row(list(d)))
    children.append(_table(width=6, has_header=True, rows=deliverable_rows))
    children.append(_divider())

    # ======= 风险与问题日志 =======
    children.append(_heading(1, "风险与问题日志"))
    children.append(
        _callout("记录项目执行过程中的风险和问题，确保及时跟踪和闭环。", icon="⚠️", color="red_background")
    )
    risk_rows = [
        _table_row(["编号", "类型", "描述", "影响等级", "负责人", "状态", "应对措施"]),
        _table_row(["（项目启动后在此记录）", "", "", "", "", "", ""]),
    ]
    children.append(_table(width=7, has_header=True, rows=risk_rows))

    children.append(_divider())

    # ======= 页脚信息 =======
    children.append(
        _paragraph(
            f"本页面由 Janus PMO 自动化系统自动创建 | 创建时间: {today} | janus_pmo_auto",
            color="gray",
        )
    )

    return children


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def create_project_space(
    project_name: str,
    project_code: str,
    client_name: str,
    pm_name: str,
    project_type: str,
) -> dict:
    """
    创建 Notion 项目空间主页。

    返回:
        dict: {"success": True, "page_id": ..., "page_url": ...} 或 {"success": False, "error": ...}
    """
    # 1. 获取 Notion Token
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        return {"success": False, "error": "环境变量 NOTION_TOKEN 未设置"}

    client = NotionClient(token)

    # 2. 验证父页面可访问
    try:
        client._request("GET", f"pages/{PMO_PARENT_PAGE_ID}")
        logger.info("父页面验证通过: PMO自动化管理体系")
    except NotionAPIError as e:
        return {
            "success": False,
            "error": f"无法访问 PMO 父页面 ({PMO_PARENT_PAGE_ID}): {e}",
        }

    # 3. 检查是否已存在同名项目页面（防重复创建）
    existing = client.search(f"{project_code} {project_name}", filter_type="page")
    for page in existing:
        title_parts = page.get("properties", {}).get("title", {}).get("title", [])
        title = "".join(t.get("plain_text", "") for t in title_parts)
        if project_code in title and project_name in title:
            page_url = page.get("url", "")
            logger.warning(f"项目页面已存在: {title} -> {page_url}")
            return {
                "success": False,
                "error": f"项目页面已存在: {title}",
                "existing_page_url": page_url,
                "existing_page_id": page["id"],
            }

    # 4. 查找关联台账数据库
    logger.info("正在查找关联台账数据库...")
    ledger_dbs = find_ledger_databases(client, project_name)

    # 5. 构建页面内容
    logger.info("正在构建项目主页内容...")
    page_title = f"【{project_code}】{project_name}"
    children = build_project_page_children(
        project_name=project_name,
        project_code=project_code,
        client_name=client_name,
        pm_name=pm_name,
        project_type=project_type,
        ledger_dbs=ledger_dbs,
    )

    # 6. Notion API 限制每次最多100个子块，分批创建
    MAX_CHILDREN_PER_REQUEST = 100
    first_batch = children[:MAX_CHILDREN_PER_REQUEST]
    remaining = children[MAX_CHILDREN_PER_REQUEST:]

    logger.info(f"正在创建项目页面: {page_title} (共{len(children)}个块)")
    try:
        page = client.create_page(
            parent_id=PMO_PARENT_PAGE_ID,
            title=page_title,
            children=first_batch,
            icon="🏗️",
        )
    except NotionAPIError as e:
        return {"success": False, "error": f"创建项目页面失败: {e}"}

    page_id = page["id"]
    page_url = page.get("url", "")
    logger.info(f"项目页面创建成功: {page_url}")

    # 追加剩余块（如有）
    if remaining:
        for i in range(0, len(remaining), MAX_CHILDREN_PER_REQUEST):
            batch = remaining[i : i + MAX_CHILDREN_PER_REQUEST]
            try:
                client._request(
                    "PATCH",
                    f"blocks/{page_id}/children",
                    {"children": batch},
                )
            except NotionAPIError as e:
                logger.error(f"追加第{i // MAX_CHILDREN_PER_REQUEST + 2}批块失败: {e}")

    # 7. 返回结果
    return {
        "success": True,
        "page_id": page_id,
        "page_url": page_url,
        "page_title": page_title,
        "project_code": project_code,
        "project_name": project_name,
        "ledger_dbs_found": {
            k: bool(v.get("id")) for k, v in ledger_dbs.items()
        },
    }


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Janus PMO - Notion 项目空间自动生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python project_space_init.py --name "XX大厦数字化" --code "PRJ-2026-001" --client "XX集团" --pm "张三" --type "数字化交付"
  python project_space_init.py -n "智慧园区" -c "PRJ-2026-002" -cl "YY科技" -p "李四" -t "IoT集成"
        """,
    )
    parser.add_argument("--name", "-n", required=True, help="项目名称")
    parser.add_argument("--code", "-c", required=True, help="项目编号 (如 PRJ-2026-001)")
    parser.add_argument("--client", "-cl", required=True, help="客户名称")
    parser.add_argument("--pm", "-p", required=True, help="项目经理姓名")
    parser.add_argument("--type", "-t", default="数字化交付", help="项目类型 (默认: 数字化交付)")
    return parser.parse_args()


def main():
    args = parse_args()

    result = create_project_space(
        project_name=args.name,
        project_code=args.code,
        client_name=args.client,
        pm_name=args.pm,
        project_type=args.type,
    )

    # 输出 JSON 到 stdout（供 n8n 捕获）
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 退出码：成功=0，失败=1
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
