# Fix Milestone Selection for Patch Bumps

The changeset milestone assignment script in the `changeset-validation` skill has a bug: when the required bump type is `patch`, it selects the wrong open milestone. Patch changesets should be assigned to the **lowest** available `X.Y.x` milestone (the oldest release series), but the current code assigns them to the **highest** (newest) milestone instead.

## Symptom

Given multiple open milestones like `0.5.x`, `0.4.x`, `0.3.x` (sorted newest-to-oldest), a patch bump selects `0.5.x` when it should select `0.3.x`. Minor bumps are unaffected — they correctly select the second-newest milestone.

## What the Script Does

The script reads a changeset JSON file (containing a `required_bump` field), fetches open GitHub milestones whose titles match the `X.Y.x` format, sorts them descending by version, and assigns the selected milestone to the PR via the GitHub API. Milestones that don't match `X.Y.x` are filtered out.

## Expected Behavior

- **Major (not applicable):** No corresponding milestone selection logic is tested.
- **Minor:** Selects the second-highest version milestone (falling back to the only one if just one exists).
- **Patch:** Should select the **lowest** version milestone (the one with the smallest major.minor among the sorted results).
- **None:** No milestone should be assigned.

## Code Style Requirements

The repository enforces code style via ESLint (configured in `eslint.config.mjs`) and Prettier. Run `pnpm lint` to verify your changes pass all style checks. Comments must end with a period.

## How to Verify

The tests mock the GitHub API to provide controlled milestone data and verify which milestone number the script assigns to the PR. Run the assignment logic with a `required_bump` of `patch` and multiple open milestones — the selected milestone must be the one with the lowest version number.
