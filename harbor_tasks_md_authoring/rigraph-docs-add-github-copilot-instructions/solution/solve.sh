#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rigraph

# Idempotency guard
if grep -qF "> **Note**: For general development guidelines, code style conventions, and AI a" ".github/copilot-instructions.md" && grep -qF "It provides routines for simple graphs and network analysis, handles large graph" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -0,0 +1,12 @@
+# GitHub Copilot Instructions for igraph/rigraph
+
+> **Note**: For general development guidelines, code style conventions, and AI agent instructions, see [`AGENTS.md`](../AGENTS.md) in the repository root.
+
+## Common Commands for Copilot Chat
+
+- Load for development: `pkgload::load_all()`
+- Run tests: `testthat::test_local(reporter = "check")`
+- Format code: `air format .`
+- Update documentation: `devtools::document()`
+
+Refer to `AGENTS.md` for more instructions.
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,38 +1,103 @@
 # AI Agent Development Guidelines for igraph
 
+> **Note**: For GitHub Copilot-specific instructions, see [`.github/copilot-instructions.md`](.github/copilot-instructions.md).
+
 ## Project Overview
 
-igraph is an R package with routines for simple graphs and network analysis. It can handle large graphs very well and provides functions for generating random and regular graphs, graph visualization, centrality methods and much more.
+igraph is an R package for network analysis and graph theory.
+It provides routines for simple graphs and network analysis, handles large graphs efficiently, and includes functions for generating random and regular graphs, graph visualization, centrality methods, and much more.
+
+## Key Technologies
+
+- **Language**: R with C/C++ backend (uses the igraph C library)
+- **Testing**: testthat framework
+- **Documentation**: roxygen2 with Markdown syntax
+- **Code Formatting**: air (R formatting tool)
+- **Build System**: R CMD, devtools, Makefile
+- **Code Generation**: Stimulus framework (see `tools/README.md`)
+
+## Development Setup
+
+### Installation and Dependencies
+
+```r
+# Install all dependencies
+pak::pak()
+# Install build dependencies
+pak::pak(dependencies = "Config/Needs/build")
+```
 
-## Install and run R
+### Install and run R
 
 - When run on GitHub Actions, assume that R, the package in its current state and all dependencies are installed.
 - Only install new packages when needed for implementing new features or tests.
-- Run `R -q -e 'testthat::test_local(reporter = "check")` to execute tests as a final step.
+- Run `R -q -e 'testthat::test_local(reporter = "check")'` to execute tests as a final step.
+
+### Building and Testing
+
+- Load package for development: `pkgload::load_all()`
+- Run tests: `testthat::test_local(reporter = "check")`
+- Build package: `devtools::build()`
+- Check package: `devtools::check()`
+- Update documentation: `devtools::document()`
+- Format code: `air format .`
 
 ## Code Style and Documentation
 
 ### PR and Commit Style
 
-- PRs and commits use the conventional commit style with backticks for code references such as `function_call()` .
-- PRs are generally squashed, a clean history within a PR is not necessary.
+- IMPORTANT: PR titles end up in `NEWS.md` grouped by conventional commit label. PRs and commits use the conventional commit style with backticks for code references such as `function_call()`
+- PRs are generally squashed, a clean history within a PR is not necessary
 
 ### Comment Style
 
-- Add comprehensive comments to utility functions that aren't immediately obvious
-- Use line breaks after each sentence in multi-sentence comments
+- Prefer expressive code over comments where possible
+- Add comments to utility functions that cannot be made immediately obvious
 - Focus comments on explaining the "why" and "how", the "what" should be clear from the code itself
-- Include context about the function's role in the testing framework
+- Use line breaks after each sentence in multi-sentence comments
 
 ### R Code Conventions
 
-- Follow existing naming conventions (snake_case for functions, camelCase for some legacy functions)
+- Follow the [tidyverse style guide](https://style.tidyverse.org)
+- Use `snake_case` for new functions
 - Use explicit package prefixes (e.g., `withr::local_db_connection()`) for clarity
-- Maintain consistent indentation and spacing patterns
-- Use meaningful variable names that reflect the testing context
+- Maintain consistent indentation (2 spaces) and spacing patterns
+- Use meaningful variable names that reflect context
 - Run `air format .` before committing changes to ensure consistent formatting
-- Keep documentation in sync with code changes. When updating roxygen2 documentation, ensure that each sentence is on its own line for better readability. Run `R -q -e 'devtools::document()'` to update the documentation.
 
-## Code Generation
+### Documentation
+
+- Use roxygen2 with Markdown syntax for all function documentation
+- Keep each sentence on its own line in roxygen2 comments for better readability
+- Document internal functions using devtag (work in progress)
+- Link to C documentation using `@cdocs` tag: `#' @cdocs igraph_function_name`
+- Always run `devtools::document()` after updating documentation
+
+### Naming Conventions
+
+- Use `max` for maximal (graph theory term: a vertex is maximal if no other vertex dominates it) and `largest` for maximum (the biggest value in a set)
+
+## File Structure and Organization
+
+### Test Files
+
+- Test files should align with source files
+- `R/name.R` → `tests/testthat/test-name.R`
+
+### Generated Files
+
+**Do not modify these files directly:**
+
+- `src/rinterface.c` (generated by Stimulus)
+- `R/aaa-auto.R` (generated by Stimulus)
+
+Update them using: `make -f Makefile-cigraph src/rinterface.c R/aaa-auto.R`
 
 See `tools/README.md` for guidelines on code generation using the Stimulus framework.
+
+## Testing
+
+- Add test cases for all new functionality
+- For newly created autogenerated functions, always add a test to `test-aaa-auto.R`
+- Test file naming should mirror source file naming
+- Run tests frequently during development and at the end: `testthat::test_local(reporter = "check")`
PATCH

echo "Gold patch applied."
