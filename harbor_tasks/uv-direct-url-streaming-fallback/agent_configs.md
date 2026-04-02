# Agent Config Files for uv-direct-url-streaming-fallback

Repo: astral-sh/uv
Commit: 5ad8577ff847d0bf115d45dd05a1efecf6fd797f
Files found: 5


---
## CLAUDE.md

```
   1 | - Read CONTRIBUTING.md for guidelines on how to run tools
   2 | - ALWAYS attempt to add a test case for changed behavior
   3 | - PREFER integration tests, e.g., at `it/...` over unit tests
   4 | - When making changes for Windows from Unix, use `cargo xwin clippy` to check compilation
   5 | - NEVER perform builds with the release profile, unless asked or reproducing performance issues
   6 | - PREFER running specific tests over running the entire test suite
   7 | - AVOID using `panic!`, `unreachable!`, `.unwrap()`, unsafe code, and clippy rule ignores
   8 | - PREFER patterns like `if let` to handle fallibility
   9 | - ALWAYS write `SAFETY` comments following our usual style when writing `unsafe` code
  10 | - PREFER `#[expect()]` over `[allow()]` if clippy must be disabled
  11 | - PREFER let chains (`if let` combined with `&&`) over nested `if let` statements
  12 | - NEVER update all dependencies in the lockfile and ALWAYS use `cargo update --precise` to make
  13 |   lockfile changes
  14 | - NEVER assume clippy warnings are pre-existing, it is very rare that `main` has warnings
  15 | - ALWAYS read and copy the style of similar tests when adding new cases
  16 | - PREFER top-level imports over local imports or fully qualified names
  17 | - AVOID shortening variable names, e.g., use `version` instead of `ver`, and `requires_python`
  18 |   instead of `rp`
```


---
## README.md

```
   1 | # uv
   2 | 
   3 | [![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
   4 | [![image](https://img.shields.io/pypi/v/uv.svg)](https://pypi.python.org/pypi/uv)
   5 | [![image](https://img.shields.io/pypi/l/uv.svg)](https://pypi.python.org/pypi/uv)
   6 | [![image](https://img.shields.io/pypi/pyversions/uv.svg)](https://pypi.python.org/pypi/uv)
   7 | [![Actions status](https://github.com/astral-sh/uv/actions/workflows/ci.yml/badge.svg)](https://github.com/astral-sh/uv/actions)
   8 | [![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?logo=discord&logoColor=white)](https://discord.gg/astral-sh)
   9 | 
  10 | An extremely fast Python package and project manager, written in Rust.
  11 | 
  12 | <p align="center">
  13 |   <picture align="center">
  14 |     <source media="(prefers-color-scheme: dark)" srcset="https://github.com/astral-sh/uv/assets/1309177/03aa9163-1c79-4a87-a31d-7a9311ed9310">
  15 |     <source media="(prefers-color-scheme: light)" srcset="https://github.com/astral-sh/uv/assets/1309177/629e59c0-9c6e-4013-9ad4-adb2bcf5080d">
  16 |     <img alt="Shows a bar chart with benchmark results." src="https://github.com/astral-sh/uv/assets/1309177/629e59c0-9c6e-4013-9ad4-adb2bcf5080d">
  17 |   </picture>
  18 | </p>
  19 | 
  20 | <p align="center">
  21 |   <i>Installing <a href="https://trio.readthedocs.io/">Trio</a>'s dependencies with a warm cache.</i>
  22 | </p>
  23 | 
  24 | ## Highlights
  25 | 
  26 | - A single tool to replace `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `twine`, `virtualenv`, and
  27 |   more.
  28 | - [10-100x faster](https://github.com/astral-sh/uv/blob/main/BENCHMARKS.md) than `pip`.
  29 | - Provides [comprehensive project management](#projects), with a
  30 |   [universal lockfile](https://docs.astral.sh/uv/concepts/projects/layout#the-lockfile).
  31 | - [Runs scripts](#scripts), with support for
  32 |   [inline dependency metadata](https://docs.astral.sh/uv/guides/scripts#declaring-script-dependencies).
  33 | - [Installs and manages](#python-versions) Python versions.
  34 | - [Runs and installs](#tools) tools published as Python packages.
  35 | - Includes a [pip-compatible interface](#the-pip-interface) for a performance boost with a familiar
  36 |   CLI.
  37 | - Supports Cargo-style [workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces) for
  38 |   scalable projects.
  39 | - Disk-space efficient, with a [global cache](https://docs.astral.sh/uv/concepts/cache) for
  40 |   dependency deduplication.
  41 | - Installable without Rust or Python via `curl` or `pip`.
  42 | - Supports macOS, Linux, and Windows.
  43 | 
  44 | uv is backed by [Astral](https://astral.sh), the creators of
  45 | [Ruff](https://github.com/astral-sh/ruff) and [ty](https://github.com/astral-sh/ty).
  46 | 
  47 | ## Installation
  48 | 
  49 | Install uv with our standalone installers:
  50 | 
  51 | ```bash
  52 | # On macOS and Linux.
  53 | curl -LsSf https://astral.sh/uv/install.sh | sh
  54 | ```
  55 | 
  56 | ```bash
  57 | # On Windows.
  58 | powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  59 | ```
  60 | 
  61 | Or, from [PyPI](https://pypi.org/project/uv/):
  62 | 
  63 | ```bash
  64 | # With pip.
  65 | pip install uv
  66 | ```
  67 | 
  68 | ```bash
  69 | # Or pipx.
  70 | pipx install uv
  71 | ```
  72 | 
  73 | If installed via the standalone installer, uv can update itself to the latest version:
  74 | 
  75 | ```bash
  76 | uv self update
  77 | ```
  78 | 
  79 | See the [installation documentation](https://docs.astral.sh/uv/getting-started/installation/) for
  80 | details and alternative installation methods.
  81 | 
  82 | ## Documentation
  83 | 
  84 | uv's documentation is available at [docs.astral.sh/uv](https://docs.astral.sh/uv).
  85 | 
  86 | Additionally, the command line reference documentation can be viewed with `uv help`.
  87 | 
  88 | ## Features
  89 | 
  90 | ### Projects
  91 | 
  92 | uv manages project dependencies and environments, with support for lockfiles, workspaces, and more,
  93 | similar to `rye` or `poetry`:
  94 | 
  95 | ```console
  96 | $ uv init example
  97 | Initialized project `example` at `/home/user/example`
  98 | 
  99 | $ cd example
 100 | 
 101 | $ uv add ruff
 102 | Creating virtual environment at: .venv
 103 | Resolved 2 packages in 170ms
 104 |    Built example @ file:///home/user/example
 105 | Prepared 2 packages in 627ms
 106 | Installed 2 packages in 1ms
 107 |  + example==0.1.0 (from file:///home/user/example)
 108 |  + ruff==0.5.0
 109 | 
 110 | $ uv run ruff check
 111 | All checks passed!
 112 | 
 113 | $ uv lock
 114 | Resolved 2 packages in 0.33ms
 115 | 
 116 | $ uv sync
 117 | Resolved 2 packages in 0.70ms
 118 | Checked 1 package in 0.02ms
 119 | ```
 120 | 
 121 | See the [project documentation](https://docs.astral.sh/uv/guides/projects/) to get started.
 122 | 
 123 | uv also supports building and publishing projects, even if they're not managed with uv. See the
 124 | [publish guide](https://docs.astral.sh/uv/guides/publish/) to learn more.
 125 | 
 126 | ### Scripts
 127 | 
 128 | uv manages dependencies and environments for single-file scripts.
 129 | 
 130 | Create a new script and add inline metadata declaring its dependencies:
 131 | 
 132 | ```console
 133 | $ echo 'import requests; print(requests.get("https://astral.sh"))' > example.py
 134 | 
 135 | $ uv add --script example.py requests
 136 | Updated `example.py`
 137 | ```
 138 | 
 139 | Then, run the script in an isolated virtual environment:
 140 | 
 141 | ```console
 142 | $ uv run example.py
 143 | Reading inline script metadata from: example.py
 144 | Installed 5 packages in 12ms
 145 | <Response [200]>
 146 | ```
 147 | 
 148 | See the [scripts documentation](https://docs.astral.sh/uv/guides/scripts/) to get started.
 149 | 
 150 | ### Tools
 151 | 
 152 | uv executes and installs command-line tools provided by Python packages, similar to `pipx`.
 153 | 
 154 | Run a tool in an ephemeral environment using `uvx` (an alias for `uv tool run`):
 155 | 
 156 | ```console
 157 | $ uvx pycowsay 'hello world!'
 158 | Resolved 1 package in 167ms
 159 | Installed 1 package in 9ms
 160 |  + pycowsay==0.0.0.2
 161 |   """
 162 | 
 163 |   ------------
 164 | < hello world! >
 165 |   ------------
 166 |    \   ^__^
 167 |     \  (oo)\_______
 168 |        (__)\       )\/\
 169 |            ||----w |
 170 |            ||     ||
 171 | ```
 172 | 
 173 | Install a tool with `uv tool install`:
 174 | 
 175 | ```console
 176 | $ uv tool install ruff
 177 | Resolved 1 package in 6ms
 178 | Installed 1 package in 2ms
 179 |  + ruff==0.5.0
 180 | Installed 1 executable: ruff
 181 | 
 182 | $ ruff --version
 183 | ruff 0.5.0
 184 | ```
 185 | 
 186 | See the [tools documentation](https://docs.astral.sh/uv/guides/tools/) to get started.
 187 | 
 188 | ### Python versions
 189 | 
 190 | uv installs Python and allows quickly switching between versions.
 191 | 
 192 | Install multiple Python versions:
 193 | 
 194 | ```console
 195 | $ uv python install 3.12 3.13 3.14
 196 | Installed 3 versions in 972ms
 197 |  + cpython-3.12.12-macos-aarch64-none (python3.12)
 198 |  + cpython-3.13.9-macos-aarch64-none (python3.13)
 199 |  + cpython-3.14.0-macos-aarch64-none (python3.14)
 200 | 
 201 | ```
 202 | 
 203 | Download Python versions as needed:
 204 | 
 205 | ```console
 206 | $ uv venv --python 3.12.0
 207 | Using Python 3.12.0
 208 | Creating virtual environment at: .venv
 209 | Activate with: source .venv/bin/activate
 210 | 
 211 | $ uv run --python pypy@3.8 -- python --version
 212 | Python 3.8.16 (a9dbdca6fc3286b0addd2240f11d97d8e8de187a, Dec 29 2022, 11:45:30)
 213 | [PyPy 7.3.11 with GCC Apple LLVM 13.1.6 (clang-1316.0.21.2.5)] on darwin
 214 | Type "help", "copyright", "credits" or "license" for more information.
 215 | >>>>
 216 | ```
 217 | 
 218 | Use a specific Python version in the current directory:
 219 | 
 220 | ```console
 221 | $ uv python pin 3.11
 222 | Pinned `.python-version` to `3.11`
 223 | ```
 224 | 
 225 | See the [Python installation documentation](https://docs.astral.sh/uv/guides/install-python/) to get
 226 | started.
 227 | 
 228 | ### The pip interface
 229 | 
 230 | uv provides a drop-in replacement for common `pip`, `pip-tools`, and `virtualenv` commands.
 231 | 
 232 | uv extends their interfaces with advanced features, such as dependency version overrides,
 233 | platform-independent resolutions, reproducible resolutions, alternative resolution strategies, and
 234 | more.
 235 | 
 236 | Migrate to uv without changing your existing workflows — and experience a 10-100x speedup — with the
 237 | `uv pip` interface.
 238 | 
 239 | Compile requirements into a platform-independent requirements file:
 240 | 
 241 | ```console
 242 | $ uv pip compile requirements.in \
 243 |    --universal \
 244 |    --output-file requirements.txt
 245 | Resolved 43 packages in 12ms
 246 | ```
 247 | 
 248 | Create a virtual environment:
 249 | 
 250 | ```console
 251 | $ uv venv
 252 | Using Python 3.12.3
 253 | Creating virtual environment at: .venv
 254 | Activate with: source .venv/bin/activate
 255 | ```
 256 | 
 257 | Install the locked requirements:
 258 | 
 259 | ```console
 260 | $ uv pip sync requirements.txt
 261 | Resolved 43 packages in 11ms
 262 | Installed 43 packages in 208ms
 263 |  + babel==2.15.0
 264 |  + black==24.4.2
 265 |  + certifi==2024.7.4
 266 |  ...
 267 | ```
 268 | 
 269 | See the [pip interface documentation](https://docs.astral.sh/uv/pip/index/) to get started.
 270 | 
 271 | ## Contributing
 272 | 
 273 | We are passionate about supporting contributors of all levels of experience and would love to see
 274 | you get involved in the project. See the
 275 | [contributing guide](https://github.com/astral-sh/uv?tab=contributing-ov-file#contributing) to get
 276 | started.
 277 | 
 278 | ## FAQ
 279 | 
 280 | #### How do you pronounce uv?
 281 | 
 282 | It's pronounced as "you - vee" ([`/juː viː/`](https://en.wikipedia.org/wiki/Help:IPA/English#Key))
 283 | 
 284 | #### How should I stylize uv?
 285 | 
 286 | Just "uv", please. See the [style guide](./STYLE.md#styling-uv) for details.
 287 | 
 288 | #### What platforms does uv support?
 289 | 
 290 | See uv's [platform support](https://docs.astral.sh/uv/reference/platforms/) document.
 291 | 
 292 | #### Is uv ready for production?
 293 | 
 294 | Yes, uv is stable and widely used in production. See uv's
 295 | [versioning policy](https://docs.astral.sh/uv/reference/versioning/) document for details.
 296 | 
 297 | ## Acknowledgements
 298 | 
 299 | uv's dependency resolver uses [PubGrub](https://github.com/pubgrub-rs/pubgrub) under the hood. We're
 300 | grateful to the PubGrub maintainers, especially [Jacob Finkelman](https://github.com/Eh2406), for
 301 | their support.
 302 | 
 303 | uv's Git implementation is based on [Cargo](https://github.com/rust-lang/cargo).
 304 | 
 305 | Some of uv's optimizations are inspired by the great work we've seen in [pnpm](https://pnpm.io/),
 306 | [Orogene](https://github.com/orogene/orogene), and [Bun](https://github.com/oven-sh/bun). We've also
 307 | learned a lot from Nathaniel J. Smith's [Posy](https://github.com/njsmith/posy) and adapted its
 308 | [trampoline](https://github.com/njsmith/posy/tree/main/src/trampolines/windows-trampolines/posy-trampoline)
 309 | for Windows support.
 310 | 
 311 | ## License
 312 | 
 313 | uv is licensed under either of
 314 | 
 315 | - Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
 316 |   <https://www.apache.org/licenses/LICENSE-2.0>)
 317 | - MIT license ([LICENSE-MIT](LICENSE-MIT) or <https://opensource.org/licenses/MIT>)
 318 | 
 319 | at your option.
 320 | 
 321 | Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in uv
 322 | by you, as defined in the Apache-2.0 license, shall be dually licensed as above, without any
 323 | additional terms or conditions.
 324 | 
 325 | <div align="center">
 326 |   <a target="_blank" href="https://astral.sh" style="background:none">
 327 |     <img src="https://raw.githubusercontent.com/astral-sh/uv/main/assets/svg/Astral.svg" alt="Made by Astral">
 328 |   </a>
 329 | </div>
```


---
## crates/README.md

```
   1 | # Crates
   2 | 
   3 | ## [uv-bench](./uv-bench)
   4 | 
   5 | Functionality for benchmarking uv.
   6 | 
   7 | ## [uv-cache-key](./uv-cache-key)
   8 | 
   9 | Generic functionality for caching paths, URLs, and other resources across platforms.
  10 | 
  11 | ## [uv-distribution-filename](./uv-distribution-filename)
  12 | 
  13 | Parse built distribution (wheel) and source distribution (sdist) filenames to extract structured
  14 | metadata.
  15 | 
  16 | ## [uv-distribution-types](./uv-distribution-types)
  17 | 
  18 | Abstractions for representing built distributions (wheels) and source distributions (sdists), and
  19 | the sources from which they can be downloaded.
  20 | 
  21 | ## [uv-install-wheel-rs](./uv-install-wheel)
  22 | 
  23 | Install built distributions (wheels) into a virtual environment.
  24 | 
  25 | ## [uv-once-map](./uv-once-map)
  26 | 
  27 | A [`waitmap`](https://github.com/withoutboats/waitmap)-like concurrent hash map for executing tasks
  28 | exactly once.
  29 | 
  30 | ## [uv-pep440-rs](./uv-pep440)
  31 | 
  32 | Utilities for interacting with Python version numbers and specifiers.
  33 | 
  34 | ## [uv-pep508-rs](./uv-pep508)
  35 | 
  36 | Utilities for parsing and evaluating
  37 | [dependency specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/),
  38 | previously known as [PEP 508](https://peps.python.org/pep-0508/).
  39 | 
  40 | ## [uv-platform-tags](./uv-platform-tags)
  41 | 
  42 | Functionality for parsing and inferring Python platform tags as per
  43 | [PEP 425](https://peps.python.org/pep-0425/).
  44 | 
  45 | ## [uv-cli](./uv-cli)
  46 | 
  47 | Command-line interface for the uv package manager.
  48 | 
  49 | ## [uv-build-frontend](./uv-build-frontend)
  50 | 
  51 | A [PEP 517](https://www.python.org/dev/peps/pep-0517/)-compatible build frontend for uv.
  52 | 
  53 | ## [uv-cache](./uv-cache)
  54 | 
  55 | Functionality for caching Python packages and associated metadata.
  56 | 
  57 | ## [uv-client](./uv-client)
  58 | 
  59 | Client for interacting with PyPI-compatible HTTP APIs.
  60 | 
  61 | ## [uv-dev](./uv-dev)
  62 | 
  63 | Development utilities for uv.
  64 | 
  65 | ## [uv-dispatch](./uv-dispatch)
  66 | 
  67 | A centralized `struct` for resolving and building source distributions in isolated environments.
  68 | Implements the traits defined in `uv-types`.
  69 | 
  70 | ## [uv-distribution](./uv-distribution)
  71 | 
  72 | Client for interacting with built distributions (wheels) and source distributions (sdists). Capable
  73 | of fetching metadata, distribution contents, etc.
  74 | 
  75 | ## [uv-extract](./uv-extract)
  76 | 
  77 | Utilities for extracting files from archives.
  78 | 
  79 | ## [uv-fs](./uv-fs)
  80 | 
  81 | Utilities for interacting with the filesystem.
  82 | 
  83 | ## [uv-git](./uv-git)
  84 | 
  85 | Functionality for interacting with Git repositories.
  86 | 
  87 | ## [uv-installer](./uv-installer)
  88 | 
  89 | Functionality for installing Python packages into a virtual environment.
  90 | 
  91 | ## [uv-python](./uv-python)
  92 | 
  93 | Functionality for detecting and leveraging the current Python interpreter.
  94 | 
  95 | ## [uv-normalize](./uv-normalize)
  96 | 
  97 | Normalize package and extra names as per Python specifications.
  98 | 
  99 | ## [uv-requirements](./uv-requirements)
 100 | 
 101 | Utilities for reading package requirements from `pyproject.toml` and `requirements.txt` files.
 102 | 
 103 | ## [uv-resolver](./uv-resolver)
 104 | 
 105 | Functionality for resolving Python packages and their dependencies.
 106 | 
 107 | ## [uv-shell](./uv-shell)
 108 | 
 109 | Utilities for detecting and manipulating shell environments.
 110 | 
 111 | ## [uv-types](./uv-types)
 112 | 
 113 | Shared traits for uv, to avoid circular dependencies.
 114 | 
 115 | ## [uv-pypi-types](./uv-pypi-types)
 116 | 
 117 | General-purpose type definitions for types used in PyPI-compatible APIs.
 118 | 
 119 | ## [uv-virtualenv](./uv-virtualenv)
 120 | 
 121 | A `venv` replacement to create virtual environments in Rust.
 122 | 
 123 | ## [uv-warnings](./uv-warnings)
 124 | 
 125 | User-facing warnings for uv.
 126 | 
 127 | ## [uv-workspace](./uv-workspace)
 128 | 
 129 | Workspace abstractions for uv.
 130 | 
 131 | ## [uv-requirements-txt](./uv-requirements-txt)
 132 | 
 133 | Functionality for parsing `requirements.txt` files.
```


---
## crates/uv-distribution/README.md

```
   1 | <!-- This file is generated. DO NOT EDIT -->
   2 | 
   3 | # uv-distribution
   4 | 
   5 | This crate is an internal component of [uv](https://crates.io/crates/uv). The Rust API exposed here
   6 | is unstable and will have frequent breaking changes.
   7 | 
   8 | This version (0.0.33) is a component of [uv 0.11.0](https://crates.io/crates/uv/0.11.0). The source
   9 | can be found [here](https://github.com/astral-sh/uv/blob/0.11.0/crates/uv-distribution).
  10 | 
  11 | See uv's
  12 | [crate versioning policy](https://docs.astral.sh/uv/reference/policies/versioning/#crate-versioning)
  13 | for details on versioning.
```


---
## crates/uv/README.md

```
   1 | <!-- This file is generated. DO NOT EDIT -->
   2 | 
   3 | # uv
   4 | 
   5 | uv is a Python package and project manager.
   6 | 
   7 | See the [documentation](https://docs.astral.sh/uv/) or [repository](https://github.com/astral-sh/uv)
   8 | for more information.
   9 | 
  10 | This crate is the entry point to the uv command-line interface. The Rust API exposed here is not
  11 | considered public interface.
  12 | 
  13 | This is version 0.11.0. The source can be found
  14 | [here](https://github.com/astral-sh/uv/blob/0.11.0/crates/uv).
  15 | 
  16 | The following uv workspace members are also available:
  17 | 
  18 | - [uv-audit](https://crates.io/crates/uv-audit)
  19 | - [uv-auth](https://crates.io/crates/uv-auth)
  20 | - [uv-bin-install](https://crates.io/crates/uv-bin-install)
  21 | - [uv-build](https://crates.io/crates/uv-build)
  22 | - [uv-build-backend](https://crates.io/crates/uv-build-backend)
  23 | - [uv-build-frontend](https://crates.io/crates/uv-build-frontend)
  24 | - [uv-cache](https://crates.io/crates/uv-cache)
  25 | - [uv-cache-info](https://crates.io/crates/uv-cache-info)
  26 | - [uv-cache-key](https://crates.io/crates/uv-cache-key)
  27 | - [uv-cli](https://crates.io/crates/uv-cli)
  28 | - [uv-client](https://crates.io/crates/uv-client)
  29 | - [uv-configuration](https://crates.io/crates/uv-configuration)
  30 | - [uv-console](https://crates.io/crates/uv-console)
  31 | - [uv-dirs](https://crates.io/crates/uv-dirs)
  32 | - [uv-dispatch](https://crates.io/crates/uv-dispatch)
  33 | - [uv-distribution](https://crates.io/crates/uv-distribution)
  34 | - [uv-distribution-filename](https://crates.io/crates/uv-distribution-filename)
  35 | - [uv-distribution-types](https://crates.io/crates/uv-distribution-types)
  36 | - [uv-extract](https://crates.io/crates/uv-extract)
  37 | - [uv-flags](https://crates.io/crates/uv-flags)
  38 | - [uv-fs](https://crates.io/crates/uv-fs)
  39 | - [uv-git](https://crates.io/crates/uv-git)
  40 | - [uv-git-types](https://crates.io/crates/uv-git-types)
  41 | - [uv-globfilter](https://crates.io/crates/uv-globfilter)
  42 | - [uv-install-wheel](https://crates.io/crates/uv-install-wheel)
  43 | - [uv-installer](https://crates.io/crates/uv-installer)
  44 | - [uv-keyring](https://crates.io/crates/uv-keyring)
  45 | - [uv-logging](https://crates.io/crates/uv-logging)
  46 | - [uv-macros](https://crates.io/crates/uv-macros)
  47 | - [uv-metadata](https://crates.io/crates/uv-metadata)
  48 | - [uv-normalize](https://crates.io/crates/uv-normalize)
  49 | - [uv-once-map](https://crates.io/crates/uv-once-map)
  50 | - [uv-options-metadata](https://crates.io/crates/uv-options-metadata)
  51 | - [uv-pep440](https://crates.io/crates/uv-pep440)
  52 | - [uv-pep508](https://crates.io/crates/uv-pep508)
  53 | - [uv-performance-memory-allocator](https://crates.io/crates/uv-performance-memory-allocator)
  54 | - [uv-platform](https://crates.io/crates/uv-platform)
  55 | - [uv-platform-tags](https://crates.io/crates/uv-platform-tags)
  56 | - [uv-preview](https://crates.io/crates/uv-preview)
  57 | - [uv-publish](https://crates.io/crates/uv-publish)
  58 | - [uv-pypi-types](https://crates.io/crates/uv-pypi-types)
  59 | - [uv-python](https://crates.io/crates/uv-python)
  60 | - [uv-redacted](https://crates.io/crates/uv-redacted)
  61 | - [uv-requirements](https://crates.io/crates/uv-requirements)
  62 | - [uv-requirements-txt](https://crates.io/crates/uv-requirements-txt)
  63 | - [uv-resolver](https://crates.io/crates/uv-resolver)
  64 | - [uv-scripts](https://crates.io/crates/uv-scripts)
  65 | - [uv-settings](https://crates.io/crates/uv-settings)
  66 | - [uv-shell](https://crates.io/crates/uv-shell)
  67 | - [uv-small-str](https://crates.io/crates/uv-small-str)
  68 | - [uv-state](https://crates.io/crates/uv-state)
  69 | - [uv-static](https://crates.io/crates/uv-static)
  70 | - [uv-test](https://crates.io/crates/uv-test)
  71 | - [uv-tool](https://crates.io/crates/uv-tool)
  72 | - [uv-torch](https://crates.io/crates/uv-torch)
  73 | - [uv-trampoline-builder](https://crates.io/crates/uv-trampoline-builder)
  74 | - [uv-types](https://crates.io/crates/uv-types)
  75 | - [uv-unix](https://crates.io/crates/uv-unix)
  76 | - [uv-version](https://crates.io/crates/uv-version)
  77 | - [uv-virtualenv](https://crates.io/crates/uv-virtualenv)
  78 | - [uv-warnings](https://crates.io/crates/uv-warnings)
  79 | - [uv-windows](https://crates.io/crates/uv-windows)
  80 | - [uv-workspace](https://crates.io/crates/uv-workspace)
  81 | 
  82 | uv's workspace members are considered internal and will have frequent breaking changes.
  83 | 
  84 | See uv's
  85 | [crate versioning policy](https://docs.astral.sh/uv/reference/policies/versioning/#crate-versioning)
  86 | for details on versioning.
```
