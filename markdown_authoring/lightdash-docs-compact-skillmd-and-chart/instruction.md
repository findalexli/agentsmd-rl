# docs: compact SKILL.md and chart resources

Source: [lightdash/lightdash#19897](https://github.com/lightdash/lightdash/pull/19897)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/developing-in-lightdash/SKILL.md`
- `skills/developing-in-lightdash/resources/big-number-chart-reference.md`
- `skills/developing-in-lightdash/resources/cartesian-chart-reference.md`
- `skills/developing-in-lightdash/resources/chart-types-reference.md`
- `skills/developing-in-lightdash/resources/cli-reference.md`
- `skills/developing-in-lightdash/resources/custom-viz-reference.md`
- `skills/developing-in-lightdash/resources/dashboard-best-practices.md`
- `skills/developing-in-lightdash/resources/funnel-chart-reference.md`
- `skills/developing-in-lightdash/resources/gauge-chart-reference.md`
- `skills/developing-in-lightdash/resources/map-chart-reference.md`
- `skills/developing-in-lightdash/resources/pie-chart-reference.md`
- `skills/developing-in-lightdash/resources/table-chart-reference.md`
- `skills/developing-in-lightdash/resources/treemap-chart-reference.md`

## What to add / change

<!-- Thanks so much for your PR, your contribution is appreciated! ❤️ -->

Closes: <!-- reference the related issue e.g. #150 -->

### Description:
<!-- Add a description of the changes proposed in the pull request. -->

<!-- Even better add a screenshot / gif / loom -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
