# Agent Config Files for ruff-ruf073-fstring-percent-format

Repo: astral-sh/ruff
Commit: b491f7ebed9ea3be8ff7990dd6119c77c57baa74
Files found: 3


---
## AGENTS.md

```
   1 | # Ruff Repository
   2 | 
   3 | This repository contains both Ruff (a Python linter and formatter) and ty (a Python type checker). The crates follow a naming convention: `ruff_*` for Ruff-specific code and `ty_*` for ty-specific code. ty reuses several Ruff crates, including the Python parser (`ruff_python_parser`) and AST definitions (`ruff_python_ast`).
   4 | 
   5 | ## Running Tests
   6 | 
   7 | Run all tests (using `nextest` for faster execution, setting `CARGO_PROFILE_DEV_OPT_LEVEL=1` to enable optimizations while retaining debug info, and setting `INSTA_FORCE_PASS=1 INSTA_UPDATE=always` to ensure all snapshots are updated):
   8 | 
   9 | ```sh
  10 | CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always cargo nextest run
  11 | ```
  12 | 
  13 | Run tests for a specific crate:
  14 | 
  15 | ```sh
  16 | CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always cargo nextest run -p ty_python_semantic
  17 | ```
  18 | 
  19 | Run a single mdtest file. The path to the mdtest file should be relative to the `crates/ty_python_semantic/resources/mdtest` folder:
  20 | 
  21 | ```sh
  22 | CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always cargo nextest run -p ty_python_semantic -- mdtest::<path/to/mdtest_file.md>
  23 | ```
  24 | 
  25 | To run a specific mdtest within a file, use a substring of the Markdown header text as `MDTEST_TEST_FILTER`. Only use this if it's necessary to isolate a single test case:
  26 | 
  27 | ```sh
  28 | MDTEST_TEST_FILTER="<filter>" CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always cargo nextest run -p ty_python_semantic -- mdtest::<path/to/mdtest_file.md>
  29 | ```
  30 | 
  31 | After running the tests, always review the contents of any snapshots that have been added or updated.
  32 | 
  33 | ## Running Clippy
  34 | 
  35 | ```sh
  36 | cargo clippy --workspace --all-targets --all-features -- -D warnings
  37 | ```
  38 | 
  39 | ## Running Debug Builds
  40 | 
  41 | Use debug builds (not `--release`) when developing, as release builds lack debug assertions and have slower compile times.
  42 | 
  43 | Run Ruff:
  44 | 
  45 | ```sh
  46 | cargo run --bin ruff -- check path/to/file.py
  47 | ```
  48 | 
  49 | Run ty:
  50 | 
  51 | ```sh
  52 | cargo run --bin ty -- check path/to/file.py
  53 | ```
  54 | 
  55 | ## Reproducing and minimizing ty ecosystem changes
  56 | 
  57 | If asked to reproduce changes in the ty ecosystem, use this script to clone the project to some
  58 | directory and install its dependencies into `.venv`:
  59 | 
  60 | ```sh
  61 | uv run scripts/setup_primer_project.py <project-name> <some-temp-dir>
  62 | ```
  63 | 
  64 | If asked to *minimize* a change in the ty ecosystem, you should start off with the above command to ensure that the change reproduces. You should then attempt to minimize the Python code required to demonstrate a behaviour difference between ty on your feature branch and ty on the main branch. Your minimization process should consist of systematically removing files from the cloned ecosystem project, and stripping content from existing files, until the behaviour difference between your branch and `main` no longer reproduces.
  65 | 
  66 | ## Pull Requests
  67 | 
  68 | When working on ty, PR titles should start with `[ty]` and be tagged with the `ty` GitHub label.
  69 | 
  70 | ## Development Guidelines
  71 | 
  72 | - All changes must be tested. If you're not testing your changes, you're not done.
  73 | - Look to see if your tests could go in an existing file before adding a new file for your tests.
  74 | - Get your tests to pass. If you didn't run the tests, your code does not work.
  75 | - Follow existing code style. Check neighboring files for patterns.
  76 | - Rust imports should always go at the top of the file, never locally in functions.
  77 | - Always run `uvx prek run -a` at the end of a task, after every rebase, after addressing any review comment, and before pushing any code.
  78 | - Avoid writing significant amounts of new code. This is often a sign that we're missing an existing method or mechanism that could help solve the problem. Look for existing utilities first.
  79 | - Try hard to avoid patterns that require `panic!`, `unreachable!`, or `.unwrap()`. Instead, try to encode those constraints in the type system. Don't be afraid to write code that's more verbose or requires largeish refactors if it enables you to avoid these unsafe calls.
  80 | - Prefer let chains (`if let` combined with `&&`) over nested `if let` statements to reduce indentation and improve readability. At the end of a task, always check your work to see if you missed opportunities to use `let` chains.
  81 | - If you *have* to suppress a Clippy lint, prefer to use `#[expect()]` over `[allow()]`, where possible. But if a lint is complaining about unused/dead code, it's usually best to just delete the unused code.
  82 | - Use comments purposefully. Don't use comments to narrate code, but do use them to explain invariants and why something unusual was done a particular way.
  83 | - When adding new ty checks, it's important to make error messages concise. Think about how an error message would look on a narrow terminal screen. Sometimes more detail can be provided in subdiagnostics or secondary annotations, but it's also important to make sure that the diagnostic is understandable if the user has passed `--output-format=concise`.
  84 | - **Salsa incrementality (ty):** Any method that accesses `.node()` must be `#[salsa::tracked]`, or it will break incrementality. Prefer higher-level semantic APIs over raw AST access.
  85 | - Run `cargo dev generate-all` after changing configuration options, CLI arguments, lint rules, or environment variable definitions, as these changes require regeneration of schemas, docs, and CLI references.
```


---
## CLAUDE.md

```
   1 | @AGENTS.md
```


---
## README.md

```
   1 | <!-- Begin section: Overview -->
   2 | 
   3 | # Ruff
   4 | 
   5 | [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
   6 | [![image](https://img.shields.io/pypi/v/ruff.svg)](https://pypi.python.org/pypi/ruff)
   7 | [![image](https://img.shields.io/pypi/l/ruff.svg)](https://github.com/astral-sh/ruff/blob/main/LICENSE)
   8 | [![image](https://img.shields.io/pypi/pyversions/ruff.svg)](https://pypi.python.org/pypi/ruff)
   9 | [![Actions status](https://github.com/astral-sh/ruff/workflows/CI/badge.svg)](https://github.com/astral-sh/ruff/actions)
  10 | [![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?logo=discord&logoColor=white)](https://discord.com/invite/astral-sh)
  11 | 
  12 | [**Docs**](https://docs.astral.sh/ruff/) | [**Playground**](https://play.ruff.rs/)
  13 | 
  14 | An extremely fast Python linter and code formatter, written in Rust.
  15 | 
  16 | <p align="center">
  17 |   <picture align="center">
  18 |     <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/1309177/232603514-c95e9b0f-6b31-43de-9a80-9e844173fd6a.svg">
  19 |     <source media="(prefers-color-scheme: light)" srcset="https://user-images.githubusercontent.com/1309177/232603516-4fb4892d-585c-4b20-b810-3db9161831e4.svg">
  20 |     <img alt="Shows a bar chart with benchmark results." src="https://user-images.githubusercontent.com/1309177/232603516-4fb4892d-585c-4b20-b810-3db9161831e4.svg">
  21 |   </picture>
  22 | </p>
  23 | 
  24 | <p align="center">
  25 |   <i>Linting the CPython codebase from scratch.</i>
  26 | </p>
  27 | 
  28 | - ⚡️ 10-100x faster than existing linters (like Flake8) and formatters (like Black)
  29 | - 🐍 Installable via `pip`
  30 | - 🛠️ `pyproject.toml` support
  31 | - 🤝 Python 3.14 compatibility
  32 | - ⚖️ Drop-in parity with [Flake8](https://docs.astral.sh/ruff/faq/#how-does-ruffs-linter-compare-to-flake8), isort, and [Black](https://docs.astral.sh/ruff/faq/#how-does-ruffs-formatter-compare-to-black)
  33 | - 📦 Built-in caching, to avoid re-analyzing unchanged files
  34 | - 🔧 Fix support, for automatic error correction (e.g., automatically remove unused imports)
  35 | - 📏 Over [800 built-in rules](https://docs.astral.sh/ruff/rules/), with native re-implementations
  36 |     of popular Flake8 plugins, like flake8-bugbear
  37 | - ⌨️ First-party [editor integrations](https://docs.astral.sh/ruff/editors) for [VS Code](https://github.com/astral-sh/ruff-vscode) and [more](https://docs.astral.sh/ruff/editors/setup)
  38 | - 🌎 Monorepo-friendly, with [hierarchical and cascading configuration](https://docs.astral.sh/ruff/configuration/#config-file-discovery)
  39 | 
  40 | Ruff aims to be orders of magnitude faster than alternative tools while integrating more
  41 | functionality behind a single, common interface.
  42 | 
  43 | Ruff can be used to replace [Flake8](https://pypi.org/project/flake8/) (plus dozens of plugins),
  44 | [Black](https://github.com/psf/black), [isort](https://pypi.org/project/isort/),
  45 | [pydocstyle](https://pypi.org/project/pydocstyle/), [pyupgrade](https://pypi.org/project/pyupgrade/),
  46 | [autoflake](https://pypi.org/project/autoflake/), and more, all while executing tens or hundreds of
  47 | times faster than any individual tool.
  48 | 
  49 | Ruff is extremely actively developed and used in major open-source projects like:
  50 | 
  51 | - [Apache Airflow](https://github.com/apache/airflow)
  52 | - [Apache Superset](https://github.com/apache/superset)
  53 | - [FastAPI](https://github.com/tiangolo/fastapi)
  54 | - [Hugging Face](https://github.com/huggingface/transformers)
  55 | - [Pandas](https://github.com/pandas-dev/pandas)
  56 | - [SciPy](https://github.com/scipy/scipy)
  57 | 
  58 | ...and [many more](#whos-using-ruff).
  59 | 
  60 | Ruff is backed by [Astral](https://astral.sh), the creators of
  61 | [uv](https://github.com/astral-sh/uv) and [ty](https://github.com/astral-sh/ty).
  62 | 
  63 | Read the [launch
  64 | post](https://astral.sh/blog/announcing-astral-the-company-behind-ruff), or the
  65 | original [project
  66 | announcement](https://notes.crmarsh.com/python-tooling-could-be-much-much-faster).
  67 | 
  68 | ## Testimonials
  69 | 
  70 | [**Sebastián Ramírez**](https://twitter.com/tiangolo/status/1591912354882764802), creator
  71 | of [FastAPI](https://github.com/tiangolo/fastapi):
  72 | 
  73 | > Ruff is so fast that sometimes I add an intentional bug in the code just to confirm it's actually
  74 | > running and checking the code.
  75 | 
  76 | [**Nick Schrock**](https://twitter.com/schrockn/status/1612615862904827904), founder of [Elementl](https://www.elementl.com/),
  77 | co-creator of [GraphQL](https://graphql.org/):
  78 | 
  79 | > Why is Ruff a gamechanger? Primarily because it is nearly 1000x faster. Literally. Not a typo. On
  80 | > our largest module (dagster itself, 250k LOC) pylint takes about 2.5 minutes, parallelized across 4
  81 | > cores on my M1. Running ruff against our _entire_ codebase takes .4 seconds.
  82 | 
  83 | [**Bryan Van de Ven**](https://github.com/bokeh/bokeh/pull/12605), co-creator
  84 | of [Bokeh](https://github.com/bokeh/bokeh/), original author
  85 | of [Conda](https://docs.conda.io/en/latest/):
  86 | 
  87 | > Ruff is ~150-200x faster than flake8 on my machine, scanning the whole repo takes ~0.2s instead of
  88 | > ~20s. This is an enormous quality of life improvement for local dev. It's fast enough that I added
  89 | > it as an actual commit hook, which is terrific.
  90 | 
  91 | [**Timothy Crosley**](https://twitter.com/timothycrosley/status/1606420868514877440),
  92 | creator of [isort](https://github.com/PyCQA/isort):
  93 | 
  94 | > Just switched my first project to Ruff. Only one downside so far: it's so fast I couldn't believe
  95 | > it was working till I intentionally introduced some errors.
  96 | 
  97 | [**Tim Abbott**](https://github.com/zulip/zulip/pull/23431#issuecomment-1302557034), lead developer of [Zulip](https://github.com/zulip/zulip) (also [here](https://github.com/astral-sh/ruff/issues/465#issuecomment-1317400028)):
  98 | 
  99 | > This is just ridiculously fast... `ruff` is amazing.
 100 | 
 101 | <!-- End section: Overview -->
 102 | 
 103 | ## Table of Contents
 104 | 
 105 | For more, see the [documentation](https://docs.astral.sh/ruff/).
 106 | 
 107 | 1. [Getting Started](#getting-started)
 108 | 1. [Configuration](#configuration)
 109 | 1. [Rules](#rules)
 110 | 1. [Contributing](#contributing)
 111 | 1. [Support](#support)
 112 | 1. [Acknowledgements](#acknowledgements)
 113 | 1. [Who's Using Ruff?](#whos-using-ruff)
 114 | 1. [License](#license)
 115 | 
 116 | ## Getting Started<a id="getting-started"></a>
 117 | 
 118 | For more, see the [documentation](https://docs.astral.sh/ruff/).
 119 | 
 120 | ### Installation
 121 | 
 122 | Ruff is available as [`ruff`](https://pypi.org/project/ruff/) on PyPI.
 123 | 
 124 | Invoke Ruff directly with [`uvx`](https://docs.astral.sh/uv/):
 125 | 
 126 | ```shell
 127 | uvx ruff check   # Lint all files in the current directory.
 128 | uvx ruff format  # Format all files in the current directory.
 129 | ```
 130 | 
 131 | Or install Ruff with `uv` (recommended), `pip`, or `pipx`:
 132 | 
 133 | ```shell
 134 | # With uv.
 135 | uv tool install ruff@latest  # Install Ruff globally.
 136 | uv add --dev ruff            # Or add Ruff to your project.
 137 | 
 138 | # With pip.
 139 | pip install ruff
 140 | 
 141 | # With pipx.
 142 | pipx install ruff
 143 | ```
 144 | 
 145 | Starting with version `0.5.0`, Ruff can be installed with our standalone installers:
 146 | 
 147 | ```shell
 148 | # On macOS and Linux.
 149 | curl -LsSf https://astral.sh/ruff/install.sh | sh
 150 | 
 151 | # On Windows.
 152 | powershell -c "irm https://astral.sh/ruff/install.ps1 | iex"
 153 | 
 154 | # For a specific version.
 155 | curl -LsSf https://astral.sh/ruff/0.15.7/install.sh | sh
 156 | powershell -c "irm https://astral.sh/ruff/0.15.7/install.ps1 | iex"
 157 | ```
 158 | 
 159 | You can also install Ruff via [Homebrew](https://formulae.brew.sh/formula/ruff), [Conda](https://anaconda.org/conda-forge/ruff),
 160 | and with [a variety of other package managers](https://docs.astral.sh/ruff/installation/).
 161 | 
 162 | ### Usage
 163 | 
 164 | To run Ruff as a linter, try any of the following:
 165 | 
 166 | ```shell
 167 | ruff check                          # Lint all files in the current directory (and any subdirectories).
 168 | ruff check path/to/code/            # Lint all files in `/path/to/code` (and any subdirectories).
 169 | ruff check path/to/code/*.py        # Lint all `.py` files in `/path/to/code`.
 170 | ruff check path/to/code/to/file.py  # Lint `file.py`.
 171 | ruff check @arguments.txt           # Lint using an input file, treating its contents as newline-delimited command-line arguments.
 172 | ```
 173 | 
 174 | Or, to run Ruff as a formatter:
 175 | 
 176 | ```shell
 177 | ruff format                          # Format all files in the current directory (and any subdirectories).
 178 | ruff format path/to/code/            # Format all files in `/path/to/code` (and any subdirectories).
 179 | ruff format path/to/code/*.py        # Format all `.py` files in `/path/to/code`.
 180 | ruff format path/to/code/to/file.py  # Format `file.py`.
 181 | ruff format @arguments.txt           # Format using an input file, treating its contents as newline-delimited command-line arguments.
 182 | ```
 183 | 
 184 | Ruff can also be used as a [pre-commit](https://pre-commit.com/) hook via [`ruff-pre-commit`](https://github.com/astral-sh/ruff-pre-commit):
 185 | 
 186 | ```yaml
 187 | - repo: https://github.com/astral-sh/ruff-pre-commit
 188 |   # Ruff version.
 189 |   rev: v0.15.7
 190 |   hooks:
 191 |     # Run the linter.
 192 |     - id: ruff-check
 193 |       args: [ --fix ]
 194 |     # Run the formatter.
 195 |     - id: ruff-format
 196 | ```
 197 | 
 198 | Ruff can also be used as a [VS Code extension](https://github.com/astral-sh/ruff-vscode) or with [various other editors](https://docs.astral.sh/ruff/editors/setup).
 199 | 
 200 | Ruff can also be used as a [GitHub Action](https://github.com/features/actions) via
 201 | [`ruff-action`](https://github.com/astral-sh/ruff-action):
 202 | 
 203 | ```yaml
 204 | name: Ruff
 205 | on: [ push, pull_request ]
 206 | jobs:
 207 |   ruff:
 208 |     runs-on: ubuntu-latest
 209 |     steps:
 210 |       - uses: actions/checkout@v4
 211 |       - uses: astral-sh/ruff-action@v3
 212 | ```
 213 | 
 214 | ### Configuration<a id="configuration"></a>
 215 | 
 216 | Ruff can be configured through a `pyproject.toml`, `ruff.toml`, or `.ruff.toml` file (see:
 217 | [_Configuration_](https://docs.astral.sh/ruff/configuration/), or [_Settings_](https://docs.astral.sh/ruff/settings/)
 218 | for a complete list of all configuration options).
 219 | 
 220 | If left unspecified, Ruff's default configuration is equivalent to the following `ruff.toml` file:
 221 | 
 222 | ```toml
 223 | # Exclude a variety of commonly ignored directories.
 224 | exclude = [
 225 |     ".bzr",
 226 |     ".direnv",
 227 |     ".eggs",
 228 |     ".git",
 229 |     ".git-rewrite",
 230 |     ".hg",
 231 |     ".ipynb_checkpoints",
 232 |     ".mypy_cache",
 233 |     ".nox",
 234 |     ".pants.d",
 235 |     ".pyenv",
 236 |     ".pytest_cache",
 237 |     ".pytype",
 238 |     ".ruff_cache",
 239 |     ".svn",
 240 |     ".tox",
 241 |     ".venv",
 242 |     ".vscode",
 243 |     "__pypackages__",
 244 |     "_build",
 245 |     "buck-out",
 246 |     "build",
 247 |     "dist",
 248 |     "node_modules",
 249 |     "site-packages",
 250 |     "venv",
 251 | ]
 252 | 
 253 | # Same as Black.
 254 | line-length = 88
 255 | indent-width = 4
 256 | 
 257 | # Assume Python 3.10
 258 | target-version = "py310"
 259 | 
 260 | [lint]
 261 | # Enable Pyflakes (`F`) and a subset of the pycodestyle (`E`) codes by default.
 262 | select = ["E4", "E7", "E9", "F"]
 263 | ignore = []
 264 | 
 265 | # Allow fix for all enabled rules (when `--fix`) is provided.
 266 | fixable = ["ALL"]
 267 | unfixable = []
 268 | 
 269 | # Allow unused variables when underscore-prefixed.
 270 | dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"
 271 | 
 272 | [format]
 273 | # Like Black, use double quotes for strings.
 274 | quote-style = "double"
 275 | 
 276 | # Like Black, indent with spaces, rather than tabs.
 277 | indent-style = "space"
 278 | 
 279 | # Like Black, respect magic trailing commas.
 280 | skip-magic-trailing-comma = false
 281 | 
 282 | # Like Black, automatically detect the appropriate line ending.
 283 | line-ending = "auto"
 284 | ```
 285 | 
 286 | Note that, in a `pyproject.toml`, each section header should be prefixed with `tool.ruff`. For
 287 | example, `[lint]` should be replaced with `[tool.ruff.lint]`.
 288 | 
 289 | Some configuration options can be provided via dedicated command-line arguments, such as those
 290 | related to rule enablement and disablement, file discovery, and logging level:
 291 | 
 292 | ```shell
 293 | ruff check --select F401 --select F403 --quiet
 294 | ```
 295 | 
 296 | The remaining configuration options can be provided through a catch-all `--config` argument:
 297 | 
 298 | ```shell
 299 | ruff check --config "lint.per-file-ignores = {'some_file.py' = ['F841']}"
 300 | ```
 301 | 
 302 | To opt in to the latest lint rules, formatter style changes, interface updates, and more, enable
 303 | [preview mode](https://docs.astral.sh/ruff/preview/) by setting `preview = true` in your configuration
 304 | file or passing `--preview` on the command line. Preview mode enables a collection of unstable
 305 | features that may change prior to stabilization.
 306 | 
 307 | See `ruff help` for more on Ruff's top-level commands, or `ruff help check` and `ruff help format`
 308 | for more on the linting and formatting commands, respectively.
 309 | 
 310 | ## Rules<a id="rules"></a>
 311 | 
 312 | <!-- Begin section: Rules -->
 313 | 
 314 | **Ruff supports over 900 lint rules**, many of which are inspired by popular tools like Flake8,
 315 | isort, pyupgrade, and others. Regardless of the rule's origin, Ruff re-implements every rule in
 316 | Rust as a first-party feature.
 317 | 
 318 | By default, Ruff enables Flake8's `F` rules, along with a subset of the `E` rules, omitting any
 319 | stylistic rules that overlap with the use of a formatter, like `ruff format` or
 320 | [Black](https://github.com/psf/black).
 321 | 
 322 | If you're just getting started with Ruff, **the default rule set is a great place to start**: it
 323 | catches a wide variety of common errors (like unused imports) with zero configuration.
 324 | 
 325 | In [preview](https://docs.astral.sh/ruff/preview/), Ruff enables an expanded set of default rules
 326 | that includes rules from the `B`, `UP`, and `RUF` categories, as well as many more. If you give the
 327 | new defaults a try, feel free to leave feedback in the [GitHub
 328 | discussion](https://github.com/astral-sh/ruff/discussions/23203), where you can also find the new
 329 | rule set listed in full.
 330 | 
 331 | <!-- End section: Rules -->
 332 | 
 333 | Beyond the defaults, Ruff re-implements some of the most popular Flake8 plugins and related code
 334 | quality tools, including:
 335 | 
 336 | - [autoflake](https://pypi.org/project/autoflake/)
 337 | - [eradicate](https://pypi.org/project/eradicate/)
 338 | - [flake8-2020](https://pypi.org/project/flake8-2020/)
 339 | - [flake8-annotations](https://pypi.org/project/flake8-annotations/)
 340 | - [flake8-async](https://pypi.org/project/flake8-async)
 341 | - [flake8-bandit](https://pypi.org/project/flake8-bandit/) ([#1646](https://github.com/astral-sh/ruff/issues/1646))
 342 | - [flake8-blind-except](https://pypi.org/project/flake8-blind-except/)
 343 | - [flake8-boolean-trap](https://pypi.org/project/flake8-boolean-trap/)
 344 | - [flake8-bugbear](https://pypi.org/project/flake8-bugbear/)
 345 | - [flake8-builtins](https://pypi.org/project/flake8-builtins/)
 346 | - [flake8-commas](https://pypi.org/project/flake8-commas/)
 347 | - [flake8-comprehensions](https://pypi.org/project/flake8-comprehensions/)
 348 | - [flake8-copyright](https://pypi.org/project/flake8-copyright/)
 349 | - [flake8-datetimez](https://pypi.org/project/flake8-datetimez/)
 350 | - [flake8-debugger](https://pypi.org/project/flake8-debugger/)
 351 | - [flake8-django](https://pypi.org/project/flake8-django/)
 352 | - [flake8-docstrings](https://pypi.org/project/flake8-docstrings/)
 353 | - [flake8-eradicate](https://pypi.org/project/flake8-eradicate/)
 354 | - [flake8-errmsg](https://pypi.org/project/flake8-errmsg/)
 355 | - [flake8-executable](https://pypi.org/project/flake8-executable/)
 356 | - [flake8-future-annotations](https://pypi.org/project/flake8-future-annotations/)
 357 | - [flake8-gettext](https://pypi.org/project/flake8-gettext/)
 358 | - [flake8-implicit-str-concat](https://pypi.org/project/flake8-implicit-str-concat/)
 359 | - [flake8-import-conventions](https://github.com/joaopalmeiro/flake8-import-conventions)
 360 | - [flake8-logging](https://pypi.org/project/flake8-logging/)
 361 | - [flake8-logging-format](https://pypi.org/project/flake8-logging-format/)
 362 | - [flake8-no-pep420](https://pypi.org/project/flake8-no-pep420)
 363 | - [flake8-pie](https://pypi.org/project/flake8-pie/)
 364 | - [flake8-print](https://pypi.org/project/flake8-print/)
 365 | - [flake8-pyi](https://pypi.org/project/flake8-pyi/)
 366 | - [flake8-pytest-style](https://pypi.org/project/flake8-pytest-style/)
 367 | - [flake8-quotes](https://pypi.org/project/flake8-quotes/)
 368 | - [flake8-raise](https://pypi.org/project/flake8-raise/)
 369 | - [flake8-return](https://pypi.org/project/flake8-return/)
 370 | - [flake8-self](https://pypi.org/project/flake8-self/)
 371 | - [flake8-simplify](https://pypi.org/project/flake8-simplify/)
 372 | - [flake8-slots](https://pypi.org/project/flake8-slots/)
 373 | - [flake8-super](https://pypi.org/project/flake8-super/)
 374 | - [flake8-tidy-imports](https://pypi.org/project/flake8-tidy-imports/)
 375 | - [flake8-todos](https://pypi.org/project/flake8-todos/)
 376 | - [flake8-type-checking](https://pypi.org/project/flake8-type-checking/)
 377 | - [flake8-use-pathlib](https://pypi.org/project/flake8-use-pathlib/)
 378 | - [flynt](https://pypi.org/project/flynt/) ([#2102](https://github.com/astral-sh/ruff/issues/2102))
 379 | - [isort](https://pypi.org/project/isort/)
 380 | - [mccabe](https://pypi.org/project/mccabe/)
 381 | - [pandas-vet](https://pypi.org/project/pandas-vet/)
 382 | - [pep8-naming](https://pypi.org/project/pep8-naming/)
 383 | - [pydocstyle](https://pypi.org/project/pydocstyle/)
 384 | - [pygrep-hooks](https://github.com/pre-commit/pygrep-hooks)
 385 | - [pylint-airflow](https://pypi.org/project/pylint-airflow/)
 386 | - [pyupgrade](https://pypi.org/project/pyupgrade/)
 387 | - [tryceratops](https://pypi.org/project/tryceratops/)
 388 | - [yesqa](https://pypi.org/project/yesqa/)
 389 | 
 390 | For a complete enumeration of the supported rules, see [_Rules_](https://docs.astral.sh/ruff/rules/).
 391 | 
 392 | ## Contributing<a id="contributing"></a>
 393 | 
 394 | Contributions are welcome and highly appreciated. To get started, check out the
 395 | [**contributing guidelines**](https://docs.astral.sh/ruff/contributing/).
 396 | 
 397 | You can also join us on [**Discord**](https://discord.com/invite/astral-sh).
 398 | 
 399 | ## Support<a id="support"></a>
 400 | 
 401 | Having trouble? Check out the existing issues on [**GitHub**](https://github.com/astral-sh/ruff/issues),
 402 | or feel free to [**open a new one**](https://github.com/astral-sh/ruff/issues/new).
 403 | 
 404 | You can also ask for help on [**Discord**](https://discord.com/invite/astral-sh).
 405 | 
 406 | ## Acknowledgements<a id="acknowledgements"></a>
 407 | 
 408 | Ruff's linter draws on both the APIs and implementation details of many other
 409 | tools in the Python ecosystem, especially [Flake8](https://github.com/PyCQA/flake8), [Pyflakes](https://github.com/PyCQA/pyflakes),
 410 | [pycodestyle](https://github.com/PyCQA/pycodestyle), [pydocstyle](https://github.com/PyCQA/pydocstyle),
 411 | [pyupgrade](https://github.com/asottile/pyupgrade), and [isort](https://github.com/PyCQA/isort).
 412 | 
 413 | In some cases, Ruff includes a "direct" Rust port of the corresponding tool.
 414 | We're grateful to the maintainers of these tools for their work, and for all
 415 | the value they've provided to the Python community.
 416 | 
 417 | Ruff's formatter is built on a fork of Rome's [`rome_formatter`](https://github.com/rome/tools/tree/main/crates/rome_formatter),
 418 | and again draws on both API and implementation details from [Rome](https://github.com/rome/tools),
 419 | [Prettier](https://github.com/prettier/prettier), and [Black](https://github.com/psf/black).
 420 | 
 421 | Ruff's import resolver is based on the import resolution algorithm from [Pyright](https://github.com/microsoft/pyright).
 422 | 
 423 | Ruff is also influenced by a number of tools outside the Python ecosystem, like
 424 | [Clippy](https://github.com/rust-lang/rust-clippy) and [ESLint](https://github.com/eslint/eslint).
 425 | 
 426 | Ruff is the beneficiary of a large number of [contributors](https://github.com/astral-sh/ruff/graphs/contributors).
 427 | 
 428 | Ruff is released under the MIT license.
 429 | 
 430 | ## Who's Using Ruff?<a id="whos-using-ruff"></a>
 431 | 
 432 | Ruff is used by a number of major open-source projects and companies, including:
 433 | 
 434 | - [Albumentations](https://github.com/albumentations-team/AlbumentationsX)
 435 | - Amazon ([AWS SAM](https://github.com/aws/serverless-application-model))
 436 | - [Anki](https://apps.ankiweb.net/)
 437 | - Anthropic ([Python SDK](https://github.com/anthropics/anthropic-sdk-python))
 438 | - [Apache Airflow](https://github.com/apache/airflow)
 439 | - AstraZeneca ([Magnus](https://github.com/AstraZeneca/magnus-core))
 440 | - [Babel](https://github.com/python-babel/babel)
 441 | - Benchling ([Refac](https://github.com/benchling/refac))
 442 | - [Bokeh](https://github.com/bokeh/bokeh)
 443 | - Capital One ([datacompy](https://github.com/capitalone/datacompy))
 444 | - CrowdCent ([NumerBlox](https://github.com/crowdcent/numerblox)) <!-- typos: ignore -->
 445 | - [Cryptography (PyCA)](https://github.com/pyca/cryptography)
 446 | - CERN ([Indico](https://getindico.io/))
 447 | - [DVC](https://github.com/iterative/dvc)
 448 | - [Dagger](https://github.com/dagger/dagger)
 449 | - [Dagster](https://github.com/dagster-io/dagster)
 450 | - Databricks ([MLflow](https://github.com/mlflow/mlflow))
 451 | - [Dify](https://github.com/langgenius/dify)
 452 | - [FastAPI](https://github.com/tiangolo/fastapi)
 453 | - [Godot](https://github.com/godotengine/godot)
 454 | - [Gradio](https://github.com/gradio-app/gradio)
 455 | - [Great Expectations](https://github.com/great-expectations/great_expectations)
 456 | - [HTTPX](https://github.com/encode/httpx)
 457 | - [Hatch](https://github.com/pypa/hatch)
 458 | - [Home Assistant](https://github.com/home-assistant/core)
 459 | - Hugging Face ([Transformers](https://github.com/huggingface/transformers),
 460 |     [Datasets](https://github.com/huggingface/datasets),
 461 |     [Diffusers](https://github.com/huggingface/diffusers))
 462 | - IBM ([Qiskit](https://github.com/Qiskit/qiskit))
 463 | - ING Bank ([popmon](https://github.com/ing-bank/popmon), [probatus](https://github.com/ing-bank/probatus))
 464 | - [Ibis](https://github.com/ibis-project/ibis)
 465 | - [ivy](https://github.com/unifyai/ivy)
 466 | - [JAX](https://github.com/jax-ml/jax)
 467 | - [Jupyter](https://github.com/jupyter-server/jupyter_server)
 468 | - [Kraken Tech](https://kraken.tech/)
 469 | - [LangChain](https://github.com/hwchase17/langchain)
 470 | - [Litestar](https://litestar.dev/)
 471 | - [LlamaIndex](https://github.com/jerryjliu/llama_index)
 472 | - Matrix ([Synapse](https://github.com/matrix-org/synapse))
 473 | - [MegaLinter](https://github.com/oxsecurity/megalinter)
 474 | - Meltano ([Meltano CLI](https://github.com/meltano/meltano), [Singer SDK](https://github.com/meltano/sdk))
 475 | - Microsoft ([Semantic Kernel](https://github.com/microsoft/semantic-kernel),
 476 |     [ONNX Runtime](https://github.com/microsoft/onnxruntime),
 477 |     [LightGBM](https://github.com/microsoft/LightGBM))
 478 | - Modern Treasury ([Python SDK](https://github.com/Modern-Treasury/modern-treasury-python))
 479 | - Mozilla ([Firefox](https://github.com/mozilla/gecko-dev))
 480 | - [Mypy](https://github.com/python/mypy)
 481 | - [Nautobot](https://github.com/nautobot/nautobot)
 482 | - Netflix ([Dispatch](https://github.com/Netflix/dispatch))
 483 | - [Neon](https://github.com/neondatabase/neon)
 484 | - [Nokia](https://nokia.com/)
 485 | - [NoneBot](https://github.com/nonebot/nonebot2)
 486 | - [NumPyro](https://github.com/pyro-ppl/numpyro)
 487 | - [ONNX](https://github.com/onnx/onnx)
 488 | - [OpenBB](https://github.com/OpenBB-finance/OpenBBTerminal)
 489 | - [Open Wine Components](https://github.com/Open-Wine-Components/umu-launcher)
 490 | - [PDM](https://github.com/pdm-project/pdm)
 491 | - [PaddlePaddle](https://github.com/PaddlePaddle/Paddle)
 492 | - [Pandas](https://github.com/pandas-dev/pandas)
 493 | - [Pillow](https://github.com/python-pillow/Pillow)
 494 | - [Poetry](https://github.com/python-poetry/poetry)
 495 | - [Polars](https://github.com/pola-rs/polars)
 496 | - [PostHog](https://github.com/PostHog/posthog)
 497 | - Prefect ([Python SDK](https://github.com/PrefectHQ/prefect), [Marvin](https://github.com/PrefectHQ/marvin))
 498 | - [PyInstaller](https://github.com/pyinstaller/pyinstaller)
 499 | - [PyMC](https://github.com/pymc-devs/pymc/)
 500 | - [PyMC-Marketing](https://github.com/pymc-labs/pymc-marketing)
 501 | - [pytest](https://github.com/pytest-dev/pytest)
 502 | - [PyTorch](https://github.com/pytorch/pytorch)
 503 | - [Pydantic](https://github.com/pydantic/pydantic)
 504 | - [Pylint](https://github.com/PyCQA/pylint)
 505 | - [PyScripter](https://github.com/pyscripter/pyscripter)
 506 | - [PyVista](https://github.com/pyvista/pyvista)
 507 | - [Reflex](https://github.com/reflex-dev/reflex)
 508 | - [River](https://github.com/online-ml/river)
 509 | - [Rippling](https://rippling.com)
 510 | - [Robyn](https://github.com/sansyrox/robyn)
 511 | - [Saleor](https://github.com/saleor/saleor)
 512 | - Scale AI ([Launch SDK](https://github.com/scaleapi/launch-python-client))
 513 | - [SciPy](https://github.com/scipy/scipy)
 514 | - Snowflake ([SnowCLI](https://github.com/Snowflake-Labs/snowcli))
 515 | - [Sphinx](https://github.com/sphinx-doc/sphinx)
 516 | - [Stable Baselines3](https://github.com/DLR-RM/stable-baselines3)
 517 | - [Starlette](https://github.com/encode/starlette)
 518 | - [Streamlit](https://github.com/streamlit/streamlit)
 519 | - [The Algorithms](https://github.com/TheAlgorithms/Python)
 520 | - [Vega-Altair](https://github.com/altair-viz/altair)
 521 | - [Weblate](https://weblate.org/)
 522 | - WordPress ([Openverse](https://github.com/WordPress/openverse))
 523 | - [ZenML](https://github.com/zenml-io/zenml)
 524 | - [Zulip](https://github.com/zulip/zulip)
 525 | - [build (PyPA)](https://github.com/pypa/build)
 526 | - [cibuildwheel (PyPA)](https://github.com/pypa/cibuildwheel)
 527 | - [delta-rs](https://github.com/delta-io/delta-rs)
 528 | - [featuretools](https://github.com/alteryx/featuretools)
 529 | - [meson-python](https://github.com/mesonbuild/meson-python)
 530 | - [nox](https://github.com/wntrblm/nox)
 531 | - [pip](https://github.com/pypa/pip)
 532 | 
 533 | ### Show Your Support
 534 | 
 535 | If you're using Ruff, consider adding the Ruff badge to your project's `README.md`:
 536 | 
 537 | ```md
 538 | [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
 539 | ```
 540 | 
 541 | ...or `README.rst`:
 542 | 
 543 | ```rst
 544 | .. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
 545 |     :target: https://github.com/astral-sh/ruff
 546 |     :alt: Ruff
 547 | ```
 548 | 
 549 | ...or, as HTML:
 550 | 
 551 | ```html
 552 | <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;"></a>
 553 | ```
 554 | 
 555 | ## License<a id="license"></a>
 556 | 
 557 | This repository is licensed under the [MIT License](https://github.com/astral-sh/ruff/blob/main/LICENSE)
 558 | 
 559 | <div align="center">
 560 |   <a target="_blank" href="https://astral.sh" style="background:none">
 561 |     <img src="https://raw.githubusercontent.com/astral-sh/ruff/main/assets/svg/Astral.svg" alt="Made by Astral">
 562 |   </a>
 563 | </div>
```
