"""
Synapse Health Monitor
======================

Monitors the health of scheduled remote Agents and the intelligence pipeline.
Checks execution recency via git log and file modification times.

Part of the Synapse Quality Assurance Framework.

Usage:
    from test_runner.health_monitor import (
        check_scheduled_agents,
        check_intelligence_pipeline,
        generate_health_report,
    )

    report = generate_health_report()
    for entry in report["agents"]:
        print(f"{entry.agent_name}: {entry.status} — {entry.message}")
"""

from __future__ import annotations

import os
import re
import subprocess
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
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Print a health report to stdout."""
    report = generate_health_report()

    print("=" * 60)
    print(f"  Synapse Health Report  —  {report.timestamp:%Y-%m-%d %H:%M:%S UTC}")
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
    print()


if __name__ == "__main__":
    main()
