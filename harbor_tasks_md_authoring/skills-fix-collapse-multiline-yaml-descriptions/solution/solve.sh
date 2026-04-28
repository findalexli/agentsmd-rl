#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "description: Create and use brand.yml files for consistent branding across Shiny" "brand-yml/SKILL.md" && grep -qF "description: Conduct rigorous, adversarial code reviews with zero tolerance for " "posit-dev/critical-code-reviewer/SKILL.md" && grep -qF "description: Research a codebase and create architectural documentation describi" "posit-dev/describe-design/SKILL.md" && grep -qF "description: Generate accessible alt text for data visualizations in Quarto docu" "quarto/quarto-alt-text/SKILL.md" && grep -qF "description: Writing and authoring Quarto documents (.qmd), including code cell " "quarto/quarto-authoring/SKILL.md" && grep -qF "description: Guidance for managing R package lifecycle according to tidyverse pr" "r-lib/lifecycle/SKILL.md" && grep -qF "description: Help users write correct R code for async, parallel, and distribute" "r-lib/mirai/SKILL.md" && grep -qF "description: Build command-line apps in R using the Rapp package. Use when creat" "r-lib/r-cli-app/SKILL.md" && grep -qF "description: R package development with devtools, testthat, and roxygen2. Use wh" "r-lib/r-package-development/SKILL.md" && grep -qF "description: Best practices for writing R package tests using testthat version 3" "r-lib/testing-r-packages/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/brand-yml/SKILL.md b/brand-yml/SKILL.md
@@ -1,16 +1,9 @@
 ---
 name: brand-yml
-description: >
-  Create and use brand.yml files for consistent branding across Shiny apps and Quarto documents.
-  Use when working with brand styling, colors, fonts, logos, or corporate identity in Shiny or
-  Quarto projects. Covers: (1) Creating new _brand.yml files from brand guidelines, (2) Applying
-  brand.yml to Shiny for R apps with bslib, (3) Applying brand.yml to Shiny for Python apps with
-  ui.Theme, (4) Using brand.yml in Quarto documents, presentations, dashboards, and PDFs, (5)
-  Modifying existing brand.yml files, (6) Troubleshooting brand integration issues. Includes
-  complete specifications and framework-specific integration guides.
+description: Create and use brand.yml files for consistent branding across Shiny apps and Quarto documents. Covers: (1) Creating new _brand.yml files, (2) Applying to Shiny (R and Python), (3) Using in Quarto, (4) Modifying existing files, and (5) Troubleshooting. Includes complete specifications and integration guides.
 metadata:
   author: Garrick Aden-Buie (@gadenbuie)
-  version: "1.0"
+  version: "1.1"
 license: MIT
 ---
 
@@ -384,4 +377,4 @@ Include Bootstrap color names when possible, either defined directly or as alias
 - **Validate incrementally**: Start with minimal structure, test, then add complexity
 - **Use references**: Define colors in palette, then reference by name in semantic colors
 - **Standard file name**: Use `_brand.yml` for automatic discovery
-- **Explicit paths**: Use custom file names only when necessary (shared branding, multiple variants)
+- **Explicit paths**: Use custom file names only when necessary (shared branding, multiple variants)
\ No newline at end of file
diff --git a/posit-dev/critical-code-reviewer/SKILL.md b/posit-dev/critical-code-reviewer/SKILL.md
@@ -1,17 +1,9 @@
 ---
 name: critical-code-reviewer
-description: >
-  Conduct rigorous, adversarial code reviews with zero tolerance for mediocrity.
-  Use when users ask to "critically review" my code or a PR, "critique my code",
-  "find issues in my code", or "what's wrong with this code". Identifies
-  security holes, lazy patterns, edge case failures, and bad practices across
-  Python, R, JavaScript/TypeScript, SQL, and front-end code. Scrutinizes error
-  handling, type safety, performance, accessibility, and code quality. Provides
-  structured feedback with severity tiers (Blocking, Required, Suggestions) and
-  specific, actionable recommendations.
+description: Conduct rigorous, adversarial code reviews with zero tolerance for mediocrity. Use when users ask to "critically review" my code or a PR, "critique my code", "find issues in my code", or "what's wrong with this code". Identifies security holes, lazy patterns, edge case failures, and bad practices across Python, R, JavaScript/TypeScript, SQL, and front-end code. Scrutinizes error handling, type safety, performance, accessibility, and code quality. Provides structured feedback with severity tiers (Blocking, Required, Suggestions) and specific, actionable recommendations.
 metadata:
   author: Garrick Aden-Buie (@gadenbuie)
-  version: "1.0"
+  version: "1.1"
 license: MIT
 ---
 
@@ -193,4 +185,4 @@ Request Changes | Needs Discussion | Approve
 [Numbered options for proceeding, e.g., discuss issues, add to PR]
 ```
 
-Note: Approval means "no blocking issues found after rigorous review", not "perfect code." Don't manufacture problems to avoid approving.
+Note: Approval means "no blocking issues found after rigorous review", not "perfect code." Don't manufacture problems to avoid approving.
\ No newline at end of file
diff --git a/posit-dev/describe-design/SKILL.md b/posit-dev/describe-design/SKILL.md
@@ -1,15 +1,9 @@
 ---
 name: describe-design
-description: >
-  Research a codebase and create architectural documentation describing how features
-  or systems work. Use when the user asks to: (1) Document how a feature works,
-  (2) Create an architecture overview, (3) Explain code structure for onboarding or
-  knowledge transfer, (4) Research and describe a system's design. Produces markdown
-  documents with Mermaid diagrams and stable code references suitable for humans and
-  AI agents.
+description: Research a codebase and create architectural documentation describing how features or systems work. Use when the user asks to: (1) Document how a feature works, (2) Create an architecture overview, (3) Explain code structure for onboarding or knowledge transfer, (4) Research and describe a system's design. Produces markdown documents with Mermaid diagrams and stable code references suitable for humans and AI agents.
 metadata:
   author: Garrick Aden-Buie (@gadenbuie)
-  version: "1.0"
+  version: "1.1"
 license: MIT
 ---
 
@@ -212,4 +206,4 @@ with unrelated components.
 - **Structure for scanning**: Use headers, tables, and lists for quick navigation.
 - **Be specific**: Include actual file paths, function names, and config keys.
 - **Serve two audiences**: Write clearly for humans; use consistent structure for AI.
-- **Stay current**: Note any assumptions about code state or version.
+- **Stay current**: Note any assumptions about code state or version.
\ No newline at end of file
diff --git a/quarto/quarto-alt-text/SKILL.md b/quarto/quarto-alt-text/SKILL.md
@@ -1,13 +1,9 @@
 ---
 name: quarto-alt-text
-description: >
-  Generate accessible alt text for data visualizations in Quarto documents. Use
-  when the user wants to add, improve, or review alt text for figures in .qmd
-  files. Triggers for requests about accessibility, figure descriptions, fig-alt,
-  screen reader support, or making Quarto documents more accessible.
+description: Generate accessible alt text for data visualizations in Quarto documents. Use when the user wants to add, improve, or review alt text for figures in .qmd files. Triggers for requests about accessibility, figure descriptions, fig-alt, screen reader support, or making Quarto documents more accessible.
 metadata:
   author: Emil Hvitfeldt (@emilhvitfeldt)
-  version: "1.0"
+  version: "1.1"
 license: MIT
 ---
 
@@ -201,4 +197,4 @@ plotting_data |>
 #|   normal distribution curve overlaid on the bottom panel clearly does not
 #|   match the data, demonstrating that normalization preserves distribution
 #|   shape rather than creating normality.
-```
+```
\ No newline at end of file
diff --git a/quarto/quarto-authoring/SKILL.md b/quarto/quarto-authoring/SKILL.md
@@ -1,15 +1,9 @@
 ---
 name: quarto-authoring
-description: >
-  Writing and authoring Quarto documents (.qmd), including code cell options,
-  figure and table captions, cross-references, callout blocks (notes, warnings,
-  tips), citations and bibliography, page layout and columns, Mermaid diagrams,
-  YAML metadata configuration, and Quarto extensions. Also covers converting and
-  migrating R Markdown (.Rmd), bookdown, blogdown, xaringan, and distill projects
-  to Quarto, and creating Quarto websites, books, presentations, and reports.
+description: Writing and authoring Quarto documents (.qmd), including code cell options, figure and table captions, cross-references, callout blocks (notes, warnings, tips), citations and bibliography, page layout and columns, Mermaid diagrams, YAML metadata configuration, and Quarto extensions. Also covers converting and migrating R Markdown (.Rmd), bookdown, blogdown, xaringan, and distill projects to Quarto, and creating Quarto websites, books, presentations, and reports.
 metadata:
   author: Mickaël Canouil (@mcanouil)
-  version: "1.2"
+  version: "1.3"
 license: MIT
 ---
 
@@ -316,4 +310,4 @@ format:
 - [Quarto Documentation](https://quarto.org/docs/)
 - [Quarto Guide](https://quarto.org/docs/guide/)
 - [Quarto Extensions](https://quarto.org/docs/extensions/)
-- [Community Extensions List](https://m.canouil.dev/quarto-extensions/)
+- [Community Extensions List](https://m.canouil.dev/quarto-extensions/)
\ No newline at end of file
diff --git a/r-lib/lifecycle/SKILL.md b/r-lib/lifecycle/SKILL.md
@@ -1,16 +1,9 @@
 ---
 name: lifecycle
-description: >
-  Guidance for managing R package lifecycle according to tidyverse principles
-  using the lifecycle package. Use when: (1) Setting up lifecycle
-  infrastructure in a package, (2) Deprecating functions or arguments,
-  (3) Renaming functions or arguments, (4) Superseding functions, (5) Marking
-  functions as experimental, (6) Understanding lifecycle stages (stable,
-  experimental, deprecated, superseded), or (7) Writing deprecation helpers for
-  complex scenarios.
+description: Guidance for managing R package lifecycle according to tidyverse principles using the lifecycle package. Use when: (1) Setting up lifecycle infrastructure in a package, (2) Deprecating functions or arguments, (3) Renaming functions or arguments, (4) Superseding functions, (5) Marking functions as experimental, (6) Understanding lifecycle stages (stable, experimental, deprecated, superseded), or (7) Writing deprecation helpers for complex scenarios.
 metadata:
   author: Garrick Aden-Buie (@gadenbuie)
-  version: "1.0"
+  version: "1.1"
 license: MIT
 ---
 
@@ -254,4 +247,4 @@ The `what` fragment must work with "was deprecated in..." appended.
 
 ## Reference
 
-See `references/lifecycle-stages.md` for detailed stage definitions and transitions.
+See `references/lifecycle-stages.md` for detailed stage definitions and transitions.
\ No newline at end of file
diff --git a/r-lib/mirai/SKILL.md b/r-lib/mirai/SKILL.md
@@ -1,15 +1,9 @@
 ---
 name: mirai
-description: >
-  Help users write correct R code for async, parallel, and distributed
-  computing using mirai. Use when users need to: run R code asynchronously
-  or in parallel, write mirai code with correct dependency passing, set up
-  local or remote parallel workers, convert code from future or parallel,
-  use parallel map operations, integrate async tasks with Shiny or promises,
-  or configure cluster/HPC computing.
+description: Help users write correct R code for async, parallel, and distributed computing using mirai. Use when users need to: run R code asynchronously or in parallel, write mirai code with correct dependency passing, set up local or remote parallel workers, convert code from future or parallel, use parallel map operations, integrate async tasks with Shiny or promises, or configure cluster/HPC computing.
 metadata:
   author: Charlie Gao (@shikokuchuo)
-  version: "1.0"
+  version: "1.1"
 license: MIT
 ---
 
@@ -449,4 +443,4 @@ mirai_map(1:10, function(x) {
   daemons(0)
   result
 })[]
-```
+```
\ No newline at end of file
diff --git a/r-lib/r-cli-app/SKILL.md b/r-lib/r-cli-app/SKILL.md
@@ -1,14 +1,9 @@
 ---
 name: r-cli-app
-description: >
-  Build command-line apps in R using the Rapp package. Use when creating
-  a CLI tool in R, adding argument parsing to an R script, turning an R
-  script into a command-line app, shipping CLIs in an R package, or
-  using Rapp (the alternative Rscript front-end). Also use for shebang
-  scripts, exec/ directory in R packages, or subcommand-based R tools.
+description: Build command-line apps in R using the Rapp package. Use when creating a CLI tool in R, adding argument parsing to an R script, turning an R script into a command-line app, shipping CLIs in an R package, or using Rapp (the alternative Rscript front-end). Also use for shebang scripts, exec/ directory in R packages, or subcommand-based R tools.
 metadata:
   author: Garrick Aden-Buie (@gadenbuie)
-  version: "1.0"
+  version: "1.1"
 license: MIT
 ---
 
@@ -236,6 +231,8 @@ Every Rapp automatically gets `--help` (human-readable) and `--help-yaml`
 
 ## Development and Testing
 
+### Interactive Development
+
 Use `Rapp::run()` to test scripts from an R session:
 
 ```r
@@ -246,6 +243,18 @@ Rapp::run("path/to/myapp.R", c("--name", "Alice", "--count", "5"))
 It returns the evaluation environment (invisibly) for inspection, and
 supports `browser()` for interactive debugging.
 
+### Testing CLI Apps in Packages
+
+Use `Rapp::run()` with `testthat` snapshot testing. Test computed values by
+accessing the returned environment, and test output with `expect_snapshot()`.
+
+**See [references/advanced.md](references/advanced.md#testing-cli-apps)** for
+detailed testing patterns, including:
+
+- Accessing computed values via the evaluation environment
+- Snapshot testing for help output and formatted text
+- Testing file side effects and state changes
+
 ---
 
 ## Complete Example: Coin Flipper
@@ -431,4 +440,4 @@ tryCatch({
 For less common topics — launcher customization (`#| launcher:` front matter),
 detailed `Rapp::install_pkg_cli_apps()` API options, and more complete examples
 (deduplication filter, variadic install-pkg, interactive fallback) — read
-`references/advanced.md`.
+`references/advanced.md`.
\ No newline at end of file
diff --git a/r-lib/r-package-development/SKILL.md b/r-lib/r-package-development/SKILL.md
@@ -1,9 +1,9 @@
 ---
 name: r-package-development
-description: >
-  R package development with devtools, testthat, and roxygen2. Use when the
-  user is working on an R package, running tests, writing documentation, or
-  building package infrastructure.
+description: R package development with devtools, testthat, and roxygen2. Use when the user is working on an R package, running tests, writing documentation, or building package infrastructure.
+metadata:
+  author: Simon P. Couch (@simonpcouch)
+  version: "1.1"
 ---
 
 # R package development
@@ -69,4 +69,4 @@ air format .
 - Each bullet should briefly describe the change to the end user and mention the related issue in parentheses.
 - A bullet can consist of multiple sentences but should not contain any new lines (i.e. DO NOT line wrap).
 - If the change is related to a function, put the name of the function early in the bullet.
-- Order bullets alphabetically by function name. Put all bullets that don't mention function names at the beginning.
+- Order bullets alphabetically by function name. Put all bullets that don't mention function names at the beginning.
\ No newline at end of file
diff --git a/r-lib/testing-r-packages/SKILL.md b/r-lib/testing-r-packages/SKILL.md
@@ -1,10 +1,9 @@
 ---
 name: testing-r-packages
-description: >
-  Best practices for writing R package tests using testthat version 3+. Use when writing, organizing, or improving tests for R packages. Covers test structure, expectations, fixtures, snapshots, mocking, and modern testthat 3 patterns including self-sufficient tests, proper cleanup with withr, and snapshot testing.
+description: Best practices for writing R package tests using testthat version 3+. Use when writing, organizing, or improving tests for R packages. Covers test structure, expectations, fixtures, snapshots, mocking, and modern testthat 3 patterns including self-sufficient tests, proper cleanup with withr, and snapshot testing.
 metadata:
   author: Garrick Aden-Buie (@gadenbuie)
-  version: "1.0"
+  version: "1.1"
 license: MIT
 ---
 
@@ -425,4 +424,4 @@ When working with testthat 3 code, prefer modern patterns:
 
 **Find slow tests:** `devtools::test(reporter = "slow")`
 
-**Shuffle tests:** `devtools::test(shuffle = TRUE)`
+**Shuffle tests:** `devtools::test(shuffle = TRUE)`
\ No newline at end of file
PATCH

echo "Gold patch applied."
