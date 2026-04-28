#!/usr/bin/env bash
set -euo pipefail

cd /workspace/keploy

# Idempotency guard
if grep -qF "description: Guide for contributing to the Keploy documentation site at github.c" ".claude/skills/keploy-docs/SKILL.md" && grep -qF "description: End-to-end verification of a change to keploy/keploy using keploy's" ".claude/skills/keploy-e2e-test/SKILL.md" && grep -qF "description: Guide for creating PRs and issues on keploy repositories \u2014 PR forma" ".claude/skills/keploy-pr-workflow/SKILL.md" && grep -qF "- **Logging** \u2014 thread `*zap.Logger` explicitly (no globals); build once via `ut" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/keploy-docs/SKILL.md b/.claude/skills/keploy-docs/SKILL.md
@@ -0,0 +1,200 @@
+---
+name: keploy-docs
+description: Guide for contributing to the Keploy documentation site at github.com/keploy/docs. Invoke when a change in keploy/keploy introduces, removes, or alters user-visible behavior (new CLI flag, changed default, new command, new configuration field, new on-disk format) and the docs need to catch up — or when the user asks to document a feature, write a quickstart, or fix a docs bug. Covers where to put the edit, every CI check that must pass, and how to reproduce each check locally before the PR.
+---
+
+# keploy-docs
+
+## When to use
+
+- A change in `keploy/keploy` alters user-visible behavior: a new or renamed CLI flag, a changed default, a new command, a new configuration field, a new on-disk file format.
+- The user reports a docs bug, confusing passage, broken example, or stale screenshot.
+- You are about to claim "feature X is documented" without having checked.
+
+**Do not** touch docs for internal refactors, CI changes, performance work, or bug fixes that don't change user-visible behavior. The docs are a contract with users — edit only when the contract changes.
+
+## Repository layout
+
+- Upstream: `github.com/keploy/docs` — Docusaurus 2 site, published at `https://docs.keploy.io`.
+- Node version: `.nvmrc` pins the project; the CI workflows use Node 20. Use `nvm use` before `yarn`.
+- Package manager: `yarn` (classic — `yarn.lock` present). `npm install` also works and is what CI runs.
+
+```
+keploy-docs/
+├── docs/                          # Shared content (components, GSoC, Hacktoberfest). NOT feature docs.
+├── versioned_docs/
+│   ├── version-4.0.0/             # ← LATEST VERSION. All feature-doc edits go here.
+│   ├── version-3.0.0/             # Archived. Touch only for explicit back-ports.
+│   ├── version-2.0.0/             # Archived.
+│   └── version-1.0.0/             # Archived.
+├── versioned_sidebars/
+│   ├── version-4.0.0-sidebars.json  # Sidebar for v4 — update when adding a new page.
+│   └── ...
+├── versions.json                  # Ordered list; first entry ("4.0.0") is current.
+├── src/                           # Site React code (theme, components). Infrastructure, not content.
+├── plugins/                       # Docusaurus plugins. Infrastructure.
+├── static/                        # Images, binary assets.
+├── STYLE.md                       # Keploy-specific prose rules (see §Style).
+├── CONTRIBUTING.md                # Contribution flow.
+├── ADDING_A_QUICKSTART.md         # Checklist for new quickstart guides.
+└── .vale.ini, vale_styles/        # Vale prose linter config.
+```
+
+## **Rule: edits go in `versioned_docs/version-4.0.0/`**
+
+This is non-negotiable. The current version listed in `versions.json` is `4.0.0`, and the first entry in that file is always the live one. Editing `version-3.0.0/` (or older) only changes archived pages that users see under a banner explaining they are out of date.
+
+Before editing, run `head -n1 versions.json` (or open the file) and confirm the current version. If it has rolled over to `5.0.0` by the time you read this, edit `versioned_docs/version-5.0.0/` instead.
+
+Do **not** put new feature docs under the top-level `docs/` directory — that folder holds components and programme pages (GSoC, Hacktoberfest), not product content.
+
+## Decision: edit existing page vs. add new page
+
+Grep `versioned_docs/version-4.0.0/` for the feature name (and its synonyms) before creating a new file. Most features have a home.
+
+**Add a new page only when:**
+- The feature is a distinct workflow with multiple steps (a quickstart, an integration guide).
+- No existing page covers the surface, and shoehorning it in would hurt the existing narrative.
+- Ask for approval before doing this.
+
+**When you add a page you must also:**
+1. Register it in `versioned_sidebars/version-4.0.0-sidebars.json` under the correct section.
+2. Match the frontmatter shape of nearby pages. Required keys: `id`, `title`, `sidebar_label`, `description`, `tags`, `keywords`.
+3. Keep the URL slug kebab-cased (`my-new-feature`, not `myNewFeature`).
+4. For a new quickstart specifically, follow `ADDING_A_QUICKSTART.md` step by step.
+
+## Style rules (from `STYLE.md`)
+
+Docs follow the [Google Developer Documentation Style Guide](https://developers.google.com/style) and the Microsoft Writing Style Guide for anything Google doesn't cover. On top of that:
+
+- **Capitalize Keploy-specific terms.** `Test-Case`, `Test-Set`, `Test-Run`, `Mock`, `Normalise` when referring to the feature. Generic usage stays lowercase and should be rare.
+- **Sentence case in headings.** `How to record your first test`, not `How To Record Your First Test`.
+- **Infinitive verbs in titles.** `Install Keploy`, not `Installing Keploy`.
+- **Active voice.** `Keploy records the calls`, not `The calls are recorded by Keploy`.
+- **En dashes (`–`) for numeric ranges.** `5–10 GB`, not `5-10 GB`.
+- **Code formatting.** Backticks for inline code. Fenced code blocks with a language hint (`bash`, `go`, `yaml`, `json`).
+- **Inclusive, jargon-free prose.** Define acronyms on first use. Prefer short, direct sentences.
+
+Vale enforces a subset of this (see §CI).
+
+## CI pipelines — all must pass 
+
+
+NOTE: ONLY REPRODUE THESE CI PIPELINES IF YOU ARE NOT CONFIDENT THAT IT WILL PASS IN CI/CD. 
+
+Every PR against `keploy/docs` runs the following GitHub Actions. **All must be green before merge.** Each one is listed below with what it checks and how to reproduce it locally so you fix problems before the CI cycle.
+
+### 1. `Deploy PR Build and Check` (`.github/workflows/build_and_check.yml`)
+
+- Runs: `npm install && npm run build`.
+- Fails if Docusaurus can't build the site — broken frontmatter, dead sidebar references, malformed MDX, missing image paths, invalid admonitions.
+
+Reproduce locally:
+
+```bash
+yarn         # or: npm install
+yarn build   # same as CI's `npm run build`
+```
+
+If `yarn build` is slow, `yarn start` (dev server at http://localhost:3000) catches most issues faster and lets you visually verify the page renders.
+
+### 2. `Check Docusaurus docs with Vale linter` (`.github/workflows/vale-lint-action.yml`)
+
+- Runs Vale 3.0.3 over `versioned_docs/` with `filter_mode: diff_context` and `fail_on_error: true`. It only flags lines you added or modified, not pre-existing issues.
+- Config lives in `.vale.ini` and `vale_styles/`. Uses the Google style pack plus a custom vocabulary (`vale_styles/config/Vocab/Base/`).
+- Alert level is `error` — warnings do not fail the build, but fix them anyway.
+
+Reproduce locally (Vale via Homebrew: `brew install vale`):
+
+```bash
+vale versioned_docs/version-4.0.0/<path-to-your-edit>.md
+```
+
+Common failures: unspelled Keploy-specific terms (add them to `vale_styles/config/Vocab/Base/accept.txt`), capitalization of Keploy terms, passive voice in Google-pack rules.
+
+### 3. `Lint Codebase` (`.github/workflows/lint.yml`)
+
+- Runs `wagoid/commitlint-github-action@v5` on every commit in the PR.
+- Enforces Conventional Commits: `<type>(<scope>): <subject>` with type in `feat | fix | docs | style | refactor | test | chore | build | ci | perf | revert`.
+- For docs changes, the type is almost always `docs:`.
+
+just be careful writing the commit messages — the rules are not surprising.
+
+### 4. `Prettify Code` (`.github/workflows/prettify_code.yml`)
+
+- Runs Prettier 2.8.8 in `--check` mode on changed `.js` and `.md` files.
+- Config in `.prettierrc.json`: `printWidth: 80`, `proseWrap: preserve`, `tabWidth: 2`, `semi: true`, no `bracketSpacing`, double quotes, trailing commas (`es5`), `arrowParens: always`.
+
+Reproduce locally:
+
+```bash
+npx prettier@2.8.8 --check versioned_docs/version-4.0.0/<path-to-your-edit>.md
+
+# To auto-fix:
+npx prettier@2.8.8 --write versioned_docs/version-4.0.0/<path-to-your-edit>.md
+```
+
+Pin Prettier to `2.8.8` — a newer version will reformat differently and the CI diff will fail.
+
+### 5. `CLA` (`.github/workflows/cla.yml`)
+
+- Requires the contributor to have signed the Keploy CLA. The bot posts a comment on the PR with a signing link if needed. First-time contributors will need to sign once.
+
+### 6. `CodeQL` (`.github/workflows/codeql.yml`)
+
+- Security scanning. Prose edits won't fail this; JS changes might.
+
+### 7. `greetings.yml`
+
+- Welcome bot on first-time contributors. Not a blocking check.
+
+### One-shot pre-push checklist
+
+Run all of these from the docs repo root before pushing:
+
+```bash
+yarn                                                      # install
+yarn build                                                # pipeline 1
+vale versioned_docs/version-4.0.0/<your-file>.md          # pipeline 2
+git log origin/main..HEAD --format='%s'                   # eyeball pipeline 3
+npx prettier@2.8.8 --check versioned_docs/version-4.0.0/<your-file>.md  # pipeline 4
+```
+
+Only push when all four are clean.
+
+## Commits and branches
+
+- Branch name: `docs/<short-kebab>` — e.g. `docs/rename-test-sets-clarify`.
+- Commit subject: `docs: <what changed>` in present-tense imperative, under ~70 chars. Use `docs(<scope>):` if a scope helps (`docs(quickstart): add flask-redis sample`).
+- Commit body: required. Blank line after the subject, then a paragraph explaining the user-facing gap this closes and any code/behavior reference.
+- Sign-off: every commit. `git commit -s`. Do not hand-construct the `Signed-off-by` trailer.
+- Do not `--amend` past a failing hook — fix and create a new commit.
+- Never `--no-verify`.
+
+## PR template
+
+Follow the PR template that is followed in docs repository.
+
+## Customer-data hygiene
+
+Same rules as `keploy-pr-workflow`. Docs are read by everyone — even the most innocent-looking example can leak a real customer. Before committing:
+
+- No real hostnames; use `example.com`, `app.example.com`, `localhost:8080`.
+- No real auth tokens, API keys, JWTs. Use placeholders: `sk-xxxxxxxx`, `Bearer <token>`.
+- No real customer/user IDs, emails, order IDs. Use `user@example.com`, `user-123`.
+- No copy-pasted production logs, stack traces, or request IDs.
+- No screenshots with real PII — scrub or regenerate from a sample app.
+- IP addresses must be RFC1918 (`10.*`, `192.168.*`), loopback, or TEST-NET (`192.0.2.1`).
+
+If you're unsure whether something is customer-derived, it is. Replace it.
+
+## Scope discipline
+
+- Only the file(s) required for the change. Don't "clean up" unrelated prose in the same PR — it muddles review and inflates the Vale diff surface.
+- Don't reformat surrounding lines. Prettier's `proseWrap: preserve` deliberately keeps hand-chosen line breaks; changing them adds noise.
+- Don't add screenshots unless the user explicitly asked for them — they age fast. If you want to add a screenshot, ask for approval before doing so. And also them to provide you with the screenshot. dont leave it blank while creating a PR. just tell at the end that a screenshot would look great, you can add it to the user. 
+
+## Related skills
+
+- `keploy-pr-workflow` — commit format, sign-off, customer-data hygiene. Same rules apply here; this skill specializes them for the docs pipeline.
+- `keploy-e2e-test` — if you are documenting a behavior change, verify the behavior against a real sample before writing the doc. Don't document from source-reading alone.
diff --git a/.claude/skills/keploy-e2e-test/SKILL.md b/.claude/skills/keploy-e2e-test/SKILL.md
@@ -0,0 +1,313 @@
+---
+name: keploy-e2e-test
+description: End-to-end verification of a change to keploy/keploy using keploy's own record/replay against a real sample application. Use whenever the user asks to test a change, verify a fix, prove that a modification works in practice, add e2e coverage for a PR, reproduce a bug against a sample app, or wire a behavior into CI. Covers deciding whether e2e is the right signal, finding or extending an existing sample script, or (only when necessary) adding a new sample and matrix entry following the repo's conventions.
+---
+
+# keploy-e2e-test
+
+End-to-end verification of a change in `keploy/keploy` by building the
+binary from source and driving it through real record → replay against a
+real sample app, exactly the way CI does.
+
+## When to use
+
+Trigger this skill whenever the user asks to:
+
+- test / verify / prove a change works against a real app
+- add e2e coverage for a fix, feature, or PR
+- reproduce an issue against one of the sample apps
+- wire a new behavior into the CI matrix
+
+## When to decline (and say so explicitly)
+
+Before doing any work, decide whether e2e record/replay is even the right
+signal. Skip with a clear, short reason if:
+
+- **Pure refactor / internal rename.** No observable behavior changed. Unit
+  tests + `go build` + `golangci-lint run` is enough.
+- **Enterprise-only code path.** The logic lives in the private
+  `keploy/integrations` repo, not in this tree. You cannot fully exercise
+  it from a fresh fork — CI skips those jobs on forks, and so should you.
+  Say so and stop.
+- **CLI-only / output-formatting changes.** If the change is in help text,
+  flag parsing, or log formatting, a unit test or a manual `keploy --help`
+  check is sufficient.
+- **Docs / workflow YAML only.** No behavior change.
+- **Infrastructure the script relies on is missing.** If the affected code
+  path needs a dependency (eBPF kernel features, a managed DB, a paid
+  service) that isn't available in the sandbox you're running in, say so
+  and propose what would be needed instead of half-running.
+- **The user hasn't told you what changed.** Ask. Don't guess an app.
+
+If you skip, say *why* in one or two sentences and stop — do not silently
+fall back to "just run the unit tests."
+
+- Also, you can even skip unit tests if they dont make sense because our code keeps on changing.
+- If you are unsure about some stuff make sure you ask for approval before doing so.
+
+## Step 1 — Understand the change
+
+Before touching anything, build a concrete picture of:
+
+1. **What code changed.** Read the diff (`git diff main...HEAD`, or the
+   files the user points at). For a PR, read the PR description and the
+   changed files — not just the titles.
+2. **Which code path it exercises.**
+   - Is it HTTP request/response matching? (`pkg/matcher`, `pkg/service/replay`)
+   - A protocol parser? (`pkg/core/proxy`, `pkg/models/<protocol>`, `pkg/agent/hooks`)
+   - On-disk YAML format? (`pkg/platform/yaml`)
+   - Mock correlation / ordering? (`pkg/service/orchestrator`)
+   - Reports / coverage? (`pkg/service/report`, `pkg/platform/coverage`)
+   - A CLI command or flag? (`cli/<cmd>.go`, `config/config.go`)
+   - Memory / performance? (`pkg/agent/memoryguard`, `main.go`)
+3. **What user-visible behavior should now change.** State it in one
+   sentence before you start looking for an app.
+4. **What the failure mode would look like** in a report — a missing mock?
+   a status mismatch? a race in the record log? Knowing this up front tells
+   you what to grep for after replay.
+
+If the affected path is obvious from the diff, say so and move on. If it
+isn't, say so and ask — do not guess.
+
+## Step 2 — Find an existing sample app that exercises this path
+
+Search broadly across the keploy organization for a sample that already
+exercises the affected surface area. The sample repos CI pulls from are in
+`AGENTS.md` under "Sample repos CI pulls from"; the complete list of sample
+repos on the org is discoverable with `gh repo list keploy`. its usually samples-* which * can be go, java etc. 
+
+How to search, in rough order of cost:
+
+1. **Look at the existing script directory first.** The canonical index of
+   what's already covered is `.github/workflows/test_workflow_scripts/`.
+   Each subdirectory maps 1:1 to a sample app, and the shell script inside
+   is what CI actually runs against that app. `ls` that tree — if one of
+   the names obviously matches your changed path (e.g. you changed DNS
+   parsing → check `golang/dns_mock/`, `golang/dns_dedup/`), read that
+   script first.
+2. **Search the matrix entries.** `grep -rn script_dir .github/workflows/*.yml`
+   shows every app currently wired into CI with its `path` (directory in
+   the samples repo) and `script_dir` (directory in `test_workflow_scripts`).
+3. **Search the sample repos themselves.** For a protocol or stack not
+   covered by an in-tree script:
+   ```bash
+   gh api repos/keploy/samples-go/contents/       --jq '.[] | select(.type == "dir") | .name'
+   gh api repos/keploy/samples-python/contents/   --jq '.[] | select(.type == "dir") | .name'
+   gh api repos/keploy/samples-typescript/contents/ --jq '.[] | select(.type == "dir") | .name'
+   gh api repos/keploy/samples-java/contents/     --jq '.[] | select(.type == "dir") | .name'
+   gh api repos/keploy/samples-rust/contents/     --jq '.[] | select(.type == "dir") | .name'
+   gh api repos/keploy/samples-csharp/contents/   --jq '.[] | select(.type == "dir") | .name'
+   ```
+   Don't hard-code which repo to look in — the best match may be in a
+   less-obvious place (e.g. a graphql-over-postgres change might be best
+   exercised by `samples-go/graphql-sql` *or* by `samples-java/spring-boot-postgres-graphql`).
+   Skim each candidate's README in the sample repo before committing.
+4. **When nothing fits.** If no sample on the org exercises the affected
+   path, you have two honest options:
+   - Extend the closest existing sample (see Step 3b).
+   - Add a new minimal sample (see Step 3c). This is the last resort — new
+     samples are expensive to maintain.
+   - dont be relunctant to do these steps if you think it is necessary.
+
+## Step 3 — Decide: use, extend, or create
+
+### 3a. Use as-is (preferred)
+
+If an existing `test_workflow_scripts/<lang>/<script_dir>/<lang>-linux.sh`
+already exercises the exact behavior your change touches — use it. Don't
+modify the script. Just build the binary and run it (Step 4).
+
+### 3b. Extend an existing script (second preference)
+
+If the app is right but the script doesn't cover the new behavior, make
+the *minimal* additive change:
+
+- Add the new traffic call inside the existing `send_request()` (or
+  whatever the script calls its traffic driver).
+- If the change introduces a new report field or a new exit-code
+  expectation, add a new check after the existing `check_test_report` /
+  report-walking loop — do not rewrite the loop.
+- Keep everything that already passes passing. If you must change an
+  existing assertion, state *why* explicitly in a comment on that line.
+- Preserve the script's prevailing style — `set -Eeuo pipefail` vs. plain,
+  `section`/`endsec` GitHub grouping helpers, trap handlers, 1 vs. 2
+  record iterations. Match what's already there.
+
+When in doubt, look at how recent extensions were done by reading the git
+history of the script you're editing.
+
+Please dont break existing code while doing it. 
+
+### 3c. Create a new sample + script (last resort)
+
+Only if no existing app exercises the path. This has two sides:
+
+**Sample-app side (in `keploy/samples-<lang>/`):**
+- Keep it minimal: one binary / module, one HTTP surface, one dependency
+  if required. Match the structure of the smallest existing samples in
+  the same repo (e.g. `samples-go/http-pokeapi`, `samples-python/flask-secret`).
+- You cannot merge a new sample into the org sample repos yourself without
+  a PR there. If that's out of scope for this task, say so and propose the
+  sample contents instead of silently trying to checkout a branch that
+  doesn't exist. 
+  Do create a PR in the sample repository while using the skill `keploy-pr-workflow` to create the PR.
+
+**`keploy/keploy` side (this repo):**
+- Create `.github/workflows/test_workflow_scripts/<lang>/<script_dir>/<lang>-linux.sh`.
+  Name `<script_dir>` as `lower_snake_case` of the sample folder name
+  (convention: see existing mappings — `echo-mysql` → `echo_mysql`,
+  `http-pokeapi` → `http_pokeapi`, `go-grpc` → `go-grpc` (kept hyphenated
+  here, so copy the convention of the closest existing neighbor rather
+  than normalizing blindly)).
+- Copy the boilerplate from the closest existing script in the same
+  language. Canonical references:
+  - Go + HTTP: `.github/workflows/test_workflow_scripts/golang/http_pokeapi/golang-linux.sh`
+  - Go + SQL/MySQL: `.github/workflows/test_workflow_scripts/golang/echo_mysql/golang-linux.sh`
+  - Node + Mongo: `.github/workflows/test_workflow_scripts/node/express_mongoose/node-linux.sh`
+  - Python + Flask: `.github/workflows/test_workflow_scripts/python/flask-secret/python-linux.sh`
+  - Java + Postgres: `.github/workflows/test_workflow_scripts/java/spring_petclinic/java-linux.sh`
+  - gRPC (modes): `.github/workflows/test_workflow_scripts/golang/go-grpc/grpc-linux.sh`
+- Add a matrix entry under the right per-language workflow:
+  - Go native Linux → `.github/workflows/golang_linux.yml`
+  - Go Docker → `.github/workflows/golang_docker.yml`
+  - gRPC → `.github/workflows/grpc_linux.yml`
+  - Python → `.github/workflows/python_linux.yml` (native) / `python_docker.yml`
+  - Node → `.github/workflows/node_linux.yml` / `node_docker.yml`
+  - Java → `.github/workflows/java_linux.yml`
+  - Schema match → `.github/workflows/schema_match_linux.yml`
+  The entry must have `name`, `path` (dir inside the samples repo),
+  `script_dir` (dir inside `test_workflow_scripts/<lang>/`), plus any
+  extra axes the workflow uses (e.g. `mode`, `enable_ssl`).
+- Do **not** add a new top-level workflow file; reuse the existing one
+  for the language. The gate job in `prepare_and_run.yml` depends on the
+  existing workflow names — new ones won't be required checks. 
+- If needed, you can create a new workflow file but try to add a new step in the existing workflow file if possible. that's much better than creating a new workflow file.
+- If the sample needs a branch of the samples repo other than `main`,
+  follow the existing pattern of `git fetch origin && git checkout
+  origin/<branch>` at the top of the script (see `echo_mysql`,
+  `risk_profile`, `sse_preflight`). Document that branch in the PR
+  description on the samples-repo side.
+
+## Step 4 — Run record / replay locally
+
+Always build the binary the same way CI does before running:
+
+```bash
+# matches CI's "build-no-race" artifact
+go build -tags=viper_bind_struct -o ./out/build-no-race/keploy .
+
+# matches CI's "build" artifact (race-enabled; needs CGO)
+CGO_ENABLED=1 go build -race -tags=viper_bind_struct -o ./out/build/keploy .
+```
+
+Then run the script the way CI does (from inside the sample app
+directory), passing the binaries through the env:
+
+```bash
+# Checkout samples repo beside this one (once)
+git clone https://github.com/keploy/samples-go   ../samples-go
+
+cd ../samples-go/<matrix.app.path>
+
+RECORD_BIN=/abs/path/to/keploy/out/build/keploy \
+REPLAY_BIN=/abs/path/to/keploy/out/build/keploy \
+GITHUB_WORKSPACE=/abs/path/to/keploy \
+bash -x $GITHUB_WORKSPACE/.github/workflows/test_workflow_scripts/<lang>/<script_dir>/<lang>-linux.sh
+```
+
+`GITHUB_WORKSPACE` must point at the keploy repo root because scripts
+source `test-iid.sh` and `update-java.sh` via that path.
+
+On Linux, `keploy` needs root for eBPF — most scripts use `sudo` on
+specific commands. Don't add `sudo` to the whole script invocation if the
+script doesn't already do that; copy the pattern used by the existing
+scripts (selective `sudo -E env PATH=$PATH "$RECORD_BIN" …`, sometimes
+`sudo "$RECORD_BIN" config --generate`).
+
+On macOS/Windows the same script pattern won't work unmodified — in those
+environments either fall back to the `*_macos.yml` / `*_windows.yml` /
+`.ps1` counterparts, or say you can't reproduce locally and run it via
+CI. State that limitation explicitly rather than pretending to test.
+
+If you can't run the script locally (no Docker, no eBPF support in a
+container, missing dependency), **say so**. Do not claim success without
+real evidence.
+
+## Step 5 — Verify
+
+The script's own success criterion is: all `./keploy/reports/test-run-*/
+test-set-*-report.yaml` have `status: PASSED`, and no `"ERROR"` or
+`"WARNING: DATA RACE"` lines appeared in the record or test logs.
+
+You must independently verify the same:
+
+```bash
+# the newest test-run dir
+RUN_DIR=$(ls -1dt ./keploy/reports/test-run-* | head -n1)
+
+# every report should say PASSED
+for rpt in "$RUN_DIR"/test-set-*-report.yaml; do
+  awk '/^status:/{print FILENAME": "$2; exit}' "$rpt"
+done
+
+# coverage (when the sample enables it)
+[ -f "$RUN_DIR/coverage.yaml" ] && cat "$RUN_DIR/coverage.yaml"
+```
+
+Additionally:
+
+- Confirm record ran the expected number of iterations (most scripts loop
+  1 or 2 times — check the `for i in 1 2; do` construct).
+- If the change is behavior-additive, the new test case or new assertion
+  you added must be present in a generated `test-set-<n>/tests/test-*.yaml`
+  or in the report's per-test breakdown.
+- If the change is a fix, run the script **against the previous `main`
+  binary first** (use the `latest` artifact pattern from CI, or just
+  build `main` into a separate path). Confirm the script fails before
+  your change and passes after. That is the clean proof of a fix.
+- Grep record and replay logs for the known-fatal markers: `grep -E
+  "ERROR|WARNING: DATA RACE"`. An "ERROR" line in keploy output fails
+  the script in CI; reproduce that gate locally.
+
+## Step 6 — Report back
+
+End with a short, factual summary:
+
+- Which sample app was used (`samples-<lang>/<path>`), and whether it was
+  used as-is, extended, or newly created.
+- Which script ran (`test_workflow_scripts/<lang>/<script_dir>/<lang>-linux.sh`).
+- What command produced the evidence (the exact `RECORD_BIN=… REPLAY_BIN=… bash …` line).
+- What the reports said (how many test sets, all PASSED, coverage %).
+- If a pre-change run showed the failure mode, say so and include the
+  relevant diff in report output.
+- If you skipped e2e, say **which** skip reason applied from the list at
+  the top — don't invent a new reason.
+- If something is failing with your changes or you found a bug in the implementation using this test then please try to fix it by finding the root cause. If you cant then report it to the user.
+
+## What not to do
+
+- Don't invent a new shell-script pattern. If the existing scripts use
+  `set -Eeuo pipefail` + `::group::` sections + a `die` trap, match that;
+  if they use a simpler linear style (`http_pokeapi`), match that. Pick
+  one of the existing templates as a starting point.
+- Don't commit `keploy/`, `keploy.yml`, `*_logs.txt`, or other run
+  artifacts from a sample app. Those are generated per run. It might be needed 
+  if the only thing you are checking is the test mode or other modes and 
+  you know you havent made any changes to the record mode. We can save CI times
+  by not running the record mode.
+- Don't edit generated eBPF Go (`pkg/agent/hooks/bpf_*_bpfel.go`) as part
+  of the e2e flow. If the eBPF programs need to change, that belongs in a
+  separate, intentional step (edit the `.c` source and regenerate).
+- Don't skip the cross-version matrix dimension. The three configs
+  (`record_latest_replay_build`, `record_build_replay_latest`,
+  `record_build_replay_build`) exist to catch mock-format incompatibility.
+  If your change would be gated on "both sides are new," either add
+  capability detection (see
+  `.github/workflows/test_workflow_scripts/golang/risk_profile/golang-linux.sh`
+  and `connect_tunnel/golang-linux.sh` for how the existing scripts
+  distinguish `*/build/keploy` from `latest`), or flag the incompatibility
+  to the user so they can decide.
+- Don't claim "tests pass" from compilation alone. `go build` succeeding
+  isn't a substitute for a real replay run. If you couldn't run, say so.
+
+For anything in samples repo side changes, you must have created a branch. Use that branch has ref in keploy/keploy to test it. 
\ No newline at end of file
diff --git a/.claude/skills/keploy-pr-workflow/SKILL.md b/.claude/skills/keploy-pr-workflow/SKILL.md
@@ -0,0 +1,92 @@
+---
+name: keploy-pr-workflow
+description: Guide for creating PRs and issues on keploy repositories — PR format, customer-data hygiene, commit conventions, sign-off. Invoke when the user asks to open, update, or review a pull request or issue, when preparing a commit that will land in main, or whenever a change is about to leave the local machine.
+---
+
+# keploy-pr-workflow
+
+## When to use
+
+- About to run `gh pr create`, `gh pr edit`, or `gh issue create`.
+- Writing a commit message that will land in `main`.
+- Reviewing your own diff before pushing.
+- Copying error output, logs, or sample data into a PR description, issue, test
+  fixture, or README.
+
+## 1. Customer-data hygiene (non-negotiable)
+
+Keploy records real user applications. Traces, mocks, recordings, and logs
+routinely carry customer data — headers with auth tokens, bodies with PII,
+internal hostnames, request IDs that map back to users. Treat every fixture,
+log snippet, and error dump as tainted until you've checked it.
+
+Before anything leaves your machine, scrub for:
+
+- **Credentials** — API keys, bearer tokens, JWTs, DB passwords, session
+  cookies, OAuth client secrets, AWS/GCP/Azure keys. If a test needs one,
+  read from env; use placeholders in docs (`sk-xxxxxxxx`, `Bearer <token>`).
+- **Internal hostnames and URLs** — `*.internal`, `*.prod`, `*.corp`, real
+  company domains. Use `example.com`, `httpbin.org`, or loopback in samples.
+- **IP addresses that aren't RFC1918 / loopback / TEST-NET** — assume any
+  public IP in a log is traceable. Replace with `192.0.2.1` (TEST-NET-1).
+- **User identifiers** — emails, usernames, account IDs, order IDs, customer
+  names. Substitute with `user@example.com`, `user-123`, etc.
+- **Request/trace IDs** — these tie back to real traffic in observability
+  systems. Redact them from pasted logs.
+- **Real recorded traffic** — never commit a customer's `keploy/test-set-*`
+  directory. Even anonymized ones tend to keep giveaways in paths or timings.
+  If you need sample recordings, generate them against `samples-go`,
+  `samples-python`, etc.
+- **Stack traces from production runs** — they leak file paths, binary
+  versions, and sometimes in-memory values.
+
+If you're unsure whether something is customer-derived, it is. Err on the
+side of redaction — you can always add detail back, you can't un-publish.
+
+## 2. Commit messages
+
+Format: `<type>(<scope>): <subject>` — Conventional Commits, enforced by
+`commitizen` via `.pre-commit-config.yaml`.
+
+Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.
+
+Rules:
+
+- Subject in present tense, imperative mood. `fix: resolve null pointer on
+  test-set reset`, not `fixed` or `fixes`.
+- Every commit includes a body — blank line after the subject, then a
+  paragraph describing **what changed and why**. Mandatory even for
+  one-liners.
+- Sign off with `git commit -s`. Let git read identity from config; don't
+  hand-construct the `Signed-off-by` trailer.
+
+## 3. PR/issue title and body
+
+The PR/issue template should match the template that is being used in the repository that we are working in. 
+
+## 4. Destructive git operations
+
+Never, without explicit user approval:
+
+- `git push --force` to `main` (or any shared branch).
+- `git reset --hard` / `git clean -fd` on a branch with uncommitted work.
+- `git branch -D` on anything not your own local branch.
+- Rebase across other contributors' published commits.
+
+When in doubt, ask. Destructive ops are cheap to confirm and expensive to
+undo.
+
+## 5. Issues
+
+When filing or commenting on an issue:
+
+- Same customer-data rules apply — scrub logs before pasting.
+- Include: keploy version (`keploy --version`), OS/arch, the exact command
+  you ran, and whether it reproduces in Docker vs native.
+- If you're attaching a recording to reproduce, regenerate it against a
+  public sample app; never attach a customer's test-set.
+
+## Related skills
+
+- `keploy-e2e-test` — verify a behavior change against a real sample before
+  opening the PR.
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,314 @@
+# AGENTS.md
+
+Practical reference for agents working in `keploy/keploy`. Everything here is
+grounded in the current state of the repo — if something below conflicts with
+what you see on disk, trust the disk and update this file.
+
+## What this project is
+
+Keploy is a backend testing tool that records real API + dependency traffic
+from a running application and replays it as deterministic tests with mocks.
+It intercepts traffic at the network layer using eBPF (Linux) and a userspace
+proxy (macOS/Windows), so apps don't need an SDK or code changes. The binary
+is a single Go CLI: `keploy`.
+
+- Go module: `go.keploy.io/server/v3`
+- Primary entry point: `main.go` → `cli.Root(...)` in `cli/root.go`
+
+## Build, run, lint, test
+
+### Build the binary
+
+```bash
+# Standard build (what CI calls "build-no-race")
+go build -tags=viper_bind_struct -o keploy .
+
+# Race-enabled build (what CI calls "build" — used as the default in CI matrices)
+CGO_ENABLED=1 go build -race -tags=viper_bind_struct -o keploy .
+```
+
+The `viper_bind_struct` build tag is required — leaving it off will cause
+config fields not to bind correctly at runtime.
+
+Version / Sentry DSN / server URL / GitHub client ID are injected via
+`-ldflags` (see `Dockerfile` and `goreleaser.yaml`). For local development
+the default `version` is `3-dev`.
+
+### Run locally
+
+Platform support is not uniform — it's gated by how the agent can
+intercept traffic on each OS:
+
+| Platform                  | Native binary (app runs on host)                                                                             | Keploy-in-Docker (app runs in Docker) |
+| ------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------- |
+| **Linux** (x86_64, arm64) | ✅ Supported — uses eBPF (`pkg/agent/hooks/linux/`). Requires root.                                          | ✅ Supported                          |
+| **Windows** (amd64)       | ✅ Supported — uses the WinDivert redirector (`pkg/agent/hooks/windows/`, `libwindows_redirector.a`).        | ✅ Supported                          |
+| **Windows** (arm64)       | ❌ Falls through to the `others` stub — `Load()` / `Record()` return "not supported on non-Linux platforms". | ✅ Supported                          |
+| **macOS** (amd64, arm64)  | ❌ Same `others` stub — there is **no** native interception path on macOS.                                   | ✅ Supported (only option)            |
+
+- On **macOS** you _cannot_ use keploy natively. You must:
+  1. Build the keploy Docker image: `sudo docker image build -t ghcr.io/keploy/keploy:v3-dev .`
+  2. Run your application inside Docker (usually via `docker compose`).
+  3. Run keploy as that Docker image, which attaches to the app container.
+     If the app isn't in Docker, keploy can't intercept its traffic on macOS.
+     This is why `prepare_and_run_macos.yml` only calls `golang_docker_macos.yml`
+     — there's no macOS-native equivalent.
+- On **Linux** you can pick either — native (with `sudo`) or via the
+  Docker image. CI exercises both (`golang_linux.yml` + `golang_docker.yml`).
+- On **Windows** (amd64) native works without sudo; Docker mode also works.
+
+**Native Linux run:**
+
+```bash
+sudo ./keploy record -c "<your app cmd>"
+sudo ./keploy test   -c "<your app cmd>" --delay 10
+```
+
+If you pass a `docker`/`docker compose` command as `-c` without sudo on
+Linux, `main.go` detects that in `utils.ShouldReexecWithSudo()` and
+`syscall.Exec`s itself under `sudo -E` (see `utils/reexec_linux.go`). On
+macOS and Windows the same helper is a no-op — `reexec_darwin.go` and
+`reexec_windows.go` both short-circuit to `false`, since those platforms
+rely on the active Docker context / Docker Desktop.
+
+### Docker
+
+```bash
+sudo docker image build -t ghcr.io/keploy/keploy:v3-dev .
+```
+
+`ghcr.io/keploy/keploy:v3-dev` is the tag CI produces for dev builds and the
+one the samples expect.
+
+### Lint
+
+Linter is `golangci-lint` with config schema v2, at `.golangci.yml`:
+
+- Enabled linters: `govet`, `staticcheck`, `errcheck`, `ineffassign`, `unused`
+- Formatters: `gofmt`, `goimports`
+- Paths excluded from linters: the generated eBPF Go files (currently `pkg/agent/hooks/bpf_arm64_bpfel.go` and `pkg/agent/hooks/bpf_x86_bpfel.go`) and `pkg/service/utgen`
+
+```bash
+golangci-lint run
+```
+
+### Commit hygiene
+
+- `.pre-commit-config.yaml` wires `commitizen` (Conventional Commits).
+- `.cz.toml` pins the convention to `cz_conventional_commits`. Use types
+  like `feat:`, `fix:`, `chore:`, `refactor:`, `test:`, `docs:`.
+- Every commit needs a description body (blank line, then a paragraph
+  explaining what changed and why).
+- Sign off every commit with `git commit -s` — this appends a
+  `Signed-off-by: <user.name> <user.email>` trailer using the values from
+  the effective git config (system → `~/.gitconfig` → `.git/config`). Do
+  not hand-construct the trailer; let git read the identity from config so
+  it matches the author.
+
+When opening PRs or issues — customer-data hygiene, PR body template, which
+files not to touch — see the **`keploy-pr-workflow` skill**
+(`.claude/skills/keploy-pr-workflow/SKILL.md`). Don't paste real traces,
+tokens, internal hostnames, or production logs into PRs, issues, tests, or
+committed fixtures.
+
+## Key commands (quick user-facing recap)
+
+| Command                      | Package                          | What it does                                                                     |
+| ---------------------------- | -------------------------------- | -------------------------------------------------------------------------------- |
+| `keploy record -c "<cmd>"`   | `pkg/service/record`             | Runs the app, captures dependency traffic into `./keploy/test-set-*`             |
+| `keploy test -c "<cmd>"`     | `pkg/service/replay`             | Replays recorded calls, mocks dependencies, writes `./keploy/reports/test-run-*` |
+| `keploy rerecord -c "<cmd>"` | `pkg/service/orchestrator`       | Re-records against new code to pick up accepted changes                          |
+| `keploy normalize`           | `pkg/service/tools`              | Accepts newly-observed responses into the golden test cases                      |
+| `keploy sanitize`            | `pkg/service/tools`              | Scrubs secrets using `custom_gitleaks_rules.toml` + built-in rules               |
+| `keploy templatize`          | `pkg/service/tools`              | Replaces dynamic values with templates in test sets                              |
+| `keploy config --generate`   | `cli/config.go`                  | Writes a default `keploy.yml`                                                    |
+| `keploy contract ...`        | `pkg/service/contract`           | OpenAPI contract generation / testing                                            |
+| `keploy diff <r1> <r2>`      | `pkg/service/diff`               | Diff two test runs                                                               |
+| `keploy report`              | `pkg/service/report`             | Summarize a previous test run                                                    |
+| `keploy export` / `import`   | `cli/export.go`, `cli/import.go` | Move test-sets between repos                                                     |
+| `keploy update`              | `cli/update.go`                  | Self-update the binary                                                           |
+| `keploy agent`               | `cli/agent.go`                   | Internal — used by the Docker image entrypoint                                   |
+
+Note: `keploy gen` (`pkg/service/utgen`, LLM unit-test generation) has its CLI
+registration commented out in `cli/utgen.go` — the implementation exists but
+the command isn't wired. Don't document it as user-facing.
+
+`keploy --help` is authoritative; if you add, rename, or disable a command,
+update this table in the same commit. Spin up a subagent to walk the `cli/`
+directory if you need the full flag list for a specific command.
+
+When a change alters user-visible behavior (new flag, changed default, new
+command, new config field), the docs at `keploy/docs` may need updating — see
+the **`keploy-docs` skill** (`.claude/skills/keploy-docs/SKILL.md`) for where
+to put the edit and which CI checks must pass.
+
+## The on-disk format (for matching against reports in scripts)
+
+After `keploy record`:
+
+```
+keploy/
+├── test-set-0/
+│   ├── tests/
+│   │   ├── test-1.yaml
+│   │   └── test-2.yaml
+│   └── mocks.yaml         (or mocks/ dir depending on version)
+├── test-set-1/
+│   └── ...
+```
+
+After `keploy test`:
+
+```
+keploy/
+└── reports/
+    └── test-run-0/                    (newest run has highest number)
+        ├── test-set-0-report.yaml     (top-level field: `status: PASSED|FAILED`)
+        ├── test-set-1-report.yaml
+        └── coverage.yaml              (when coverage is enabled)
+```
+
+The `status:` line is the ground truth scripts grep for. See
+`.github/workflows/test_workflow_scripts/golang/echo_mysql/golang-linux.sh`
+for the canonical report-parsing loop.
+
+## Conventions
+
+### Keploy-specific
+
+- **Package doc comments** — every `package foo` opens with `// Package foo ...`.
+- **Root context** — get the cancellable root from `utils.NewCtx()` (`utils/ctx.go`). It installs SIGINT/SIGTERM handlers that call `cancel`. Don't call `context.Background()` in service code.
+- **Goroutine lifecycle** — use `errgroup.WithContext(ctx)` for any goroutine, not bare `go func()` or `sync.WaitGroup`. Split work across per-phase errgroups (setup / run-app / req) with their own cancel funcs so one phase can tear down without killing the others — `pkg/service/record/record.go:78-88` is the canonical layout.
+- **Logging** — thread `*zap.Logger` explicitly (no globals); build once via `utils/log.New()`. Use `utils.LogError(logger, err, "msg", ...fields)` in place of `logger.Error(...)` — it drops `context.Canceled` so expected shutdown paths don't spam the log. (It does **not** set `ErrCode`; that's separate.). If something is failing, the logs should also tell the user the next step on what to do.
+- **Exit code** — `utils.ErrCode` is a package-level `int` that `main.go` passes to `os.Exit`. Set it to `1` when you want the process to exit non-zero; today only `pkg/service/replay/replay.go` flips it (on failed test runs).
+- **Errors** — wrap with `fmt.Errorf("...: %w", err)`. Classify app-lifecycle failures with `models.AppError` + `models.AppErrorType` (string enum in `pkg/models/errors.go`). Prefer `errors.Is` / `errors.As` over string matching; custom errors carrying a diagnostic payload (e.g. `mockMismatchError`) must implement `Unwrap()`.
+- **Config access** — services read from the `*config.Config` wired in `cli/provider/`. Don't call `os.Getenv` from `pkg/service/` or `pkg/core/`; add a field to `config.Config`, parse it in `cmdConfigurator` / `main.go`, thread it in.
+- **Interfaces live where they're consumed** — each `pkg/service/<name>/service.go` defines the small interfaces that package depends on (`TestDB`, `MockDB`, `Telemetry`, `Instrumentation`, ...). Keep them 1–10 methods and role-shaped; concrete implementations live in separate packages (e.g. `pkg/platform/yaml/testdb/`) and are wired in `cli/provider/core_service.go`.
+- **Context-aware I/O** — long-lived flows should use `ctxReader` / `ctxWriter` from `pkg/platform/yaml/yaml.go` so file I/O honors cancellation.
+- **Generated code** — the eBPF Go files `pkg/agent/hooks/bpf_*_bpfel.go` (today: `bpf_arm64_bpfel.go`, `bpf_x86_bpfel.go`) are generated from `.c` sources. Never edit by hand; they're linter-excluded in `.golangci.yml`. Regenerate via the eBPF toolchain if probe behavior must change.
+
+### General Go hygiene (universal rules this codebase follows)
+
+- **Accept interfaces, return structs.** Define an interface at the point of _use_, not the point of _implementation_. If there's a single impl and a single consumer, you probably don't need the interface yet.
+- **`context.Context` is the first parameter** on every exported method — after the receiver, before everything else. Never store a context in a struct.
+- **Don't thread state through `context.WithValue`.** It's for request-scoped values (trace IDs, auth), not for dependency injection — pass dependencies as struct fields or function args. The one tolerated exception here is `models.ErrGroupKey`, which carries the parent errgroup.
+- **Panic at boundaries only.** Library and service code returns errors. `recover` lives at top-level goroutine entry points and `main` (see `utils.Recover`). Don't panic to signal expected failure.
+- **Table-driven tests with `testify`.** `require` for fail-fast assertions, `assert` when the test should continue. Unit coverage is sparse in this repo — protocol-level behavior is verified via the `keploy-e2e-test` skill, so write table-driven tests for pure logic and reach for e2e when behavior crosses a boundary.
+- **Doc comments on every exported symbol.** `<Name> does X.` form — godoc is the public contract.
+- **Keep functions short and intention-revealing.** If a function has more than ~3 nested levels or ~50 logical lines, split it before adding more branches. Naming earns its keep: a function named `parseRecordFrame` beats a comment above a block called `doStep`.
+- **Minimize exported surface.** Only capitalize identifiers that actually need to leave the package. Shrinking the public API is the cheapest refactor available.
+
+Note: All of the things mentioned in Conventions can be ignored if you are not sure about it and you are not fully confident. 
+
+## CI at a glance
+
+### Entry points
+
+- `.github/workflows/prepare_and_run.yml` — primary Linux CI. Runs on PRs to `main` and pushes to `main`. Everything below is downstream of this.
+- `.github/workflows/prepare_and_run_macos.yml` — same idea for macOS (self-hosted).
+- `.github/workflows/prepare_and_run_windows.yml` — Windows equivalents.
+- `.github/workflows/prepare_and_run_integrations.yml` — runs the private-parser-only matrix subset for the integrations repo.
+- `.github/workflows/manual-release.yml` — `workflow_dispatch` only; triggers the enterprise pipeline.
+
+### What `prepare_and_run.yml` does
+
+1. **Builds three binaries up front** so every matrix job can mix and match:
+   - `build-no-race` — `go build -tags=viper_bind_struct`
+   - `build` — `go build -race -tags=viper_bind_struct` (CGO on)
+   - `latest` — downloads the most recent GitHub release
+     Each is uploaded as an artifact with that name.
+2. **Builds a Docker image** and pushes it to `ttl.sh` with a unique per-run tag.
+3. **Fans out** to per-language workflows via `workflow_call`:
+   - `golang_linux.yml` — `samples-go` apps, native Linux
+   - `golang_docker.yml` — `samples-go` apps, through the Docker image
+   - `golang_wsl.yml` — `samples-go` apps, WSL
+   - `python_linux.yml`, `python_docker.yml` — `samples-python`
+   - `node_linux.yml`, `node_docker.yml` — `samples-typescript`
+   - `java_linux.yml` — `samples-java`
+   - `grpc_linux.yml` — gRPC-specific go matrix
+   - `schema_match_linux.yml` — schema-match matrix (python)
+   - `fuzzer_linux.yml`, `node_mapping.yml` — specialised
+4. **Gates on a single job `gate`**. That's the only required status check — re-running the `gate` alone is pointless; it just re-checks upstream results.
+
+### Matrix structure (the pattern every language workflow follows)
+
+```yaml
+matrix:
+  app:
+    - name: <display-name>
+      path: <directory in samples-<lang> repo>
+      script_dir: <directory in .github/workflows/test_workflow_scripts/<lang>/>
+  config:
+    - job: record_latest_replay_build # record with released binary, replay with this PR's build
+      record_src: latest
+      replay_src: build
+    - job: record_build_replay_latest # record with this PR's build, replay with released binary
+      record_src: build
+      replay_src: latest
+    - job: record_build_replay_build # both this PR's build — exercises same-version behavior
+      record_src: build
+      replay_src: build
+```
+
+The three `config` entries are how CI guarantees **mock format backwards and
+forwards compatibility**: any new change must interoperate with the last
+released binary in both directions. If your change would break either,
+it needs to be gated on something (capability detection, version check, or
+feature flag) — see `risk_profile/golang-linux.sh` for a concrete example
+that branches on `case "${REPLAY_BIN:-}" in */build/keploy) ...`.
+
+Each matrix job ends with a step that:
+
+```bash
+cd samples-<lang>/${{ matrix.app.path }}
+source $GITHUB_WORKSPACE/.github/workflows/test_workflow_scripts/<lang>/${{ matrix.app.script_dir }}/<lang>-linux.sh
+```
+
+The script receives `RECORD_BIN` and `REPLAY_BIN` in the environment, set by
+the `./.github/actions/download-binary` composite action.
+
+### Sample test script anatomy
+
+All of them:
+
+1. `source $GITHUB_WORKSPACE/.github/workflows/test_workflow_scripts/test-iid.sh` — writes a fake `~/.keploy/installation-id.yaml` so telemetry init doesn't prompt.
+2. Clean `keploy/` and `keploy.yml` from any prior run.
+3. `$RECORD_BIN config --generate` and optionally `sed` noise rules into `keploy.yml` (e.g. `global: {"body": {"updated_at":[]}}`).
+4. Bring up any dependency containers (MySQL, Postgres, Mongo, Redis) and wait for readiness.
+5. Build the sample app (`go build`, `mvn package`, `npm ci`, `pip install`, …).
+6. Define `send_request()` — waits for app health, drives traffic, sleeps, kills keploy by PID (`pgrep keploy`).
+7. Run **record** once or twice in the background with `tee`, then grep the log for `"ERROR"` and `"WARNING: DATA RACE"` (both are fatal).
+8. Optionally stop the DB containers before replay (forces Keploy to use mocks — catches "mock missed" regressions).
+9. Run **replay**: `"$REPLAY_BIN" test -c "./app" --delay N --generateGithubActions=false 2>&1 | tee test_logs.txt`.
+10. Walk `./keploy/reports/test-run-*/test-set-*-report.yaml` (newest via `ls -1dt ... | head -n1`), grep each for `status:`, fail if any aren't `PASSED`.
+11. Exit 0 on success, 1 on any failure.
+
+You can add your own way if you are confident about it. 
+
+### Sample repos CI pulls from
+
+| CI workflow                                                                                                     | Sample repo                    | Where samples live          |
+| --------------------------------------------------------------------------------------------------------------- | ------------------------------ | --------------------------- |
+| `golang_linux.yml`, `golang_docker.yml`, `golang_wsl.yml`, `grpc_linux.yml`, `schema_match_linux.yml` (go side) | `keploy/samples-go`            | `samples-go/<path>`         |
+| `python_linux.yml`, `python_docker.yml`, `schema_match_linux.yml` (python side)                                 | `keploy/samples-python`        | `samples-python/<path>`     |
+| `node_linux.yml`, `node_docker.yml`, `node_mapping.yml`                                                         | `keploy/samples-typescript`    | `samples-typescript/<path>` |
+| `java_linux.yml`                                                                                                | `keploy/samples-java`          | `samples-java/<path>`       |
+
+
+## Where to look first for common changes
+
+| If you're changing...                | Start here                                                                                                                              |
+| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
+| Record/replay behavior of a protocol | `pkg/core/proxy/` + `pkg/models/<protocol>`                                                                                             |
+| Mock matching logic                  | `pkg/matcher/` + `pkg/service/replay/`                                                                                                  |
+| On-disk YAML format                  | `pkg/platform/yaml/` + `pkg/models/mock.go`, `testcase.go`                                                                              |
+| CLI flags                            | `cli/<command>.go` + `cli/provider/`                                                                                                    |
+| Config defaults                      | `config/default.go` + `config/config.go`                                                                                                |
+| Test reports                         | `pkg/service/report/`                                                                                                                   |
+| Coverage                             | `pkg/platform/coverage/`                                                                                                                |
+| eBPF probe behavior                  | `pkg/agent/hooks/` (C sources — do not edit generated Go)                                                                               |
+| Adding a sample to CI                | a sample repo (`samples-go`, …) + `.github/workflows/test_workflow_scripts/<lang>/<script_dir>/` + a matrix entry in the right workflow |
+
+When adding end-to-end coverage for a behavior change, prefer extending an
+existing sample + its script over creating a new one. See the
+`keploy-e2e-test` skill for the full decision tree.
PATCH

echo "Gold patch applied."
