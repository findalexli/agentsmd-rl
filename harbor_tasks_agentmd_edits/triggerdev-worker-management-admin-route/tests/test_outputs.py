"""
Task: triggerdev-worker-management-admin-route
Repo: triggerdotdev/trigger.dev @ 37aadfc80bf72b71cfc98cd3fb8a76717aea143e
PR:   2032

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/trigger.dev"
ROUTE_FILE = Path(REPO) / "apps/webapp/app/routes/admin.api.v1.workers.ts"
README_FILE = Path(REPO) / "apps/supervisor/README.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_route():
    return ROUTE_FILE.read_text()


def read_readme():
    return README_FILE.read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript file must exist and contain valid structure."""
    content = read_route()
    # File should have the action export and schema definition
    assert "RequestBodySchema" in content, "Missing RequestBodySchema"
    assert "export async function action" in content, "Missing action export"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — API schema changes
# ---------------------------------------------------------------------------

def test_schema_uses_project_id():
    """Request schema should use 'projectId' instead of 'makeDefaultForProjectId'."""
    content = read_route()
    # Find the schema definition block
    schema_match = re.search(
        r"RequestBodySchema\s*=\s*z\.object\(\{(.*?)\}\)",
        content,
        re.DOTALL,
    )
    assert schema_match, "Could not find RequestBodySchema definition"
    schema_body = schema_match.group(1)

    # Use word-boundary match to avoid matching substring in makeDefaultForProjectId
    assert re.search(r"(?<!\w)projectId\s*:", schema_body), \
        "Schema should have a 'projectId' field"
    assert "makeDefaultForProjectId" not in schema_body, \
        "Schema should not have the old 'makeDefaultForProjectId' field"


def test_schema_has_boolean_flags():
    """Schema should have makeDefaultForProject and removeDefaultFromProject as booleans."""
    content = read_route()
    schema_match = re.search(
        r"RequestBodySchema\s*=\s*z\.object\(\{(.*?)\}\)",
        content,
        re.DOTALL,
    )
    assert schema_match, "Could not find RequestBodySchema definition"
    schema_body = schema_match.group(1)

    # Both should be boolean fields (z.boolean())
    assert re.search(r"makeDefaultForProject\s*:\s*z\.boolean\(\)", schema_body), \
        "Schema should have 'makeDefaultForProject' as z.boolean()"
    assert re.search(r"removeDefaultFromProject\s*:\s*z\.boolean\(\)", schema_body), \
        "Schema should have 'removeDefaultFromProject' as z.boolean()"


def test_remove_default_handling():
    """Route should handle removeDefaultFromProject by clearing the project's default worker group."""
    content = read_route()
    # The action function should check for removeDefaultFromProject
    assert "removeDefaultFromProject" in content, \
        "Route should reference removeDefaultFromProject"
    # Should set defaultWorkerGroupId to null when removing
    assert "defaultWorkerGroupId: null" in content or "defaultWorkerGroupId:null" in content, \
        "Route should set defaultWorkerGroupId to null when removing default"
    # Should validate projectId is required for removal
    assert "projectId is required" in content, \
        "Route should validate that projectId is required"


def test_existing_group_check():
    """Route should check for existing worker groups before creating new ones."""
    content = read_route()
    # Should query for existing worker group by name/queue before creating
    assert "workerInstanceGroup" in content, \
        "Route should query workerInstanceGroup to check for existing groups"
    # Should have different outcomes for existing vs new groups
    assert "worker group already exists" in content, \
        "Route should handle the case where a worker group already exists"


def test_helper_functions():
    """Route should extract helper functions for worker group operations."""
    content = read_route()
    # There should be at least 3 async functions total (the action + extracted helpers)
    async_fns = re.findall(r"async\s+function\s+(\w+)", content)
    assert len(async_fns) >= 3, \
        f"Expected at least 3 async functions (action + helpers), found {len(async_fns)}: {async_fns}"
    # The helper functions should cover: creating groups, setting defaults, removing defaults
    # Check that there are functions beyond just 'action' that handle these operations
    helpers = [fn for fn in async_fns if fn != "action"]
    assert len(helpers) >= 2, \
        f"Expected at least 2 helper functions beyond action, found {len(helpers)}: {helpers}"


def test_outcome_field_in_responses():
    """API responses should include an 'outcome' field describing what happened."""
    content = read_route()
    # The route should return outcome descriptions in JSON responses
    outcomes = re.findall(r'outcome:\s*"([^"]+)"', content)
    assert len(outcomes) >= 3, \
        f"Expected at least 3 distinct outcome messages, found {len(outcomes)}: {outcomes}"
    # Check that key outcomes are present
    outcome_text = " ".join(outcomes).lower()
    assert "created" in outcome_text or "new" in outcome_text, \
        "Should have an outcome for creating a new worker group"
    assert "removed" in outcome_text or "remove" in outcome_text, \
        "Should have an outcome for removing default"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation updates
# ---------------------------------------------------------------------------





