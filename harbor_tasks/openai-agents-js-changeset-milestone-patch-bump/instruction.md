# Fix changeset milestone selection for patch bumps

The `openai-agents-js` monorepo ships an automation script that assigns a
GitHub release-series milestone (titles of the form `X.Y.x`, e.g. `0.3.x`,
`0.4.x`, `0.5.x`) to a pull request based on the changeset's required
version bump. The script lives under
`.codex/skills/changeset-validation/scripts/` and is wired in as the
`changeset:assign-milestone` script in the root `package.json`.

The script is invoked as:

```
pnpm changeset:assign-milestone -- <path-to-json>
```

The JSON file at `<path-to-json>` has the shape `{"required_bump":
"patch" | "minor" | "none"}`. When a `GITHUB_TOKEN` and
`GITHUB_EVENT_PATH` are set (as in CI), the script lists the repository's
open milestones via the GitHub REST API
(`GET /repos/{owner}/{repo}/milestones?state=open&per_page=100`), filters
those whose title matches `^(\d+)\.(\d+)\.x$`, sorts the matches in
descending order by `(major, minor)`, then selects exactly one milestone
to assign to the PR via
`PATCH /repos/{owner}/{repo}/issues/{number}` with body
`{"milestone": <number>}`.

## What is broken

The selection rule for patch bumps is wrong. The intended policy is:

- **patch** → assign the **lowest available** `X.Y.x` milestone (the
  *oldest* still-open series).
- **minor** → assign the **second-most-recent** milestone when more than
  one is open, falling back to the most recent if only one exists.
- **none** → do nothing.

Today, the script always picks the **most recent** milestone for `patch`
bumps. So with open milestones `[0.3.x, 0.4.x, 0.5.x]` and a patch
changeset, the script currently assigns `0.5.x`, when it should assign
`0.3.x`.

The minor-bump and `none` behaviours are correct and must remain so:

- For a minor bump with the three milestones above, the script must
  continue to assign `0.4.x` (the second-most-recent).
- For a minor bump with exactly one open milestone (e.g. `0.7.x`), the
  script must continue to assign that single milestone.
- For `required_bump: "none"`, the script must not make any GitHub API
  calls.

Milestones whose title does not match `X.Y.x` (for example `Backlog`,
`Future`) must continue to be filtered out before selection — they are
never eligible targets.

## What to change

Adjust the milestone-selection branch in the script's `assignMilestone`
function so the rules above hold for every `required_bump` value.
Other behaviour — argv parsing, environment-variable handling, the early
`return`s on missing tokens / event payload / unknown bump, the GitHub
REST request shapes, sort order — must remain unchanged.

## Code Style Requirements

The repository enforces ESLint with Prettier defaults (see
`eslint.config.mjs`) and the contributor guide (`AGENTS.md`) requires
that any code comments end with a period. Keep the modified script
ESLint-clean and follow Conventional Commits if you are crafting a
commit message (`fix:` is appropriate for this change).
