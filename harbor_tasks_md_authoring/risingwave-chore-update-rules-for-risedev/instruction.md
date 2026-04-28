# chore: update rules for risedev usage in `build-run-test.mdc` 

Source: [risingwavelabs/risingwave#24224](https://github.com/risingwavelabs/risingwave/pull/24224)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/build-run-test.mdc`

## What to add / change

I hereby agree to the terms of the [RisingWave Labs, Inc. Contributor License Agreement](https://raw.githubusercontent.com/risingwavelabs/risingwave/17af8a747593ebdbfa826691daf75bdab7d14fa0/.github/contributor-license-agreement.txt).



## What's changed and what's your intention?

As title, to make sure it's up-to-date and works well with latest trending agents like Codex.

## Checklist

- [x] I have written necessary rustdoc comments.
- [x] <!-- OPTIONAL --> I have added necessary unit tests and integration tests.
- [ ] <!-- OPTIONAL --> I have added test labels as necessary. <!-- See https://github.com/risingwavelabs/risingwave/blob/main/docs/developer-guide.md#ci-labels-guide) -->
- [ ] <!-- OPTIONAL --> I have added fuzzing tests or opened an issue to track them. <!-- Recommended for new SQL features, see #7934 -->
- [ ] <!-- OPTIONAL --> My PR contains breaking changes. <!-- If it deprecates some features, please create a tracking issue to remove them in the future -->
- [ ] <!-- OPTIONAL --> My PR changes performance-critical code, so I will run (micro) benchmarks and present the results. <!-- To manually trigger a benchmark, please check out [Notion](https://www.notion.so/risingwave-labs/Manually-trigger-nexmark-performance-dashboard-test-b784f1eae1cf48889b2645d020b6b7d3). -->
- [ ] <!-- OPTIONAL --> I have checked the [Release Timeline](https://github.com/risingwavelabs/rw-commits-history/blob/main/release_timeline.md) and [Currently Supported Version

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
