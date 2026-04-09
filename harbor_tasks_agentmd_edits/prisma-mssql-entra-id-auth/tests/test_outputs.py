"""
Task: prisma-mssql-entra-id-auth
Repo: prisma/prisma @ a60fe90928873bcec23b0fd07a002c164d7f4d27
PR:   28156

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/prisma"
ADAPTER_DIR = Path(REPO) / "packages" / "adapter-mssql"
CONN_STRING_FILE = ADAPTER_DIR / "src" / "connection-string.ts"
README_FILE = ADAPTER_DIR / "README.md"


def _run_tsx(script: str) -> subprocess.CompletedProcess:
    """Write a TS test script and execute it with tsx in the adapter-mssql dir."""
    test_file = ADAPTER_DIR / "_test_probe.ts"
    test_file.write_text(script)
    try:
        return subprocess.run(
            ["npx", "tsx", "_test_probe.ts"],
            cwd=str(ADAPTER_DIR),
            capture_output=True,
            timeout=30,
        )
    finally:
        test_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """connection-string.ts must parse as valid TypeScript."""
    content = CONN_STRING_FILE.read_text()
    assert len(content) > 500, "connection-string.ts should be a substantial file"
    assert abs(content.count("{") - content.count("}")) < 3, \
        "connection-string.ts has unbalanced braces — likely a syntax error"

    # Verify tsx can actually parse the file (catches real TS syntax errors)
    r = _run_tsx(
        "import { parseConnectionString } from './src/connection-string'\n"
        "console.log(typeof parseConnectionString)\n"
    )
    assert r.returncode == 0, \
        f"connection-string.ts fails to parse:\n{r.stderr.decode()}"
    assert "function" in r.stdout.decode(), \
        "parseConnectionString should be an exported function"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — runtime behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_runtime_default_azure_credential():
    """parseConnectionString must map DefaultAzureCredential to azure-active-directory-default."""
    r = _run_tsx("""
import { parseConnectionString } from './src/connection-string'

const config = parseConnectionString(
  'sqlserver://localhost:1433;database=testdb;authentication=DefaultAzureCredential'
)
const result = {
  authType: config.authentication?.type,
  user: config.user ?? null,
  database: config.database,
}
console.log(JSON.stringify(result))
""")
    assert r.returncode == 0, \
        f"parseConnectionString threw on DefaultAzureCredential:\n{r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert result["authType"] == "azure-active-directory-default", \
        f"Expected azure-active-directory-default, got {result['authType']}"
    assert result["user"] is None, \
        "DefaultAzureCredential should not set user"
    assert result["database"] == "testdb", \
        "Should still parse database parameter"


# [pr_diff] fail_to_pass
def test_runtime_ad_password():
    """parseConnectionString must handle ActiveDirectoryPassword with all required params."""
    r = _run_tsx("""
import { parseConnectionString } from './src/connection-string'

const config = parseConnectionString(
  'sqlserver://localhost:1433;database=testdb;authentication=ActiveDirectoryPassword;userName=user1;password=pass1;clientId=cid1'
)
const result = {
  authType: config.authentication?.type,
  options: config.authentication?.options,
}
console.log(JSON.stringify(result))
""")
    assert r.returncode == 0, \
        f"parseConnectionString threw on ActiveDirectoryPassword:\n{r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert result["authType"] == "azure-active-directory-password", \
        f"Expected azure-active-directory-password, got {result['authType']}"
    opts = result["options"]
    assert opts["userName"] == "user1", f"Expected userName=user1, got {opts.get('userName')}"
    assert opts["password"] == "pass1", f"Expected password=pass1, got {opts.get('password')}"
    assert opts["clientId"] == "cid1", f"Expected clientId=cid1, got {opts.get('clientId')}"


# [pr_diff] fail_to_pass
def test_runtime_ad_password_validation():
    """parseConnectionString must throw when ActiveDirectoryPassword is missing required params."""
    r = _run_tsx("""
import { parseConnectionString } from './src/connection-string'

try {
  // Missing clientId — should throw
  parseConnectionString(
    'sqlserver://localhost:1433;database=testdb;authentication=ActiveDirectoryPassword;userName=user1;password=pass1'
  )
  console.log('NO_ERROR')
} catch (e: any) {
  console.log('ERROR:' + e.message)
}
""")
    assert r.returncode == 0, f"Script failed:\n{r.stderr.decode()}"
    output = r.stdout.decode().strip()
    assert output.startswith("ERROR:"), \
        f"Should have thrown for missing clientId, got: {output}"
    assert "ActiveDirectoryPassword" in output, \
        f"Error should mention ActiveDirectoryPassword: {output}"


# [pr_diff] fail_to_pass
def test_runtime_service_principal():
    """parseConnectionString must handle ActiveDirectoryServicePrincipal."""
    r = _run_tsx("""
import { parseConnectionString } from './src/connection-string'

const config = parseConnectionString(
  'sqlserver://localhost:1433;database=testdb;authentication=ActiveDirectoryServicePrincipal;userName=my-client;password=my-secret'
)
const result = {
  authType: config.authentication?.type,
  options: config.authentication?.options,
}
console.log(JSON.stringify(result))
""")
    assert r.returncode == 0, \
        f"parseConnectionString threw on ActiveDirectoryServicePrincipal:\n{r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert result["authType"] == "azure-active-directory-service-principal-secret", \
        f"Expected azure-active-directory-service-principal-secret, got {result['authType']}"
    opts = result["options"]
    assert opts["clientId"] == "my-client", \
        f"userName should map to clientId, got {opts.get('clientId')}"
    assert opts["clientSecret"] == "my-secret", \
        f"password should map to clientSecret, got {opts.get('clientSecret')}"


# [pr_diff] fail_to_pass
def test_runtime_managed_identity():
    """parseConnectionString must handle ActiveDirectoryManagedIdentity."""
    r = _run_tsx("""
import { parseConnectionString } from './src/connection-string'

const config = parseConnectionString(
  'sqlserver://localhost:1433;database=testdb;authentication=ActiveDirectoryManagedIdentity;clientId=cid;msiEndpoint=ep1;msiSecret=sec1'
)
const result = {
  authType: config.authentication?.type,
  options: config.authentication?.options,
}
console.log(JSON.stringify(result))
""")
    assert r.returncode == 0, \
        f"parseConnectionString threw on ActiveDirectoryManagedIdentity:\n{r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert result["authType"] == "azure-active-directory-msi-app-service", \
        f"Expected azure-active-directory-msi-app-service, got {result['authType']}"
    opts = result["options"]
    assert opts["clientId"] == "cid", f"Expected clientId=cid, got {opts.get('clientId')}"


# [pr_diff] fail_to_pass
def test_runtime_duplicate_param_rejected():
    """parseConnectionString must throw on duplicate connection string parameters."""
    r = _run_tsx("""
import { parseConnectionString } from './src/connection-string'

try {
  parseConnectionString('sqlserver://localhost:1433;database=testdb;database=otherdb')
  console.log('NO_ERROR')
} catch (e: any) {
  console.log('ERROR:' + e.message)
}
""")
    assert r.returncode == 0, f"Script failed:\n{r.stderr.decode()}"
    output = r.stdout.decode().strip()
    assert output.startswith("ERROR:"), \
        f"Should have thrown for duplicate parameter, got: {output}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_params_still_parsed():
    """Existing connection string parameters (database, user, password, encrypt) must still work."""
    r = _run_tsx("""
import { parseConnectionString } from './src/connection-string'

const config = parseConnectionString(
  'sqlserver://myhost:1433;database=mydb;user=admin;password=secret;encrypt=true;trustServerCertificate=true'
)
const result = {
  server: config.server,
  port: config.port,
  database: config.database,
  user: config.user,
  password: config.password,
  encrypt: config.options?.encrypt,
  trustServerCertificate: config.options?.trustServerCertificate,
}
console.log(JSON.stringify(result))
""")
    assert r.returncode == 0, \
        f"parseConnectionString failed on basic params:\n{r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert result["server"] == "myhost", f"Expected server=myhost, got {result['server']}"
    assert result["port"] == 1433, f"Expected port=1433, got {result['port']}"
    assert result["database"] == "mydb", f"Expected database=mydb, got {result['database']}"
    assert result["user"] == "admin", f"Expected user=admin, got {result['user']}"
    assert result["password"] == "secret", f"Expected password=secret, got {result['password']}"
    assert result["encrypt"] is True, f"Expected encrypt=true, got {result['encrypt']}"


# [static] pass_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo itself
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_prettier_formatting():
    """Repo's TypeScript files follow Prettier formatting (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "src/*.ts"],
        capture_output=True, text=True, timeout=60, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Prettier formatting check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typescript_syntax():
    """Repo's TypeScript source files have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", "import './src/connection-string.ts'"],
        capture_output=True, text=True, timeout=30, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"TypeScript syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_test_file_structure():
    """Repo's test files have valid structure and imports (pass_to_pass)."""
    test_file = ADAPTER_DIR / "src" / "connection-string.test.ts"
    content = test_file.read_text()

    # Basic structure checks
    assert "describe(" in content, "Test file should have describe() blocks"
    assert "it(" in content, "Test file should have it() tests"
    assert "expect(" in content, "Test file should use expect() assertions"
    assert "parseConnectionString" in content, "Test file should test parseConnectionString"

    # Check balanced braces (basic syntax check)
    open_count = content.count("{")
    close_count = content.count("}")
    assert open_count == close_count, "Test file has unbalanced braces"


# ---------------------------------------------------------------------------
# Config edit (config_edit) — README.md documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass
def test_readme_entra_id_docs():
    """README.md must document Entra ID authentication options."""
    content = README_FILE.read_text()

    has_entra = "entra" in content.lower() or "azure active directory" in content.lower()
    assert has_entra, \
        "README.md should document Entra ID (Azure Active Directory) authentication"

    assert "DefaultAzureCredential" in content, \
        "README.md should document DefaultAzureCredential authentication option"
    assert "ActiveDirectoryPassword" in content, \
        "README.md should document ActiveDirectoryPassword authentication option"
    assert "ActiveDirectoryServicePrincipal" in content, \
        "README.md should document ActiveDirectoryServicePrincipal authentication option"


# [config_edit] fail_to_pass
def test_readme_connection_string_docs():
    """README.md must document connection string instantiation."""
    content = README_FILE.read_text()

    assert "connection string" in content.lower(), \
        "README.md should mention connection string usage"
    assert "sqlserver://" in content, \
        "README.md should include a sqlserver:// connection string example"
    assert "PrismaMssql(" in content, \
        "README.md should show PrismaMssql constructor usage"
