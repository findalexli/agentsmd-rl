# Fix SPDX license for SKILL.md and zh-CN.md

Source: [apache/airflow#62185](https://github.com/apache/airflow/pull/62185)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/airflow-translations/SKILL.md`
- `.github/skills/airflow-translations/locales/zh-CN.md`

## What to add / change

<!-- SPDX-License-Identifier: Apache-2.0
      https://www.apache.org/licenses/LICENSE-2.0 -->

<!--
Thank you for contributing!

Please provide above a brief description of the changes made in this pull request.
Write a good git commit message following this guide: http://chris.beams.io/posts/git-commit/

Please make sure that your code changes are covered with tests.
And in case of new features or big changes remember to adjust the documentation.

Feel free to ping (in general) for the review if you do not see reaction for a few days
(72 Hours is the minimum reaction time you can expect from volunteers) - we sometimes miss notifications.

In case of an existing issue, reference it using one of the following:

* closes: #ISSUE
* related: #ISSUE
-->

---

* related: #61984 

### Why

According to the https://github.com/apache/airflow/pull/62145, the SPDX licence should not have any extra characters after the specification, moving the URL to a separate line is better in context of automated parsers, for both `SKILL.md` and `zh-CN.md`.

##### Was generative AI tooling used to co-author this PR?

<!--
If generative AI tooling has been used in the process of authoring this PR, please
change below checkbox to `[X]` followed by the name of the tool, uncomment the "Generated-by".
-->

- [ ] Yes (please specify the tool below)

<!--
Generated-by: [Tool Name] following [the guidelines](https://github.com/apache/airflow/blob/main/contributing-docs

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
