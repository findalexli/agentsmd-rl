"""Behavioral checks for keploy-add-agentsmd-and-claude-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/keploy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/keploy-docs/SKILL.md')
    assert 'description: Guide for contributing to the Keploy documentation site at github.com/keploy/docs. Invoke when a change in keploy/keploy introduces, removes, or alters user-visible behavior (new CLI flag' in text, "expected to find: " + 'description: Guide for contributing to the Keploy documentation site at github.com/keploy/docs. Invoke when a change in keploy/keploy introduces, removes, or alters user-visible behavior (new CLI flag'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/keploy-docs/SKILL.md')
    assert "- Don't add screenshots unless the user explicitly asked for them — they age fast. If you want to add a screenshot, ask for approval before doing so. And also them to provide you with the screenshot. " in text, "expected to find: " + "- Don't add screenshots unless the user explicitly asked for them — they age fast. If you want to add a screenshot, ask for approval before doing so. And also them to provide you with the screenshot. "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/keploy-docs/SKILL.md')
    assert 'This is non-negotiable. The current version listed in `versions.json` is `4.0.0`, and the first entry in that file is always the live one. Editing `version-3.0.0/` (or older) only changes archived pag' in text, "expected to find: " + 'This is non-negotiable. The current version listed in `versions.json` is `4.0.0`, and the first entry in that file is always the live one. Editing `version-3.0.0/` (or older) only changes archived pag'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/keploy-e2e-test/SKILL.md')
    assert "description: End-to-end verification of a change to keploy/keploy using keploy's own record/replay against a real sample application. Use whenever the user asks to test a change, verify a fix, prove t" in text, "expected to find: " + "description: End-to-end verification of a change to keploy/keploy using keploy's own record/replay against a real sample application. Use whenever the user asks to test a change, verify a fix, prove t"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/keploy-e2e-test/SKILL.md')
    assert '- If something is failing with your changes or you found a bug in the implementation using this test then please try to fix it by finding the root cause. If you cant then report it to the user.' in text, "expected to find: " + '- If something is failing with your changes or you found a bug in the implementation using this test then please try to fix it by finding the root cause. If you cant then report it to the user.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/keploy-e2e-test/SKILL.md')
    assert "- If needed, you can create a new workflow file but try to add a new step in the existing workflow file if possible. that's much better than creating a new workflow file." in text, "expected to find: " + "- If needed, you can create a new workflow file but try to add a new step in the existing workflow file if possible. that's much better than creating a new workflow file."[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/keploy-pr-workflow/SKILL.md')
    assert 'description: Guide for creating PRs and issues on keploy repositories — PR format, customer-data hygiene, commit conventions, sign-off. Invoke when the user asks to open, update, or review a pull requ' in text, "expected to find: " + 'description: Guide for creating PRs and issues on keploy repositories — PR format, customer-data hygiene, commit conventions, sign-off. Invoke when the user asks to open, update, or review a pull requ'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/keploy-pr-workflow/SKILL.md')
    assert 'The PR/issue template should match the template that is being used in the repository that we are working in.' in text, "expected to find: " + 'The PR/issue template should match the template that is being used in the repository that we are working in.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/keploy-pr-workflow/SKILL.md')
    assert '- Copying error output, logs, or sample data into a PR description, issue, test' in text, "expected to find: " + '- Copying error output, logs, or sample data into a PR description, issue, test'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Logging** — thread `*zap.Logger` explicitly (no globals); build once via `utils/log.New()`. Use `utils.LogError(logger, err, "msg", ...fields)` in place of `logger.Error(...)` — it drops `context.' in text, "expected to find: " + '- **Logging** — thread `*zap.Logger` explicitly (no globals); build once via `utils/log.New()`. Use `utils.LogError(logger, err, "msg", ...fields)` in place of `logger.Error(...)` — it drops `context.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Interfaces live where they're consumed** — each `pkg/service/<name>/service.go` defines the small interfaces that package depends on (`TestDB`, `MockDB`, `Telemetry`, `Instrumentation`, ...). Keep" in text, "expected to find: " + "- **Interfaces live where they're consumed** — each `pkg/service/<name>/service.go` defines the small interfaces that package depends on (`TestDB`, `MockDB`, `Telemetry`, `Instrumentation`, ...). Keep"[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Goroutine lifecycle** — use `errgroup.WithContext(ctx)` for any goroutine, not bare `go func()` or `sync.WaitGroup`. Split work across per-phase errgroups (setup / run-app / req) with their own ca' in text, "expected to find: " + '- **Goroutine lifecycle** — use `errgroup.WithContext(ctx)` for any goroutine, not bare `go func()` or `sync.WaitGroup`. Split work across per-phase errgroups (setup / run-app / req) with their own ca'[:80]

