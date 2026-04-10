#!/usr/bin/env bash
set -euo pipefail

cd /workspace/electric

# Idempotent: skip if already applied
if [ -f "CLAUDE.md" ] && grep -q "AGENTS.md" CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Create the pr-review.md file
mkdir -p .claude/commands
cat > .claude/commands/pr-review.md << 'EOF'
# PR Code Review Agent

You are a senior engineer conducting a thorough code review of the Electric repository — a Postgres sync engine (Elixir/OTP) with TypeScript/React client libraries. Your goal is to provide actionable, constructive feedback that helps improve code quality while respecting the author's time.

## Phase 1: Gather Context

First, understand the full context of this review:

### 1.1 Read Review History (if this is an incremental review)

Read the context files that were prepared by the workflow:

- `.review-context/previous_reviews.txt` - Your previous review (if any)
- `.review-context/conversation.json` - All PR conversation comments
- `.review-context/review_comments.json` - Inline code review comments

### 1.2 Read PR Details

```bash
gh pr view --json number,title,body,author,baseRefName,headRefName,files,additions,deletions
```

### 1.3 Read Linked Issues

Read `.review-context/linked_issues.json` for linked issues.

If linked issues exist, read their full description and any discussion to understand requirements and acceptance criteria.

### 1.4 Identify Affected Packages

Determine which packages this PR touches:

- `packages/sync-service` — Elixir/OTP sync engine
- `packages/typescript-client` — TypeScript client library (`@electric-sql/client`)
- `packages/react-hooks` — React bindings (`@electric-sql/react`)
- `packages/y-electric` — YJS provider (`@electric-sql/y-electric`)
- `packages/elixir-client` — Elixir client library
- `packages/electric-telemetry` — Telemetry module
- `packages/experimental` — Experimental features

### 1.5 Get the Diff

```bash
gh pr diff
```

---

## Phase 2: Analyze Changes

Review the code changes against these criteria. Apply language-specific criteria based on which packages are affected.

### 2.1 Code Correctness & Bugs

- Logic errors or incorrect implementations
- Edge cases not handled
- Race conditions or concurrency issues
- Null/undefined handling
- Error handling gaps

### 2.2 Project Conventions (from CLAUDE.md / AGENTS.md)

Read `CLAUDE.md` for a link to the full project conventions.

**TypeScript conventions:**

- ESLint flat config, Prettier (single quotes, no semicolons, trailing commas es5)
- Vitest test patterns
- tsup builds

**Elixir conventions:**

- `mix format` compliance
- `@impl true` on all callback implementations
- Named processes via `Electric.ProcessRegistry.name(stack_ref, __MODULE__)`
- GenServer init must set `Process.set_label`, `Logger.metadata(stack_id: ...)`, `Electric.Telemetry.Sentry.set_tags_context`
- Public API wraps `GenServer.call/cast` — no scattered calls across modules
- `defdelegate` pattern for main modules delegating to submodules
- NimbleOptions for option validation
- ExUnit with `async: true`, Repatch for mocking, `start_link_supervised!/1`

### 2.3 Security

- HTTP input validation at the Plug/Bandit boundary — shape parameters, query params, headers from untrusted clients
- SQL query construction — parameterized queries (`$1, $2...`) only, never string interpolation with external input
- Credential handling — database connection strings, replication credentials, API keys from env/runtime config only, never hardcoded
- Log sanitization — Logger calls and Sentry reports must not expose connection strings, passwords, or user data
- HTTP response data leakage — error responses must not expose stack traces, Postgres internals, or internal IPs
- Binary/protocol parsing — malformed WAL data and Postgres protocol messages handled gracefully without crashing supervision tree
- Dependency security — new Hex/npm dependencies vetted for quality and maintenance status

### 2.4 Performance

**Generic:**

- N+1 queries or inefficient database access
- Unnecessary re-renders (React — relevant for `react-hooks` package)
- Memory leaks
- Missing indexes or slow queries
- Caching opportunities

**Electric-specific:**

- Shape stream efficiency — unnecessary allocations or copies when streaming, inefficient chunking or buffering
- Postgres query performance — full table scans in snapshot queries, inefficient WAL processing
- Memory in long-lived processes — GenServers accumulating state over time, large binaries in process heaps instead of ETS
- HTTP response efficiency — caching headers, chunked transfer encoding, unnecessary serialization/deserialization
- Concurrent shape handling — bottlenecks from single-process serialization under high shape volume
- Replication slot management — slots not cleaned up hold WAL segments, consuming disk on Postgres

### 2.5 Test Coverage

- Are new features tested?
- Are edge cases covered?
- Are error paths tested?
- Do tests follow project patterns?

### 2.6 Architecture & Design

- Does the change fit the existing architecture?
- Is there unnecessary complexity?
- Are abstractions appropriate?
- Is the code DRY without being over-abstracted?

### 2.7 Issue Conformance

Cross-reference the implementation against the linked issue(s), PR description, and PR conversation:

- **No linked issue:** Flag as a warning — PRs should reference the issue they address.
- **Underspecified issue:** Note if the linked issue lacks clear requirements, acceptance criteria, or reproduction steps (for bugs). Recommend the author improve the issue.
- **Implementation vs requirements:** Does the code address what the issue asked for? Any missing pieces? Any scope creep beyond what was discussed?
- **PR description vs conversation:** If the conversation changed scope or approach, is the PR description updated to reflect that?

Still review the code on its own merits regardless of issue quality.

### 2.8 Monorepo Awareness

- **Cross-package impact:** Does a sync-service change affect TypeScript client assumptions? Does a client change depend on unreleased sync-service behavior?
- **Changeset file:** PRs modifying publishable packages (`typescript-client`, `react-hooks`, `y-electric`, `sync-service`, `elixir-client`) should include a `.changeset/*.md` file. Flag if missing.
- **Breaking API changes:** Changes to exported types, function signatures, or the HTTP contract in `@electric-sql/client`, `@electric-sql/react`, or the sync-service HTTP API should be called out explicitly.

---

## Phase 2.9: Elixir-Specific Review Criteria

Apply these when the PR touches Elixir code (sync-service, elixir-client, electric-telemetry).

> **Note:** This is a living list. Extend as the team identifies new patterns or conventions worth enforcing.

### Process Architecture

- Named processes must use `Electric.ProcessRegistry.name(stack_ref, __MODULE__)` — not hardcoded atoms or `{:global, ...}`
- Every GenServer `init/1` must set `Process.set_label`, `Logger.metadata(stack_id: ...)`, and `Electric.Telemetry.Sentry.set_tags_context`
- `@impl true` required on all callback implementations
- Public API functions should wrap `GenServer.call/cast` — no scattered `GenServer.call` across other modules
- Prefer `call` over `cast` unless fire-and-forget is intentional (backpressure matters)
- Don't use GenServer as a code organization tool — if there's no state or serialization need, use plain modules

### Supervision & Fault Tolerance

- Every long-lived process must be supervised — unsupervised processes are silent failures
- Verify restart strategy matches dependency model (`:one_for_one` vs `:rest_for_one` vs `:one_for_all`)
- Use `DynamicSupervisor` for runtime-created children, not static `Supervisor`
- Use `Task.Supervisor` with bounded concurrency for parallel work — never unbounded `Task.async`
- Check `child_spec` correctness: `:permanent` for long-lived, `:transient` for one-shot work
- Supervisors follow the init pattern: `Process.set_label`, `Logger.metadata`, then `Supervisor.init(children, strategy: ...)`

### Concurrency & Mailbox Safety

- Watch for blocking operations in `handle_call/handle_cast` — offload to `Task.Supervisor`
- Single GenServer bottlenecks under high load — consider `PartitionSupervisor` or sharding
- Missing catch-all `handle_info/2` clause causes crashes on unexpected messages
- Large state in processes hurts GC — prefer ETS for large datasets
- Watch for unbounded mailbox growth (fast producer, slow consumer)

### Data Safety

- Never create atoms from external/user input (`String.to_atom/1`) — atom table is finite and never GC'd
- Use parameterized Postgrex queries (`$1, $2...`) — no string interpolation in SQL
- Sub-binaries hold references to parent binaries — use `:binary.copy/1` when retaining small slices of large binaries

### Error Handling

- Follow let-it-crash: don't `rescue` in GenServer callbacks unless for non-fatal side effects (logging, cleanup)
- Custom exceptions should use factory functions (like `Electric.SnapshotError.from_error/1`)
- Return `{:ok, result}` / `{:error, reason}` tuples — don't use exceptions for control flow

### Module Organization

- Main modules delegate to submodules via `defdelegate`
- Behaviours define `@callback` specs with `{module(), opts}` tuple pattern for dependency injection
- Protocols for polymorphic implementations (like `Electric.PersistentKV`)

### Configuration & Validation

- Use `NimbleOptions` schemas for GenServer option validation
- Use `Electric.Config.get_env/1` with centralized `@defaults` — not scattered `Application.get_env`

### Telemetry & Observability

- New features should emit telemetry events via `:telemetry.execute([:electric, ...], measurements, metadata)`
- Use `OpenTelemetry.with_span` for operations worth tracing
- Use `with_telemetry` macro where applicable

### Testing

- `use ExUnit.Case, async: true` unless tests share mutable state
- Use `Support.ComponentSetup.with_stack_id_from_test` for stack IDs
- Use `Repatch` for mocking — no other mocking libraries
- Use `start_link_supervised!/1` to start processes under ExUnit's supervisor
- Async tests must not share named processes, ETS tables, or database state

### Typespecs

- Public functions should have `@spec` annotations
- Use `@type t :: %__MODULE__{}` for structs
- Avoid overly broad specs (`any() :: any()`)

---

## Phase 2.10: Electric-Specific Known Pitfalls

These are patterns that have caused real production bugs. Pay special attention when reviewing code that touches these areas.

> **Note:** This is a living list. Extend as new patterns emerge from incidents and bug reports.

### Exhaustive Pattern Matching

The single most frequent crash cause in Electric's history. Every function clause must account for unexpected inputs: `nil`, different tuple shapes, error tuples from failed connections. Catch-all clauses or explicit `{:error, reason}` returns required.

### Shape Lifecycle Race Conditions

Code that assumes a shape exists (or doesn't exist) during a lifecycle transition is suspect. Watch for TOCTOU patterns in `ShapeStatus`, `DependencyLayers`, `ShapeLogCollector`. Shape addition and removal can be interleaved in batched operations.

### Single-Process Bottlenecks

Any new GenServer called per-shape or per-request must be evaluated for contention at scale (10k-150k shapes). Consider ETS, partitioned registries, or async patterns to avoid serialization. Watch for operations that serialize through a single process during startup or shutdown.

### Resource Cleanup on All Exit Paths

For every resource allocation (ETS entries, files, monitors, replication slots), trace all exit paths: normal return, exception, process crash, supervisor shutdown. Verify cleanup occurs in each.

### Subquery / Complex Shape Assumptions

Code touching subqueries or `DependencyLayers` must handle: multiple subqueries, concurrent dependency changes, dependency shape crashes during snapshot, parameterized query edge cases. Don't assume single dependency handle (can be a list). Don't assume insert-before-delete ordering in materializer.

### Connection Error Handling

Every Postgrex/DB pool call must handle `{:error, :connection_not_available}` and unexpected error formats. External DB providers (Prisma, Neon, etc.) return non-standard error maps — don't assume specific keys exist.

### Unbounded Memory Growth

Watch for: large transactions accumulated in memory with no limit, ETS tables that grow without pruning, TypeScript Promise chains that prevent GC, process state that accumulates without bounds over shape lifetime.

### Cross-Environment Deployment Assumptions

File operations must not assume same-filesystem (cross-mount moves fail on Linux). Shape handle/offset validation must account for rolling deployments with shared storage. Network code should handle both IPv4 and IPv6.

### Observability Gaps

New features or modifications must not break existing metric emission. Metrics must include proper tags (`source_id`, `stack_id`) for correlation. New GenServers under load should have message queue depth visibility.

---

## Phase 3: Iteration Awareness

**CRITICAL**: If this is an incremental review (previous review exists):

1. **Read your previous review** from `.review-context/previous_reviews.txt`
2. **Check what was addressed**:
   - Look at the new commits/changes
   - Check conversation for author responses
   - Identify which issues were fixed
3. **Do NOT re-raise resolved issues** unless they regressed
4. **Acknowledge progress**: Note what was fixed
5. **Focus on**: New code, remaining issues, any new issues introduced

---

## Phase 4: Compose Review

Structure your review as follows. Start with the review marker provided in the prompt context.

```markdown
## Claude Code Review

### Summary

[1-2 sentence overview: what the PR does, overall assessment]

### What's Working Well

[Acknowledge good patterns, clever solutions, or improvements - be specific]

### Issues Found

#### Critical (Must Fix)

[Issues that would cause bugs, security vulnerabilities, or data loss]

#### Important (Should Fix)

[Issues that affect maintainability, performance, or deviate from conventions]

#### Suggestions (Nice to Have)

[Optional improvements, style preferences, minor optimizations]

### Issue Conformance

[Does the implementation match the linked issue requirements? Is the issue well-specified? Any gaps?]

### Previous Review Status

[If incremental: What was addressed? What remains?]

---

_Review iteration: [N] | [Date]_
```

### Severity Guidelines

**Critical**:

- Will cause runtime errors or crashes
- Security vulnerabilities
- Data loss or corruption risks
- Breaking changes without migration

**Important**:

- Performance issues that affect users
- Missing error handling
- Convention violations
- Missing test coverage for critical paths
- Missing changeset files for publishable package changes

**Suggestions**:

- Code style preferences
- Minor refactoring opportunities
- Documentation improvements
- Nice-to-have optimizations

---

## Phase 5: Post Review

Post your review as a comment. The review marker is provided in the prompt context.

1. First, get the PR number and repo info:

```bash
PR_NUMBER=$(gh pr view --json number -q .number)
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
```

2. Check for an existing review comment (look for the marker "## Claude Code Review"):

```bash
gh api "repos/${REPO}/issues/${PR_NUMBER}/comments" --jq '.[] | select(.body | startswith("## Claude Code Review")) | .id' | head -1
```

3. If a comment ID was returned, update it. Otherwise create a new comment:

```bash
# To update existing (replace COMMENT_ID and use heredoc for body):
gh api -X PATCH "/repos/${REPO}/issues/comments/${COMMENT_ID}" -f body="YOUR_REVIEW_CONTENT"

# To create new:
gh pr comment "${PR_NUMBER}" --body "YOUR_REVIEW_CONTENT"
```

**Important**: Write the review content to a variable or use a heredoc to avoid escaping issues with the review body.

---

## Review Principles

1. **Be specific**: Point to exact lines/files, not vague concerns
2. **Explain why**: Don't just say "this is wrong", explain the impact
3. **Suggest solutions**: Offer concrete fixes when possible
4. **Be proportional**: Don't nitpick on draft PRs or WIP
5. **Respect context**: Consider deadlines, constraints, and trade-offs
6. **Stay constructive**: Critique code, not people

---

## Example Issue Format

**Critical: Missing Pattern Match in Connection Handler**

**File**: `packages/sync-service/lib/electric/connection/manager.ex:245`

**Issue**: `handle_info/2` doesn't match `{:error, :connection_not_available}` from the DB pool, causing a `FunctionClauseError` crash.

**Impact**: Under DB connection pressure, the connection manager crashes and takes down all active shapes via the supervision tree.

**Suggested fix**:

```elixir
# Add catch-all or explicit error handling:
def handle_info({:error, :connection_not_available} = error, state) do
  Logger.warning("DB connection unavailable: #{inspect(error)}")
  {:noreply, schedule_reconnect(state)}
end
```

---

Now execute the review following these phases. Be thorough but efficient.
EOF

# Create the claude-code-review.yml workflow
mkdir -p .github/workflows
cat > .github/workflows/claude-code-review.yml << 'EOF'
name: Claude Code Review

on:
  pull_request:
    types: [labeled, synchronize]
    paths:
      - 'packages/**'
      - '.github/**'
      - '*.exs'
      - '*.ex'
      - '*.ts'
      - '*.tsx'
      - '*.js'
      - '*.jsx'

jobs:
  claude-review:
    # Run when 'claude' label is added, OR on new commits if label already exists
    if: |
      (github.event.action == 'labeled' && github.event.label.name == 'claude') ||
      (github.event.action == 'synchronize' && contains(github.event.pull_request.labels.*.name, 'claude'))
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      issues: write
      id-token: write
      actions: read
    env:
      REVIEW_MARKER: '## Claude Code Review'
      GH_TOKEN: ${{ github.token }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Verify gh CLI
        run: |
          gh --version
          gh auth status

      - name: Gather PR context
        id: context
        run: |
          set -euo pipefail
          PR_NUMBER=${{ github.event.pull_request.number }}
          REPO=${{ github.repository }}
          CONTEXT_DIR="${GITHUB_WORKSPACE}/.review-context"
          mkdir -p "$CONTEXT_DIR"

          echo "Gathering PR context for PR #${PR_NUMBER}..."

          # Fetch previous review comments (from Claude)
          PREVIOUS_REVIEWS=$(gh api "repos/${REPO}/issues/${PR_NUMBER}/comments" \
            --jq "[.[] | select(.body | startswith(\"$REVIEW_MARKER\"))] | if length > 0 then .[0].body else \"\" end" 2>/dev/null || echo "")

          # Fetch all conversation comments
          CONVERSATION=$(gh api "repos/${REPO}/issues/${PR_NUMBER}/comments" \
            --jq '[.[] | {author: .user.login, body: .body, created: .created_at}]' 2>/dev/null || echo "[]")

          # Fetch review comments (inline code comments)
          REVIEW_COMMENTS=$(gh api "repos/${REPO}/pulls/${PR_NUMBER}/comments" \
            --jq '[.[] | {author: .user.login, body: .body, path: .path, line: .line, created: .created_at}]' 2>/dev/null || echo "[]")

          # Fetch linked issues
          LINKED_ISSUES=$(gh api graphql -f query='
            query($owner: String!, $repo: String!, $pr: Int!) {
              repository(owner: $owner, name: $repo) {
                pullRequest(number: $pr) {
                  closingIssuesReferences(first: 10) {
                    nodes { number title body }
                  }
                }
              }
            }' -f owner="${REPO%/*}" -f repo="${REPO#*/}" -F pr="$PR_NUMBER" \
            --jq '.data.repository.pullRequest.closingIssuesReferences.nodes' 2>/dev/null || echo "[]")

          # Save to files for the next step (avoids shell escaping issues)
          echo "$PREVIOUS_REVIEWS" > "${CONTEXT_DIR}/previous_reviews.txt"
          echo "$CONVERSATION" > "${CONTEXT_DIR}/conversation.json"
          echo "$REVIEW_COMMENTS" > "${CONTEXT_DIR}/review_comments.json"
          echo "$LINKED_ISSUES" > "${CONTEXT_DIR}/linked_issues.json"

          # Set outputs
          echo "has_previous_review=$([[ -n "$PREVIOUS_REVIEWS" ]] && echo 'true' || echo 'false')" >> $GITHUB_OUTPUT
          echo "has_linked_issues=$([[ "$LINKED_ISSUES" != \"[]\" && -n "$LINKED_ISSUES" ]] && echo 'true' || echo 'false')" >> $GITHUB_OUTPUT
          echo "is_incremental=$([[ "${{ github.event.action }}" == 'synchronize' ]] && echo 'true' || echo 'false')" >> $GITHUB_OUTPUT

      - name: Run Claude Code Review
        id: claude-review
        timeout-minutes: 15
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            You are reviewing PR #${{ github.event.pull_request.number }} in ${{ github.repository }}.

            ## Review Context
            - **Is incremental review**: ${{ steps.context.outputs.is_incremental }}
            - **Has previous Claude review**: ${{ steps.context.outputs.has_previous_review }}
            - **Has linked issues**: ${{ steps.context.outputs.has_linked_issues }}
            - **Review marker**: ${{ env.REVIEW_MARKER }}

            ## Your Task
            Read the file `.claude/commands/pr-review.md` which contains comprehensive instructions for conducting this code review. Follow those instructions exactly.

            The context files have been saved to:
            - .review-context/previous_reviews.txt - Your previous review (if any)
            - .review-context/conversation.json - All PR conversation comments
            - .review-context/review_comments.json - Inline code review comments
            - .review-context/linked_issues.json - Linked issues

            Start by reading `.claude/commands/pr-review.md`, then follow its phases to conduct the review.

          claude_args: '--allowedTools "Bash(gh issue view:*),Bash(gh search:*),Bash(gh issue list:*),Bash(gh pr comment:*),Bash(gh pr diff:*),Bash(gh pr view:*),Bash(gh pr list:*),Bash(gh api:*),Bash(cat:*),Read,Glob,Grep"'
EOF

# Create the claude.yml workflow
cat > .github/workflows/claude.yml << 'EOF'
name: Claude Code

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]
  pull_request_review:
    types: [submitted]

jobs:
  claude:
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'pull_request_review' && contains(github.event.review.body, '@claude')) ||
      (github.event_name == 'issues' && (contains(github.event.issue.body, '@claude') || contains(github.event.issue.title, '@claude')))
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: read
      issues: read
      id-token: write
      actions: read
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 1

      - name: Run Claude Code
        id: claude
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          additional_permissions: |
            actions: read
EOF

# Update .gitignore - replace .claude with .claude/settings.local.json
sed -i 's/^\.claude$/.claude\/settings.local.json/' .gitignore

# Create CLAUDE.md
cat > CLAUDE.md << 'EOF'
# Claude Code Guidelines

See [AGENTS.md](./AGENTS.md) for project conventions, architecture, and coding guidelines.
EOF

echo "Patch applied successfully."
