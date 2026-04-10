#!/usr/bin/env python3
"""
generate-article.py — Local HTML article generator for ai-team-system

Usage:
  python scripts/generate-article.py obs/path/to/article.md
  python scripts/generate-article.py obs/path/to/article.md --open
  python scripts/generate-article.py obs/path/to/article.md --output D:/shared/

Output: obs/generated-articles/YYYY-MM-DD-title.html (self-contained, no external deps)
"""

import sys
import re
import argparse
from pathlib import Path
from datetime import datetime

# ── optional imports ──────────────────────────────────────────────────────────
try:
    import markdown
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
    HAS_MARKDOWN = True
except ImportError:
    print("ERROR: 'markdown' library not installed. Run: pip install markdown", file=sys.stderr)
    sys.exit(1)

try:
    from markdown.extensions.codehilite import CodeHiliteExtension
    import pygments  # noqa: F401
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False


# ── style constants (science-tech blue theme) ─────────────────────────────────
COLOR_BRAND         = "#1890ff"
COLOR_TEXT          = "#333333"
COLOR_MUTED         = "#666666"
COLOR_BG_CODE       = "#282c34"
COLOR_FG_CODE       = "#abb2bf"
COLOR_BG_QUOTE      = "#f0f7ff"
COLOR_INLINE_CODE_BG = "#f5f5f5"
COLOR_INLINE_CODE_FG = "#e83e8c"


def _pygments_css() -> str:
    if not HAS_PYGMENTS:
        return ""
    try:
        from pygments.formatters import HtmlFormatter
        return HtmlFormatter(style="monokai", noclasses=False).get_style_defs(".codehilite")
    except Exception:
        return ""


PAGE_CSS = f"""
* {{ box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                 "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    font-size: 16px; line-height: 1.9; color: {COLOR_TEXT};
    background: #ffffff; max-width: 860px;
    margin: 0 auto; padding: 40px 24px 80px;
}}
h1 {{ font-size: 26px; font-weight: bold; margin: 32px 0 16px; color: {COLOR_TEXT}; }}
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
    background: {COLOR_INLINE_CODE_BG}; color: {COLOR_INLINE_CODE_FG};
    padding: 2px 6px; border-radius: 4px; font-size: 13px;
}}
pre {{
    background: {COLOR_BG_CODE}; color: {COLOR_FG_CODE};
    padding: 16px 20px; border-radius: 8px; overflow-x: auto;
    margin: 16px 0; font-size: 14px; line-height: 1.6;
}}
pre code {{ background: transparent; color: inherit; padding: 0; border-radius: 0; font-size: inherit; }}
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
img {{ max-width: 100%; border-radius: 8px; margin: 16px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
.article-header {{ border-bottom: 2px solid {COLOR_BRAND}; padding-bottom: 20px; margin-bottom: 32px; }}
.article-title {{ font-size: 28px; font-weight: bold; color: {COLOR_TEXT}; margin: 0 0 12px 0; line-height: 1.4; }}
.article-meta {{ font-size: 13px; color: {COLOR_MUTED}; display: flex; gap: 16px; flex-wrap: wrap; }}
.tag {{
    display: inline-block; background: #e6f7ff; color: {COLOR_BRAND};
    padding: 3px 10px; border-radius: 16px; font-size: 12px; margin: 2px 3px;
}}
.article-footer {{
    margin-top: 60px; padding-top: 20px; border-top: 1px solid #e8e8e8;
    font-size: 12px; color: #aaaaaa; text-align: center;
}}
"""


# ── front-matter parser ───────────────────────────────────────────────────────
_FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

def parse_front_matter(text: str) -> tuple:
    """Return (meta dict, body text). Handles key:value and [list] syntax."""
    meta = {}
    m = _FM_RE.match(text)
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


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^\w\-\u4e00-\u9fff]', '', text)
    return re.sub(r'-+', '-', text).strip('-') or "article"


# ── HTML assembly ─────────────────────────────────────────────────────────────
def build_html(meta: dict, content_html: str, source_file: str) -> str:
    title    = meta.get("title", Path(source_file).stem)
    date_str = meta.get("date", datetime.today().strftime("%Y-%m-%d"))
    author   = meta.get("author", "")
    tags_raw = meta.get("tags", [])
    desc     = meta.get("description", "")

    tags = tags_raw if isinstance(tags_raw, list) else ([tags_raw] if tags_raw else [])
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in tags)

    meta_parts = []
    if date_str:
        meta_parts.append(f'<span>📅 {date_str[:10]}</span>')
    if author:
        meta_parts.append(f'<span>✍️ {author}</span>')

    meta_html = '<div class="article-meta">' + "".join(meta_parts)
    if tags_html:
        meta_html += f'<div style="margin-top:8px;">{tags_html}</div>'
    meta_html += '</div>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <style>
{PAGE_CSS}
{_pygments_css()}
  </style>
</head>
<body>
<header class="article-header">
  <h1 class="article-title">{title}</h1>
  {meta_html}
</header>
<article>
{content_html}
</article>
<footer class="article-footer">
  Generated by Synapse &middot; {datetime.now().strftime("%Y-%m-%d %H:%M")}
  &middot; Source: {Path(source_file).name}
</footer>
</body>
</html>"""


def convert_markdown(body: str) -> str:
    exts = [TableExtension(), FencedCodeExtension(), "nl2br", "sane_lists"]
    if HAS_PYGMENTS:
        exts.append(CodeHiliteExtension(linenums=False, css_class="codehilite", guess_lang=True))
    return markdown.Markdown(extensions=exts).convert(body)


def resolve_output_path(input_path: Path, meta: dict, output_dir: Path) -> Path:
    date_str = str(meta.get("date", datetime.today().strftime("%Y-%m-%d")))[:10]
    slug = slugify(meta.get("title", input_path.stem)) or slugify(input_path.stem)
    return output_dir / f"{date_str}-{slug}.html"


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate self-contained styled HTML from Markdown.")
    parser.add_argument("input", help="Path to .md source file")
    parser.add_argument("--output", default=None, help="Output directory (default: obs/generated-articles/)")
    parser.add_argument("--open", action="store_true", help="Open in browser after generation")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    repo_root  = Path(__file__).resolve().parent.parent
    output_dir = Path(args.output).resolve() if args.output else repo_root / "obs" / "generated-articles"
    output_dir.mkdir(parents=True, exist_ok=True)

    source_text  = input_path.read_text(encoding="utf-8")
    meta, body   = parse_front_matter(source_text)
    content_html = convert_markdown(body)
    html         = build_html(meta, content_html, str(input_path))

    out_path = resolve_output_path(input_path, meta, output_dir)
    out_path.write_text(html, encoding="utf-8")

    print(f"✅ Generated : {out_path}")
    print(f"   Title    : {meta.get('title', input_path.stem)}")
    print(f"   Size     : {out_path.stat().st_size // 1024} KB")
    if not HAS_PYGMENTS:
        print("   ⚠️  Tip: install pygments for syntax highlighting: pip install pygments")

    if args.open:
        import webbrowser
        webbrowser.open(out_path.as_uri())

    return 0


if __name__ == "__main__":
    sys.exit(main())
