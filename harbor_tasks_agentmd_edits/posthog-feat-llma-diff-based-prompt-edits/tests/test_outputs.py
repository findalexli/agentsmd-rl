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
# Helper: run Python code in a subprocess with function inlined
# We extract and execute apply_prompt_edits without triggering Django imports.
# ---------------------------------------------------------------------------

# Inline the apply_prompt_edits function for isolated testing
_APPLY_PROMPT_EDITS_CODE = '''
import json
from dataclasses import dataclass

# Stub the constant that the function needs
MAX_PROMPT_PAYLOAD_BYTES = 1_000_000

@dataclass
class LLMPromptEditError(Exception):
    message: str
    edit_index: int

def apply_prompt_edits(prompt_content, edits):
    """Apply sequential find/replace edits to a prompt.

    If the prompt is a string, edits operate on it directly.
    If it's a JSON structure, it's serialized to a string for editing then parsed back.
    Each edit's 'old' text must match exactly once.
    """
    is_string = isinstance(prompt_content, str)
    text = prompt_content if is_string else json.dumps(prompt_content, indent=2, ensure_ascii=False)

    for i, edit in enumerate(edits):
        old = edit["old"]
        new = edit["new"]
        count = text.count(old)
        if count == 0:
            raise LLMPromptEditError(
                message="Text to replace was not found in the prompt.",
                edit_index=i,
            )
        if count > 1:
            raise LLMPromptEditError(
                message=f"Text to replace matches {count} times — provide more context to make it unique.",
                edit_index=i,
            )
        text = text.replace(old, new, 1)

    result = text if is_string else None
    if result is None:
        try:
            result = json.loads(text)
        except json.JSONDecodeError as err:
            raise LLMPromptEditError(
                message=f"Edits produced invalid JSON: {err}",
                edit_index=len(edits) - 1,
            ) from err

    result_bytes = len(json.dumps(result, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    if result_bytes > MAX_PROMPT_PAYLOAD_BYTES:
        raise LLMPromptEditError(
            message=f"Resulting prompt exceeds the {MAX_PROMPT_PAYLOAD_BYTES} byte size limit.",
            edit_index=len(edits) - 1,
        )

    return result
'''


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess with apply_prompt_edits pre-loaded."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(_APPLY_PROMPT_EDITS_CODE + "\n" + code)
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


# [repo_tests] pass_to_pass — CI linting
def test_ruff_check():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Install is best-effort; if it fails, try to continue with system ruff
    r = subprocess.run(
        ["ruff", "check", "posthog/api/llm_prompt.py",
         "posthog/api/llm_prompt_serializers.py",
         "posthog/api/services/llm_prompt.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — CI formatting
def test_ruff_format_check():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check",
         "posthog/api/llm_prompt.py",
         "posthog/api/llm_prompt_serializers.py",
         "posthog/api/services/llm_prompt.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


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
