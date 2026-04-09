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
# Pass-to-pass (repo_tests) — verify repo CI/CD still works
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typescript_compiles():
    """Repo's TypeScript files compile and load (pass_to_pass)."""
    r = _run_ts("""
import { parseConnectionString } from './src/connection-string.ts'
import { extractSchemaFromConnectionString } from './src/connection-string.ts'

// Test that imports work and basic parsing functions
const config = parseConnectionString('sqlserver://localhost:1433;database=testdb;user=sa;password=test')
if (config.server !== 'localhost') throw new Error('Server mismatch')
if (config.database !== 'testdb') throw new Error('Database mismatch')
if (config.user !== 'sa') throw new Error('User mismatch')

// Test schema extraction
const schema = extractSchemaFromConnectionString('sqlserver://localhost;database=testdb;schema=custom')
if (schema !== 'custom') throw new Error('Schema extraction failed')

console.log('TypeScript compilation and basic parsing: OK')
""")
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_connection_string_parsing():
    """Connection string parsing works for all parameter variations (pass_to_pass)."""
    r = _run_ts("""
import { parseConnectionString } from './src/connection-string.ts'

const testCases = [
    // Basic parsing
    { input: 'sqlserver://localhost:1433;database=testdb;user=sa;password=mypassword', expected: { server: 'localhost', port: 1433, database: 'testdb', user: 'sa', password: 'mypassword' } },
    // Alternative user parameter names
    { input: 'sqlserver://localhost;database=testdb;username=sa;password=pw', expected: { user: 'sa' } },
    { input: 'sqlserver://localhost;database=testdb;uid=sa;password=pw', expected: { user: 'sa' } },
    // Alternative password parameter names
    { input: 'sqlserver://localhost;database=testdb;user=sa;pwd=mypassword', expected: { password: 'mypassword' } },
    // Alternative database parameter names
    { input: 'sqlserver://localhost;initial catalog=testdb;user=sa;password=pw', expected: { database: 'testdb' } },
    // Boolean options
    { input: 'sqlserver://localhost;database=testdb;encrypt=true', expected: { encrypt: true } },
    { input: 'sqlserver://localhost;database=testdb;trustServerCertificate=false', expected: { trustServerCertificate: false } },
]

for (const tc of testCases) {
    const config = parseConnectionString(tc.input)
    for (const [key, value] of Object.entries(tc.expected)) {
        let actual
        if (key === 'encrypt' || key === 'trustServerCertificate') {
            actual = config.options?.[key]
        } else {
            actual = config[key as keyof typeof config]
        }
        if (actual !== value) {
            throw new Error(`Test failed for "${tc.input}": expected ${key}=${value}, got ${actual}`)
        }
    }
}

console.log('All connection string parsing tests passed: OK')
""")
    assert r.returncode == 0, f"Connection string parsing test failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_error_handling():
    """Connection string error handling works correctly (pass_to_pass)."""
    r = _run_ts("""
import { parseConnectionString } from './src/connection-string.ts'

// Test invalid port
let threw = false
try {
    parseConnectionString('sqlserver://localhost:invalid;database=testdb')
} catch (e: any) {
    threw = true
    if (!e.message.includes('Invalid port number')) throw new Error('Wrong error for invalid port')
}
if (!threw) throw new Error('Should have thrown for invalid port')

// Test missing server
threw = false
try {
    parseConnectionString('sqlserver://;database=testdb')
} catch (e: any) {
    threw = true
    if (!e.message.includes('Server host is required')) throw new Error('Wrong error for missing server')
}
if (!threw) throw new Error('Should have thrown for missing server')

// Test invalid isolation level
threw = false
try {
    parseConnectionString('sqlserver://localhost;database=testdb;isolationLevel=INVALID')
} catch (e: any) {
    threw = true
    if (!e.message.includes('Invalid isolation level')) throw new Error('Wrong error for invalid isolation level')
}
if (!threw) throw new Error('Should have thrown for invalid isolation level')

console.log('Error handling tests passed: OK')
""")
    assert r.returncode == 0, f"Error handling test failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_timeout_and_pool_params():
    """Timeout and pool parameters are parsed correctly (pass_to_pass)."""
    r = _run_ts("""
import { parseConnectionString } from './src/connection-string.ts'

// Test connection timeout
const config1 = parseConnectionString('sqlserver://localhost;database=testdb;connectTimeout=30')
if (config1.connectionTimeout !== 30) throw new Error('connectTimeout not parsed')

// Test connectionLimit (pool max)
const config2 = parseConnectionString('sqlserver://localhost;database=testdb;connectionLimit=10')
if (config2.pool?.max !== 10) throw new Error('connectionLimit not parsed')

// Test poolTimeout (acquire timeout in ms)
const config3 = parseConnectionString('sqlserver://localhost;database=testdb;poolTimeout=15')
if (config3.pool?.acquireTimeoutMillis !== 15000) throw new Error('poolTimeout not parsed')

// Test socketTimeout (request timeout)
const config4 = parseConnectionString('sqlserver://localhost;database=testdb;socketTimeout=60')
if (config4.requestTimeout !== 60) throw new Error('socketTimeout not parsed')

console.log('Timeout and pool parameter tests passed: OK')
""")
    assert r.returncode == 0, f"Timeout/pool params test failed:\n{r.stderr}"


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
