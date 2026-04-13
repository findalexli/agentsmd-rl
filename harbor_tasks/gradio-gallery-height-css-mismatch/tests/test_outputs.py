"""
Task: gradio-gallery-height-css-mismatch
Repo: gradio-app/gradio @ 611d40b529b6c97e41e09ae0a60804ad71a9bf58
PR:   12927

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
GALLERY = f"{REPO}/js/gallery/shared/Gallery.svelte"
INDEX = f"{REPO}/js/gallery/Index.svelte"
TYPES = f"{REPO}/js/gallery/types.ts"


def _node_eval(script: str, timeout: int = 10) -> str:
    """Run a short Node.js script and return stdout."""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout,
    )
    return r.stdout.strip()


def _extract_style_height_expr(src: str) -> str | None:
    """Extract the expression inside style:height={...} from Svelte source."""
    marker = "style:height={"
    idx = src.find(marker)
    if idx == -1:
        return None
    start = idx + len(marker)
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    return src[start : i - 1].strip()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_css_class_consistency():
    """CSS selectors in <style> must match class names used in the template."""
    src = Path(GALLERY).read_text()
    style_idx = src.find("<style")
    assert style_idx != -1, "No <style> block found in Gallery.svelte"

    template = src[:style_idx]
    css = src[style_idx:]

    # Collect class names from the template
    tmpl_classes = set()
    for m in re.finditer('class=["\']([^"\']+)["\']', template):
        tmpl_classes.update(m.group(1).split())

    # Collect CSS class selectors from style block
    css_selectors = set()
    for m in re.finditer(r"\.([a-zA-Z_][\w-]*)\s*[{,:]", css):
        css_selectors.add(m.group(1))

    # Every container/gallery class used in the template must have a CSS rule
    for cls in tmpl_classes:
        if len(cls) < 4:
            continue
        if "container" in cls or "gallery" in cls:
            assert cls in css_selectors, (
                f"Template uses class '{cls}' but no matching CSS rule exists — "
                f"styles will never apply"
            )


# [pr_diff] fail_to_pass
def test_string_height_preserved():
    """style:height must preserve CSS string values like '300px' and '50vh'."""
    src = Path(GALLERY).read_text()
    expr = _extract_style_height_expr(src)
    assert expr is not None, "No style:height={...} binding found"

    # Evaluate the expression with various string heights via Node
    script = f"""
    const expr = {json.dumps(expr)};
    const fn = new Function('height', 'return ' + expr);
    const results = {{
        '300px': fn('300px'),
        '50vh': fn('50vh'),
        '10em': fn('10em'),
    }};
    console.log(JSON.stringify(results));
    """
    out = _node_eval(script)
    results = json.loads(out)

    for value, result in results.items():
        assert result == value, (
            f"String height '{value}' was corrupted to '{result}' — "
            f"likely unconditional + 'px' suffix"
        )


# [pr_diff] fail_to_pass
def test_height_forwarding_accepts_strings():
    """Index.svelte must forward string heights (e.g. '300px') to Gallery."""
    src = Path(INDEX).read_text()

    # Find height={...} expressions that reference gradio
    script = f"""
    const src = {json.dumps(src)};
    const re = /height\s*=\s*\{{/g;
    let m, found = false;
    while ((m = re.exec(src)) !== null) {{
        let i = m.index + m[0].length, d = 1;
        while (i < src.length && d > 0) {{
            if (src[i] === '{{') d++;
            else if (src[i] === '}}') d--;
            i++;
        }}
        const expr = src.slice(m.index + m[0].length, i - 1).trim();
        if (!expr.includes('gradio')) continue;
        found = true;
        try {{
            const fn = new Function('gradio', 'return ' + expr);
            const r = fn({{ props: {{ height: '300px' }} }});
            console.log(JSON.stringify({{ found: true, result: r === undefined ? '__UNDEFINED__' : r }}));
            process.exit(0);
        }} catch(e) {{
            console.log(JSON.stringify({{ found: true, error: e.message }}));
            process.exit(0);
        }}
    }}
    if (!found) {{
        console.log(JSON.stringify({{ found: false }}));
    }}
    """
    out = _node_eval(script)
    data = json.loads(out)

    if data["found"]:
        assert "error" not in data, f"Expression eval error: {data.get('error')}"
        assert data["result"] == "300px", (
            f"String height '300px' was dropped or transformed to {data['result']!r} "
            f"during forwarding — only numeric heights are being passed through"
        )
    else:
        # No gradio-referencing height expression; check height prop exists at all
        assert re.search(r"height\s*=\s*\{", src), "No height prop found in Index.svelte"


# [pr_diff] fail_to_pass
def test_height_type_accepts_string():
    """GalleryProps.height type must accept CSS string values, not just number|'auto'."""
    src = Path(TYPES).read_text()
    m = re.search(r"height\s*[?:]?\s*:\s*([^;}\n]+)", src, re.MULTILINE)
    assert m is not None, "No height type definition found in types.ts"

    typedef = m.group(1).strip()
    assert "string" in typedef, (
        f"height type is '{typedef}' — must include 'string' to accept CSS values "
        f"like '300px' or '50vh'"
    )


# [pr_diff] fail_to_pass
def test_upload_wrapper_height():
    """Upload wrapper area must have height styling so it doesn't collapse."""
    src = Path(INDEX).read_text()
    style_idx = src.find("<style")
    assert style_idx != -1, "No <style> block in Index.svelte"

    css = src[style_idx:]
    # Check for a rule that gives the upload/wrapper area height
    has_height_rule = bool(
        re.search(r"upload[-_]?wrapper[^}]*height", css, re.IGNORECASE)
        or re.search(r"wrapper[^}]*\{[^}]*height\s*:", css, re.IGNORECASE)
        or re.search(r"wrapper[^}]*\{[^}]*flex\s*:", css, re.IGNORECASE)
    )
    assert has_height_rule, (
        "No CSS rule gives the upload wrapper area a height — "
        "the interactive upload area will collapse to zero height"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_numeric_height_still_works():
    """Numeric height (e.g. 300) must still produce valid CSS like '300px'."""
    src = Path(GALLERY).read_text()
    expr = _extract_style_height_expr(src)
    assert expr is not None, "No style:height={...} binding found"

    script = f"""
    const fn = new Function('height', 'return ' + {json.dumps(expr)});
    const r = fn(300);
    console.log(JSON.stringify(r));
    """
    out = _node_eval(script)
    result = json.loads(out)
    assert result in ("300px", 300), (
        f"Numeric height 300 produced {result!r} — expected '300px' or 300"
    )


# [pr_diff] pass_to_pass
def test_auto_height_returns_null():
    """height='auto' must produce null (no inline style override, let CSS handle it)."""
    src = Path(GALLERY).read_text()
    expr = _extract_style_height_expr(src)
    assert expr is not None, "No style:height={...} binding found"

    script = f"""
    const fn = new Function('height', 'return ' + {json.dumps(expr)});
    const r = fn('auto');
    console.log(JSON.stringify(r));
    """
    out = _node_eval(script)
    result = json.loads(out)
    assert result is None or result == "auto", (
        f"Auto height produced {result!r} — expected null or 'auto'"
    )


# [pr_diff] pass_to_pass
def test_hidden_upload_input_preserved():
    """hidden-upload-input class must still exist for webcam mode toggling."""
    src = Path(INDEX).read_text()
    assert "hidden-upload-input" in src, (
        "hidden-upload-input class was removed — needed to hide the upload "
        "input when webcam is active"
    )


# [static] pass_to_pass
def test_gallery_not_stub():
    """Gallery.svelte must be a real Svelte component, not a stub."""
    src = Path(GALLERY).read_text()
    lines = src.split("\n")
    assert len(lines) > 100, f"Gallery.svelte has only {len(lines)} lines — likely a stub"
    assert "<script" in src, "No <script> block — not a real Svelte component"
    assert "<style" in src, "No <style> block — not a real Svelte component"
    assert re.search(r'class=["\']', src), "No class attributes — not a real template"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and gold
# ---------------------------------------------------------------------------

_REPO_SETUP_DONE = False


def _ensure_setup():
    """Enable corepack and install dependencies (idempotent)."""
    global _REPO_SETUP_DONE
    if _REPO_SETUP_DONE:
        return
    subprocess.run(
        "corepack enable && corepack prepare pnpm@latest --activate",
        shell=True, capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    _REPO_SETUP_DONE = True


def test_repo_format_check():
    """Repo code formatting check passes (pass_to_pass)."""
    _ensure_setup()
    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_unit_tests():
    """Repo unit tests pass (pass_to_pass)."""
    _ensure_setup()
    r = subprocess.run(
        ["pnpm", "test:run"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_gallery_unit_tests():
    """Gallery component unit tests pass (pass_to_pass)."""
    _ensure_setup()
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--config", ".config/vitest.config.ts", "js/gallery/Gallery.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Gallery unit tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_client_build():
    """Client library builds successfully (pass_to_pass)."""
    _ensure_setup()
    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Client build failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_gallery_build():
    """Gallery component builds successfully (pass_to_pass)."""
    _ensure_setup()
    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/gallery", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Gallery build failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_css_generation():
    """CSS generation from theme works (pass_to_pass)."""
    _ensure_setup()
    r = subprocess.run(
        ["pnpm", "css"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"CSS generation failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
