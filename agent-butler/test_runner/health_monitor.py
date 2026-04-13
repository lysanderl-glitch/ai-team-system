"""
Synapse Health Monitor
======================

Monitors the health of scheduled remote Agents and the intelligence pipeline.
Checks execution recency via git log and file modification times.

Includes a mixed-mode Slack alert system with three severity levels:
  - P0 (Critical): >48h no heartbeat — immediate Slack push
  - P1 (Warning):  >24h no heartbeat — folded into /plan-day morning check
  - P2 (Info):     informational — weekly summary only

Alert functions generate action lists; they do **not** call Slack directly.
The calling layer (scheduled Agent / plan-day Skill) is responsible for dispatch.

Part of the Synapse Quality Assurance Framework.

Usage:
    from test_runner.health_monitor import (
        check_scheduled_agents,
        check_intelligence_pipeline,
        generate_health_report,
        AlertLevel,
        format_slack_alert,
        generate_alert_actions,
        get_morning_check_items,
    )

    report = generate_health_report()
    for entry in report.agents:
        print(f"{entry.agent_name}: {entry.status} — {entry.message}")

    # Generate alert actions (does not send anything)
    actions = generate_alert_actions(report)

    # Get items for /plan-day morning check
    morning_items = get_morning_check_items()
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:
    yaml = None  # graceful fallback; will use hardcoded agent list


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_DIR = _PROJECT_ROOT / "agent-butler" / "config"
_N8N_CONFIG = _CONFIG_DIR / "n8n_integration.yaml"
_INTEL_DIR = _PROJECT_ROOT / "obs" / "daily-intelligence"
_ARTICLES_DIR = _PROJECT_ROOT / "obs" / "generated-articles"

# Fallback agent definitions when n8n_integration.yaml is unavailable
_DEFAULT_AGENTS: list[dict[str, str]] = [
    {
        "name": "task_auto_resume",
        "description": "Task auto-resume agent (6:00am Dubai)",
        "schedule": "0 2 * * *",
        "output_pattern": "active_tasks",
    },
    {
        "name": "daily_intelligence",
        "description": "Daily intelligence report agent (8:00am Dubai)",
        "schedule": "0 4 * * *",
        "output_pattern": "daily-ai-intelligence",
    },
    {
        "name": "intelligence_action",
        "description": "Intelligence action pipeline agent (10:00am Dubai)",
        "schedule": "0 6 * * *",
        "output_pattern": "action-report",
    },
    {
        "name": "calendar_sync",
        "description": "SPE calendar sync agent (6:15am Dubai)",
        "schedule": "15 2 * * *",
        "output_pattern": "calendar",
    },
    {
        "name": "daily_review",
        "description": "SPE daily review agent (8:00pm Dubai)",
        "schedule": "0 16 * * *",
        "output_pattern": "daily-retro",
    },
]

# Thresholds
_WARNING_HOURS = 24
_CRITICAL_HOURS = 48


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class HealthStatus:
    """Health status of a single scheduled agent."""

    agent_name: str
    last_execution: Optional[datetime] = None
    status: str = "unknown"  # healthy / warning / critical / unknown
    message: str = ""


@dataclass
class PipelineStatus:
    """Health status of the intelligence pipeline."""

    daily_report: HealthStatus = field(
        default_factory=lambda: HealthStatus(agent_name="daily_intelligence_report")
    )
    action_report: HealthStatus = field(
        default_factory=lambda: HealthStatus(agent_name="intelligence_action_report")
    )
    overall: str = "unknown"  # healthy / warning / critical


@dataclass
class HealthReport:
    """Comprehensive health report combining all checks."""

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    agents: list[HealthStatus] = field(default_factory=list)
    pipeline: Optional[PipelineStatus] = None
    overall: str = "unknown"  # healthy / warning / critical
    summary: str = ""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_agent_definitions() -> list[dict[str, str]]:
    """Load scheduled agent definitions from n8n config or fall back to defaults."""
    if not _N8N_CONFIG.exists() or yaml is None:
        return _DEFAULT_AGENTS

    try:
        with open(_N8N_CONFIG, encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception:
        return _DEFAULT_AGENTS

    agents: list[dict[str, str]] = []

    # Extract from event_chains.daily_pipeline
    event_chains = config.get("event_chains", {})
    daily_pipeline = event_chains.get("daily_pipeline", {})
    for step in daily_pipeline.get("chain", []):
        event_desc = step.get("event", "")
        trigger_id = step.get("trigger", "")
        name = re.sub(r"[^a-z0-9]+", "_", event_desc.lower()).strip("_")
        agents.append({
            "name": name,
            "description": event_desc,
            "trigger": trigger_id,
            "output_pattern": "",
        })

    # Extract from scheduled_agents
    scheduled = config.get("scheduled_agents", {})
    for agent_key, agent_def in scheduled.items():
        if not isinstance(agent_def, dict):
            continue
        agents.append({
            "name": agent_key,
            "description": agent_def.get("description", agent_key),
            "schedule": agent_def.get("schedule", ""),
            "output_pattern": "",
        })

    # Extract from workflow_mapping (scheduled ones)
    workflow_map = config.get("workflow_mapping", {})
    for wf_name, wf_def in workflow_map.items():
        if not isinstance(wf_def, dict):
            continue
        schedule = wf_def.get("schedule", "")
        if schedule:
            agents.append({
                "name": wf_def.get("workflow", wf_name),
                "description": wf_def.get("description", wf_name),
                "schedule": schedule,
                "output_pattern": "",
            })

    return agents if agents else _DEFAULT_AGENTS


def _git_last_commit_touching(pattern: str) -> Optional[datetime]:
    """Find the datetime of the most recent git commit that touched files matching *pattern*."""
    try:
        result = subprocess.run(
            [
                "git", "log", "-1",
                "--format=%aI",
                "--", pattern,
            ],
            capture_output=True,
            text=True,
            cwd=str(_PROJECT_ROOT),
            timeout=15,
        )
        output = result.stdout.strip()
        if output:
            return datetime.fromisoformat(output)
    except Exception:
        pass
    return None


def _newest_file_mtime(directory: Path, pattern: str = "*") -> Optional[datetime]:
    """Return the modification time of the newest file in *directory* matching *pattern*."""
    if not directory.is_dir():
        return None

    newest: Optional[datetime] = None
    for entry in directory.iterdir():
        if not entry.is_file():
            continue
        if pattern != "*" and pattern not in entry.name:
            continue
        mtime = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc)
        if newest is None or mtime > newest:
            newest = mtime
    return newest


def _classify_recency(
    last_execution: Optional[datetime],
    now: Optional[datetime] = None,
) -> tuple[str, str]:
    """Classify a last-execution timestamp into status + message."""
    if now is None:
        now = datetime.now(timezone.utc)

    if last_execution is None:
        return "critical", "No execution record found"

    # Ensure both datetimes are offset-aware for comparison
    if last_execution.tzinfo is None:
        last_execution = last_execution.replace(tzinfo=timezone.utc)

    age = now - last_execution
    age_hours = age.total_seconds() / 3600

    if age_hours <= _WARNING_HOURS:
        return "healthy", f"Last executed {age_hours:.1f}h ago"
    elif age_hours <= _CRITICAL_HOURS:
        return "warning", f"Last executed {age_hours:.1f}h ago (>{_WARNING_HOURS}h)"
    else:
        return "critical", f"Last executed {age_hours:.1f}h ago (>{_CRITICAL_HOURS}h)"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_scheduled_agents() -> list[HealthStatus]:
    """
    Check the execution status of all scheduled remote agents.

    For each agent, attempts to find its most recent execution by:
      1. Scanning git log for commits mentioning the agent or its outputs.
      2. Checking output file modification times in known directories.

    Returns a list of ``HealthStatus`` entries, one per agent.
    """
    agents = _load_agent_definitions()
    now = datetime.now(timezone.utc)
    results: list[HealthStatus] = []

    for agent in agents:
        name = agent.get("name", "unknown")
        description = agent.get("description", name)
        output_pattern = agent.get("output_pattern", "")

        last_exec: Optional[datetime] = None

        # Strategy 1: check git log for commits mentioning the agent
        git_time = _git_last_commit_touching(f"*{output_pattern}*") if output_pattern else None
        if git_time is not None:
            last_exec = git_time

        # Strategy 2: check file modification times in intelligence directories
        for scan_dir in (_INTEL_DIR, _ARTICLES_DIR):
            if output_pattern:
                mtime = _newest_file_mtime(scan_dir, output_pattern)
            else:
                mtime = _newest_file_mtime(scan_dir)
            if mtime is not None and (last_exec is None or mtime > last_exec):
                last_exec = mtime

        status, message = _classify_recency(last_exec, now)

        results.append(HealthStatus(
            agent_name=name,
            last_execution=last_exec,
            status=status,
            message=f"[{description}] {message}",
        ))

    return results


def check_intelligence_pipeline() -> PipelineStatus:
    """
    Check the intelligence pipeline specifically.

    Verifies:
      - Daily intelligence report exists for today (or yesterday).
      - Action report exists for today (or yesterday).

    Returns a ``PipelineStatus`` with individual and overall health.
    """
    now = datetime.now(timezone.utc)
    pipeline = PipelineStatus()

    # --- Daily intelligence report ---
    daily_mtime = _newest_file_mtime(_INTEL_DIR, "daily-ai-intelligence")
    git_daily = _git_last_commit_touching("obs/daily-intelligence/*daily-ai-intelligence*")
    best_daily = max(
        (t for t in (daily_mtime, git_daily) if t is not None),
        default=None,
    )
    status, msg = _classify_recency(best_daily, now)
    pipeline.daily_report = HealthStatus(
        agent_name="daily_intelligence_report",
        last_execution=best_daily,
        status=status,
        message=msg,
    )

    # --- Action report ---
    action_mtime = _newest_file_mtime(_INTEL_DIR, "action-report")
    git_action = _git_last_commit_touching("obs/daily-intelligence/*action-report*")
    best_action = max(
        (t for t in (action_mtime, git_action) if t is not None),
        default=None,
    )
    status, msg = _classify_recency(best_action, now)
    pipeline.action_report = HealthStatus(
        agent_name="intelligence_action_report",
        last_execution=best_action,
        status=status,
        message=msg,
    )

    # --- Overall pipeline status ---
    statuses = [pipeline.daily_report.status, pipeline.action_report.status]
    if "critical" in statuses:
        pipeline.overall = "critical"
    elif "warning" in statuses:
        pipeline.overall = "warning"
    elif all(s == "healthy" for s in statuses):
        pipeline.overall = "healthy"
    else:
        pipeline.overall = "unknown"

    return pipeline


def generate_health_report() -> HealthReport:
    """
    Generate a comprehensive health report covering all monitored systems.

    Combines:
      - Scheduled agent health checks
      - Intelligence pipeline status
      - Overall system health classification

    Returns a ``HealthReport`` dataclass.
    """
    report = HealthReport()

    # 1. Scheduled agents
    report.agents = check_scheduled_agents()

    # 2. Intelligence pipeline
    report.pipeline = check_intelligence_pipeline()

    # 3. Overall status
    all_statuses = [a.status for a in report.agents]
    if report.pipeline:
        all_statuses.append(report.pipeline.overall)

    if "critical" in all_statuses:
        report.overall = "critical"
    elif "warning" in all_statuses:
        report.overall = "warning"
    elif all(s == "healthy" for s in all_statuses):
        report.overall = "healthy"
    else:
        report.overall = "unknown"

    # 4. Summary
    total = len(report.agents)
    healthy_count = sum(1 for a in report.agents if a.status == "healthy")
    warning_count = sum(1 for a in report.agents if a.status == "warning")
    critical_count = sum(1 for a in report.agents if a.status == "critical")

    parts = [f"System health: {report.overall.upper()}"]
    parts.append(f"Agents: {healthy_count}/{total} healthy")
    if warning_count:
        parts.append(f"{warning_count} warning")
    if critical_count:
        parts.append(f"{critical_count} critical")
    if report.pipeline:
        parts.append(f"Pipeline: {report.pipeline.overall}")

    report.summary = " | ".join(parts)

    return report


# ---------------------------------------------------------------------------
# Alert Level Classification
# ---------------------------------------------------------------------------

class AlertLevel:
    """Alert severity levels for the mixed-mode notification system.

    - P0_CRITICAL: >48h no heartbeat — immediate Slack push
    - P1_WARNING:  >24h no heartbeat — folded into plan-day morning check
    - P2_INFO:     informational — included in weekly summary only
    """

    P0_CRITICAL = "P0"  # >48h no heartbeat, immediate Slack push
    P1_WARNING = "P1"   # >24h no heartbeat, fold into plan-day morning check
    P2_INFO = "P2"      # informational, weekly summary


_STATUS_TO_ALERT: dict[str, str] = {
    "critical": AlertLevel.P0_CRITICAL,
    "warning": AlertLevel.P1_WARNING,
    "healthy": AlertLevel.P2_INFO,
    "unknown": AlertLevel.P0_CRITICAL,  # unknown treated as critical
}

_ALERT_EMOJI: dict[str, str] = {
    AlertLevel.P0_CRITICAL: "\U0001f6a8",  # 🚨
    AlertLevel.P1_WARNING: "\u26a0\ufe0f",  # ⚠️
    AlertLevel.P2_INFO: "\u2139\ufe0f",     # ℹ️
}


def _classify_alert_level(status: str) -> str:
    """Map a health status string to an AlertLevel constant."""
    return _STATUS_TO_ALERT.get(status, AlertLevel.P0_CRITICAL)


# ---------------------------------------------------------------------------
# Slack Alert Formatting
# ---------------------------------------------------------------------------

def format_slack_alert(health_report: HealthReport) -> Optional[str]:
    """Generate a Slack alert message from a health report.

    Only returns a message when the report contains P0 (critical) items.
    Returns ``None`` if there is nothing urgent to report.

    The message uses Slack mrkdwn formatting.
    """
    critical_items: list[HealthStatus] = [
        a for a in health_report.agents if a.status in ("critical", "unknown")
    ]

    # Also check pipeline components
    if health_report.pipeline:
        for entry in (health_report.pipeline.daily_report,
                      health_report.pipeline.action_report):
            if entry.status in ("critical", "unknown"):
                critical_items.append(entry)

    if not critical_items:
        return None

    lines: list[str] = []
    lines.append("\U0001f6a8 *Synapse System Alert*")
    lines.append("")
    lines.append(f"*Status*: {health_report.overall.upper()}")
    lines.append(f"*Time*: {health_report.timestamp:%Y-%m-%d %H:%M:%S UTC}")
    lines.append("")
    lines.append("*Failing items:*")

    for item in critical_items:
        since = (
            item.last_execution.strftime("%Y-%m-%d %H:%M")
            if item.last_execution
            else "never"
        )
        lines.append(
            f"\u2022 *{item.agent_name}* \u2014 {item.status}: "
            f"{item.message} (last: {since})"
        )

    lines.append("")
    lines.append("*Suggested actions:*")
    lines.append("1. Check remote Agent configuration on `https://claude.ai/code/scheduled`")
    lines.append("2. Run `/schedule list` to verify scheduled task status")
    lines.append("3. Review git log for recent execution artifacts")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Alert Action Generation
# ---------------------------------------------------------------------------

def generate_alert_actions(health_report: HealthReport) -> list[dict]:
    """Generate a list of alert actions based on the health report.

    Returns a list of action dicts that the caller (scheduled Agent or
    plan-day Skill) can use to dispatch notifications.  This function does
    **not** call any external API itself — it only produces the action plan.

    Each action dict has the shape::

        {
            "level": "P0" | "P1" | "P2",
            "action": "slack_send" | "include_in_plan_day" | "include_in_weekly",
            "channel": str | None,
            "message": str | None,
            "items": list[dict] | None,
            "immediate": bool,
        }
    """
    actions: list[dict] = []

    # Collect items by alert level
    p0_items: list[HealthStatus] = []
    p1_items: list[HealthStatus] = []
    p2_items: list[HealthStatus] = []

    all_entries: list[HealthStatus] = list(health_report.agents)
    if health_report.pipeline:
        all_entries.append(health_report.pipeline.daily_report)
        all_entries.append(health_report.pipeline.action_report)

    for entry in all_entries:
        level = _classify_alert_level(entry.status)
        if level == AlertLevel.P0_CRITICAL:
            p0_items.append(entry)
        elif level == AlertLevel.P1_WARNING:
            p1_items.append(entry)
        else:
            p2_items.append(entry)

    # P0 — immediate Slack push
    if p0_items:
        slack_message = format_slack_alert(health_report)
        actions.append({
            "level": AlertLevel.P0_CRITICAL,
            "action": "slack_send",
            "channel": "#synapse-alerts",
            "message": slack_message,
            "items": [
                {
                    "agent": item.agent_name,
                    "status": item.status,
                    "message": item.message,
                    "last_execution": (
                        item.last_execution.isoformat()
                        if item.last_execution
                        else None
                    ),
                }
                for item in p0_items
            ],
            "immediate": True,
        })

    # P1 — fold into plan-day morning check
    if p1_items:
        actions.append({
            "level": AlertLevel.P1_WARNING,
            "action": "include_in_plan_day",
            "channel": None,
            "message": None,
            "items": [
                {
                    "agent": item.agent_name,
                    "status": item.status,
                    "message": item.message,
                    "last_execution": (
                        item.last_execution.isoformat()
                        if item.last_execution
                        else None
                    ),
                }
                for item in p1_items
            ],
            "immediate": False,
        })

    # P2 — weekly summary only
    if p2_items:
        actions.append({
            "level": AlertLevel.P2_INFO,
            "action": "include_in_weekly",
            "channel": None,
            "message": None,
            "items": [
                {
                    "agent": item.agent_name,
                    "status": item.status,
                    "message": item.message,
                    "last_execution": (
                        item.last_execution.isoformat()
                        if item.last_execution
                        else None
                    ),
                }
                for item in p2_items
            ],
            "immediate": False,
        })

    return actions


# ---------------------------------------------------------------------------
# Plan-Day Morning Check Interface
# ---------------------------------------------------------------------------

def get_morning_check_items() -> list[dict]:
    """Return P1 + P2 items for the /plan-day morning check.

    Runs a full health check and returns a list of attention items at
    warning or info level (P0 critical items are handled via immediate
    Slack push and are excluded here to avoid duplication).

    Each item has the shape::

        {
            "level": "P1" | "P2",
            "agent": str,
            "message": str,
            "since": str | None,   # ISO timestamp of last execution
        }
    """
    report = generate_health_report()

    items: list[dict] = []
    all_entries: list[HealthStatus] = list(report.agents)
    if report.pipeline:
        all_entries.append(report.pipeline.daily_report)
        all_entries.append(report.pipeline.action_report)

    for entry in all_entries:
        level = _classify_alert_level(entry.status)
        if level in (AlertLevel.P1_WARNING, AlertLevel.P2_INFO):
            items.append({
                "level": level,
                "agent": entry.agent_name,
                "message": entry.message,
                "since": (
                    entry.last_execution.isoformat()
                    if entry.last_execution
                    else None
                ),
            })

    return items


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Print a health report to stdout.

    Usage::

        python -m test_runner.health_monitor            # report only
        python -m test_runner.health_monitor --alert     # report + alert actions JSON
    """
    alert_mode = "--alert" in sys.argv

    report = generate_health_report()

    print("=" * 60)
    print(f"  Synapse Health Report  \u2014  {report.timestamp:%Y-%m-%d %H:%M:%S UTC}")
    print(f"  Overall: {report.overall.upper()}")
    print("=" * 60)

    print("\n--- Scheduled Agents ---")
    for agent in report.agents:
        icon = {"healthy": "[OK]", "warning": "[!!]", "critical": "[XX]"}.get(
            agent.status, "[??]"
        )
        last = agent.last_execution.strftime("%Y-%m-%d %H:%M") if agent.last_execution else "never"
        print(f"  {icon} {agent.agent_name:<30} last={last}  {agent.message}")

    if report.pipeline:
        print("\n--- Intelligence Pipeline ---")
        for entry in (report.pipeline.daily_report, report.pipeline.action_report):
            icon = {"healthy": "[OK]", "warning": "[!!]", "critical": "[XX]"}.get(
                entry.status, "[??]"
            )
            last = entry.last_execution.strftime("%Y-%m-%d %H:%M") if entry.last_execution else "never"
            print(f"  {icon} {entry.agent_name:<30} last={last}  {entry.message}")
        print(f"  Pipeline overall: {report.pipeline.overall.upper()}")

    print(f"\nSummary: {report.summary}")

    if alert_mode:
        actions = generate_alert_actions(report)
        print("\n--- Alert Actions (JSON) ---")
        print(json.dumps(actions, indent=2, ensure_ascii=False, default=str))

        # Also show the Slack message preview if there is one
        slack_msg = format_slack_alert(report)
        if slack_msg:
            print("\n--- Slack Message Preview ---")
            print(slack_msg)
        else:
            print("\n(No P0 alerts — no immediate Slack message needed)")

    print()


if __name__ == "__main__":
    main()
