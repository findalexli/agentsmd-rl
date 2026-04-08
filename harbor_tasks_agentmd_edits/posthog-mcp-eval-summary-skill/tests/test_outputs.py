"""
Task: posthog-mcp-eval-summary-skill
Repo: PostHog/posthog @ 69f47d880ee65fd3e9a769a12a7d80997dea555e
PR:   53656

Expose LLM evaluation summary endpoint as an MCP tool, plus write the
exploring-llm-evaluations SKILL.md that teaches agents how to use it.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path("/workspace/posthog")

TOOLS_YAML = REPO / "products/llm_analytics/mcp/tools.yaml"
API_TS = REPO / "services/mcp/src/generated/llm_analytics/api.ts"
HANDLER_TS = REPO / "services/mcp/src/tools/generated/llm_analytics.ts"
TOOL_DEFS_JSON = REPO / "services/mcp/schema/generated-tool-definitions.json"
SKILLS_README = REPO / "products/llm_analytics/skills/README.md"
EVAL_SKILL_MD = REPO / "products/llm_analytics/skills/exploring-llm-evaluations/SKILL.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_tools_yaml() -> dict:
    return yaml.safe_load(TOOLS_YAML.read_text())


def _get_eval_summary_tool() -> dict:
    data = _load_tools_yaml()
    return data["tools"]["llm-analytics-evaluation-summary-create"]


# ---------------------------------------------------------------------------
# Fail-to-pass (code behavior) — tools.yaml + generated code
# ---------------------------------------------------------------------------

def test_eval_summary_tool_enabled():
    """tools.yaml must have llm-analytics-evaluation-summary-create enabled."""
    tool = _get_eval_summary_tool()
    assert tool.get("enabled") is True, \
        f"Tool should be enabled, got: {tool.get('enabled')}"


def test_eval_summary_tool_scopes():
    """The evaluation-summary tool must declare llm_analytics:write scope."""
    tool = _get_eval_summary_tool()
    scopes = tool.get("scopes", [])
    assert "llm_analytics:write" in scopes, \
        f"Missing llm_analytics:write scope, got: {scopes}"


def test_eval_summary_tool_annotations_and_consent():
    """Tool must have correct annotations and requires_ai_consent."""
    tool = _get_eval_summary_tool()
    ann = tool.get("annotations", {})
    assert ann.get("readOnly") is False, "Should not be readOnly"
    assert ann.get("destructive") is False, "Should not be destructive"
    assert ann.get("idempotent") is True, "Should be idempotent"
    assert tool.get("requires_ai_consent") is True, "Must require AI consent"


def test_zod_schema_exported_in_api_ts():
    """Generated api.ts must export the EvaluationSummaryCreateBody Zod schema."""
    content = API_TS.read_text()
    assert "LlmAnalyticsEvaluationSummaryCreateBody" in content, \
        "Missing LlmAnalyticsEvaluationSummaryCreateBody in api.ts"
    assert "evaluation_id" in content, "Schema must include evaluation_id field"
    assert "force_refresh" in content, "Schema must include force_refresh field"
    assert "generation_ids" in content, "Schema must include generation_ids field"
    # Verify the schema has the right filter enum values
    assert "'all'" in content or '"all"' in content, "Schema must include 'all' filter"
    assert "'fail'" in content or '"fail"' in content, "Schema must include 'fail' filter"


def test_tool_handler_registered_in_generated_tools():
    """Generated llm_analytics.ts must register the evaluation-summary handler in GENERATED_TOOLS."""
    content = HANDLER_TS.read_text()
    assert "llm-analytics-evaluation-summary-create" in content, \
        "Handler not registered in generated tools"
    assert "evaluation_summary" in content.lower(), \
        "Handler must reference evaluation_summary endpoint"
    assert "LlmAnalyticsEvaluationSummaryCreateSchema" in content, \
        "Handler must use the Zod schema"


def test_tool_def_json_has_entry():
    """generated-tool-definitions.json must include the evaluation summary tool entry."""
    data = json.loads(TOOL_DEFS_JSON.read_text())
    tool_def = data.get("llm-analytics-evaluation-summary-create")
    assert tool_def is not None, "Tool definition missing from schema JSON"
    scopes = tool_def.get("required_scopes", [])
    assert "llm_analytics:write" in scopes, \
        f"Missing llm_analytics:write scope, got: {scopes}"
    assert tool_def.get("requires_ai_consent") is True, "Must require AI consent"
    ann = tool_def.get("annotations", {})
    assert ann.get("idempotentHint") is True, "Should have idempotentHint: true"


def test_snapshot_json_exists_and_valid():
    """The JSON snapshot for the tool schema must exist and be valid JSON with required fields."""
    snapshot = REPO / "services/mcp/tests/unit/__snapshots__/tool-schemas/common/llm-analytics-evaluation-summary-create.json"
    assert snapshot.exists(), "Snapshot file must exist"
    data = json.loads(snapshot.read_text())
    props = data.get("properties", {})
    assert "evaluation_id" in props, "Snapshot must have evaluation_id property"
    assert "filter" in props, "Snapshot must have filter property"
    assert "force_refresh" in props, "Snapshot must have force_refresh property"
    assert "generation_ids" in props, "Snapshot must have generation_ids property"
    assert "evaluation_id" in data.get("required", []), "evaluation_id must be required"


# ---------------------------------------------------------------------------
# Fail-to-pass (config/documentation) — SKILL.md + README
# ---------------------------------------------------------------------------

def test_skills_readme_lists_evaluations():
    """products/llm_analytics/skills/README.md must list exploring-llm-evaluations."""
    content = SKILLS_README.read_text()
    assert "exploring-llm-evaluations" in content, \
        "skills/README.md must reference the exploring-llm-evaluations skill"
    # Verify description mentions evaluations
    assert "evaluation" in content.lower(), \
        "README should mention evaluations in the skill description"


def test_skill_md_exists_with_frontmatter():
    """exploring-llm-evaluations/SKILL.md must exist with valid frontmatter."""
    assert EVAL_SKILL_MD.exists(), "SKILL.md file must exist"
    content = EVAL_SKILL_MD.read_text()
    assert content.startswith("---"), "SKILL.md must have YAML frontmatter"
    fm_end = content.index("---", 3)
    frontmatter = yaml.safe_load(content[3:fm_end])
    assert frontmatter.get("name") == "exploring-llm-evaluations", \
        f"Frontmatter name wrong: {frontmatter.get('name')}"
    assert "description" in frontmatter, "Frontmatter must have description"
    desc = frontmatter["description"].lower()
    assert "evaluation" in desc, "Description must mention evaluations"


def test_skill_md_documents_summary_tool():
    """SKILL.md must document the evaluation summary tool and its parameters."""
    content = EVAL_SKILL_MD.read_text().lower()
    # Must reference the tool name or its endpoint
    assert "evaluation-summary-create" in content or \
           "evaluation_summary" in content, \
           "SKILL.md must reference the evaluation summary tool"
    # Must document key parameters
    assert "filter" in content, "Must document filter parameter"
    assert "force_refresh" in content or "force refresh" in content, \
        "Must mention force_refresh / cache behavior"


def test_skill_md_covers_both_evaluation_types():
    """SKILL.md must document both hog and llm_judge evaluation types."""
    content = EVAL_SKILL_MD.read_text().lower()
    assert "hog" in content, "Must document Hog (deterministic) evaluation type"
    assert "llm_judge" in content or "llm judge" in content, \
        "Must document LLM judge evaluation type"
    # Both types should be contrasted
    assert "deterministic" in content or "reproducible" in content, \
        "Should describe Hog evaluators as deterministic/reproducible"


def test_skill_md_has_workflow_sections():
    """SKILL.md must contain structured workflow guidance for investigation."""
    content = EVAL_SKILL_MD.read_text().lower()
    # Should have workflow sections for common tasks
    assert "workflow" in content or "step" in content, \
        "SKILL.md should have workflow/step-by-step sections"
    assert "$ai_evaluation" in content, \
        "Must reference the $ai_evaluation event schema"


def test_skill_md_frontmatter_follows_conventions():
    """SKILL.md name must be lowercase kebab-case, description under 1024 chars."""
    assert EVAL_SKILL_MD.exists(), "SKILL.md file must exist"
    content = EVAL_SKILL_MD.read_text()
    fm_end = content.index("---", 3)
    frontmatter = yaml.safe_load(content[3:fm_end])
    name = frontmatter.get("name", "")
    # Name: lowercase kebab-case per writing-skills convention
    assert name == name.lower(), f"Skill name must be lowercase: {name}"
    assert " " not in name, f"Skill name must use kebab-case (no spaces): {name}"
    assert "-" in name or name.isalpha(), f"Skill name should use kebab-case: {name}"
    # Description: under 1024 chars per writing-skills convention
    desc = frontmatter.get("description", "")
    assert len(desc) <= 1024, f"Description too long: {len(desc)} chars (max 1024)"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

def test_existing_clustering_tool_unchanged():
    """Previously enabled clustering-jobs-list tool must remain enabled."""
    data = _load_tools_yaml()
    clustering = data["tools"].get("llm-analytics-clustering-jobs-list", {})
    assert clustering.get("enabled") is True, \
        "Clustering jobs list tool should remain enabled"


def test_existing_skills_remain_in_readme():
    """Previously listed skills must still appear in skills/README.md."""
    content = SKILLS_README.read_text()
    assert "exploring-llm-traces" in content, \
        "exploring-llm-traces skill should still be listed"
    assert "exploring-llm-clusters" in content, \
        "exploring-llm-clusters skill should still be listed"
