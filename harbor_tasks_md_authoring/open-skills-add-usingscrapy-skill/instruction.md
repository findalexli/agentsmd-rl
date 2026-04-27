# Add using-scrapy skill

Source: [besoeasy/open-skills#12](https://github.com/besoeasy/open-skills/pull/12)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/using-scrapy/SKILL.md`

## What to add / change

Adds a new skill for [Scrapy](https://github.com/scrapy/scrapy), a Python web crawling and scraping framework suited for large-scale, structured data extraction.

## New skill: `skills/using-scrapy/SKILL.md`

- **`basic_usage`** — CSS-selector spider with pagination following, output to JSON/CSV
- **`robust_usage`** — Production spider with autothrottle, configurable delays, retry logic, `errback` error handling, and `FEEDS` config; includes `CrawlerProcess` for script-mode execution (no project required)
- **`extract_with_xpath`** — XPath variant for complex HTML structures

```python
class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com"]

    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(),
                "author": quote.css("small.author::text").get(),
                "tags": quote.css("a.tag::text").getall(),
            }
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

Includes rate limiting best practices (`ROBOTSTXT_OBEY`, `AUTOTHROTTLE_ENABLED`), troubleshooting for common errors (403, 429, JS-rendered content), agent prompt, and cross-links to related scraping skills.

<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

> 
> ----
> 
> *This section details on the original issue y

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
