# fix(skill): add signInWithPassword return format and checkAuth guidance

Source: [TencentCloudBase/CloudBase-MCP#589](https://github.com/TencentCloudBase/CloudBase-MCP/pull/589)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `config/source/skills/auth-web/SKILL.md`

## What to add / change

## Summary
- Replace bare `signInWithPassword` one-liners with full `{ data, error }` destructuring showing success path (`data.user.id`) and error handling
- Add "Checking login state" section: recommend `getLoginState()` over `getUser()` for route guards, explain anonymous session pitfall
- Update `handleLogin` example to destructure `{ data, error }` consistently

## Root Cause
From cms-scaffold evaluation: agents produce **different return-value handling each run** because the skill only showed the call signature, not the response shape:
- Run A: `const result = await auth.signInWithPassword(...)` then `result.error` → works ✅
- Run B: `const result: any = ...` then `result.uid` → fails ❌ (uid is not top-level)
- Run C: `const { error } = ...` then success path never uses `data` → no uid available

## Depends on
- PR #588 (anonymous session pitfall) — already merged

## Test plan
- [ ] Verify auth-web/SKILL.md renders correctly
- [ ] Run cms-scaffold with `--skillSourceRef fix/auth-web-signin-return-format` to verify agent uses correct return format
- [ ] Note: end-to-end effect depends on next npm release (specs/attribution.md §6.2.2)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
