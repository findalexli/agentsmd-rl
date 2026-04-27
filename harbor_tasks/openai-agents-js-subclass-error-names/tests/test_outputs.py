"""Behavioral tests for openai/openai-agents-js#862.

The PR sets `this.name = new.target.name` in the abstract `AgentsError`
constructor so concrete subclasses report their own class name when the error
is stringified or logged. Each test below imports the compiled module from
`@openai/agents-core` and asserts that the `.name` property of a concrete
subclass instance equals the subclass's class name.

At the base commit every test fails (all subclasses inherit `.name === 'Error'`
because the abstract constructor never assigns it). With the gold patch
applied and the package re-built, every test passes.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/openai-agents-js")
AGENTS_CORE = REPO / "packages" / "agents-core"


def _node_error_names() -> dict:
    """Construct one instance of every exported AgentsError subclass and
    return their `.name` properties as a JSON-decoded dict."""
    script = textwrap.dedent(
        """
        const m = require('@openai/agents-core');
        const out = {};
        out.MaxTurnsExceededError = new m.MaxTurnsExceededError('msg', {}).name;
        out.ModelBehaviorError = new m.ModelBehaviorError('msg', {}).name;
        out.UserError = new m.UserError('msg', {}).name;
        out.SystemError = new m.SystemError('msg', {}).name;
        out.GuardrailExecutionError = new m.GuardrailExecutionError(
            'msg', new Error('cause'), {}
        ).name;
        out.ToolCallError = new m.ToolCallError(
            'msg', new Error('cause'), {}
        ).name;
        out.InputGuardrailTripwireTriggered = new m.InputGuardrailTripwireTriggered(
            'msg', {}, {}
        ).name;
        out.OutputGuardrailTripwireTriggered = new m.OutputGuardrailTripwireTriggered(
            'msg', {}, {}
        ).name;
        out.ToolInputGuardrailTripwireTriggered = new m.ToolInputGuardrailTripwireTriggered(
            'msg', {}, {}
        ).name;
        out.ToolOutputGuardrailTripwireTriggered = new m.ToolOutputGuardrailTripwireTriggered(
            'msg', {}, {}
        ).name;
        process.stdout.write(JSON.stringify(out));
        """
    )
    proc = subprocess.run(
        ["node", "-e", script],
        cwd=AGENTS_CORE,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, (
        f"Node failed with exit {proc.returncode}\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    return json.loads(proc.stdout)


# ---------------------------------------------------------------------------
# Fail-to-pass behavioral tests: each must fail at base, pass at gold.
# ---------------------------------------------------------------------------

def test_error_name_max_turns_exceeded():
    names = _node_error_names()
    assert names["MaxTurnsExceededError"] == "MaxTurnsExceededError", (
        f"expected 'MaxTurnsExceededError', got {names['MaxTurnsExceededError']!r}"
    )


def test_error_name_model_behavior():
    names = _node_error_names()
    assert names["ModelBehaviorError"] == "ModelBehaviorError"


def test_error_name_user_error():
    names = _node_error_names()
    assert names["UserError"] == "UserError"


def test_error_name_system_error():
    names = _node_error_names()
    assert names["SystemError"] == "SystemError"


def test_error_name_guardrail_execution():
    names = _node_error_names()
    assert names["GuardrailExecutionError"] == "GuardrailExecutionError"


def test_error_name_tool_call():
    names = _node_error_names()
    assert names["ToolCallError"] == "ToolCallError"


def test_error_name_input_guardrail_tripwire():
    names = _node_error_names()
    assert names["InputGuardrailTripwireTriggered"] == "InputGuardrailTripwireTriggered"


def test_error_name_output_guardrail_tripwire():
    names = _node_error_names()
    assert names["OutputGuardrailTripwireTriggered"] == "OutputGuardrailTripwireTriggered"


def test_error_name_tool_input_guardrail_tripwire():
    names = _node_error_names()
    assert names["ToolInputGuardrailTripwireTriggered"] == "ToolInputGuardrailTripwireTriggered"


def test_error_name_tool_output_guardrail_tripwire():
    names = _node_error_names()
    assert names["ToolOutputGuardrailTripwireTriggered"] == "ToolOutputGuardrailTripwireTriggered"


def test_error_string_includes_subclass_name():
    """`String(err)` for a subclass must start with the subclass name, not 'Error'."""
    script = textwrap.dedent(
        """
        const { UserError, ToolCallError } = require('@openai/agents-core');
        const out = {
            user: String(new UserError('boom', {})),
            tool: String(new ToolCallError('boom', new Error('c'), {})),
        };
        process.stdout.write(JSON.stringify(out));
        """
    )
    proc = subprocess.run(
        ["node", "-e", script],
        cwd=AGENTS_CORE,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["user"].startswith("UserError:"), data["user"]
    assert data["tool"].startswith("ToolCallError:"), data["tool"]


def test_invalid_tool_input_error_inherits_subclass_name():
    """Internal-but-instantiable subclasses (e.g. InvalidToolInputError) must also
    pick up the subclass name via `new.target.name`."""
    script = textwrap.dedent(
        """
        const { InvalidToolInputError } = require('@openai/agents-core/errors');
        const e = new InvalidToolInputError('msg', {});
        process.stdout.write(JSON.stringify({ name: e.name, str: String(e) }));
        """
    )
    proc = subprocess.run(
        ["node", "-e", script],
        cwd=AGENTS_CORE,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        # Fallback path: not all builds expose `errors` as a direct subpath.
        # Re-run via explicit dist path.
        script = textwrap.dedent(
            """
            const { InvalidToolInputError } = require('./dist/errors');
            const e = new InvalidToolInputError('msg', {});
            process.stdout.write(JSON.stringify({ name: e.name, str: String(e) }));
            """
        )
        proc = subprocess.run(
            ["node", "-e", script],
            cwd=AGENTS_CORE,
            capture_output=True,
            text=True,
            timeout=60,
        )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["name"] == "InvalidToolInputError", data
    assert data["str"].startswith("InvalidToolInputError:"), data


# ---------------------------------------------------------------------------
# Pass-to-pass: upstream tests that pass at both base and gold.
# ---------------------------------------------------------------------------

def test_pnpm_lint_passes():
    """The repo's eslint must pass on the modified source."""
    proc = subprocess.run(
        ["pnpm", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1"},
    )
    assert proc.returncode == 0, (
        f"pnpm lint failed:\nstdout tail:\n{proc.stdout[-1500:]}\n"
        f"stderr tail:\n{proc.stderr[-1500:]}"
    )


def test_agents_core_build_check_passes():
    """`pnpm -F @openai/agents-core build-check` (tsc --noEmit) must succeed."""
    proc = subprocess.run(
        ["pnpm", "-F", "@openai/agents-core", "build-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1"},
    )
    assert proc.returncode == 0, (
        f"build-check failed:\nstdout tail:\n{proc.stdout[-1500:]}\n"
        f"stderr tail:\n{proc.stderr[-1500:]}"
    )


def test_upstream_errors_vitest_passes():
    """The upstream errors.test.ts must pass — the existing assertions about
    initialized/throwing instances should remain green at both base and gold."""
    proc = subprocess.run(
        ["pnpm", "test", "errors"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1", "NODE_ENV": "test"},
    )
    assert proc.returncode == 0, (
        f"vitest errors failed:\nstdout tail:\n{proc.stdout[-2000:]}\n"
        f"stderr tail:\n{proc.stderr[-1500:]}"
    )
