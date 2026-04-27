# Correct the Ghost setup-command instructions

## Background

The Ghost monorepo (`/workspace/Ghost`) ships several user-facing setup
recipes — in agent instruction files, contributor docs, the Codex
environment definition, and the `enforce-package-manager` warning script.
All of them currently teach contributors and AI agents to run:

```bash
pnpm setup
```

That command is **broken**. `setup` is a *built-in* `pnpm` subcommand
(it is meant to set up the environment for pnpm itself), not Ghost's
first-time-setup script. To run Ghost's `setup` script defined in
`package.json`, you must invoke it explicitly with `pnpm run setup`.

A second related issue: pnpm itself must come from the right version.
Ghost expects pnpm to be managed via [Corepack](https://nodejs.org/api/corepack.html),
the Node.js shim that selects the package-manager version pinned in the
repository. Running `pnpm` before corepack is enabled may pick up the
wrong version. The fix is to run `corepack enable pnpm` before any
`pnpm` invocation, and the documentation needs to teach this.

## What's wrong

Every place in the repo that documents or scripts the first-time setup
of Ghost has the same two defects:

1. It tells the user to run `pnpm setup` (broken — runs pnpm's built-in,
   not Ghost's `setup` script).
2. It does not mention enabling corepack, which is required so that the
   correct pinned version of pnpm is used.

Concretely, the symptoms a contributor or agent will hit when following
the current docs are:

- Running `pnpm setup` does *not* install Ghost's dependencies or
  initialize submodules; it tries to set up pnpm itself.
- Running `pnpm` without first enabling corepack may use a globally
  installed pnpm whose version diverges from the repo's pinned version.

## What needs to change

Update the user-facing setup recipes throughout the repo so they teach
the correct two-step sequence — enable corepack, then run Ghost's setup
script via `pnpm run setup`. The replacement guidance the
`enforce-package-manager` script prints to misguided contributors must
also be corrected.

Specifically, the following user-facing surfaces all currently mislead
users about how to set up Ghost and must be corrected:

- The root agent-instructions file's `### Development` block (which
  describes the day-one commands an agent should run).
- The contributor quick-start documentation under `docs/`.
- The end-to-end test suite README's `### Prerequisites` section, which
  currently lists pnpm as something to install separately rather than
  noting it is provided via corepack.
- The Codex environment definition under `.codex/environments/`, whose
  `[setup].script` is what Codex executes for first-time setup.
- The error message printed by the `enforce-package-manager` guard
  script in `.github/scripts/`, whose "Common command replacements"
  table currently maps `yarn setup` to the broken `pnpm setup`.

After your changes:

- `corepack enable pnpm` must appear in the contributor quick-start and
  in the agent instruction file's development block, ahead of the
  setup-script invocation.
- The setup-script invocation must be `pnpm run setup` everywhere it
  used to be `pnpm setup`. In particular the `enforce-package-manager`
  guard script's "Common command replacements" table must contain the
  literal line:

  ```
  yarn setup   -> pnpm run setup
  ```

  and the Codex environment's `[setup].script` block must invoke
  `pnpm run setup`.
- The e2e README's prerequisites must explain that pnpm is provided via
  corepack rather than listing pnpm as a separate install. The current
  prerequisite line `- Node.js and pnpm installed` should no longer
  appear.

- The `enforce-package-manager` script's "Common command replacements"
  table currently contains the broken line `yarn setup   -> pnpm setup`
  (note the literal sequence, including the run of spaces). That broken
  line must be replaced with the corrected mapping shown above.

## How to verify

Run `pytest` on the test suite under `/tests/test_outputs.py`. The tests
parse the TOML config, execute the JavaScript guard script with a
non-pnpm `npm_config_user_agent` to check its error output, and read
the markdown files to confirm the corrected instructions are present.
