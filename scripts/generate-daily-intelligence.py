#!/usr/bin/env python3
"""
generate-daily-intelligence.py — 每日AI技术情报HTML报告生成器

将 Markdown 格式的情报报告转为品牌化 HTML，存储到 obs/daily-intelligence/

Usage:
  python scripts/generate-daily-intelligence.py report.md
  python scripts/generate-daily-intelligence.py report.md --open
  python scripts/generate-daily-intelligence.py report.md --notify

输入: Markdown 文件 (由 Claude Code 定时任务生成)
输出: obs/daily-intelligence/YYYY-MM-DD-daily-ai-intelligence.html
"""

import sys
import re
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import markdown
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
except ImportError:
    print("ERROR: 'markdown' library not installed. Run: pip install markdown", file=sys.stderr)
    sys.exit(1)

try:
    from markdown.extensions.codehilite import CodeHiliteExtension
    import pygments
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False


# ── 品牌色彩 ──────────────────────────────────────────────────────────────────
COLOR_BRAND         = "#1890ff"
COLOR_ACCENT        = "#722ed1"   # 情报报告专用强调色(紫色)
COLOR_TEXT          = "#333333"
COLOR_MUTED         = "#666666"
COLOR_BG_CODE       = "#282c34"
COLOR_FG_CODE       = "#abb2bf"
COLOR_BG_QUOTE      = "#f0f7ff"
COLOR_SUCCESS       = "#52c41a"
COLOR_WARNING       = "#faad14"
COLOR_DANGER        = "#f5222d"


def _pygments_css() -> str:
    if not HAS_PYGMENTS:
        return ""
    try:
        from pygments.formatters import HtmlFormatter
        return HtmlFormatter(style="monokai", noclasses=False).get_style_defs(".codehilite")
    except Exception:
        return ""


REPORT_CSS = f"""
* {{ box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                 "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    font-size: 16px; line-height: 1.9; color: {COLOR_TEXT};
    background: #f5f7fa; margin: 0; padding: 0;
}}
.report-container {{
    max-width: 900px; margin: 0 auto; padding: 20px 24px 60px;
    background: #ffffff; min-height: 100vh;
    box-shadow: 0 0 40px rgba(0,0,0,0.06);
}}

/* 报告头部 */
.report-header {{
    background: linear-gradient(135deg, {COLOR_BRAND} 0%, {COLOR_ACCENT} 100%);
    color: #ffffff; padding: 32px 28px; border-radius: 12px;
    margin-bottom: 32px; position: relative; overflow: hidden;
}}
.report-header::after {{
    content: "AI"; position: absolute; right: 20px; top: -10px;
    font-size: 120px; font-weight: 900; opacity: 0.08; color: #fff;
}}
.report-title {{
    font-size: 26px; font-weight: bold; margin: 0 0 8px 0;
    line-height: 1.4; position: relative; z-index: 1;
}}
.report-subtitle {{
    font-size: 14px; opacity: 0.85; margin: 0;
    position: relative; z-index: 1;
}}
.report-date {{
    display: inline-block; background: rgba(255,255,255,0.2);
    padding: 4px 14px; border-radius: 20px; font-size: 13px;
    margin-top: 12px; position: relative; z-index: 1;
}}

/* 执行摘要卡片 */
.executive-summary {{
    background: {COLOR_BG_QUOTE}; border-left: 4px solid {COLOR_BRAND};
    padding: 20px 24px; border-radius: 0 8px 8px 0;
    margin: 24px 0;
}}
.executive-summary h2 {{
    font-size: 18px; color: {COLOR_BRAND}; margin: 0 0 12px 0;
    border: none; padding: 0;
}}

/* 正文样式 */
h1 {{ font-size: 24px; font-weight: bold; margin: 32px 0 16px; color: {COLOR_TEXT}; }}
h2 {{
    font-size: 20px; font-weight: bold; margin: 28px 0 12px;
    padding-left: 12px; border-left: 4px solid {COLOR_BRAND}; color: {COLOR_BRAND};
}}
h3 {{ font-size: 17px; font-weight: bold; margin: 22px 0 10px; color: {COLOR_TEXT}; }}
h4 {{ font-size: 15px; font-weight: bold; margin: 18px 0 8px; color: {COLOR_MUTED}; }}
p  {{ font-size: 15px; line-height: 1.9; margin: 14px 0; color: {COLOR_TEXT}; }}
a  {{ color: {COLOR_BRAND}; text-decoration: none; border-bottom: 1px solid {COLOR_BRAND}; }}
strong {{ color: {COLOR_BRAND}; font-weight: bold; }}
em     {{ color: #e65100; }}

code {{
    font-family: Consolas, Monaco, "Courier New", monospace;
    background: #f5f5f5; color: #e83e8c;
    padding: 2px 6px; border-radius: 4px; font-size: 13px;
}}
pre {{
    background: {COLOR_BG_CODE}; color: {COLOR_FG_CODE};
    padding: 16px 20px; border-radius: 8px; overflow-x: auto;
    margin: 16px 0; font-size: 14px; line-height: 1.6;
}}
pre code {{ background: transparent; color: inherit; padding: 0; font-size: inherit; }}

blockquote {{
    border-left: 4px solid {COLOR_BRAND}; padding: 12px 16px;
    background: {COLOR_BG_QUOTE}; margin: 16px 0;
    color: {COLOR_TEXT}; border-radius: 0 6px 6px 0;
}}
ul, ol {{ padding-left: 24px; margin: 12px 0; }}
li {{ margin: 8px 0; line-height: 1.7; }}

table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }}
th {{
    background: {COLOR_BRAND}; color: #fff; padding: 12px;
    border: 1px solid #e8e8e8; font-weight: bold; text-align: left;
}}
td {{ padding: 10px 12px; border: 1px solid #e8e8e8; }}
tr:nth-child(even) td {{ background: #f8faff; }}

hr {{
    border: none; height: 1px;
    background: linear-gradient(to right, transparent, {COLOR_BRAND}, transparent);
    margin: 28px 0;
}}

/* 优先级标签 */
.priority-high {{
    display: inline-block; background: {COLOR_DANGER}; color: #fff;
    padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;
}}
.priority-medium {{
    display: inline-block; background: {COLOR_WARNING}; color: #fff;
    padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;
}}
.priority-low {{
    display: inline-block; background: {COLOR_SUCCESS}; color: #fff;
    padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;
}}

/* 行动建议卡片 */
.action-card {{
    background: #f6ffed; border: 1px solid #b7eb8f;
    padding: 16px 20px; border-radius: 8px; margin: 12px 0;
}}

/* 页脚 */
.report-footer {{
    margin-top: 48px; padding-top: 20px; border-top: 2px solid {COLOR_BRAND};
    font-size: 12px; color: #aaa; text-align: center;
}}
.report-footer .brand {{
    color: {COLOR_BRAND}; font-weight: bold;
}}

/* 审查标记 */
.review-badge {{
    display: inline-block; background: {COLOR_SUCCESS}; color: #fff;
    padding: 4px 12px; border-radius: 16px; font-size: 12px;
    margin-left: 8px; vertical-align: middle;
}}
"""


def parse_front_matter(text: str) -> tuple:
    fm_re = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    meta = {}
    m = fm_re.match(text)
    if not m:
        return meta, text
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if val.startswith("[") and val.endswith("]"):
            val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
        if key:
            meta[key] = val
    return meta, text[m.end():]


def convert_markdown(body: str) -> str:
    exts = [TableExtension(), FencedCodeExtension(), "nl2br", "sane_lists"]
    if HAS_PYGMENTS:
        exts.append(CodeHiliteExtension(linenums=False, css_class="codehilite", guess_lang=True))
    return markdown.Markdown(extensions=exts).convert(body)


def post_process_html(html: str) -> str:
    """后处理：添加优先级标签样式"""
    html = re.sub(r'【高优先级】', '<span class="priority-high">HIGH</span>', html)
    html = re.sub(r'【中优先级】', '<span class="priority-medium">MED</span>', html)
    html = re.sub(r'【低优先级】', '<span class="priority-low">LOW</span>', html)
    return html


def build_report_html(meta: dict, content_html: str) -> str:
    title = meta.get("title", f"AI技术情报日报")
    date_str = meta.get("date", datetime.today().strftime("%Y-%m-%d"))
    issue = meta.get("issue", "")

    issue_text = f" | 第{issue}期" if issue else ""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - {date_str}</title>
  <style>
{REPORT_CSS}
{_pygments_css()}
  </style>
</head>
<body>
<div class="report-container">

<header class="report-header">
  <h1 class="report-title">{title}</h1>
  <p class="report-subtitle">Lysander CEO + Graphify 智囊团联合出品{issue_text}</p>
  <span class="report-date">{date_str}</span>
  <span class="review-badge">智囊团审查通过</span>
</header>

<article>
{content_html}
</article>

<footer class="report-footer">
  <p><span class="brand">Lysander AI Team</span> &middot; Daily Intelligence Report</p>
  <p>Generated {datetime.now().strftime("%Y-%m-%d %H:%M")} &middot; Reviewed by Graphify Think Tank</p>
</footer>

</div>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Generate daily AI intelligence HTML report.")
    parser.add_argument("input", help="Path to .md source file")
    parser.add_argument("--output", default=None, help="Output directory")
    parser.add_argument("--open", action="store_true", help="Open in browser")
    parser.add_argument("--notify", action="store_true", help="Send notification via n8n")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent.parent
    output_dir = Path(args.output).resolve() if args.output else repo_root / "obs" / "daily-intelligence"
    output_dir.mkdir(parents=True, exist_ok=True)

    source_text = input_path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(source_text)
    content_html = convert_markdown(body)
    content_html = post_process_html(content_html)
    html = build_report_html(meta, content_html)

    date_str = str(meta.get("date", datetime.today().strftime("%Y-%m-%d")))[:10]
    out_path = output_dir / f"{date_str}-daily-ai-intelligence.html"
    out_path.write_text(html, encoding="utf-8")

    print(f"Generated: {out_path}")
    print(f"Title   : {meta.get('title', 'Daily Intelligence')}")
    print(f"Size    : {out_path.stat().st_size // 1024} KB")

    if args.open:
        import webbrowser
        webbrowser.open(out_path.as_uri())

    if args.notify:
        try:
            import urllib.request
            import json
            data = json.dumps({
                "type": "daily_intelligence",
                "title": meta.get("title", "AI Daily Intelligence"),
                "date": date_str,
                "path": str(out_path),
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://n8n.lysander.bond/webhook/daily-intelligence",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=10)
            print("Notification sent via n8n")
        except Exception as e:
            print(f"Notification failed (non-critical): {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
