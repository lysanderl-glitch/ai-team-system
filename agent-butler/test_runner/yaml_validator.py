"""
Synapse YAML Configuration Validator
=====================================

Three-level validation for YAML configuration files:
  Level 1 — Syntax: can the file be parsed as valid YAML?
  Level 2 — (Reserved for future JSON-Schema validation)
  Level 3 — Reference integrity: do cross-file references resolve?

Part of the Synapse Quality Assurance Framework.

Usage:
    from test_runner.yaml_validator import (
        validate_yaml_syntax,
        validate_yaml_references,
        validate_all_yaml,
    )

    result = validate_yaml_syntax("agent-butler/config/organization.yaml")
    print(result.passed, result.issues)
"""

from __future__ import annotations

import glob as _glob
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    yaml = None


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_DIR = _PROJECT_ROOT / "agent-butler" / "config"
_PERSONNEL_DIR = _PROJECT_ROOT / "obs" / "01-team-knowledge" / "HR" / "personnel"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ValidationIssue:
    """A single validation issue found in a YAML file."""

    file: str
    level: int  # 1 = syntax, 2 = schema, 3 = reference
    severity: str  # error / warning / info
    path: str  # dotted path within the YAML structure (if applicable)
    value: str  # the problematic value
    message: str  # human-readable description


@dataclass
class ValidationResult:
    """Aggregated result of validating one or more YAML files."""

    file: str
    passed: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_issue(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)
        if issue.severity == "error":
            self.passed = False


# ---------------------------------------------------------------------------
# Reference rules — declarative mapping of YAML paths to validation checks
# ---------------------------------------------------------------------------

# Pattern syntax:
#   "**.key"  — match `key` at any depth
#   "a.b.key" — match literal nested path

_REFERENCE_RULES: dict[str, dict[str, dict[str, str]]] = {
    "organization.yaml": {
        "**.specialist_id": {
            "check": "personnel_file_exists",
            "description": "specialist_id must correspond to a personnel file",
        },
        "**.reports_to": {
            "check": "name_exists_in_org",
            "description": "reports_to must reference an existing member name",
        },
    },
    "active_tasks.yaml": {
        "**.assigned_team": {
            "check": "team_exists_in_org",
            "description": "assigned_team must match a team in organization.yaml",
        },
        "**.assigned_to": {
            "check": "personnel_file_exists",
            "description": "assigned_to must correspond to a personnel file",
        },
    },
    "n8n_integration.yaml": {
        "**.webhook_url": {
            "check": "url_format",
            "description": "webhook_url must be a valid HTTP(S) URL",
        },
        "**.prompt_file": {
            "check": "file_exists_relative",
            "description": "prompt_file must point to an existing file",
        },
    },
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_by_pattern(
    data: Any,
    key_pattern: str,
    current_path: str = "",
) -> list[tuple[str, Any]]:
    """
    Recursively extract values matching a dotted key pattern.

    ``"**.key"`` matches ``key`` at any nesting level.
    ``"a.b.key"`` matches the exact path.

    Returns a list of ``(dotted_path, value)`` tuples.
    """
    results: list[tuple[str, Any]] = []

    if key_pattern.startswith("**."):
        target_key = key_pattern[3:]
        # Search recursively for the target key
        if isinstance(data, dict):
            for k, v in data.items():
                full_path = f"{current_path}.{k}" if current_path else k
                if k == target_key and v is not None:
                    results.append((full_path, v))
                # Recurse into the value regardless
                results.extend(_extract_by_pattern(v, key_pattern, full_path))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                full_path = f"{current_path}[{i}]"
                results.extend(_extract_by_pattern(item, key_pattern, full_path))
    else:
        # Exact path matching
        parts = key_pattern.split(".", 1)
        if isinstance(data, dict) and parts[0] in data:
            full_path = f"{current_path}.{parts[0]}" if current_path else parts[0]
            if len(parts) == 1:
                if data[parts[0]] is not None:
                    results.append((full_path, data[parts[0]]))
            else:
                results.extend(
                    _extract_by_pattern(data[parts[0]], parts[1], full_path)
                )

    return results


def _personnel_file_exists(specialist_id: str) -> bool:
    """Check whether a personnel markdown file exists for the given specialist_id."""
    if not _PERSONNEL_DIR.is_dir():
        return True  # cannot verify, assume ok

    # Personnel files are stored as <team>/<specialist_id>.md
    matches = list(_PERSONNEL_DIR.rglob(f"{specialist_id}.md"))
    return len(matches) > 0


def _load_org_names() -> set[str]:
    """Load all member names from organization.yaml for cross-reference checks."""
    org_file = _CONFIG_DIR / "organization.yaml"
    if not org_file.exists() or yaml is None:
        return set()

    try:
        with open(org_file, encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception:
        return set()

    names: set[str] = set()
    _collect_names(config, names)
    return names


def _collect_names(data: Any, names: set[str]) -> None:
    """Recursively collect all 'name' values from a nested structure."""
    if isinstance(data, dict):
        if "name" in data and isinstance(data["name"], str):
            names.add(data["name"])
        for v in data.values():
            _collect_names(v, names)
    elif isinstance(data, list):
        for item in data:
            _collect_names(item, names)


def _load_org_teams() -> set[str]:
    """Load all team names from organization.yaml."""
    org_file = _CONFIG_DIR / "organization.yaml"
    if not org_file.exists() or yaml is None:
        return set()

    try:
        with open(org_file, encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception:
        return set()

    teams: set[str] = set()
    team_section = config.get("teams", {})
    if isinstance(team_section, dict):
        for team_key, team_def in team_section.items():
            teams.add(team_key)
            if isinstance(team_def, dict) and "name" in team_def:
                teams.add(team_def["name"])
    return teams


_URL_RE = re.compile(r"^https?://.+", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_yaml_syntax(file_path: str | Path) -> ValidationResult:
    """
    Level 1: Validate that a file is parseable as YAML.

    Returns a ``ValidationResult`` with syntax-level issues.
    """
    file_path = Path(file_path)
    result = ValidationResult(file=str(file_path))

    if not file_path.exists():
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=1,
            severity="error",
            path="",
            value="",
            message=f"File does not exist: {file_path}",
        ))
        return result

    if yaml is None:
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=1,
            severity="warning",
            path="",
            value="",
            message="PyYAML not installed; cannot validate YAML syntax",
        ))
        return result

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as exc:
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=1,
            severity="error",
            path="",
            value="",
            message=f"Cannot read file: {exc}",
        ))
        return result

    try:
        yaml.safe_load(content)
    except yaml.YAMLError as exc:
        result.add_issue(ValidationIssue(
            file=str(file_path),
            level=1,
            severity="error",
            path="",
            value="",
            message=f"YAML syntax error: {exc}",
        ))

    return result


def validate_yaml_references(file_path: str | Path) -> ValidationResult:
    """
    Level 3: Validate cross-file references in a YAML configuration.

    Checks specialist_id references against HR personnel files,
    file_path references against the filesystem, and URL formats.

    Returns a ``ValidationResult`` with reference-level issues.
    """
    file_path = Path(file_path)
    result = ValidationResult(file=str(file_path))

    # First, ensure the file is valid YAML
    syntax_result = validate_yaml_syntax(file_path)
    if not syntax_result.passed:
        result.issues.extend(syntax_result.issues)
        result.passed = False
        return result

    if yaml is None:
        return result  # cannot check references without yaml

    try:
        with open(file_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception:
        return result  # syntax check already covers this

    if config is None:
        return result  # empty file is valid

    # Look up rules for this file
    basename = file_path.name
    rules = _REFERENCE_RULES.get(basename, {})

    if not rules:
        # No rules defined for this file; still valid
        return result

    # Lazy-load cross-reference data only when needed
    org_names: Optional[set[str]] = None
    org_teams: Optional[set[str]] = None

    for pattern, rule in rules.items():
        check_type = rule["check"]
        matches = _extract_by_pattern(config, pattern)

        for dotted_path, value in matches:
            str_value = str(value).strip()
            if not str_value:
                continue

            if check_type == "personnel_file_exists":
                if not _personnel_file_exists(str_value):
                    result.add_issue(ValidationIssue(
                        file=str(file_path),
                        level=3,
                        severity="error",
                        path=dotted_path,
                        value=str_value,
                        message=(
                            f"Personnel file not found for '{str_value}' "
                            f"in {_PERSONNEL_DIR}"
                        ),
                    ))

            elif check_type == "name_exists_in_org":
                if org_names is None:
                    org_names = _load_org_names()
                if org_names and str_value not in org_names:
                    result.add_issue(ValidationIssue(
                        file=str(file_path),
                        level=3,
                        severity="warning",
                        path=dotted_path,
                        value=str_value,
                        message=(
                            f"Name '{str_value}' not found in organization.yaml"
                        ),
                    ))

            elif check_type == "team_exists_in_org":
                if org_teams is None:
                    org_teams = _load_org_teams()
                if org_teams and str_value not in org_teams:
                    result.add_issue(ValidationIssue(
                        file=str(file_path),
                        level=3,
                        severity="warning",
                        path=dotted_path,
                        value=str_value,
                        message=(
                            f"Team '{str_value}' not found in organization.yaml"
                        ),
                    ))

            elif check_type == "url_format":
                if not _URL_RE.match(str_value):
                    result.add_issue(ValidationIssue(
                        file=str(file_path),
                        level=3,
                        severity="error",
                        path=dotted_path,
                        value=str_value,
                        message=f"Invalid URL format: '{str_value}'",
                    ))

            elif check_type == "file_exists_relative":
                target = _PROJECT_ROOT / str_value
                if not target.exists():
                    result.add_issue(ValidationIssue(
                        file=str(file_path),
                        level=3,
                        severity="warning",
                        path=dotted_path,
                        value=str_value,
                        message=f"Referenced file not found: {target}",
                    ))

    return result


def validate_all_yaml(
    config_dir: Optional[str | Path] = None,
) -> list[ValidationResult]:
    """
    Validate all YAML files in the configuration directory.

    Runs Level 1 (syntax) on every file and Level 3 (references) on files
    that have defined reference rules.

    Returns a list of ``ValidationResult``, one per file.
    """
    if config_dir is None:
        config_dir = _CONFIG_DIR
    else:
        config_dir = Path(config_dir)

    results: list[ValidationResult] = []

    if not config_dir.is_dir():
        dummy = ValidationResult(file=str(config_dir))
        dummy.add_issue(ValidationIssue(
            file=str(config_dir),
            level=1,
            severity="error",
            path="",
            value="",
            message=f"Config directory does not exist: {config_dir}",
        ))
        results.append(dummy)
        return results

    yaml_files = sorted(config_dir.glob("*.yaml")) + sorted(config_dir.glob("*.yml"))

    for yaml_file in yaml_files:
        # Level 1: syntax
        syntax_result = validate_yaml_syntax(yaml_file)

        # Level 3: references (only if syntax passes and rules exist)
        if syntax_result.passed and yaml_file.name in _REFERENCE_RULES:
            ref_result = validate_yaml_references(yaml_file)
            # Merge reference issues into the syntax result
            syntax_result.issues.extend(ref_result.issues)
            if not ref_result.passed:
                syntax_result.passed = False

        results.append(syntax_result)

    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Validate all YAML configs and print results."""
    results = validate_all_yaml()

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    print("=" * 60)
    print("  Synapse YAML Validation Report")
    print("=" * 60)

    for result in results:
        icon = "[OK]" if result.passed else "[FAIL]"
        fname = Path(result.file).name
        print(f"\n  {icon} {fname}")
        for issue in result.issues:
            sev = issue.severity.upper()
            print(f"       L{issue.level} [{sev}] {issue.message}")
            if issue.path:
                print(f"              at: {issue.path} = {issue.value}")

    print(f"\n  Total: {total} files | {passed} passed | {failed} failed")
    print()


if __name__ == "__main__":
    main()
