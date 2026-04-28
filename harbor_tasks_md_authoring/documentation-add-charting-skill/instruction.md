# Add Charting SKILL

Source: [QuantConnect/Documentation#2325](https://github.com/QuantConnect/Documentation/pull/2325)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `03 Writing Algorithms/36 Charting/SKILL.md`

## What to add / change

## Summary

Adds a Skill file at `03 Writing Algorithms/36 Charting/SKILL.md` modeled on the existing Scheduled Events and Logging skills. Gives an agent the rules it needs to add custom charts to a QuantConnect/LEAN algorithm without silently truncating the output.

Three hard, silent-failure rules are elevated to `## Critical rule:` sections:

- Don't reuse reserved chart names (`Assets Sales Volume`, `Exposure`, `Portfolio Margin`) or reserved series names inside default charts (`Equity`, `Return`, `Equity Drawdown`, `Benchmark`, `Portfolio Turnover`, `Strategy Capacity`).
- Count every series against the tier cap before adding (10 on Free/QR, 25 on Team/Trading Firm, 100 on Institution), built-ins included — if over cap, collapse loops into buckets/summary series, push per-symbol detail to the Object Store, or ask the user which charts matter most.
- Stay under the per-series data-points cap — only a concern at minute/second/tick resolution (or handlers plotting many times per day). `plot_indicator` is the preferred call at daily/hourly resolution; on minute/second/tick, switch to `plot(chart, indicator)` from `on_end_of_day`.

Also covers: the six `SeriesType` members and which data shape each fits, auto-creation on first `plot` call, `series index` for overlay vs subchart, `CandlestickSeries` needing OHLC/`TradeBar` (and `QuoteBar.collapse()`), the `Indicator` vs `TradeBarIndicator` restriction in `plot_indicators`, and when to route bulk structured data to the Object S

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
