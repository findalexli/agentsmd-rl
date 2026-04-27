"""Behavioral checks for github-copilot-for-azure-add-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/github-copilot-for-azure")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/investigate-integration-test/SKILL.md')
    assert 'description: "Investigate a failing integration test from a GitHub issue. Downloads logs/artifacts, analyzes the failure, examines relevant skills, and suggests fixes. TRIGGERS: investigate integratio' in text, "expected to find: " + 'description: "Investigate a failing integration test from a GitHub issue. Downloads logs/artifacts, analyzes the failure, examines relevant skills, and suggests fixes. TRIGGERS: investigate integratio'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/investigate-integration-test/SKILL.md')
    assert '3. Look through the logs/artifacts and analyze the test with the prompt specified in the issue to diagnose the failure.' in text, "expected to find: " + '3. Look through the logs/artifacts and analyze the test with the prompt specified in the issue to diagnose the failure.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/investigate-integration-test/SKILL.md')
    assert "5. Offer a suggested fix for each identified problem. Do not implement any fixes without the user's approval." in text, "expected to find: " + "5. Offer a suggested fix for each identified problem. Do not implement any fixes without the user's approval."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/submit-skill-fix-pr/SKILL.md')
    assert 'description: "Submit a pull request with skill fixes. Validates skill structure, bumps versions, and creates a PR with a proper description. TRIGGERS: submit skill fix, create fix PR, skill fix pull r' in text, "expected to find: " + 'description: "Submit a pull request with skill fixes. Validates skill structure, bumps versions, and creates a PR with a proper description. TRIGGERS: submit skill fix, create fix PR, skill fix pull r'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/submit-skill-fix-pr/SKILL.md')
    assert '2. From the `scripts` directory run `npm run frontmatter` and `npm run references` to validate the skill structure. Fix and commit any problems.' in text, "expected to find: " + '2. From the `scripts` directory run `npm run frontmatter` and `npm run references` to validate the skill structure. Fix and commit any problems.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/submit-skill-fix-pr/SKILL.md')
    assert '4. Push the branch to origin and create a PR into upstream. The PR description should include:' in text, "expected to find: " + '4. Push the branch to origin and create a PR into upstream. The PR description should include:'[:80]

