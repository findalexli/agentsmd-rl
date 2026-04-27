"""Behavioural tests for angular/angular#67966 (improve angular-new-app skill).

Each test invokes a real subprocess against the SKILL.md file under
/workspace/angular/skills/dev-skills/angular-new-app/SKILL.md. Tests assert
that distinctive signal content from the gold patch is present and that the
removed/redundant content is gone. The Gemini-based Track 2 judge in
eval_manifest.yaml.config_edits handles semantic quality scoring.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/angular")
SKILL_PATH = REPO / "skills" / "dev-skills" / "angular-new-app" / "SKILL.md"


def _grep_count(literal: str) -> int:
    """Return number of lines in SKILL.md that contain `literal` (fixed string)."""
    r = subprocess.run(
        ["grep", "-cF", "--", literal, str(SKILL_PATH)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    # grep -c: rc=0 → matches printed; rc=1 → no matches; >1 → real error.
    if r.returncode in (0, 1):
        return int(r.stdout.strip() or "0")
    raise RuntimeError(f"grep failed (rc={r.returncode}): {r.stderr}")


# ---------------------------------------------------------------------------
# fail_to_pass — these MUST fail at the base commit and pass after the fix.
# ---------------------------------------------------------------------------

def test_skill_description_typo_corrected():
    """Frontmatter description: 'whenver' → 'whenever' (typo fix)."""
    assert _grep_count("whenver") == 0, (
        "Frontmatter description still contains the misspelling 'whenver'."
    )
    assert _grep_count("whenever a user wants") >= 1, (
        "Expected the corrected word 'whenever a user wants' in description."
    )


def test_redundant_persona_intro_consolidated():
    """The standalone short persona line is removed — only the consolidated
    persona paragraph remains."""
    redundant_line = (
        "You are an expert Angular developer and have access to tools to "
        "create new Angular apps."
    )
    assert _grep_count(redundant_line) == 0, (
        "Redundant persona intro line is still present as a standalone "
        "sentence; it should be consolidated into the main persona paragraph."
    )


def test_step2_lists_useful_ng_new_flags():
    """Step 2 documents commonly useful `ng new` flags (--style, --routing,
    --ssr, --prefix, --skip-tests)."""
    for flag in ("--style", "--routing", "--ssr", "--prefix", "--skip-tests"):
        assert _grep_count(flag) >= 1, (
            f"Expected the '{flag}' flag to be documented in step 2."
        )


def test_step4_lists_missing_generators():
    """Step 4 documents the missing generators: guard, interceptor, resolver,
    enum, class — each invoked via `npx ng generate <kind> <name>`."""
    expected = [
        "npx ng generate guard <guard-name>",
        "npx ng generate interceptor <interceptor-name>",
        "npx ng generate resolver <resolver-name>",
        "npx ng generate enum <enum-name>",
        "npx ng generate class <class-name>",
    ]
    for snippet in expected:
        assert _grep_count(snippet) >= 1, (
            f"Expected step 4 to document the generator command "
            f"`{snippet}`."
        )


def test_ai_configuration_capitalization():
    """Capitalization fix: 'ai configuration' → 'AI configuration' in step 2."""
    # The lowercase form should be gone.
    assert _grep_count("Load the contents of that ai configuration") == 0, (
        "Expected 'ai configuration' to be capitalized to 'AI configuration'."
    )
    assert _grep_count("AI configuration") >= 1, (
        "Expected 'AI configuration' (capitalized) somewhere in step 2."
    )


# ---------------------------------------------------------------------------
# pass_to_pass — structural sanity that holds before and after the fix.
# ---------------------------------------------------------------------------

def test_skill_has_yaml_frontmatter():
    """SKILL.md begins with a YAML frontmatter block."""
    r = subprocess.run(
        ["head", "-1", str(SKILL_PATH)],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert r.stdout.strip() == "---", (
        f"Expected SKILL.md to start with '---' (YAML frontmatter), "
        f"got: {r.stdout!r}"
    )
    assert _grep_count("name: angular-new-app") >= 1, (
        "Expected `name: angular-new-app` in frontmatter."
    )


def test_skill_keeps_existing_generators():
    """The already-listed generators (component, service, pipe, directive,
    interface) are still present — the fix only adds, never removes."""
    for snippet in (
        "npx ng generate component <component-name>",
        "npx ng generate service <service-name>",
        "npx ng generate pipe <pipe-name>",
        "npx ng generate directive <directive-name>",
        "npx ng generate interface <interface-name>",
    ):
        assert _grep_count(snippet) >= 1, (
            f"Pre-existing generator command `{snippet}` is missing — "
            "this test should pass at base and after the fix."
        )
