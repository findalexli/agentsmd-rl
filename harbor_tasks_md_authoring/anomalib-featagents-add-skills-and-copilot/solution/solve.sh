#!/usr/bin/env bash
set -euo pipefail

cd /workspace/anomalib

# Idempotency guard
if grep -qF "description: Run or continue model benchmarks, collect measured results, and ref" ".agents/skills/benchmark-and-docs-refresh/SKILL.md" && grep -qF "- Review the nearest documentation surface, not just the edited Python file: `RE" ".agents/skills/docs-changelog/SKILL.md" && grep -qF "- If the docs page is a lightweight API/reference page, still ensure it does not" ".agents/skills/model-doc-sync/SKILL.md" && grep -qF "description: Export, validate, and publish model sample-result images into docs/" ".agents/skills/model-sample-image-export/SKILL.md" && grep -qF "- Training side effects such as checkpointing, timing, compression, or visualiza" ".agents/skills/models-data/SKILL.md" && grep -qF "- Security-sensitive changes should be reviewed with the repo's CI security tool" ".agents/skills/pr-workflow/SKILL.md" && grep -qF "- Document constructor arguments in the class docstring rather than in a separat" ".agents/skills/python-docstrings/SKILL.md" && grep -qF "- Prefer repository-established typing patterns such as `X | None`, `type[...]`," ".agents/skills/python-style/SKILL.md" && grep -qF "- For tensor-heavy logic, ensure tests assert the properties that matter: shapes" ".agents/skills/testing/SKILL.md" && grep -qF "- Do not add third-party-derived code unless its license allows redistribution a" ".agents/skills/third-party-code/SKILL.md" && grep -qF ".cursor/rules/python_docstrings.mdc" ".cursor/rules/python_docstrings.mdc" && grep -qF "- Treat `src/anomalib/`, `application/`, `tests/`, `docs/`, `.github/`, and rele" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/benchmark-and-docs-refresh/SKILL.md b/.agents/skills/benchmark-and-docs-refresh/SKILL.md
@@ -0,0 +1,102 @@
+---
+name: benchmark-and-docs-refresh
+description: Run or continue model benchmarks, collect measured results, and refresh README/docs benchmark sections from generated artifacts. Use when benchmark tables in model docs need to be created, updated, or corrected.
+---
+
+# Benchmark and Docs Refresh
+
+Use this skill to update benchmark sections in model documentation from real benchmark outputs.
+
+## Scope
+
+This skill focuses on:
+
+- running or continuing benchmarks
+- collecting benchmark CSV results from `results/`
+- updating benchmark tables in model READMEs
+- updating matching docs pages when benchmark status changes
+
+It does not own sample image export. Use `model-sample-image-export` for that.
+
+## Request changes when
+
+- incomplete benchmark coverage is presented;
+- README or docs benchmark status drifts from the actual run state.
+
+## Preferred Benchmark Workflow
+
+Always prefer:
+
+- `tools/experimental/benchmarking/benchmark.py`
+
+with an appropriate config file.
+
+If the stock benchmark path is insufficient for a specific model:
+
+1. derive a small helper script from the benchmark workflow
+2. keep it model-specific unless multiple models clearly need the same pattern
+3. save measurable outputs such as CSV files under `results/`
+
+## Required Evidence
+
+Only publish benchmark values when they come from actual artifacts, for example:
+
+- `results/<model>_benchmark.csv`
+- benchmark-generated CSV files under `runs/` or `results/`
+- model-specific run outputs that clearly record the measured metrics
+
+Never infer missing values.
+
+## Update Rules
+
+When refreshing benchmark tables:
+
+1. Read the target README and matching docs page first.
+2. Read the benchmark artifact source.
+3. Fill only the shot-settings and metrics that actually exist.
+4. Leave unavailable rows blank or TODO.
+5. Update status wording if the benchmark is still partial or still running.
+
+## Table Conventions
+
+Common sections to refresh:
+
+- `### Image-Level AUC`
+- `### Pixel-Level AUC`
+- `### Image F1 Score`
+- `### Pixel F1 Score`
+
+If a README only contains placeholders, replace only the rows supported by measured results.
+
+## Docs Synchronization Rules
+
+If the README benchmark state changes, update the matching docs page under:
+
+- `docs/source/markdown/guides/reference/models/image/<model>.md`
+- `docs/source/markdown/guides/reference/models/video/<model>.md`
+
+The docs page may stay shorter than the README, but it must not contradict it.
+
+## Quality Checks
+
+Before finishing:
+
+1. Confirm the benchmark artifact still exists.
+2. Confirm copied values exactly match the artifact.
+3. Confirm averages are computed from measured values only.
+4. Confirm incomplete rows remain clearly incomplete.
+5. Confirm README/docs wording matches reality.
+
+## Reviewer checklist
+
+- Check that the artifact exists.
+- Check that every copied value matches.
+- Check that partial runs are labeled clearly.
+- Check README and docs wording for consistency.
+
+## Repo-Specific Notes
+
+- Some benchmark jobs in this repo may require derived helper scripts.
+- Some long runs are better continued in tmux/background sessions.
+- A benchmark can be complete enough to fill a subset of rows without justifying all rows.
+- Never replace TODOs with fabricated numbers.
diff --git a/.agents/skills/docs-changelog/SKILL.md b/.agents/skills/docs-changelog/SKILL.md
@@ -0,0 +1,59 @@
+---
+name: docs-changelog
+description: Reviews anomalib docstrings, documentation updates, and changelog expectations
+---
+
+# Anomalib Documentation and Changelog Review
+
+Use this skill when reviewing docstrings, user docs, examples, READMEs, and release-note impact.
+
+## Purpose and scope
+
+Use this skill when code changes may affect user-visible documentation, examples, READMEs, or release notes.
+
+## Request changes when
+
+- user-facing behavior changes without matching docs updates;
+- public APIs change without docstring or reference-doc updates;
+- a significant user-facing change is missing a `CHANGELOG.md` entry under `## [Unreleased]`;
+- examples or README usage snippets no longer match the actual API.
+
+## Docstrings
+
+- Public Python APIs should use Google-style docstrings.
+- Use the existing `python-docstrings` skill for docstring formatting details.
+- Ask for docstrings when behavior is non-trivial, user-facing, or part of a reusable API surface.
+- For tensors, arrays, batches, or structured outputs, ask reviewers to document shapes or field expectations when they matter for correct usage.
+
+## Documentation updates
+
+- If a PR changes APIs, CLI behavior, model behavior, config structure, workflows, or outputs, ask for related documentation updates.
+- Review the nearest documentation surface, not just the edited Python file: `README.md`, docs under `docs/source/markdown/`, model-specific `README.md`, examples, or reference pages.
+- Prefer small, precise doc updates over broad rewrites.
+
+## Changelog
+
+- Significant user-facing changes should update `CHANGELOG.md` under `## [Unreleased]`.
+- Use the existing Keep a Changelog section headings already present in the repo: `Added`, `Removed`, `Changed`, `Deprecated`, `Fixed`.
+- Purely internal changes may not need a changelog entry, but reviewers should call out missing entries for behavior, API, docs, or user workflow changes.
+
+## Repo-grounded review anchors
+
+- `CONTRIBUTING.md`
+- `docs/source/markdown/guides/developer/contributing.md`
+- `.agents/skills/python-docstrings/SKILL.md`
+- `CHANGELOG.md`
+
+## Review prompts
+
+- Does the code change require docstring, README, docs page, or example updates?
+- Are docstrings informative enough for users to understand behavior and expected inputs?
+- Should this change be recorded under `## [Unreleased]`?
+- If a public symbol or module changed, is the reference documentation still accurate?
+
+## Reviewer checklist
+
+- Check docstrings for public APIs.
+- Check README, docs, and examples for user-facing changes.
+- Check `CHANGELOG.md` for significant changes.
+- Check that docs match the current API and workflow.
diff --git a/.agents/skills/model-doc-sync/SKILL.md b/.agents/skills/model-doc-sync/SKILL.md
@@ -0,0 +1,142 @@
+---
+name: model-doc-sync
+description: Keep anomalib model READMEs, docs pages, image assets, and benchmark/result references in sync
+---
+
+# Model README and Docs Sync
+
+Use this skill when updating model documentation, benchmark tables, sample-result images, or docs reference pages for
+an anomalib model.
+
+## Purpose and scope
+
+Use this skill to keep model READMEs, docs pages, images, and benchmark/sample references aligned.
+
+## Request changes when
+
+- a model README changes but the matching docs page is left stale;
+- image references point to missing assets;
+- benchmark tables do not match committed artifacts;
+- sample-result sections imply coverage that the repo does not actually contain.
+
+## Keep these surfaces aligned
+
+- `src/anomalib/models/**/README.md`
+- `docs/source/markdown/guides/reference/models/**`
+- `docs/source/images/**`
+- benchmark and run artifacts under `results/`
+
+## Canonical repo paths
+
+### Model READMEs
+
+- Image model READMEs usually live at `src/anomalib/models/image/<model>/README.md`.
+- Video model READMEs may live at `src/anomalib/models/video/<model>/README.md`.
+- There are also category-level READMEs such as `src/anomalib/models/image/README.md` and `src/anomalib/models/video/README.md`.
+
+### Model docs pages
+
+- Image model docs pages usually live at `docs/source/markdown/guides/reference/models/image/<model>.md`.
+- Video model docs pages usually live at `docs/source/markdown/guides/reference/models/video/<model>.md`.
+- Keep `docs/source/markdown/guides/reference/models/**/index.md` up-to-date.
+- The docs pages should also contain architecture image and description.
+
+### Image assets
+
+- Model images typically live at `docs/source/images/<model>/`.
+- Common patterns include `architecture.*` and `results/0.png`, `results/1.png`, `results/2.png`.
+- Some models use nonstandard names or multiple architecture images, for example `docs/source/images/cs_flow/`.
+
+### Result artifacts
+
+- Measured artifacts may exist under `results/<ModelName>/...`.
+- Treat `results/` as evidence for benchmark/sample claims, not as a place to invent values from partial runs.
+
+## Required workflow
+
+### 1. Inspect before editing
+
+For the target model:
+
+1. Read the model README.
+2. Read the matching docs page if it exists.
+3. Inspect `docs/source/images/<model>/` or the repo-specific variant actually used.
+4. Check whether measured artifacts already exist in `results/`.
+5. Check whether referenced sample-result images exist and are still valid.
+
+Never update only one of README or docs when both exist.
+
+### 2. Keep these sections synchronized
+
+If present in the README, verify that the docs page and assets do not contradict it:
+
+- title and model name
+- description
+- architecture section and image references
+- usage section
+- benchmark section
+- sample results section
+- TODO notes about missing benchmarks or images
+
+Docs pages do not need to duplicate the full README, but they must stay consistent with it.
+
+### 3. Benchmark update rules
+
+- Prefer the repository's existing benchmarking workflow, starting with `tools/experimental/benchmarking/`.
+- Use measured results only.
+- Source values from committed artifacts such as files under `results/`.
+- Do not fabricate averages, rows, or per-category scores.
+- If only part of the benchmark is complete, fill only the supported values and leave the rest clearly blank or TODO.
+- If benchmarking is still in progress, say so explicitly.
+
+### 4. Sample image rules
+
+- Only add sample-result images from completed model outputs.
+- Confirm the referenced output is not degenerate or misleading.
+- Do not publish obviously broken masks, empty masks, NaN-driven outputs, or placeholder images as final examples.
+- Copy or export valid final images into the matching `docs/source/images/...` location.
+- If fewer than three valid sample images exist, use a precise TODO note instead of broken links or bad examples.
+
+## README conventions
+
+- Prefer repository-consistent image references such as `/docs/source/images/<model>/...` when the README already uses that pattern.
+- If sample-result images are missing, leave a TODO note instead of a broken link.
+- Keep benchmark/sample wording consistent with the actual artifacts checked into the repo.
+
+## Docs page conventions
+
+- Use the real docs-page path depth when referencing images.
+- Many model docs pages act as reference wrappers around module docs, so keep them aligned with the README without forcing full duplication.
+- If the docs page is a lightweight API/reference page, still ensure it does not contradict README claims about architecture, benchmarks, or results.
+
+## Validation checklist
+
+Before finishing:
+
+1. README and docs page agree on benchmark and sample status.
+2. Every referenced image path exists.
+3. Benchmark tables match committed artifacts.
+4. Any TODO left behind is accurate and specific.
+5. Any helper script remains narrow and model-specific unless a general solution is clearly justified.
+
+## Known repo pitfalls
+
+- Some model/image paths do not match exactly, for example `csflow` vs `cs_flow`.
+- Some models have architecture images but not three sample-result images.
+- Some models have results artifacts under `results/` without a fully synced docs surface yet.
+- Docs pages can drift from README changes even when image paths still resolve.
+
+## Review prompts
+
+- Did the README, docs page, and image assets all get checked together?
+- Do benchmark values come from committed measured artifacts?
+- Are sample-result images valid and non-misleading?
+- Are any missing assets called out explicitly instead of hidden behind broken links?
+- Is there any model-specific naming quirk that needs a manual path check?
+
+## Reviewer checklist
+
+- Check README and docs page together.
+- Check every referenced image path.
+- Check benchmark claims against committed artifacts.
+- Check TODO notes for accuracy.
diff --git a/.agents/skills/model-sample-image-export/SKILL.md b/.agents/skills/model-sample-image-export/SKILL.md
@@ -0,0 +1,109 @@
+---
+name: model-sample-image-export
+description: Export, validate, and publish model sample-result images into docs/source/images and reference them from README/docs pages. Use when model sample images are missing, outdated, or suspected to be invalid.
+---
+
+# Model Sample Image Export
+
+Use this skill to create or refresh sample-result images for model documentation.
+
+## Scope
+
+This skill focuses on:
+
+- selecting completed trained checkpoints or finished benchmark runs
+- exporting prediction/sample images
+- copying or saving them into `docs/source/images/<model>/results/`
+- updating README/docs sample-result references
+- rejecting broken or misleading outputs
+
+It does not own benchmark table maintenance. Use `benchmark-and-docs-refresh` for that.
+
+## Request changes when
+
+- sample images come from incomplete or untrusted runs;
+- published outputs are clearly degenerate or misleading;
+- README or docs references point to missing image files;
+- the docs surface implies three valid examples when fewer trustworthy outputs exist.
+
+## Required Source Quality
+
+Only use sample images from:
+
+- completed trained checkpoints
+- completed benchmark runs with valid prediction outputs
+- finished model outputs that can be traced back to a real run artifact
+- if no suitable completed checkpoint, benchmark output, or other traceable run artifact exists, schedule a few runs to generate trustworthy sample images
+
+Do not use:
+
+- incomplete runs
+- partially written checkpoints
+- outputs with empty/degenerate masks
+- outputs driven by NaNs or obviously broken predictions
+
+## Required Workflow
+
+1. Identify candidate checkpoints/runs in `results/`.
+2. Verify the run is complete enough to trust.
+3. If verification fails, schedule a few runs to train the model on a few categories.
+4. Generate predictions from the checkpoint/run.
+5. Inspect output quality before publishing images.
+6. Save the selected images into `docs/source/images/<model>/results/`.
+7. Update README/docs references.
+
+## Preferred Output Layout
+
+- `docs/source/images/<model>/results/0.png`
+- `docs/source/images/<model>/results/1.png`
+- `docs/source/images/<model>/results/2.png`
+
+If you have fewer than 3 trustworthy images, train the model on a few more categories to generate more sample images.
+
+## README Update Pattern
+
+Preferred pattern:
+
+```md
+### Sample Results
+
+![Sample Result 1](/docs/source/images/<model>/results/0.png "Sample Result 1")
+```
+
+Repeat for additional images.
+
+## Docs Update Pattern
+
+Preferred docs-page pattern:
+
+````md
+    ## Sample Results
+
+    ```{eval-rst}
+    .. image:: ../../../../../images/<model>/results/0.png
+    ```
+````
+
+## Validation Rules
+
+Before publishing an image:
+
+1. Check that the referenced file exists.
+2. Check that the image is visually plausible.
+3. Check that the mask/anomaly region is not obviously wrong.
+4. Check that the sample came from a trained or otherwise valid completed run.
+5. If a model/category output is degenerate, exclude it and say so explicitly.
+
+## Reviewer checklist
+
+- Check run completeness.
+- Check image quality.
+- Check exported file existence.
+- Check README and docs references.
+
+## Repo-Specific Notes
+
+- In this repo, some completed checkpoints can still produce bad masks.
+- If generic visualization helpers fail, derive a narrow exporter for the specific model/run.
+- Keep exporter scripts focused and traceable to the chosen checkpoints.
+- When in doubt, prefer fewer trustworthy sample images over a full set of misleading ones.
diff --git a/.agents/skills/models-data/SKILL.md b/.agents/skills/models-data/SKILL.md
@@ -0,0 +1,76 @@
+---
+name: models-data
+description: Reviews anomalib model, data, callback, metric, and CLI integration conventions
+---
+
+# Anomalib Models and Data Review
+
+Use this skill when reviewing changes under models, data, callbacks, metrics, pipelines, deployment, or CLI integration.
+
+## Purpose and scope
+
+Use this skill for architectural fit. It is most useful when a change affects how anomalib models are built,
+configured, loaded, or connected to data, callbacks, metrics, or CLI/config entrypoints.
+
+## Request changes when
+
+- a model does not fit the established `AnomalibModule`-based architecture;
+- structured data is replaced with ad hoc dictionaries where anomalib already has typed item/batch dataclasses;
+- callback or engine behavior bypasses existing Lightning or anomalib extension points;
+- public metrics, models, or CLI components are added without matching exports, docs, or config compatibility;
+- user-facing constructor/config surfaces become opaque or harder to serialize.
+
+## Models
+
+- New trainable models should fit the existing `AnomalibModule`-based architecture.
+- Review whether the model integrates cleanly with existing model discovery and loading patterns in `src/anomalib/models/__init__.py`.
+- Prefer Lightning hooks and existing framework extension points over ad hoc training side effects inside model bodies.
+- Check that configurable constructor arguments are explicit and compatible with the repo's `jsonargparse`-driven config flow.
+
+## Data and dataclasses
+
+- Data should move through anomalib's typed dataclass system rather than ad hoc dictionaries where the library already has structured item/batch types.
+- Changes to shared dataclasses should preserve validation and batching behavior.
+- `src/anomalib/data/dataclasses/generic.py` is the main reference for `FieldDescriptor`, typed fields, update behavior, and batch/item patterns.
+- If a dataclass surface changes, review both runtime behavior and the corresponding public documentation.
+
+## Callbacks and engine integration
+
+- Training side effects such as checkpointing, timing, compression, or visualization should follow the callback-based patterns already present in `src/anomalib/callbacks/`.
+- New callback-style behavior should align with Lightning callback usage instead of bypassing the engine lifecycle.
+- Do not approve model/callback changes that tightly couple to trainer internals when a documented hook already exists.
+
+## Metrics
+
+- Metrics should align with the torchmetrics-based patterns in `src/anomalib/metrics/base.py`.
+- Review whether image-level and pixel-level metric handling remains clear and consistent.
+- If a metric becomes part of the public API, verify that exports and docs are updated too.
+
+## CLI and config compatibility
+
+- Review whether user-configurable types remain compatible with `jsonargparse` and the existing CLI/config structure.
+- Prefer explicit constructor parameters over opaque config plumbing when the component is user-facing.
+- If a new public component is configurable, ask whether config-driven usage and import paths are documented and tested.
+
+## Repo-grounded review anchors
+
+- `src/anomalib/models/__init__.py`
+- `src/anomalib/data/dataclasses/generic.py`
+- `src/anomalib/callbacks/__init__.py`
+- `src/anomalib/metrics/base.py`
+- `src/anomalib/cli/cli.py`
+
+## Review prompts
+
+- Does the change fit anomalib's module, data, and callback architecture?
+- Is structured data still flowing through the established dataclass/batch system?
+- Will this remain usable from config files and CLI entrypoints?
+- Are public exports, docs, and integration points updated alongside the code?
+
+## Reviewer checklist
+
+- Check model architecture fit.
+- Check typed data flow.
+- Check callback and metric integration.
+- Check CLI/config compatibility.
+- Check exports and docs for new public surfaces.
diff --git a/.agents/skills/pr-workflow/SKILL.md b/.agents/skills/pr-workflow/SKILL.md
@@ -0,0 +1,59 @@
+---
+name: pr-workflow
+description: Reviews anomalib contributor workflow, PR title, branch naming, and quality gate expectations
+---
+
+# Anomalib PR Workflow Review
+
+Use this skill when reviewing whether a change is ready for contribution and merge.
+
+## Purpose and scope
+
+Use this skill for merge readiness, contributor workflow, CI expectations, PR title checks, and branch naming.
+
+## Request changes when
+
+- the PR title does not follow the repository's Conventional Commit style;
+- branch naming does not match `<type>/<scope>/<description>`;
+- required quality gates, docs, tests, or changelog updates are missing;
+- workflow or security-sensitive changes are not reviewed to the repo's standards.
+
+## Quality gates
+
+- Contributors are expected to run `prek run --all-files` and `pytest tests/` before finalizing a PR.
+- Review feedback should align with the project's configured checks in `pyproject.toml` and `.pre-commit-config.yaml`.
+- Security-sensitive changes should be reviewed with the repo's CI security tooling in mind: Bandit, CodeQL, Semgrep, Zizmor, Trivy, and Dependabot.
+
+## PR titles and branch names
+
+- PR titles should follow Conventional Commits as described in `CONTRIBUTING.md`.
+- Branch names should follow `<type>/<scope>/<description>`.
+- Allowed types and scopes should match the repository's Commitizen configuration in `pyproject.toml`.
+
+## Reviewer expectations
+
+- Ask for precise, actionable fixes grounded in repo policy rather than generic preferences.
+- Escalate missing tests, missing docs, missing changelog entries, or workflow/security risks before approval.
+- Be stricter when a PR changes CLI entrypoints, workflows, deployment, inferencers, or user-facing public APIs.
+
+## Repo-grounded review anchors
+
+- `CONTRIBUTING.md`
+- `docs/source/markdown/guides/developer/contributing.md`
+- `docs/source/markdown/guides/developer/code_review_checklist.md`
+- `.pre-commit-config.yaml`
+- `pyproject.toml`
+- `SECURITY.md`
+
+## Review prompts
+
+- Is the PR title valid for the eventual squash commit?
+- Are branch naming, changelog, tests, and docs in good shape for merge?
+- Do the requested changes line up with the project's existing CI and security gates?
+
+## Reviewer checklist
+
+- Check PR title.
+- Check branch naming.
+- Check CI, test, doc, and changelog readiness.
+- Check workflow and security-sensitive files more strictly.
diff --git a/.agents/skills/python-docstrings/SKILL.md b/.agents/skills/python-docstrings/SKILL.md
@@ -0,0 +1,92 @@
+---
+name: python-docstrings
+description: Enforces Google-style Python docstrings for Python code
+---
+
+# Python Docstring Rules
+
+Use this skill when reviewing or writing Python docstrings.
+
+## Purpose and scope
+
+- Use Google-style docstrings.
+- Focus on public Python modules, classes, functions, and methods.
+- Keep docstrings compact, specific, and easy to scan.
+
+## Request changes when
+
+- a public API has no docstring;
+- the summary line is vague or inaccurate;
+- arguments, returns, or intentionally raised exceptions are undocumented;
+- a non-trivial public API needs an example but does not have one.
+
+## Required structure
+
+1. Short description
+2. Optional longer explanation
+3. `Args`
+4. `Returns`
+5. Optional `Raises`
+6. Optional `Example`
+
+## Formatting rules
+
+- Limit docstrings to 120 characters per line.
+- In `Args`, use `name (type): description`.
+- In `Returns`, describe both the type and meaning of the returned value.
+- Add `Raises` when the function intentionally raises exceptions.
+- Use doctest-style `Example` blocks with `>>>` when examples help clarify usage.
+
+## Reviewer checklist
+
+- Is the docstring present on the public API?
+- Is the summary line accurate?
+- Are inputs, outputs, and exceptions documented?
+- Would a user understand how to call this API from the docstring alone?
+
+## Example
+
+```python
+def my_function(param1: int, param2: str = "default") -> bool:
+    """Short description.
+
+    A longer explanation.
+
+    Args:
+        param1 (int): Explanation of param1.
+        param2 (str): Explanation of param2. Defaults to "default".
+
+    Returns:
+        bool: Explanation of the return value.
+
+    Example:
+        >>> my_function(1, "test")
+        True
+    """
+    return True
+```
+
+## Docstring for `__init__` method
+
+- Document constructor arguments in the class docstring rather than in a separate `__init__` docstring.
+
+```python
+class MyClass:
+    """My class description.
+
+    A longer explanation.
+
+    Args:
+        param1 (int): Description of param1.
+        param2 (str): Description of param2.
+
+    Example:
+        >>> my_class = MyClass(param1=1, param2="test")
+        >>> my_class.param1
+        1
+        >>> my_class.param2
+        'test'
+    """
+    def __init__(self, param1: int, param2: str) -> None:
+        ...
+```
diff --git a/.agents/skills/python-style/SKILL.md b/.agents/skills/python-style/SKILL.md
@@ -0,0 +1,68 @@
+---
+name: python-style
+description: Reviews anomalib Python style, typing, imports, and public API conventions
+---
+
+# Anomalib Python Style Review
+
+Use this skill when reviewing Python code in `src/anomalib/` or `tests/`.
+
+## Purpose and scope
+
+This skill covers Python style, typing, imports, exports, copyright headers, and basic code hygiene.
+
+## Core rules
+
+- Target the repository's Python baseline.
+- Follow the Ruff-configured line length of 120 characters.
+- Match nearby anomalib code before suggesting stylistic rewrites.
+- Prefer explicit, readable code over clever shortcuts.
+
+## Request changes when
+
+- public APIs are missing type annotations;
+- new code introduces weak typing such as unnecessary `Any` or untyped public `**kwargs`;
+- imports or exports drift from nearby package patterns;
+- a touched Python file is missing the expected copyright/SPDX header;
+- error handling becomes less explicit or debug code is left behind.
+
+## Typing
+
+- Public functions, methods, and constructors should have explicit type annotations.
+- Prefer repository-established typing patterns such as `X | None`, `type[...]`, `Sequence[...]`, `TypeVar`, and `Generic` where they fit.
+- Do not weaken types without a strong reason.
+- Flag vague escape hatches such as unnecessary `Any`, broad untyped `**kwargs`, or type suppressions that hide real issues.
+
+## Imports and exports
+
+- Keep imports grouped as standard library, third-party, then local imports.
+- Prefer absolute imports inside `anomalib`.
+- When a public symbol is added to an `__init__.py`, verify that `__all__` stays accurate.
+
+## Copyright and license header
+
+- Python source files should include the standard Intel copyright and SPDX header used across the repository.
+- For a **new** file, use the current year only, for example:
+  - `# Copyright (C) 2026 Intel Corporation`
+  - `# SPDX-License-Identifier: Apache-2.0`
+- For an **existing** file updated in 2026, ensure the year or year range includes 2026.
+  - Example: update `2024` to `2024-2026`.
+  - Example: keep `2026` for a single-year file created in 2026.
+
+## Error handling and code hygiene
+
+- Catch specific exceptions instead of broad or silent failure patterns.
+- Ask for explicit exceptions and informative error messages.
+- Flag debug prints, dead code, commented-out code, and magic values that should be named constants or config.
+- Prefer explicit validation with raised exceptions over fragile assumptions.
+
+## Repo-grounded review anchors
+
+- `pyproject.toml` defines Ruff, pydocstyle, mypy, pytest, and Commitizen expectations.
+
+## Reviewer checklist
+
+- Check typing on public APIs.
+- Check imports and exports.
+- Check the copyright/SPDX header on touched Python files.
+- Check for obvious code hygiene regressions.
diff --git a/.agents/skills/testing/SKILL.md b/.agents/skills/testing/SKILL.md
@@ -0,0 +1,56 @@
+---
+name: testing
+description: Review/generate unit, integration, and regression test expectations
+---
+
+# Anomalib Testing Review/Generation
+
+Use this skill when reviewing/generating additions or changes that should be covered by tests.
+
+## Purpose and scope
+
+Use this skill to decide what test coverage is required and whether existing tests still prove the intended behavior.
+
+## Request changes when
+
+- new behavior ships without tests;
+- behavior changes update code but not existing tests;
+- a bug fix has no regression test when one is feasible;
+- tests are flaky, network-dependent, or placed in the wrong area of the suite.
+
+## Test placement and scope
+
+- Tests should live under `tests/` and generally mirror the code area they validate.
+- Prefer the established split between `tests/unit/` and `tests/integration/`.
+- Ask for unit tests for new behavior and for integration coverage when cross-component behavior changes.
+
+## Test style
+
+- Follow pytest conventions already used in the repo.
+- Prefer fixtures and parametrization where they improve clarity and coverage.
+- Keep tests offline and deterministic where practical.
+- For tensor-heavy logic, ensure tests assert the properties that matter: shapes, values, reconstruction behavior, errors, or invariants.
+
+## Regression mindset
+
+- Bug fixes should include a regression test when feasible.
+- Behavior changes should update existing tests, not only add new ones.
+- If the change touches CLI/config/model loading or pipeline orchestration, review whether a higher-level test is also needed.
+
+## Repo-grounded review anchors
+
+- `pyproject.toml` for pytest markers and test path configuration
+
+## Review prompts
+
+- What test proves the new behavior works?
+- What existing behavior could regress because of this change?
+- Is the test placed in the right part of the suite?
+- Does the change need both unit and integration coverage?
+
+## Reviewer checklist
+
+- Check that new behavior has test coverage.
+- Check that changed behavior updates old tests too.
+- Check placement under `tests/unit/` or `tests/integration/`.
+- Check determinism and offline execution.
diff --git a/.agents/skills/third-party-code/SKILL.md b/.agents/skills/third-party-code/SKILL.md
@@ -0,0 +1,60 @@
+---
+name: third-party-code
+description: Review/generate third-party code attribution, licensing, and notice requirements
+---
+
+# Third-Party Code Review
+
+Use this skill when reviewing or generating code that is copied from, adapted from, or substantially based on an
+external project.
+
+## Purpose and scope
+
+Use this skill for licensing, attribution, notices, and repository bookkeeping around third-party-derived code.
+
+## Core rule
+
+- Do not add third-party-derived code unless its license allows redistribution and modification compatible with this repository.
+- Preserve upstream attribution and required notices.
+- Track the imported/adapted component in the repository's third-party inventory.
+
+## Request changes when
+
+- third-party-derived code is added without a matching `third-party-programs.txt` entry;
+- a colocated `LICENSE` file is missing;
+- upstream attribution or license text is removed or weakened;
+- license compatibility has not been verified for copied or adapted code.
+
+## Required actions for new third-party-derived code
+
+- Add or update an entry in `third-party-programs.txt`.
+- Add a colocated `LICENSE` file in the relevant component or subtree.
+- Name the upstream project and author/source in that `LICENSE` file.
+- Include the upstream license text or required notice in that `LICENSE` file.
+- Keep the anomalib-side copyright/SPDX notice pattern when the repository's existing third-party examples do so.
+
+## Required actions for updates to existing third-party-derived code
+
+- Preserve existing attribution, SPDX tags, and license text.
+- Do not remove or weaken upstream notices.
+- Update `third-party-programs.txt` if the tracked component, source, or licensing metadata changes.
+
+## Repo-grounded review anchors
+
+- `third-party-programs.txt`
+- `src/**/LICENSE`
+
+## Review prompts
+
+- Is this code copied or adapted from a third-party source?
+- If yes, is there a matching entry in `third-party-programs.txt`?
+- Is there a colocated `LICENSE` file with upstream attribution and license text?
+- Are required notices preserved in modified files and surrounding documentation?
+- Has anyone verified that the upstream license is compatible with redistribution in this repository?
+
+## Reviewer checklist
+
+- Check whether the code is third-party-derived.
+- Check `third-party-programs.txt`.
+- Check the colocated `LICENSE` file.
+- Check attribution and compatibility.
diff --git a/.cursor/rules/python_docstrings.mdc b/.cursor/rules/python_docstrings.mdc
@@ -1,60 +0,0 @@
----
-description: Standards for Python docstrings using Google style
-globs: **/*.py
----
-
-# Python Docstring Rules
-
-You are an expert Python developer who writes high-quality, Google-style docstrings.
-
-## General Guidelines
-
--   **Style:** Use Google-style docstrings.
--   **Line Length:** Limit docstrings to 120 characters per line.
--   **Structure:**
-    1.  **Short Description:** A concise summary of the function, class, or module.
-    2.  **Longer Explanation:** (Optional) detailed description of the behavior.
-    3.  **Args:** Description of arguments.
-    4.  **Returns:** Description of return values.
-    5.  **Raises:** (Optional) Description of raised exceptions.
-    6.  **Example:** Usage examples using doctest style.
-
-## Formatting Details
-
-### Args Section
-
--   List each argument with its type and a description.
--   Format: `param_name (type): Description. Defaults to value.`
--   If types are long, they can be included in the description or wrapped.
-
-### Returns Section
-
--   Describe the return value and its type.
--   Format: `type: Description.`
-
-### Example Section
-
--   Use `>>>` for code examples (doctest style).
--   Show the expected output on the following lines.
-
-## Example
-
-```python
-def my_function(param1: int, param2: str = "default") -> bool:
-    """Short description.
-
-    A longer explanation.
-
-    Args:
-        param1 (int): Explanation of param1.
-        param2 (str): Explanation of param2. Defaults to "default".
-
-    Returns:
-        bool: Explanation of the return value.
-
-    Example:
-        >>> my_function(1, "test")
-        True
-    """
-    return True
-```
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -0,0 +1,57 @@
+# Anomalib Copilot Instructions
+
+Use these instructions when reviewing code changes in `anomalib`.
+
+## Primary rule
+
+Prefer the repository-local skills under `.agents/skills/` instead of embedding all review policy here.
+
+## Purpose and scope
+
+Use this file for repository-wide review guidance. Use the skill files below for topic-specific rules.
+
+## Review priorities
+
+- Keep reviews aligned with existing anomalib patterns instead of introducing new conventions.
+- Prefer small, targeted feedback over broad refactors unless the PR explicitly aims to refactor.
+- Treat `src/anomalib/`, `application/`, `tests/`, `docs/`, `.github/`, and relevant `.agents/skills/` files as first-class review surfaces.
+- If a change touches `application/`, note that Anomalib Studio has some separate tooling and config from the root project.
+
+## Minimum checklist
+
+When writing review comments, explicitly check:
+
+1. Correctness and edge cases
+2. Architecture fit with anomalib patterns
+3. Typing and public API clarity
+4. Docstrings, docs, and changelog updates
+5. Unit/integration coverage
+6. Security and workflow risk
+7. Maintainability and code hygiene
+
+## Review tone
+
+- Be specific and actionable.
+- Prefer comments like "Please add/adjust X because anomalib expects Y" over generic style remarks.
+- Ground feedback in the repository skills and the source documents they reference.
+
+## Skills to use
+
+- Python style, typing, imports, and API hygiene:
+  - `.agents/skills/python-style/SKILL.md`
+- Models, data, dataclasses, callbacks, metrics, and CLI integration:
+  - `.agents/skills/models-data/SKILL.md`
+- Docstrings, docs updates, and changelog expectations:
+  - `.agents/skills/docs-changelog/SKILL.md`
+  - `.agents/skills/python-docstrings/SKILL.md`
+  - `.agents/skills/model-doc-sync/SKILL.md`
+- Unit/integration/regression test expectations:
+  - `.agents/skills/testing/SKILL.md`
+- PR title, branch naming, contributor workflow, and quality gates:
+  - `.agents/skills/pr-workflow/SKILL.md`
+- Third-party code attribution and licensing:
+  - `.agents/skills/third-party-code/SKILL.md`
+- Benchmark and docs refresh:
+  - `.agents/skills/benchmark-and-docs-refresh/SKILL.md`
+- Model README and docs page sample image:
+  - `.agents/skills/model-sample-image-export/SKILL.md`
PATCH

echo "Gold patch applied."
