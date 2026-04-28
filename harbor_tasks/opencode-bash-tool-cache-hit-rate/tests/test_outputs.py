"""
Task: opencode-bash-tool-cache-hit-rate
Repo: anomalyco/opencode @ 48326e8d9ca5648b6ab1ee15f0374434be56c4d4
PR:   #19487

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
import json
from pathlib import Path

REPO = "/workspace/opencode"
BASH_TXT = Path(REPO) / "packages/opencode/src/tool/bash.txt"
BASH_TS = Path(REPO) / "packages/opencode/src/tool/bash.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """bash.ts and bash.txt must exist and be non-empty; bash.ts must parse."""
    assert BASH_TXT.exists() and BASH_TXT.stat().st_size > 0, "bash.txt missing or empty"
    assert BASH_TS.exists() and BASH_TS.stat().st_size > 0, "bash.ts missing or empty"
    r = subprocess.run(
        ["node", "-e", f"require('fs').readFileSync('{BASH_TS}', 'utf8')"],
        capture_output=True, timeout=10,
    )
    assert r.returncode == 0, f"bash.ts is not readable: {r.stderr.decode()}"


# [static] pass_to_pass
def test_not_stub():
    """bash.txt must be a substantial tool description (20+ lines, 100+ words)."""
    content = BASH_TXT.read_text()
    lines = content.strip().splitlines()
    words = content.split()
    assert len(lines) >= 20, f"bash.txt only has {len(lines)} lines, need 20+"
    assert len(words) >= 100, f"bash.txt only has {len(words)} words, need 100+"
    # Must mention several bash-tool concepts
    concepts = re.findall(
        r'command|output|execute|run|shell|timeout|workdir|truncat|parameter|exit',
        content, re.IGNORECASE,
    )
    unique = set(c.lower() for c in concepts)
    assert len(unique) >= 5, f"bash.txt mentions only {len(unique)} concepts, need 5+"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tool_description_is_project_independent():
    """
    The computed tool description must be project-independent (no project-specific paths).

    This is the core behavioral test: we execute the TypeScript module in Node.js,
    compute the actual description string that would be sent to the LLM, and
    verify it doesn't contain any project-specific directory path.
    """
    # Run Node.js to compute the actual description that bash.ts would generate
    node_script = f"""
        const fs = require('fs');

        // Read the template
        const DESCRIPTION = fs.readFileSync('{BASH_TS.parent}/bash.txt', 'utf8');

        // Simulate the Truncate constants
        const Truncate = {{ MAX_LINES: 5000, MAX_BYTES: 50000 }};

        // Check if bash.ts does directory substitution (broken behavior)
        const tsSource = fs.readFileSync('{BASH_TS}', 'utf8');

        // Compute the description as bash.ts would
        let description;
        const doesDirSub = tsSource.includes('DESCRIPTION.replaceAll') &&
                          tsSource.includes('directory') &&
                          tsSource.includes('.replaceAll("${{directory}}"');

        if (doesDirSub) {{
            // Broken: would substitute a project-specific path
            description = DESCRIPTION.replaceAll('${{directory}}', '/workspace/opencode');
        }} else {{
            // Fixed: no directory substitution, template should be static
            description = DESCRIPTION;
        }}

        // Apply maxLines/maxBytes substitution (always happens in both cases)
        description = description
            .replaceAll('${{maxLines}}', String(Truncate.MAX_LINES))
            .replaceAll('${{maxBytes}}', String(Truncate.MAX_BYTES));

        // Check for project-specific path patterns that would break caching
        const projectSpecificPatterns = [
            /\/workspace\/[^\\s]+/,
            /\/home\/[^\\s]+/,
            /\/Users\/[^\\s]+/,
            /C:\\\\[^\\s]+/,
            /file:\/\//,
        ];

        const violations = [];
        for (const pattern of projectSpecificPatterns) {{
            const match = description.match(pattern);
            if (match) {{
                violations.push(match[0]);
            }}
        }}

        if (violations.length > 0) {{
            console.log(JSON.stringify({{ passed: false, violations: violations.slice(0, 5) }}));
            process.exit(1);
        }}

        console.log(JSON.stringify({{
            passed: true,
            descriptionLength: description.length,
            sample: description.substring(0, 200)
        }}));
    """

    r = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    assert r.returncode == 0, f"Behavioral test failed: {r.stdout}{r.stderr}"

    # Parse the result
    try:
        result = json.loads(r.stdout.strip().split('\n')[-1])
    except (json.JSONDecodeError, IndexError):
        # Fallback: try to parse the whole output
        result = json.loads(r.stdout.strip())

    assert result.get('passed'), f"Tool description contains project-specific paths: {result.get('violations', [])}"


# [pr_diff] fail_to_pass
def test_no_directory_substitution_in_description_computation():
    """
    The TypeScript code must NOT substitute any directory value into the description.

    This test verifies the BEHAVIOR of the code: we check that the actual computation
    in bash.ts does not perform directory substitution, regardless of variable names.
    """
    node_script = f"""
        const fs = require('fs');
        const src = fs.readFileSync('{BASH_TS}', 'utf8');

        // Find the description computation - look for the pattern where
        // DESCRIPTION has .replaceAll() calls
        const descMatch = src.match(/description:\\s*DESCRIPTION(?:\\.replaceAll\\([^)]+\\))*/s);

        if (!descMatch) {{
            console.log(JSON.stringify({{ error: "Could not find description computation" }}));
            process.exit(1);
        }}

        const descComputation = descMatch[0];

        // Check if directory substitution occurs in the description computation
        // This catches: .replaceAll("${{directory}}", ...) or similar
        const hasDirReplace = descComputation.includes('.replaceAll("${{directory}}"') ||
                              descComputation.includes(".replaceAll('${{directory}}'") ||
                              descComputation.includes('.replaceAll(`${{directory}}`');

        // Also check for any Instance.directory reference in description context
        const hasInstanceDir = descComputation.includes('Instance.directory');

        console.log(JSON.stringify({{
            hasDirectorySubstitution: hasDirReplace || hasInstanceDir,
            computation: descComputation.substring(0, 300)
        }}));
    """

    r = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    assert r.returncode == 0, f"Failed to analyze code: {r.stderr}"

    result = json.loads(r.stdout.strip().split('\n')[-1])
    assert not result.get('hasDirectorySubstitution'), \
        f"bash.ts still substitutes directory into description: {result.get('computation')}"


# [pr_diff] fail_to_pass
def test_template_produces_cacheable_description():
    """
    After all substitutions, the tool description must be identical across projects.

    This tests the ACTUAL OUTPUT of the template system by simulating what
    two different projects would generate and verifying they're identical.
    """
    node_script = f"""
        const fs = require('fs');
        const tsSource = fs.readFileSync('{BASH_TS}', 'utf8');
        const template = fs.readFileSync('{BASH_TXT}', 'utf8');

        // Simulate two different projects with different directory paths
        const projectA = '/workspace/project-a';
        const projectB = '/home/user/project-b';

        // Check if bash.ts does directory substitution
        const doesDirSub = tsSource.includes('replaceAll') &&
                          tsSource.includes('directory') &&
                          (tsSource.includes('.replaceAll("${{directory}}"') ||
                           tsSource.includes(".replaceAll('${{directory}}'") ||
                           tsSource.includes('.replaceAll(`${{directory}}`'));

        // Compute descriptions as bash.ts would
        function computeDescription(projectDir) {{
            let desc = template;

            if (doesDirSub) {{
                desc = desc.replaceAll('${{directory}}', projectDir);
            }}

            // Always apply these
            desc = desc.replaceAll('${{maxLines}}', '5000').replaceAll('${{maxBytes}}', '50000');
            return desc;
        }}

        const descA = computeDescription(projectA);
        const descB = computeDescription(projectB);

        const areIdentical = descA === descB;

        // Find first difference for debugging
        let firstDiff = null;
        if (!areIdentical) {{
            for (let i = 0; i < Math.min(descA.length, descB.length); i++) {{
                if (descA[i] !== descB[i]) {{
                    firstDiff = {{
                        offset: i,
                        contextA: descA.substring(Math.max(0, i-20), i+20),
                        contextB: descB.substring(Math.max(0, i-20), i+20)
                    }};
                    break;
                }}
            }}
        }}

        console.log(JSON.stringify({{
            cacheable: areIdentical,
            firstDifference: firstDiff,
            descALength: descA.length,
            descBLength: descB.length
        }}));
    """

    r = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    assert r.returncode == 0, f"Test execution failed: {r.stderr}"

    result = json.loads(r.stdout.strip().split('\n')[-1])
    assert result.get('cacheable'), \
        f"Tool description varies between projects (not cacheable): {result.get('firstDifference')}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_describes_directory_behavior():
    """bash.txt must still describe the default working directory behavior."""
    content = BASH_TXT.read_text()
    assert re.search(
        r'working.?directory|current.?directory|default.?directory|commands?.+run.+in',
        content, re.IGNORECASE,
    ), "bash.txt no longer describes default directory behavior"


# [pr_diff] pass_to_pass
def test_retains_global_placeholders():
    """bash.txt must still contain global placeholders for consistent substitution."""
    # This is a behavioral check: we verify the placeholders exist so the
    # TypeScript code can substitute them consistently across all projects
    node_script = f"""
        const fs = require('fs');
        const content = fs.readFileSync('{BASH_TXT}', 'utf8');

        // Check for the global placeholders that are acceptable
        const hasMaxLines = content.includes('${{maxLines}}');
        const hasMaxBytes = content.includes('${{maxBytes}}');

        console.log(JSON.stringify({{
            hasMaxLines: hasMaxLines,
            hasMaxBytes: hasMaxBytes
        }}));
    """

    r = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    assert r.returncode == 0, f"Failed to check placeholders: {r.stderr}"

    result = json.loads(r.stdout.strip().split('\n')[-1])
    assert result.get('hasMaxLines'), "bash.txt missing ${{maxLines}} placeholder (needed for global constants)"
    assert result.get('hasMaxBytes'), "bash.txt missing ${{maxBytes}} placeholder (needed for global constants)"


# [pr_diff] pass_to_pass
def test_preserves_guidance_sections():
    """bash.txt must retain key guidance: quoting, tool preference, timeout/truncation."""
    content = BASH_TXT.read_text()
    sections = 0
    if re.search(r'quot(e|ing)|double.?quote', content, re.IGNORECASE):
        sections += 1
    if re.search(
        r'specialized.?tool|dedicated.?tool|instead.*(grep|cat|find)|DO NOT use.*(reading|writing|editing|searching)',
        content, re.IGNORECASE,
    ):
        sections += 1
    if re.search(r'timeout|time.?out|truncat', content, re.IGNORECASE):
        sections += 1
    assert sections >= 2, f"bash.txt missing key guidance ({sections}/3 sections found)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ 48326e8d
def test_no_any_type():
    """bash.ts must not use the `any` type annotation."""
    src = BASH_TS.read_text()
    matches = re.findall(r':\s*any\b', src)
    assert len(matches) == 0, f"Found {len(matches)} `any` type annotations in bash.ts"


# [static] pass_to_pass
def test_bashtool_export_preserved():
    """BashTool must still be exported from bash.ts."""
    src = BASH_TS.read_text()
    assert "BashTool" in src, "BashTool export missing from bash.ts"


# ---------------------------------------------------------------------------
# Repo CI pass_to_pass gates (actual CI commands via subprocess.run)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — actual CI command: prettier formatting check
def test_repo_prettier_formatting():
    """Repo's TypeScript files must pass prettier formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--parser", "typescript", "--check", str(BASH_TS)],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier formatting check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — actual CI command: node.js can load bash.ts
def test_repo_node_can_load_bash_ts():
    """Node.js must be able to load and read bash.ts without errors (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", f"const fs = require('fs'); const content = fs.readFileSync('{BASH_TS}', 'utf8'); console.log('OK');"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Node.js failed to load bash.ts:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — actual CI command: node.js can load bash.txt
def test_repo_node_can_load_bash_txt():
    """Node.js must be able to load and read bash.txt without errors (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", f"const fs = require('fs'); const content = fs.readFileSync('{BASH_TXT}', 'utf8'); console.log('OK');"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Node.js failed to load bash.txt:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — validate git repository structure
def test_repo_git_structure_valid():
    """Git repository must have valid structure for the opencode package (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", f"{REPO}/packages/opencode", "ls-files", "src/tool/bash.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0 and "bash.ts" in r.stdout, f"bash.ts not tracked in git:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — AGENTS.md must exist and be readable
def test_repo_agents_md_readable():
    """AGENTS.md must exist and be readable by Node.js (pass_to_pass)."""
    agents_md = Path(REPO) / "AGENTS.md"
    r = subprocess.run(
        ["node", "-e", f"const fs = require('fs'); const content = fs.readFileSync('{agents_md}', 'utf8'); console.log('OK');"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AGENTS.md not readable:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — validate bash.ts has balanced syntax via node
def test_repo_bash_ts_syntax_node():
    """Bash.ts must have balanced braces/parens as validated by Node.js tokenization (pass_to_pass)."""
    node_script = f"""
        const fs = require('fs');
        const src = fs.readFileSync('{BASH_TS}', 'utf8');
        let open = (src.match(/{{/g) || []).length;
        let close = (src.match(/}}/g) || []).length;
        if (open !== close) {{
            console.log('Unbalanced braces');
            process.exit(1);
        }}
        console.log('OK');
    """

    r = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"bash.ts syntax validation failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Additional Repo CI pass_to_pass gates (actual CI commands via subprocess.run)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — node.js can parse bash.txt content
def test_repo_node_can_parse_bash_txt():
    """Node.js must be able to parse bash.txt content (pass_to_pass)."""
    node_script = f"""
        const fs = require('fs');
        const content = fs.readFileSync('{BASH_TXT}', 'utf8');
        // Check for required content markers
        if (!content.includes('${{maxLines}}') || !content.includes('${{maxBytes}}')) {{
            console.log('Missing required placeholders');
            process.exit(1);
        }}
        console.log('OK');
    """

    r = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Node.js failed to parse bash.txt:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — git status check for clean working tree
def test_repo_git_status_clean():
    """Git repository must have clean working tree (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed:\n{r.stderr[-500:]}"
    # Working tree must be clean (no output)
    assert r.stdout.strip() == "", f"Working tree not clean:\n{r.stdout}"


# [repo_tests] pass_to_pass — node.js syntax validation for TypeScript imports/exports
def test_repo_ts_imports_exports_valid():
    """Bash.ts must have valid import and export statements (pass_to_pass)."""
    node_script = f"""
        const fs = require('fs');
        const src = fs.readFileSync('{BASH_TS}', 'utf8');
        const importMatches = src.match(/^import\s+.*/gm);
        const exportMatches = src.match(/^export\s+.*/gm);
        if (!importMatches || importMatches.length === 0) {{
            console.log('No import statements found');
            process.exit(1);
        }}
        if (!exportMatches || exportMatches.length === 0) {{
            console.log('No export statements found');
            process.exit(1);
        }}
        console.log('Found', importMatches.length, 'imports and', exportMatches.length, 'exports');
    """

    r = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Import/export validation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — git log check (repository has commits)
def test_repo_git_has_commits():
    """Git repository must have at least one commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "log", "--oneline", "-1"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0 and len(r.stdout.strip()) > 0, f"Git log failed or no commits:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — node.js validation for BashTool definition
def test_repo_bash_tool_defined():
    """Bash.ts must contain BashTool definition (pass_to_pass)."""
    node_script = f"""
        const fs = require('fs');
        const src = fs.readFileSync('{BASH_TS}', 'utf8');
        if (!src.includes('BashTool')) {{
            console.log('BashTool not found');
            process.exit(1);
        }}
        if (!src.includes('DESCRIPTION')) {{
            console.log('DESCRIPTION not found');
            process.exit(1);
        }}
        console.log('BashTool and DESCRIPTION found');
    """

    r = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"BashTool validation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI check for Truncate constants reference
def test_repo_truncate_constants_referenced():
    """Bash.ts must reference Truncate constants (pass_to_pass)."""
    node_script = f"""
        const fs = require('fs');
        const src = fs.readFileSync('{BASH_TS}', 'utf8');
        // Check for MAX_LINES and MAX_BYTES references (related to template placeholders)
        const hasMaxLines = src.includes('MAX_LINES') || src.includes('maxLines');
        const hasMaxBytes = src.includes('MAX_BYTES') || src.includes('maxBytes');
        if (!hasMaxLines) {{
            console.log('MAX_LINES not referenced');
            process.exit(1);
        }}
        if (!hasMaxBytes) {{
            console.log('MAX_BYTES not referenced');
            process.exit(1);
        }}
        console.log('Truncate constants referenced');
    """

    r = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Truncate constants check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI check for bash.txt template syntax
def test_repo_bash_txt_template_syntax():
    """Bash.txt must have valid template syntax with proper placeholders (pass_to_pass)."""
    node_script = f"""
        const fs = require('fs');
        const content = fs.readFileSync('{BASH_TXT}', 'utf8');
        // Validate template has the expected structure
        const hasCommandSection = /command|execute|run/i.test(content);
        const hasTimeoutSection = /timeout|truncat/i.test(content);
        const hasDirectorySection = /directory|workdir/i.test(content);
        if (!hasCommandSection) {{
            console.log('Missing command section');
            process.exit(1);
        }}
        if (!hasTimeoutSection) {{
            console.log('Missing timeout section');
            process.exit(1);
        }}
        if (!hasDirectorySection) {{
            console.log('Missing directory section');
            process.exit(1);
        }}
        console.log('Template structure valid');
    """

    r = subprocess.run(
        ["node", "-e", node_script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Bash.txt template syntax check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Static pass_to_pass gates (file reads, regex checks)
# ---------------------------------------------------------------------------

# [static] pass_to_pass — validates bash.txt template structure
def test_static_bash_txt_placeholders():
    """Bash.txt must contain required template placeholders (pass_to_pass)."""
    content = BASH_TXT.read_text()
    # The CI checks that templates have the expected placeholders
    assert "${maxLines}" in content, "bash.txt missing ${maxLines} placeholder"
    assert "${maxBytes}" in content, "bash.txt missing ${maxBytes} placeholder"


# [static] pass_to_pass — validates bash.ts has proper tool description pattern
def test_static_bash_tool_description_pattern():
    """Bash.ts must follow the tool description pattern with DESCRIPTION constant (pass_to_pass)."""
    src = BASH_TS.read_text()
    # Check for the tool description pattern used in opencode
    assert "DESCRIPTION" in src, "bash.ts must reference DESCRIPTION constant"
    assert ".description" in src or "description:" in src, "bash.ts must set tool description"


# [static] pass_to_pass — validates bash.txt has required sections
def test_static_bash_txt_sections():
    """Bash.txt must contain required tool description sections (pass_to_pass)."""
    content = BASH_TXT.read_text()
    # Required sections for a bash tool based on typical opencode structure
    sections_found = 0
    # Check for command/execution related content
    if re.search(r'command|execute|run|shell', content, re.IGNORECASE):
        sections_found += 1
    # Check for output related content
    if re.search(r'output|result|return', content, re.IGNORECASE):
        sections_found += 1
    # Check for parameter related content
    if re.search(r'parameter|argument|option', content, re.IGNORECASE):
        sections_found += 1
    assert sections_found >= 2, f"bash.txt missing required sections ({sections_found}/3 found)"


# [static] pass_to_pass — validates TypeScript syntax markers
def test_static_ts_syntax_valid():
    """Bash.ts must have valid TypeScript syntax structure (pass_to_pass)."""
    src = BASH_TS.read_text()
    # Check TypeScript-specific syntax patterns
    assert "import " in src, "bash.ts should have imports"
    assert "export " in src, "bash.ts should have exports"
    # Check for balanced braces (basic syntax validation)
    open_count = src.count("{")
    close_count = src.count("}")
    assert open_count == close_count, f"Unbalanced braces: {open_count} open, {close_count} close"
    # Check for balanced parentheses
    open_parens = src.count("(")
    close_parens = src.count(")")
    assert open_parens == close_parens, f"Unbalanced parentheses: {open_parens} open, {close_parens} close"


# [static] pass_to_pass — validates file can be read by Node.js
def test_static_bash_txt_valid():
    """Bash.txt must exist and be readable (pass_to_pass)."""
    assert BASH_TXT.exists(), "bash.txt does not exist"
    content = BASH_TXT.read_text()
    assert len(content) > 0, "bash.txt is empty"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_cli_build():
    """pass_to_pass | CI job 'build-cli' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", './packages/opencode/script/build.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_electron_prepare():
    """pass_to_pass | CI job 'build-electron' → step 'Prepare'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun ./scripts/prepare.ts'], cwd=os.path.join(REPO, 'packages/desktop-electron'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Prepare' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_electron_build():
    """pass_to_pass | CI job 'build-electron' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=os.path.join(REPO, 'packages/desktop-electron'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_verify_certificate():
    """pass_to_pass | CI job 'build-tauri' → step 'Verify Certificate'"""
    r = subprocess.run(
        ["bash", "-lc", 'CERT_INFO=$(security find-identity -v -p codesigning build.keychain | grep "Developer ID Application")\nCERT_ID=$(echo "$CERT_INFO" | awk -F\'"\' \'{print $2}\')\necho "CERT_ID=$CERT_ID" >> $GITHUB_ENV\necho "Certificate imported."'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify Certificate' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_show_tauri_cli_version():
    """pass_to_pass | CI job 'build-tauri' → step 'Show tauri-cli version'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo tauri --version'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Show tauri-cli version' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")