"""
Task: posthog-featphai-prompts-for-dynamic-properties
Repo: PostHog/posthog @ 14b7a8edebb1b574414ac9866a417fbe7c8170c0
PR:   52913

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
from pathlib import Path

REPO = "/workspace/posthog"

# The 8 dynamic property patterns that the PR documents
DYNAMIC_PERSON_PATTERNS = [
    "$survey_dismissed/",
    "$survey_responded/",
    "$feature_enrollment/",
    "$feature_interaction/",
    "$product_tour_dismissed/",
    "$product_tour_shown/",
    "$product_tour_completed/",
]
DYNAMIC_EVENT_PATTERNS = [
    "$feature/",
]
ALL_DYNAMIC_PATTERNS = DYNAMIC_PERSON_PATTERNS + DYNAMIC_EVENT_PATTERNS


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    files = [
        "ee/hogai/chat_agent/taxonomy/prompts.py",
        "ee/hogai/tools/read_taxonomy/core.py",
        "posthog/hogql_queries/ai/event_taxonomy_query_runner.py",
    ]
    for f in files:
        src = (Path(REPO) / f).read_text()
        compile(src, f, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_prompt_documents_dynamic_properties():
    """PROPERTY_TYPES_PROMPT must contain a dynamic_person_properties section
    documenting all 8 dynamic property patterns."""
    src = (Path(REPO) / "ee/hogai/chat_agent/taxonomy/prompts.py").read_text()

    # Must have the section tags
    assert "<dynamic_person_properties>" in src, \
        "prompts.py should contain <dynamic_person_properties> section"
    assert "</dynamic_person_properties>" in src, \
        "prompts.py should contain closing </dynamic_person_properties> tag"

    # Must document all dynamic property patterns
    for pattern in ALL_DYNAMIC_PATTERNS:
        assert pattern in src, \
            f"prompts.py should document the dynamic property pattern '{pattern}'"


# [pr_diff] fail_to_pass
def test_taxonomy_tool_person_hint():
    """read_taxonomy core.py must define a person properties hint constant
    and append it when querying person entity properties."""
    src = (Path(REPO) / "ee/hogai/tools/read_taxonomy/core.py").read_text()

    # Must have the hint constant with key patterns
    assert "DYNAMIC_PERSON_PROPERTIES_HINT" in src, \
        "core.py should define DYNAMIC_PERSON_PROPERTIES_HINT"
    for pattern in DYNAMIC_PERSON_PATTERNS:
        assert pattern in src, \
            f"core.py should include '{pattern}' in person hint"

    # Must conditionally append hint for person entity queries
    assert 'entity == "person"' in src or "entity == 'person'" in src, \
        "core.py should check entity == 'person' to conditionally append hint"


# [pr_diff] fail_to_pass

    # Must have the event hint constant
    assert "DYNAMIC_EVENT_PROPERTIES_HINT" in src, \
        "core.py should define DYNAMIC_EVENT_PROPERTIES_HINT"
    assert "$feature/" in src, \
        "core.py event hint should document $feature/{flag_key} pattern"

    # The function should append event hint to event property results
    # Check that ReadEventProperties case includes the hint
    assert re.search(
        r"ReadEventProperties.*DYNAMIC_EVENT_PROPERTIES_HINT",
        src, re.DOTALL
    ), "core.py should append DYNAMIC_EVENT_PROPERTIES_HINT for event property queries"


# [pr_diff] fail_to_pass

    # These patterns must be in the omit list
    required_patterns = [
        "feature_enrollment",
        "feature_interaction",
        "product_tour",
    ]
    for pattern in required_patterns:
        assert pattern in src, \
            f"Omit filter should include '{pattern}' to exclude dynamic properties"

    # The old exact-match patterns should be broadened to prefix matches
    # survey_dismissed -> survey_dismiss (prefix to catch both survey_dismissed/id and survey_dismissed)
    assert "survey_dismiss" in src, \
        "Omit filter should match survey dismiss patterns"


# ---------------------------------------------------------------------------
# Config-edit (agent_config) — SKILL.md and reference doc updates
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass

    # Must link to the dynamic properties reference
    assert "dynamic" in content.lower() and "propert" in content.lower(), \
        "SKILL.md should reference dynamic properties documentation"

    # Must mention key concepts so the AI agent knows these exist
    assert "taxonomy-dynamic-properties" in content or "dynamic-properties" in content, \
        "SKILL.md should link to the dynamic properties reference file"


# [agent_config] fail_to_pass
def test_dynamic_properties_reference_doc():
    """A reference doc must exist documenting all dynamic property patterns
    with their types and descriptions."""
    # Find the reference doc — could be .md or .md.j2
    ref_dir = Path(REPO) / "products/posthog_ai/skills/query-examples/references"
    candidates = list(ref_dir.glob("*dynamic*propert*")) + list(ref_dir.glob("*taxonomy*dynamic*"))
    assert len(candidates) > 0, \
        "A reference doc for dynamic properties should exist in the query-examples/references/ directory"

    content = candidates[0].read_text()

    # Must document person property patterns
    for pattern in ["$survey_dismissed", "$feature_enrollment", "$product_tour_dismissed"]:
        assert pattern in content, \
            f"Dynamic properties reference doc should document '{pattern}'"

    # Must document event property patterns
    assert "$feature/" in content, \
        "Dynamic properties reference doc should document '$feature/{flag_key}'"

    # Must distinguish person vs event properties
    assert "person" in content.lower(), \
        "Reference doc should mention person properties"
    assert "event" in content.lower(), \
        "Reference doc should mention event properties"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """execute_taxonomy_query must have real match/case logic, not just pass/return."""
    src = (Path(REPO) / "ee/hogai/tools/read_taxonomy/core.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "execute_taxonomy_query":
            # Should have meaningful body (match statement with cases)
            body_types = [type(s).__name__ for s in node.body]
            assert len(node.body) >= 2, \
                "execute_taxonomy_query should have real logic, not just a stub"
            break
    else:
        raise AssertionError("execute_taxonomy_query function not found in core.py")
