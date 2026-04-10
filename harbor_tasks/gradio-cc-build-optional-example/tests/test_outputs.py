"""
Task: gradio-cc-build-optional-example
Repo: gradio @ d815881739689f45f5387ea52cc92e2cddf8adcf
PR:   13182

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/gradio"
BUILD_TS = f"{REPO}/js/preview/src/build.ts"


def _eval_exports_construction(pkg_js_literal: str) -> subprocess.CompletedProcess:
    """
    Extract the exports array construction from build.ts, strip the TS type
    annotation, and evaluate it inside Node.js with mock helpers and the
    supplied ``pkg`` object.  Returns the subprocess result; stdout contains
    the JSON-serialised exports array on success.
    """
    script = (
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync('{BUILD_TS}', 'utf-8');\n"
        "\n"
        "const startIdx = src.indexOf('const exports');\n"
        "const endIdx   = src.indexOf('for (const [out_path', startIdx);\n"
        "if (startIdx < 0 || endIdx < 0) {\n"
        "    console.error('Cannot find exports construction block in build.ts');\n"
        "    process.exit(2);\n"
        "}\n"
        "\n"
        "let code = src.substring(startIdx, endIdx).trim();\n"
        "// Strip TS type annotation: `: (string | any)[][]`\n"
        "code = code.replace(/:\\s*\\([^)]+\\)\\[\\]\\[\\]\\s*=/, ' =');\n"
        "\n"
        "const fn = new Function(\n"
        "    'join', '__dirname', 'source_dir', 'template_dir', 'pkg',\n"
        "    code + '\\nreturn exports;'\n"
        ");\n"
        "\n"
        "const join = (...a) => a.join('/');\n"
        f"const pkg  = {pkg_js_literal};\n"
        "\n"
        "const result = fn(join, '/mock-dir', '/mock-src', '/mock-tpl', pkg);\n"
        "console.log(JSON.stringify(result));\n"
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", dir="/tmp", delete=False
    ) as f:
        f.write(script)
        tmp = f.name
    try:
        return subprocess.run(["node", tmp], capture_output=True, timeout=30)
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """build.ts must exist and contain the expected function signature."""
    src = Path(BUILD_TS).read_text()
    assert len(src) > 100, "build.ts is too short or empty"
    assert "export async function make_build" in src, (
        "make_build function signature not found in build.ts"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_missing_example_no_crash():
    """Exports construction must not crash when ./example is absent."""
    pkg = '{ exports: { ".": { gradio: "index.svelte" } } }'
    r = _eval_exports_construction(pkg)
    assert r.returncode == 0, (
        f"build.ts crashes when ./example is missing from package.json:\n"
        f"{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_missing_example_one_entry():
    """When ./example is absent the exports array must have exactly 1 entry."""
    pkg = '{ exports: { ".": { gradio: "comp.svelte" } } }'
    r = _eval_exports_construction(pkg)
    assert r.returncode == 0, f"Crashed: {r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert len(result) == 1, (
        f"Expected 1 export entry (component only) but got {len(result)}: {result}"
    )


# [pr_diff] fail_to_pass
def test_null_example_no_crash():
    """Exports construction must not crash when ./example is null."""
    pkg = '{ exports: { ".": { gradio: "index.svelte" }, "./example": null } }'
    r = _eval_exports_construction(pkg)
    assert r.returncode == 0, (
        f"build.ts crashes when ./example is null:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_example_present_two_entries():
    """When ./example IS present the exports array must have 2 entries."""
    pkg = (
        '{ exports: { ".": { gradio: "index.svelte" },'
        ' "./example": { gradio: "example.svelte" } } }'
    )
    r = _eval_exports_construction(pkg)
    assert r.returncode == 0, f"Crashed: {r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert len(result) == 2, (
        f"Expected 2 export entries but got {len(result)}: {result}"
    )


# [static] pass_to_pass
def test_build_function_not_stub():
    """make_build must contain real build logic (vite build call)."""
    src = Path(BUILD_TS).read_text()
    assert "make_build" in src, "make_build function not found"
    assert "build(" in src, "make_build must still call vite build()"
    assert "pkg.exports" in src, "make_build must reference pkg.exports"
    fn_start = src.index("make_build")
    assert len(src[fn_start:]) > 200, "make_build function body is suspiciously short"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD verification
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # pnpm install
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"
    # format check
    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_preview_build():
    """Repo's @gradio/preview package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # pnpm install
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"
    # preview package build
    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/preview", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Preview package build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_client_build():
    """Repo's @gradio/client package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # pnpm install
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"
    # client package build
    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Client package build failed:\n{r.stderr[-500:]}"



# [repo_tests] pass_to_pass
def test_repo_install_frozen_lockfile():
    """Repo's pnpm lockfile is valid and installable (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install --frozen-lockfile failed:\\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_node_syntax_check():
    """Modified build.ts has valid Node.js syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", BUILD_TS],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Node.js syntax check failed:\\n{r.stderr[-500:]}"
