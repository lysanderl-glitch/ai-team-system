"""
Synapse Session Runner — Skill E2E Test Execution Engine
=========================================================

Core module for running end-to-end smoke tests against Synapse Skills.
Executes Skills via `claude -p --output-format stream-json` in isolated
temporary directories, parses the NDJSON output stream, and returns
structured test results.

Architecture:
    1. parse_ndjson()     - Parse NDJSON stream into tool calls, transcript, cost
    2. run_skill_test()   - Execute a single prompt via claude CLI subprocess
    3. run_skill_smoke()  - High-level orchestrator: setup -> execute -> teardown

Based on the design in:
    obs/03-process-knowledge/quality-assurance-framework.md (Section 4.1)

Adapted from gstack's test/helpers/session-runner.ts for Python + Synapse.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ToolCall:
    """A single tool invocation extracted from the NDJSON stream."""
    tool: str
    input: dict = field(default_factory=dict)
    output: str = ""


@dataclass
class CostEstimate:
    """Token usage and cost information from the result event."""
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0
    turns_used: int = 0


@dataclass
class SkillTestResult:
    """Complete result of a single skill test execution."""
    tool_calls: list[ToolCall] = field(default_factory=list)
    exit_reason: str = "unknown"
    duration: float = 0.0
    output: str = ""
    cost_estimate: CostEstimate = field(default_factory=CostEstimate)
    transcript: list[dict] = field(default_factory=list)
    model: str = ""
    errors: list[str] = field(default_factory=list)


@dataclass
class SmokeSuiteResult:
    """Result of a full smoke test scenario (execution + metadata for assertions)."""
    skill_name: str = ""
    scenario_name: str = ""
    test_result: Optional[SkillTestResult] = None
    assertions: list[dict] = field(default_factory=list)  # populated by assertion_engine


# ---------------------------------------------------------------------------
# Default configuration
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TURNS = 10
DEFAULT_TIMEOUT = 120
DEFAULT_ALLOWED_TOOLS = ["Bash", "Read", "Write", "Edit", "Grep", "Glob"]


# ---------------------------------------------------------------------------
# NDJSON Parser
# ---------------------------------------------------------------------------

def parse_ndjson(lines: list[str]) -> dict[str, Any]:
    """
    Parse NDJSON output from ``claude -p --output-format stream-json``.

    Extracts:
        - transcript:  list of all parsed JSON events
        - result_line: the final ``type: "result"`` event (or None)
        - tool_calls:  ordered list of ToolCall objects
        - turn_count:  number of assistant turns observed

    Adapted from gstack session-runner.ts ``parseNDJSON()``.

    Parameters
    ----------
    lines : list[str]
        Raw lines of NDJSON output (one JSON object per line).

    Returns
    -------
    dict with keys ``transcript``, ``result_line``, ``tool_calls``, ``turn_count``.
    """
    transcript: list[dict] = []
    result_line: Optional[dict] = None
    tool_calls: list[ToolCall] = []
    turn_count: int = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            logger.debug("Skipping malformed NDJSON line: %s", line[:120])
            continue

        transcript.append(event)

        # Count assistant turns and extract tool_use blocks
        if event.get("type") == "assistant":
            turn_count += 1
            content = event.get("message", {}).get("content", [])
            for item in content:
                if item.get("type") == "tool_use":
                    tool_calls.append(ToolCall(
                        tool=item.get("name", "unknown"),
                        input=item.get("input", {}),
                    ))

        # Extract tool_result content to pair with the preceding tool_use
        if event.get("type") == "tool_result":
            content = event.get("content", "")
            # Attach output to the most recent matching tool call if possible
            if tool_calls:
                last_call = tool_calls[-1]
                if not last_call.output:
                    if isinstance(content, list):
                        # content can be a list of text blocks
                        last_call.output = "\n".join(
                            block.get("text", "") for block in content
                            if isinstance(block, dict)
                        )
                    elif isinstance(content, str):
                        last_call.output = content

        # Capture the result summary event
        if event.get("type") == "result":
            result_line = event

    return {
        "transcript": transcript,
        "result_line": result_line,
        "tool_calls": tool_calls,
        "turn_count": turn_count,
    }


# ---------------------------------------------------------------------------
# Core test executor
# ---------------------------------------------------------------------------

def run_skill_test(
    prompt: str,
    working_directory: str,
    max_turns: int = DEFAULT_MAX_TURNS,
    allowed_tools: Optional[list[str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
    model: Optional[str] = None,
) -> SkillTestResult:
    """
    Execute a single Skill test via ``claude -p`` in an isolated directory.

    The prompt is written to a temporary file to avoid shell-escaping issues
    (following gstack's approach). The CLI is invoked with ``--output-format
    stream-json`` so we get a full NDJSON transcript.

    Parameters
    ----------
    prompt : str
        The user prompt to send to claude (typically a slash-command invocation).
    working_directory : str
        The directory claude should run in (cwd). Should be a disposable temp dir.
    max_turns : int
        Maximum agentic turns before the CLI stops.
    allowed_tools : list[str] | None
        Explicit tool allowlist. ``None`` uses DEFAULT_ALLOWED_TOOLS.
    timeout : int
        Subprocess timeout in seconds.
    model : str | None
        Model to use. ``None`` reads ``SYNAPSE_TEST_MODEL`` env var or falls
        back to DEFAULT_MODEL.

    Returns
    -------
    SkillTestResult
        Structured result including tool calls, cost, exit reason, etc.
    """
    if allowed_tools is None:
        allowed_tools = list(DEFAULT_ALLOWED_TOOLS)
    if model is None:
        model = os.environ.get("SYNAPSE_TEST_MODEL", DEFAULT_MODEL)

    start_time = time.time()

    # Write prompt to a temp file to avoid shell-escaping issues
    prompt_fd, prompt_path = tempfile.mkstemp(
        prefix="synapse-test-prompt-", suffix=".txt"
    )
    try:
        with os.fdopen(prompt_fd, "w", encoding="utf-8") as f:
            f.write(prompt)
    except Exception:
        # If writing fails, close the fd and clean up
        try:
            os.close(prompt_fd)
        except OSError:
            pass
        try:
            os.unlink(prompt_path)
        except OSError:
            pass
        raise

    # Build CLI arguments
    args = [
        "claude", "-p",
        "--model", model,
        "--output-format", "stream-json",
        "--verbose",
        "--dangerously-skip-permissions",
        "--max-turns", str(max_turns),
    ]
    # Append each allowed tool as a separate argument
    if allowed_tools:
        args.append("--allowed-tools")
        args.extend(allowed_tools)

    stdin_file = None
    try:
        stdin_file = open(prompt_path, "r", encoding="utf-8")
        proc = subprocess.run(
            args,
            stdin=stdin_file,
            capture_output=True,
            text=True,
            cwd=working_directory,
            timeout=timeout,
        )
        exit_code = proc.returncode
        stdout_lines = proc.stdout.strip().split("\n") if proc.stdout else []
        stderr_text = proc.stderr or ""

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        logger.warning("Skill test timed out after %ds", timeout)
        return SkillTestResult(
            exit_reason="timeout",
            duration=duration,
            model=model,
            errors=[f"Timeout after {timeout}s"],
        )
    except FileNotFoundError:
        duration = time.time() - start_time
        logger.error("claude CLI not found on PATH")
        return SkillTestResult(
            exit_reason="cli_not_found",
            duration=duration,
            model=model,
            errors=["claude CLI not found — ensure it is installed and on PATH"],
        )
    except Exception as exc:
        duration = time.time() - start_time
        logger.error("Unexpected error running claude CLI: %s", exc)
        return SkillTestResult(
            exit_reason="error",
            duration=duration,
            model=model,
            errors=[f"Unexpected error: {exc}"],
        )
    finally:
        if stdin_file is not None:
            stdin_file.close()
        try:
            os.unlink(prompt_path)
        except OSError:
            pass

    duration = time.time() - start_time

    # Parse NDJSON output
    parsed = parse_ndjson(stdout_lines)

    # Determine exit reason from the result event
    result_line = parsed["result_line"]
    exit_reason = _determine_exit_reason(result_line, exit_code)

    # Build cost estimate
    cost = _extract_cost_estimate(result_line)

    # Collect errors from stderr if present
    errors: list[str] = []
    if stderr_text.strip():
        errors.append(stderr_text.strip())

    return SkillTestResult(
        tool_calls=parsed["tool_calls"],
        exit_reason=exit_reason,
        duration=duration,
        output=result_line.get("result", "") if result_line else "",
        cost_estimate=cost,
        transcript=parsed["transcript"],
        model=model,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# High-level smoke test orchestrator
# ---------------------------------------------------------------------------

def run_skill_smoke(
    skill_name: str,
    scenario: dict[str, Any],
) -> SmokeSuiteResult:
    """
    Run a complete smoke test for a single scenario of a Skill.

    Lifecycle:
        1. Create an isolated temporary directory
        2. Prepare preconditions (create files, directories, etc.)
        3. Execute the skill prompt via ``run_skill_test``
        4. Package the result (assertions are left for assertion_engine)
        5. Clean up the temporary directory

    Parameters
    ----------
    skill_name : str
        Name of the skill being tested (e.g. "capture").
    scenario : dict
        A scenario dict from test_scenarios, with keys:
            - name (str): scenario display name
            - input (str): the prompt / slash-command to run
            - preconditions (dict, optional): files to create, dirs to make
            - max_turns (int, optional): override DEFAULT_MAX_TURNS
            - timeout (int, optional): override DEFAULT_TIMEOUT
            - expected (dict, optional): assertion spec (passed through, not evaluated here)

    Returns
    -------
    SmokeSuiteResult
        Contains the SkillTestResult and metadata. The ``assertions`` field
        is left empty — it will be populated by the assertion_engine module.
    """
    scenario_name = scenario.get("name", "unnamed")
    prompt = scenario.get("input", "")
    preconditions = scenario.get("preconditions", {})
    max_turns = scenario.get("max_turns", DEFAULT_MAX_TURNS)
    timeout = scenario.get("timeout", DEFAULT_TIMEOUT)

    logger.info(
        "Running smoke test: skill=%s scenario=%s", skill_name, scenario_name
    )

    tmp_dir = tempfile.mkdtemp(prefix=f"synapse-smoke-{skill_name}-")

    try:
        # Prepare preconditions
        _prepare_preconditions(tmp_dir, preconditions)

        # Execute the test
        test_result = run_skill_test(
            prompt=prompt,
            working_directory=tmp_dir,
            max_turns=max_turns,
            timeout=timeout,
        )

        return SmokeSuiteResult(
            skill_name=skill_name,
            scenario_name=scenario_name,
            test_result=test_result,
            assertions=[],  # to be filled by assertion_engine
        )

    except Exception as exc:
        logger.error(
            "Smoke test failed with exception: skill=%s scenario=%s error=%s",
            skill_name, scenario_name, exc,
        )
        error_result = SkillTestResult(
            exit_reason="setup_error",
            errors=[f"Smoke test setup/execution error: {exc}"],
        )
        return SmokeSuiteResult(
            skill_name=skill_name,
            scenario_name=scenario_name,
            test_result=error_result,
            assertions=[],
        )

    finally:
        # Clean up the temporary directory
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            logger.debug("Cleaned up temp dir: %s", tmp_dir)
        except Exception as cleanup_err:
            logger.warning("Failed to clean up temp dir %s: %s", tmp_dir, cleanup_err)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _determine_exit_reason(result_line: Optional[dict], exit_code: int) -> str:
    """Derive a human-readable exit reason from the result event or exit code."""
    if result_line:
        subtype = result_line.get("subtype", "")
        is_error = result_line.get("is_error", False)
        if subtype == "success" and not is_error:
            return "success"
        if subtype == "success" and is_error:
            return "error_api"
        if subtype:
            return subtype
    # Fallback to exit code
    if exit_code == 0:
        return "success"
    return f"exit_code_{exit_code}"


def _extract_cost_estimate(result_line: Optional[dict]) -> CostEstimate:
    """Extract token usage and cost from the result event."""
    if not result_line:
        return CostEstimate()

    usage = result_line.get("usage", {})
    return CostEstimate(
        input_tokens=usage.get("input_tokens", 0),
        output_tokens=usage.get("output_tokens", 0),
        estimated_cost=result_line.get("total_cost_usd", 0.0),
        turns_used=result_line.get("num_turns", 0),
    )


def _prepare_preconditions(tmp_dir: str, preconditions: dict[str, Any]) -> None:
    """
    Set up the test environment in *tmp_dir* according to *preconditions*.

    Supported precondition keys:
        - files: list of {path, content} dicts — create files with given content
        - directories: list of dir paths to create

    All paths are relative to tmp_dir.
    """
    base = Path(tmp_dir)

    # Create directories
    for dir_path in preconditions.get("directories", []):
        target = base / dir_path
        target.mkdir(parents=True, exist_ok=True)
        logger.debug("Created precondition dir: %s", target)

    # Create files
    for file_spec in preconditions.get("files", []):
        file_path = file_spec.get("path", "")
        content = file_spec.get("content", "")
        if not file_path:
            continue
        target = base / file_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        logger.debug("Created precondition file: %s (%d bytes)", target, len(content))
