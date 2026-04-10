You are reviewing the eval_manifest.yaml and test_outputs.py for harbor task `$ARGUMENTS` to add MISSING checks derived from the repo's agent config files.

## Steps

1. Read `harbor_tasks/$ARGUMENTS/agent_configs.md` completely — this concatenates ALL agent config files from the repo, with headers like `## File: CLAUDE.md` or `## File: .github/copilot-instructions.md`
2. Read `harbor_tasks/$ARGUMENTS/eval_manifest.yaml` to see existing checks
3. Read `harbor_tasks/$ARGUMENTS/solution/solve.sh` to see which files are changed
4. Read `harbor_tasks/$ARGUMENTS/tests/test_outputs.py` to see current tests
5. Read `harbor_tasks/$ARGUMENTS/task.toml` to get the base_commit for source attribution

## CRITICAL: Line number attribution

The `agent_configs.md` file concatenates multiple config files with headers. The line numbers in agent_configs.md do NOT match the original file line numbers.

When citing a rule, you MUST:
- Identify which original file it comes from (e.g., `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`)
- Use the line number **within that original file**, NOT the line number in agent_configs.md
- The header `## File: AGENTS.md (lines 1-250)` tells you where each file starts — subtract accordingly
- Example: if agent_configs.md line 150 is in the AGENTS.md section which starts at agent_configs.md line 100, and AGENTS.md started at line 1, then the original line is 150-100+1 = 51

In the `source` field, use the **original file path** (e.g., `AGENTS.md`, not `agent_configs.md`).

## Classification: Programmatic vs Rubric

**If a rule can be checked with code → it MUST be a programmatic check (test function), NOT a rubric rule.**

Ask yourself: "Can I write a grep, AST parse, or subprocess command to verify this?" If yes → programmatic check.

Examples of PROGRAMMATIC (add to test_outputs.py):
- "No wildcard imports" → AST check for `from X import *`
- "No print() calls" → AST check for print function calls
- "Use snake_case for functions" → AST check on function names
- "No .unwrap() in production code" → grep for `.unwrap()`
- "Run ruff/prettier" → subprocess call
- "Explicit type hints on public functions" → AST check for missing annotations
- "No hardcoded URLs/endpoints" → regex scan

Examples of TRUE RUBRIC (only for eval_manifest.yaml rubric section):
- "Code should be well-documented" (subjective — how much is enough?)
- "Prefer composition over inheritance" (judgment call per case)
- "Error messages should be helpful" (subjective quality)
- "Follow existing patterns in the codebase" (requires holistic judgment)

**When in doubt, make it a programmatic check.** Only use rubric for rules that genuinely require human/LLM judgment.

## For each rule in agent_configs.md:

1. Is it relevant to the files changed by this task? If not → skip
2. Is it already covered by an existing check? If yes → skip
3. Can it be checked programmatically? If yes → add as check + test function
4. Is it purely subjective? → add as rubric rule

For programmatic checks, add to BOTH:
- `eval_manifest.yaml`: check entry with `origin: agent_config` and correct `source` attribution
- `test_outputs.py`: test function with comment `# [agent_config] pass_to_pass — <file>:<lines> @ <commit>`

## Output

Edit eval_manifest.yaml and test_outputs.py. Do NOT modify existing checks or tests — only ADD new ones.

If agent_configs.md doesn't exist or has no relevant rules, say so and exit without editing.
