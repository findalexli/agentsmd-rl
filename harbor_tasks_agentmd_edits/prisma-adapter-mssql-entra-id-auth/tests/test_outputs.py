"""
Task: prisma-adapter-mssql-entra-id-auth
Repo: prisma/prisma @ a60fe90928873bcec23b0fd07a002c164d7f4d27
PR:   28156

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/prisma"
ADAPTER_DIR = f"{REPO}/packages/adapter-mssql"


def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a TypeScript snippet via tsx in the adapter-mssql directory."""
    script_path = Path(ADAPTER_DIR) / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["tsx", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=ADAPTER_DIR,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """connection-string.ts must be valid TypeScript that tsx can load."""
    r = _run_ts("""
import { parseConnectionString } from './src/connection-string.ts'
console.log(typeof parseConnectionString)
""")
    assert r.returncode == 0, f"Failed to import connection-string.ts: {r.stderr}"
    assert "function" in r.stdout.strip(), f"Expected 'function', got: {r.stdout.strip()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_default_azure_credential_auth():
    """parseConnectionString must support authentication=DefaultAzureCredential."""
    r = _run_ts("""
import { parseConnectionString } from './src/connection-string.ts'
const config = parseConnectionString(
    'sqlserver://myserver:1433;database=testdb;authentication=DefaultAzureCredential'
)
console.log(JSON.stringify({
    authType: config.authentication?.type ?? null,
    user: config.user ?? null,
    password: config.password ?? null,
}))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["authType"] == "azure-active-directory-default", \
        f"Expected azure-active-directory-default, got: {data['authType']}"
    assert data["user"] is None, "user should not be set for DefaultAzureCredential"
    assert data["password"] is None, "password should not be set for DefaultAzureCredential"


# [pr_diff] fail_to_pass
def test_active_directory_password_auth():
    """parseConnectionString must support ActiveDirectoryPassword with userName/password/clientId."""
    r = _run_ts("""
import { parseConnectionString } from './src/connection-string.ts'
const config = parseConnectionString(
    'sqlserver://myserver:1433;database=mydb;authentication=ActiveDirectoryPassword;userName=alice;password=s3cret;clientId=cid-999'
)
const auth = config.authentication as any
console.log(JSON.stringify({
    authType: auth?.type ?? null,
    userName: auth?.options?.userName ?? null,
    password: auth?.options?.password ?? null,
    clientId: auth?.options?.clientId ?? null,
    tenantId: auth?.options?.tenantId ?? null,
}))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["authType"] == "azure-active-directory-password", \
        f"Expected azure-active-directory-password, got: {data['authType']}"
    assert data["userName"] == "alice"
    assert data["password"] == "s3cret"
    assert data["clientId"] == "cid-999"
    assert data["tenantId"] == "", f"tenantId should default to empty string, got: {data['tenantId']}"


# [pr_diff] fail_to_pass
def test_service_principal_auth():
    """parseConnectionString must support ActiveDirectoryServicePrincipal."""
    r = _run_ts("""
import { parseConnectionString } from './src/connection-string.ts'
const config = parseConnectionString(
    'sqlserver://azuredb:1433;database=prod;authentication=ActiveDirectoryServicePrincipal;userName=sp-client-id;password=sp-secret'
)
const auth = config.authentication as any
console.log(JSON.stringify({
    authType: auth?.type ?? null,
    clientId: auth?.options?.clientId ?? null,
    clientSecret: auth?.options?.clientSecret ?? null,
    tenantId: auth?.options?.tenantId ?? null,
}))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["authType"] == "azure-active-directory-service-principal-secret", \
        f"Expected azure-active-directory-service-principal-secret, got: {data['authType']}"
    assert data["clientId"] == "sp-client-id"
    assert data["clientSecret"] == "sp-secret"
    assert data["tenantId"] == ""


# [pr_diff] fail_to_pass
def test_auth_missing_params_throws():
    """ActiveDirectoryPassword without clientId must throw an error."""
    r = _run_ts("""
import { parseConnectionString } from './src/connection-string.ts'
try {
    parseConnectionString(
        'sqlserver://localhost:1433;database=testdb;authentication=ActiveDirectoryPassword;userName=user1;password=pass1'
    )
    console.log('NO_ERROR')
} catch (e: any) {
    console.log('ERROR:' + e.message)
}
""")
    assert r.returncode == 0, f"Script crashed: {r.stderr}"
    output = r.stdout.strip()
    assert output.startswith("ERROR:"), \
        f"Expected error for missing clientId, but got: {output}"
    assert "clientId" in output, f"Error should mention clientId: {output}"


# [pr_diff] fail_to_pass
def test_managed_identity_auth():
    """parseConnectionString must support ActiveDirectoryManagedIdentity."""
    r = _run_ts("""
import { parseConnectionString } from './src/connection-string.ts'
const config = parseConnectionString(
    'sqlserver://azuredb:1433;database=prod;authentication=ActiveDirectoryManagedIdentity;clientId=mi-client;msiEndpoint=https://msi.example;msiSecret=mi-secret'
)
const auth = config.authentication as any
console.log(JSON.stringify({
    authType: auth?.type ?? null,
    clientId: auth?.options?.clientId ?? null,
    msiEndpoint: auth?.options?.msiEndpoint ?? null,
    msiSecret: auth?.options?.msiSecret ?? null,
}))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["authType"] == "azure-active-directory-msi-app-service", \
        f"Expected azure-active-directory-msi-app-service, got: {data['authType']}"
    assert data["clientId"] == "mi-client"
    assert data["msiEndpoint"] == "https://msi.example"
    assert data["msiSecret"] == "mi-secret"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_basic_parsing_preserved():
    """Basic connection string parsing (user/password/database) must still work."""
    r = _run_ts("""
import { parseConnectionString } from './src/connection-string.ts'
const config = parseConnectionString(
    'sqlserver://dbhost:5432;database=mydb;user=admin;password=hunter2;encrypt=true'
)
console.log(JSON.stringify({
    server: config.server,
    port: config.port,
    database: config.database,
    user: config.user,
    password: config.password,
    encrypt: config.options?.encrypt,
}))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["server"] == "dbhost"
    assert data["port"] == 5432
    assert data["database"] == "mydb"
    assert data["user"] == "admin"
    assert data["password"] == "hunter2"
    assert data["encrypt"] is True


# ---------------------------------------------------------------------------
# Config/documentation update tests (agentmd-edit)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_documents_entra_auth():
    """README.md must document Entra ID / Active Directory authentication options."""
    readme = Path(REPO) / "packages/adapter-mssql/README.md"
    content = readme.read_text()
    assert "entra" in content.lower() or "ActiveDirectory" in content, \
        "README should document Entra ID / Active Directory authentication"
    assert "DefaultAzureCredential" in content, \
        "README should mention DefaultAzureCredential authentication option"
    assert "ActiveDirectoryPassword" in content, \
        "README should mention ActiveDirectoryPassword authentication option"
    assert "ActiveDirectoryServicePrincipal" in content, \
        "README should mention ActiveDirectoryServicePrincipal option"


# [pr_diff] fail_to_pass
def test_readme_documents_connection_string_usage():
    """README.md must show how to use a connection string with the adapter."""
    readme = Path(REPO) / "packages/adapter-mssql/README.md"
    content = readme.read_text()
    assert "connection string" in content.lower(), \
        "README should explain connection string usage"
    assert "sqlserver://" in content, \
        "README should include a connection string example with sqlserver:// protocol"
