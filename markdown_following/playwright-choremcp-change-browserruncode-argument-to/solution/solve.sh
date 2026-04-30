#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'A JavaScript function containing Playwright code to execute' packages/playwright/src/mcp/browser/tools/runCode.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'PYEOF'
from pathlib import Path

# --- 1. Fix runCode.ts ---
rc = Path("packages/playwright/src/mcp/browser/tools/runCode.ts")
src = rc.read_text()

# Replace schema description (3 parts)
src = src.replace(
    "Playwright code snippet to run",
    "A JavaScript function containing Playwright code to execute"
)
src = src.replace(
    "The snippet should access the \\`page\\` object to interact with the page. Can make multiple statements. \\`return\\` is allowed.",
    "It will be invoked with a single argument, page, which you can use for any page interaction."
)
src = src.replace(
    "For example: \\`await page.getByRole('button', { name: 'Submit' }).click(); return await page.title();\\`",
    "For example: \\`async (page) => { await page.getByRole('button', { name: 'Submit' }).click(); return await page.title(); }\\`"
)

# Replace response.addCode
src = src.replace(
    "response.addCode(params.code);",
    "response.addCode(`await (${params.code})(page);`);"
)

# Replace IIFE execution pattern (multi-line)
src = src.replace(
    "          const result = await (async () => {\n            ${params.code};\n          })();",
    "          const result = await (${params.code})(page);"
)

rc.write_text(src)
print("Fixed runCode.ts")

# --- 2. Fix .claude/agents/playwright-test-planner.md ---
claude_agent = Path("examples/todomvc/.claude/agents/playwright-test-planner.md")
content = claude_agent.read_text()
content = content.replace(
    "mcp__playwright-test__browser_press_key, mcp__playwright-test__browser_select_option",
    "mcp__playwright-test__browser_press_key, mcp__playwright-test__browser_run_code, mcp__playwright-test__browser_select_option"
)
claude_agent.write_text(content)
print("Fixed .claude/agents/playwright-test-planner.md")

# --- 3. Fix .github/agents/playwright-test-planner.agent.md ---
gh_agent = Path("examples/todomvc/.github/agents/playwright-test-planner.agent.md")
content = gh_agent.read_text()
content = content.replace(
    "  - playwright-test/browser_press_key\n  - playwright-test/browser_select_option",
    "  - playwright-test/browser_press_key\n  - playwright-test/browser_run_code\n  - playwright-test/browser_select_option"
)
gh_agent.write_text(content)
print("Fixed .github/agents/playwright-test-planner.agent.md")

# --- 4. Fix packages agent file ---
pkg_agent = Path("packages/playwright/src/agents/playwright-test-planner.agent.md")
content = pkg_agent.read_text()
content = content.replace(
    "  - playwright-test/browser_press_key\n  - playwright-test/browser_select_option",
    "  - playwright-test/browser_press_key\n  - playwright-test/browser_run_code\n  - playwright-test/browser_select_option"
)
pkg_agent.write_text(content)
print("Fixed packages/playwright/src/agents/playwright-test-planner.agent.md")
PYEOF

echo "Patch applied successfully."
