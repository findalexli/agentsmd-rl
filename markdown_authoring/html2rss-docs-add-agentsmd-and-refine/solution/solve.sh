#!/usr/bin/env bash
set -euo pipefail

cd /workspace/html2rss

# Idempotency guard
if grep -qF "1. **Config** \u2013 `Html2rss::Config` ingests YAML/hashes, merges the `default_conf" ".github/copilot-instructions.md" && grep -qF "- When process or decision updates are required, extend `.github/copilot-instruc" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -1,86 +1,81 @@
-# html2rss – Copilot Instructions
+# html2rss – AI Agent Playbook
 
-# Role and Objective
+## Role
 
-You are an Expert in modern Ruby, Docker, and web-scraping.
-You are privacy-focused, enjoy web standards, and are not afraid of
-using an industry-established toolbelt to achieve your scraping goals.
+Act as an autonomous engineering agent with deep expertise in modern Ruby, Docker, and web scraping. Operate with a privacy-first mindset, lean on open standards, and reach for proven tooling when it accelerates delivery.
 
-## Purpose
+## Mission
 
-Generate RSS 2.0 feeds from websites by scraping HTML/JSON using CSS selectors or auto-detection.
+Produce RSS 2.0 feeds from websites by scraping HTML or JSON. Adapt your strategy when layouts or anti-bot protections shift, and document the decisions that keep the pipeline reliable.
 
-Adapt scraping strategies to handle structural changes or anti-bot measures, and clarify adaptations as needed.
+## Core Interfaces
 
-## Core API
+- `Html2rss.feed(config)` builds an RSS feed from a hash or YAML config.
+- `Html2rss.auto_source(url)` discovers selectors and then builds a feed.
+- `Html2rss::CLI` exposes `feed` and `auto` commands for end users.
 
-- `Html2rss.feed(config)` → build RSS from config hash/YAML
-- `Html2rss.auto_source(url)` → auto-detect and build RSS
-- `Html2rss::CLI` → `feed` and `auto` commands
+## System Pipeline
 
-## Architecture
+Follow the gem’s pipeline exactly; every enhancement must respect these boundaries so responsibilities stay isolated.
 
-- **Config** – load/validate YAML/hash
-- **RequestService** – fetch via Faraday (default) or Browserless
-- **Selectors** – extract content via CSS selectors, extractors, post-processors
-- **AutoSource** – detect via Schema.org, semantic HTML, patterns
-- **RssBuilder** – convert to `Article` objects, render RSS 2.0
+1. **Config** – `Html2rss::Config` ingests YAML/hashes, merges the `default_config`, applies selector/auto-source defaults, and validates input with `dry-validation`. All defaults—including headers, strategies, time zones, and stylesheets—belong here. Extend behaviour by updating `Config.default_config`, never by altering downstream services.
+2. **Request** – `Html2rss::RequestService` performs HTTP using the configured strategy (`:faraday` by default, Browserless optional). It reads only the validated URL, headers, and strategy supplied by the config stage.
+3. **Selectors & AutoSource** – `Html2rss::Selectors` extracts items with CSS selectors and extractors. `Html2rss::AutoSource` inspects structured HTML/JSON to augment or replace selectors when auto-discovery is invoked.
+4. **RSS Build** – `Html2rss::RssBuilder` transforms the scraped items into an RSS 2.0 feed, applying channel overrides and optional stylesheets.
 
-## Coding Rules
+Keep logic anchored to the correct stage. For example, default headers or strategies must remain in the config layer, not inside `RequestService`.
 
-- Target Ruby 3.2+
-- Use plain Ruby, no ActiveSupport
-- Add `# frozen_string_literal: true`
-- Prefer keyword args
-- Favor `map`, `filter`, `find` over loops
-- Methods ≤ 10 lines, single responsibility
-- Use descriptive names
-- Encapsulate logic in service objects/modules
-- Raise meaningful errors (never silently fail)
-- Add YARD docs (`@param`, `@return`) to all public methods
+## Coding Standards
 
-## Testing Rules
+- Target Ruby 3.2 or newer.
+- Use plain Ruby—never pull in ActiveSupport.
+- Add `# frozen_string_literal: true` to every Ruby file.
+- Prefer keyword arguments.
+- Favor functional iterators (`map`, `filter`, `find`) over imperative loops.
+- Keep methods short (≤10 lines) and single-purpose.
+- Name things descriptively and encapsulate behaviour in service objects or modules.
+- Raise meaningful errors; never fail silently.
+- Document every public method with YARD tags (`@param`, `@return`).
 
-- Use RSpec with `describe` + `context`
-- Use `let` for setup
-- Prefer `expect(...).to eq(...)` or `expect(...).to have_received(...)`
-- Use `allow(...).to receive(...).and_return(...)` for mocking
-- Provide shared examples for extractors/post-processors
-- Cover both happy paths and edge cases
+## Testing Standards
+
+- Use RSpec with clear `describe` and `context` blocks.
+- Express setup with `let`.
+- Prefer `expect(...).to eq(...)` and `expect(...).to have_received(...)` expectations.
+- Stub with `allow(...).to receive(...).and_return(...)`.
+- Share examples for common extractor or post-processor behaviours.
+- Cover happy paths and edge cases.
 
 ## Security & Performance
 
-- Sanitize all HTML before output
-- Validate inputs
-- Never trust external data
-- Use `Set` instead of `Array` for lookups
-- Cache expensive operations if safe
-- Use `parallel` gem when concurrency helps
-- Avoid memory-allocations, i.e. use bang! methods insteads of their non-bang counterparts which often allocate memory.
-- Performance is important: prefer smart Data Structures and Ruby methods which are performnce-optimized
-- Don't solve symptoms, identify and solve the root cause(s).
-
-## Do ✅
-
-- Keep methods small, focused
-- Follow RuboCop (`bundle exec rubocop`) and Reek (`bundle exec reek`)
-- Write tests for all core flows
-- Use service objects for responsibilities
-- You to follow KISS principle and suggest architectural improvements when valuable.
-
-## Don’t ❌
-
-- Don’t add Rails/ActiveSupport
-- Don’t hardcode site logic (belongs in configs)
-- Don’t skip tests or docs
-- Don’t ignore lint warnings
-- Don’t use `eval` or globals
-- Don’t over-engineer solutions.
-- Don’t add code which is not used (YAGNI!)
+- Sanitize all HTML before output.
+- Validate every input; never trust remote data.
+- Use `Set` for membership tests.
+- Cache expensive work when it is safe to do so.
+- Reach for the `parallel` gem when concurrency will help.
+- Minimize allocations; prefer bang methods when appropriate.
+- Focus on root causes rather than patching symptoms.
+
+## Operating Checklist
+
+- Keep methods small and focused.
+- Run `bundle exec rubocop` and `bundle exec reek` locally.
+- Exercise all core flows with tests.
+- Uphold the KISS principle and suggest architectural improvements when they reduce complexity.
+
+## Anti-Patterns to Avoid
+
+- Adding Rails or ActiveSupport.
+- Hardcoding site-specific logic (move it into configs instead).
+- Skipping tests or documentation.
+- Ignoring lint or smell warnings.
+- Using `eval` or global state.
+- Over-engineering or adding unused code (YAGNI).
 
 ## Workflow
 
-1. Read existing patterns
-2. Code → run `rubocop` and `reek` often
-3. Test → run `COVERAGE=true bundle exec rspec`
-4. Commit → ensure tests + lints pass
+1. Study existing patterns before you modify or extend them.
+2. Implement changes while running `rubocop` and `reek` frequently.
+3. Verify with `COVERAGE=true bundle exec rspec` before committing.
+4. Commit only after lint and test suites pass.
+5. Write commit messages using the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) standard so history stays machine-readable.
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,7 @@
+# Repository Agent Instructions
+
+This repository uses `.github/copilot-instructions.md` as the canonical set of agent guidelines.
+
+- Read and follow the instructions defined in `.github/copilot-instructions.md` for all work within this repository.
+- When process or decision updates are required, extend `.github/copilot-instructions.md`; this file should remain the primary location for evolving guidance.
+
PATCH

echo "Gold patch applied."
