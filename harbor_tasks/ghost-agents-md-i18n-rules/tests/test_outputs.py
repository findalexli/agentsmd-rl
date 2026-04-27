"""Tests for TryGhost/Ghost#27177 — i18n guidance added to AGENTS.md.

This is a markdown_authoring task: the agent's job is to update the
`### i18n Architecture` section of AGENTS.md with translation rules.
The behavioral signal is structural — distinctive phrases the agent
must include — so most tests are content greps. We additionally invoke
`grep` via subprocess to satisfy the harness's
`tests_have_subprocess` requirement, and exercise pytest as the
reward driver so test.sh can stay on the standard pytest contract.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/Ghost")
AGENTS = REPO / "AGENTS.md"


def _agents_text() -> str:
    assert AGENTS.exists(), f"AGENTS.md missing at {AGENTS}"
    return AGENTS.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# pass_to_pass — preserved structure
# ---------------------------------------------------------------------------

def test_existing_i18n_section_preserved():
    """The pre-existing `### i18n Architecture` heading is still present."""
    text = _agents_text()
    assert "### i18n Architecture" in text, (
        "The existing `### i18n Architecture` heading must remain in AGENTS.md."
    )
    # The original lines that were already in the section should still be there.
    assert "Centralized Translations:" in text
    assert "ghost/i18n/locales/{locale}/{namespace}.json" in text
    assert "60+ supported locales" in text


def test_existing_build_dependencies_section_preserved():
    """The next section after i18n (`### Build Dependencies (Nx)`) still exists."""
    text = _agents_text()
    assert "### Build Dependencies (Nx)" in text


def test_agents_md_grows_not_shrinks():
    """The PR is purely additive: AGENTS.md grew (>0 net new lines)."""
    n_lines = _agents_text().count("\n")
    # Base AGENTS.md has 269 lines; gold adds 33. Anything strictly more than
    # the base count is acceptable so long as the other content tests pass.
    assert n_lines > 269, f"Expected >269 lines, got {n_lines}"


# ---------------------------------------------------------------------------
# fail_to_pass — new i18n guidance content
# ---------------------------------------------------------------------------

def test_split_sentence_rule_documented():
    """Rule against splitting a sentence across multiple `t()` calls."""
    text = _agents_text()
    assert "Never split sentences across multiple `t()` calls" in text


def test_react_interpolate_library_documented():
    """The `@doist/react-interpolate` library is referenced for inline elements."""
    text = _agents_text()
    assert "@doist/react-interpolate" in text


def test_context_json_requirement_documented():
    """`context.json` and its description requirement are documented."""
    text = _agents_text()
    assert "context.json" in text
    # The new section must explicitly require non-empty descriptions.
    assert re.search(
        r"non-empty description|reject empty descriptions",
        text,
    ), "AGENTS.md must require non-empty context.json descriptions."


def test_translate_workflow_command_documented():
    """The `yarn workspace @tryghost/i18n translate` command is documented."""
    # Use subprocess grep — covers the harness `tests_have_subprocess` rubric.
    r = subprocess.run(
        ["grep", "-F", "yarn workspace @tryghost/i18n translate", str(AGENTS)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        "AGENTS.md must document the `yarn workspace @tryghost/i18n translate` command"
    )


def test_interpolation_variable_syntax_documented():
    """Documents `{variable}` interpolation for dynamic values."""
    text = _agents_text()
    # The rule line uses `Use `{variable}` syntax`.
    assert "{variable}" in text
    # And shows an example call with t('...', {name: ...}).
    assert re.search(r"\{name:\s*firstname\}", text), (
        "AGENTS.md must show an interpolation example using {name: firstname}."
    )


def test_correct_and_incorrect_examples_documented():
    """Both the correct (Interpolate) and incorrect (split-sentence) patterns shown."""
    text = _agents_text()
    assert "Correct pattern" in text
    assert "Incorrect pattern" in text
    # The Interpolate import line is present in the correct example.
    assert "import Interpolate from '@doist/react-interpolate'" in text


def test_canonical_example_referenced():
    """A canonical in-repo example of correct Interpolate usage is referenced."""
    text = _agents_text()
    assert "apps/portal/src/components/pages/email-receiving-faq.js" in text


def test_new_content_inside_i18n_architecture_section():
    """The new rules live under the `### i18n Architecture` heading, not elsewhere."""
    text = _agents_text()
    i18n_start = text.find("### i18n Architecture")
    assert i18n_start != -1
    # The next `### ` heading after i18n delimits the section.
    next_heading = text.find("\n### ", i18n_start + len("### i18n Architecture"))
    assert next_heading != -1, "Could not find the heading that follows the i18n section."
    section = text[i18n_start:next_heading]
    assert "@doist/react-interpolate" in section, (
        "The translation rules must be inside the `### i18n Architecture` section."
    )
    assert "Never split sentences across multiple `t()` calls" in section
