#!/usr/bin/env bash
set -euo pipefail

cd /workspace/huggingface-hub

# Idempotency guard
if grep -qF "- **PR description**: keep it casual. Include a `## Summary` with a few bullet p" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -65,36 +65,50 @@ Python client library for the Hugging Face Hub. Source code is in `src/huggingfa
 - `tqdm.py` — Custom progress bar wrappers.
 - Other: `_datetime.py`, `_dotenv.py`, `_git_credential.py`, `_subprocess.py`, `_telemetry.py`, `sha.py`, `_xet.py`, ...
 
-### Serialization (`src/huggingface_hub/serialization/`)
+### CLI (`src/huggingface_hub/cli/`)
 
-- `_torch.py` — `save_torch_model()`, `load_torch_model()`, state-dict splitting, safetensors support.
-- `_dduf.py` — DDUF format support.
+Entry point: `hf.py` (Typer app). Subcommands split into modules: `auth.py`, `repos.py`, `spaces.py`, `models.py`, `datasets.py`, `buckets.py`, `jobs.py`, `collections.py`, `webhooks.py`, etc.
 
-### CLI (`src/huggingface_hub/cli/`)
+#### Adding CLI commands
+
+**Structure & naming conventions:**
+
+- Commands are organized as **Typer groups** registered in `hf.py` (e.g. `app.add_typer(spaces_cli, name="spaces")`).
+- Each module creates its app with `typer_factory(help="...")` and defines commands with `@app.command("name")`.
+- Use **pipe-separated aliases**: `@app.command("list | ls")` registers both `list` and `ls`.
+- Use standard **verb names**: `ls`/`list`, `info`, `create`, `set`, `delete`, `update`.
+- For **sub-resources** with multiple operations, create a nested subgroup: `volumes_cli = typer_factory(...)` then `spaces_cli.add_typer(volumes_cli, name="volumes")` → gives `hf spaces volumes ls/set/delete`. See `repos.py` for examples (`tag_cli`, `branch_cli`).
+
+**Reusable option types** (from `_cli_utils.py` — import and use these, don't reinvent):
+
+- `TokenOpt`, `RepoIdArg`, `RepoTypeOpt`, `RevisionOpt` — standard auth/repo options.
+- `SearchOpt`, `AuthorOpt`, `FilterOpt`, `LimitOpt` — list/search options.
+- `FormatWithAutoOpt` / `FormatOpt` — output format (`auto|json|human|quiet|agent`).
+- `VolumesOpt` + `parse_volumes()` — `-v`/`--volume` flag with `hf://[TYPE/]SOURCE:/MOUNT_PATH[:ro]` syntax.
+- `get_hf_api(token=token)` — creates an `HfApi` instance with token.
+- `api_object_to_dict(obj)` — converts dataclass API objects to dicts for output.
+
+**Output** (from `_output.py` — use the `out` singleton):
 
-Entry point: `hf.py` (Typer app). Subcommands split into modules: `auth.py`, `repo.py`, `repo_files.py`, etc.
+Convention: stderr for prompts/warnings, stdout for data. Warnings go to stderr even in quiet/json modes.
 
-### Tests (`tests/`)
+- `out.table(items)` — list results (auto-formats as padded table / TSV / JSON depending on `--format`).
+- `out.dict(data)` — single-item detail view.
+- `out.result("Message", key=value, ...)` — success summary with green checkmark.
+- `out.confirm("Prompt?", yes=yes)` — confirmation for destructive operations. Pair with a `-y`/`--yes` flag.
+- `out.hint("...")` — actionable follow-up suggestion. Try to add hints when adding new commands or refactoring a command. Hints should preferably reuse the input args to be specific to the current use case. Example: `out.hint(f"Use 'hf buckets ls {bucket_id}' to list files from the bucket.")` after a bucket creation.
+- `out.text()`, `out.warning()`, `out.error()` — free-form output.
 
-- One `test_<module>.py` per source module (e.g. `test_hf_api.py`, `test_file_download.py`, `test_inference_client.py`).
-- `conftest.py` — Fixtures (temp cache dirs, env patching).
-- `testing_utils.py` / `testing_constants.py` — Shared test helpers and staging-repo constants.
-- `cassettes/` — Recorded HTTP responses for offline tests (`@pytest.mark.vcr`). **Do not add new cassettes.**
-- `fixtures/` — Static test data.
+**Destructive operations** should use `out.confirm()` with a `yes: Annotated[bool, typer.Option("-y", "--yes", help="Answer Yes to prompt automatically.")]` parameter.
 
-### Dev scripts (`utils/`)
+**Errors**: raise `CLIError("message")` for user-facing errors. Never wrap API calls with try/except for `RepositoryNotFoundError`, `RevisionNotFoundError`, etc. (already done globally)
 
-- `check_static_imports.py` — Ensures `__init__.py` static imports match the lazy loader.
-- `check_all_variable.py` — Validates `__all__` exports.
-- `generate_async_inference_client.py` — Generates `AsyncInferenceClient` from sync client.
-- `generate_inference_types.py` — Generates inference type definitions.
-- `generate_cli_reference.py` — Generates CLI docs.
+**Generated docs**: `make style` auto-regenerates `docs/source/en/package_reference/cli.md` via `utils/generate_cli_reference.py`. Don't edit that file by hand.
 
-## Style
+**Guides**: update the CLI guide `docs/sources/en/guides/cli.md` when adding / updating CLI commands. If the command is specific to a topic which has its own guide in `docs/sources/en/guides`, add a mention in the guide as well, using the same tone as the existing guide.
+
+**CLI tests**: add tests in `tests/test_cli.py`. Try to group tests into classes when relevant. Do not add a test for each specific use case / parameter set. Usually testing the 1-2 main use cases is enough.
 
-- Max line length: 119 chars.
-- Linter/formatter: `ruff`.
-- Imports sorted by `ruff` (isort-compatible).
 
 ### Type checking: local vs CI
 
@@ -105,8 +119,26 @@ Locally, `make quality` runs `ty check src` using whatever version of `ty` is in
 
 If CI fails on type checks that pass locally, the likely cause is a newer `ty` version or a `mypy`-only diagnostic. Fix the reported errors rather than downgrading the checker.
 
-## Testing notes
+## Commits & PRs
+
+- **Commit message prefix**: use `[Area]` prefix matching the scope, e.g. `[CLI] Add ...`, `[CLI] Fix ...`, `[Inference] ...`.
+- **PR title**: short (under 70 chars), same `[Area]` prefix convention.
+- **PR description**: keep it casual. Include a `## Summary` with a few bullet points and real CLI/code **examples** from manual testing (copy-paste terminal output). No need for a formal "Test plan" section. Call out breaking changes explicitly if any. It is important to document any decision taken in the PR or instructions provided in the prompt while working on the PR, ideally with the rationale behind it.
+
+## Code conventions
+
+### Simplicity is the #1 priority
+
+- No premature abstractions. No unnecessary generalization.
+- Don't implement features until they're actually needed.
+- Don't accept parameters without a use case.
+- No redundant `try`/`except` - don't catch errors already handled up the call stack.
+- Prefer strictness now, relax later.
+
+### Follow Python 3.10+ idioms
 
-- Tests use `pytest` with `pytest-env` setting `HUGGINGFACE_CO_STAGING=1` (tests hit staging Hub by default).
-- Most integration tests require `HF_TOKEN` to be set. Unit tests don't.
-- do not register or commit new HTTP cassettes.
+- `match`/`case` over `if`/`elif` chains when dispatching on a value.
+- `str | None` not `Optional[str]`.
+- f-strings over `.format()` or `%`.
+- Walrus operator (`:=`) when it improves readability.
+- Comprehensions over `map`/`filter` with lambdas.
\ No newline at end of file
PATCH

echo "Gold patch applied."
