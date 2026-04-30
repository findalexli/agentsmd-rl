# Remove deprecated skills

Source: [binance/binance-skills-hub#243](https://github.com/binance/binance-skills-hub/pull/243)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/binance/algo/CHANGELOG.md`
- `skills/binance/algo/LICENSE.md`
- `skills/binance/algo/SKILL.md`
- `skills/binance/algo/references/authentication.md`
- `skills/binance/alpha/CHANGELOG.md`
- `skills/binance/alpha/LICENSE.md`
- `skills/binance/alpha/SKILL.md`
- `skills/binance/alpha/references/authentication.md`
- `skills/binance/assets/CHANGELOG.md`
- `skills/binance/assets/LICENSE.md`
- `skills/binance/assets/SKILL.md`
- `skills/binance/assets/references/authentication.md`
- `skills/binance/convert/CHANGELOG.md`
- `skills/binance/convert/LICENSE.md`
- `skills/binance/convert/SKILL.md`
- `skills/binance/convert/references/authentication.md`
- `skills/binance/derivatives-trading-coin-futures/CHANGELOG.md`
- `skills/binance/derivatives-trading-coin-futures/LICENSE.md`
- `skills/binance/derivatives-trading-coin-futures/SKILL.md`
- `skills/binance/derivatives-trading-coin-futures/references/authentication.md`
- `skills/binance/derivatives-trading-options/CHANGELOG.md`
- `skills/binance/derivatives-trading-options/LICENSE.md`
- `skills/binance/derivatives-trading-options/SKILL.md`
- `skills/binance/derivatives-trading-options/references/authentication.md`
- `skills/binance/derivatives-trading-portfolio-margin-pro/CHANGELOG.md`
- `skills/binance/derivatives-trading-portfolio-margin-pro/LICENSE.md`
- `skills/binance/derivatives-trading-portfolio-margin-pro/SKILL.md`
- `skills/binance/derivatives-trading-portfolio-margin-pro/references/authentication.md`
- `skills/binance/derivatives-trading-portfolio-margin/CHANGELOG.md`
- `skills/binance/derivatives-trading-portfolio-margin/LICENSE.md`
- `skills/binance/derivatives-trading-portfolio-margin/SKILL.md`
- `skills/binance/derivatives-trading-portfolio-margin/references/authentication.md`
- `skills/binance/derivatives-trading-usds-futures/CHANGELOG.md`
- `skills/binance/derivatives-trading-usds-futures/LICENSE.md`
- `skills/binance/derivatives-trading-usds-futures/SKILL.md`
- `skills/binance/derivatives-trading-usds-futures/references/authentication.md`
- `skills/binance/margin-trading/CHANGELOG.md`
- `skills/binance/margin-trading/LICENSE.md`
- `skills/binance/margin-trading/SKILL.md`
- `skills/binance/margin-trading/references/authentication.md`
- `skills/binance/simple-earn/CHANGELOG.md`
- `skills/binance/simple-earn/LICENSE.md`
- `skills/binance/simple-earn/SKILL.md`
- `skills/binance/simple-earn/references/authentication.md`
- `skills/binance/spot/CHANGELOG.md`
- `skills/binance/spot/LICENSE.md`
- `skills/binance/spot/SKILL.md`
- `skills/binance/spot/references/authentication.md`
- `skills/binance/sub-account/CHANGELOG.md`
- `skills/binance/sub-account/LICENSE.md`
- `skills/binance/sub-account/SKILL.md`
- `skills/binance/sub-account/references/authentication.md`
- `skills/binance/vip-loan/CHANGELOG.md`
- `skills/binance/vip-loan/LICENSE.md`
- `skills/binance/vip-loan/SKILL.md`
- `skills/binance/vip-loan/references/authentication.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
