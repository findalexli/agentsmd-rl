"""
Task: posthog-feat-llma-diff-based-prompt-edits
Repo: PostHog/posthog @ 209f5d790aaee15baaf509ee15268edd932f5f23
PR:   53378

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

import yaml

REPO = "/workspace/posthog"

# ---------------------------------------------------------------------------
# Helper: run Python code in a subprocess with Django stubs pre-configured
# so we can exercise apply_prompt_edits without a full Django stack.
# ---------------------------------------------------------------------------

_DJANGO_STUBS = """\
import sys, types, json

for mod in ["django", "django.conf", "django.db", "django.db.models",
            "posthog", "posthog.api", "posthog.api.llm_prompt_serializers",
            "posthog.exceptions_capture", "posthog.models",
            "posthog.models.llm_prompt"]:
    if mod not in sys.modules:
        sys.modules[mod] = types.ModuleType(mod)
sys.modules["django.db"].IntegrityError = type("IntegrityError", (Exception,), {})
sys.modules["django.db"].transaction = types.ModuleType("transaction")
sys.modules["django.db"].transaction.atomic = lambda *a, **k: None
sys.modules["django.db.models"].QuerySet = object
sys.modules["posthog.api.llm_prompt_serializers"].MAX_PROMPT_PAYLOAD_BYTES = 1_000_000
sys.modules["posthog.exceptions_capture"].capture_exception = lambda *a, **k: None
sys.modules["posthog.models"].Team = object
sys.modules["posthog.models"].User = object
sys.modules["posthog.models.llm_prompt"].LLMPrompt = object
sys.modules["posthog.models.llm_prompt"].annotate_llm_prompt_version_history_metadata = lambda x: x

from posthog.api.services.llm_prompt import apply_prompt_edits, LLMPromptEditError
"""


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess with Django stubs pre-configured."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(_DJANGO_STUBS + "\n" + code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    import py_compile
    files = [
        "posthog/api/llm_prompt.py",
        "posthog/api/llm_prompt_serializers.py",
        "posthog/api/services/llm_prompt.py",
    ]
    for f in files:
        path = Path(REPO) / f
        assert path.exists(), f"{f} not found"
        py_compile.compile(str(path), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_apply_edits_single():
    """apply_prompt_edits applies a single find/replace to a string prompt."""
    r = _run_py("""
result = apply_prompt_edits(
    "You are a helpful assistant.",
    [{"old": "helpful assistant", "new": "expert coding assistant"}],
)
assert result == "You are a expert coding assistant.", f"Got: {result!r}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_apply_edits_multiple_sequential():
    """Multiple edits are applied in order."""
    r = _run_py("""
result = apply_prompt_edits(
    "Hello world. Goodbye world.",
    [
        {"old": "Hello world", "new": "Hi there"},
        {"old": "Goodbye world", "new": "See you later"},
    ],
)
assert result == "Hi there. See you later.", f"Got: {result!r}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_apply_edits_not_found_error():
    """apply_prompt_edits raises error when old text is not found."""
    r = _run_py("""
try:
    apply_prompt_edits("Hello world", [{"old": "nonexistent text", "new": "x"}])
    print("FAIL: no exception raised")
except LLMPromptEditError as e:
    assert "not found" in e.message.lower(), f"Unexpected message: {e.message}"
    assert e.edit_index == 0, f"Expected edit_index=0, got {e.edit_index}"
    print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_apply_edits_ambiguous_error():
    """apply_prompt_edits raises error when old text matches multiple times."""
    r = _run_py("""
try:
    apply_prompt_edits("foo bar foo", [{"old": "foo", "new": "baz"}])
    print("FAIL: no exception raised")
except LLMPromptEditError as e:
    assert "2" in e.message, f"Should mention 2 matches: {e.message}"
    assert e.edit_index == 0, f"Expected edit_index=0, got {e.edit_index}"
    print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_apply_edits_json_prompt():
    """apply_prompt_edits works on JSON (dict) prompts."""
    r = _run_py("""
result = apply_prompt_edits(
    {"system": "You are helpful.", "temperature": 0.7},
    [{"old": "You are helpful.", "new": "You are an expert."}],
)
assert isinstance(result, dict), f"Expected dict, got {type(result)}"
assert result["system"] == "You are an expert.", f"Got: {result['system']!r}"
assert result["temperature"] == 0.7, f"Temperature changed: {result['temperature']}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural checks for new code
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_serializer_has_edits_field():
    """LLMPromptPublishSerializer defines an 'edits' field."""
    import ast
    src = (Path(REPO) / "posthog/api/llm_prompt_serializers.py").read_text()
    tree = ast.parse(src)
    found_class = False
    has_edits = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "LLMPromptPublishSerializer":
            found_class = True
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == "edits":
                            has_edits = True
    assert found_class, "LLMPromptPublishSerializer class not found"
    assert has_edits, "LLMPromptPublishSerializer must define an 'edits' field"


# ---------------------------------------------------------------------------
# Config/doc update checks (agentmd-edit)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_documents_edits():
    """SKILL.md must document the incremental edits feature for prompt-update."""
    skill_md = Path(REPO) / "products/llm_analytics/skills/skills-store/SKILL.md"
    assert skill_md.exists(), "SKILL.md not found"
    content = skill_md.read_text()
    content_lower = content.lower()
    assert "edits" in content_lower, "SKILL.md should document the 'edits' parameter"
    assert "old" in content_lower and "new" in content_lower, \
        "SKILL.md should explain the old/new edit operation fields"
    assert "prompt-update" in content, "SKILL.md should show prompt-update usage with edits"
    assert "prompt" in content_lower and ("exclusive" in content_lower or "not both" in content_lower or "one of" in content_lower), \
        "SKILL.md should mention that prompt and edits are mutually exclusive"


# [pr_diff] fail_to_pass
def test_mcp_yaml_includes_edits():
    """prompts.yaml MCP tool definition must include the edits parameter."""
    prompts_yaml = Path(REPO) / "products/llm_analytics/mcp/prompts.yaml"
    assert prompts_yaml.exists(), "prompts.yaml not found"
    content = prompts_yaml.read_text()
    data = yaml.safe_load(content)
    tools = data.get("tools", {})
    prompt_update = tools.get("prompt-update", {})
    description = prompt_update.get("description", "")
    assert "edits" in description.lower(), \
        "prompt-update description should mention edits"
    include_params = prompt_update.get("include_params", [])
    assert "edits" in include_params, \
        f"prompt-update include_params should list 'edits', got: {include_params}"


# [agent_config] fail_to_pass — AGENTS.md:85 @ 209f5d790aaee15baaf509ee15268edd932f5f23
def test_serializer_fields_have_help_text():
    """New serializer fields must have help_text (per AGENTS.md line 85)."""
    import ast
    src = (Path(REPO) / "posthog/api/llm_prompt_serializers.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "LLMPromptEditOperationSerializer":
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id in ("old", "new"):
                            if isinstance(item.value, ast.Call):
                                kwarg_names = [kw.arg for kw in item.value.keywords]
                                assert "help_text" in kwarg_names, \
                                    f"Field '{target.id}' in LLMPromptEditOperationSerializer missing help_text"
            return
    assert False, "LLMPromptEditOperationSerializer class not found in serializers"
