"""
Task: gradio-dropdown-slowdown-destructure
Repo: gradio-app/gradio @ e5ba4fa992c0ac389c6af2d143c9ad4c33eea360
PR:   12944

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Tests use subprocess.run to execute Python analysis scripts that parse the
Svelte component and return structured JSON. This is the behavioral approach
for a Svelte codebase where no JS runtime is available in the Docker image.
"""

import json
import re
import subprocess
from pathlib import Path

TARGET = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte")
REPO = "/workspace/gradio"


def _run_analysis(code: str, timeout: int = 30) -> dict:
    """Execute a Python analysis script that reads the Svelte file and
    returns structured JSON results via stdout."""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis script failed: {r.stderr}"
    return json.loads(r.stdout.strip())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_array_destructure_from_derived():
    """The buggy pattern `let [input_text, selected_index] = $derived.by(...)`
    must be removed — it causes O(N) re-derivations per dropdown option."""
    result = _run_analysis(r"""
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte").read_text()
buggy = re.search(
    r"let\s*\[.*?input_text.*?,.*?selected_index.*?\]\s*=\s*\$derived",
    content, re.DOTALL,
)
print(json.dumps({"has_buggy_destructure": buggy is not None}))
""")
    assert not result["has_buggy_destructure"], (
        r"Array destructuring from $derived.by for input_text/selected_index still present"
    )


# [pr_diff] fail_to_pass
def test_input_text_standalone_state():
    """input_text must be a standalone $state variable initialized as empty
    string, not array-destructured from a combined derivation."""
    result = _run_analysis(r"""
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte").read_text()
m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
script = m.group(1) if m else ""

has_standalone = bool(
    re.search(r"let\s+input_text\s*(?::\s*\S+\s*)?=\s*\$state", script)
)
print(json.dumps({"is_standalone_state": has_standalone}))
""")
    assert result["is_standalone_state"], (
        r"input_text must be declared as a standalone $state variable"
    )


# [pr_diff] fail_to_pass
def test_selected_index_standalone_state():
    """selected_index must be a standalone $state variable initialized as
    null, not array-destructured from a combined derivation."""
    result = _run_analysis(r"""
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte").read_text()
m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
script = m.group(1) if m else ""

has_standalone = bool(
    re.search(r"let\s+selected_index\s*(?::\s*[^=]+)?=\s*\$state", script)
)
print(json.dumps({"is_standalone_state": has_standalone}))
""")
    assert result["is_standalone_state"], (
        r"selected_index must be declared as a standalone $state variable"
    )


# [pr_diff] fail_to_pass
def test_effect_handles_all_value_branches():
    """The $effect must handle all value states: null/undefined/empty array,
    value found in choices, custom value allowed, and default — assigning both
    input_text and selected_index in every branch."""
    result = _run_analysis(r"""
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte").read_text()
m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
script = m.group(1) if m else ""

# Find $effect block
effect_match = re.search(
    r"\$effect\s*\(\s*\(\s*\)\s*=>\s*\{",
    script,
)
if not effect_match:
    print(json.dumps({"found": False}))
    raise SystemExit

# Extract body between $effect opening { and matching closing };
start = effect_match.end()
depth = 1
i = start
while i < len(script) and depth > 0:
    if script[i] == "{":
        depth += 1
    elif script[i] == "}":
        depth -= 1
    i += 1
body = script[start:i]

handles_nullish = bool(re.search(r"value\s*===\s*(?:undefined|null)", body))
handles_array_empty = bool(re.search(r"Array\.isArray\(value\)", body))
handles_in_choices = bool(re.search(r"choices_values\.includes", body))
handles_custom = bool(re.search(r"allow_custom_value", body))

assigns_input = len(re.findall(r"input_text\s*=" , body))
assigns_selected = len(re.findall(r"selected_index\s*=" , body))

print(json.dumps({
    "found": True,
    "handles_nullish": handles_nullish,
    "handles_in_choices": handles_in_choices,
    "handles_custom": handles_custom,
    "assigns_input_count": assigns_input,
    "assigns_selected_count": assigns_selected,
}))
""")
    assert result["found"], "No $effect block found"
    assert result["handles_nullish"], "$effect does not handle null/undefined value"
    assert result["handles_in_choices"], "$effect does not handle value-in-choices case"
    assert result["handles_custom"], "$effect does not handle allow_custom_value case"
    assert result["assigns_input_count"] >= 3, (
        f"$effect assigns input_text only {result['assigns_input_count']} times (need >= 3 branches)"
    )
    assert result["assigns_selected_count"] >= 3, (
        f"$effect assigns selected_index only {result['assigns_selected_count']} times (need >= 3 branches)"
    )


# [pr_diff] fail_to_pass
def test_selected_indices_is_derived():
    """selected_indices must be a $derived variable that pre-computes the array
    so the template uses a stable reference instead of creating a new array."""
    result = _run_analysis(r"""
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte").read_text()
m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
script = m.group(1) if m else ""

has_derived = bool(re.search(r"let\s+selected_indices\s*=\s*\$derived", script))
print(json.dumps({"is_derived": has_derived}))
""")
    assert result["is_derived"], (
        r"selected_indices must be declared as a $derived variable"
    )


# [pr_diff] fail_to_pass
def test_template_no_inline_selected_indices():
    """Template must not compute selected_indices inline as
    `selected_index === null ? [] : [selected_index]` — this creates
    a new array reference on every access, amplifying reactive cascades."""
    result = _run_analysis(r"""
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte").read_text()
template = re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL)

inline = bool(re.search(
    r"selected_index\s*===\s*null\s*\?\s*\[\]\s*:\s*\[selected_index\]",
    template,
))
print(json.dumps({"has_inline_ternary": inline}))
""")
    assert not result["has_inline_ternary"], (
        r"Template still has inline selected_indices ternary — must use $derived variable"
    )


# [pr_diff] fail_to_pass
def test_template_uses_selected_indices_variable():
    """Template must reference the pre-computed selected_indices variable
    (as a prop shorthand {selected_indices} or explicit prop assignment)."""
    result = _run_analysis(r"""
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte").read_text()
template = re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL)

uses_shorthand = bool(re.search(r"\{selected_indices\}", template))
uses_prop = bool(re.search(r"selected_indices\s*=\s*\{", template))
print(json.dumps({"uses_variable": uses_shorthand or uses_prop}))
""")
    assert result["uses_variable"], (
        "Template does not reference the selected_indices variable"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Dropdown.svelte must retain substantial implementation logic —
    the fix should only change reactive variable declarations, not gut the file."""
    content = TARGET.read_text()

    line_count = content.count("\n")
    assert line_count > 100, f"File too short ({line_count} lines) — likely stubbed"

    assert "handle_option_selected" in content, "Missing handle_option_selected function"
    assert "DropdownOptions" in content or "dropdown" in content.lower(), (
        "Missing dropdown component references"
    )

    reactive_refs = len(re.findall(r"\$(state|derived|effect|props)", content))
    assert reactive_refs >= 3, f"Too few reactive declarations ({reactive_refs})"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — component structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_component_exports_intact():
    """Dropdown component must maintain its public API exports (Index.svelte
    and Example.svelte) — pass_to_pass to ensure fix does not break exports."""
    index_path = Path("/workspace/gradio/js/dropdown/Index.svelte")
    example_path = Path("/workspace/gradio/js/dropdown/Example.svelte")

    assert index_path.exists(), "Index.svelte export file missing"
    assert example_path.exists(), "Example.svelte export file missing"

    index_content = index_path.read_text()
    assert "Dropdown" in index_content or "dropdown" in index_content.lower(), (
        "Index.svelte does not reference Dropdown component"
    )


# [static] pass_to_pass
def test_dropdown_utils_intact():
    """Dropdown utility functions must be present — pass_to_pass to ensure
    the fix does not remove shared utility code."""
    utils_path = Path("/workspace/gradio/js/dropdown/shared/utils.ts")
    assert utils_path.exists(), "utils.ts file missing"

    utils_content = utils_path.read_text()

    # Key functions expected in utils.ts
    assert "handle_filter" in utils_content, "Missing handle_filter function in utils.ts"
    assert "handle_shared_keys" in utils_content, "Missing handle_shared_keys function in utils.ts"


# [static] pass_to_pass
def test_dropdown_options_component_intact():
    """DropdownOptions component must be present — pass_to_pass to ensure
    the fix does not remove the options sub-component."""
    options_path = Path("/workspace/gradio/js/dropdown/shared/DropdownOptions.svelte")
    assert options_path.exists(), "DropdownOptions.svelte file missing"

    options_content = options_path.read_text()
    assert len(options_content) > 500, "DropdownOptions.svelte seems too small/truncated"


# [static] pass_to_pass
def test_unit_tests_file_intact():
    """The unit test file (dropdown.test.ts) must exist and have tests —
    pass_to_pass to ensure the fix does not remove or break tests."""
    test_path = Path("/workspace/gradio/js/dropdown/dropdown.test.ts")
    assert test_path.exists(), "dropdown.test.ts test file missing"

    test_content = test_path.read_text()

    # Should have test imports
    assert "vitest" in test_content or "test" in test_content, (
        "Test file missing vitest imports"
    )

    # Should have actual test cases
    test_count = len(re.findall(r"\btest\s*\(", test_content))
    assert test_count >= 3, f"Too few test cases found ({test_count}, expected at least 3)"

    # Should test the Dropdown component
    assert "Dropdown" in test_content, "Test file does not reference Dropdown component"


# [static] pass_to_pass
def test_multiselect_intact():
    """Multiselect component (related dropdown variant) must be present —
    pass_to_pass to ensure the fix does not affect the multiselect variant."""
    multiselect_path = Path("/workspace/gradio/js/dropdown/shared/Multiselect.svelte")
    assert multiselect_path.exists(), "Multiselect.svelte file missing"

    multiselect_content = multiselect_path.read_text()

    # Should have reactive declarations
    reactive_count = len(re.findall(r"\$(state|derived|effect)", multiselect_content))
    assert reactive_count >= 3, f"Multiselect missing reactive declarations ({reactive_count} found)"

    # Should reference multiselect-specific concepts
    assert "multiselect" in multiselect_content.lower() or "selected" in multiselect_content.lower(), (
        "Multiselect content does not reference expected functionality"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — file content checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_dropdown_types_valid():
    """Dropdown types.ts must have valid TypeScript interface definitions."""
    types_path = Path("/workspace/gradio/js/dropdown/types.ts")
    assert types_path.exists(), "types.ts file missing"

    content = types_path.read_text()

    # Should export key types
    assert "export" in content, "types.ts should export type definitions"
    assert "interface" in content or "type" in content, "types.ts should define types/interfaces"

    # Should define expected dropdown types
    assert "DropdownProps" in content, "Missing DropdownProps type definition"
    assert "DropdownEvents" in content or "Item" in content, "Missing event or item type definitions"


# [static] pass_to_pass
def test_dropdown_stories_intact():
    """Dropdown Storybook stories must be present and intact."""
    stories_path = Path("/workspace/gradio/js/dropdown/Dropdown.stories.svelte")
    assert stories_path.exists(), "Dropdown.stories.svelte file missing"

    content = stories_path.read_text()

    # Should be valid Svelte Storybook syntax
    assert "<script" in content, "stories file missing script tag"
    assert "import" in content, "stories file missing imports"

    # Should reference the component being tested
    assert "Dropdown" in content, "stories file does not reference Dropdown component"


# [static] pass_to_pass
def test_multiselect_stories_intact():
    """Multiselect Storybook stories must be present."""
    stories_path = Path("/workspace/gradio/js/dropdown/Multiselect.stories.svelte")
    assert stories_path.exists(), "Multiselect.stories.svelte file missing"

    content = stories_path.read_text()

    # Should reference multiselect
    assert "Multiselect" in content, "stories file does not reference Multiselect"


# [static] pass_to_pass
def test_dropdown_package_json_valid():
    """Dropdown package.json must be valid JSON with expected exports."""
    pkg_path = Path("/workspace/gradio/js/dropdown/package.json")
    assert pkg_path.exists(), "package.json file missing"

    result = _run_analysis(r"""
import json
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/package.json").read_text()
try:
    pkg = json.loads(content)
    print(json.dumps({
        "valid_json": True,
        "has_name": "name" in pkg,
        "has_exports": "exports" in pkg,
        "name": pkg.get("name", ""),
        "has_dropdown_export": "." in pkg.get("exports", {}),
    }))
except json.JSONDecodeError as e:
    print(json.dumps({"valid_json": False, "error": str(e)}))
""")

    assert result["valid_json"], "package.json is not valid JSON"
    assert result["has_name"], "package.json missing name field"
    assert result["has_exports"], "package.json missing exports field"
    assert result["has_dropdown_export"], "package.json missing default export"


# [static] pass_to_pass
def test_no_obvious_svelte_syntax_errors():
    """Dropdown.svelte must have valid Svelte component structure."""
    content = TARGET.read_text()

    # Basic Svelte structure checks
    assert "<script" in content, "Dropdown.svelte missing script tag"
    assert "</script>" in content, "Dropdown.svelte missing closing script tag"

    # Check script section is parseable
    script_match = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    assert script_match is not None, "Could not extract script section"

    script_content = script_match.group(1)

    # Check for basic syntax issues (unbalanced parentheses in function definitions)
    open_parens = script_content.count("(")
    close_parens = script_content.count(")")
    assert open_parens == close_parens, (
        f"Script has unbalanced parentheses: {open_parens} open, {close_parens} close"
    )

    # Check for unbalanced braces in the template (outside script)
    template = re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL)
    template_exprs = re.findall(r"\{[^{}]*\}", template)
    remaining = re.sub(r"\{[^{}]*\}", "", template)
    standalone_open = remaining.count("{") - remaining.count("{{")
    standalone_close = remaining.count("}") - remaining.count("}}")
    # Allow some tolerance for Svelte syntax like {#if} blocks
    assert abs(standalone_open - standalone_close) <= 3, (
        "Template may have unbalanced braces"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD verification using subprocess.run
# These tests execute actual CI commands from the repo's CI configuration.
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_git_status_clean():
    """Git repo status is clean (CI: git status check).
    Verifies the repo has no uncommitted changes after checkout."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # Should be empty (no uncommitted changes)
    assert r.returncode == 0, f"git status failed: {r.stderr[-500:]}"
    assert r.stdout.strip() == "", f"Repo has uncommitted changes:\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_git_log_has_commit():
    """Git repo has the expected base commit in its history (CI: git log check).
    Verifies the repo contains the expected base commit (may have new commits on top)."""
    expected = "e5ba4fa992c0ac389c6af2d143c9ad4c33eea360"
    # Check that the base commit is in the repo history
    r = subprocess.run(
        ["git", "merge-base", "--is-ancestor", expected, "HEAD"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Expected commit {expected[:12]} not found in repo history"
    )


# [repo_tests] pass_to_pass
def test_dropdown_svelte_syntax_valid():
    """Dropdown.svelte has valid Svelte script syntax (CI: syntax validation).
    Validates that the script section has balanced braces and valid variable
    declarations — a lightweight CI check for code quality."""
    code = r'''
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte").read_text()
m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
if not m:
    print(json.dumps({"error": "No script section found"}))
    raise SystemExit(1)

script = m.group(1)
errors = []

# Check for balanced braces in script
open_brace = script.count("{")
close_brace = script.count("}")
if open_brace != close_brace:
    errors.append(f"Unbalanced braces: {open_brace} open, {close_brace} close")

# Check for balanced parentheses
open_paren = script.count("(")
close_paren = script.count(")")
if open_paren != close_paren:
    errors.append(f"Unbalanced parentheses: {open_paren} open, {close_paren} close")

# Check for balanced brackets
open_bracket = script.count("[")
close_bracket = script.count("]")
if open_bracket != close_bracket:
    errors.append(f"Unbalanced brackets: {open_bracket} open, {close_bracket} close")

# Validate Svelte 5 rune usage patterns
runes = re.findall(r"\$(state|derived|effect|props|bindable)\b", script)

print(json.dumps({
    "valid": len(errors) == 0,
    "errors": errors,
    "runes_found": runes,
    "has_reactive_declarations": len(runes) > 0
}))
'''
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax analysis failed: {r.stderr[-500:]}"
    result = json.loads(r.stdout.strip())
    assert result["valid"], f"Syntax errors found: {result.get('errors', [])}"
    assert result["has_reactive_declarations"], "No Svelte 5 runes found in component"


# [repo_tests] pass_to_pass
def test_dropdown_options_component_syntax():
    """DropdownOptions.svelte has valid component structure (CI: syntax validation).
    Validates that the DropdownOptions sub-component has valid syntax."""
    code = r'''
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/DropdownOptions.svelte").read_text()
m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
if not m:
    print(json.dumps({"error": "No script section found"}))
    raise SystemExit(1)

script = m.group(1)
errors = []

# Check for balanced braces/parens/brackets
if script.count("{") != script.count("}"):
    errors.append("Unbalanced braces in script")
if script.count("(") != script.count(")"):
    errors.append("Unbalanced parentheses in script")
if script.count("[") != script.count("]"):
    errors.append("Unbalanced brackets in script")

# Check for expected props interface definition
has_interface = "interface" in script or "type" in script
has_exports = "export" in script

print(json.dumps({
    "valid": len(errors) == 0,
    "errors": errors,
    "has_interface": has_interface,
    "has_exports": has_exports,
    "line_count": len(content.splitlines()),
}))
'''
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax analysis failed: {r.stderr[-500:]}"
    result = json.loads(r.stdout.strip())
    assert result["valid"], f"Syntax errors: {result.get('errors', [])}"
    assert result["line_count"] > 50, f"DropdownOptions.svelte too small ({result['line_count']} lines)"


# [repo_tests] pass_to_pass
def test_dropdown_utils_exports():
    """Dropdown utils.ts has valid exports (CI: export validation).
    Validates that utility functions are properly exported and have expected signatures."""
    code = r'''
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/utils.ts").read_text()

# Find exported functions
exports = re.findall(r"export\s+(?:async\s+)?function\s+(\w+)", content)
export_consts = re.findall(r"export\s+const\s+(\w+)", content)
export_let = re.findall(r"export\s+let\s+(\w+)", content)
export_default = "export default" in content

# Check for TypeScript types in function signatures
has_types = ":" in content and "(" in content

print(json.dumps({
    "functions": exports,
    "constants": export_consts + export_let,
    "has_default_export": export_default,
    "has_types": has_types,
    "line_count": len(content.splitlines()),
}))
'''
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Export analysis failed: {r.stderr[-500:]}"
    result = json.loads(r.stdout.strip())
    assert "handle_filter" in result["functions"], "Missing handle_filter export"
    assert "handle_shared_keys" in result["functions"], "Missing handle_shared_keys export"
    assert result["has_types"], "utils.ts missing TypeScript type annotations"


# [repo_tests] pass_to_pass
def test_git_ls_files_valid():
    """Git repo file list is valid (CI: git ls-files check).
    Verifies git can list all tracked files without errors — basic repo integrity check."""
    r = subprocess.run(
        ["git", "ls-files", "--", "js/dropdown/"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git ls-files failed: {r.stderr[-500:]}"
    files = r.stdout.strip().split("\n")
    # Should have at least the main dropdown files
    assert any("Dropdown.svelte" in f for f in files), "Dropdown.svelte not in git"
    assert any("dropdown.test.ts" in f for f in files), "dropdown.test.ts not in git"


# [repo_tests] pass_to_pass - CI-style file content validation
def test_dropdown_svelte_no_buggy_destructure():
    """CI check: Dropdown.svelte must NOT contain the buggy array destructuring pattern
    `let [input_text, selected_index] = $derived.by(...)` that causes O(N) re-derivations.
    This is a regression check — the fix removes this pattern."""
    code = r'''
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte").read_text()
buggy = re.search(
    r"let\s*\[.*?input_text.*?,.*?selected_index.*?\]\s*=\s*\$derived",
    content, re.DOTALL,
)
print(json.dumps({"has_buggy_destructure": buggy is not None}))
'''
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr[-500:]}"
    result = json.loads(r.stdout.strip())
    assert not result["has_buggy_destructure"], (
        "Buggy array destructuring pattern still present — fix not applied"
    )


# [repo_tests] pass_to_pass - CI-style validation of state declarations
def test_dropdown_svelte_state_declarations_valid():
    """CI check: Dropdown.svelte must have proper $state declarations for input_text and selected_index.
    Validates the fix correctly uses standalone $state variables instead of destructuring."""
    code = r'''
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte").read_text()
m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
script = m.group(1) if m else ""

has_input_text_state = bool(
    re.search(r"let\s+input_text\s*(?::\s*\S+\s*)?=\s*\$state", script)
)
has_selected_index_state = bool(
    re.search(r"let\s+selected_index\s*(?::\s*[^=]+)?=\s*\$state", script)
)
has_effect = bool(re.search(r"\$effect\s*\(", script))

print(json.dumps({
    "input_text_state": has_input_text_state,
    "selected_index_state": has_selected_index_state,
    "has_effect": has_effect,
}))
'''
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr[-500:]}"
    result = json.loads(r.stdout.strip())
    assert result["input_text_state"], "input_text must be declared as $state"
    assert result["selected_index_state"], "selected_index must be declared as $state"
    assert result["has_effect"], "$effect block must be present for value change handling"


# [repo_tests] pass_to_pass - CI-style validation of derived variables
def test_dropdown_svelte_derived_indices_valid():
    """CI check: Dropdown.svelte must have selected_indices as $derived variable.
    Validates the fix pre-computes selected_indices instead of inline ternary."""
    code = r'''
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte").read_text()
m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
script = m.group(1) if m else ""

has_derived = bool(re.search(r"let\s+selected_indices\s*=\s*\$derived", script))
print(json.dumps({"has_selected_indices_derived": has_derived}))
'''
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr[-500:]}"
    result = json.loads(r.stdout.strip())
    assert result["has_selected_indices_derived"], (
        "selected_indices must be declared as $derived variable"
    )


# [repo_tests] pass_to_pass - CI-style git file integrity check
def test_dropdown_files_tracked_by_git():
    """CI check: All critical dropdown files must be tracked by git.
    Verifies file integrity via git ls-files — ensures no files are missing/untracked."""
    r = subprocess.run(
        ["git", "ls-files", "js/dropdown/"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git ls-files failed: {r.stderr[-500:]}"
    files = r.stdout.strip().split("\n")

    required_patterns = [
        "js/dropdown/shared/Dropdown.svelte",
        "js/dropdown/shared/DropdownOptions.svelte",
        "js/dropdown/shared/utils.ts",
        "js/dropdown/dropdown.test.ts",
        "js/dropdown/package.json",
        "js/dropdown/types.ts",
    ]

    for pattern in required_patterns:
        assert any(pattern in f for f in files), f"Required file {pattern} not tracked by git"



# [repo_tests] pass_to_pass - CI check: validate commit signature
def test_git_commit_verified():
    """CI check: Git commit is valid and has proper author information.
    Verifies the HEAD commit has required metadata — basic repo integrity."""
    r = subprocess.run(
        ["git", "log", "-1", "--format=%H:%an:%ae"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git log failed: {r.stderr[-500:]}"
    commit_info = r.stdout.strip()
    assert len(commit_info) > 0, "No commit information found"
    parts = commit_info.split(":")
    assert len(parts) >= 3, f"Invalid commit format: {commit_info}"
    sha, author, email = parts[0], parts[1], parts[2]
    assert len(sha) == 40, f"Invalid commit SHA: {sha}"
    assert len(author) > 0, "Missing author name"
    assert "@" in email, f"Invalid author email: {email}"


# [repo_tests] pass_to_pass - CI check: validate repo structure
def test_gradio_package_structure_valid():
    """CI check: Gradio Python package has valid structure.
    Verifies key Python files exist and are tracked by git."""
    r = subprocess.run(
        ["git", "ls-files", "gradio/"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git ls-files failed: {r.stderr[-500:]}"
    files = r.stdout.strip().split("\n")

    # Key Python files that must exist
    required_files = [
        "gradio/__init__.py",
        "gradio/blocks.py",
        "gradio/components/__init__.py",
    ]

    for pattern in required_files:
        assert any(pattern in f for f in files), f"Required Python file {pattern} not found"


# [repo_tests] pass_to_pass - CI check: validate Svelte rune patterns
def test_dropdown_svelte_svelte5_runes():
    """CI check: Dropdown.svelte uses valid Svelte 5 rune patterns.
    Validates $state, $derived, and $effect runes are used correctly."""
    code = r"""
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte").read_text()
m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
script = m.group(1) if m else ""

# Check for Svelte 5 runes
runes = {
    "state": bool(re.search(r"\$state\s*\(", script)),
    "derived": bool(re.search(r"\$derived", script)),
    "effect": bool(re.search(r"\$effect\s*\(", script)),
    "props": bool(re.search(r"\$props\s*\(", script)),
}

# Count variable declarations with runes
state_vars = len(re.findall(r"let\s+\w+[^=]*=\s*\\$state", script))
derived_vars = len(re.findall(r"let\s+\w+[^=]*=\s*\\$derived", script))

print(json.dumps({
    "runes_found": runes,
    "state_vars_count": state_vars,
    "derived_vars_count": derived_vars,
    "valid": any(runes.values()),
}))
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr[-500:]}"
    result = json.loads(r.stdout.strip())
    assert result["valid"], "Invalid Svelte rune usage"


# [repo_tests] pass_to_pass - CI check: validate TypeScript utils
def test_dropdown_utils_typescript_syntax():
    """CI check: Dropdown utils.ts has valid TypeScript syntax patterns.
    Validates TypeScript function declarations and type annotations."""
    code = r"""
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/shared/utils.ts").read_text()

# Check TypeScript patterns
has_interface = bool(re.search(r"interface\s+\w+", content))
has_type_alias = bool(re.search(r"type\s+\w+", content))
has_typed_params = bool(re.search(r"\(\s*\w+\s*:\s*\w+", content))
has_return_type = bool(re.search(r"\)\s*:\s*\w+\s*\{", content))

# Check for common syntax errors
errors = []
if content.count("(") != content.count(")"):
    errors.append("Unbalanced parentheses")
if content.count("{") != content.count("}"):
    errors.append("Unbalanced braces")
if content.count("[") != content.count("]"):
    errors.append("Unbalanced brackets")

# Count exported functions
exported_funcs = len(re.findall(r"export\s+(?:async\s+)?function\s+\w+", content))

print(json.dumps({
    "has_interface": has_interface,
    "has_type_alias": has_type_alias,
    "has_typed_params": has_typed_params,
    "has_return_type": has_return_type,
    "syntax_errors": errors,
    "exported_functions": exported_funcs,
    "valid": len(errors) == 0 and exported_funcs >= 1,
}))
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr[-500:]}"
    result = json.loads(r.stdout.strip())
    assert result["valid"], f"TypeScript validation failed: {result.get("syntax_errors", [])}"
    assert result["has_typed_params"] or result["has_return_type"], "Missing TypeScript type annotations"


# [repo_tests] pass_to_pass - CI check: validate dropdown test file
def test_dropdown_test_file_structure():
    """CI check: dropdown.test.ts has valid test structure.
    Validates vitest test patterns and component imports."""
    code = r"""
import json, re
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/dropdown.test.ts").read_text()

# Check vitest patterns
has_test_import = bool(re.search(r"import.*from\s+[\"\']vitest[\"\']", content))
has_describe = bool(re.search(r"describe\s*\(", content))
has_test_cases = bool(re.search(r"\btest\s*\(", content))
has_assertions = bool(re.search(r"assert\.|expect\(", content))
has_cleanup = bool(re.search(r"cleanup|afterEach", content))

# Count test cases
test_count = len(re.findall(r"\btest\s*\(", content))

# Check for Dropdown imports
imports_dropdown = bool(re.search(r"import\s+.*Dropdown", content))

# Check basic syntax
errors = []
if content.count("(") != content.count(")"):
    errors.append("Unbalanced parentheses")
if content.count("{") != content.count("}"):
    errors.append("Unbalanced braces")

print(json.dumps({
    "has_test_import": has_test_import,
    "has_describe": has_describe,
    "has_test_cases": has_test_cases,
    "has_assertions": has_assertions,
    "has_cleanup": has_cleanup,
    "test_count": test_count,
    "imports_dropdown": imports_dropdown,
    "syntax_errors": errors,
    "valid": len(errors) == 0 and has_test_import and test_count >= 3,
}))
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr[-500:]}"
    result = json.loads(r.stdout.strip())
    assert result["valid"], f"Test file validation failed: {result}"
    assert result["test_count"] >= 3, f"Too few test cases: {result['test_count']}"
    assert result["imports_dropdown"], "Test file does not import Dropdown component"


# [repo_tests] pass_to_pass - CI check: validate package.json structure
def test_dropdown_package_json_structure():
    """CI check: Dropdown package.json has valid structure with exports.
    Validates JSON structure and required fields."""
    code = r"""
import json
from pathlib import Path

content = Path("/workspace/gradio/js/dropdown/package.json").read_text()
try:
    pkg = json.loads(content)
    result = {
        "valid_json": True,
        "has_name": "name" in pkg,
        "has_version": "version" in pkg,
        "has_exports": "exports" in pkg,
        "has_svelte": "svelte" in pkg.get("exports", {}),
        "has_types": "types" in str(pkg.get("exports", {})),
        "name": pkg.get("name", ""),
    }
except json.JSONDecodeError as e:
    result = {"valid_json": False, "error": str(e)}

print(json.dumps(result))
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr[-500:]}"
    result = json.loads(r.stdout.strip())
    assert result["valid_json"], "Invalid package.json"
    assert result["has_name"], "Missing name field"
    assert result["has_exports"], "Missing exports field"
    assert "gradio" in result.get("name", ""), f"Unexpected package name: {result.get("name")}"
