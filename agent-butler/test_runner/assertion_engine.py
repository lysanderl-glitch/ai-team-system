"""
Assertion Engine for Synapse Skill E2E Testing
===============================================

Provides assertion primitives and a batch runner for verifying Skill execution
results produced by the Session Runner.

Key capabilities:
    - Tool call chain subsequence matching (ordered, with gaps allowed)
    - Individual tool call verification with optional input content matching
    - File modification detection (git diff + existence checks)
    - File content regex matching
    - Exit reason and error-free assertions
    - Batch assertion execution via run_assertions()

All assertions return structured results (AssertionResult / SuiteAssertionResult)
and never raise exceptions on failure -- they report passed=False with details.

Part of the Synapse Quality Assurance Framework.
See: obs/03-process-knowledge/quality-assurance-framework.md section 4.3
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Import ToolCall / SkillTestResult from session_runner.
# session_runner.py may not exist yet during early development; in that case
# we define lightweight stubs so assertion_engine can be developed and tested
# independently.
# ---------------------------------------------------------------------------
try:
    from test_runner.session_runner import SkillTestResult, ToolCall
except ImportError:
    try:
        from agent_butler.test_runner.session_runner import SkillTestResult, ToolCall
    except ImportError:
        # Lightweight stubs for standalone development / unit testing.
        @dataclass
        class ToolCall:  # type: ignore[no-redef]
            """Stub -- replaced at runtime when session_runner is available."""
            tool: str = ""
            input: dict = field(default_factory=dict)
            output: str = ""

        @dataclass
        class SkillTestResult:  # type: ignore[no-redef]
            """Stub -- replaced at runtime when session_runner is available."""
            tool_calls: list = field(default_factory=list)
            exit_reason: str = "unknown"
            duration: float = 0.0
            output: str = ""
            errors: list = field(default_factory=list)


# ============================================================================
# Data classes
# ============================================================================

@dataclass
class AssertionResult:
    """Result of a single assertion check."""

    passed: bool
    assertion_type: str
    message: str
    details: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.assertion_type}: {self.message}"


@dataclass
class SuiteAssertionResult:
    """Aggregated result of running a batch of assertions."""

    total: int = 0
    passed: int = 0
    failed: int = 0
    results: list[AssertionResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return self.failed == 0 and self.total > 0

    def add(self, result: AssertionResult) -> None:
        """Append one assertion result and update counters."""
        self.results.append(result)
        self.total += 1
        if result.passed:
            self.passed += 1
        else:
            self.failed += 1

    def summary(self) -> str:
        status = "ALL PASSED" if self.all_passed else f"{self.failed} FAILED"
        return f"Assertions: {self.passed}/{self.total} passed ({status})"


# ============================================================================
# Individual assertion functions
# ============================================================================

def assert_tool_chain(
    actual_calls: list[ToolCall],
    expected_chain: list[str],
    *,
    message: Optional[str] = None,
) -> AssertionResult:
    """Verify that *actual_calls* contains *expected_chain* as an ordered subsequence.

    ``expected_chain`` is a list of tool names, e.g. ``["Read", "Edit", "Bash"]``.
    The actual call list may contain additional calls between the expected ones;
    only the relative order matters.

    A wildcard ``"*"`` in the expected chain matches any single tool name.

    Parameters
    ----------
    actual_calls:
        List of ``ToolCall`` objects captured during session execution.
    expected_chain:
        Ordered tool names that must appear as a subsequence.
    message:
        Optional custom failure/success message.

    Returns
    -------
    AssertionResult
    """
    actual_names = [c.tool for c in actual_calls]
    search_idx = 0

    for expected_tool in expected_chain:
        found = False
        while search_idx < len(actual_calls):
            actual_tool = actual_calls[search_idx].tool
            search_idx += 1

            if expected_tool == "*" or actual_tool == expected_tool:
                found = True
                break

        if not found:
            return AssertionResult(
                passed=False,
                assertion_type="tool_chain",
                message=message or (
                    f"Tool chain mismatch: expected '{expected_tool}' not found "
                    f"in remaining calls"
                ),
                details={
                    "expected_chain": expected_chain,
                    "actual_chain": actual_names,
                    "missing_tool": expected_tool,
                },
            )

    return AssertionResult(
        passed=True,
        assertion_type="tool_chain",
        message=message or "Tool chain matches expected subsequence",
        details={
            "expected_chain": expected_chain,
            "actual_chain": actual_names,
        },
    )


def assert_tool_called(
    actual_calls: list[ToolCall],
    tool_name: str,
    *,
    input_contains: Optional[str] = None,
    message: Optional[str] = None,
) -> AssertionResult:
    """Verify that a specific tool was called, optionally with input containing a string.

    Parameters
    ----------
    actual_calls:
        List of ``ToolCall`` objects.
    tool_name:
        The tool name to look for (e.g. ``"Edit"``).
    input_contains:
        If provided, at least one matching call must have this substring
        in ``str(call.input)``.
    message:
        Optional custom message.

    Returns
    -------
    AssertionResult
    """
    matching_calls = [c for c in actual_calls if c.tool == tool_name]

    if not matching_calls:
        return AssertionResult(
            passed=False,
            assertion_type="tool_called",
            message=message or f"Tool '{tool_name}' was never called",
            details={
                "expected_tool": tool_name,
                "input_contains": input_contains,
                "actual_tools": [c.tool for c in actual_calls],
            },
        )

    if input_contains is not None:
        input_matched = [
            c for c in matching_calls
            if input_contains in str(c.input)
        ]
        if not input_matched:
            return AssertionResult(
                passed=False,
                assertion_type="tool_called",
                message=message or (
                    f"Tool '{tool_name}' was called but no call's input "
                    f"contains '{input_contains}'"
                ),
                details={
                    "expected_tool": tool_name,
                    "input_contains": input_contains,
                    "matching_call_count": len(matching_calls),
                    "inputs_seen": [str(c.input)[:200] for c in matching_calls],
                },
            )

    qualifier = ""
    if input_contains:
        qualifier = f" with input containing '{input_contains}'"
    return AssertionResult(
        passed=True,
        assertion_type="tool_called",
        message=message or f"Tool '{tool_name}' was called{qualifier}",
        details={
            "expected_tool": tool_name,
            "matching_call_count": len(matching_calls),
        },
    )


def assert_file_modified(
    work_dir: str,
    file_path: str,
    *,
    message: Optional[str] = None,
) -> AssertionResult:
    """Verify that a file was modified (via git diff) or at least exists.

    Strategy:
    1. Try ``git diff --name-only`` in *work_dir* to detect tracked changes.
    2. If git is unavailable or the file is untracked, fall back to existence check.

    Parameters
    ----------
    work_dir:
        The working directory (isolated test environment root).
    file_path:
        Relative path within *work_dir* (e.g. ``"agent-butler/config/personal_tasks.yaml"``).
    message:
        Optional custom message.

    Returns
    -------
    AssertionResult
    """
    abs_path = os.path.join(work_dir, file_path)

    # Strategy 1: git diff (catches tracked modifications + staged additions)
    try:
        git_result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            cwd=work_dir,
            timeout=10,
        )
        if git_result.returncode == 0:
            changed_files = git_result.stdout.strip().splitlines()
            # Also check untracked files
            git_untracked = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                capture_output=True,
                text=True,
                cwd=work_dir,
                timeout=10,
            )
            if git_untracked.returncode == 0:
                changed_files.extend(git_untracked.stdout.strip().splitlines())

            # Normalize separators for cross-platform matching
            normalised = [f.replace("\\", "/") for f in changed_files]
            target = file_path.replace("\\", "/")

            if target in normalised:
                return AssertionResult(
                    passed=True,
                    assertion_type="file_modified",
                    message=message or f"File '{file_path}' was modified (git)",
                    details={"method": "git_diff", "file": file_path},
                )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass  # git not available -- fall through to existence check

    # Strategy 2: file existence fallback
    if os.path.exists(abs_path):
        return AssertionResult(
            passed=True,
            assertion_type="file_modified",
            message=message or f"File '{file_path}' exists (existence check; git unavailable)",
            details={"method": "existence_check", "file": file_path},
        )

    return AssertionResult(
        passed=False,
        assertion_type="file_modified",
        message=message or f"File '{file_path}' was not modified and does not exist",
        details={"file": file_path, "work_dir": work_dir},
    )


def assert_file_contains(
    work_dir: str,
    file_path: str,
    pattern: str,
    *,
    message: Optional[str] = None,
) -> AssertionResult:
    """Verify that a file's content matches a regex pattern.

    Parameters
    ----------
    work_dir:
        Working directory root.
    file_path:
        Relative path within *work_dir*.
    pattern:
        Regular expression to search for in the file content.
    message:
        Optional custom message.

    Returns
    -------
    AssertionResult
    """
    abs_path = os.path.join(work_dir, file_path)

    if not os.path.exists(abs_path):
        return AssertionResult(
            passed=False,
            assertion_type="file_contains",
            message=message or f"File '{file_path}' does not exist",
            details={"file": file_path, "pattern": pattern},
        )

    try:
        with open(abs_path, encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as exc:
        return AssertionResult(
            passed=False,
            assertion_type="file_contains",
            message=message or f"Failed to read '{file_path}': {exc}",
            details={"file": file_path, "pattern": pattern, "error": str(exc)},
        )

    match = re.search(pattern, content)
    if match:
        return AssertionResult(
            passed=True,
            assertion_type="file_contains",
            message=message or f"File '{file_path}' matches pattern '{pattern}'",
            details={
                "file": file_path,
                "pattern": pattern,
                "match": match.group(0)[:200],
            },
        )

    return AssertionResult(
        passed=False,
        assertion_type="file_contains",
        message=message or f"File '{file_path}' does not match pattern '{pattern}'",
        details={
            "file": file_path,
            "pattern": pattern,
            "content_preview": content[:300],
        },
    )


def assert_exit_reason(
    result: SkillTestResult,
    expected: str,
    *,
    message: Optional[str] = None,
) -> AssertionResult:
    """Verify the session's exit reason matches the expected value.

    Parameters
    ----------
    result:
        The ``SkillTestResult`` from session execution.
    expected:
        Expected exit reason string (e.g. ``"success"``, ``"timeout"``).
    message:
        Optional custom message.

    Returns
    -------
    AssertionResult
    """
    passed = result.exit_reason == expected
    return AssertionResult(
        passed=passed,
        assertion_type="exit_reason",
        message=message or (
            f"Exit reason is '{expected}'" if passed
            else f"Expected exit reason '{expected}', got '{result.exit_reason}'"
        ),
        details={
            "expected": expected,
            "actual": result.exit_reason,
        },
    )


def assert_no_errors(
    result: SkillTestResult,
    *,
    message: Optional[str] = None,
) -> AssertionResult:
    """Verify that the session completed without errors.

    Checks ``result.errors`` for any recorded error strings.

    Parameters
    ----------
    result:
        The ``SkillTestResult`` from session execution.
    message:
        Optional custom message.

    Returns
    -------
    AssertionResult
    """
    if not result.errors:
        return AssertionResult(
            passed=True,
            assertion_type="no_errors",
            message=message or "No errors recorded",
            details={},
        )

    return AssertionResult(
        passed=False,
        assertion_type="no_errors",
        message=message or f"Session had {len(result.errors)} error(s)",
        details={
            "error_count": len(result.errors),
            "errors": result.errors[:10],  # cap to avoid huge output
        },
    )


# ============================================================================
# Batch assertion runner
# ============================================================================

def run_assertions(
    test_result: SkillTestResult,
    expected_config: dict[str, Any],
    work_dir: str,
) -> SuiteAssertionResult:
    """Execute a batch of assertions described by *expected_config*.

    ``expected_config`` schema::

        {
            "tool_chain": ["Read", "Edit", "Bash"],
            "tool_called": [
                {"tool": "Edit", "input_contains": "personal_tasks.yaml"}
            ],
            "file_modified": [
                "agent-butler/config/personal_tasks.yaml"
            ],
            "file_contains": [
                {"file": "...", "pattern": "CAP-.*pending"}
            ],
            "exit_reason": "success",
            "no_errors": true
        }

    All keys are optional. Only present keys trigger assertions.

    Parameters
    ----------
    test_result:
        The ``SkillTestResult`` from session execution.
    expected_config:
        Dictionary describing expected outcomes (see schema above).
    work_dir:
        Working directory root for file-based assertions.

    Returns
    -------
    SuiteAssertionResult
    """
    suite = SuiteAssertionResult()

    # --- exit_reason ---
    if "exit_reason" in expected_config:
        suite.add(assert_exit_reason(test_result, expected_config["exit_reason"]))

    # --- no_errors ---
    if expected_config.get("no_errors", False):
        suite.add(assert_no_errors(test_result))

    # --- tool_chain ---
    if "tool_chain" in expected_config:
        chain = expected_config["tool_chain"]
        # Accept both ["Read", "Edit"] shorthand and [{"tool": "Read"}, ...] form
        if chain and isinstance(chain[0], str):
            suite.add(assert_tool_chain(test_result.tool_calls, chain))
        else:
            # Dict form -- extract tool names for subsequence matching and
            # additionally run input_contains checks per entry.
            tool_names = [entry.get("tool", "*") for entry in chain]
            suite.add(assert_tool_chain(test_result.tool_calls, tool_names))
            # Per-entry input_contains checks
            for entry in chain:
                if "input_contains" in entry:
                    suite.add(assert_tool_called(
                        test_result.tool_calls,
                        entry.get("tool", "*"),
                        input_contains=entry["input_contains"],
                    ))

    # --- tool_called ---
    if "tool_called" in expected_config:
        for spec in expected_config["tool_called"]:
            suite.add(assert_tool_called(
                test_result.tool_calls,
                spec["tool"],
                input_contains=spec.get("input_contains"),
            ))

    # --- file_modified ---
    if "file_modified" in expected_config:
        for fpath in expected_config["file_modified"]:
            suite.add(assert_file_modified(work_dir, fpath))

    # --- file_contains ---
    if "file_contains" in expected_config:
        for spec in expected_config["file_contains"]:
            suite.add(assert_file_contains(
                work_dir,
                spec["file"],
                spec["pattern"],
            ))

    return suite
