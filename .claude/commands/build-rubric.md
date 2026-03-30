# Build Rubric

Build `rubric.yaml` for `harbor_tasks/$ARGUMENTS/` by extracting rules **verbatim** from the repo's agent config files at the base commit.

## Steps

1. **Get base commit** from `harbor_tasks/$ARGUMENTS/environment/Dockerfile` — find the `git checkout` line.

2. **Enumerate all agent config files** at that commit:
   ```
   gh api "repos/OWNER/REPO/git/trees/BASE_COMMIT?recursive=1" --jq '.tree[] | select(.path | test("CLAUDE\\.md|AGENTS\\.md|SKILL\\.md|\\.cursorrules|copilot-instructions")) | .path'
   ```

3. **Fetch each config file** and read it:
   ```
   gh api "repos/OWNER/REPO/contents/PATH?ref=BASE_COMMIT" --jq '.content' | base64 -d
   ```

4. **Identify which config files are relevant** to this task:
   - Root configs (CLAUDE.md, AGENTS.md) always apply
   - Subdirectory configs apply if the PR touches files in that subdirectory
   - Check which files the PR changes by reading `solution/solve.sh`

5. **Extract rules verbatim**. For each config file, find lines that state requirements, constraints, or conventions. Copy the text exactly — do not paraphrase or invent.

6. **Write `rubric.yaml`** in this format:
   ```yaml
   # Rules from repo agent configs, evaluated by LLM judge.
   rules:
     - rule: "exact text from the config file"
       from: "path/to/AGENTS.md:LINE_NUMBER"
     - rule: "another exact rule"
       from: ".claude/skills/write-test/SKILL.md:14"
   ```

## Rules

- **NEVER fabricate rules.** Every rule must be a direct quote or minimal paraphrase of text that actually exists at the cited file and line.
- **ALWAYS verify line numbers.** After writing the rubric, re-read the source file and confirm the cited line contains the rule text.
- **Use full repo-relative paths.** `extensions/CLAUDE.md`, not `CLAUDE.md` (repos can have multiple).
- **Skip irrelevant rules.** A rule about "commit message format" doesn't belong in a rubric for a code bugfix. Only include rules an agent would need to follow when solving this specific task.
- **If no config files exist at the base commit**, write an empty rubric with a comment explaining why.
- **ONLY include rules evaluable from a code diff.** The LLM judge sees ONLY the git diff — nothing else. Exclude:
  - Process rules ("read files before modifying", "get approval before changing X", "run pre-commit")
  - PR/commit rules ("add Co-authored-by", "reference an issue", "disclose AI usage")
  - Tooling rules ("use uv not pip", "run make style")
  - Rules requiring runtime verification ("tests must pass", "no performance regressions")
  - Subjective size/effort rules ("PRs should be brief", "minimize the diff", "avoid writing significant amounts of new code") — these penalize correct fixes that happen to be multi-line

  INCLUDE only rules about **code quality visible in a diff**:
  - Style ("match surrounding patterns", "no wildcard imports", "explicit type hints")
  - Architecture ("composition over inheritance", "no global process groups")
  - Safety ("guard array access", "handle malformed input gracefully")
  - Naming ("snake_case", "PascalCase loggers")

## Validation

After writing the rubric, mentally apply the gold patch (read `solution/solve.sh`) and ask: **would a correct fix pass every rule?** If any rule would fail on the gold patch, it's too subjective or not diff-evaluable — remove it.
