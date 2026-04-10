"""
PMO知识库闭环脚本
从项目复盘报告中提取经验教训，自动沉淀到PMO知识库。
支持从Notion复盘页面提取，或手动输入。
闭环路径：项目复盘 → 经验提取 → 知识库归档 → 模板/流程优化建议

由 janus_pmo_auto 负责运维
"""
import sys
import io
import os
import json
import argparse
from datetime import datetime
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import requests
except ImportError:
    print("需要安装 requests: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

NOTION_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# 经验教训分类体系
LESSON_CATEGORIES = {
    "scope": "范围管理",
    "schedule": "进度管理",
    "quality": "质量管理",
    "risk": "风险管理",
    "communication": "沟通管理",
    "resource": "资源管理",
    "technical": "技术实施",
    "client": "客户管理",
    "tool": "工具/自动化",
    "process": "流程优化",
}

# 经验教训严重度
SEVERITY_LEVELS = {
    "critical": "🔴 关键",
    "important": "🟡 重要",
    "minor": "🟢 改进",
}

# 知识库关键词到分类的映射（用于自动分类）
KEYWORD_CATEGORY_MAP = {
    "需求变更": "scope",
    "范围蔓延": "scope",
    "scope": "scope",
    "延期": "schedule",
    "进度": "schedule",
    "逾期": "schedule",
    "工期": "schedule",
    "质量": "quality",
    "缺陷": "quality",
    "bug": "quality",
    "测试": "quality",
    "风险": "risk",
    "沟通": "communication",
    "客户": "client",
    "资源": "resource",
    "人员": "resource",
    "技术": "technical",
    "集成": "technical",
    "IoT": "technical",
    "BIM": "technical",
    "工具": "tool",
    "自动化": "tool",
    "脚本": "tool",
    "Notion": "tool",
    "Asana": "tool",
    "流程": "process",
    "模板": "process",
    "SOP": "process",
}


def notion_headers():
    token = os.environ.get("NOTION_TOKEN", "")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


# ---------------------------------------------------------------------------
# 经验教训提取与分类
# ---------------------------------------------------------------------------


def auto_classify(text):
    """基于关键词自动分类"""
    text_lower = text.lower()
    scores = defaultdict(int)
    for keyword, category in KEYWORD_CATEGORY_MAP.items():
        if keyword.lower() in text_lower:
            scores[category] += 1
    if scores:
        return max(scores, key=scores.get)
    return "process"  # 默认归入流程优化


def extract_lessons_from_text(text, project_name=""):
    """从文本中提取结构化的经验教训"""
    lessons = []
    current_lesson = None

    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        # 识别经验教训条目（以编号、数字或bullet开头）
        is_lesson_start = False
        for prefix in ["L0", "- ", "* ", "· "]:
            if line.startswith(prefix):
                is_lesson_start = True
                break
        # 数字编号
        if line[:1].isdigit() and (line[1:2] == "." or line[1:2] == "、"):
            is_lesson_start = True

        if is_lesson_start:
            if current_lesson:
                lessons.append(current_lesson)

            # 清理前缀
            clean = line.lstrip("L0123456789.-*· 、")
            category = auto_classify(clean)

            current_lesson = {
                "description": clean,
                "category": category,
                "category_name": LESSON_CATEGORIES.get(category, "其他"),
                "project": project_name,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "severity": "important",
                "action": "",
            }
        elif current_lesson:
            # 附加描述或行动建议
            if "建议" in line or "措施" in line or "改进" in line:
                current_lesson["action"] = line.lstrip("→ ")
            else:
                current_lesson["description"] += " " + line

    if current_lesson:
        lessons.append(current_lesson)

    return lessons


# ---------------------------------------------------------------------------
# 知识库存储（本地JSON + Notion可选）
# ---------------------------------------------------------------------------

KNOWLEDGE_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "obs", "01-team-knowledge", "pmo_lessons_learned.json"
)


def load_knowledge_db():
    """加载本地经验教训库"""
    if os.path.exists(KNOWLEDGE_DB_PATH):
        with open(KNOWLEDGE_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"lessons": [], "stats": {"total": 0, "by_category": {}}}


def save_knowledge_db(db):
    """保存本地经验教训库"""
    os.makedirs(os.path.dirname(KNOWLEDGE_DB_PATH), exist_ok=True)
    with open(KNOWLEDGE_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def add_lessons_to_db(lessons):
    """将经验教训添加到知识库"""
    db = load_knowledge_db()

    for lesson in lessons:
        lesson["id"] = f"LL-{db['stats']['total'] + 1:04d}"
        db["lessons"].append(lesson)
        db["stats"]["total"] += 1

        cat = lesson["category"]
        db["stats"]["by_category"][cat] = db["stats"]["by_category"].get(cat, 0) + 1

    save_knowledge_db(db)
    return db


# ---------------------------------------------------------------------------
# 优化建议生成
# ---------------------------------------------------------------------------


def generate_optimization_suggestions(db):
    """基于经验教训库生成PMO优化建议"""
    suggestions = []

    # 统计各分类频次
    cat_counts = db["stats"]["by_category"]
    if not cat_counts:
        return suggestions

    # 高频问题分类 → 优化建议
    sorted_cats = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)

    for cat, count in sorted_cats[:5]:
        cat_name = LESSON_CATEGORIES.get(cat, cat)
        if count >= 3:
            suggestions.append({
                "category": cat_name,
                "frequency": count,
                "severity": "🔴 高频",
                "suggestion": f"「{cat_name}」领域已积累{count}条经验教训，建议：\n"
                              f"  → 审查现有{cat_name}相关SOP和模板是否需要更新\n"
                              f"  → 将高频问题的预防措施纳入阶段门检查清单\n"
                              f"  → 在项目启动阶段增加{cat_name}专项评审",
            })
        elif count >= 2:
            suggestions.append({
                "category": cat_name,
                "frequency": count,
                "severity": "🟡 关注",
                "suggestion": f"「{cat_name}」领域有{count}条经验教训，建议持续关注",
            })

    return suggestions


# ---------------------------------------------------------------------------
# 报告输出
# ---------------------------------------------------------------------------


def print_knowledge_report(db, new_lessons=None):
    """打印知识库报告"""
    print(f"\n{'=' * 60}")
    print("📚 PMO经验教训知识库")
    print(f"{'=' * 60}")
    print(f"  总条目数: {db['stats']['total']}")

    if db["stats"]["by_category"]:
        print(f"\n  分类统计:")
        for cat, count in sorted(db["stats"]["by_category"].items(), key=lambda x: x[1], reverse=True):
            cat_name = LESSON_CATEGORIES.get(cat, cat)
            bar = "█" * count
            print(f"    {cat_name:<10} {bar} ({count})")

    if new_lessons:
        print(f"\n{'─' * 60}")
        print(f"  本次新增 {len(new_lessons)} 条:")
        for lesson in new_lessons:
            sev = SEVERITY_LEVELS.get(lesson["severity"], "")
            print(f"    [{lesson['id']}] {sev} [{lesson['category_name']}] {lesson['description'][:50]}")
            if lesson.get("action"):
                print(f"           → {lesson['action'][:50]}")

    # 优化建议
    suggestions = generate_optimization_suggestions(db)
    if suggestions:
        print(f"\n{'─' * 60}")
        print("  📋 PMO优化建议:")
        for s in suggestions:
            print(f"\n  {s['severity']} {s['category']}:")
            for line in s["suggestion"].split("\n"):
                print(f"    {line}")

    print(f"\n{'=' * 60}")
    print(f"  知识库文件: {KNOWLEDGE_DB_PATH}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="PMO知识库闭环 — 经验教训自动沉淀")
    sub = parser.add_subparsers(dest="command")

    # 添加经验教训
    add_parser = sub.add_parser("add", help="添加经验教训")
    add_parser.add_argument("--project", "-p", required=True, help="项目名称")
    add_parser.add_argument("--text", "-t", help="经验教训文本（多条用换行分隔）")
    add_parser.add_argument("--file", "-f", help="从文件读取经验教训")

    # 查看知识库
    sub.add_parser("report", help="查看知识库报告")

    # 搜索
    search_parser = sub.add_parser("search", help="搜索经验教训")
    search_parser.add_argument("keyword", help="搜索关键词")

    # 导出
    sub.add_parser("export", help="导出知识库为Markdown")

    args = parser.parse_args()

    if args.command == "add":
        text = ""
        if args.text:
            text = args.text
        elif args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            print("请输入经验教训（每行一条，Ctrl+Z结束）:")
            try:
                text = sys.stdin.read()
            except EOFError:
                pass

        if not text.strip():
            print("❌ 无输入内容")
            sys.exit(1)

        print(f"📝 从项目「{args.project}」提取经验教训...")
        lessons = extract_lessons_from_text(text, args.project)
        print(f"   识别到 {len(lessons)} 条")

        if lessons:
            db = add_lessons_to_db(lessons)
            print_knowledge_report(db, lessons)
        else:
            print("   未识别到结构化经验教训条目")

    elif args.command == "report":
        db = load_knowledge_db()
        print_knowledge_report(db)

    elif args.command == "search":
        db = load_knowledge_db()
        keyword = args.keyword.lower()
        matches = [
            l for l in db["lessons"]
            if keyword in l["description"].lower()
            or keyword in l.get("action", "").lower()
            or keyword in l.get("category_name", "").lower()
        ]
        print(f"🔍 搜索「{args.keyword}」: 找到 {len(matches)} 条")
        for l in matches:
            sev = SEVERITY_LEVELS.get(l["severity"], "")
            print(f"  [{l['id']}] {sev} [{l['category_name']}] {l['description'][:60]}")
            print(f"         项目: {l['project']} | {l['date']}")

    elif args.command == "export":
        db = load_knowledge_db()
        print("# PMO经验教训库\n")
        print(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        print(f"总条目数: {db['stats']['total']}\n")

        # 按分类分组
        by_cat = defaultdict(list)
        for l in db["lessons"]:
            by_cat[l["category_name"]].append(l)

        for cat_name, lessons in by_cat.items():
            print(f"\n## {cat_name} ({len(lessons)}条)\n")
            for l in lessons:
                print(f"- **[{l['id']}]** {l['description']}")
                if l.get("action"):
                    print(f"  - 建议: {l['action']}")
                print(f"  - 来源: {l['project']} ({l['date']})")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
