import json
import os
import subprocess
import tempfile


REPO = "/workspace/openai-agents-js"


def _run_node_script(script, timeout=30):
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(suffix=".mjs", text=True)
        os.write(fd, script.encode("utf-8"))
        os.close(fd)
        return subprocess.run(
            ["node", tmp], capture_output=True, text=True, timeout=timeout
        )
    finally:
        if tmp:
            os.unlink(tmp)


# ---------------------------------------------------------------------------
# F2P tests
# ---------------------------------------------------------------------------


def test_validate_shape_accepts_major():
    """The changeset-validation-result.mjs script accepts 'major' as required_bump."""
    result_script = os.path.join(
        REPO,
        ".codex/skills/changeset-validation/scripts/changeset-validation-result.mjs",
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as fh:
        json.dump(
            {"ok": True, "errors": [], "warnings": [], "required_bump": "major"},
            fh,
        )
        json_path = fh.name
    try:
        r = subprocess.run(
            ["node", result_script, json_path],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"Script rejected 'major' bump (rc={r.returncode}):\n"
            f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
        )
    finally:
        os.unlink(json_path)


def test_schema_accepts_major():
    """JSON schema enum for required_bump includes 'major'."""
    schema_path = os.path.join(REPO, ".github/codex/schemas/changeset-validation.json")
    with open(schema_path) as fh:
        schema = json.load(fh)
    enum_vals = schema["properties"]["required_bump"]["enum"]
    assert "major" in enum_vals, f"enum={enum_vals}"
    for v in ("patch", "minor", "none"):
        assert v in enum_vals, f"missing {v} from enum={enum_vals}"
    assert len(enum_vals) == 4, (
        f"expected 4 enum values, got {len(enum_vals)}: {enum_vals}"
    )


def test_milestone_sort_ascending():
    """The milestone sort comparator sorts ascending (a - b, not b - a)."""
    src_path = os.path.join(
        REPO,
        ".codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs",
    )
    # Extract the sort comparator from the source and test it behaviorally.
    # The comparator is an arrow function inside .sort((a, b) => { ... })
    script = (
        'import { readFileSync } from "fs";\n'
        'const src = readFileSync("' + src_path + '", "utf8");\n'
        # Find the sort block: everything between .sort((a, b) => { and the matching })
        # We look for the arrow function body then extract it
        "const idx = src.indexOf('.sort((a, b) =>');\n"
        "if (idx === -1) { console.error('sort not found'); process.exit(2); }\n"
        "const rest = src.slice(idx);\n"
        # Find opening brace of the arrow body
        "const openBrace = rest.indexOf('{');\n"
        "if (openBrace === -1) { console.error('open brace not found'); process.exit(2); }\n"
        # Find matching closing brace by counting
        "let depth = 0;\n"
        "let closeBrace = -1;\n"
        "for (let i = openBrace; i < rest.length; i++) {\n"
        "  if (rest[i] === '{') depth++;\n"
        "  else if (rest[i] === '}') { depth--; if (depth === 0) { closeBrace = i; break; } }\n"
        "}\n"
        "if (closeBrace === -1) { console.error('close brace not found'); process.exit(2); }\n"
        "const body = rest.slice(openBrace + 1, closeBrace).trim();\n"
        # Build a comparator function from the extracted body
        "const comparator = new Function('a', 'b', body);\n"
        # Test with sample entries
        'const entry = (major, minor) => ({ parsed: { major, minor } });\n'
        "const items = [\n"
        "  entry(2, 0), entry(1, 5), entry(1, 0), entry(3, 1),\n"
        "].sort(comparator);\n"
        "const majors = items.map(i => i.parsed.major);\n"
        # Ascending: [1, 1, 2, 3]
        "if (JSON.stringify(majors) !== '[1,1,2,3]') {\n"
        '  console.error("FAIL: majors =", JSON.stringify(majors), "expected [1,1,2,3]");\n'
        "  process.exit(1);\n"
        "}\n"
        # Within v1: minors should be [0, 5]
        "const v1minors = items.filter(i => i.parsed.major === 1).map(i => i.parsed.minor);\n"
        "if (JSON.stringify(v1minors) !== '[0,5]') {\n"
        '  console.error("FAIL: v1 minors =", JSON.stringify(v1minors), "expected [0,5]");\n'
        "  process.exit(1);\n"
        "}\n"
        'console.log("PASS");\n'
    )
    r = _run_node_script(script)
    assert r.returncode == 0, (
        f"Milestone sort test failed (rc={r.returncode}):\n"
        f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    )


def test_milestone_handles_major_bump():
    """The milestone target selection correctly picks targets for major/minor/patch bumps."""
    src_path = os.path.join(
        REPO,
        ".codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs",
    )
    script = (
        'import { readFileSync } from "fs";\n'
        'const src = readFileSync("' + src_path + '", "utf8");\n'
        # Locate sort block and 'if (!targetEntry)' marker
        "const sortStart = src.indexOf('.sort((a, b) =>');\n"
        "const targetCheck = src.indexOf('if (!targetEntry)');\n"
        "if (sortStart === -1 || targetCheck === -1) {\n"
        "  console.error('required landmarks not found'); process.exit(2);\n"
        "}\n"
        # Find matching closing brace of the sort arrow-function body
        "const arrowBody = src.indexOf('{', sortStart);\n"
        "let depth = 0, closeBrace = -1;\n"
        "for (let i = arrowBody; i < src.length; i++) {\n"
        "  if (src[i] === '{') depth++;\n"
        "  else if (src[i] === '}') { depth--; if (depth === 0) { closeBrace = i; break; } }\n"
        "}\n"
        "if (closeBrace === -1) { console.error('sort close brace not found'); process.exit(2); }\n"
        # Skip past: }, \n, ), ; and whitespace
        "let pos = closeBrace + 1;\n"
        "while (pos < src.length && /[\\s);]/.test(src[pos])) pos++;\n"
        "const targetLogic = src.slice(pos, targetCheck).trim();\n"
        # Build a test function that runs the extracted logic
        "const fn = new Function('parsed', 'requiredBump', `\n"
        "${targetLogic}\n"
        "return targetEntry;\n"
        '`);\n'
        # Test data: ascending-sorted milestone entries
        'const make = (major, minor) => ({ parsed: { major, minor } });\n'
        "const data = [make(1, 0), make(1, 5), make(2, 0), make(2, 3)];\n"
        # patch -> lowest version in current major (1.0)
        'const rp = fn(data, "patch");\n'
        'if (!rp || rp.parsed.major !== 1 || rp.parsed.minor !== 0) {\n'
        '  console.error("FAIL patch: expected 1.0 got", rp ? JSON.stringify(rp.parsed) : "undefined");\n'
        "  process.exit(1);\n"
        "}\n"
        # minor -> second-lowest in current major (1.5)
        'const rm = fn(data, "minor");\n'
        'if (!rm || rm.parsed.major !== 1 || rm.parsed.minor !== 5) {\n'
        '  console.error("FAIL minor: expected 1.5 got", rm ? JSON.stringify(rm.parsed) : "undefined");\n'
        "  process.exit(1);\n"
        "}\n"
        # major -> first entry of next major (2.0)
        'const rM = fn(data, "major");\n'
        'if (!rM || rM.parsed.major !== 2 || rM.parsed.minor !== 0) {\n'
        '  console.error("FAIL major: expected 2.0 got", rM ? JSON.stringify(rM.parsed) : "undefined");\n'
        "  process.exit(1);\n"
        "}\n"
        # Edge case: only one major version -> major target should be undefined
        "const single = [make(1, 0), make(1, 3)];\n"
        'const rU = fn(single, "major");\n'
        "if (rU !== undefined) {\n"
        '  console.error("FAIL single-major: expected undefined got", JSON.stringify(rU.parsed));\n'
        "  process.exit(1);\n"
        "}\n"
        'console.log("PASS");\n'
    )
    r = _run_node_script(script)
    assert r.returncode == 0, (
        f"Milestone target selection test failed (rc={r.returncode}):\n"
        f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    )


# ---------------------------------------------------------------------------
# P2P tests
# ---------------------------------------------------------------------------


def test_repo_lint():
    """Repo ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True, text=True, timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Lint failed (rc={r.returncode}):\n"
        f"STDERR: {r.stderr[-800:]}\nSTDOUT: {r.stdout[-800:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_build_all_packages():
    """pass_to_pass | CI job 'test' → step 'Build all packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build all packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_check_generated_declarations():
    """pass_to_pass | CI job 'test' → step 'Check generated declarations'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r -F "@openai/*" dist:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check generated declarations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_linter():
    """pass_to_pass | CI job 'test' → step 'Run linter'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run linter' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_type_check_docs_scripts():
    """pass_to_pass | CI job 'test' → step 'Type-check docs scripts'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docs:scripts:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Type-check docs scripts' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_compile_examples():
    """pass_to_pass | CI job 'test' → step 'Compile examples'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r build-check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Compile examples' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")