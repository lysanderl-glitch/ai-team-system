"""
Synapse HTML Report Validator
==============================

Three-level validation for generated HTML reports:
  Level 1 — Syntax: can the file be parsed by html.parser without errors?
  Level 2 — Content completeness: size, structure, unreplaced placeholders.
  Level 3 — Data freshness: dates, stale markers, placeholder text.

Part of the Synapse Quality Assurance Framework.

Usage:
    from test_runner.html_validator import (
        validate_html_report,
        validate_latest_reports,
    )

    result = validate_html_report("obs/daily-intelligence/2026-04-10-daily-ai-intelligence.html")
    print(result.passed, result.issues)
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_INTEL_DIR = _PROJECT_ROOT / "obs" / "daily-intelligence"
_ARTICLES_DIR = _PROJECT_ROOT / "obs" / "generated-articles"

# Level 2 thresholds
_MIN_FILE_SIZE_BYTES = 1024  # 1 KB

# Level 3 stale markers
_STALE_MARKERS = [
    "暂无数据",
    "数据加载失败",
    "No data available",
    "Loading...",
    "TODO",
    "PLACEHOLDER",
    "TBD",
]

# Regex for unreplaced template placeholders like {{variable}}
_PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")

# Date patterns commonly found in report text (YYYY-MM-DD)
_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ValidationIssue:
    """A single validation issue found in an HTML report."""

    file: str
    level: int  # 1 = syntax, 2 = completeness, 3 = freshness
    severity: str  # error / warning / info
    message: str


@dataclass
class ValidationResult:
    """Aggregated result of validating one HTML file."""

    file: str
    passed: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_issue(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)
        if issue.severity == "error":
            self.passed = False


# ---------------------------------------------------------------------------
# HTML parser for structural analysis
# ---------------------------------------------------------------------------

class _ReportParser(HTMLParser):
    """Custom HTML parser that collects structural metadata and text content."""

    def __init__(self) -> None:
        super().__init__()
        self.has_html: bool = False
        self.has_head: bool = False
        self.has_body: bool = False
        self.has_title: bool = False
        self.text_content: list[str] = []
        self.unreplaced_placeholders: list[str] = []
        self.parse_errors: list[str] = []
        self._tag_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        tag_lower = tag.lower()
        self._tag_stack.append(tag_lower)
        if tag_lower == "html":
            self.has_html = True
        elif tag_lower == "head":
            self.has_head = True
        elif tag_lower == "body":
            self.has_body = True
        elif tag_lower == "title":
            self.has_title = True

    def handle_endtag(self, tag: str) -> None:
        # Pop matching tag from stack (lenient — don't fail on mismatch)
        tag_lower = tag.lower()
        if self._tag_stack and self._tag_stack[-1] == tag_lower:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        self.text_content.append(data)
        placeholders = _PLACEHOLDER_RE.findall(data)
        self.unreplaced_placeholders.extend(placeholders)

    def error(self, message: str) -> None:  # type: ignore[override]
        self.parse_errors.append(message)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_dates_from_text(text: str) -> list[datetime]:
    """Extract all YYYY-MM-DD dates found in text, returning them as datetimes."""
    dates: list[datetime] = []
    for match in _DATE_RE.finditer(text):
        try:
            dt = datetime.strptime(match.group(1), "%Y-%m-%d")
            dates.append(dt.replace(tzinfo=timezone.utc))
        except ValueError:
            continue
    return dates


def _extract_date_from_filename(file_path: Path) -> Optional[datetime]:
    """Try to extract a date from the filename (e.g. 2026-04-10-daily-report.html)."""
    match = _DATE_RE.search(file_path.name)
    if match:
        try:
            dt = datetime.strptime(match.group(1), "%Y-%m-%d")
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def _newest_html_files(directory: Path, count: int = 5) -> list[Path]:
    """Return the *count* most recently modified HTML files in a directory."""
    if not directory.is_dir():
        return []

    html_files = list(directory.glob("*.html"))
    html_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return html_files[:count]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_html_report(
    file_path: str | Path,
    freshness_days: int = 2,
) -> ValidationResult:
    """
    Validate an HTML report file with three-level checks.

    Args:
        file_path: Path to the HTML file.
        freshness_days: Maximum age (in days) for dates found in the report
                        before a freshness warning is raised.

    Returns:
        A ``ValidationResult`` with all discovered issues.
    """
    file_path = Path(file_path)
    result = ValidationResult(file=str(file_path))

    # --- Pre-check: file exists ---
    if not file_path.exists():
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=1,
            severity="error",
            message=f"File does not exist: {file_path}",
        ))
        return result

    # --- Read file ---
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as exc:
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=1,
            severity="error",
            message=f"Cannot read file: {exc}",
        ))
        return result

    # ===================================================================
    # Level 1: HTML syntax
    # ===================================================================
    parser = _ReportParser()
    try:
        parser.feed(content)
    except Exception as exc:
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=1,
            severity="error",
            message=f"HTML parse error: {exc}",
        ))
        return result  # cannot proceed if parsing fails

    for err in parser.parse_errors:
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=1,
            severity="error",
            message=f"HTML parser error: {err}",
        ))

    # ===================================================================
    # Level 2: Content completeness
    # ===================================================================

    # File size check
    file_size = file_path.stat().st_size
    if file_size < _MIN_FILE_SIZE_BYTES:
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=2,
            severity="warning",
            message=(
                f"File too small ({file_size} bytes < {_MIN_FILE_SIZE_BYTES} bytes). "
                f"Report may be incomplete."
            ),
        ))

    # Structural checks
    if not parser.has_html:
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=2,
            severity="error",
            message="Missing <html> tag",
        ))

    if not parser.has_head:
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=2,
            severity="warning",
            message="Missing <head> tag",
        ))

    if not parser.has_body:
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=2,
            severity="error",
            message="Missing <body> tag",
        ))

    # Unreplaced placeholders
    if parser.unreplaced_placeholders:
        unique_placeholders = sorted(set(parser.unreplaced_placeholders))
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=2,
            severity="error",
            message=(
                f"Unreplaced template placeholders found: "
                f"{', '.join(unique_placeholders)}"
            ),
        ))

    # ===================================================================
    # Level 3: Data freshness
    # ===================================================================
    full_text = " ".join(parser.text_content)

    # Stale marker check
    for marker in _STALE_MARKERS:
        if marker in full_text:
            result.add_issue(ValidationIssue(
                file=str(file_path),
                level=3,
                severity="warning",
                message=f"Stale placeholder detected: '{marker}'",
            ))

    # Date freshness check
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=freshness_days)

    # Check date from filename
    filename_date = _extract_date_from_filename(file_path)
    if filename_date and filename_date < cutoff:
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=3,
            severity="info",
            message=(
                f"Report filename date ({filename_date:%Y-%m-%d}) is "
                f"older than {freshness_days} days"
            ),
        ))

    # Check dates embedded in content
    content_dates = _extract_dates_from_text(full_text)
    if content_dates:
        newest_date = max(content_dates)
        if newest_date < cutoff:
            result.add_issue(ValidationIssue(
                file=str(file_path),
                level=3,
                severity="warning",
                message=(
                    f"Newest date in report content ({newest_date:%Y-%m-%d}) is "
                    f"older than {freshness_days} days — data may be stale"
                ),
            ))

    return result


def validate_latest_reports(
    count: int = 5,
    scan_dirs: Optional[list[str | Path]] = None,
    freshness_days: int = 2,
) -> list[ValidationResult]:
    """
    Validate the most recently generated HTML reports.

    Scans ``obs/daily-intelligence/`` and ``obs/generated-articles/`` by default,
    taking the *count* newest HTML files from each directory.

    Args:
        count: Number of recent files to validate per directory.
        scan_dirs: Override the directories to scan.
        freshness_days: Passed through to ``validate_html_report``.

    Returns:
        A list of ``ValidationResult``, one per file.
    """
    if scan_dirs is None:
        directories = [_INTEL_DIR, _ARTICLES_DIR]
    else:
        directories = [Path(d) for d in scan_dirs]

    results: list[ValidationResult] = []

    for directory in directories:
        files = _newest_html_files(directory, count)
        if not files:
            # Report that the directory has no HTML files
            dummy = ValidationResult(file=str(directory))
            dummy.add_issue(ValidationIssue(
                file=str(directory),
                level=2,
                severity="warning",
                message=f"No HTML files found in {directory}",
            ))
            results.append(dummy)
            continue

        for html_file in files:
            results.append(validate_html_report(html_file, freshness_days))

    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Validate latest HTML reports and print results."""
    results = validate_latest_reports()

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    print("=" * 60)
    print("  Synapse HTML Report Validation")
    print("=" * 60)

    for result in results:
        icon = "[OK]" if result.passed else "[FAIL]"
        fname = Path(result.file).name
        print(f"\n  {icon} {fname}")
        for issue in result.issues:
            sev = issue.severity.upper()
            print(f"       L{issue.level} [{sev}] {issue.message}")

    print(f"\n  Total: {total} reports | {passed} passed | {failed} failed")
    print()


if __name__ == "__main__":
    main()
