"""
Task: nextjs-turbopack-lazy-metadata-tla
Repo: vercel/next.js @ 04cc2f2ed2a2a65cf5ba78ea251be22a5f41e7c9
PR:   #91705

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"
RUST_FILE = Path(REPO) / "crates/next-core/src/app_page_loader_tree.rs"
TS_FILE = Path(REPO) / "packages/next/src/lib/metadata/resolve-metadata.ts"


def _rust_code_lines(src: str) -> list[str]:
    """Return non-comment lines from Rust source (strips // and /* */ comments)."""
    lines = []
    in_block = False
    for line in src.splitlines():
        s = line.strip()
        if in_block:
            if "*/" in s:
                in_block = False
            continue
        if s.startswith("//"):
            continue
        if "/*" in s and "*/" not in s:
            in_block = True
            continue
        # strip trailing comments
        code = re.split(r"\s*//", line, maxsplit=1)[0]
        lines.append(code)
    return lines


def _rust_code(src: str) -> str:
    return "\n".join(_rust_code_lines(src))


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_target_files_exist():
    """Both modified files must exist."""
    assert RUST_FILE.exists(), f"Missing {RUST_FILE}"
    assert TS_FILE.exists(), f"Missing {TS_FILE}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_lazy_require_wrappers():
    """Eager requires replaced with lazy arrow-function wrappers in Rust codegen.

    Base: const {id} = require(/*turbopackChunkingType: shared*/"...")
    Fix:  const {id} = () => require(/*turbopackChunkingType: shared*/"...")

    All turbopackChunkingType require patterns must be wrapped in () =>.
    """
    code = _rust_code(RUST_FILE.read_text())

    # Find all lines that assign a require with turbopackChunkingType
    # These appear inside format!() strings in the Rust source
    require_lines = [
        ln for ln in code.splitlines()
        if "require(" in ln and "turbopackChunkingType" in ln
    ]
    assert len(require_lines) >= 2, (
        f"Expected >=2 turbopackChunkingType require lines, found {len(require_lines)}"
    )

    # Every such line must have an arrow function wrapper: () => require(
    # or =>\n require( across format string lines
    for ln in require_lines:
        assert "=>" in ln and "require(" in ln, (
            f"require with turbopackChunkingType not wrapped in arrow function: {ln.strip()}"
        )

    # Verify the wrapping is specifically () => require pattern (not some other arrow)
    lazy_count = sum(
        1 for ln in require_lines
        if re.search(r"=>\s*require\(", ln)
    )
    assert lazy_count >= 2, (
        f"Expected >=2 '() => require(...)' patterns, found {lazy_count}"
    )


# [pr_diff] fail_to_pass
def test_await_lazy_loaders():
    """Generated JS must await lazy loader calls before accessing metadata.

    The fix adds patterns like:
      interopDefault(await {identifier}())
    There must be await on a function invocation (not just await props.params).
    """
    code = _rust_code(RUST_FILE.read_text())

    # Must have "await" followed by an identifier and "()" — i.e. awaiting a call
    # This pattern appears in the writeln! strings for generated JS
    await_call_matches = re.findall(r"await\s+\w+\(\)", code)
    assert len(await_call_matches) >= 2, (
        f"Expected >=2 'await <fn>()' patterns in generated code, found {len(await_call_matches)}"
    )

    # The awaited result must be passed to interopDefault
    interop_await = re.findall(r"interopDefault\s*\(\s*await\s+\w+\(\)\s*\)", code)
    assert len(interop_await) >= 2, (
        f"Expected >=2 'interopDefault(await fn())' patterns, found {len(interop_await)}"
    )


# [pr_diff] fail_to_pass
def test_no_interop_default_in_collect_static():
    """collectStaticImagesFiles must call imageModule directly, not via interopDefault.

    Base: await interopDefault(imageModule)(props)
    Fix:  await imageModule(props)
    """
    src = TS_FILE.read_text()
    fn_start = src.find("collectStaticImagesFiles")
    assert fn_start != -1, "collectStaticImagesFiles function not found"
    fn_chunk = src[fn_start:fn_start + 2000]

    # interopDefault must NOT wrap imageModule in this function
    assert not re.search(r"interopDefault\s*\(\s*imageModule", fn_chunk), (
        "imageModule is still wrapped in interopDefault"
    )
    # imageModule must be called directly with props
    assert re.search(r"imageModule\s*\(", fn_chunk), (
        "imageModule is not called as a function"
    )


# [pr_diff] fail_to_pass
def test_metadata_image_async_function():
    """Generated loader tree returns metadata images as async functions.

    Base: {identifier}.default,  (synchronous property access)
    Fix:  async (props) => interopDefault(await {identifier}())(props),
          async (props) => { const mod = interopDefault(await {identifier}()); ... }

    Must have async (props) => patterns AND no synchronous {identifier}.default access.
    """
    code = _rust_code(RUST_FILE.read_text())

    # Fix introduces "async (props) =>" in writeln!/format! strings
    async_props = re.findall(r"async\s*\(props\)\s*=>", code)
    assert len(async_props) >= 2, (
        f"Expected >=2 'async (props) =>' patterns, found {len(async_props)}"
    )

    # The buggy pattern: {identifier}.default directly accessed in writeln!/format!
    # After fix, metadata properties use 'mod.' instead of '{identifier}.default.'
    sync_default = re.findall(r"\{identifier\}\.default[,.\s]", code)
    assert len(sync_default) == 0, (
        f"Found {len(sync_default)} synchronous {{identifier}}.default accesses — "
        "these should be replaced with 'mod.' references"
    )


# [pr_diff] fail_to_pass
def test_interop_default_import_removed():
    """interopDefault import must be removed from resolve-metadata.ts.

    The fix removes: import { interopDefault } from '../interop-default'
    because the Rust-generated code now handles interop itself.
    """
    src = TS_FILE.read_text()

    # The specific import statement must not exist
    assert not re.search(
        r"""import\s*\{\s*interopDefault\s*\}\s*from\s*['"]\.\.\/interop-default['"]""",
        src,
    ), "interopDefault is still imported from '../interop-default'"

    # interopDefault must not be called anywhere in the file
    # (it was only used in collectStaticImagesFiles which now calls imageModule directly)
    assert "interopDefault" not in src, (
        "interopDefault still referenced in resolve-metadata.ts"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_collect_static_images_files_intact():
    """collectStaticImagesFiles must still exist and use Promise.all."""
    src = TS_FILE.read_text()
    assert "collectStaticImagesFiles" in src, "collectStaticImagesFiles missing"
    assert "Promise.all" in src, "Promise.all missing"


# [pr_diff] pass_to_pass
def test_rust_loader_functions_intact():
    """Key symbols in the Rust loader tree must be preserved."""
    src = RUST_FILE.read_text()
    assert "fillMetadataSegment" in src, "fillMetadataSegment missing"
    assert "get_content_type" in src, "get_content_type missing"
    count = len(re.findall(r"turbopackChunkingType", src))
    assert count >= 3, (
        f"Only {count} turbopackChunkingType annotations (need >=3 after fix adds one)"
    )


# [pr_diff] pass_to_pass
def test_all_metadata_types_handled():
    """Rust loader tree must handle all metadata types."""
    src = RUST_FILE.read_text()
    for mtype in ("icon", "apple", "openGraph", "twitter"):
        assert mtype in src, f"Missing metadata type: {mtype}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:306 @ 04cc2f2
def test_no_secrets_in_source():
    """No secret values (tokens, API keys) in modified source files."""
    for fpath in (RUST_FILE, TS_FILE):
        src = fpath.read_text()
        assert not re.search(
            r"(?:api[_-]?key|secret|token|password|credential)\s*[:=]\s*['\"][^'\"]+['\"]",
            src, re.I,
        ), f"Potential hardcoded secret found in {fpath.name}"
