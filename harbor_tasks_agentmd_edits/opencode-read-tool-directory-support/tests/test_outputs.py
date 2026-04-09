"""
Task: opencode-read-tool-directory-support
Repo: anomalyco/opencode @ e3471526f4c71b2c4ee00117e125e179da01e6e2
PR:   13090

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/opencode"

READ_TS = Path(REPO) / "packages" / "opencode" / "src" / "tool" / "read.ts"
READ_TXT = Path(REPO) / "packages" / "opencode" / "src" / "tool" / "read.txt"
EDIT_TXT = Path(REPO) / "packages" / "opencode" / "src" / "tool" / "edit.txt"
SKILL_MD = Path(REPO) / ".opencode" / "skill" / "bun-file-io" / "SKILL.md"


def _run_bun(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Bun script in the repo context."""
    script_path = Path(REPO) / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["bun", "run", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ts_balanced_braces():
    """Modified TypeScript files must have balanced braces and parentheses."""
    for filepath in [READ_TS]:
        text = filepath.read_text()
        assert len(text) > 100, f"{filepath.name} appears empty"
        brace_depth = 0
        paren_depth = 0
        in_string = None
        prev = ""
        for ch in text:
            if in_string:
                if ch == in_string and prev != "\\":
                    in_string = None
            elif ch in ('"', "'", "`"):
                in_string = ch
            elif ch == "{":
                brace_depth += 1
            elif ch == "}":
                brace_depth -= 1
            elif ch == "(":
                paren_depth += 1
            elif ch == ")":
                paren_depth -= 1
            prev = ch
        assert brace_depth == 0, (
            f"{filepath.name} has unbalanced braces (depth={brace_depth})"
        )
        assert paren_depth == 0, (
            f"{filepath.name} has unbalanced parens (depth={paren_depth})"
        )


# [agent_config] pass_to_pass — .opencode/skill/bun-file-io/SKILL.md:28 @ e3471526
def test_bun_api_convention():
    """Modified code uses Bun.file() API per SKILL.md convention."""
    src = READ_TS.read_text()
    assert "Bun.file(filepath)" in src, (
        "read.ts should use Bun.file() API per SKILL.md "
        "'Prefer Bun APIs over Node fs for file access' rule"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_stat_based_existence():
    """read.ts must use stat() not exists() for file/dir existence detection."""
    result = _run_bun("""
import * as fs from "node:fs/promises"
import * as os from "node:os"
import * as path from "node:path"

// Demonstrate the bug: Bun.file().exists() returns false for directories
const tmp = await fs.mkdtemp(path.join(os.tmpdir(), "eval-"))
try {
    const bunExists = await Bun.file(tmp).exists()
    if (bunExists) {
        // If Bun fixed this upstream, the test concept still holds
        console.log("NOTE: Bun.file().exists() now works for dirs")
    }

    // stat() correctly detects directories
    const stat = await Bun.file(tmp).stat().catch(() => undefined)
    if (!stat || !stat.isDirectory()) {
        console.error("FAIL: stat() should detect directory")
        process.exit(1)
    }

    // Verify read.ts uses stat-based approach
    const src = await Bun.file("packages/opencode/src/tool/read.ts").text()
    if (src.includes("await file.exists()")) {
        console.error("FAIL: read.ts still uses file.exists() which fails for directories")
        process.exit(1)
    }
    if (!src.includes("file.stat()")) {
        console.error("FAIL: read.ts should use file.stat() for existence check")
        process.exit(1)
    }

    console.log("PASS")
} finally {
    await fs.rm(tmp, { recursive: true })
}
""")
    assert result.returncode == 0, (
        f"Stat-based existence check failed:\n{result.stdout}\n{result.stderr}"
    )


# [pr_diff] fail_to_pass
def test_directory_listing_branch():
    """read.ts must have directory listing code with readdir, sorting, and XML output."""
    result = _run_bun("""
import * as fs from "node:fs/promises"
import * as os from "node:os"
import * as path from "node:path"

// Create a test directory to exercise the listing logic
const tmp = await fs.mkdtemp(path.join(os.tmpdir(), "eval-"))
await fs.mkdir(path.join(tmp, "subdir"))
await Bun.write(path.join(tmp, "alpha.txt"), "hello")
await Bun.write(path.join(tmp, "beta.txt"), "world")

try {
    // Verify readdir + sort produces expected listing (same logic as read.ts)
    const dirents = await fs.readdir(tmp, { withFileTypes: true })
    const entries = await Promise.all(
        dirents.map(async (dirent) => {
            if (dirent.isDirectory()) return dirent.name + "/"
            return dirent.name
        })
    )
    entries.sort((a, b) => a.localeCompare(b))

    if (entries.length !== 3) {
        console.error("FAIL: Expected 3 entries, got " + entries.length)
        process.exit(1)
    }
    if (entries[0] !== "alpha.txt" || entries[2] !== "subdir/") {
        console.error("FAIL: Unexpected sort order: " + JSON.stringify(entries))
        process.exit(1)
    }

    // Verify read.ts has this directory listing implementation
    const src = await Bun.file("packages/opencode/src/tool/read.ts").text()

    const checks = [
        ["readdir(filepath", "readdir call for directory listing"],
        ["entries.sort(", "sorted directory entries"],
        ["<type>directory</type>", "directory type in XML output"],
        ['dirent.name + "/"', "trailing slash for subdirectories"],
        ["entries.slice(offset", "offset pagination for directory listing"],
    ]

    for (const [pattern, desc] of checks) {
        if (!src.includes(pattern)) {
            console.error("FAIL: Missing " + desc + " (pattern: " + pattern + ")")
            process.exit(1)
        }
    }

    console.log("PASS: directory listing logic verified")
} finally {
    await fs.rm(tmp, { recursive: true })
}
""")
    assert result.returncode == 0, (
        f"Directory listing check failed:\n{result.stdout}\n{result.stderr}"
    )


# [pr_diff] fail_to_pass
def test_output_format_modernized():
    """Read output must use 'N: line' format and <content>/<path>/<type> XML tags."""
    src = READ_TS.read_text()

    # Line format: old = padStart(5, "0") + "| ", new = "N: "
    assert 'padStart(5' not in src, (
        "read.ts still uses old zero-padded line number format"
    )
    assert '${index + offset + 1}: ${line}' in src, (
        "read.ts should use 'N: line' format with colon separator"
    )

    # XML tags: old = <file>...</file>, new = <content>/<path>/<type>
    assert "<content>" in src, "read.ts should use <content> tag"
    assert "</content>" in src, "read.ts should use </content> closing tag"
    assert "<path>" in src, "read.ts should use <path> tag for filepath"
    assert "<type>file</type>" in src, "read.ts should output file type tag"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_directory_note():
    """SKILL.md must document that Bun.file().exists() returns false for directories."""
    content = SKILL_MD.read_text()
    content_lower = content.lower()

    # Must mention the exists() + directory gotcha
    assert "exists()" in content, (
        "SKILL.md should mention exists() in context of directory handling"
    )
    assert "directory" in content_lower, (
        "SKILL.md should mention directories in the context of exists()"
    )
    assert "false" in content_lower, (
        "SKILL.md should state that exists() returns false for directories"
    )


# [pr_diff] fail_to_pass
def test_read_txt_directory_support():
    """read.txt must describe directory reading capability."""
    content = READ_TXT.read_text()
    content_lower = content.lower()

    # Must mention directory support (not present in base version)
    assert "directory" in content_lower or "directories" in content_lower, (
        "read.txt should mention directory support"
    )

    # Must describe the new line format with colon
    assert ": " in content, (
        "read.txt should describe the colon-based line number format"
    )

    # Should NOT reference old cat -n format
    assert "cat -n" not in content_lower, (
        "read.txt should not reference old cat -n format"
    )


# [pr_diff] fail_to_pass
def test_edit_txt_line_format():
    """edit.txt must reference the new line number format (colon + space)."""
    content = EDIT_TXT.read_text()

    # New format reference: "line number + colon + space"
    assert "colon" in content.lower() or "`: `" in content or "`1: `" in content, (
        "edit.txt should describe the new line number format using colon"
    )

    # Old format reference should be gone
    assert "spaces + line number + tab" not in content, (
        "edit.txt still has old 'spaces + line number + tab' format description"
    )
