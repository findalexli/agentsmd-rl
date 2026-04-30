# Restore the `changelog-collect` skill so it loads at startup

The Ant Design repository ships several agent skills under `.agents/skills/`,
each with its own `SKILL.md`. At startup, the agent harness scans this
directory to register skills.

## Symptom

The `changelog-collect` skill (located at
`.agents/skills/changelog-collect/SKILL.md`) is **silently skipped** during
startup, even though its file exists and contains the expected workflow
documentation. None of the other skills in the same directory have this
problem — `commit-msg`, `create-pr`, `issue-reply`, and `version-release`
all load correctly.

## What you need to do

Make `.agents/skills/changelog-collect/SKILL.md` discoverable by the harness
in the same way the sibling skills are.

The fix should:

- Be confined to `.agents/skills/changelog-collect/SKILL.md`. Do not modify
  any other file.
- Preserve the existing skill body unchanged (the heading
  `# Changelog 收集工具` and all the workflow content beneath it).
- Use the loader-required identifier `changelog-collect` for this skill
  (matching its directory name under `.agents/skills/`).
- Provide a substantive, non-trivial description (at least ~30 characters)
  that explains what the skill does and when to invoke it, so the loader
  and the agent can decide whether the skill is relevant. The description
  must be a real explanation of the skill's purpose, not a placeholder
  string.

Look at the sibling `SKILL.md` files in `.agents/skills/*/SKILL.md` to see
the exact mechanism the loader expects — they are otherwise structurally
identical to `changelog-collect`, yet they load correctly while
`changelog-collect` does not.
