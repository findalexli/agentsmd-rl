"""Tests for effect-ts/effect#6123 — sql-kysely proxy get invariant fix."""
import os
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/effect"
PKG = "/workspace/effect/packages/sql-kysely"


def _run_tsx(script: str, timeout: int = 60):
    """Write a temporary .mjs script inside the package dir and run it via tsx."""
    script_path = Path(PKG) / "_scaffold_tmp.mjs"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["npx", "tsx", str(script_path)],
            cwd=PKG,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        try:
            script_path.unlink()
        except FileNotFoundError:
            pass


# ───────────────────────── f2p ─────────────────────────


def test_hash_twice_does_not_throw():
    """Calling Hash.hash twice on a kysely builder must not throw the proxy
    invariant TypeError. On the buggy base, the second call throws because the
    proxy's get trap wraps a non-configurable, non-writable cached value."""
    script = textwrap.dedent("""
        import * as SqlKysely from "@effect/sql-kysely/Kysely"
        import { Hash } from "effect"
        import { SqliteDialect } from "kysely"
        import SqliteDB from "better-sqlite3"

        const db = SqlKysely.make({
          dialect: new SqliteDialect({ database: new SqliteDB(":memory:") })
        })
        const b = db.selectFrom("users").selectAll()
        Hash.hash(b)
        Hash.hash(b)
        console.log("HASH_TWICE_OK")
    """)
    r = _run_tsx(script)
    assert r.returncode == 0, (
        f"Hash.hash twice failed.\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "HASH_TWICE_OK" in r.stdout


def test_hash_returns_stable_value():
    """The hash returned by repeated Hash.hash() calls must be the same number.
    On base, the second call throws (so the values can't be compared); on fix,
    both calls return the cached numeric hash."""
    script = textwrap.dedent("""
        import * as SqlKysely from "@effect/sql-kysely/Kysely"
        import { Hash } from "effect"
        import { SqliteDialect } from "kysely"
        import SqliteDB from "better-sqlite3"

        const db = SqlKysely.make({
          dialect: new SqliteDialect({ database: new SqliteDB(":memory:") })
        })
        const b = db.selectFrom("users").selectAll()
        const h1 = Hash.hash(b)
        const h2 = Hash.hash(b)
        const h3 = Hash.hash(b)
        if (typeof h1 !== "number" || typeof h2 !== "number" || typeof h3 !== "number") {
          console.error("NOT_NUMBER", typeof h1, typeof h2, typeof h3)
          process.exit(2)
        }
        if (h1 !== h2 || h2 !== h3) {
          console.error("MISMATCH", h1, h2, h3)
          process.exit(3)
        }
        console.log("HASH_STABLE_OK", h1)
    """)
    r = _run_tsx(script)
    assert r.returncode == 0, (
        f"Stable hash check failed.\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "HASH_STABLE_OK" in r.stdout


def test_hash_works_for_multiple_builder_shapes():
    """The fix must apply to all kysely builder kinds — select, insert, update,
    delete — not just the one in the PR's reproduction. On base, every shape
    eventually triggers the proxy invariant on the second hash call."""
    script = textwrap.dedent("""
        import * as SqlKysely from "@effect/sql-kysely/Kysely"
        import { Hash } from "effect"
        import { SqliteDialect } from "kysely"
        import SqliteDB from "better-sqlite3"

        const db = SqlKysely.make({
          dialect: new SqliteDialect({ database: new SqliteDB(":memory:") })
        })

        const builders = [
          db.selectFrom("users").selectAll(),
          db.insertInto("users").values({ name: "x" }),
          db.updateTable("users").set({ name: "y" }),
          db.deleteFrom("users"),
          db.selectFrom("users").select(["id"]).where("id", "=", 1),
        ]

        for (const b of builders) {
          const a = Hash.hash(b)
          const c = Hash.hash(b)
          if (a !== c) {
            console.error("MISMATCH", a, c)
            process.exit(2)
          }
        }
        console.log("ALL_SHAPES_OK")
    """)
    r = _run_tsx(script)
    assert r.returncode == 0, (
        f"Multi-shape hash check failed.\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "ALL_SHAPES_OK" in r.stdout


def test_proxy_returns_frozen_property_actual_value():
    """Direct test of the proxy invariant fix: define a non-configurable,
    non-writable property on an object that ends up wrapped, then read it.

    We use Object.defineProperty (mirroring Hash.hash's caching strategy) on a
    column reference returned from the kysely AST. The proxy's get trap must
    return the property's actual value, not a wrapped/recomputed one."""
    script = textwrap.dedent("""
        import * as SqlKysely from "@effect/sql-kysely/Kysely"
        import { SqliteDialect } from "kysely"
        import SqliteDB from "better-sqlite3"

        const db = SqlKysely.make({
          dialect: new SqliteDialect({ database: new SqliteDB(":memory:") })
        })
        const b = db.selectFrom("users").selectAll()

        const SENTINEL = Symbol("sentinel")
        const value = { tag: "actual" }
        Object.defineProperty(b, SENTINEL, {
          value,
          writable: false,
          configurable: false,
          enumerable: false,
        })

        const got = b[SENTINEL]
        if (got !== value) {
          console.error("WRONG_IDENTITY", got)
          process.exit(2)
        }
        if (got.tag !== "actual") {
          console.error("WRONG_VALUE", got)
          process.exit(3)
        }
        console.log("FROZEN_PROP_OK")
    """)
    r = _run_tsx(script)
    assert r.returncode == 0, (
        f"Frozen-property invariant check failed.\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "FROZEN_PROP_OK" in r.stdout


# ───────────────────────── p2p ─────────────────────────


def test_kysely_query_compiles():
    """Basic compile sanity: selectFrom("users").selectAll() must compile to
    standard SQL. This works on base (the proxy's wrapping doesn't break
    .compile()) and continues to work after the fix."""
    script = textwrap.dedent("""
        import * as SqlKysely from "@effect/sql-kysely/Kysely"
        import { SqliteDialect } from "kysely"
        import SqliteDB from "better-sqlite3"

        const db = SqlKysely.make({
          dialect: new SqliteDialect({ database: new SqliteDB(":memory:") })
        })
        const sql = db.selectFrom("users").selectAll().compile().sql
        if (sql !== 'select * from "users"') {
          console.error("WRONG_SQL", sql)
          process.exit(2)
        }
        console.log("COMPILE_OK")
    """)
    r = _run_tsx(script)
    assert r.returncode == 0, (
        f"Compile sanity failed.\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "COMPILE_OK" in r.stdout


def test_repo_kysely_vitest():
    """Run the upstream sql-kysely Kysely.test.ts via vitest. This exercises
    the full insert/select/update/delete pipeline through the proxy."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "test/Kysely.test.ts"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Upstream Kysely.test.ts failed.\nstdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-1000:]}"
    )


def test_repo_sqlite_vitest():
    """Run the upstream sql-kysely Sqlite.test.ts via vitest."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "test/Sqlite.test.ts"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Upstream Sqlite.test.ts failed.\nstdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-1000:]}"
    )


def test_package_typecheck():
    """The package must still typecheck after the change."""
    r = subprocess.run(
        ["pnpm", "exec", "tsc", "-b", "tsconfig.json"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"tsc failed.\nstdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-1000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_pnpm():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm circular'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_pnpm_2():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_pnpm_3():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm codegen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")