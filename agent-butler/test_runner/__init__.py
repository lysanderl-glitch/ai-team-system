"""
Synapse Skill E2E Test Runner
==============================

This package provides the infrastructure for running end-to-end smoke tests
against Synapse Skills via the `claude -p` CLI in isolated environments.

Modules:
    session_runner    - Core session execution engine (parse NDJSON, run tests,
                        orchestrate smoke test lifecycle)
    assertion_engine  - Assertion primitives and batch runner for verifying
                        Skill execution results
    health_monitor    - Scheduled agent health monitoring and pipeline checks
    yaml_validator    - YAML configuration syntax and reference validation
    html_validator    - HTML report structure, completeness, and freshness checks

Usage:
    from test_runner.session_runner import run_skill_smoke, run_skill_test
    from test_runner.assertion_engine import run_assertions, assert_tool_chain
    from test_runner.health_monitor import generate_health_report
    from test_runner.yaml_validator import validate_all_yaml
    from test_runner.html_validator import validate_latest_reports

Part of the Synapse Quality Assurance Framework.
"""

from test_runner.session_runner import (
    CostEstimate,
    SkillTestResult,
    SmokeSuiteResult,
    ToolCall,
    filter_skills_by_changes,
    get_all_skill_names,
    parse_ndjson,
    run_skill_smoke,
    run_skill_test,
)

from test_runner.assertion_engine import (
    AssertionResult,
    SuiteAssertionResult,
    assert_exit_reason,
    assert_file_contains,
    assert_file_modified,
    assert_no_errors,
    assert_tool_called,
    assert_tool_chain,
    run_assertions,
)

from test_runner.health_monitor import (
    HealthReport,
    HealthStatus,
    PipelineStatus,
    check_intelligence_pipeline,
    check_scheduled_agents,
    generate_health_report,
)

from test_runner.yaml_validator import (
    ValidationIssue as YamlValidationIssue,
    ValidationResult as YamlValidationResult,
    validate_all_yaml,
    validate_yaml_references,
    validate_yaml_syntax,
)

from test_runner.html_validator import (
    ValidationIssue as HtmlValidationIssue,
    ValidationResult as HtmlValidationResult,
    validate_html_report,
    validate_latest_reports,
)

__all__ = [
    # session_runner
    "ToolCall",
    "CostEstimate",
    "SkillTestResult",
    "SmokeSuiteResult",
    "filter_skills_by_changes",
    "get_all_skill_names",
    "parse_ndjson",
    "run_skill_test",
    "run_skill_smoke",
    # assertion_engine
    "AssertionResult",
    "SuiteAssertionResult",
    "assert_tool_chain",
    "assert_tool_called",
    "assert_file_modified",
    "assert_file_contains",
    "assert_exit_reason",
    "assert_no_errors",
    "run_assertions",
    # health_monitor
    "HealthStatus",
    "PipelineStatus",
    "HealthReport",
    "check_scheduled_agents",
    "check_intelligence_pipeline",
    "generate_health_report",
    # yaml_validator
    "YamlValidationIssue",
    "YamlValidationResult",
    "validate_yaml_syntax",
    "validate_yaml_references",
    "validate_all_yaml",
    # html_validator
    "HtmlValidationIssue",
    "HtmlValidationResult",
    "validate_html_report",
    "validate_latest_reports",
]
