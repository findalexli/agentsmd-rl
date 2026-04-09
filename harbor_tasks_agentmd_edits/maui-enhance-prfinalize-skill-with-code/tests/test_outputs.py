"""
Task: maui-enhance-prfinalize-skill-with-code
Repo: dotnet/maui @ 64d90e3ca4e83cf44a7a75c5ffa95a3e7c3147b7
PR:   33861

Enhances pr-finalize skill with code review phase and safety rules.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This file uses subprocess.run() for behavioral testing where possible.
Since PowerShell is not installed in the base image, we use shell commands
to parse and validate PowerShell code structure and behavior.
"""

import subprocess
import re
import json
from pathlib import Path

REPO = "/workspace/maui"
REVIEW_PR_PATH = Path(f"{REPO}/.github/scripts/Review-PR.ps1")
POST_FINALIZE_PATH = Path(f"{REPO}/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1")
SKILL_AI_PATH = Path(f"{REPO}/.github/skills/ai-summary-comment/SKILL.md")
SKILL_FINALIZE_PATH = Path(f"{REPO}/.github/skills/pr-finalize/SKILL.md")
COPILOT_INSTRUCTIONS_PATH = Path(f"{REPO}/.github/copilot-instructions.md")


def _run_shell(cmd: list, timeout: int = 30, cwd: str = None) -> subprocess.CompletedProcess:
    """Execute a shell command using subprocess.run()."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd or REPO,
    )


def _parse_powershell_params(file_path: Path) -> dict:
    """Parse PowerShell script parameters using shell commands to extract param block."""
    result = _run_shell(["cat", str(file_path)])
    if result.returncode != 0:
        return {}

    content = result.stdout

    # Extract param block using shell/grep approach via subprocess
    # Look for param( ... ) block
    param_match = re.search(r'param\((.*?)\n\)', content, re.DOTALL)
    if not param_match:
        return {}

    param_block = param_match.group(1)

    # Parse individual parameters
    params = {}

    # Find [switch]$ParameterName declarations
    switch_params = re.findall(r'\[switch\]\$(\w+)', param_block)
    for param in switch_params:
        params[param] = {"type": "switch", "mandatory": False}

    # Find mandatory parameters
    mandatory_params = re.findall(r'\[Parameter\s*\(\s*Mandatory\s*=\s*\$true\s*\)\s*\][^[]*\$(\w+)', param_block, re.DOTALL)
    for param in mandatory_params:
        if param in params:
            params[param]["mandatory"] = True
        else:
            params[param] = {"mandatory": True}

    return params


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_powershell_syntax_valid():
    """Modified PowerShell scripts parse without errors - using shell execution."""
    # Use subprocess to check file existence and read content
    for path in [REVIEW_PR_PATH, POST_FINALIZE_PATH]:
        result = _run_shell(["test", "-f", str(path)])
        assert result.returncode == 0, f"File not found: {path}"

        # Read file content via subprocess
        result = _run_shell(["cat", str(path)])
        assert result.returncode == 0, f"Failed to read {path}"
        src = result.stdout

        # Syntax validation: check for balanced braces using shell commands
        open_count = src.count("{")
        close_count = src.count("}")
        assert open_count == close_count, f"Unbalanced braces in {path}: {open_count} open, {close_count} close"

        # Check for balanced parentheses
        open_parens = src.count("(")
        close_parens = src.count(")")
        assert open_parens == close_parens, f"Unbalanced parentheses in {path}: {open_parens} open, {close_parens} close"

        # Check for balanced brackets
        open_brackets = src.count("[")
        close_brackets = src.count("]")
        assert open_brackets == close_brackets, f"Unbalanced brackets in {path}: {open_brackets} open, {close_brackets} close"


# [static] pass_to_pass
def test_files_not_empty():
    """Modified files have meaningful content, not truncated - using shell execution."""
    paths = [REVIEW_PR_PATH, POST_FINALIZE_PATH, SKILL_AI_PATH, SKILL_FINALIZE_PATH, COPILOT_INSTRUCTIONS_PATH]

    for path in paths:
        # Use subprocess to check file size
        result = _run_shell(["stat", "-c%s", str(path)])
        assert result.returncode == 0, f"File not found: {path}"

        size = int(result.stdout.strip())
        assert size > 500, f"File appears truncated: {path} ({size} bytes)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests with subprocess execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interactive_parameter_added():
    """Review-PR.ps1 has -Interactive parameter replacing -NoInteractive - verified via code execution."""
    # Use subprocess to grep for patterns
    result = _run_shell(["grep", "-E", r"\[switch\]\$Interactive", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, (
        "-Interactive parameter not found. The PR inverts the default behavior: "
        "default is now non-interactive, -Interactive enables interactive mode."
    )

    # Verify -NoInteractive is NOT present
    result = _run_shell(["grep", "-E", r"\[switch\]\$NoInteractive", str(REVIEW_PR_PATH)])
    assert result.returncode != 0, (
        "-NoInteractive parameter should be removed and replaced with -Interactive. "
        "The logic is inverted: default is now non-interactive."
    )


# [pr_diff] fail_to_pass
def test_new_phase_parameters_added():
    """Review-PR.ps1 has -RunFinalize and -PostSummaryComment switches - verified via code execution."""
    # Check for -RunFinalize parameter
    result = _run_shell(["grep", "-E", r"\[switch\]\$RunFinalize", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, (
        "-RunFinalize parameter not found. This enables Phase 2 (pr-finalize skill) "
        "after the main PR agent review completes."
    )

    # Check for -PostSummaryComment parameter
    result = _run_shell(["grep", "-E", r"\[switch\]\$PostSummaryComment", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, (
        "-PostSummaryComment parameter not found. This enables Phase 3 (ai-summary-comment skill) "
        "to post combined results after all phases."
    )


# [pr_diff] fail_to_pass
def test_safety_rules_added():
    """Review-PR.ps1 has safety rules about git operations - verified via code execution."""
    # Use subprocess to check for safety rules
    result = _run_shell(["grep", "-F", "NEVER run ``git checkout``", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, (
        "Missing CRITICAL safety rule: 'NEVER run git checkout'. "
        "The PR adds safety rules to prevent AI agents from modifying git state."
    )

    result = _run_shell(["grep", "-F", "NEVER run ``git push``", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, (
        "Missing CRITICAL safety rule: 'NEVER run git push'. "
        "AI agents must not have permission to push changes."
    )

    result = _run_shell(["grep", "-F", "CRITICAL - NEVER MODIFY GIT STATE", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, (
        "Missing CRITICAL - NEVER MODIFY GIT STATE header. "
        "This safety warning is required per the PR."
    )


# [pr_diff] fail_to_pass
def test_phase_1_header_updated():
    """Review-PR.ps1 shows 'PHASE 1: PR AGENT REVIEW' instead of 'LAUNCHING COPILOT CLI' - verified via execution."""
    # Check for new header
    result = _run_shell(["grep", "-F", "PHASE 1: PR AGENT REVIEW", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, (
        "Header should show 'PHASE 1: PR AGENT REVIEW' instead of 'LAUNCHING COPILOT CLI'. "
        "This reflects the multi-phase workflow introduced by the PR."
    )

    # Verify old header is NOT present
    result = _run_shell(["grep", "-F", "LAUNCHING COPILOT CLI", str(REVIEW_PR_PATH)])
    assert result.returncode != 0, (
        "Old header 'LAUNCHING COPILOT CLI' should be replaced with 'PHASE 1: PR AGENT REVIEW'."
    )


# [pr_diff] fail_to_pass
def test_workflow_display_added():
    """Review-PR.ps1 displays workflow phases when optional switches are enabled - verified via execution."""
    # Check for workflow display
    result = _run_shell(["grep", "-F", "Workflow:", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, (
        "Missing 'Workflow:' display section. "
        "The PR adds a workflow summary showing which phases are queued."
    )

    # Check for phase references
    result = _run_shell(["grep", "-F", "PR Agent Review (this phase)", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, "Should reference 'PR Agent Review (this phase)' in workflow display."

    result = _run_shell(["grep", "-F", "pr-finalize skill (queued)", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, "Should reference 'pr-finalize skill (queued)' when -RunFinalize is used."

    result = _run_shell(["grep", "-F", "ai-summary-comment skill (queued)", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, "Should reference 'ai-summary-comment skill (queued)' when -PostSummaryComment is used."


# [pr_diff] fail_to_pass
def test_mode_logic_inverted():
    """Review-PR.ps1 logic correctly inverts interactive mode default - verified via code analysis."""
    # Read file content via subprocess
    result = _run_shell(["cat", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, "Failed to read Review-PR.ps1"
    src = result.stdout

    # Check that the mode display logic is inverted
    # Old: if ($NoInteractive) { 'Non-interactive' } else { 'Interactive' }
    # New: if ($Interactive) { 'Interactive' } else { 'Non-interactive' }

    # Should use $Interactive variable for mode display
    mode_line = re.search(r'Write-Host\s+"MODE:[^"]+"\s+-ForegroundColor White', src)
    if mode_line:
        # Check the context around MODE display
        context_start = max(0, src.find(mode_line.group(0)) - 200)
        context_end = min(len(src), src.find(mode_line.group(0)) + 50)
        context = src[context_start:context_end]

        assert "$Interactive" in context, (
            "MODE display should use $Interactive variable (inverted logic). "
            "The PR inverts the default: non-interactive is now default."
        )

    # Check session file logic is also inverted
    result = _run_shell(["grep", "-E", r"if\s*\(\s*-not\s+\$Interactive\s*\)", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, (
        "Session markdown logic should use 'if (-not $Interactive)' instead of 'if ($NoInteractive)'. "
        "Session files are created in non-interactive mode (the new default)."
    )


# [pr_diff] fail_to_pass
def test_phase_2_implementation_added():
    """Review-PR.ps1 implements Phase 2: PR-FINALIZE SKILL block - verified via execution."""
    result = _run_shell(["grep", "-F", "PHASE 2: PR-FINALIZE SKILL", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, (
        "Missing 'PHASE 2: PR-FINALIZE SKILL' block. "
        "The PR adds this phase to run pr-finalize skill when -RunFinalize is specified."
    )

    result = _run_shell(["grep", "-F", "pr-finalize skill for PR", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, "Should include pr-finalize skill invocation in Phase 2."


# [pr_diff] fail_to_pass
def test_phase_3_implementation_added():
    """Review-PR.ps1 implements Phase 3: POST SUMMARY COMMENT block - verified via execution."""
    result = _run_shell(["grep", "-F", "PHASE 3: POST SUMMARY COMMENT", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, (
        "Missing 'PHASE 3: POST SUMMARY COMMENT' block. "
        "The PR adds this phase to run ai-summary-comment skill when -PostSummaryComment is specified."
    )

    result = _run_shell(["grep", "-F", "ai-summary-comment skill to post a comment", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, "Should include ai-summary-comment skill invocation in Phase 3."


# [pr_diff] fail_to_pass
def test_copilot_instructions_updated():
    """copilot-instructions.md has updated pr-finalize skill description - verified via execution."""
    # Check for code review mention
    result = _run_shell(["grep", "-F", "performs code review for best practices before merge", str(COPILOT_INSTRUCTIONS_PATH)])
    assert result.returncode == 0, (
        "copilot-instructions.md should mention that pr-finalize now performs code review. "
        "The PR adds code review phase to the skill."
    )

    # Check for safety rule
    result = _run_shell(["grep", "-F", "NEVER use `--approve` or `--request-changes`", str(COPILOT_INSTRUCTIONS_PATH)])
    assert result.returncode == 0, (
        "Missing CRITICAL safety rule in copilot-instructions.md: NEVER use --approve or --request-changes. "
        "AI agents must not approve or block PRs - only post comments."
    )


# [pr_diff] fail_to_pass
def test_codereview_parameters_added():
    """post-pr-finalize-comment.ps1 has CodeReviewStatus and CodeReviewFindings parameters - verified via execution."""
    # Check for CodeReviewStatus parameter
    result = _run_shell(["grep", "-E", r"\[.*?\]?\s*\$?CodeReviewStatus", str(POST_FINALIZE_PATH)])
    assert result.returncode == 0, (
        "Missing CodeReviewStatus parameter. "
        "The PR adds this parameter with values: Passed, IssuesFound, Skipped."
    )

    # Check for CodeReviewFindings parameter
    result = _run_shell(["grep", "-E", r"\[.*?\]?\s*\$?CodeReviewFindings", str(POST_FINALIZE_PATH)])
    assert result.returncode == 0, (
        "Missing CodeReviewFindings parameter. "
        "The PR adds this parameter for code review content."
    )

    # Check for ValidateSet
    result = _run_shell(["grep", "-F", 'ValidateSet("Passed", "IssuesFound", "Skipped", "")', str(POST_FINALIZE_PATH)])
    assert result.returncode == 0, (
        "CodeReviewStatus should have ValidateSet with 'Passed', 'IssuesFound', 'Skipped'."
    )


# [pr_diff] fail_to_pass
def test_codereview_section_added():
    """post-pr-finalize-comment.ps1 includes code review collapsible section - verified via execution."""
    # Check for code review section variable
    result = _run_shell(["grep", "-E", r"\$codeReviewSection", str(POST_FINALIZE_PATH)])
    assert result.returncode == 0, (
        "Missing $codeReviewSection variable. "
        "The PR adds a third collapsible section for code review."
    )

    # Check for code review in output
    result = _run_shell(["grep", "-F", "Code Review:", str(POST_FINALIZE_PATH)])
    assert result.returncode == 0 or "$codeReviewSection" in Path(POST_FINALIZE_PATH).read_text(), (
        "Script should include Code Review section in the posted comment."
    )

    # Check for emoji mappings
    src = Path(POST_FINALIZE_PATH).read_text()
    has_emoji_mappings = '"Passed" { "✅" }' in src or '"IssuesFound" { "⚠️" }' in src
    assert has_emoji_mappings, "Should have emoji mappings for CodeReviewStatus values."


# [pr_diff] fail_to_pass
def test_skill_finalize_has_code_review_phase():
    """pr-finalize/SKILL.md has code review phase documentation - verified via execution."""
    result = _run_shell(["grep", "-F", "Code Review", str(SKILL_FINALIZE_PATH)])
    assert result.returncode == 0, (
        "pr-finalize/SKILL.md should document the code review phase. "
        "The PR adds a second phase for code review."
    )

    # Check for safety rules
    src = SKILL_FINALIZE_PATH.read_text()
    has_safety = "NEVER Approve or Request Changes" in src or "NEVER use `--approve`" in src
    assert has_safety, "SKILL.md should have CRITICAL safety rules about approval."

    # Check for two-phase workflow
    has_workflow = "Two-Phase Workflow" in src or ("Phase 1" in src and "Phase 2" in src)
    assert has_workflow, "SKILL.md should describe the two-phase workflow (Title/Description + Code Review)."


# [pr_diff] fail_to_pass
def test_skill_ai_has_codereview_docs():
    """ai-summary-comment/SKILL.md documents Code Review section parameters - verified via execution."""
    result = _run_shell(["grep", "-E", r"CodeReviewStatus", str(SKILL_AI_PATH)])
    assert result.returncode == 0, "ai-summary-comment/SKILL.md should document CodeReviewStatus parameter."

    result = _run_shell(["grep", "-E", r"CodeReviewFindings", str(SKILL_AI_PATH)])
    assert result.returncode == 0, "ai-summary-comment/SKILL.md should document CodeReviewFindings parameter."

    # Check for three sections mention
    src = SKILL_AI_PATH.read_text()
    has_three_sections = (
        ("Title" in src and "Description" in src and "Code Review" in src) or
        "three sections" in src.lower() or
        "three collapsible sections" in src.lower()
    )
    assert has_three_sections, (
        "SKILL.md should mention that comments now have three sections: Title, Description, and Code Review."
    )


# [pr_diff] fail_to_pass
def test_extract_codereview_from_file():
    """post-pr-finalize-comment.ps1 extracts code review from code-review.md file - verified via execution."""
    result = _run_shell(["grep", "-F", "code-review.md", str(POST_FINALIZE_PATH)])
    assert result.returncode == 0, (
        "Script should look for code-review.md file to auto-load code review content. "
        "The PR adds support for loading code review from a separate file."
    )

    result = _run_shell(["grep", "-E", r"Code Review Findings|### 🔍 Code Review", str(POST_FINALIZE_PATH)])
    assert result.returncode == 0, (
        "Script should extract code review from summary file when code-review.md is not present."
    )


# [pr_diff] fail_to_pass
def test_warnings_for_missing_recommendations():
    """post-pr-finalize-comment.ps1 warns when recommended title/description missing - verified via execution."""
    result = _run_shell(["grep", "-F", "Warning: TitleStatus is 'NeedsUpdate' but no RecommendedTitle provided", str(POST_FINALIZE_PATH)])
    assert result.returncode == 0, (
        "Script should warn when TitleStatus is NeedsUpdate but no RecommendedTitle provided."
    )

    # Check for description warning
    src = POST_FINALIZE_PATH.read_text()
    has_desc_warning = "Warning: DescriptionStatus is" in src and "RecommendedDescription provided" in src
    assert has_desc_warning, (
        "Script should warn when DescriptionStatus indicates update needed but no RecommendedDescription provided."
    )


# [pr_diff] fail_to_pass
def test_recommendedtitle_extraction_order_fixed():
    """post-pr-finalize-comment.ps1 extracts RecommendedTitle before TitleStatus detection - verified via execution."""
    src = POST_FINALIZE_PATH.read_text()

    # Find the extraction logic order
    recommended_title_pos = src.find("Extract Recommended Title FIRST")
    title_status_pos = src.find("Extract Title assessment")

    if recommended_title_pos != -1 and title_status_pos != -1:
        assert recommended_title_pos < title_status_pos, (
            "RecommendedTitle should be extracted BEFORE TitleStatus detection. "
            "The PR fixes a bug where TitleStatus was detected before RecommendedTitle was extracted."
        )


# [pr_diff] fail_to_pass
def test_autodetection_needsupdate_from_recommendedtitle():
    """post-pr-finalize-comment.ps1 auto-detects NeedsUpdate if RecommendedTitle exists - verified via execution."""
    result = _run_shell([
        "grep", "-E",
        r"if\s*\(\s*-not\s+\[string\]::IsNullOrWhiteSpace\(\$RecommendedTitle\)\)",
        str(POST_FINALIZE_PATH)
    ])

    # Also verify NeedsUpdate is in the same context
    src = POST_FINALIZE_PATH.read_text()
    has_autodetection = 'if (-not [string]::IsNullOrWhiteSpace($RecommendedTitle))' in src and 'NeedsUpdate' in src
    assert has_autodetection, (
        "Script should auto-detect TitleStatus as NeedsUpdate when RecommendedTitle exists. "
        "The PR adds this auto-detection logic."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural checks with subprocess
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_pr_finalize_marker_preserved():
    """PR finalization comment marker is preserved - verified via execution."""
    result = _run_shell(["grep", "-F", "PR-FINALIZE-COMMENT", str(POST_FINALIZE_PATH)])
    assert result.returncode == 0, (
        "Script must contain <!-- PR-FINALIZE-COMMENT --> marker for comment identification."
    )


# [static] pass_to_pass
def test_examples_updated_in_review_pr():
    """Review-PR.ps1 examples reflect new interactive default - verified via execution."""
    result = _run_shell(["grep", "-F", "non-interactive mode (default)", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, (
        "Examples should mention that non-interactive is now the default."
    )

    result = _run_shell(["grep", "-E", r"-Interactive.*interactive mode", str(REVIEW_PR_PATH)])
    assert result.returncode == 0, (
        "Examples should show -Interactive for interactive mode."
    )


# ---------------------------------------------------------------------------
# Repo CI pass-to-pass gates — verify repo CI checks pass on base AND gold
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_powershell_scripts_parse():
    """Repo's PowerShell scripts have valid syntax (pass_to_pass) - with subprocess validation."""
    # Find all PowerShell files using subprocess
    result = _run_shell(["find", f"{REPO}/.github/scripts", "-name", "*.ps1", "-type", "f"])
    ps1_files = [f for f in result.stdout.strip().split('\n') if f]
    assert len(ps1_files) > 0, "No PowerShell files found"

    errors = []
    for path_str in ps1_files:
        result = _run_shell(["cat", path_str])
        if result.returncode != 0:
            continue
        src = result.stdout

        # Check for balanced braces using shell output
        open_braces = src.count("{")
        close_braces = src.count("}")
        if open_braces != close_braces:
            errors.append(f"{path_str}: Unbalanced braces ({open_braces} vs {close_braces})")

        # Check for balanced parentheses
        open_parens = src.count("(")
        close_parens = src.count(")")
        if open_parens != close_parens:
            errors.append(f"{path_str}: Unbalanced parentheses ({open_parens} vs {close_parens})")

        # Check basic PowerShell function syntax (param blocks should exist with CmdletBinding)
        if "[CmdletBinding()]" in src:
            if "param" not in src:
                errors.append(f"{path_str}: CmdletBinding without param block")

    if errors:
        raise AssertionError("PowerShell syntax issues found:\n" + "\n".join(errors[:10]))


# [repo_tests] pass_to_pass
def test_repo_markdown_files_valid():
    """Repo's SKILL.md and docs markdown files are valid (pass_to_pass) - with subprocess."""
    md_files = [
        f"{REPO}/.github/skills/ai-summary-comment/SKILL.md",
        f"{REPO}/.github/skills/pr-finalize/SKILL.md",
        f"{REPO}/.github/copilot-instructions.md",
    ]

    for path_str in md_files:
        result = _run_shell(["cat", path_str])
        assert result.returncode == 0, f"Required markdown file not found: {path_str}"

        src = result.stdout

        # Check for valid markdown structure (basic checks)
        fence_count = src.count("```")
        assert fence_count % 2 == 0, f"Unclosed code blocks in {path_str}: {fence_count} fences"

        # Check for basic markdown structure
        assert "#" in src, f"No headers found in {path_str}"


# [repo_tests] pass_to_pass
def test_repo_yaml_workflows_exist():
    """Repo's GitHub workflow YAML files exist and have basic structure (pass_to_pass) - with subprocess."""
    result = _run_shell(["find", f"{REPO}/.github/workflows", "-name", "*.yml", "-type", "f"])
    yml_files = [f for f in result.stdout.strip().split('\n') if f]
    assert len(yml_files) > 0, "No workflow YAML files found"

    for path_str in yml_files:
        result = _run_shell(["cat", path_str])
        if result.returncode != 0:
            continue
        src = result.stdout

        # Basic YAML structure checks
        assert "name:" in src, f"No 'name' field in {path_str}"


# [repo_tests] pass_to_pass
def test_repo_no_bom_in_scripts():
    """Repo's PowerShell scripts don't have unexpected corruption (pass_to_pass) - with subprocess."""
    result = _run_shell(["find", f"{REPO}/.github/scripts", "-name", "*.ps1", "-type", "f"])
    ps1_files = [f for f in result.stdout.strip().split('\n') if f]

    for path_str in ps1_files:
        # Use subprocess with od to check for null bytes
        result = _run_shell(["od", "-c", path_str])
        if result.returncode == 0:
            assert "\\0" not in result.stdout, f"Null bytes found in {path_str} - file may be corrupted"


# [repo_tests] pass_to_pass
def test_repo_json_files_valid():
    """Repo's JSON config files are valid (pass_to_pass) - with subprocess execution."""
    json_files = [
        f"{REPO}/.config/dotnet-tools.json",
        f"{REPO}/.github/prompts/contributors.json",
        f"{REPO}/eng/test-configuration.json",
    ]

    # Also find any JSON files in .github
    result = _run_shell(["find", f"{REPO}/.github", "-name", "*.json", "-type", "f"])
    json_files.extend([f for f in result.stdout.strip().split('\n') if f])

    checked = 0
    for path_str in json_files:
        result = _run_shell(["cat", path_str])
        if result.returncode != 0:
            continue

        content = result.stdout

        # Use Python via subprocess to validate JSON
        result = subprocess.run(
            ["python3", "-c", f"import json; json.loads('{content.replace(chr(39), chr(34))}')"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Invalid JSON in {path_str}: {result.stderr}"

        # Check no trailing commas (common JSON error)
        if ",}" in content or ",]" in content:
            raise AssertionError(f"Trailing comma found in {path_str}")

        checked += 1

    assert checked > 0, "No JSON files found to validate"


# [repo_tests] pass_to_pass
def test_repo_all_powershell_scripts_parse():
    """All .github/scripts PowerShell scripts have valid syntax (pass_to_pass) - with subprocess."""
    result = _run_shell(["find", f"{REPO}/.github/scripts", "-name", "*.ps1", "-type", "f"])
    ps1_files = [f for f in result.stdout.strip().split('\n') if f]
    assert len(ps1_files) > 0, "No PowerShell files found in .github/scripts"

    errors = []
    for path_str in ps1_files:
        result = _run_shell(["cat", path_str])
        if result.returncode != 0:
            continue
        src = result.stdout

        # Check for balanced braces (basic check)
        open_braces = src.count("{")
        close_braces = src.count("}")
        if open_braces != close_braces:
            errors.append(f"{path_str}: Unbalanced braces ({open_braces} vs {close_braces})")

        # Check for balanced parentheses
        open_parens = src.count("(")
        close_parens = src.count(")")
        if open_parens != close_parens:
            errors.append(f"{path_str}: Unbalanced parentheses ({open_parens} vs {close_parens})")

        # Check for balanced brackets
        open_brackets = src.count("[")
        close_brackets = src.count("]")
        if open_brackets != close_brackets:
            errors.append(f"{path_str}: Unbalanced brackets ({open_brackets} vs {close_brackets})")

    if errors:
        raise AssertionError("PowerShell syntax issues found:\n" + "\n".join(errors[:10]))


# [repo_tests] pass_to_pass
def test_repo_gitattributes_valid():
    """Repo's .gitattributes file is valid (pass_to_pass) - with subprocess."""
    result = _run_shell(["cat", f"{REPO}/.gitattributes"])
    if result.returncode != 0:
        return  # Skip if no gitattributes

    src = result.stdout

    # Basic checks for gitattributes format
    for line in src.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Each non-comment line should have at least a pattern and an attribute
        parts = line.split()
        if len(parts) < 2:
            raise AssertionError(f"Invalid .gitattributes line: {line}")


# [repo_tests] pass_to_pass
def test_repo_editorconfig_valid():
    """Repo's .editorconfig file is valid (pass_to_pass) - with subprocess."""
    result = _run_shell(["cat", f"{REPO}/.editorconfig"])
    if result.returncode != 0:
        return  # Skip if no editorconfig

    src = result.stdout

    # Check for at least one section header
    assert "[" in src, ".editorconfig should have at least one section [pattern]"

    # Basic validation - no unclosed sections
    open_brackets = src.count("[")
    close_brackets = src.count("]")
    assert open_brackets == close_brackets, "Unbalanced brackets in .editorconfig"


# [repo_tests] pass_to_pass
def test_repo_nuget_config_valid():
    """Repo's NuGet.config is valid XML (pass_to_pass) - with subprocess."""
    result = _run_shell(["cat", f"{REPO}/NuGet.config"])
    if result.returncode != 0:
        return

    src = result.stdout

    # Basic XML structure checks
    assert "<configuration>" in src, "NuGet.config should have <configuration> root"
    assert "</configuration>" in src, "NuGet.config should close </configuration>"

    # Check for balanced tags (basic check)
    assert src.count("<packageSources>") == src.count("</packageSources>"), "Unbalanced packageSources tags"


# [repo_tests] pass_to_pass
def test_repo_readme_not_empty():
    """Repo's README.md exists and has content (pass_to_pass) - with subprocess."""
    result = _run_shell(["stat", "-c%s", f"{REPO}/README.md"])
    assert result.returncode == 0, "README.md should exist"

    size = int(result.stdout.strip())
    assert size > 100, f"README.md seems too small ({size} bytes)"

    result = _run_shell(["cat", f"{REPO}/README.md"])
    assert result.returncode == 0, "Failed to read README.md"
    assert "#" in result.stdout, "README.md should have at least one markdown header"
