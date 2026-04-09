"""
Task: posthog-llm-traces-list-skill-docs
Repo: PostHog/posthog @ bfcaca7712c5a0c3b4b24d2d3f76e79fefc62d87
PR:   53160

This PR adds a new LLM traces list query example, converts the single-trace
query from static markdown to a Jinja2 template using render_hogql_example(),
and enhances the exploring-llm-traces SKILL.md with schema discovery guidance
and richer filter examples.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/posthog"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python script in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


def test_skill_frontmatter_valid():
    """Both SKILL.md files have valid YAML frontmatter."""
    r = _run_py("""
import yaml
from pathlib import Path

skill_files = [
    "products/llm_analytics/skills/exploring-llm-traces/SKILL.md",
    "products/posthog_ai/skills/query-examples/SKILL.md",
]
for sf in skill_files:
    content = (Path(".") / sf).read_text()
    assert content.startswith("---"), f"{sf} must start with YAML frontmatter"
    end = content.index("---", 3)
    frontmatter = content[3:end].strip()
    data = yaml.safe_load(frontmatter)
    assert "name" in data, f"{sf} frontmatter must have 'name' field"
    assert "description" in data, f"{sf} frontmatter must have 'description' field"
    assert isinstance(data["description"], str), f"{sf} description must be a string"
    print(f"PASS: {sf}")
""")
    assert r.returncode == 0, f"Frontmatter validation failed:\n{r.stderr}"
    assert "PASS:" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Jinja2 template conversion
# ---------------------------------------------------------------------------


def test_jinja2_template_valid():
    """example-llm-trace.md.j2 exists and is valid Jinja2 using render_hogql_example()."""
    r = _run_py("""
import jinja2
from pathlib import Path

j2_path = Path("products/posthog_ai/skills/query-examples/references/example-llm-trace.md.j2")
assert j2_path.exists(), "example-llm-trace.md.j2 must exist"

content = j2_path.read_text()
assert len(content) > 50, "Template must have meaningful content"

# Parse as Jinja2 to verify syntax
env = jinja2.Environment()
parsed = env.parse(content)

# Verify it uses the render_hogql_example helper
assert "render_hogql_example" in content, (
    "Template must call render_hogql_example()"
)

# Verify it passes a TraceQuery kind
assert "TraceQuery" in content, (
    "Template must use TraceQuery kind in render_hogql_example call"
)

# Verify prose content is preserved (not just the template call)
assert "LLM Trace query" in content, "Template must retain the title"
assert "$ai_input" in content, "Template must retain the warning about large properties"

print("PASS")
""")
    assert r.returncode == 0, f"Jinja2 template validation failed:\n{r.stderr}"
    assert "PASS" in r.stdout


def test_static_trace_replaced_by_template():
    """Old static example-llm-trace.md must be replaced by the .j2 template."""
    r = _run_py("""
from pathlib import Path

refs = Path("products/posthog_ai/skills/query-examples/references")

old_md = refs / "example-llm-trace.md"
new_j2 = refs / "example-llm-trace.md.j2"

assert not old_md.exists(), (
    "Static example-llm-trace.md must be removed (replaced by .j2 template)"
)
assert new_j2.exists(), (
    "example-llm-trace.md.j2 must exist as the replacement"
)

print("PASS")
""")
    assert r.returncode == 0, f"Template replacement check failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — new traces list reference document
# ---------------------------------------------------------------------------


def test_traces_list_reference_exists():
    """example-llm-traces-list.md must exist with two-phase SQL query pattern."""
    r = _run_py("""
import re
from pathlib import Path

doc = Path("products/posthog_ai/skills/query-examples/references/example-llm-traces-list.md")
assert doc.exists(), "example-llm-traces-list.md must exist"

content = doc.read_text()
assert len(content) > 500, "Document must be substantial (has two SQL phases)"

# Must describe the two-phase approach
assert "Phase 1" in content, "Must have Phase 1 section"
assert "Phase 2" in content, "Must have Phase 2 section"

# Phase 1 must find trace IDs
assert "$ai_trace_id" in content, "Must reference $ai_trace_id property"
assert "GROUP BY" in content, "SQL must use GROUP BY for aggregation"

# Phase 2 must aggregate metrics
assert "total_latency" in content, "Phase 2 must compute total_latency"
assert "input_tokens" in content, "Phase 2 must aggregate input_tokens"
assert "output_tokens" in content, "Phase 2 must aggregate output_tokens"
assert "error_count" in content, "Phase 2 must include error_count"

# Must omit large content fields (key design decision)
assert "$ai_input" in content, "Must mention omitted fields"
assert "omit" in content.lower(), "Must explain that large fields are omitted"

# Validate SQL blocks are structurally sound
sql_blocks = re.findall(r'```sql\\n(.*?)```', content, re.DOTALL)
assert len(sql_blocks) >= 2, "Must have at least 2 SQL code blocks (one per phase)"
for i, sql in enumerate(sql_blocks):
    assert "SELECT" in sql, f"SQL block {i+1} must have SELECT"
    assert "FROM" in sql.upper(), f"SQL block {i+1} must have FROM"

# Cross-reference to single trace query must exist
assert "example-llm-trace" in content, "Must cross-reference single trace query"

print("PASS")
""")
    assert r.returncode == 0, f"Traces list reference check failed:\n{r.stderr}"
    assert "PASS" in r.stdout


def test_traces_list_has_cost_columns():
    """Traces list Phase 2 query must aggregate input/output/total cost."""
    r = _run_py("""
import re
from pathlib import Path

doc = Path("products/posthog_ai/skills/query-examples/references/example-llm-traces-list.md")
content = doc.read_text()

# Isolate Phase 2 section
phases = content.split("Phase 2")
assert len(phases) >= 2, "Must have Phase 2 section"
phase2 = phases[1]

# Must include cost columns in the SQL
assert "input_cost" in phase2, "Phase 2 must include input_cost column"
assert "output_cost" in phase2, "Phase 2 must include output_cost column"
assert "total_cost" in phase2, "Phase 2 must include total_cost column"

# Must reference the underlying HogQL property
assert "$ai_total_cost_usd" in phase2, "Must use $ai_total_cost_usd property"

# Verify cost columns use sumIf aggregation and rounding
sql_match = re.search(r'```sql\\n.*?```', phase2, re.DOTALL)
assert sql_match, "Phase 2 must contain a SQL block"
sql = sql_match.group()
assert "sumIf" in sql, "Cost columns must use sumIf aggregation"
assert "round" in sql, "Cost values must be rounded for readability"

print("PASS")
""")
    assert r.returncode == 0, f"Cost columns check failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — SKILL.md config updates
# ---------------------------------------------------------------------------


def test_exploring_skill_schema_discovery():
    """exploring-llm-traces SKILL.md must guide schema discovery workflow."""
    r = _run_py("""
from pathlib import Path

skill = Path("products/llm_analytics/skills/exploring-llm-traces/SKILL.md")
content = skill.read_text()

# Must have schema discovery section
assert "Discovering the schema" in content, (
    "SKILL.md must have a 'Discovering the schema' section"
)

# Must instruct calling read-data-schema before filtering
assert "read-data-schema" in content, (
    "Must reference read-data-schema tool"
)

# Must describe the 3-step discovery workflow
assert "event_properties" in content, (
    "Must reference event_properties kind for schema discovery"
)
assert "event_property_values" in content, (
    "Must reference event_property_values kind for value discovery"
)

# Must warn about not assuming property names from training data
lower = content.lower()
assert "never assume" in lower or "cannot be guessed" in lower, (
    "Must warn against assuming property names"
)

# Verify the discovery steps are ordered (step 1 before 2 before 3)
step1_pos = content.find("Confirm AI events")
step2_pos = content.find("Find filterable properties")
step3_pos = content.find("Get actual values")
assert step1_pos > 0, "Must have step 1: Confirm AI events"
assert step2_pos > step1_pos, "Step 2 must come after step 1"
assert step3_pos > step2_pos, "Step 3 must come after step 2"

print("PASS")
""")
    assert r.returncode == 0, f"Schema discovery check failed:\n{r.stderr}"
    assert "PASS" in r.stdout


def test_exploring_skill_filter_examples():
    """SKILL.md must include AND-ed filter and person property filter examples."""
    r = _run_py("""
from pathlib import Path

skill = Path("products/llm_analytics/skills/exploring-llm-traces/SKILL.md")
content = skill.read_text()

# Must explain AND-ed filters
assert "AND-ed" in content, "Must explain that multiple filters are AND-ed together"

# AND-ed filter example must reference specific properties
assert "$ai_provider" in content, "AND-ed filter example must include $ai_provider"
assert "$ai_is_error" in content, "AND-ed filter example must include $ai_is_error"

# Person property filtering with icontains operator
assert '"type": "person"' in content or "'type': 'person'" in content, (
    "Must include a person property filter example"
)
assert "icontains" in content, "Person filter example must show icontains operator"

# Filter examples must contain a "properties" array structure
assert '"properties"' in content, "Filter examples must show properties array"

print("PASS")
""")
    assert r.returncode == 0, f"Filter examples check failed:\n{r.stderr}"
    assert "PASS" in r.stdout


def test_exploring_skill_cross_references():
    """SKILL.md must cross-reference the query-examples skill documents."""
    r = _run_py("""
from pathlib import Path

skill = Path("products/llm_analytics/skills/exploring-llm-traces/SKILL.md")
content = skill.read_text()

# Must reference both example documents
assert "example-llm-trace.md" in content, (
    "Must reference single trace example document"
)
assert "example-llm-traces-list.md" in content, (
    "Must reference traces list example document"
)
assert "query-examples" in content, (
    "Must reference the query-examples skill"
)

# Verify the cross-referenced files actually exist in the repo
refs_dir = Path("products/posthog_ai/skills/query-examples/references")
assert (refs_dir / "example-llm-trace.md.j2").exists(), (
    "Cross-referenced example-llm-trace must exist (as .j2 template)"
)
assert (refs_dir / "example-llm-traces-list.md").exists(), (
    "Cross-referenced example-llm-traces-list must exist"
)

print("PASS")
""")
    assert r.returncode == 0, f"Cross-references check failed:\n{r.stderr}"
    assert "PASS" in r.stdout


def test_query_examples_links_traces_list():
    """query-examples SKILL.md must link to the new traces list reference."""
    r = _run_py("""
from pathlib import Path

skill = Path("products/posthog_ai/skills/query-examples/SKILL.md")
content = skill.read_text()

# Must link to the new reference
assert "example-llm-traces-list.md" in content, (
    "query-examples SKILL.md must link to example-llm-traces-list.md"
)

# Link text must describe the content
assert "two-phase" in content.lower() or "traces list" in content.lower(), (
    "Link text must describe the traces list query"
)

# The linked file must actually exist
ref = Path("products/posthog_ai/skills/query-examples/references/example-llm-traces-list.md")
assert ref.exists(), "Referenced file must exist"

# The link must be a relative markdown link in a list item
found_link = False
for line in content.split("\\n"):
    if "example-llm-traces-list.md" in line:
        assert "](." in line, "Link must be a relative markdown link"
        found_link = True
        break
assert found_link, "Must find the link in the document"

print("PASS")
""")
    assert r.returncode == 0, f"Query examples links check failed:\n{r.stderr}"
    assert "PASS" in r.stdout
