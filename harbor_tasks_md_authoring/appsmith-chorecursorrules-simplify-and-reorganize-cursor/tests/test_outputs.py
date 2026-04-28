"""Behavioral checks for appsmith-chorecursorrules-simplify-and-reorganize-cursor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/appsmith")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/agent-behavior.mdc')
    assert "- **No Trigger Happy**: Don't start write actions and long plans without confirming intent from user explicitly" in text, "expected to find: " + "- **No Trigger Happy**: Don't start write actions and long plans without confirming intent from user explicitly"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/agent-behavior.mdc')
    assert 'description: Agent workflow orchestration, task management, and core principles for all interactions' in text, "expected to find: " + 'description: Agent workflow orchestration, task management, and core principles for all interactions'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/agent-behavior.mdc')
    assert "- **Minimat Impact**: Changes should only touch what's necessary. Avoid introducing bugs." in text, "expected to find: " + "- **Minimat Impact**: Changes should only touch what's necessary. Avoid introducing bugs."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend.mdc')
    assert '`controllers/`, `services/`, `domains/`, `repositories/`, `dtos/`, `configurations/`, `git/`, `authentication/`, `exports/`, `imports/`, `workflows/`, `modules/`, `migrations/`' in text, "expected to find: " + '`controllers/`, `services/`, `domains/`, `repositories/`, `dtos/`, `configurations/`, `git/`, `authentication/`, `exports/`, `imports/`, `workflows/`, `modules/`, `migrations/`'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend.mdc')
    assert '| `appsmith-plugins` | ~28 datasource plugins (Postgres, Mongo, MySQL, REST API, GraphQL, S3, Snowflake, Redis, Oracle, Google Sheets, OpenAI, Anthropic, etc.) |' in text, "expected to find: " + '| `appsmith-plugins` | ~28 datasource plugins (Postgres, Mongo, MySQL, REST API, GraphQL, S3, Snowflake, Redis, Oracle, Google Sheets, OpenAI, Anthropic, etc.) |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/backend.mdc')
    assert 'Community and enterprise code coexist. Look for `ce/` and `ee/` sub-packages within each module. Enterprise logic extends or overrides CE implementations.' in text, "expected to find: " + 'Community and enterprise code coexist. Look for `ce/` and `ee/` sub-packages within each module. Enterprise logic extends or overrides CE implementations.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/commit/semantic-pr-validator.mdc')
    assert 'PR titles must follow [Conventional Commits](https://www.conventionalcommits.org/). Enforced by the `semantic-prs` GitHub app (config: `.github/semantic.yml`, `titleOnly: true` — only the PR title is ' in text, "expected to find: " + 'PR titles must follow [Conventional Commits](https://www.conventionalcommits.org/). Enforced by the `semantic-prs` GitHub app (config: `.github/semantic.yml`, `titleOnly: true` — only the PR title is '[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/commit/semantic-pr-validator.mdc')
    assert 'The PR description follows the template in `.github/pull_request_template.md`. When generating a PR description, gather all needed information **in a single prompt** — do not ask the user multiple tim' in text, "expected to find: " + 'The PR description follows the template in `.github/pull_request_template.md`. When generating a PR description, gather all needed information **in a single prompt** — do not ask the user multiple tim'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/commit/semantic-pr-validator.mdc')
    assert 'If the user has already provided this info (e.g., in the conversation or task description), or has explicitly said to skip it, do not ask again.' in text, "expected to find: " + 'If the user has already provided this info (e.g., in the conversation or task description), or has explicitly said to skip it, do not ask again.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/commit/semantic-pr.md')
    assert '.cursor/rules/commit/semantic-pr.md' in text, "expected to find: " + '.cursor/rules/commit/semantic-pr.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend.mdc')
    assert '`pages/`, `widgets/`, `sagas/`, `reducers/`, `actions/`, `selectors/`, `components/`, `IDE/`, `git/`, `layoutSystems/`, `plugins/`, `ce/`, `ee/`, `enterprise/`' in text, "expected to find: " + '`pages/`, `widgets/`, `sagas/`, `reducers/`, `actions/`, `selectors/`, `components/`, `IDE/`, `git/`, `layoutSystems/`, `plugins/`, `ce/`, `ee/`, `enterprise/`'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend.mdc')
    assert 'Look for `ce/`, `ee/`, and `enterprise/` directories under `src/`. Enterprise logic extends or overrides CE implementations.' in text, "expected to find: " + 'Look for `ce/`, `ee/`, and `enterprise/` directories under `src/`. Enterprise logic extends or overrides CE implementations.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/frontend.mdc')
    assert 'description: React frontend — TypeScript SPA, monorepo packages, Redux-Saga, key directories, testing, and build commands' in text, "expected to find: " + 'description: React frontend — TypeScript SPA, monorepo packages, Redux-Saga, key directories, testing, and build commands'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/index.md')
    assert '.cursor/rules/index.md' in text, "expected to find: " + '.cursor/rules/index.md'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/index.mdc')
    assert 'Enterprise and community edition code coexist in the same repo. Look for `ce/` and `ee/` directories within both `app/server` and `app/client`. Enterprise-specific logic extends or overrides CE implem' in text, "expected to find: " + 'Enterprise and community edition code coexist in the same repo. Look for `ce/` and `ee/` directories within both `app/server` and `app/client`. Enterprise-specific logic extends or overrides CE implem'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/index.mdc')
    assert '- **RTS** (`app/client/packages/rts/`) — Node.js Express real-time server, SCIM, workflow proxy' in text, "expected to find: " + '- **RTS** (`app/client/packages/rts/`) — Node.js Express real-time server, SCIM, workflow proxy'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/index.mdc')
    assert '- **Server** (`app/server/`) — Java 17, Spring Boot 3.x (Reactive WebFlux), Maven, MongoDB' in text, "expected to find: " + '- **Server** (`app/server/`) — Java 17, Spring Boot 3.x (Reactive WebFlux), Maven, MongoDB'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/infra.mdc')
    assert 'Key scripts: `deploy_preview.sh`, `build_dp_from_branch.sh`, `cleanup_dp.sh`, `health_check.sh`, `generate_info_json.sh`, `prepare_server_artifacts.sh`, `local_testing.sh`' in text, "expected to find: " + 'Key scripts: `deploy_preview.sh`, `build_dp_from_branch.sh`, `cleanup_dp.sh`, `health_check.sh`, `generate_info_json.sh`, `prepare_server_artifacts.sh`, `local_testing.sh`'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/infra.mdc')
    assert '**Caddy (reverse proxy):** Config in `deploy/docker/fs/opt/appsmith/`. `caddy-reconfigure.mjs` generates Caddyfile from env vars. `run-caddy.sh` starts Caddy.' in text, "expected to find: " + '**Caddy (reverse proxy):** Config in `deploy/docker/fs/opt/appsmith/`. `caddy-reconfigure.mjs` generates Caddyfile from env vars. `run-caddy.sh` starts Caddy.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/infra.mdc')
    assert 'Setup guides (`ClientSetup.md`, `ServerSetup.md`), contribution guidelines, widget development guide, custom JS library docs.' in text, "expected to find: " + 'Setup guides (`ClientSetup.md`, `ServerSetup.md`), contribution guidelines, widget development guide, custom JS library docs.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/quality/performance-optimizer.mdc')
    assert '- Minimize expensive properties in frequently repainted elements (box-shadow, border-radius, filter)' in text, "expected to find: " + '- Minimize expensive properties in frequently repainted elements (box-shadow, border-radius, filter)'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/quality/performance-optimizer.mdc')
    assert 'description: Performance anti-patterns to watch for in JS/TS, Java, and CSS code reviews' in text, "expected to find: " + 'description: Performance anti-patterns to watch for in JS/TS, Java, and CSS code reviews'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/quality/performance-optimizer.mdc')
    assert '- Choose collections by access pattern: `ArrayList` for sequential, `HashMap` for lookup' in text, "expected to find: " + '- Choose collections by access pattern: `ArrayList` for sequential, `HashMap` for lookup'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/quality/pre-commit-checks.mdc')
    assert '.cursor/rules/quality/pre-commit-checks.mdc' in text, "expected to find: " + '.cursor/rules/quality/pre-commit-checks.mdc'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/task-list.mdc')
    assert '.cursor/rules/task-list.mdc' in text, "expected to find: " + '.cursor/rules/task-list.mdc'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing/test-generator.mdc')
    assert 'description: Test conventions and examples for frontend (Jest/Cypress) and backend (JUnit) — file naming, frameworks, and patterns' in text, "expected to find: " + 'description: Test conventions and examples for frontend (Jest/Cypress) and backend (JUnit) — file naming, frameworks, and patterns'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing/test-generator.mdc')
    assert '- **Frontend unit:** `ComponentName.test.tsx` (colocated with source)' in text, "expected to find: " + '- **Frontend unit:** `ComponentName.test.tsx` (colocated with source)'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/testing/test-generator.mdc')
    assert 'import { render, screen, fireEvent } from "@testing-library/react";' in text, "expected to find: " + 'import { render, screen, fireEvent } from "@testing-library/react";'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/verification/bug-fix-verifier.mdc')
    assert 'description: Bug fix quality checklist — reproduction, root cause analysis, testing, and regression prevention' in text, "expected to find: " + 'description: Bug fix quality checklist — reproduction, root cause analysis, testing, and regression prevention'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/verification/bug-fix-verifier.mdc')
    assert '- Use optional chaining or lodash/get for nested property access' in text, "expected to find: " + '- Use optional chaining or lodash/get for nested property access'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/verification/bug-fix-verifier.mdc')
    assert '- Write a failing test that demonstrates the bug before fixing' in text, "expected to find: " + '- Write a failing test that demonstrates the bug before fixing'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/verification/feature-implementation-validator.mdc')
    assert '.cursor/rules/verification/feature-implementation-validator.mdc' in text, "expected to find: " + '.cursor/rules/verification/feature-implementation-validator.mdc'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/verification/feature-verifier.mdc')
    assert 'description: Feature implementation checklist — requirements, code quality, testing, and documentation standards' in text, "expected to find: " + 'description: Feature implementation checklist — requirements, code quality, testing, and documentation standards'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/verification/feature-verifier.mdc')
    assert '- Controllers should not access repositories directly — use services' in text, "expected to find: " + '- Controllers should not access repositories directly — use services'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/verification/feature-verifier.mdc')
    assert '- Follow project coding standards and architecture (CE/EE patterns)' in text, "expected to find: " + '- Follow project coding standards and architecture (CE/EE patterns)'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/verification/workflow-validator.mdc')
    assert '- Using deprecated action versions (prefer `@v4` for checkout, setup-node, etc.)' in text, "expected to find: " + '- Using deprecated action versions (prefer `@v4` for checkout, setup-node, etc.)'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/verification/workflow-validator.mdc')
    assert '- Missing `permissions` block when workflow needs write access' in text, "expected to find: " + '- Missing `permissions` block when workflow needs write access'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/verification/workflow-validator.mdc')
    assert '- `on` — trigger configuration (push, pull_request, etc.)' in text, "expected to find: " + '- `on` — trigger configuration (push, pull_request, etc.)'[:80]

