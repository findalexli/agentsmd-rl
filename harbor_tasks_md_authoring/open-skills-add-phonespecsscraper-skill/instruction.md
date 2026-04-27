# Add phone-specs-scraper skill

Source: [besoeasy/open-skills#8](https://github.com/besoeasy/open-skills/pull/8)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/phone-specs-scraper/SKILL.md`

## What to add / change

## Summary

Adds a comprehensive skill for scraping smartphone specifications from multiple sources including GSM Arena, PhoneDB, MK Mobile Arena, and others.

### What's included:
- Bash and Node.js methods for scraping phone specs
- Search functionality using SearXNG to find comparison pages
- Comparison logic with automatic upgrade/downgrade detection
- Support for 8+ phone specification websites
- Code examples for extracting detailed technical specs
- Rate limiting and best practices guidance

### Use cases:
- Comparing smartphone specifications side-by-side
- Building phone comparison tools
- Researching device features before purchase
- Automated phone database population

### Example usage demonstrated:
Created detailed Pixel 9 vs Pixel 10 comparison report showing:
- 7 major upgrades (telephoto camera, brighter display, larger battery, etc.)
- 4 downgrades (lower MP counts, Wi-Fi 7 removal)
- 10 unchanged specifications
- ASCII visualizations for quick comparison

The skill follows the existing template format with both Bash and Node.js examples.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
