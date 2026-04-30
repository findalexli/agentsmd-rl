"""Behavioral checks for linea-attestation-registry-docglobal-add-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/linea-attestation-registry")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/00-operating-model.mdc')
    assert 'Cursor is strictly forbidden from committing, pushing, rebasing, merging, force pushing, tagging, or modifying Git history.' in text, "expected to find: " + 'Cursor is strictly forbidden from committing, pushing, rebasing, merging, force pushing, tagging, or modifying Git history.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/00-operating-model.mdc')
    assert 'Prioritize must (blocking) vs should (recommended) based on context (e.g., chores may waive non critical items).' in text, "expected to find: " + 'Prioritize must (blocking) vs should (recommended) based on context (e.g., chores may waive non critical items).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/00-operating-model.mdc')
    assert 'All items are mandatory unless explicitly waived with justification (tracked in ticket comments or scratchpad):' in text, "expected to find: " + 'All items are mandatory unless explicitly waived with justification (tracked in ticket comments or scratchpad):'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/01-principles.mdc')
    assert 'Apply 12 Factor App: config via env, stateless processes, concurrency, disposability.' in text, "expected to find: " + 'Apply 12 Factor App: config via env, stateless processes, concurrency, disposability.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/01-principles.mdc')
    assert 'Distinguish must (mandatory, blocking) vs should (recommended) in all rules.' in text, "expected to find: " + 'Distinguish must (mandatory, blocking) vs should (recommended) in all rules.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/01-principles.mdc')
    assert 'Error handling must be robust, predictable, with graceful degradation.' in text, "expected to find: " + 'Error handling must be robust, predictable, with graceful degradation.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/02-reliability.mdc')
    assert 'Idempotency for writes, payments, duplicates harmful endpoints (exactly once or at least once semantics documented).' in text, "expected to find: " + 'Idempotency for writes, payments, duplicates harmful endpoints (exactly once or at least once semantics documented).'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/02-reliability.mdc')
    assert 'Jobs and background tasks must be idempotent, retry safe, observable with progress, resumable.' in text, "expected to find: " + 'Jobs and background tasks must be idempotent, retry safe, observable with progress, resumable.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/02-reliability.mdc')
    assert 'Nonce based replay protection and explicit expiry mandatory for signatures and attestations.' in text, "expected to find: " + 'Nonce based replay protection and explicit expiry mandatory for signatures and attestations.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/05-security.mdc')
    assert 'Never trust client supplied identifiers, roles, addresses, chain state, or feature flags.' in text, "expected to find: " + 'Never trust client supplied identifiers, roles, addresses, chain state, or feature flags.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/05-security.mdc')
    assert 'Reason explicitly about auth bypass, token leakage, session fixation, misconfiguration.' in text, "expected to find: " + 'Reason explicitly about auth bypass, token leakage, session fixation, misconfiguration.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/05-security.mdc')
    assert 'Never log secrets, tokens, private keys, raw signatures, or sensitive payloads.' in text, "expected to find: " + 'Never log secrets, tokens, private keys, raw signatures, or sensitive payloads.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/10-solidity.mdc')
    assert 'description: Solidity security, upgradeability, gas, and testing' in text, "expected to find: " + 'description: Solidity security, upgradeability, gas, and testing'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/10-solidity.mdc')
    assert 'Foundry preferred, Hardhat tolerated with justification' in text, "expected to find: " + 'Foundry preferred, Hardhat tolerated with justification'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/10-solidity.mdc')
    assert 'Reentrancy protection or checks effects interactions.' in text, "expected to find: " + 'Reentrancy protection or checks effects interactions.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/12-foundry.mdc')
    assert 'Coverage gaps on admin only functions are acceptable if access control is tested.' in text, "expected to find: " + 'Coverage gaps on admin only functions are acceptable if access control is tested.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/12-foundry.mdc')
    assert 'Scripts must be idempotent where possible. (Cross ref: 02-reliability.mdc)' in text, "expected to find: " + 'Scripts must be idempotent where possible. (Cross ref: 02-reliability.mdc)'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/12-foundry.mdc')
    assert 'Alternative toolchains are allowed only with explicit justification' in text, "expected to find: " + 'Alternative toolchains are allowed only with explicit justification'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/20-wagmi-viem.mdc')
    assert 'wagmi config must define supported chains including Linea, RPC fallback, timeouts, retry policy.' in text, "expected to find: " + 'wagmi config must define supported chains including Linea, RPC fallback, timeouts, retry policy.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/20-wagmi-viem.mdc')
    assert 'Writes must handle pending, replacement, cancellation, and receipt confirmation.' in text, "expected to find: " + 'Writes must handle pending, replacement, cancellation, and receipt confirmation.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/20-wagmi-viem.mdc')
    assert 'Signatures must use signTypedData with explicit domain and user readable intent.' in text, "expected to find: " + 'Signatures must use signTypedData with explicit domain and user readable intent.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/30-next-react.mdc')
    assert 'Onchain reads in Server Components only if wallet independent.' in text, "expected to find: " + 'Onchain reads in Server Components only if wallet independent.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/30-next-react.mdc')
    assert 'description: Next.js App Router and React discipline' in text, "expected to find: " + 'description: Next.js App Router and React discipline'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/30-next-react.mdc')
    assert 'Wallet and wagmi logic only in Client Components.' in text, "expected to find: " + 'Wallet and wagmi logic only in Client Components.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/35-typescript.mdc')
    assert 'description: TypeScript strictness and domain modeling' in text, "expected to find: " + 'description: TypeScript strictness and domain modeling'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/35-typescript.mdc')
    assert 'Prefer domain types over primitives.' in text, "expected to find: " + 'Prefer domain types over primitives.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/35-typescript.mdc')
    assert 'Fail at compile time, not runtime.' in text, "expected to find: " + 'Fail at compile time, not runtime.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/40-nestjs.mdc')
    assert 'Manage env vars with dotenv or similar; validate with zod or class-validator.' in text, "expected to find: " + 'Manage env vars with dotenv or similar; validate with zod or class-validator.'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/40-nestjs.mdc')
    assert 'Check database and cache connectivity in readiness.' in text, "expected to find: " + 'Check database and cache connectivity in readiness.'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/40-nestjs.mdc')
    assert 'Expose `/metrics` endpoint for Prometheus scraping.' in text, "expected to find: " + 'Expose `/metrics` endpoint for Prometheus scraping.'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/42-prisma.mdc')
    assert 'Generic data layer principles (pagination, N+1 prevention, backfills)' in text, "expected to find: " + 'Generic data layer principles (pagination, N+1 prevention, backfills)'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/42-prisma.mdc')
    assert 'description: Prisma client, migrations, relations, and transactions' in text, "expected to find: " + 'description: Prisma client, migrations, relations, and transactions'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/42-prisma.mdc')
    assert 'Raw SQL forbidden unless justified for performance and documented.' in text, "expected to find: " + 'Raw SQL forbidden unless justified for performance and documented.'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/45-data-layer.mdc')
    assert 'Destructive changes require phased rollout and rollback. (Cross ref: 02-reliability.mdc)' in text, "expected to find: " + 'Destructive changes require phased rollout and rollback. (Cross ref: 02-reliability.mdc)'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/45-data-layer.mdc')
    assert 'This file is the single source of truth for cross stack data rules.' in text, "expected to find: " + 'This file is the single source of truth for cross stack data rules.'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/45-data-layer.mdc')
    assert 'ORM or database specific files must not redefine these principles,' in text, "expected to find: " + 'ORM or database specific files must not redefine these principles,'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/50-testing-ci.mdc')
    assert 'Avoid coverage driven testing. Use coverage as a signal only; critical paths must be meaningfully tested and gaps justified.' in text, "expected to find: " + 'Avoid coverage driven testing. Use coverage as a signal only; critical paths must be meaningfully tested and gaps justified.'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/50-testing-ci.mdc')
    assert 'CI blocks merges if tests, lint, typecheck, or build fail.' in text, "expected to find: " + 'CI blocks merges if tests, lint, typecheck, or build fail.'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/50-testing-ci.mdc')
    assert 'Dependency audits required before production.' in text, "expected to find: " + 'Dependency audits required before production.'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/55-comments-docs.mdc')
    assert 'description: Comments and documentation discipline' in text, "expected to find: " + 'description: Comments and documentation discipline'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/55-comments-docs.mdc')
    assert 'Explain intent only when non obvious.' in text, "expected to find: " + 'Explain intent only when non obvious.'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/55-comments-docs.mdc')
    assert 'Update docs when behavior changes:' in text, "expected to find: " + 'Update docs when behavior changes:'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/60-web3-product.mdc')
    assert 'Backend idempotency mandatory. (Cross ref: 02-reliability.mdc)' in text, "expected to find: " + 'Backend idempotency mandatory. (Cross ref: 02-reliability.mdc)'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/60-web3-product.mdc')
    assert 'Replay protection required. (Cross ref: 02-reliability.mdc)' in text, "expected to find: " + 'Replay protection required. (Cross ref: 02-reliability.mdc)'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/60-web3-product.mdc')
    assert 'Measure time to wallet ready and meaningful feedback.' in text, "expected to find: " + 'Measure time to wallet ready and meaningful feedback.'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/65-release-rollout.mdc')
    assert 'description: Release strategy, rollouts, and production safety' in text, "expected to find: " + 'description: Release strategy, rollouts, and production safety'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/65-release-rollout.mdc')
    assert 'Release is not complete until verification is done.' in text, "expected to find: " + 'Release is not complete until verification is done.'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/65-release-rollout.mdc')
    assert 'Avoid full blast releases for risky changes.' in text, "expected to find: " + 'Avoid full blast releases for risky changes.'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/70-observability-ops.mdc')
    assert 'Jobs must be idempotent, retry safe, observable, resumable. (Cross ref: 02-reliability.mdc)' in text, "expected to find: " + 'Jobs must be idempotent, retry safe, observable, resumable. (Cross ref: 02-reliability.mdc)'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/70-observability-ops.mdc')
    assert 'Metrics must cover latency, error rate, throughput, dependency health.' in text, "expected to find: " + 'Metrics must cover latency, error rate, throughput, dependency health.'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/70-observability-ops.mdc')
    assert 'Document runbooks for risky systems, with ownership definition.' in text, "expected to find: " + 'Document runbooks for risky systems, with ownership definition.'[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/80-accessibility-performance.mdc')
    assert 'Support i18n and responsive design where the product requires it.' in text, "expected to find: " + 'Support i18n and responsive design where the product requires it.'[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/80-accessibility-performance.mdc')
    assert 'Prevent performance regressions on critical user flows.' in text, "expected to find: " + 'Prevent performance regressions on critical user flows.'[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/80-accessibility-performance.mdc')
    assert 'description: Accessibility and frontend performance' in text, "expected to find: " + 'description: Accessibility and frontend performance'[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/90-monorepo.mdc')
    assert 'Use `overrides` in `pnpm-workspace.yaml` to patch vulnerable transitive dependencies.' in text, "expected to find: " + 'Use `overrides` in `pnpm-workspace.yaml` to patch vulnerable transitive dependencies.'[:80]


def test_signal_55():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/90-monorepo.mdc')
    assert 'All packages live in `packages/` for new projects, or `apps/` for existing ones.' in text, "expected to find: " + 'All packages live in `packages/` for new projects, or `apps/` for existing ones.'[:80]


def test_signal_56():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/90-monorepo.mdc')
    assert 'globs: ["pnpm-workspace.yaml", "pnpm-lock.yaml", "**/package.json", ".nvmrc"]' in text, "expected to find: " + 'globs: ["pnpm-workspace.yaml", "pnpm-lock.yaml", "**/package.json", ".nvmrc"]'[:80]


def test_signal_57():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/92-docker.mdc')
    assert 'RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile' in text, "expected to find: " + 'RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile'[:80]


def test_signal_58():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/92-docker.mdc')
    assert 'description: Docker multi stage builds, security, caching' in text, "expected to find: " + 'description: Docker multi stage builds, security, caching'[:80]


def test_signal_59():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/92-docker.mdc')
    assert 'CI must pass `--build-arg NODE_VERSION=$(cat .nvmrc)`.' in text, "expected to find: " + 'CI must pass `--build-arg NODE_VERSION=$(cat .nvmrc)`.'[:80]


def test_signal_60():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/95-github-actions.mdc')
    assert 'Use PR templates with checklists (e.g., DoD verification) where helpful.' in text, "expected to find: " + 'Use PR templates with checklists (e.g., DoD verification) where helpful.'[:80]


def test_signal_61():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/95-github-actions.mdc')
    assert 'Extract common steps into composite actions in `.github/actions/`.' in text, "expected to find: " + 'Extract common steps into composite actions in `.github/actions/`.'[:80]


def test_signal_62():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/95-github-actions.mdc')
    assert 'description: GitHub Actions security, performance, conventions' in text, "expected to find: " + 'description: GitHub Actions security, performance, conventions'[:80]


def test_signal_63():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/99-meta.mdc')
    assert 'Enforce via CI (e.g., lint rules files for consistency) when worth the maintenance cost.' in text, "expected to find: " + 'Enforce via CI (e.g., lint rules files for consistency) when worth the maintenance cost.'[:80]


def test_signal_64():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/99-meta.mdc')
    assert 'Review annually or on major tool changes (e.g., Solidity upgrades).' in text, "expected to find: " + 'Review annually or on major tool changes (e.g., Solidity upgrades).'[:80]


def test_signal_65():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/99-meta.mdc')
    assert 'Track waivers and justifications in PRs and tickets.' in text, "expected to find: " + 'Track waivers and justifications in PRs and tickets.'[:80]

