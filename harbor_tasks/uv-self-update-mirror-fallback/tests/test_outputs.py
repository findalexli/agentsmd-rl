"""
Task: uv-self-update-mirror-fallback
Repo: astral-sh/uv @ 7228ad62b9de7f9b5d887ef4b2be9bb033a04191
PR:   14936

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Rust code — no cargo/compiler in the Docker image. Tests use
subprocess.run() to execute Python analysis that parses the Rust
source and verifies the behavioral fix (mirror URL + fallback logic).
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/uv"
FILE = Path(REPO) / "crates/uv-bin-install/src/lib.rs"


def _stripped_source() -> str:
    """Return file source with comments removed (prevents keyword-stuffing)."""
    src = FILE.read_text(encoding="utf-8")
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src


def _extract_fn(src: str, name: str) -> str | None:
    """Extract a function body (from 'fn <name>' to its closing brace)."""
    pat = re.compile(r"fn\s+" + re.escape(name) + r"\s*[\(<]")
    m = pat.search(src)
    if not m:
        return None
    try:
        start = src.index("{", m.start())
    except ValueError:
        return None
    depth = 0
    in_string = False
    escape_next = False
    for i in range(start, len(src)):
        c = src[i]
        if escape_next:
            escape_next = False
            continue
        if c == "\\" and in_string:
            escape_next = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        if depth == 0:
            return src[m.start() : i + 1]
    return None


def _extract_match_arm(fn_body: str | None, arm_name: str) -> str | None:
    """Extract a single match arm, string-aware."""
    if fn_body is None:
        return None
    idx = fn_body.find(arm_name)
    if idx < 0:
        return None
    rest = fn_body[idx:]
    arrow = rest.find("=>")
    if arrow < 0:
        return None
    brace_depth = 0
    bracket_depth = 0
    paren_depth = 0
    in_string = False
    escape_next = False
    for i in range(arrow + 2, len(rest)):
        c = rest[i]
        if escape_next:
            escape_next = False
            continue
        if c == "\\" and in_string:
            escape_next = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == "{":
            brace_depth += 1
        elif c == "}":
            brace_depth -= 1
            if brace_depth < 0:
                return rest[:i]
        elif c == "[":
            bracket_depth += 1
        elif c == "]":
            bracket_depth -= 1
        elif c == "(":
            paren_depth += 1
        elif c == ")":
            paren_depth -= 1
        elif (
            c == ","
            and brace_depth == 0
            and bracket_depth == 0
            and paren_depth == 0
        ):
            return rest[: i + 1]
    return rest


def _variant_maps_to_true(fn_body: str, variant: str) -> bool:
    """Check if a Self::<variant> pattern leads to => true in a match expr."""
    lines = fn_body.split("\n")
    for i, line in enumerate(lines):
        if variant in line:
            window = "\n".join(lines[max(0, i - 6) : i + 10])
            if re.search(r"=>\s*true", window):
                return True
    return False


# ---------------------------------------------------------------------------
# Analysis scripts for subprocess execution (behavioral verification)
# Using % substitution instead of .format() to avoid brace conflicts
# ---------------------------------------------------------------------------

_MANIFEST_URLS_TEMPLATE = """
import json
import re

FILE = %(file_path)r


def analyze():
    src = open(FILE, encoding="utf-8").read()
    # Strip comments
    src = re.sub(r"/\\*.*?\\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\\n]*", "", src)

    # Find manifest_urls function
    m = re.search(r"fn\\s+manifest_urls\\s*[\\(<]", src)
    if not m:
        return {"error": "manifest_urls function not found"}

    # Extract function body with brace matching
    start = src.index("{", m.start())
    depth = 0
    in_str = False
    esc = False
    end = start
    for i in range(start, len(src)):
        c = src[i]
        if esc:
            esc = False
            continue
        if c == "\\\\" and in_str:
            esc = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        if depth == 0:
            end = i + 1
            break

    fn_body = src[m.start():end]

    # Extract Self::Uv arm
    idx = fn_body.find("Self::Uv")
    if idx < 0:
        return {"error": "Self::Uv arm not found"}

    rest = fn_body[idx:]
    arrow = rest.find("=>")
    if arrow < 0:
        return {"error": "No => in Self::Uv arm"}

    # Parse arm body to find where it ends
    bd = 0
    bkd = 0
    pd = 0
    in_s = False
    esc2 = False
    arm_end = len(rest)
    for i in range(arrow + 2, len(rest)):
        c = rest[i]
        if esc2:
            esc2 = False
            continue
        if c == "\\\\" and in_s:
            esc2 = True
            continue
        if c == '"':
            in_s = not in_s
            continue
        if in_s:
            continue
        if c == "{":
            bd += 1
        elif c == "}":
            bd -= 1
            if bd < 0:
                arm_end = i
                break
        elif c == "[":
            bkd += 1
        elif c == "]":
            bkd -= 1
        elif c == "(":
            pd += 1
        elif c == ")":
            pd -= 1
        elif c == "," and bd == 0 and bkd == 0 and pd == 0:
            arm_end = i + 1
            break

    uv_arm = rest[:arm_end]

    # Analyze URL construction
    has_mirror = bool(re.search(r"format!\\s*\\([^)]*VERSIONS_MANIFEST_MIRROR", uv_arm))
    has_canonical = bool(re.search(r"format!\\s*\\([^)]*VERSIONS_MANIFEST_URL\\b", uv_arm))

    mirror_pos = -1
    canonical_pos = -1
    mm = re.search(r"format!\\s*\\([^)]*VERSIONS_MANIFEST_MIRROR", uv_arm)
    mc = re.search(r"format!\\s*\\([^)]*VERSIONS_MANIFEST_URL\\b", uv_arm)
    if mm:
        mirror_pos = mm.start()
    if mc:
        canonical_pos = mc.start()

    parse_calls = len(re.findall(r"parse\\s*\\(\\s*&?\\s*format!\\s*\\(", uv_arm))
    non_blank = len([l for l in uv_arm.split("\\n") if l.strip()])

    # Additional check: look for vec! macro with multiple elements
    vec_elements = len(re.findall(r"DisplaySafeUrl::parse\\s*\\(", uv_arm))

    return {
        "has_mirror": has_mirror,
        "has_canonical": has_canonical,
        "mirror_before_canonical": mirror_pos < canonical_pos if mirror_pos >= 0 and canonical_pos >= 0 else False,
        "parse_call_count": parse_calls,
        "non_blank_lines": non_blank,
        "url_element_count": vec_elements,
    }


if __name__ == "__main__":
    result = analyze()
    print(json.dumps(result))
"""

# Use % formatting to avoid brace conflicts with Rust code
_MANIFEST_URLS_SCRIPT = _MANIFEST_URLS_TEMPLATE % {"file_path": str(FILE)}


_FALLBACK_TEMPLATE = """
import json
import re

FILE = %(file_path)r


def analyze():
    src = open(FILE, encoding="utf-8").read()
    src = re.sub(r"/\\*.*?\\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\\n]*", "", src)

    # Find should_try_next_url function
    m = re.search(r"fn\\s+should_try_next_url\\s*[\\(<]", src)
    if not m:
        return {"error": "should_try_next_url function not found"}

    start = src.index("{", m.start())
    depth = 0
    in_str = False
    esc = False
    end = start
    for i in range(start, len(src)):
        c = src[i]
        if esc:
            esc = False
            continue
        if c == "\\\\" and in_str:
            esc = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        if depth == 0:
            end = i + 1
            break

    fn_body = src[m.start():end]

    # Check which error variants map to => true
    # Pattern: Self::Variant {..} | Self::Variant(..) => true
    variants_to_check = ["ManifestParse", "ManifestUtf8", "Download", "ManifestFetch", "Stream"]
    results = {}
    lines = fn_body.split("\\n")

    for variant in variants_to_check:
        present = bool(re.search(r"\\b" + variant + r"\\b", fn_body))
        maps_true = False
        if present:
            for i, line in enumerate(lines):
                if variant in line:
                    window = "\\n".join(lines[max(0, i - 6) : i + 10])
                    if re.search(r"=>\\s*true", window):
                        maps_true = True
                        break
        results[variant] = {"present": present, "maps_to_true": maps_true}

    return results


if __name__ == "__main__":
    result = analyze()
    print(json.dumps(result))
"""

_FALLBACK_SCRIPT = _FALLBACK_TEMPLATE % {"file_path": str(FILE)}


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------


def test_uv_mirror_url():
    """Binary::Uv manifest_urls arm constructs URL from VERSIONS_MANIFEST_MIRROR.

    Before fix: Uv arm only used VERSIONS_MANIFEST_URL (GitHub only)
    After fix: Uv arm uses VERSIONS_MANIFEST_MIRROR first, then GitHub
    """
    r = subprocess.run(
        ["python3", "-c", _MANIFEST_URLS_SCRIPT],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, data.get("error", "")
    assert data["has_mirror"], (
        "Uv arm does not construct URL with VERSIONS_MANIFEST_MIRROR"
    )


def test_uv_mirror_order():
    """Binary::Uv lists mirror URL before canonical GitHub URL.

    Before fix: Uv arm had no mirror URL
    After fix: Uv arm has mirror URL first, then canonical URL
    """
    r = subprocess.run(
        ["python3", "-c", _MANIFEST_URLS_SCRIPT],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, data.get("error", "")
    assert data["has_mirror"] and data["has_canonical"], (
        f"Uv arm missing mirror ({data['has_mirror']}) or canonical ({data['has_canonical']})"
    )
    assert data["mirror_before_canonical"], (
        "Mirror URL must appear before canonical URL (fallback order matters)"
    )


def test_manifest_parse_fallback():
    """ManifestParse errors trigger URL fallback in should_try_next_url.

    Before fix: should_try_next_url didn't check ManifestParse
    After fix: ManifestParse errors return true (try next URL)
    """
    r = subprocess.run(
        ["python3", "-c", _FALLBACK_SCRIPT],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, data.get("error", "")
    mp = data["ManifestParse"]
    assert mp["present"], "ManifestParse not referenced in should_try_next_url"
    assert mp["maps_to_true"], "ManifestParse does not trigger fallback (should return true)"


def test_manifest_utf8_fallback():
    """ManifestUtf8 errors trigger URL fallback in should_try_next_url.

    Before fix: should_try_next_url didn't check ManifestUtf8
    After fix: ManifestUtf8 errors return true (try next URL)
    """
    r = subprocess.run(
        ["python3", "-c", _FALLBACK_SCRIPT],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, data.get("error", "")
    mu = data["ManifestUtf8"]
    assert mu["present"], "ManifestUtf8 not referenced in should_try_next_url"
    assert mu["maps_to_true"], "ManifestUtf8 does not trigger fallback (should return true)"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks (inline OK for p2p)
# ---------------------------------------------------------------------------


def test_ruff_urls_intact():
    """Binary::Ruff still has both mirror and canonical URLs in manifest_urls.

    The fix should not break Ruff's existing mirror+canonical URL setup.
    """
    src = _stripped_source()
    manifest_fn = _extract_fn(src, "manifest_urls")
    assert manifest_fn is not None, "manifest_urls function not found"

    ruff_arm = _extract_match_arm(manifest_fn, "Self::Ruff")
    assert ruff_arm is not None, "Self::Ruff arm not found"
    assert re.search(r"VERSIONS_MANIFEST_MIRROR", ruff_arm), (
        "Ruff arm missing mirror URL (regression)"
    )
    assert re.search(r"VERSIONS_MANIFEST_URL\b", ruff_arm), (
        "Ruff arm missing canonical URL (regression)"
    )


def test_existing_fallback_intact():
    """Download and ManifestFetch still trigger fallback in should_try_next_url.

    The fix adds new variants but should not break existing fallback logic.
    """
    src = _stripped_source()
    fallback_fn = _extract_fn(src, "should_try_next_url")
    assert fallback_fn is not None, "should_try_next_url function not found"

    for variant in ["Download", "ManifestFetch"]:
        assert re.search(rf"\b{variant}\b", fallback_fn), (
            f"{variant} not in should_try_next_url (regression)"
        )
        assert _variant_maps_to_true(fallback_fn, variant), (
            f"{variant} does not map to true (regression)"
        )


def test_stream_fallback_intact():
    """Stream errors still trigger fallback in should_try_next_url.

    The fix should preserve Stream error fallback behavior.
    """
    src = _stripped_source()
    fallback_fn = _extract_fn(src, "should_try_next_url")
    assert fallback_fn is not None, "should_try_next_url function not found"

    assert re.search(r"\bStream\b", fallback_fn), (
        "Stream not in should_try_next_url (regression)"
    )
    assert _variant_maps_to_true(fallback_fn, "Stream"), (
        "Stream does not map to true (regression)"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------


def test_no_panic_unreachable():
    """No panic! or unreachable! in manifest_urls or should_try_next_url.

    CLAUDE.md line 7: AVOID using panic!, unreachable!, .unwrap(), unsafe code
    """
    src = _stripped_source()
    for fn_name in ["manifest_urls", "should_try_next_url"]:
        fn_body = _extract_fn(src, fn_name)
        assert fn_body is not None, f"{fn_name} function not found"
        assert not re.search(r"\bpanic!\b", fn_body), (
            f"{fn_name} contains panic! (violates CLAUDE.md)"
        )
        assert not re.search(r"\bunreachable!\b", fn_body), (
            f"{fn_name} contains unreachable! (violates CLAUDE.md)"
        )


def test_no_unsafe_blocks():
    """No unsafe code in manifest_urls or should_try_next_url.

    CLAUDE.md line 7: AVOID unsafe code
    """
    src = _stripped_source()
    for fn_name in ["manifest_urls", "should_try_next_url"]:
        fn_body = _extract_fn(src, fn_name)
        assert fn_body is not None, f"{fn_name} function not found"
        assert not re.search(r"\bunsafe\s*\{", fn_body), (
            f"{fn_name} contains unsafe block (violates CLAUDE.md)"
        )


def test_no_allow_attribute():
    """No #[allow()] in modified functions — prefer #[expect()].

    CLAUDE.md line 10: PREFER #[expect()] over #[allow()]
    """
    src = _stripped_source()
    for fn_name in ["manifest_urls", "should_try_next_url"]:
        fn_body = _extract_fn(src, fn_name)
        assert fn_body is not None, f"{fn_name} function not found"
        assert not re.search(r"#\[allow\(", fn_body), (
            f"{fn_name} uses #[allow()] — prefer #[expect()] per CLAUDE.md"
        )


# ---------------------------------------------------------------------------
# Anti-stub (static) — behavioral verification
# ---------------------------------------------------------------------------


def test_uv_arm_not_stub():
    """Binary::Uv arm is a real implementation, not a stub.

    Stubs have very few lines. Real implementation has multiple URL
    entries and proper structure.
    """
    r = subprocess.run(
        ["python3", "-c", _MANIFEST_URLS_SCRIPT],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, data.get("error", "")
    assert data["parse_call_count"] >= 2, (
        f"Uv arm has {data['parse_call_count']} parse(format!()) calls, need >= 2 (stub?)"
    )
    assert data["non_blank_lines"] >= 4, (
        f"Uv arm has {data['non_blank_lines']} non-blank lines, need >= 4 (stub?)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and gold
# ---------------------------------------------------------------------------


def test_repo_ruff_check():
    """Repo's Python code passes ruff linting (pass_to_pass).

    Runs: ruff check .
    Origin: .github/workflows/check-lint.yml
    """
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "check", "."],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Repo's Python code passes ruff format check (pass_to_pass).

    Runs: ruff format --check .
    Origin: .github/workflows/check-fmt.yml
    """
    r = subprocess.run(
        ["pip", "install", "-q", "ruff"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "format", "--check", "."],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_typos():
    """Repo passes typos spell check (pass_to_pass).

    Runs: typos
    Origin: .github/workflows/check-lint.yml
    """
    r = subprocess.run(
        ["pip", "install", "-q", "typos"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install typos: {r.stderr}"

    r = subprocess.run(
        ["/usr/local/bin/typos"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Typos check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_validate_pyproject():
    """Repo's pyproject.toml passes validation (pass_to_pass).

    Runs: validate-pyproject pyproject.toml
    Origin: .github/workflows/check-lint.yml
    """
    r = subprocess.run(
        ["pip", "install", "-q", "validate-pyproject"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install validate-pyproject: {r.stderr}"

    r = subprocess.run(
        ["validate-pyproject", f"{REPO}/pyproject.toml"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"pyproject.toml validation failed:\n{r.stdout}\n{r.stderr}"
