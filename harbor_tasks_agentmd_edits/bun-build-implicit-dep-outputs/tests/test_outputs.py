"""
Task: bun-build-implicit-dep-outputs
Repo: oven-sh/bun @ c721d357ad9ed04017bb24d21decf5739dba3911
PR:   #28858

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This is a TypeScript build-system task (requires full toolchain to
actually build). Tests analyze the TypeScript source code to verify the
correct ninja dependency patterns are used.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/bun"
BUN_TS = Path(REPO) / "scripts/build/bun.ts"
COMPILE_TS = Path(REPO) / "scripts/build/compile.ts"
CLAUDE_MD = Path(REPO) / "scripts/build/CLAUDE.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_analysis(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python analysis script via subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout,
    )


def _get_section(text: str, heading: str, next_heading: str = "## ") -> str | None:
    """Extract a markdown section between two headings."""
    pat = rf"{re.escape(heading)}\s*\n(.*?)(?={re.escape(next_heading)}|\Z)"
    m = re.search(pat, text, re.DOTALL)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — source files exist and are non-empty
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_source_files_exist():
    """Modified source files must exist and be non-empty."""
    for f in [BUN_TS, COMPILE_TS, CLAUDE_MD]:
        assert f.exists(), f"{f} does not exist"
        assert f.stat().st_size > 0, f"{f} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cc_implicit_dep_outputs():
    """The compileC lambda must pass depOutputs as implicitInputs (not
    orderOnlyInputs) to cc(). This is the core fix: C files need implicit deps
    on dep outputs so ninja invalidates when dep libs change."""
    r = _run_analysis(f'''
import re, sys
text = open("{BUN_TS}").read()

# Find the compileC lambda
m = re.search(r"const compileC\s*=\s*\(src:\s*string\)\s*:\s*string\s*=>\s*{{", text)
if not m:
    print("FAIL:compileC_not_found"); sys.exit(0)
body = text[m.end():m.end()+1000]

# Must have implicitInputs: depOutputs
if not re.search(r"implicitInputs\s*:\s*depOutputs", body):
    print("FAIL:no_implicit_depOutputs"); sys.exit(0)

# Must have orderOnlyInputs: codegenOrderOnly (NOT depOrderOnly)
if not re.search(r"orderOnlyInputs\s*:\s*codegenOrderOnly", body):
    print("FAIL:no_codegenOrderOnly"); sys.exit(0)

# Must NOT have old depOrderOnly variable in the cc call
if re.search(r"depOrderOnly", body):
    print("FAIL:old_depOrderOnly_in_cc"); sys.exit(0)

print("PASS")
''')
    assert r.returncode == 0, f"Script error: {r.stderr}"
    assert "PASS" in r.stdout, f"cc() dep check failed: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_no_pch_cxx_implicit_dep_outputs():
    """In the no-PCH cxx path (else branch), opts must use implicitInputs
    with depOutputs and orderOnlyInputs with codegenOrderOnly."""
    r = _run_analysis(f'''
import re, sys
text = open("{BUN_TS}").read()

# Find the else branch for no-PCH cxx
m = re.search(r"\}}\s*else\s*\{{", text)
if not m:
    print("FAIL:no_else_branch"); sys.exit(0)

# Find the else branch that has "No PCH" comment nearby
all_else = list(re.finditer(r"\}}\s*else\s*\{{", text))
found = False
for em in all_else:
    # Check the surrounding context for no-PCH indicators
    context = text[max(0, em.start()-200):em.end()+600]
    if "No PCH" in context or "no PCH" in context or "pchOut" in context:
        body = context
        # Must have implicitInputs = depOutputs
        if re.search(r"implicitInputs\s*=\s*depOutputs", body):
            # Must have orderOnlyInputs = codegenOrderOnly
            if re.search(r"orderOnlyInputs\s*=\s*codegenOrderOnly", body):
                found = True
                break

if not found:
    print("FAIL:no_implicit_in_no_pch_path"); sys.exit(0)
print("PASS")
''')
    assert r.returncode == 0, f"Script error: {r.stderr}"
    assert "PASS" in r.stdout, f"No-PCH cxx check failed: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_codegen_order_only_separate():
    """The codegenOrderOnly variable must be just codegen.cppAll, NOT
    including depOutputs. The old code had depOrderOnly = [...depOutputs,
    ...codegen.cppAll] which lumped them together."""
    text = BUN_TS.read_text()
    # Must have the new variable name
    assert re.search(r"const codegenOrderOnly\s*=\s*codegen\.cppAll", text), \
        "codegenOrderOnly must be assigned from codegen.cppAll only"
    # Must NOT have the old depOrderOnly variable
    assert not re.search(r"const depOrderOnly", text), \
        "Old depOrderOnly variable must be removed (replaced by codegenOrderOnly)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_md_gotchas_implicit_deps():
    """scripts/build/CLAUDE.md Gotchas section must state that PCH, cc, and
    no-PCH cxx all need implicit dep on depOutputs — not just PCH."""
    text = CLAUDE_MD.read_text()
    gotchas = _get_section(text, "## Gotchas")
    assert gotchas is not None, "Gotchas section not found in CLAUDE.md"

    # Must mention all three: PCH, cc, and no-PCH cxx together
    assert re.search(r"PCH.*cc.*no-PCH cxx", gotchas) or \
           re.search(r"PCH, cc, and no-PCH cxx", gotchas), \
        "Gotchas must mention PCH, cc, and no-PCH cxx needing implicit dep"

    # Must mention "implicit dep" (not "order-only") for depOutputs
    assert re.search(r"implicit dep on `depOutputs`", gotchas), \
        "Gotchas must say 'implicit dep on depOutputs'"

    # Must NOT have the old separate rules
    assert not re.search(r"PCH needs implicit dep.*\n.*\n.*cxx needs order-only", gotchas), \
        "Old separate PCH/cxx rules must be replaced with unified rule"


# [pr_diff] fail_to_pass
def test_claude_md_ninja_primer_implicit_example():
    """The ninja primer example must show dep output (lib*.a) as an implicit
    dep (|), not order-only (||). The old example had the dep as order-only."""
    text = CLAUDE_MD.read_text()
    # Find the ninja primer section
    primer = _get_section(text, "## Ninja primer", "## Iterating")
    assert primer is not None, "Ninja primer section not found"

    # The example build line must show implicit dep on dep output
    # Pattern: | deps/zstd/libzstd.a (implicit) not || ../../vendor/zstd/.ref (order-only)
    assert re.search(r"\|\s*deps/zstd/libzstd\.a", primer) or \
           re.search(r"\|\s*\w+/zstd/libzstd\.a", primer), \
        "Ninja example must show dep output as implicit dep (|)"

    # Must NOT show the old pattern with .ref as the dep
    assert not re.search(r"\|\|\s*\.\./\.\./vendor/zstd/\.ref", primer), \
        "Old .ref order-only pattern must be removed from example"


# [pr_diff] fail_to_pass
def test_claude_md_depfile_explains_implicit():
    """The depfile explanation in CLAUDE.md must distinguish codegen headers
    (order-only) from dep outputs (implicit), explaining that local sub-builds
    rewrite forwarding headers as undeclared side effects."""
    text = CLAUDE_MD.read_text()
    # Find the depfile section
    depfile_section = None
    for m in re.finditer(r"\*\*`depfile`\*\*", text):
        # Get surrounding paragraph
        start = m.start()
        end = text.find("\n\n", start)
        if end == -1:
            end = len(text)
        depfile_section = text[start:end]
        break

    assert depfile_section is not None, "depfile section not found in CLAUDE.md"

    # Must explain dep outputs as implicit
    assert "implicit" in depfile_section.lower(), \
        "depfile section must mention implicit deps for dep outputs"

    # Must explain why: local sub-builds rewrite forwarding headers
    assert "forwarding headers" in depfile_section.lower() or \
           "undeclared side effect" in depfile_section.lower(), \
        "depfile section must explain WebKit forwarding header side effects"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_dep_outputs_comment_updated():
    """The depOutputs variable comment must describe its new purpose as
    'implicit-dep signal' not 'PCH order-only-deps'."""
    text = BUN_TS.read_text()
    assert re.search(r"implicit-dep signal", text), \
        "depOutputs comment must mention 'implicit-dep signal'"
    assert not re.search(r"PCH order-only-deps on these", text), \
        "Old 'PCH order-only-deps' comment must be removed"


# [pr_diff] pass_to_pass
def test_compile_opts_docs_updated():
    """compile.ts CompileOpts.implicitInputs doc must mention dep outputs
    (lib*.a) as the invalidation signal. orderOnlyInputs doc must redirect
    dep outputs to implicitInputs."""
    text = COMPILE_TS.read_text()
    # implicitInputs must mention dep outputs
    assert re.search(r"implicitInputs.*dep outputs|dep outputs.*implicitInputs", text, re.DOTALL) or \
           re.search(r"lib\*\.a.*invalidation signal", text) or \
           re.search(r"dep outputs.*\n.*invalidation signal", text), \
        "implicitInputs doc must mention dep outputs / lib*.a invalidation signal"

    # orderOnlyInputs must say "codegen headers" not "dep outputs"
    m = re.search(r"orderOnlyInputs.*?(?=\n\s*/\*\*|\n\s*\})", text, re.DOTALL)
    if m:
        section = m.group(0)
        assert "codegen" in section.lower() or \
               re.search(r"implicitInputs instead", section), \
            "orderOnlyInputs doc must redirect dep outputs to implicitInputs"


# [static] pass_to_pass
def test_not_stub():
    """emitBun must have substantial implementation (not just pass/return).
    Verify the function has real logic with control flow and multiple calls."""
    text = BUN_TS.read_text()
    m = re.search(r"export function emitBun\b", text)
    assert m, "emitBun function not found"

    # Extract function body (up to next export function or end of file)
    body_start = text.index("{", m.start())
    brace_count = 0
    body_end = body_start
    for i in range(body_start, min(body_start + 50000, len(text))):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                body_end = i + 1
                break

    body = text[body_start:body_end]
    real_lines = [l for l in body.split("\n")
                  if l.strip() and not l.strip().startswith("//")
                  and l.strip() not in ("{", "}", "};")]

    assert len(real_lines) >= 50, f"emitBun has only {len(real_lines)} real lines, need >= 50"
    assert "const " in body, "emitBun must have variable declarations"
    assert "cc(" in body or "cxx(" in body, "emitBun must call cc/cxx compile functions"
