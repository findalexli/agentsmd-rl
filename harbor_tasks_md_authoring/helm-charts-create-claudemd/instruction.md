# create Claude.md

Source: [grafana-community/helm-charts#63](https://github.com/grafana-community/helm-charts/pull/63)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

#### What this PR does / why we need it

Not sure how many of us use Claude, but I figured this was a helpful start.  It also has some dependency on https://github.com/grafana-community/helm-charts/pull/62 since I developed that first.  If that's closed then I'll edit this.

#### Which issue this PR fixes

#### Special notes for your reviewer

#### Checklist

<!-- [Place an '[x]' (no spaces) in all applicable fields. Please remove unrelated fields.] -->
- [x] [DCO](https://github.com/prometheus-community/helm-charts/blob/main/CONTRIBUTING.md#sign-off-your-work) signed
- [ ] Chart Version bumped
- [ ] Title of the PR starts with chart name (e.g. `[prometheus-couchdb-exporter]`)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
