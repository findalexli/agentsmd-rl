"""
Task: gradio-button-scale-parameter
Repo: gradio-app/gradio @ a0fff5cb0e4cc0f8cc3fff7b5fbe18a031c7cc27
PR:   12911

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Svelte-only change (no Node.js in test env), so behavioral tests use
subprocess.run to parse and validate the component structure rigorously.
"""

import json
import subprocess
from pathlib import Path

TARGET = Path("/workspace/gradio/js/button/Index.svelte")
REPO = Path("/workspace/gradio")


def _extract_button_attrs():
    """Use subprocess to parse the Svelte file and extract Button element attributes."""
    script = r'''
import json, re, sys
from pathlib import Path

content = Path("/workspace/gradio/js/button/Index.svelte").read_text()

# Strip JS comments
content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

# Find all <Button ...> elements and extract their attributes
button_tags = re.findall(r"<Button\s+([^>]*)/??>", content, re.DOTALL)
if not button_tags:
    print(json.dumps({"error": "no_button_tag"}))
    sys.exit(0)

attrs = {}
for tag in button_tags:
    # Extract key={value} bindings
    for m in re.finditer(r"(\w+)\s*=\s*\{([^}]+)\}", tag):
        attrs[m.group(1)] = m.group(1).strip()

print(json.dumps({"bindings": attrs, "raw_tags": button_tags}))
'''
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=15, cwd=str(REPO),
    )
    return r


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_scale_reads_from_shared():
    """Button scale prop bound to gradio.shared.scale, not gradio.props.scale."""
    script = r'''
import json, re, sys
from pathlib import Path

content = Path("/workspace/gradio/js/button/Index.svelte").read_text()
content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

button_tags = re.findall(r"<Button\s+([^>]*)/??>", content, re.DOTALL)
if not button_tags:
    print(json.dumps({"ok": False, "reason": "no_button_tag"}))
    sys.exit(0)

for tag in button_tags:
    m = re.search(r"scale\s*=\s*\{([^}]+)\}", tag)
    if m:
        val = m.group(1).strip()
        # On the base commit, scale reads from gradio.props.scale (broken)
        if "gradio.props.scale" in val:
            print(json.dumps({"ok": False, "reason": f"reads_props:{val}"}))
            sys.exit(0)
        # After the fix, scale reads from gradio.shared.scale
        if "gradio.shared" in val and "scale" in val:
            print(json.dumps({"ok": True, "binding": val}))
            sys.exit(0)

# If no scale binding found at all, something is wrong
print(json.dumps({"ok": False, "reason": "no_scale_binding"}))
'''
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=15, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Parse script failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("ok"), f"Bug not fixed: {result.get('reason', r.stdout)}"


# [pr_diff] fail_to_pass
def test_scale_not_in_button_props():
    """scale field removed from ButtonProps type definition (shared prop)."""
    script = r'''
import json, re, sys
from pathlib import Path

content = Path("/workspace/gradio/js/button/Index.svelte").read_text()
content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

# Look for destructured type annotation: let { ... }: { scale: number; ... }
# This is how ButtonProps are declared in this Svelte file
type_block_m = re.search(r"let\s*\{[^}]*\}\s*:\s*\{([^}]+)\}", content, re.DOTALL)
if type_block_m:
    props_block = type_block_m.group(1)
    if re.search(r"\bscale\s*:", props_block):
        print(json.dumps({"ok": False, "reason": "scale_in_type_block"}))
        sys.exit(0)

# Also check interface/type ButtonProps
iface_m = re.search(
    r"(?:interface|type)\s+ButtonProps\s*[={]\s*\{([^}]*)\}", content, re.DOTALL
)
if iface_m:
    if re.search(r"\bscale\s*:", iface_m.group(1)):
        print(json.dumps({"ok": False, "reason": "scale_in_interface"}))
        sys.exit(0)

# Final sweep: any standalone "scale: number" in a type context
if re.search(r"\bscale\s*:\s*number\b", content):
    print(json.dumps({"ok": False, "reason": "scale_typed_as_number"}))
    sys.exit(0)

print(json.dumps({"ok": True}))
'''
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=15, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Parse script failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("ok"), f"scale still in props: {result.get('reason', r.stdout)}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_svelte_parses():
    """Index.svelte exists and has basic Svelte structure."""
    content = TARGET.read_text()
    assert "<script" in content, "Missing <script> tag"
    assert "<Button" in content, "Missing <Button> component usage"


# [static] pass_to_pass
def test_other_props_intact():
    """Other ButtonProps fields (value, variant, size, link, icon) still present."""
    import re
    content = TARGET.read_text()
    content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
    for prop in ["value", "variant", "size", "link", "icon"]:
        assert re.search(rf"\b{prop}\b", content), (
            f"Expected prop '{prop}' missing — agent may have over-deleted"
        )


# [static] pass_to_pass
def test_not_stub():
    """File has meaningful Svelte component, not emptied or stubbed."""
    import re
    content = TARGET.read_text()
    assert len(content) >= 200, "File too small — likely stubbed"
    script_m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    assert script_m, "No <script> section found"
    assert len(script_m.group(1).strip()) >= 50, "Script section too small"
    assert "gradio" in content, "No gradio reference — file was likely replaced"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — Repo CI/CD checks that should pass on
# both base commit AND after the fix. These use Python subprocess to validate
# Svelte structure. Note: Node.js/pnpm not available in this environment, so
# we use Python static analysis as lightweight P2P gates.
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_svelte_syntax():
    """Svelte file has valid structure: script tag, imports, and component (pass_to_pass)."""
    script = r'''
import re
from pathlib import Path

content = Path("/workspace/gradio/js/button/Index.svelte").read_text()

# Basic Svelte structure checks
assert "<script" in content, "Missing <script> tag"
assert "</script>" in content, "Missing </script> tag"

# Check for imports (TypeScript interfaces)
assert "interface" in content or "type " in content, "Missing type/interface definitions"

# Check for component usage
assert "<Button" in content, "Missing <Button> component usage"

# Check for proper binding syntax pattern
binding_pattern = re.search(r"\w+\s*=\s*\{[^}]+\}", content)
assert binding_pattern, "No prop bindings found in Svelte style"

print("Svelte syntax checks passed")
'''
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=15, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Svelte syntax check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_button_props_structure():
    """Button component has valid type/prop declarations (pass_to_pass)."""
    script = r'''
import re
from pathlib import Path

content = Path("/workspace/gradio/js/button/Index.svelte").read_text()
content_clean = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
content_clean = re.sub(r"/\*.*?\*/", "", content_clean, flags=re.DOTALL)

# Check that the file has type declarations - can be interface or type alias
# The Button component uses: interface ButtonProps { ... }
has_type_declaration = False

# Look for interface or type definition (e.g., "interface ButtonProps {")
if re.search(r"(?:interface|type)\s+\w+Props\s*\{", content_clean, re.DOTALL):
    has_type_declaration = True

# The file should have some form of type declaration
assert has_type_declaration, "No type declarations found (expected interface or type Props)"
print("Button props structure is valid")
'''
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=15, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Button props structure check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_gradio_bindings_valid():
    """Component uses valid gradio bindings where required (pass_to_pass)."""
    script = r'''
import re
from pathlib import Path

content = Path("/workspace/gradio/js/button/Index.svelte").read_text()
content_clean = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
content_clean = re.sub(r"/\*.*?\*/", "", content_clean, flags=re.DOTALL)

# Find all <Button ...> usages and their bindings
button_tags = re.findall(r"<Button\s+([^>]*)/?>", content_clean, re.DOTALL)
assert button_tags, "No <Button> tags found"

bindings = []
for tag in button_tags:
    # Extract prop={value} bindings
    for m in re.finditer(r"(\w+)\s*=\s*\{([^}]+)\}", tag):
        prop_name = m.group(1)
        prop_value = m.group(2).strip()
        bindings.append((prop_name, prop_value))

print(f"Found bindings: {bindings}")

# Core visual props should reference gradio (either props or shared)
# These are the props that affect the component's appearance/behavior
core_props = ["value", "variant", "size", "scale", "link", "icon", "visible", "disabled"]
for prop, value in bindings:
    if prop in core_props:
        # These should reference gradio (either props or shared namespace)
        assert "gradio." in value, f"Core prop {prop}={value} should reference gradio"

print("Core gradio bindings are valid")
'''
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=15, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Gradio bindings validation failed:\n{r.stderr}\n{r.stdout}"
