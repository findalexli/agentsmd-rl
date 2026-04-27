"""Behavioral tests for cloudflare/workers-sdk#13407.

Agent's task: implement
`packages/local-explorer-ui/src/utils/agent-prompt.ts` with three exported
functions: `getLocalExplorerApiEndpoint`, `createLocalExplorerPrompt`, and
`copyTextToClipboard`.

We don't run vitest from inside the workers-sdk monorepo (full pnpm install
is expensive and not needed). Instead, an isolated `/test-runner/`
directory has vitest pre-installed and a copy of the upstream PR's test
suite. Each test below copies the agent's source file into the runner and
invokes vitest with a `-t` filter to assert the matching test name passes.
"""

from __future__ import annotations

import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

REPO = Path("/workspace/workers-sdk")
TARGET = REPO / "packages/local-explorer-ui/src/utils/agent-prompt.ts"
RUNNER = Path("/test-runner")
RUNNER_SRC = RUNNER / "src/agent-prompt.ts"


def _sync_target() -> None:
    RUNNER_SRC.parent.mkdir(parents=True, exist_ok=True)
    if TARGET.exists():
        shutil.copy(TARGET, RUNNER_SRC)
    else:
        RUNNER_SRC.write_text("// missing\n")


def _run_vitest(name_filter: str) -> subprocess.CompletedProcess:
    _sync_target()
    return subprocess.run(
        ["npx", "--no-install", "vitest", "run", "-t", name_filter, "--reporter=verbose"],
        cwd=str(RUNNER),
        capture_output=True,
        text=True,
        timeout=180,
    )


@lru_cache(maxsize=1)
def _run_full_vitest() -> subprocess.CompletedProcess:
    _sync_target()
    return subprocess.run(
        ["npx", "--no-install", "vitest", "run", "--reporter=verbose"],
        cwd=str(RUNNER),
        capture_output=True,
        text=True,
        timeout=240,
    )


def test_target_file_exists() -> None:
    """f2p: agent created the file at the expected path."""
    assert TARGET.exists(), f"Expected file at {TARGET}"
    text = TARGET.read_text()
    assert text.strip(), "File is empty"
    assert "export" in text, "File has no exports"


def test_endpoint_join_behavior() -> None:
    """f2p: getLocalExplorerApiEndpoint concatenates origin + apiPath."""
    r = _run_vitest("builds api endpoint from origin and api path")
    assert r.returncode == 0, (
        "vitest failed for endpoint-join test:\n"
        f"STDOUT:\n{r.stdout[-1500:]}\nSTDERR:\n{r.stderr[-500:]}"
    )


def test_prompt_contains_required_phrases() -> None:
    """f2p: createLocalExplorerPrompt produces the required substrings."""
    r = _run_vitest("generates prompt text with resolved api endpoint")
    assert r.returncode == 0, (
        "vitest failed for prompt-generation test:\n"
        f"STDOUT:\n{r.stdout[-1500:]}\nSTDERR:\n{r.stderr[-500:]}"
    )


def test_clipboard_calls_writetext() -> None:
    """f2p: copyTextToClipboard delegates to clipboard.writeText with the text."""
    r = _run_vitest("copies prompt text to clipboard")
    assert r.returncode == 0, (
        "vitest failed for clipboard test:\n"
        f"STDOUT:\n{r.stdout[-1500:]}\nSTDERR:\n{r.stderr[-500:]}"
    )


def test_full_vitest_suite_passes() -> None:
    """f2p: complete upstream vitest suite passes (matches PR's test file)."""
    r = _run_full_vitest()
    assert r.returncode == 0, (
        "Full vitest suite failed:\n"
        f"STDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-500:]}"
    )


def test_endpoint_join_varied_inputs() -> None:
    """f2p: endpoint join works for multiple origin/path combinations
    (anti-hardcode guard)."""
    _sync_target()
    probe = """
import {
    getLocalExplorerApiEndpoint,
} from "../src/agent-prompt";
import { test } from "vitest";

test("varied origin/path inputs", ({ expect }) => {
    const cases: [string, string, string][] = [
        ["http://localhost:8787", "/cdn-cgi/explorer/api", "http://localhost:8787/cdn-cgi/explorer/api"],
        ["https://example.com", "/api/v1", "https://example.com/api/v1"],
        ["http://0.0.0.0:3000", "/x", "http://0.0.0.0:3000/x"],
        ["https://a.b.c", "/", "https://a.b.c/"],
    ];
    for (const [origin, path, expected] of cases) {
        expect(getLocalExplorerApiEndpoint(origin, path)).toBe(expected);
    }
});
"""
    extra = RUNNER / "test/_varied.test.ts"
    extra.write_text(probe)
    try:
        r = subprocess.run(
            [
                "npx", "--no-install", "vitest", "run",
                "test/_varied.test.ts", "--reporter=verbose",
            ],
            cwd=str(RUNNER), capture_output=True, text=True, timeout=120,
        )
        assert r.returncode == 0, (
            "Varied-inputs test failed:\n"
            f"STDOUT:\n{r.stdout[-1500:]}\nSTDERR:\n{r.stderr[-500:]}"
        )
    finally:
        if extra.exists():
            extra.unlink()


def test_prompt_substitutes_endpoint_dynamically() -> None:
    """f2p: prompt text reflects the apiEndpoint parameter, not a hardcoded
    URL (anti-hardcode guard)."""
    _sync_target()
    probe = """
import { createLocalExplorerPrompt } from "../src/agent-prompt";
import { test } from "vitest";

test("prompt reflects custom endpoint", ({ expect }) => {
    const ep = "https://example.test/path/x";
    const p = createLocalExplorerPrompt(ep);
    expect(p).toContain("API endpoint: https://example.test/path/x.");
    expect(p).toContain("Fetch the OpenAPI schema from https://example.test/path/x");
    expect(p).not.toContain("{{apiEndpoint}}");
});
"""
    extra = RUNNER / "test/_dynamic.test.ts"
    extra.write_text(probe)
    try:
        r = subprocess.run(
            [
                "npx", "--no-install", "vitest", "run",
                "test/_dynamic.test.ts", "--reporter=verbose",
            ],
            cwd=str(RUNNER), capture_output=True, text=True, timeout=120,
        )
        assert r.returncode == 0, (
            "Dynamic endpoint test failed:\n"
            f"STDOUT:\n{r.stdout[-1500:]}\nSTDERR:\n{r.stderr[-500:]}"
        )
    finally:
        if extra.exists():
            extra.unlink()


def test_typescript_strict_compiles() -> None:
    """f2p: agent's file compiles cleanly under TypeScript strict mode.
    AGENTS.md mandates strict TS; tsc --noEmit is part of `pnpm check`."""
    _sync_target()
    r = subprocess.run(
        ["npx", "--no-install", "tsc", "--noEmit", "-p", "tsconfig.json"],
        cwd=str(RUNNER), capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, (
        "TypeScript strict-mode compile failed:\n"
        f"STDOUT:\n{r.stdout[-1500:]}\nSTDERR:\n{r.stderr[-500:]}"
    )


def test_existing_utils_unmodified() -> None:
    """p2p: agent did not modify pre-existing utility files in the same
    directory (regression guard against scope creep). Hashes are pinned
    to the base commit's tree."""
    import hashlib

    expected = {
        "packages/local-explorer-ui/src/utils/format.ts":
            "ff3a87da7e02fac3b7ec10f99fb97adf44324e0b34cdb433bb37d21168632fe7",
        "packages/local-explorer-ui/src/utils/sidebar-state.ts":
            "3c8c76375c7275d936054f9d140e4c17604f34fa880382fe511ac845d59deac7",
    }
    for rel, want in expected.items():
        path = REPO / rel
        assert path.exists(), f"{rel} missing — agent removed an existing file"
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        assert got == want, (
            f"{rel} was modified (sha256={got}, expected={want}). "
            "The PR's scope is limited to creating agent-prompt.ts; do not "
            "touch other utility files."
        )
