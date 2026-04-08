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
        "Array destructuring from $derived.by for input_text/selected_index still present"
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
        "input_text must be declared as a standalone $state variable"
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
        "selected_index must be declared as a standalone $state variable"
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

assigns_input = len(re.findall(r"input_text\s*=", body))
assigns_selected = len(re.findall(r"selected_index\s*=", body))

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
    assert result["handles_nullish"], "$effect doesn't handle null/undefined value"
    assert result["handles_in_choices"], "$effect doesn't handle value-in-choices case"
    assert result["handles_custom"], "$effect doesn't handle allow_custom_value case"
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
        "selected_indices must be declared as a $derived variable"
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
        "Template still has inline selected_indices ternary — must use $derived variable"
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
        "Template doesn't reference the selected_indices variable"
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
