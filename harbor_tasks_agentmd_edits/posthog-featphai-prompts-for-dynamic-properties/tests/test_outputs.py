"""
Task: posthog-featphai-prompts-for-dynamic-properties
Repo: PostHog/posthog @ 14b7a8edebb1b574414ac9866a417fbe7c8170c0
PR:   52913

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/posthog"


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python snippet in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified Python files must parse without errors."""
    for f in [
        "ee/hogai/chat_agent/taxonomy/prompts.py",
        "ee/hogai/tools/read_taxonomy/core.py",
        "posthog/hogql_queries/ai/event_taxonomy_query_runner.py",
    ]:
        r = _run_python(f"import ast; ast.parse(open('{f}').read()); print('OK')")
        assert r.returncode == 0, f"{f} syntax error: {r.stderr}"
        assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI tooling verification
# ---------------------------------------------------------------------------

def test_repo_ruff_check():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    # Install ruff if not present
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Run ruff check on modified files
    r = subprocess.run(
        ["ruff", "check", "ee/hogai/chat_agent/taxonomy/prompts.py",
         "ee/hogai/tools/read_taxonomy/core.py",
         "posthog/hogql_queries/ai/event_taxonomy_query_runner.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    # Install ruff if not present
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Run ruff format check on modified files
    r = subprocess.run(
        ["ruff", "format", "--check", "ee/hogai/chat_agent/taxonomy/prompts.py",
         "ee/hogai/tools/read_taxonomy/core.py",
         "posthog/hogql_queries/ai/event_taxonomy_query_runner.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_syntax_modified_files():
    """Python syntax validation via AST on modified files (pass_to_pass)."""
    files = [
        "ee/hogai/chat_agent/taxonomy/prompts.py",
        "ee/hogai/tools/read_taxonomy/core.py",
        "posthog/hogql_queries/ai/event_taxonomy_query_runner.py",
    ]
    for f in files:
        r = _run_python(f"import ast; ast.parse(open('{f}').read()); print('OK')")
        assert r.returncode == 0, f"{f} syntax error: {r.stderr}"
        assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_prompt_documents_dynamic_properties():
    """PROPERTY_TYPES_PROMPT must contain a <dynamic_person_properties> section
    documenting all 8 dynamic property patterns."""
    r = _run_python(r"""
import ast, json, sys

def extract_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr == 'strip' and isinstance(node.func.value, ast.Constant):
            return node.func.value.value.strip()
    return None

with open('ee/hogai/chat_agent/taxonomy/prompts.py') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == 'PROPERTY_TYPES_PROMPT':
                val = extract_str(node.value)
                print(json.dumps({"found": True, "value": val}))
                sys.exit(0)

print(json.dumps({"found": False, "value": None}))
""")
    assert r.returncode == 0, f"AST extraction failed: {r.stderr}"
    data = json.loads(r.stdout.strip().split("\n")[-1])
    assert data["found"], "PROPERTY_TYPES_PROMPT not found in prompts.py"

    value = data["value"]
    if value is None:
        # Fallback if string is built dynamically (f-string, concat, etc.)
        value = (Path(REPO) / "ee/hogai/chat_agent/taxonomy/prompts.py").read_text()

    assert "<dynamic_person_properties>" in value, "Missing <dynamic_person_properties> section"
    assert "</dynamic_person_properties>" in value, "Missing closing tag"
    for p in [
        "$survey_dismissed/", "$survey_responded/",
        "$feature_enrollment/", "$feature/",
        "$feature_interaction/",
        "$product_tour_dismissed/", "$product_tour_shown/", "$product_tour_completed/",
    ]:
        assert p in value, f"PROPERTY_TYPES_PROMPT missing pattern '{p}'"


def test_taxonomy_tool_person_hint():
    """core.py must define DYNAMIC_PERSON_PROPERTIES_HINT with person-specific
    patterns and dispatch it conditionally for person entity queries."""
    r = _run_python(r"""
import ast, json

def extract_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr == 'strip' and isinstance(node.func.value, ast.Constant):
            return node.func.value.value.strip()
    return None

with open('ee/hogai/tools/read_taxonomy/core.py') as f:
    source = f.read()
    tree = ast.parse(source)

hint_value = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == 'DYNAMIC_PERSON_PROPERTIES_HINT':
                hint_value = extract_str(node.value)
                break

func_source = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'execute_taxonomy_query':
        func_source = ast.get_source_segment(source, node)
        break

print(json.dumps({"hint_value": hint_value, "func_source": func_source}))
""")
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip().split("\n")[-1])

    hint = data["hint_value"]
    assert hint is not None, "DYNAMIC_PERSON_PROPERTIES_HINT not defined in core.py"
    for p in ["$survey_dismissed", "$feature_enrollment", "$product_tour_dismissed"]:
        assert p in hint, f"Person hint missing '{p}'"

    func = data["func_source"]
    assert func is not None, "execute_taxonomy_query function not found"
    assert "DYNAMIC_PERSON_PROPERTIES_HINT" in func, \
        "execute_taxonomy_query must reference DYNAMIC_PERSON_PROPERTIES_HINT"
    assert 'entity == "person"' in func or "entity == 'person'" in func, \
        "execute_taxonomy_query must check entity == 'person' for conditional hint"


def test_taxonomy_tool_event_hint():
    """core.py must define DYNAMIC_EVENT_PROPERTIES_HINT with the $feature/
    pattern and dispatch it for event/action property queries."""
    r = _run_python(r"""
import ast, json

def extract_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr == 'strip' and isinstance(node.func.value, ast.Constant):
            return node.func.value.value.strip()
    return None

with open('ee/hogai/tools/read_taxonomy/core.py') as f:
    source = f.read()
    tree = ast.parse(source)

hint_value = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == 'DYNAMIC_EVENT_PROPERTIES_HINT':
                hint_value = extract_str(node.value)
                break

func_source = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'execute_taxonomy_query':
        func_source = ast.get_source_segment(source, node)
        break

print(json.dumps({"hint_value": hint_value, "func_source": func_source}))
""")
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip().split("\n")[-1])

    hint = data["hint_value"]
    assert hint is not None, "DYNAMIC_EVENT_PROPERTIES_HINT not defined in core.py"
    assert "$feature/" in hint, "Event hint missing '$feature/' pattern"

    func = data["func_source"]
    assert func is not None, "execute_taxonomy_query function not found"
    assert "DYNAMIC_EVENT_PROPERTIES_HINT" in func, \
        "execute_taxonomy_query must reference DYNAMIC_EVENT_PROPERTIES_HINT"


def test_omit_filter_expanded():
    """The event taxonomy omit filter must include new dynamic property patterns."""
    r = _run_python(r"""
import ast, json

with open('posthog/hogql_queries/ai/event_taxonomy_query_runner.py') as f:
    source = f.read()
    tree = ast.parse(source)

omit_strings = []
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_get_omit_filter':
        for child in ast.walk(node):
            if isinstance(child, ast.List):
                for elt in child.elts:
                    try:
                        omit_strings.append(ast.literal_eval(elt))
                    except Exception:
                        pass
        break

print(json.dumps({"omit_strings": omit_strings}))
""")
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip().split("\n")[-1])
    assert len(data["omit_strings"]) > 0, "omit_list empty or _get_omit_filter not found"

    omit_joined = " ".join(data["omit_strings"])
    assert "feature_enrollment" in omit_joined, "Omit filter missing feature_enrollment"
    assert "feature_interaction" in omit_joined, "Omit filter missing feature_interaction"
    assert "product_tour" in omit_joined, "Omit filter missing product_tour"
    assert "survey_dismiss" in omit_joined, "Omit filter should use survey_dismiss prefix"


# ---------------------------------------------------------------------------
# Config-edit (agent_config) - SKILL.md and reference doc
# ---------------------------------------------------------------------------

def test_skill_md_references_dynamic_properties():
    """SKILL.md must reference the dynamic properties documentation."""
    content = (Path(REPO) / "products/posthog_ai/skills/query-examples/SKILL.md").read_text()
    assert "taxonomy-dynamic-properties" in content or "dynamic-properties" in content, \
        "SKILL.md should link to the dynamic properties reference file"


def test_dynamic_properties_reference_doc():
    """A reference doc must exist documenting all dynamic property patterns."""
    ref_dir = Path(REPO) / "products/posthog_ai/skills/query-examples/references"
    candidates = list(ref_dir.glob("*dynamic*propert*")) + list(ref_dir.glob("*taxonomy*dynamic*"))
    assert len(candidates) > 0, "Dynamic properties reference doc not found"

    content = candidates[0].read_text()
    for pattern in ["$survey_dismissed", "$feature_enrollment", "$product_tour_dismissed"]:
        assert pattern in content, f"Reference doc missing '{pattern}'"
    assert "$feature/" in content, "Reference doc missing '$feature/{flag_key}'"
    assert "person" in content.lower(), "Reference doc should mention person properties"
    assert "event" in content.lower(), "Reference doc should mention event properties"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - anti-stub
# ---------------------------------------------------------------------------

def test_not_stub():
    """execute_taxonomy_query must have real match/case logic."""
    r = _run_python(r"""
import ast, json

with open('ee/hogai/tools/read_taxonomy/core.py') as f:
    tree = ast.parse(f.read())

result = {"found": False, "body_len": 0}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'execute_taxonomy_query':
        result = {"found": True, "body_len": len(node.body)}
        break

print(json.dumps(result))
""")
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip().split("\n")[-1])
    assert data["found"], "execute_taxonomy_query not found"
    assert data["body_len"] >= 2, "execute_taxonomy_query should have real logic"
