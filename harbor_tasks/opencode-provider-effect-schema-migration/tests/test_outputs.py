"""
Tests for anomalyco/opencode#24027:
refactor(provider): migrate provider domain to Effect Schema.
"""
import json
import os
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/opencode"
PKG = f"{REPO}/packages/opencode"
PROVIDER_DIR = f"{PKG}/src/provider"

AUTH_TS = Path(f"{PROVIDER_DIR}/auth.ts")
MODELS_TS = Path(f"{PROVIDER_DIR}/models.ts")
PROVIDER_TS = Path(f"{PROVIDER_DIR}/provider.ts")
SCHEMA_MD = Path(f"{PKG}/specs/effect/schema.md")


def _read(p: Path) -> str:
    assert p.is_file(), f"missing file: {p}"
    return p.read_text()


def _has_zod_import(text: str) -> bool:
    """True if the file still has any zod import statement."""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("//") or s.startswith("*") or s.startswith("/*"):
            continue
        if not s.startswith("import"):
            continue
        if re.search(r'from\s+["\']zod["\']', s):
            return True
    return False


# --------------------------------------------------------------------------
# fail_to_pass: structural checks proving the migration was performed
# --------------------------------------------------------------------------

def test_auth_no_zod_import():
    """auth.ts no longer imports zod."""
    assert not _has_zod_import(_read(AUTH_TS)), \
        "packages/opencode/src/provider/auth.ts must no longer import 'zod'"


def test_models_no_zod_import():
    """models.ts no longer imports zod."""
    assert not _has_zod_import(_read(MODELS_TS)), \
        "packages/opencode/src/provider/models.ts must no longer import 'zod'"


def test_provider_no_zod_import():
    """provider.ts no longer imports zod."""
    assert not _has_zod_import(_read(PROVIDER_TS)), \
        "packages/opencode/src/provider/provider.ts must no longer import 'zod'"


def test_auth_uses_named_schema_error():
    """auth.ts errors switched from NamedError.create to namedSchemaError."""
    text = _read(AUTH_TS)
    assert "namedSchemaError" in text, \
        "auth.ts must use namedSchemaError for typed errors"
    # Each of the four errors must use the new pattern.
    for err_name in ("OauthMissing", "OauthCodeMissing",
                     "OauthCallbackFailed", "ValidationFailed"):
        assert re.search(
            rf"export\s+const\s+{err_name}\s*=\s*namedSchemaError\b", text
        ), f"{err_name} must be defined with namedSchemaError(...)"


def test_provider_uses_named_schema_error():
    """provider.ts errors switched from NamedError.create to namedSchemaError."""
    text = _read(PROVIDER_TS)
    assert "namedSchemaError" in text
    for err_name in ("ModelNotFoundError", "InitError"):
        assert re.search(
            rf"export\s+const\s+{err_name}\s*=\s*namedSchemaError\b", text
        ), f"{err_name} must be defined with namedSchemaError(...)"


def test_models_uses_effect_schema():
    """models.ts uses Effect Schema (not zod) for the Cost / Model / Provider schemas."""
    text = _read(MODELS_TS)
    assert re.search(r'from\s+["\']effect["\']', text), \
        "models.ts must import from 'effect'"
    assert ("Schema.Struct" in text) or ("Schema.Class" in text), \
        "models.ts schemas must be defined with Effect Schema (Schema.Struct or Schema.Class)"
    # Exported Model and Provider must be Effect Schema (Struct or Class), not zod.
    for name in ("Model", "Provider"):
        const_struct = re.search(
            rf"export\s+const\s+{name}\s*=\s*Schema\.Struct", text
        )
        class_form = re.search(
            rf"export\s+class\s+{name}\s+extends\s+Schema\.Class", text
        )
        assert const_struct or class_form, (
            f"export {name} must be defined with Schema.Struct or Schema.Class"
        )


def test_schema_md_provider_section_done():
    """specs/effect/schema.md marks the three provider files as complete."""
    text = _read(SCHEMA_MD)
    assert "[x] `src/provider/auth.ts`" in text
    assert "[x] `src/provider/models.ts`" in text
    assert "[x] `src/provider/provider.ts`" in text
    # Make sure none are still unchecked.
    assert "[ ] `src/provider/auth.ts`" not in text
    assert "[ ] `src/provider/models.ts`" not in text
    assert "[ ] `src/provider/provider.ts`" not in text


def test_models_schema_decodes_valid_data():
    """The migrated models.ts Model schema decodes a real models.dev shape via Effect Schema.

    This only succeeds when Model is an Effect Schema (Schema.decodeUnknownSync
    requires an Effect Schema interface — passing a zod schema throws).
    """
    sample = {
        "id": "gpt-4-test",
        "name": "GPT-4 Test",
        "release_date": "2026-01-01",
        "attachment": True,
        "reasoning": False,
        "temperature": True,
        "tool_call": True,
        "limit": {"context": 128000, "output": 4096},
        "cost": {"input": 1.0, "output": 2.0},
    }

    sample_json = json.dumps(sample)
    script = textwrap.dedent(
        f"""
        import {{ Schema }} from "effect"
        import {{ Model, Provider }} from "./src/provider/models"

        const modelInput = JSON.parse({json.dumps(sample_json)}) as unknown
        const decoded: any = Schema.decodeUnknownSync(Model as any)(modelInput)
        if (decoded.id !== "gpt-4-test") {{
          console.error("DECODE_BAD_ID", decoded.id)
          process.exit(1)
        }}
        if (decoded.limit.context !== 128000) {{
          console.error("DECODE_BAD_CONTEXT", decoded.limit.context)
          process.exit(1)
        }}

        // Also verify Provider is an Effect Schema by decoding a record-of-models shape.
        const provInput = {{
          name: "test", id: "test-prov", env: ["FOO"],
          models: {{ "gpt-4-test": modelInput }},
        }} as unknown
        const prov: any = Schema.decodeUnknownSync(Provider as any)(provInput)
        if (prov.id !== "test-prov") {{
          console.error("PROVIDER_BAD_ID", prov.id)
          process.exit(1)
        }}
        console.log("MIGRATION_DECODE_OK")
        """
    )

    script_path = Path(f"{PKG}/__migration_decode_check.ts")
    script_path.write_text(script)
    try:
        r = subprocess.run(
            ["bun", "run", str(script_path.name)],
            cwd=PKG,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert r.returncode == 0, (
            f"bun run failed (rc={r.returncode}):\n"
            f"STDOUT: {r.stdout[-1000:]}\n"
            f"STDERR: {r.stderr[-1500:]}"
        )
        assert "MIGRATION_DECODE_OK" in r.stdout, (
            "Effect Schema decode did not succeed. Output:\n"
            f"{r.stdout[-1000:]}\n{r.stderr[-1000:]}"
        )
    finally:
        try:
            script_path.unlink()
        except FileNotFoundError:
            pass


# --------------------------------------------------------------------------
# pass_to_pass: repo-level CI gates that should remain green
# --------------------------------------------------------------------------

def test_repo_typecheck():
    """`bun typecheck` from packages/opencode passes."""
    r = subprocess.run(
        ["bun", "typecheck"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"bun typecheck failed:\n"
        f"STDOUT: {r.stdout[-1500:]}\nSTDERR: {r.stderr[-1500:]}"
    )
