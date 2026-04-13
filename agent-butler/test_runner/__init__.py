"""
Synapse Skill E2E Test Runner
==============================

This package provides the infrastructure for running end-to-end smoke tests
against Synapse Skills via the `claude -p` CLI in isolated environments.

Modules:
    session_runner   - Core session execution engine (parse NDJSON, run tests,
                       orchestrate smoke test lifecycle)

Usage:
    from test_runner.session_runner import run_skill_smoke, run_skill_test

Part of the Synapse Quality Assurance Framework.
"""

from test_runner.session_runner import (
    CostEstimate,
    SkillTestResult,
    SmokeSuiteResult,
    ToolCall,
    parse_ndjson,
    run_skill_smoke,
    run_skill_test,
)

__all__ = [
    "ToolCall",
    "CostEstimate",
    "SkillTestResult",
    "SmokeSuiteResult",
    "parse_ndjson",
    "run_skill_test",
    "run_skill_smoke",
]
