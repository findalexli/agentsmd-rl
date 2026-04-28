#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruby-git

# Idempotency guard
if grep -qF "- [Rule 2 \u2014 SYNOPSIS does NOT show `--`: protect operands from flag misinterpret" ".github/skills/command-implementation/REFERENCE.md" && grep -qF "description: \"Scaffolds new and reviews existing Git::Commands::* classes with u" ".github/skills/command-implementation/SKILL.md" && grep -qF "- [Command Implementation](../command-implementation/SKILL.md) \u2014 class" ".github/skills/command-test-conventions/SKILL.md" && grep -qF "[Command Implementation](../command-implementation/SKILL.md) skill, not YARD rev" ".github/skills/command-yard-documentation/SKILL.md" && grep -qF "- [Command Implementation](../command-implementation/SKILL.md) \u2014 generates and r" ".github/skills/extract-command-from-lib/SKILL.md" && grep -qF "- [Command Implementation](../command-implementation/SKILL.md) \u2014 generating and" ".github/skills/project-context/SKILL.md" && grep -qF "See [Command Implementation](../command-implementation/SKILL.md) for the canonic" ".github/skills/refactor-command-to-commandlineresult/SKILL.md" && grep -qF "and [`requires_git_version` convention](../command-implementation/REFERENCE.md#r" ".github/skills/review-arguments-dsl/CHECKLIST.md" && grep -qF "- [Command Implementation](../command-implementation/SKILL.md) \u2014 class structure" ".github/skills/review-arguments-dsl/SKILL.md" && grep -qF "- [Command Implementation](../command-implementation/SKILL.md) \u2014 class structure" ".github/skills/review-backward-compatibility/SKILL.md" && grep -qF ".github/skills/review-command-implementation/SKILL.md" ".github/skills/review-command-implementation/SKILL.md" && grep -qF "- [Command Implementation](../command-implementation/SKILL.md) \u2014 class" ".github/skills/review-command-tests/SKILL.md" && grep -qF "- [Command Implementation](../command-implementation/REFERENCE.md#phased-rollout" ".github/skills/review-cross-command-consistency/SKILL.md" && grep -qF "Using the Reviewing Skills skill, review .github/skills/command-implementation/." ".github/skills/reviewing-skills/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/command-implementation/REFERENCE.md b/.github/skills/command-implementation/REFERENCE.md
@@ -1,87 +1,42 @@
----
-name: scaffold-new-command
-description: "Generates a production-ready Git::Commands::* class with unit tests, integration tests, and YARD docs using the Base architecture. Use when creating a new command from scratch."
----
+# Command Implementation — Reference
 
-# Scaffold New Command
-
-Generate a production-ready command class, unit tests, integration tests, and YARD
-docs using the `Git::Commands::Base` architecture.
+Detailed reference for `Git::Commands::Base` command classes. This file is loaded
+by subagents during the [Command Implementation](SKILL.md) workflow.
 
 ## Contents
 
 - [Contents](#contents)
-- [Related skills](#related-skills)
-- [Input](#input)
-  - [Git documentation for the git command](#git-documentation-for-the-git-command)
-- [Reference](#reference)
-  - [Files to generate](#files-to-generate)
-  - [Single class vs. sub-command namespace](#single-class-vs-sub-command-namespace)
-    - [When to use sub-commands](#when-to-use-sub-commands)
-    - [Do NOT split by output format / output mode](#do-not-split-by-output-format--output-mode)
-    - [When to keep a single class](#when-to-keep-a-single-class)
-    - [Naming sub-command classes](#naming-sub-command-classes)
-    - [Namespace module template](#namespace-module-template)
-  - [Command template (Base pattern)](#command-template-base-pattern)
-    - [Overriding `call` — inline example](#overriding-call--inline-example)
-  - [Options completeness — consult the latest-version docs first](#options-completeness--consult-the-latest-version-docs-first)
-    - [`requires_git_version` convention](#requires_git_version-convention)
-    - [Execution-model conflicts](#execution-model-conflicts)
-  - [`end_of_options` placement](#end_of_options-placement)
-    - [Rule 1 — SYNOPSIS shows `--`: mirror the SYNOPSIS](#rule-1--synopsis-shows----mirror-the-synopsis)
-    - [Rule 2 — SYNOPSIS does NOT show `--`: protect operands from flag misinterpretation](#rule-2--synopsis-does-not-show----protect-operands-from-flag-misinterpretation)
-  - [Exit status guidance](#exit-status-guidance)
-  - [Facade delegation and policy options](#facade-delegation-and-policy-options)
-  - [Phased rollout, compatibility, and quality gates](#phased-rollout-compatibility-and-quality-gates)
-- [Workflow](#workflow)
-- [Output](#output)
-
-## Related skills
-
-- [Review Arguments DSL](../review-arguments-dsl/SKILL.md) — verify every DSL entry
-  is correct and complete
-- [YARD Documentation](../yard-documentation/SKILL.md) — authoritative source for
-  YARD formatting rules and writing standards (load before starting)
-- [Command YARD Documentation](../command-yard-documentation/SKILL.md) — verify
-  documentation completeness and formatting
-- [RSpec Unit Testing Standards](../rspec-unit-testing-standards/SKILL.md) — baseline
-  RSpec rules all generated unit specs must comply with
-- [Command Test Conventions](../command-test-conventions/SKILL.md) — conventions for
-  writing and reviewing unit and integration tests for command classes
-- [Review Command Implementation](../review-command-implementation/SKILL.md) —
-  canonical class-shape checklist, phased rollout gates, and internal compatibility
-  contracts
-
-## Input
-
-The user provides the target `Git::Commands::*` class name and the git subcommand (or
-subcommand + sub-action) it wraps. The agent gathers the following.
-
-### Git documentation for the git command
-
-- **Latest-version online command documentation**
-
-  Determine the latest released git version by running `bin/latest-git-version`
-  (it prints a version string such as `2.49.0`). Then read the **entire** official
-  git documentation online man page for that version from the URL
-  `https://git-scm.com/docs/git-{command}/{version}` (e.g.,
-  `https://git-scm.com/docs/git-push/2.49.0`). This version will be used as the
-  primary authority for DSL completeness, including the options to include in the
-  DSL, argument names, aliases, ordering, etc.
-
-- **Minimum-version online command documentation**
-
-  Read the **entire** official git documentation online man page for the command for
-  the `Git::MINIMUM_GIT_VERSION` version of git. This will be used only for
-  command-introduction and `requires_git_version` decisions. Fetch this version from
-  URL `https://git-scm.com/docs/git-{command}/{version}`.
-
-Do **not** scaffold from local `git <command> -h` output — the installed Git
-version is unknown and may differ from the latest supported version.
-
-## Reference
-
-### Files to generate
+- [Files to generate](#files-to-generate)
+- [Single class vs. sub-command namespace](#single-class-vs-sub-command-namespace)
+  - [When to use sub-commands](#when-to-use-sub-commands)
+  - [Do NOT split by output format / output mode](#do-not-split-by-output-format--output-mode)
+  - [When to keep a single class](#when-to-keep-a-single-class)
+  - [Naming sub-command classes](#naming-sub-command-classes)
+  - [Namespace module template](#namespace-module-template)
+- [Architecture contract](#architecture-contract)
+- [Command template (Base pattern)](#command-template-base-pattern)
+- [`#call` override guidance](#call-override-guidance)
+  - [Overriding `call` — inline example](#overriding-call--inline-example)
+  - [Action-option-with-optional-value commands](#action-option-with-optional-value-commands)
+  - [When to use `skip_cli` on `operand`](#when-to-use-skip_cli-on-operand)
+- [`Base#with_stdin` mechanics](#basewith_stdin-mechanics)
+- [Options completeness — consult the latest-version docs first](#options-completeness--consult-the-latest-version-docs-first)
+  - [`requires_git_version` convention](#requires_git_version-convention)
+  - [Execution-model conflicts](#execution-model-conflicts)
+- [`end_of_options` placement](#end_of_options-placement)
+  - [Rule 1 — SYNOPSIS shows `--`: mirror the SYNOPSIS](#rule-1--synopsis-shows----mirror-the-synopsis)
+  - [Rule 2 — SYNOPSIS does NOT show `--`: protect operands from flag misinterpretation](#rule-2--synopsis-does-not-show----protect-operands-from-flag-misinterpretation)
+- [Exit status guidance](#exit-status-guidance)
+- [Facade delegation and policy options](#facade-delegation-and-policy-options)
+- [Internal compatibility contract](#internal-compatibility-contract)
+- [Phased rollout requirements](#phased-rollout-requirements)
+- [Common failures](#common-failures)
+  - [Policy/output-control flag hardcoded as `literal` (neutrality violation)](#policyoutput-control-flag-hardcoded-as-literal-neutrality-violation)
+  - [Unnecessary `def call` override](#unnecessary-def-call-override)
+  - [`execution_option` for fixed kwargs](#execution_option-for-fixed-kwargs)
+  - [Other common failures](#other-common-failures)
+
+## Files to generate
 
 For `Git::Commands::Foo::Bar`, **all three files are required and must be created**:
 
@@ -94,13 +49,13 @@ Optional (first command in module):
 
 - `lib/git/commands/foo.rb`
 
-### Single class vs. sub-command namespace
+## Single class vs. sub-command namespace
 
 Most git commands map to a single class. Split into a namespace module with multiple
 sub-command classes when the git command surfaces **meaningfully different
 operations** that have distinct call shapes or protocols.
 
-#### When to use sub-commands
+### When to use sub-commands
 
 **Split by operation** — when the git command has named sub-actions whose option sets
 have little overlap (each sub-action would have mostly dead options if they shared
@@ -117,7 +72,7 @@ git worktree add / list / remove / move
 uses `Base#with_stdin`; mixing that with a no-stdin path in one class produces an
 awkward interface.
 
-#### Do NOT split by output format / output mode
+### Do NOT split by output format / output mode
 
 **Output-mode flags are NOT a reason to create separate subclasses.** When a git
 command supports multiple output formats via flags (`--patch`, `--numstat`, `--raw`,
@@ -153,15 +108,15 @@ define which git sub-operation the class represents (e.g., `literal 'stash'`,
 `literal 'show'`, `literal '--delete'`). Output-format flags are not operation
 selectors.
 
-#### When to keep a single class
+### When to keep a single class
 
 - Different output modes (`--patch`, `--numstat`, `--raw`): **always** use a single
   class; expose modes as DSL options.
 - Minor option variations that share the same argument set.
 - When the "special mode" is just 1–2 flags — use `flag_option`/`value_option`.
 - When callers would always need multiple modes together (the facade composes them).
 
-#### Naming sub-command classes
+### Naming sub-command classes
 
 Prefer **user-oriented names** (what the caller gets back) over flag names
 (implementation detail the caller shouldn't need to know):
@@ -184,7 +139,7 @@ Two hard constraints:
   `Git::Commands::*`. A reader seeing `CommandFoo::BarInfo` expects a data struct,
   not a class that runs a subprocess.
 
-#### Namespace module template
+### Namespace module template
 
 When splitting, create a bare namespace module file (`foo.rb`) — no class — matching
 the pattern of `diff.rb` and `cat_file.rb`:
@@ -212,7 +167,55 @@ end
 Each sub-command file adds `@see Git::Commands::Foo` to link back to the parent
 module's overview.
 
-### Command template (Base pattern)
+## Architecture contract
+
+For migrated commands, the expected structure is:
+
+```ruby
+require 'git/commands/base'
+
+class SomeCommand < Git::Commands::Base
+  arguments do
+    ...
+  end
+
+  # optional — only when introduced after Git::MINIMUM_GIT_VERSION
+  requires_git_version '2.29.0'
+
+  # optional for non-zero successful exits
+  # reason comment
+  allow_exit_status 0..1
+
+  # @!method call(*, **)
+  #
+  #   @overload call(**options)
+  #
+  #     YARD docs for this command's call signature.
+  #
+  #     @return [Git::CommandLineResult]
+end
+```
+
+The `@!method` directive is the correct YARD form when the class contains **no
+explicit `def call`** — YARD uses it to render per-command docs on the inherited
+`call` method. When the class **does** define `def call` explicitly, place YARD
+docs directly above `def call` and omit the `@!method` directive.
+
+Shared behavior lives in `Base`:
+
+- binds arguments
+- calls `@execution_context.command_capturing(*args, **args.execution_options, raise_on_failure: false)`
+- raises `Git::FailedError` unless exit status is in allowed range (`0..0` default)
+
+Structural requirements:
+
+- Class inherits from `Git::Commands::Base`
+- File requires `git/commands/base` (not `git/commands/arguments`)
+- Has exactly one `arguments do` declaration
+- Does not define command-specific `initialize` that only assigns
+  `@execution_context`
+
+## Command template (Base pattern)
 
 ```ruby
 # frozen_string_literal: true
@@ -280,17 +283,58 @@ YARD tag formatting rules (short descriptions, continuation paragraphs, punctuat
 are defined in the [YARD Documentation](../yard-documentation/SKILL.md) skill. The
 template above demonstrates the correct form.
 
-When the command requires an explicit `def call` override (input validation, stdin
-feeding, non-trivial option routing), place YARD docs **directly above** `def call`
-instead of using `@!method`. See the [`#call` override
-guidance](../review-command-implementation/SKILL.md#call-override-guidance) in the
-Review Command Implementation skill.
-
-#### Overriding `call` — inline example
-
-When `def call(...) = super` is not enough, override `call` explicitly. Place YARD
-doc comments **directly above** `def call` — do **not** use `# @!method call(*, **)`
-alongside an explicit override:
+## `#call` override guidance
+
+Most commands use only a `# @!method call(*, **)` YARD directive with no
+explicit `def call` — the inherited `Base#call` handles binding, execution,
+and exit-status validation automatically. Do **not** add `def call(*, **) = super`
+or `def call(*, **) / super / end` for commands that need no custom logic; it
+adds no behavior and conflicts with the `@!method` directive.
+
+**Override `call` only when the command needs:**
+
+1. **Input validation the DSL cannot express** — per-argument validation parameters
+   (`required:`, `type:`, `allow_nil:`, etc.) and operand format validation belong
+   in `arguments do`. Cross-argument constraint methods are generally **not** declared;
+   git validates its own option semantics. The narrow exception is **arguments git
+   cannot observe in its argv**: if an argument is `skip_cli: true` and never
+   reaches git's argv, git cannot detect incompatibilities — use `conflicts` and/or
+   `requires_one_of` in the DSL (e.g., `cat-file --batch` uses both because
+   `:objects` is `skip_cli: true`). Do not raise `ArgumentError` manually for things
+   the DSL can express via a constraint declaration.
+2. **stdin feeding** — batch protocols (`--batch`, `--batch-check`) via
+   `Base#with_stdin`
+3. **Non-trivial option routing** — build different argument sets based on
+   which options are present
+4. **Action-option-with-optional-value** — when the command's primary action is
+   expressed as an option with an optional value (man-page notation:
+   `--flag[=<value>]`). The DSL entry uses `flag_or_value_option :name, inline:
+   true, type: [TrueClass, String]` and the override maps a positional `call` API
+   onto the keyword:
+
+   ```ruby
+   def call(value = true, *, **)
+     super(*, **, option_name: value)
+   end
+   ```
+
+**When overriding:**
+
+- Bind arguments via `args_definition.bind(...)` — do not reimplement binding
+- Delegate exit-status handling to `validate_exit_status!` — do not reimplement
+- Do not call `super` after manual binding; use `@execution_context.command_capturing` directly
+
+**DSL defaults:**
+
+Defaults defined in the DSL (e.g., `operand :paths, default: ['.']`) are applied
+automatically during `args_definition.bind(...)` — do not set defaults manually in
+`call`.
+
+When the command requires an explicit `def call` override, place YARD doc comments
+**directly above** `def call` — do **not** use `# @!method call(*, **)` alongside
+an explicit override.
+
+### Overriding `call` — inline example
 
 ```ruby
 # @overload call(*objects, **options)
@@ -335,7 +379,7 @@ arguments do
 end
 ```
 
-##### Action-option-with-optional-value commands
+### Action-option-with-optional-value commands
 
 When a git command's primary action is an option with an optional value (man-page
 notation: `--flag[=<value>]`, e.g. `git am --show-current-patch[=(diff|raw)]`), use
@@ -378,7 +422,7 @@ Where:
 The `type: [TrueClass, String]` on the DSL entry rejects `false` at bind time,
 removing the need for manual validation in the override.
 
-##### When to use `skip_cli` on `operand`
+### When to use `skip_cli` on `operand`
 
 Use `operand ..., skip_cli: true` when all of the following are true:
 
@@ -405,16 +449,41 @@ Key points:
 - **Extract helpers** like `run_batch` to stay within Rubocop `Metrics/MethodLength`
   and `Metrics/AbcSize` thresholds. Aim to keep `call` under ~10 lines.
 
-### Options completeness — consult the latest-version docs first
+## `Base#with_stdin` mechanics
+
+`Base#with_stdin(content)` opens an `IO.pipe`, spawns a background `Thread` that
+writes `content` to the write end (then closes it), and yields the read end as
+`in:` to the execution context. The threaded write prevents deadlocks when
+`content` exceeds the OS pipe buffer — the subprocess can drain the pipe
+concurrently. The thread also rescues `Errno::EPIPE` / `IOError` so it exits
+cleanly if the subprocess closes stdin early.
+
+Use `with_stdin` instead of manual pipe management. `StringIO` cannot be used
+because `Process.spawn` requires a real file descriptor.
+
+Example — batch stdin protocol (as used by `git cat-file --batch`):
+
+```ruby
+def call(*, **)
+  bound = args_definition.bind(*, **)
+  with_stdin(Array(bound.objects).map { |object| "#{object}\n" }.join) do |stdin_r|
+    run_batch(bound, stdin_r)
+  end
+end
+```
+
+## Options completeness — consult the latest-version docs first
 
 **Before writing any DSL entries**, use the documentation fetched during the
-[Input](#git-documentation-for-the-git-command) phase and enumerate every option the
-latest-version docs describe.
+[Input](SKILL.md#git-documentation-for-the-git-command) phase and enumerate every
+option the latest-version docs describe.
 
-#### `requires_git_version` convention
+### `requires_git_version` convention
 
 `requires_git_version` is a **class-level** declaration only. Individual options do
-**not** carry version annotations.
+**not** carry version annotations. The declaration must use a `'major.minor.patch'`
+string (e.g., `'2.29.0'`), not a `Gem::Version` or `Range` — pre-release versions
+are not supported.
 
 | Scenario | Action |
 |---|---|
@@ -488,7 +557,7 @@ This step is required. A command class that only exposes the options that happen
 be used today in `Git::Lib` is incomplete — callers of the future API should not need
 to re-open the docs just because the scaffold only covered current usage.
 
-#### Execution-model conflicts
+### Execution-model conflicts
 
 Command classes are neutral — they never hardcode policy choices. Policy defaults
 (`edit: false`, `progress: false`, etc.) belong to the facade (`Git::Lib`).
@@ -516,12 +585,12 @@ CONTRIBUTING.md.
 **`--verbose`/`-v` and `--quiet`/`-q`:** include these unless their git
 implementation requires interactive I/O.
 
-### `end_of_options` placement
+## `end_of_options` placement
 
 Determine placement based on whether the SYNOPSIS explicitly shows `--`. See the
 Review Arguments DSL checklist for the full decision tree.
 
-#### Rule 1 — SYNOPSIS shows `--`: mirror the SYNOPSIS
+### Rule 1 — SYNOPSIS shows `--`: mirror the SYNOPSIS
 
 When the SYNOPSIS explicitly shows `--` between operand groups (e.g., `[<tree-ish>]
 [--] [<pathspec>...]`), place `end_of_options` in the same position the SYNOPSIS
@@ -538,7 +607,7 @@ end_of_options                                                # mirrors SYNOPSIS
 value_option :pathspec, as_operand: true, repeatable: true    # AFTER end_of_options
 ```
 
-#### Rule 2 — SYNOPSIS does NOT show `--`: protect operands from flag misinterpretation
+### Rule 2 — SYNOPSIS does NOT show `--`: protect operands from flag misinterpretation
 
 Insert `end_of_options` immediately before the first `operand` whenever any
 `flag_option`, `value_option`, `flag_or_value_option`, `key_value_option`, or
@@ -576,7 +645,7 @@ unnecessarily verbose command lines (e.g. `git remote remove -- origin` instead
 `git remote remove origin`). When in doubt, add it — the Review Arguments DSL skill
 flags a missing `end_of_options` as an error when options appear before operands.
 
-### Exit status guidance
+## Exit status guidance
 
 - Default: no declaration needed (`0..0` from `Base`)
 - Non-default: declare `allow_exit_status <range>` and add rationale comment
@@ -593,7 +662,7 @@ allow_exit_status 0..1
 allow_exit_status 0..7
 ```
 
-### Facade delegation and policy options
+## Facade delegation and policy options
 
 The command class is only half the story. After scaffolding the command, you must
 also write (or update) the `Git::Lib` method that **delegates** to it. The facade
@@ -633,89 +702,92 @@ See [Extract Command from Lib](../extract-command-from-lib/SKILL.md) for the com
 delegation workflow and additional patterns (stdout passthrough, parsed return
 values, opts-hash normalization).
 
-### Phased rollout, compatibility, and quality gates
-
-See [Review Command Implementation](../review-command-implementation/SKILL.md) for
-the canonical phased rollout checklist, internal compatibility contract, and quality
-gate commands. In summary:
-
-- **always work on a feature branch** — never commit or push directly to `main`;
-  create a branch before starting (`git checkout -b <feature-branch-name>`) and open
-  a pull request when the slice is ready
-- migrate in small slices (pilot or family), not all commands at once
-- keep each slice independently revertible
-- pass per-slice gates: `bundle exec rspec`, `bundle exec rake test`, `bundle exec
-  rubocop`, `bundle exec rake yard`
-
-## Workflow
-
-1. **Gather input** — collect the target class name and git subcommand from
-   the [Input](#input), then fetch the latest-version and minimum-version
-   git documentation per [Git documentation for the git
-   command](#git-documentation-for-the-git-command).
-
-2. **Determine class structure** — decide between a single class and a sub-command
-   namespace per [Single class vs. sub-command
-   namespace](#single-class-vs-sub-command-namespace).
-
-3. **For each command / sub-command class**, repeat steps 3a–3f:
-
-   a. **Scaffold the command class (subagent)** — delegate to a subagent: load
-      the [YARD Documentation](../yard-documentation/SKILL.md) skill, then
-      generate `lib/git/commands/{command}.rb` using the [Command
-      template](#command-template-base-pattern). Populate the `arguments do`
-      block with all options from the latest-version docs per [Options
-      completeness](#options-completeness--consult-the-latest-version-docs-first),
-      applying the [Execution-model conflicts](#execution-model-conflicts),
-      [`end_of_options` placement](#end_of_options-placement), and [Exit status
-      guidance](#exit-status-guidance) rules. Pass the fetched git documentation
-      to the subagent.
-
-   Steps 3b and 3c may run **in parallel** (they produce independent files).
-
-   b. **Scaffold unit tests (subagent)** — delegate to a subagent: load
-      **[Command Test Conventions](../command-test-conventions/SKILL.md)** (which loads
-      [RSpec Unit Testing Standards](../rspec-unit-testing-standards/SKILL.md)),
-      then generate `spec/unit/git/commands/{command}_spec.rb` following the
-      unit test conventions. Fix all findings, then re-run the review until clean.
-
-   c. **Scaffold integration tests (subagent)** — delegate to a subagent: load
-      **[Command Test Conventions](../command-test-conventions/SKILL.md)**, then generate
-      `spec/integration/git/commands/{command}_spec.rb` following the integration
-      test conventions. Fix all findings, then re-run the review until clean.
-
-   d. **Review Arguments DSL (subagent)** — delegate to a subagent: load and
-      apply **[Review Arguments DSL](../review-arguments-dsl/SKILL.md)** (and its
-      [CHECKLIST.md](../review-arguments-dsl/CHECKLIST.md)) against the
-      `arguments do` block. Fix all findings, then re-run the review until clean.
-      **Complete this step before starting steps 3e–3f** — DSL corrections change
-      the CLI arguments that tests and YARD docs must reflect.
-
-   Steps 3e and 3f may run **in parallel** (they review independent file sets).
-
-   e. **Review Command Tests (subagent)** — delegate to a subagent: load and
-      apply **[Command Test Conventions](../command-test-conventions/SKILL.md)** against
-      the unit and integration spec files. Fix all findings, then re-run the
-      review until clean.
-
-   f. **Review YARD Documentation (subagent)** — delegate to a subagent: load
-      and apply **[Command YARD Documentation](../command-yard-documentation/SKILL.md)**
-      against the command class. Fix all findings, then re-run the review until
-      clean.
-
-4. **Scaffold facade delegation** — write or update the `Git::Lib` method per [Facade
-   delegation and policy options](#facade-delegation-and-policy-options).
-
-5. **Run quality gates** — pass per-slice gates: `bundle exec rspec`, `bundle exec
-   rake test`, `bundle exec rubocop`, `bundle exec rake yard`.
-
-## Output
-
-Produce:
-
-1. **Command class** — `lib/git/commands/{command}.rb` (and optionally the namespace
-   module file for the first command in a namespace)
-2. **Unit tests** — `spec/unit/git/commands/{command}_spec.rb`
-3. **Integration tests** — `spec/integration/git/commands/{command}_spec.rb`
-4. **Facade delegation** — updated `Git::Lib` method in `lib/git/lib.rb`
-5. **All quality gates pass** — rspec, minitest, rubocop, and yard all green
+## Internal compatibility contract
+
+This is the canonical location for the internal compatibility contract. Other
+skills reference this section rather than duplicating it.
+
+Ensure refactors preserve these contract expectations:
+
+- constructor shape remains `initialize(execution_context)` (inherited from `Base`)
+- command entrypoint remains `call(*, **)` at runtime (via `Base#call`)
+- argument-definition metadata remains available via `args_definition`
+
+If an intentional deviation exists, require migration notes/changelog documentation.
+
+## Phased rollout requirements
+
+This is the canonical location for phased rollout requirements. Other skills
+reference this section rather than duplicating the full checklist.
+
+For migration PRs, verify process constraints:
+
+- changes are on a feature branch — **never commit or push directly to `main`**
+- migration slice is scoped (pilot or one family), not all commands at once
+- each slice is independently revertible
+- refactor-only changes are not mixed with unrelated behavior changes
+- quality gates pass for the slice — discover tasks via
+  `bundle exec ruby -e "require 'rake'; load 'Rakefile'; puts Rake::Task['default:parallel'].prerequisites"`
+  and run each individually via `bundle exec rake <task>`, fixing failures before
+  advancing
+
+## Common failures
+
+### Policy/output-control flag hardcoded as `literal` (neutrality violation)
+
+`literal` entries for output-control, editor-suppression, progress, or verbose
+flags inside a command class violate the neutrality principle. The command class
+must model the git CLI faithfully; the facade sets safe defaults and callers may
+override them.
+
+Symptom: the command class contains one or more of:
+
+```ruby
+# ❌ Any of these are neutrality violations
+literal '--no-edit'
+literal '--verbose'
+literal '--no-progress'
+literal '--no-color'
+literal '--porcelain'
+```
+
+Fix: convert each to a DSL option and pass the policy value from the facade:
+
+```ruby
+# ✅ In the command class — neutral DSL declaration
+flag_option :edit, negatable: true
+flag_option :progress, negatable: true
+flag_option :verbose
+value_option :format
+
+# ✅ In Git::Lib — facade passes the policy value explicitly
+Git::Commands::Pull.new(self).call(edit: false, progress: false)
+Git::Commands::Mv.new(self).call(*args, verbose: true)
+Git::Commands::Fsck.new(self).call(progress: false)
+```
+
+See "Command-layer neutrality" in CONTRIBUTING.md for the full policy.
+
+### Unnecessary `def call` override
+
+Do **not** add `def call(*, **) = super` or `def call(*, **) / super / end` for
+commands that need no custom logic; it adds no behavior and conflicts with the
+`@!method` directive.
+
+### `execution_option` for fixed kwargs
+
+`execution_option` must **not** be used for kwargs whose value must be
+unconditionally fixed regardless of caller input. If a kwarg always has a specific
+required value (e.g. `chomp: false` for commands returning raw content where trailing
+newlines are data), hardcode it in a `def call` override instead — exposing it via
+`execution_option` would allow callers to override a value that must never change.
+
+### Other common failures
+
+- lingering `ARGS = Arguments.define` constant and custom `#call`
+- command-specific duplicated exit-status checks instead of `allow_exit_status`
+- missing rationale comment for `allow_exit_status`
+- missing YARD directive (`# @!method call(*, **)`)
+- `call` override that reimplements `Base#call` logic instead of delegating to `validate_exit_status!`
+- using a manual `IO.pipe` inline instead of `Base#with_stdin` for stdin-feeding commands
+- migration PR scope too broad (not phased)
diff --git a/.github/skills/command-implementation/SKILL.md b/.github/skills/command-implementation/SKILL.md
@@ -0,0 +1,223 @@
+---
+name: command-implementation
+description: "Scaffolds new and reviews existing Git::Commands::* classes with unit tests, integration tests, and YARD docs using the Base architecture. Use when creating a new command from scratch, updating an existing command, or reviewing a command class for correctness."
+---
+
+# Command Implementation
+
+Scaffold new and review existing `Git::Commands::Base` command classes, unit tests,
+integration tests, and YARD docs.
+
+## Contents
+
+- [Contents](#contents)
+- [Related skills](#related-skills)
+- [Input](#input)
+  - [Command source code](#command-source-code)
+  - [Command test code](#command-test-code)
+  - [Git documentation for the git command](#git-documentation-for-the-git-command)
+- [Reference](#reference)
+- [Workflow](#workflow)
+- [Output](#output)
+
+## Related skills
+
+Additional related skills:
+
+- [Review Arguments DSL](../review-arguments-dsl/SKILL.md) — verify every DSL entry
+  is correct and complete
+- [Command YARD Documentation](../command-yard-documentation/SKILL.md) — verify
+  documentation completeness and formatting
+- [RSpec Unit Testing Standards](../rspec-unit-testing-standards/SKILL.md) — baseline
+  RSpec rules all generated unit specs must comply with
+- [Command Test Conventions](../command-test-conventions/SKILL.md) — conventions for
+  writing and reviewing unit and integration tests for command classes
+- [Review Cross-Command Consistency](../review-cross-command-consistency/SKILL.md) —
+  sibling consistency within a command family
+
+## Input
+
+The user provides the target `Git::Commands::*` class name and the git subcommand (or
+subcommand + sub-action) it wraps. The agent gathers the following.
+
+### Command source code
+
+Read the command class from `lib/git/commands/{command}.rb` or, for subcommands,
+`lib/git/commands/{command}/{subcommand}.rb`. For subcommands, also read the
+namespace module at `lib/git/commands/{command}.rb` which lists all sibling
+subcommands and provides the module-level documentation.
+
+Skip this step when scaffolding a new command (the file does not exist yet).
+
+### Command test code
+
+Read unit tests matching `spec/unit/git/commands/{command}/**/*_spec.rb`. Use these as
+supplemental evidence when tracing the verification chain (Ruby call → bound
+argument → expected git CLI). Coverage completeness is assessed by the
+[Command Test Conventions](../command-test-conventions/SKILL.md) skill.
+
+Skip this step when scaffolding a new command (the file does not exist yet).
+
+### Git documentation for the git command
+
+- **Latest-version online command documentation**
+
+  Read the **entire** official git documentation online man page for the command
+  for the latest version of git. This version will be used as the primary
+  authority for DSL completeness, including the options to include in the
+  DSL, argument names, aliases, ordering, etc.
+  Fetch this version from the URL `https://git-scm.com/docs/git-{command}`
+  (this URL always serves the latest release).
+
+- **Minimum-version online command documentation**
+
+  Read the **entire** official git documentation online man page for the command for
+  the `Git::MINIMUM_GIT_VERSION` version of git. This will be used only for
+  command-introduction and `requires_git_version` decisions. Fetch this version from
+  URL `https://git-scm.com/docs/git-{command}/{version}`.
+
+Do **not** scaffold from local `git <command> -h` output — the installed Git
+version is unknown and may differ from the latest supported version. Local help may
+be used as a supplemental check only.
+
+## Reference
+
+See [REFERENCE.md](REFERENCE.md) for the full reference covering:
+
+- Files to generate
+- Single class vs. sub-command namespace (when to split, naming, templates)
+- Architecture contract and structural requirements
+- Command template (Base pattern)
+- `#call` override guidance (when to override, stdin feeding, action-option patterns)
+- `Base#with_stdin` mechanics
+- Options completeness (version conventions, execution-model conflicts)
+- `end_of_options` placement rules
+- Exit status guidance
+- Facade delegation and policy options
+- Internal compatibility contract
+- Phased rollout requirements
+- Common failures
+
+Subagents load REFERENCE.md directly during the workflow steps that need it.
+
+## Workflow
+
+This skill supports three modes. Determine which mode applies before starting:
+
+- **Scaffold** — creating a new command class from scratch. Follow all steps.
+- **Update** — adding options to an existing command class: skip steps 2, 3a, 3b,
+  and 3c (the class and test files already exist). Start from step 1, then proceed
+  directly to 3d → 3e → 3f → 4 → 5.
+- **Review** — auditing an existing command class for correctness (no changes).
+  Follow all steps but produce findings instead of code.
+
+1. **Gather input** — collect the target class name and git subcommand from
+   the [Input](#input), then fetch the latest-version and minimum-version
+   git documentation per [Git documentation for the git
+   command](#git-documentation-for-the-git-command).
+
+2. **Determine class structure** *(scaffold mode only)* — decide between a single
+   class and a sub-command namespace per [Single class vs. sub-command
+   namespace](REFERENCE.md#single-class-vs-sub-command-namespace).
+
+3. **For each command / sub-command class**, repeat steps 3a–3f:
+
+   a. **Scaffold the command class (subagent)** *(scaffold mode only)* — delegate
+      to a subagent: load [REFERENCE.md](REFERENCE.md) and the
+      [YARD Documentation](../yard-documentation/SKILL.md) skill, then generate
+      `lib/git/commands/{command}.rb` using the [Command
+      template](REFERENCE.md#command-template-base-pattern). Populate the
+      `arguments do` block with all options from the latest-version docs per
+      [Options completeness](REFERENCE.md#options-completeness--consult-the-latest-version-docs-first),
+      applying the [Execution-model conflicts](REFERENCE.md#execution-model-conflicts),
+      [`end_of_options` placement](REFERENCE.md#end_of_options-placement), and
+      [Exit status guidance](REFERENCE.md#exit-status-guidance) rules. Pass the
+      fetched git documentation to the subagent.
+
+   Steps 3b and 3c may run **in parallel** (they produce independent files).
+
+   b. **Scaffold unit tests (subagent)** *(scaffold mode only)* — delegate to a
+      subagent: load **[Command Test
+      Conventions](../command-test-conventions/SKILL.md)** (which loads [RSpec Unit
+      Testing Standards](../rspec-unit-testing-standards/SKILL.md)), then generate
+      `spec/unit/git/commands/{command}_spec.rb` following the unit test
+      conventions. Fix all findings, then repeat the review until clean.
+
+   c. **Scaffold integration tests (subagent)** *(scaffold mode only)* — delegate
+      to a subagent: load **[Command Test
+      Conventions](../command-test-conventions/SKILL.md)**, then generate
+      `spec/integration/git/commands/{command}_spec.rb` following the integration
+      test conventions. Fix all findings, then repeat the review until clean.
+
+   d. **Review Arguments DSL (subagent)** — delegate to a subagent: load and
+      apply **[Review Arguments DSL](../review-arguments-dsl/SKILL.md)** (and its
+      [CHECKLIST.md](../review-arguments-dsl/CHECKLIST.md)) against the
+      `arguments do` block. Fix all findings, then repeat the review until clean.
+      **Complete this step before starting steps 3e–3f** — DSL corrections change
+      the CLI arguments that tests and YARD docs must reflect.
+
+   Steps 3e and 3f may run **in parallel** (they review independent file sets).
+
+   e. **Review Command Tests (subagent)** — delegate to a subagent: load and
+      apply **[Command Test Conventions](../command-test-conventions/SKILL.md)** against
+      the unit and integration spec files. Fix all findings, then repeat the
+      review until clean.
+
+   f. **Review YARD Documentation (subagent)** — delegate to a subagent: load
+      and apply **[Command YARD Documentation](../command-yard-documentation/SKILL.md)**
+      against the command class. Fix all findings, then repeat the review until
+      clean.
+
+4. **Review class shape and declarations** — load
+   [REFERENCE.md](REFERENCE.md) and verify against the
+   [Architecture contract](REFERENCE.md#architecture-contract), [`#call` override
+   guidance](REFERENCE.md#call-override-guidance), [Exit status
+   guidance](REFERENCE.md#exit-status-guidance), [`requires_git_version`
+   convention](REFERENCE.md#requires_git_version-convention), [Internal compatibility
+   contract](REFERENCE.md#internal-compatibility-contract), and [Common
+   failures](REFERENCE.md#common-failures). Additionally:
+
+   - For **scaffold** and **update** modes: write or update the
+     `Git::Lib` method per [Facade delegation and policy
+     options](REFERENCE.md#facade-delegation-and-policy-options).
+   - For **migration PRs**: verify [Phased rollout
+     requirements](REFERENCE.md#phased-rollout-requirements).
+
+5. **Run quality gates** — discover the prerequisite tasks for
+   `default:parallel` and run them sequentially, fixing failures before
+   advancing:
+
+   ```bash
+   bundle exec ruby -e "require 'rake'; load 'Rakefile'; puts Rake::Task['default:parallel'].prerequisites"
+   ```
+
+   Run each listed task in order via `bundle exec rake <task>`. On failure, fix
+   the issue and re-run that task. Once it passes, continue to the next. After
+   all tasks pass, re-run the full sequence from the first task to confirm no
+   fix broke an earlier gate. Repeat until the whole sequence runs without error.
+
+## Output
+
+For **scaffold** and **update** modes, produce:
+
+1. **Command class** — `lib/git/commands/{command}.rb` (and optionally the namespace
+   module file for the first command in a namespace)
+2. **Unit tests** — `spec/unit/git/commands/{command}_spec.rb`
+3. **Integration tests** — `spec/integration/git/commands/{command}_spec.rb`
+4. **Facade delegation** — updated `Git::Lib` method in `lib/git/lib.rb`
+5. **All quality gates pass** — rspec, minitest, rubocop, and yard all green
+
+For **review** mode, produce:
+
+| Check | Status | Issue |
+| --- | --- | --- |
+| Base inheritance | Pass/Fail | ... |
+| arguments DSL | Pass/Fail | ... |
+| call shim | Pass/Fail | ... |
+| allow_exit_status usage | Pass/Fail | ... |
+| requires_git_version | Pass/Fail | ... |
+| output parsing absent | Pass/Fail | ... |
+| compatibility contract | Pass/Fail | ... |
+
+Then list required fixes and indicate whether the migration slice is safe to merge
+under phased-rollout rules.
diff --git a/.github/skills/command-test-conventions/SKILL.md b/.github/skills/command-test-conventions/SKILL.md
@@ -15,7 +15,7 @@ Conventions for writing and reviewing unit and integration tests for
   coverage; this skill adds command-specific conventions on top
 - [Review Arguments DSL](../review-arguments-dsl/SKILL.md) — verifying DSL entries
   match git CLI
-- [Review Command Implementation](../review-command-implementation/SKILL.md) — class
+- [Command Implementation](../command-implementation/SKILL.md) — class
   structure, phased rollout gates, and internal compatibility contracts
 - [Command YARD Documentation](../command-yard-documentation/SKILL.md)
   — documentation completeness for command classes
diff --git a/.github/skills/command-yard-documentation/SKILL.md b/.github/skills/command-yard-documentation/SKILL.md
@@ -14,7 +14,7 @@ command-specific rules.
 This skill verifies that YARD docs accurately mirror the `arguments do` block
 as-implemented. It does not re-adjudicate which options belong based on Git
 version — version gating is the domain of the DSL and the
-[Scaffold New Command](../scaffold-new-command/SKILL.md) skill, not YARD review.
+[Command Implementation](../command-implementation/SKILL.md) skill, not YARD review.
 
 ## Contents
 
@@ -44,7 +44,7 @@ version — version gating is the domain of the DSL and the
   source for general YARD formatting rules and writing standards
 - [Review Arguments DSL](../review-arguments-dsl/SKILL.md) — verifying DSL entries
   match git CLI
-- [Review Command Implementation](../review-command-implementation/SKILL.md) — class
+- [Command Implementation](../command-implementation/SKILL.md) — class
   structure, phased rollout gates, and internal compatibility contracts
 - [Command Test Conventions](../command-test-conventions/SKILL.md) — unit/integration
   test conventions for command classes
diff --git a/.github/skills/extract-command-from-lib/SKILL.md b/.github/skills/extract-command-from-lib/SKILL.md
@@ -62,11 +62,10 @@ Before starting, you **MUST** load the following skill(s) in their entirety:
 
 Run or reference these skills during the workflow:
 
-- [Scaffold New Command](../scaffold-new-command/SKILL.md) — generates the `Git::Commands::*` class, unit tests,
-  integration tests, and YARD docs (used in Step 4 if the command class does not
-  exist yet)
-- [Review Command Implementation](../review-command-implementation/SKILL.md) — canonical class-shape checklist, phased
-  rollout gates, and internal compatibility contracts
+- [Command Implementation](../command-implementation/SKILL.md) — generates and reviews `Git::Commands::*`
+  classes, unit tests, integration tests, and YARD docs (used in Step 4 if the
+  command class does not exist yet); also the canonical class-shape checklist,
+  phased rollout gates, and internal compatibility contracts
 - [Review Arguments DSL](../review-arguments-dsl/SKILL.md) — verifying DSL entries match git CLI
 - [Command Test Conventions](../command-test-conventions/SKILL.md) — unit/integration test conventions for command classes
 - [Command YARD Documentation](../command-yard-documentation/SKILL.md) — documentation completeness for command classes
@@ -189,7 +188,7 @@ Before making any changes, verify that `tests/units/` has adequate tests for the
 2. **If the command class already exists**, skip to Step 5.
 
 3. **If the command class does not exist**, scaffold it using the
-  [Scaffold New Command](../scaffold-new-command/SKILL.md) skill. This produces:
+  [Command Implementation](../command-implementation/SKILL.md) skill. This produces:
 
    - `lib/git/commands/<command>.rb` (or `lib/git/commands/<family>/<action>.rb`)
    - `spec/unit/git/commands/<command>_spec.rb`
diff --git a/.github/skills/project-context/SKILL.md b/.github/skills/project-context/SKILL.md
@@ -31,8 +31,8 @@ coding standard details, or implementation constraints.
 
 - [Development Workflow](../development-workflow/SKILL.md) — TDD cycle and commit
   conventions for day-to-day work
-- [Scaffold New Command](../scaffold-new-command/SKILL.md) — generating new command
-  classes in the layered architecture
+- [Command Implementation](../command-implementation/SKILL.md) — generating and
+  reviewing command classes in the layered architecture
 - [YARD Documentation](../yard-documentation/SKILL.md) — documentation
   standards
 
@@ -284,7 +284,7 @@ swallow exceptions silently.
 
 Follow the three-layer pattern: command class (CLI contract) → parser (output
 transform) → `Git::Lib` method (orchestration + rich object). See
-[Scaffold New Command](../scaffold-new-command/SKILL.md).
+[Command Implementation](../command-implementation/SKILL.md).
 
 ### Working with paths
 
diff --git a/.github/skills/refactor-command-to-commandlineresult/SKILL.md b/.github/skills/refactor-command-to-commandlineresult/SKILL.md
@@ -47,7 +47,7 @@ Before starting, you **MUST** load the following skill(s) in their entirety:
 
 ## Related skills
 
-- [Review Command Implementation](../review-command-implementation/SKILL.md) — canonical class-shape checklist, phased
+- [Command Implementation](../command-implementation/SKILL.md) — canonical class-shape checklist, phased
   rollout gates, and internal compatibility contracts
 - [Review Arguments DSL](../review-arguments-dsl/SKILL.md) — verifying DSL entries match git CLI
 - [Command Test Conventions](../command-test-conventions/SKILL.md) — unit/integration test conventions for command classes
@@ -118,7 +118,7 @@ end
 
 ## Migration process and internal compatibility
 
-See [Review Command Implementation](../review-command-implementation/SKILL.md) for the canonical phased rollout checklist
+See [Command Implementation](../command-implementation/SKILL.md) for the canonical phased rollout checklist
 and internal compatibility contract. In summary:
 
 - **always work on a feature branch** — never commit or push directly to `main`;
diff --git a/.github/skills/review-arguments-dsl/CHECKLIST.md b/.github/skills/review-arguments-dsl/CHECKLIST.md
@@ -683,9 +683,10 @@ semantics. There are two narrow exceptions:
 ## 7. Check class-level declarations
 
 The following class-level declarations are **not** part of `arguments do` but should
-be verified alongside DSL entries. The canonical rules live in [Review Command
-Implementation](../review-command-implementation/SKILL.md) — see §3 (exit-status)
-and §4 (version gating). Briefly:
+be verified alongside DSL entries. The canonical rules live in [Command
+Implementation](../command-implementation/REFERENCE.md) — see
+[Exit status guidance](../command-implementation/REFERENCE.md#exit-status-guidance)
+and [`requires_git_version` convention](../command-implementation/REFERENCE.md#requires_git_version-convention). Briefly:
 
 - **`allow_exit_status`** — present with a `Range` and rationale comment when the
   command has non-zero successful exits.
diff --git a/.github/skills/review-arguments-dsl/SKILL.md b/.github/skills/review-arguments-dsl/SKILL.md
@@ -25,7 +25,7 @@ methods and modifiers.
 
 ## Related skills
 
-- [Review Command Implementation](../review-command-implementation/SKILL.md) — class structure, phased rollout gates, and
+- [Command Implementation](../command-implementation/SKILL.md) — class structure, phased rollout gates, and
   internal compatibility contracts
 - [Command Test Conventions](../command-test-conventions/SKILL.md) — unit/integration test conventions for command classes
 - [Command YARD Documentation](../command-yard-documentation/SKILL.md) — documentation completeness for command classes
@@ -52,13 +52,12 @@ argument → expected git CLI). Coverage completeness is assessed by the
 
 - **Latest-version online command documentation**
 
-  Determine the latest released git version by running `bin/latest-git-version`
-  (it prints a version string such as `2.49.0`). Then read the **entire** official
-  git documentation online man page for that version from the URL
-  `https://git-scm.com/docs/git-{command}/{version}` (e.g.,
-  `https://git-scm.com/docs/git-push/2.49.0`). This version will be used as the
-  primary authority for DSL completeness, including the options to include in the
+  Read the **entire** official git documentation online man page for the command
+  for the latest version of git. This version will be used as the primary
+  authority for DSL completeness, including the options to include in the
   DSL, argument names, aliases, ordering, etc.
+  Fetch this version from the URL `https://git-scm.com/docs/git-{command}`
+  (this URL always serves the latest release).
 
 - **Minimum-version online command documentation**
 
diff --git a/.github/skills/review-backward-compatibility/SKILL.md b/.github/skills/review-backward-compatibility/SKILL.md
@@ -48,7 +48,7 @@ Replace `branch` with the specific git command(s) you want to audit (e.g.,
 
 - [Refactor Command to CommandLineResult](../refactor-command-to-commandlineresult/SKILL.md) — migrating command classes to Base;
   the counterpart to this skill's `Git::Lib` facade focus
-- [Review Command Implementation](../review-command-implementation/SKILL.md) — class structure, phased rollout gates, and
+- [Command Implementation](../command-implementation/SKILL.md) — class structure, phased rollout gates, and
   internal compatibility contracts
 
 ## Objective
diff --git a/.github/skills/review-command-implementation/SKILL.md b/.github/skills/review-command-implementation/SKILL.md
@@ -1,387 +0,0 @@
----
-name: review-command-implementation
-description: "Verifies a command class follows the Git::Commands::Base architecture contract and contains no duplicated execution behavior. Use after implementing or modifying a command class."
----
-
-# Review Command Implementation
-
-Verify a command class follows the current `Git::Commands::Base` architecture and
-contains no duplicated execution behavior.
-
-## Contents
-
-- [Contents](#contents)
-- [Related skills](#related-skills)
-- [Input](#input)
-  - [Command source code](#command-source-code)
-  - [Command test code](#command-test-code)
-  - [Git documentation for the git command](#git-documentation-for-the-git-command)
-- [Reference](#reference)
-  - [Architecture Contract](#architecture-contract)
-  - [`#call` Override Guidance](#call-override-guidance)
-  - [`Base#with_stdin` Mechanics](#basewith_stdin-mechanics)
-  - [Git Version Gating](#git-version-gating)
-  - [Internal Compatibility Contract](#internal-compatibility-contract)
-  - [Phased Rollout Requirements](#phased-rollout-requirements)
-  - [Common Failures](#common-failures)
-- [Workflow](#workflow)
-- [Output](#output)
-
-## Related skills
-
-Before starting, you **MUST** load the following prerequisite skill(s) in their
-entirety:
-
-- [YARD Documentation](../yard-documentation/SKILL.md) — authoritative source for
-  YARD formatting rules and writing standards
-
-Additional related skills:
-
-- [Review Arguments DSL](../review-arguments-dsl/SKILL.md) — verifying DSL entries match git CLI
-- [Command Test Conventions](../command-test-conventions/SKILL.md) — unit/integration test conventions for command classes
-- [Command YARD Documentation](../command-yard-documentation/SKILL.md) — documentation completeness for command classes
-- [Review Cross-Command Consistency](../review-cross-command-consistency/SKILL.md) — sibling consistency within a command family
-
-## Input
-
-What the agent requires to run this skill and where to get it.
-
-### Command source code
-
-Read the command class from `lib/git/commands/{command}.rb` or, for subcommands,
-`lib/git/commands/{command}/{subcommand}.rb`. For subcommands, also read the
-namespace module at `lib/git/commands/{command}.rb` which lists all sibling
-subcommands and provides the module-level documentation.
-
-### Command test code
-
-Read unit tests matching `spec/unit/git/commands/{command}/**/*_spec.rb`.
-
-### Git documentation for the git command
-
-- **Latest-version online command documentation**
-
-  Determine the latest released git version by running `bin/latest-git-version`
-  (it prints a version string such as `2.49.0`). Then read the **entire** official
-  git documentation online man page for that version from the URL
-  `https://git-scm.com/docs/git-{command}/{version}` (e.g.,
-  `https://git-scm.com/docs/git-push/2.49.0`). This version will be used as the
-  primary authority for DSL completeness, including the options to include in the
-  DSL, argument names, aliases, ordering, etc.
-
-- **Minimum-version online command documentation**
-
-  Read the **entire** official git documentation online man page for the command for
-  the `Git::MINIMUM_GIT_VERSION` version of git. This will be used only for
-  command-introduction and `requires_git_version` decisions. Fetch this version from
-  URL `https://git-scm.com/docs/git-{command}/{version}`.
-
-Do **not** scaffold from local `git <command> -h` output alone — the installed Git
-version is unknown and may differ from the latest supported version. Local help may
-be used as a supplemental check only.
-
-## Reference
-
-### Architecture Contract
-
-For migrated commands, the expected structure is:
-
-```ruby
-require 'git/commands/base'
-
-class SomeCommand < Git::Commands::Base
-  arguments do
-    ...
-  end
-
-  # optional — only when introduced after Git::MINIMUM_GIT_VERSION
-  requires_git_version '2.29.0'
-
-  # optional for non-zero successful exits
-  # reason comment
-  allow_exit_status 0..1
-
-  # @!method call(*, **)
-  #
-  #   @overload call(**options)
-  #
-  #     YARD docs for this command's call signature.
-  #
-  #     @return [Git::CommandLineResult]
-end
-```
-
-The `@!method` directive is the correct YARD form when the class contains **no
-explicit `def call`** — YARD uses it to render per-command docs on the inherited
-`call` method. When the class **does** define `def call` explicitly, place YARD
-docs directly above `def call` and omit the `@!method` directive.
-
-Shared behavior lives in `Base`:
-
-- binds arguments
-- calls `@execution_context.command_capturing(*args, **args.execution_options, raise_on_failure: false)`
-- raises `Git::FailedError` unless exit status is in allowed range (`0..0` default)
-
-### `#call` Override Guidance
-
-Most commands use only a `# @!method call(*, **)` YARD directive with no
-explicit `def call` — the inherited `Base#call` handles binding, execution,
-and exit-status validation automatically. Do **not** add `def call(*, **) = super`
-or `def call(*, **) / super / end` for commands that need no custom logic; it
-adds no behavior and conflicts with the `@!method` directive.
-
-**Override `call` only when the command needs:**
-
-1. **Input validation the DSL cannot express** — per-argument validation parameters
-   (`required:`, `type:`, `allow_nil:`, etc.) and operand format validation belong
-   in `arguments do`. Cross-argument constraint methods are generally **not** declared;
-   git validates its own option semantics. The narrow exception is **arguments git
-   cannot observe in its argv**: if an argument is `skip_cli: true` and never
-   reaches git's argv, git cannot detect incompatibilities — use `conflicts` and/or
-   `requires_one_of` in the DSL (e.g., `cat-file --batch` uses both because
-   `:objects` is `skip_cli: true`). Do not raise `ArgumentError` manually for things
-   the DSL can express via a constraint declaration.
-2. **stdin feeding** — batch protocols (`--batch`, `--batch-check`) via
-   `Base#with_stdin`
-3. **Non-trivial option routing** — build different argument sets based on
-   which options are present
-4. **Action-option-with-optional-value** — when the command's primary action is
-   expressed as an option with an optional value (man-page notation:
-   `--flag[=<value>]`). The DSL entry uses `flag_or_value_option :name, inline:
-   true, type: [TrueClass, String]` and the override maps a positional `call` API
-   onto the keyword:
-
-   ```ruby
-   def call(value = true, *, **)
-     super(*, **, option_name: value)
-   end
-   ```
-
-   See [Action-option-with-optional-value commands](../scaffold-new-command/SKILL.md#action-option-with-optional-value-commands)
-   for the full pattern and rationale.
-
-**When overriding:**
-
-- Bind arguments via `args_definition.bind(...)` — do not reimplement binding
-- Delegate exit-status handling to `validate_exit_status!` — do not reimplement
-- Do not call `super` after manual binding; use `@execution_context.command_capturing` directly
-
-**DSL defaults:**
-
-Defaults defined in the DSL (e.g., `operand :paths, default: ['.']`) are applied
-automatically during `args_definition.bind(...)` — do not set defaults manually in
-`call`.
-
-### `Base#with_stdin` Mechanics
-
-`Base#with_stdin(content)` opens an `IO.pipe`, spawns a background `Thread` that
-writes `content` to the write end (then closes it), and yields the read end as
-`in:` to the execution context. The threaded write prevents deadlocks when
-`content` exceeds the OS pipe buffer — the subprocess can drain the pipe
-concurrently. The thread also rescues `Errno::EPIPE` / `IOError` so it exits
-cleanly if the subprocess closes stdin early.
-
-Use `with_stdin` instead of manual pipe management. `StringIO` cannot be used
-because `Process.spawn` requires a real file descriptor.
-
-Example — batch stdin protocol (as used by `git cat-file --batch`):
-
-```ruby
-def call(*, **)
-  bound = args_definition.bind(*, **)
-  with_stdin(Array(bound.objects).map { |object| "#{object}\n" }.join) do |stdin_r|
-    run_batch(bound, stdin_r)
-  end
-end
-```
-
-### Git Version Gating
-
-Version gating is **command-level only** — individual options do not carry version
-annotations.
-
-| Scenario | Expected declaration |
-| --- | --- |
-| Command exists in `Git::MINIMUM_GIT_VERSION` | No `requires_git_version` — do not add one |
-| Command was introduced after `Git::MINIMUM_GIT_VERSION` | `requires_git_version '<version>'` at the version the command was introduced |
-
-Example:
-
-```ruby
-# Git::MINIMUM_GIT_VERSION is 2.28.0 and `git maintenance` was introduced in git 2.29.0:
-requires_git_version '2.29.0'
-```
-
-### Internal Compatibility Contract
-
-This is the canonical location for the internal compatibility contract. Other
-skills reference this section rather than duplicating it.
-
-Ensure refactors preserve these contract expectations:
-
-- constructor shape remains `initialize(execution_context)` (inherited from `Base`)
-- command entrypoint remains `call(*, **)` at runtime (via `Base#call`)
-- argument-definition metadata remains available via `args_definition`
-
-If an intentional deviation exists, require migration notes/changelog documentation.
-
-### Phased Rollout Requirements
-
-This is the canonical location for phased rollout requirements. Other skills
-reference this section rather than duplicating the full checklist.
-
-For migration PRs, verify process constraints:
-
-- changes are on a feature branch — **never commit or push directly to `main`**
-- migration slice is scoped (pilot or one family), not all commands at once
-- each slice is independently revertible
-- refactor-only changes are not mixed with unrelated behavior changes
-- quality gates pass for the slice (`bundle exec rspec`, `bundle exec rake test`,
-  `bundle exec rubocop`, `bundle exec rake yard`)
-
-### Common Failures
-
-#### Policy/output-control flag hardcoded as `literal` (neutrality violation)
-
-`literal` entries for output-control, editor-suppression, progress, or verbose
-flags inside a command class violate the neutrality principle. The command class
-must model the git CLI faithfully; the facade sets safe defaults and callers may
-override them.
-
-Symptom: the command class contains one or more of:
-
-```ruby
-# ❌ Any of these are neutrality violations
-literal '--no-edit'
-literal '--verbose'
-literal '--no-progress'
-literal '--no-color'
-literal '--porcelain'
-```
-
-Fix: convert each to a DSL option and pass the policy value from the facade:
-
-```ruby
-# ✅ In the command class — neutral DSL declaration
-flag_option :edit, negatable: true
-flag_option :progress, negatable: true
-flag_option :verbose
-value_option :format
-
-# ✅ In Git::Lib — facade passes the policy value explicitly
-Git::Commands::Pull.new(self).call(edit: false, progress: false)
-Git::Commands::Mv.new(self).call(*args, verbose: true)
-Git::Commands::Fsck.new(self).call(progress: false)
-```
-
-See "Command-layer neutrality" in CONTRIBUTING.md for the full policy.
-
-#### Other common failures
-
-- lingering `ARGS = Arguments.define` constant and custom `#call`
-- command-specific duplicated exit-status checks instead of `allow_exit_status`
-- missing rationale comment for `allow_exit_status`
-- missing YARD directive (`# @!method call(*, **)`)
-- `call` override that reimplements `Base#call` logic instead of delegating to `validate_exit_status!`
-- using a manual `IO.pipe` inline instead of `Base#with_stdin` for stdin-feeding commands
-- migration PR scope too broad (not phased)
-
-## Workflow
-
-1. **Check class shape** — verify structural requirements:
-
-   - [ ] Class inherits from `Git::Commands::Base`
-   - [ ] Requires `git/commands/base` (not `git/commands/arguments`)
-   - [ ] Has exactly one `arguments do` declaration
-   - [ ] Does not define command-specific `initialize` that only assigns
-         `@execution_context`
-
-2. **Check `#call` implementation** — verify against the
-   [`#call` Override Guidance](#call-override-guidance):
-
-   **Simple commands** (no pre-call logic needed):
-   - [ ] Uses `# @!method call(*, **)` YARD directive with nested `@overload` blocks as documentation shim
-   - [ ] Contains no custom bind/execute/exit-status logic
-   - [ ] Does not parse output in command class
-
-   **Commands with legitimate `call` overrides** (input validation, stdin protocol,
-   non-trivial option routing):
-   - [ ] YARD docs are placed **directly above** `def call` (no `@!method` directive)
-   - [ ] Override calls `args_definition.bind(...)` directly — does *not* duplicate `Base#call` logic
-   - [ ] Exit-status validation delegates to `validate_exit_status!` (not reimplemented inline)
-   - [ ] Stdin-feeding commands use `Base#with_stdin` (not a manual `IO.pipe` inline)
-   - [ ] Any `ArgumentError` raised manually or via DSL constraint covers only what
-         git cannot validate: per-argument failures and constraints on `skip_cli: true`
-         arguments. Cross-argument constraint methods are **not** declared for
-         git-visible arguments — the narrow exception is arguments git cannot observe
-         in its argv (e.g., `skip_cli: true` operands: `conflicts :objects,
-         :batch_all_objects` and `requires_one_of :objects, :batch_all_objects`).
-         See the validation delegation policy in
-         `redesign/3_architecture_implementation.md` Insight 6.
-   - [ ] Bulk of override is extracted into a private helper (`run_batch`, etc.) to satisfy Rubocop `Metrics` thresholds
-   - [ ] Does not parse output in command class
-
-3. **Check exit-status configuration** — verify `allow_exit_status` usage:
-
-   - [ ] Commands with non-zero successful exits declare `allow_exit_status <range>`
-   - [ ] Declaration includes a short rationale comment explaining git semantics
-   - [ ] Range values match expected command behavior
-
-4. **Check git version gating** — verify `requires_git_version` against the
-   [Git Version Gating](#git-version-gating) reference:
-
-   - [ ] Declaration uses a `'major.minor.patch'` string (e.g., `'2.29.0'`), not a
-         `Gem::Version` or `Range` — pre-release versions are not supported
-   - [ ] Version matches the git release that introduced the command — check the
-         command's man page history to determine when it was introduced
-   - [ ] Declaration is not present on commands that exist in `Git::MINIMUM_GIT_VERSION`
-
-5. **Check arguments DSL quality** — run the
-   [Review Arguments DSL](../review-arguments-dsl/SKILL.md) skill against the
-   command's `arguments do` block. That skill covers DSL method selection,
-   alias/modifier correctness, ordering, completeness, and class-level
-   declarations. Additionally verify:
-
-   - [ ] `execution_option` is **not** used for kwargs whose value must be unconditionally
-         fixed regardless of caller input. If a kwarg always has a specific required value
-         (e.g. `chomp: false` for commands returning raw content where trailing newlines are
-         data), hardcode it in a `def call` override instead — exposing it via
-         `execution_option` would allow callers to override a value that must never change.
-
-6. **Check internal compatibility contract** — verify the three contract
-   expectations in [Internal Compatibility Contract](#internal-compatibility-contract):
-
-   - [ ] constructor shape remains `initialize(execution_context)` (inherited from `Base`)
-   - [ ] command entrypoint remains `call(*, **)` at runtime (via `Base#call`)
-   - [ ] argument-definition metadata remains available via `args_definition`
-
-   If an intentional deviation exists, require migration notes/changelog documentation.
-
-7. **Check phased rollout / rollback requirements** — for migration PRs, verify
-   against the [Phased Rollout Requirements](#phased-rollout-requirements):
-
-   - [ ] changes are on a feature branch — **never commit or push directly to `main`**
-   - [ ] migration slice is scoped (pilot or one family), not all commands at once
-   - [ ] each slice is independently revertible
-   - [ ] refactor-only changes are not mixed with unrelated behavior changes
-   - [ ] quality gates pass for the slice (`bundle exec rspec`, `bundle exec rake test`,
-         `bundle exec rubocop`, `bundle exec rake yard`)
-
-8. **Collect issues** — record all findings for the [Output](#output).
-
-## Output
-
-For each file, produce:
-
-| Check | Status | Issue |
-| --- | --- | --- |
-| Base inheritance | Pass/Fail | ... |
-| arguments DSL | Pass/Fail | ... |
-| call shim | Pass/Fail | ... |
-| allow_exit_status usage | Pass/Fail | ... |
-| requires_git_version | Pass/Fail | ... |
-| output parsing absent | Pass/Fail | ... |
-| compatibility contract | Pass/Fail | ... |
-
-Then list required fixes and indicate whether the migration slice is safe to merge
-under phased-rollout rules.
diff --git a/.github/skills/review-command-tests/SKILL.md b/.github/skills/review-command-tests/SKILL.md
@@ -31,7 +31,7 @@ Conventions for writing and reviewing unit and integration tests for
   coverage; this skill adds command-specific conventions on top
 - [Review Arguments DSL](../review-arguments-dsl/SKILL.md) — verifying DSL entries
   match git CLI
-- [Review Command Implementation](../review-command-implementation/SKILL.md) — class
+- [Command Implementation](../command-implementation/SKILL.md) — class
   structure, phased rollout gates, and internal compatibility contracts
 - [Command YARD Documentation](../command-yard-documentation/SKILL.md)
   — documentation completeness for command classes
diff --git a/.github/skills/review-cross-command-consistency/SKILL.md b/.github/skills/review-cross-command-consistency/SKILL.md
@@ -50,7 +50,7 @@ Before starting, you **MUST** load the following skill(s) in their entirety:
 
 ## Related skills
 
-- [Review Command Implementation](../review-command-implementation/SKILL.md) — canonical class-shape checklist, phased
+- [Command Implementation](../command-implementation/REFERENCE.md#phased-rollout-requirements) — canonical class-shape checklist, phased
   rollout gates, and internal compatibility contracts
 - [Review Arguments DSL](../review-arguments-dsl/SKILL.md) — verifying DSL entries match git CLI
 - [Command Test Conventions](../command-test-conventions/SKILL.md) — unit/integration test conventions for command classes
@@ -119,7 +119,7 @@ only as a supplemental check.
 
 ### 7. Migration process consistency
 
-See **Review Command Implementation § Phased rollout / rollback requirements** for
+See **[Command Implementation § Phased rollout requirements](../command-implementation/REFERENCE.md#phased-rollout-requirements)** for
 the canonical checklist. During a cross-command audit, verify that sibling commands
 were migrated in the same slice and that the same quality gates were applied.
 
diff --git a/.github/skills/reviewing-skills/SKILL.md b/.github/skills/reviewing-skills/SKILL.md
@@ -33,7 +33,7 @@ Attach this file to your Copilot Chat context, then invoke it with the skill
 folder or SKILL.md file(s) to review. Examples:
 
 ```text
-Using the Reviewing Skills skill, review .github/skills/scaffold-new-command/.
+Using the Reviewing Skills skill, review .github/skills/command-implementation/.
 ```
 
 ```text
PATCH

echo "Gold patch applied."
