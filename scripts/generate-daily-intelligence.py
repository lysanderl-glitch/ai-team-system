#!/usr/bin/env python3
"""
generate-daily-intelligence.py — 每日AI技术情报HTML报告生成器

视觉设计参考：https://www.janusd.com/
品牌色：Gold #FCAD2A / Deep Blue #013A7D / Cyan #028CDC / White #FFFFFF

Usage:
  python scripts/generate-daily-intelligence.py report.md
  python scripts/generate-daily-intelligence.py report.md --open
  python scripts/generate-daily-intelligence.py report.md --notify
"""

import sys
import re
import argparse
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


# ── Janus Brand Colors (from janusd.com logo SVG) ───────────────────────────
GOLD        = "#FCAD2A"
DEEP_BLUE   = "#013A7D"
CYAN        = "#028CDC"
DARK_BG     = "#0A1628"
DARK_CARD   = "#111D33"
WHITE       = "#FFFFFF"
LIGHT_GRAY  = "#F7F8FA"
TEXT_PRIMARY = "#1A1A2E"
TEXT_SECONDARY = "#5A6072"
TEXT_MUTED   = "#8E95A7"
BORDER      = "#E2E6EE"
CODE_BG     = "#0D1B2A"
CODE_FG     = "#E0E6F0"


def _pygments_css() -> str:
    if not HAS_PYGMENTS:
        return ""
    try:
        from pygments.formatters import HtmlFormatter
        return HtmlFormatter(style="monokai", noclasses=False).get_style_defs(".codehilite")
    except Exception:
        return ""


JANUS_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 35 44" width="28" height="36" style="vertical-align: middle; margin-right: 10px;">
  <path d="M24.39 0.09C25.4-0.32 26.42 0.73 26.42 2.18V41.44C26.42 42.89 25.4 43.93 24.39 43.52L9.71 39.63L18.24 38.6C18.75 38.52 19.21 38.25 19.55 37.83C19.89 37.41 20.08 36.87 20.08 36.32V7.32C20.07 6.76 19.89 6.23 19.55 5.81C19.21 5.4 18.74 5.12 18.24 5.05L9.63 4L24.39 0.09Z" fill="white"/>
  <path d="M2.45 38.84L16.61 37.33C17.12 37.25 17.58 37 17.92 36.6C18.26 36.21 18.45 35.7 18.45 35.18V8.42C18.45 7.9 18.26 7.39 17.92 7C17.58 6.61 17.12 6.36 16.61 6.29L2.45 4.77C2.15 4.72 1.84 4.75 1.55 4.83C1.25 4.92 0.98 5.07 0.75 5.27C0.52 5.47 0.33 5.72 0.2 6C0.07 6.29 0 6.59 0 6.9V36.69C0 37 0.07 37.31 0.2 37.59C0.32 37.88 0.51 38.13 0.74 38.33C0.98 38.53 1.25 38.69 1.54 38.77C1.84 38.86 2.15 38.88 2.45 38.84Z" fill="#FCAD2A"/>
  <path d="M31.87 7.93L28.1 7.52V36.09L31.87 35.71V7.93Z" fill="#013A7D"/>
  <path d="M33.13 8.05V35.57C34.11 35.36 34.81 34.8 34.81 34.06V9.55C34.81 8.81 34.11 8.26 33.13 8.05Z" fill="#028CDC"/>
</svg>"""

REPORT_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                 "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    font-size: 15px; line-height: 1.8; color: {TEXT_PRIMARY};
    background: {LIGHT_GRAY};
    -webkit-font-smoothing: antialiased;
}}

.report-wrapper {{
    max-width: 880px; margin: 0 auto; padding: 32px 20px 80px;
}}

/* ── Hero Header (Dark, janusd.com style) ─────────────────────────────── */
.report-header {{
    background: {DARK_BG};
    padding: 48px 40px 40px;
    border-radius: 16px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}}
.report-header::before {{
    content: "";
    position: absolute; top: 0; right: 0;
    width: 320px; height: 100%;
    background: linear-gradient(135deg, transparent 30%, rgba(2,141,220,0.08) 100%);
    pointer-events: none;
}}
.report-header::after {{
    content: "";
    position: absolute; bottom: 0; left: 40px; right: 40px;
    height: 3px;
    background: linear-gradient(90deg, {GOLD}, {CYAN}, transparent);
    border-radius: 2px;
}}
.header-top {{
    display: flex; align-items: center; margin-bottom: 24px;
    position: relative; z-index: 1;
}}
.header-brand {{
    font-size: 13px; font-weight: 500; color: {TEXT_MUTED};
    letter-spacing: 2px; text-transform: uppercase;
}}
.report-title {{
    font-size: 28px; font-weight: 700; color: {WHITE};
    line-height: 1.3; margin-bottom: 12px;
    position: relative; z-index: 1;
}}
.report-subtitle {{
    font-size: 14px; color: {TEXT_MUTED}; margin-bottom: 20px;
    position: relative; z-index: 1;
}}
.header-meta {{
    display: flex; gap: 16px; align-items: center; flex-wrap: wrap;
    position: relative; z-index: 1;
}}
.meta-tag {{
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 5px 14px; border-radius: 20px;
    font-size: 12px; color: rgba(255,255,255,0.7);
    font-weight: 500;
}}
.meta-tag.gold {{ border-color: rgba(252,173,42,0.3); color: {GOLD}; }}

/* ── Content Area ─────────────────────────────────────────────────────── */
.report-content {{
    background: {WHITE};
    border-radius: 12px;
    padding: 40px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    border: 1px solid {BORDER};
}}

/* ── Typography ───────────────────────────────────────────────────────── */
h1 {{
    font-size: 24px; font-weight: 700; color: {TEXT_PRIMARY};
    margin: 40px 0 16px; line-height: 1.3;
}}
h2 {{
    font-size: 19px; font-weight: 600; color: {DEEP_BLUE};
    margin: 36px 0 14px; padding-bottom: 10px;
    border-bottom: 2px solid {GOLD};
    display: inline-block;
}}
h2::after {{
    content: ""; display: block;
}}
h3 {{
    font-size: 16px; font-weight: 600; color: {TEXT_PRIMARY};
    margin: 28px 0 10px;
}}
h4 {{
    font-size: 14px; font-weight: 600; color: {TEXT_SECONDARY};
    margin: 20px 0 8px; text-transform: uppercase; letter-spacing: 0.5px;
}}
p {{
    font-size: 15px; line-height: 1.8; margin: 12px 0;
    color: {TEXT_PRIMARY};
}}
a {{
    color: {CYAN}; text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: border-color 0.2s;
}}
a:hover {{ border-bottom-color: {CYAN}; }}
strong {{ color: {DEEP_BLUE}; font-weight: 600; }}
em {{ color: {GOLD}; font-style: normal; font-weight: 500; }}

/* ── Blockquote (Executive Summary) ───────────────────────────────────── */
blockquote {{
    background: linear-gradient(135deg, rgba(1,58,125,0.04), rgba(2,141,220,0.04));
    border-left: 3px solid {GOLD};
    padding: 20px 24px;
    margin: 20px 0;
    border-radius: 0 8px 8px 0;
    font-size: 15px; line-height: 1.9;
    color: {TEXT_PRIMARY};
}}
blockquote p {{ margin: 0; }}

/* ── Code ─────────────────────────────────────────────────────────────── */
code {{
    font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
    background: rgba(1,58,125,0.06); color: {DEEP_BLUE};
    padding: 2px 7px; border-radius: 4px; font-size: 13px;
    font-weight: 500;
}}
pre {{
    background: {CODE_BG}; color: {CODE_FG};
    padding: 20px 24px; border-radius: 10px; overflow-x: auto;
    margin: 20px 0; font-size: 13px; line-height: 1.7;
    border: 1px solid rgba(255,255,255,0.05);
}}
pre code {{
    background: transparent; color: inherit;
    padding: 0; border-radius: 0; font-size: inherit;
}}

/* ── Lists ────────────────────────────────────────────────────────────── */
ul, ol {{ padding-left: 24px; margin: 12px 0; }}
li {{
    margin: 8px 0; line-height: 1.7;
    color: {TEXT_PRIMARY};
}}
li::marker {{ color: {GOLD}; }}

/* ── Tables ───────────────────────────────────────────────────────────── */
table {{
    width: 100%; border-collapse: collapse;
    margin: 20px 0; font-size: 14px;
    border-radius: 8px; overflow: hidden;
    border: 1px solid {BORDER};
}}
th {{
    background: {DEEP_BLUE}; color: {WHITE};
    padding: 12px 16px; font-weight: 600;
    text-align: left; font-size: 13px;
    letter-spacing: 0.3px;
}}
td {{
    padding: 11px 16px; border-bottom: 1px solid {BORDER};
    color: {TEXT_PRIMARY};
}}
tr:last-child td {{ border-bottom: none; }}
tr:nth-child(even) td {{ background: {LIGHT_GRAY}; }}

/* ── Horizontal Rule ──────────────────────────────────────────────────── */
hr {{
    border: none; height: 1px;
    background: {BORDER};
    margin: 32px 0;
}}

/* ── Priority Tags ────────────────────────────────────────────────────── */
.priority-high {{
    display: inline-block; background: {GOLD}; color: {DARK_BG};
    padding: 3px 12px; border-radius: 4px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
}}
.priority-medium {{
    display: inline-block; background: {CYAN}; color: {WHITE};
    padding: 3px 12px; border-radius: 4px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
}}
.priority-low {{
    display: inline-block; background: rgba(1,58,125,0.1); color: {DEEP_BLUE};
    padding: 3px 12px; border-radius: 4px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.5px;
}}

/* ── Images ───────────────────────────────────────────────────────────── */
img {{
    max-width: 100%; border-radius: 8px; margin: 16px 0;
}}

/* ── Footer ───────────────────────────────────────────────────────────── */
.report-footer {{
    margin-top: 40px; padding: 24px 40px;
    background: {DARK_BG}; border-radius: 12px;
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 12px;
}}
.footer-brand {{
    display: flex; align-items: center; gap: 8px;
    font-size: 13px; color: rgba(255,255,255,0.5); font-weight: 500;
}}
.footer-brand .gold {{ color: {GOLD}; }}
.footer-info {{
    font-size: 12px; color: rgba(255,255,255,0.35);
}}

/* ── Responsive ───────────────────────────────────────────────────────── */
@media (max-width: 640px) {{
    .report-wrapper {{ padding: 16px 12px 60px; }}
    .report-header {{ padding: 32px 24px 28px; }}
    .report-content {{ padding: 24px 20px; }}
    .report-title {{ font-size: 22px; }}
    .report-footer {{ padding: 20px 24px; flex-direction: column; text-align: center; }}
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
    html = re.sub(r'【高优先级】', '<span class="priority-high">HIGH</span>', html)
    html = re.sub(r'【中优先级】', '<span class="priority-medium">MED</span>', html)
    html = re.sub(r'【低优先级】', '<span class="priority-low">LOW</span>', html)
    return html


def build_report_html(meta: dict, content_html: str) -> str:
    title = meta.get("title", "AI技术情报日报")
    date_str = meta.get("date", datetime.today().strftime("%Y-%m-%d"))
    issue = meta.get("issue", "")
    report_type = meta.get("report_type", "intelligence")
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    issue_text = f"Issue #{issue}" if issue else ""
    type_label = "Action Report" if report_type == "action" else "Daily Intelligence"

    tags_html = "".join(f'<span class="meta-tag">{t}</span>' for t in tags[:4])
    if issue_text:
        tags_html += f'<span class="meta-tag gold">{issue_text}</span>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — {date_str}</title>
  <style>
{REPORT_CSS}
{_pygments_css()}
  </style>
</head>
<body>
<div class="report-wrapper">

<header class="report-header">
  <div class="header-top">
    {JANUS_LOGO_SVG}
    <span class="header-brand">Synapse &middot; {type_label}</span>
  </div>
  <h1 class="report-title">{title}</h1>
  <p class="report-subtitle">Lysander CEO + Graphify Think Tank</p>
  <div class="header-meta">
    <span class="meta-tag gold">{date_str}</span>
    {tags_html}
  </div>
</header>

<div class="report-content">
{content_html}
</div>

<footer class="report-footer">
  <div class="footer-brand">
    {JANUS_LOGO_SVG}
    <span><span class="gold">Synapse</span> &middot; Janus Digital &middot; Lysander AI Team</span>
  </div>
  <div class="footer-info">
    Generated {datetime.now().strftime("%Y-%m-%d %H:%M")} &middot; Reviewed by Graphify Think Tank
  </div>
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
    report_type = meta.get("report_type", "intelligence")
    suffix = "action-report" if report_type == "action" else "daily-ai-intelligence"
    out_path = output_dir / f"{date_str}-{suffix}.html"
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
