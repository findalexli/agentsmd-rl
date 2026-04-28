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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo itself
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_prettier_formatting():
    """Repo's TypeScript files follow Prettier formatting (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "src/connection-string.ts", "src/connection-string.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Prettier formatting check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typescript_syntax():
    """Repo's TypeScript source files have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", "import './src/connection-string.ts'"],
        capture_output=True, text=True, timeout=60, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"TypeScript syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_connection_string_imports():
    """Repo's connection-string.ts can be imported without errors (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", "const m = require('./src/connection-string.ts'); console.log(typeof m.parseConnectionString)"],
        capture_output=True, text=True, timeout=60, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"connection-string.ts import failed:\n{r.stderr[-500:]}"
    assert "function" in r.stdout, f"parseConnectionString should be a function, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_test_file_prettier():
    """Repo's test files follow Prettier formatting (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "src/connection-string.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Test file Prettier check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_parse_connection_string_runs():
    """Repo's parseConnectionString function runs basic tests (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
const { parseConnectionString } = require('./src/connection-string.ts');
const result = parseConnectionString('sqlserver://localhost:1433;database=testdb;user=sa;password=secret');
if (result.server !== 'localhost') throw new Error('Server mismatch');
if (result.database !== 'testdb') throw new Error('Database mismatch');
console.log('OK');
"""],
        capture_output=True, text=True, timeout=60, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"parseConnectionString basic test failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, f"Expected OK output, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_prettier_formatting_src():
    """Repo CI - Prettier formatting check on entire src/ directory (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "src/"],
        capture_output=True, text=True, timeout=120, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Prettier check on src/ failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tsx_syntax_all_src():
    """Repo CI - TypeScript syntax validation on all src/ files via tsx (pass_to_pass)."""
    # Check that all .ts files in src/ can be parsed by tsx
    src_dir = ADAPTER_DIR / "src"
    ts_files = list(src_dir.glob("*.ts"))
    for ts_file in ts_files:
        if ts_file.name.endswith(".test.ts"):
            continue  # Skip test files - they need vitest
        r = subprocess.run(
            ["npx", "tsx", "-e", f"import './src/{ts_file.name}'; console.log('OK:{ts_file.name}')"],
            capture_output=True, text=True, timeout=30, cwd=str(ADAPTER_DIR),
        )
        assert r.returncode == 0, f"TypeScript syntax error in {ts_file.name}:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_connection_string_exports():
    """Repo CI - connection-string.ts exports all expected functions (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
import * as mod from './src/connection-string.ts';
const exports = Object.keys(mod);
const required = ['parseConnectionString', 'extractSchemaFromConnectionString'];
for (const name of required) {
  if (!exports.includes(name)) {
    console.log('MISSING:' + name);
    process.exit(1);
  }
}
console.log('EXPORTS_OK');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Export check failed:\n{r.stderr[-500:]}"
    assert "EXPORTS_OK" in r.stdout, f"Expected EXPORTS_OK, got: {r.stdout}"


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


# [repo_tests] pass_to_pass
def test_repo_user_param_aliases():
    """Repo CI - connection-string.ts handles all user parameter aliases (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
const { parseConnectionString } = require('./src/connection-string.ts');
const testCases = [
  'sqlserver://localhost;database=testdb;user=sa;password=mypassword',
  'sqlserver://localhost;database=testdb;username=sa;password=mypassword',
  'sqlserver://localhost;database=testdb;uid=sa;password=mypassword',
  'sqlserver://localhost;database=testdb;userid=sa;password=mypassword',
];
for (const cs of testCases) {
  const config = parseConnectionString(cs);
  if (config.user !== 'sa') {
    console.log('FAIL: Expected user=sa for: ' + cs);
    console.log('Got: ' + config.user);
    process.exit(1);
  }
}
console.log('USER_ALIASES_OK');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"User param aliases test failed:\n{r.stderr[-500:]}"
    assert "USER_ALIASES_OK" in r.stdout, f"Expected USER_ALIASES_OK, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_password_param_aliases():
    """Repo CI - connection-string.ts handles password parameter aliases (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
const { parseConnectionString } = require('./src/connection-string.ts');
const testCases = [
  'sqlserver://localhost;database=testdb;user=sa;password=mypassword',
  'sqlserver://localhost;database=testdb;user=sa;pwd=mypassword',
];
for (const cs of testCases) {
  const config = parseConnectionString(cs);
  if (config.password !== 'mypassword') {
    console.log('FAIL: Expected password=mypassword for: ' + cs);
    process.exit(1);
  }
}
console.log('PASSWORD_ALIASES_OK');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Password param aliases test failed:\n{r.stderr[-500:]}"
    assert "PASSWORD_ALIASES_OK" in r.stdout, f"Expected PASSWORD_ALIASES_OK, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_database_param_aliases():
    """Repo CI - connection-string.ts handles database parameter aliases (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
const { parseConnectionString } = require('./src/connection-string.ts');
const testCases = [
  'sqlserver://localhost;database=testdb;user=sa;password=mypassword',
  'sqlserver://localhost;initial catalog=testdb;user=sa;password=mypassword',
];
for (const cs of testCases) {
  const config = parseConnectionString(cs);
  if (config.database !== 'testdb') {
    console.log('FAIL: Expected database=testdb for: ' + cs);
    process.exit(1);
  }
}
console.log('DATABASE_ALIASES_OK');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Database param aliases test failed:\n{r.stderr[-500:]}"
    assert "DATABASE_ALIASES_OK" in r.stdout, f"Expected DATABASE_ALIASES_OK, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_encrypt_boolean_values():
    """Repo CI - connection-string.ts handles encrypt boolean values correctly (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
const { parseConnectionString } = require('./src/connection-string.ts');
const trueCase = parseConnectionString('sqlserver://localhost;database=testdb;encrypt=true');
if (trueCase.options?.encrypt !== true) {
  console.log('FAIL: Expected encrypt=true to set options.encrypt=true');
  process.exit(1);
}
const falseCase = parseConnectionString('sqlserver://localhost;database=testdb;encrypt=false');
if (falseCase.options?.encrypt !== false) {
  console.log('FAIL: Expected encrypt=false to set options.encrypt=false');
  process.exit(1);
}
const trueCaseUpper = parseConnectionString('sqlserver://localhost;database=testdb;encrypt=TRUE');
if (trueCaseUpper.options?.encrypt !== true) {
  console.log('FAIL: Expected encrypt=TRUE to set options.encrypt=true');
  process.exit(1);
}
console.log('ENCRYPT_BOOLEAN_OK');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Encrypt boolean test failed:\n{r.stderr[-500:]}"
    assert "ENCRYPT_BOOLEAN_OK" in r.stdout, f"Expected ENCRYPT_BOOLEAN_OK, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_connection_pool_params():
    """Repo CI - connection-string.ts parses pool parameters correctly (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
const { parseConnectionString } = require('./src/connection-string.ts');
const limitCase = parseConnectionString('sqlserver://localhost;database=testdb;connectionLimit=10');
if (limitCase.pool?.max !== 10) {
  console.log('FAIL: Expected pool.max=10, got: ' + limitCase.pool?.max);
  process.exit(1);
}
const poolTimeoutCase = parseConnectionString('sqlserver://localhost;database=testdb;poolTimeout=15');
if (poolTimeoutCase.pool?.acquireTimeoutMillis !== 15000) {
  console.log('FAIL: Expected pool.acquireTimeoutMillis=15000, got: ' + poolTimeoutCase.pool?.acquireTimeoutMillis);
  process.exit(1);
}
console.log('POOL_PARAMS_OK');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Pool params test failed:\n{r.stderr[-500:]}"
    assert "POOL_PARAMS_OK" in r.stdout, f"Expected POOL_PARAMS_OK, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_timeout_params():
    """Repo CI - connection-string.ts parses timeout parameters correctly (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
const { parseConnectionString } = require('./src/connection-string.ts');
const connectTimeout = parseConnectionString('sqlserver://localhost;database=testdb;connectTimeout=30');
if (connectTimeout.connectionTimeout !== 30) {
  console.log('FAIL: Expected connectionTimeout=30 for connectTimeout, got: ' + connectTimeout.connectionTimeout);
  process.exit(1);
}
const connectionTimeout = parseConnectionString('sqlserver://localhost;database=testdb;connectionTimeout=30');
if (connectionTimeout.connectionTimeout !== 30) {
  console.log('FAIL: Expected connectionTimeout=30 for connectionTimeout, got: ' + connectionTimeout.connectionTimeout);
  process.exit(1);
}
const loginTimeout = parseConnectionString('sqlserver://localhost;database=testdb;loginTimeout=45');
if (loginTimeout.connectionTimeout !== 45) {
  console.log('FAIL: Expected connectionTimeout=45 for loginTimeout, got: ' + loginTimeout.connectionTimeout);
  process.exit(1);
}
const socketTimeout = parseConnectionString('sqlserver://localhost;database=testdb;socketTimeout=60');
if (socketTimeout.requestTimeout !== 60) {
  console.log('FAIL: Expected requestTimeout=60, got: ' + socketTimeout.requestTimeout);
  process.exit(1);
}
console.log('TIMEOUT_PARAMS_OK');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Timeout params test failed:\n{r.stderr[-500:]}"
    assert "TIMEOUT_PARAMS_OK" in r.stdout, f"Expected TIMEOUT_PARAMS_OK, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_application_name_params():
    """Repo CI - connection-string.ts parses application name parameters correctly (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
const { parseConnectionString } = require('./src/connection-string.ts');
const appName = parseConnectionString('sqlserver://localhost;database=testdb;applicationName=MyApp');
if (appName.options?.appName !== 'MyApp') {
  console.log('FAIL: Expected options.appName=MyApp for applicationName, got: ' + appName.options?.appName);
  process.exit(1);
}
const appNameWithSpace = parseConnectionString('sqlserver://localhost;database=testdb;application name=MyApp2');
if (appNameWithSpace.options?.appName !== 'MyApp2') {
  console.log('FAIL: Expected options.appName=MyApp2 for "application name", got: ' + appNameWithSpace.options?.appName);
  process.exit(1);
}
console.log('APP_NAME_PARAMS_OK');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Application name params test failed:\n{r.stderr[-500:]}"
    assert "APP_NAME_PARAMS_OK" in r.stdout, f"Expected APP_NAME_PARAMS_OK, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_isolation_level_params():
    """Repo CI - connection-string.ts parses isolation level parameters correctly (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
const { parseConnectionString } = require('./src/connection-string.ts');
const testCases = [
  { input: 'sqlserver://localhost;database=testdb;isolationLevel=READ COMMITTED', expected: 2 },
  { input: 'sqlserver://localhost;database=testdb;isolationLevel=READ UNCOMMITTED', expected: 1 },
  { input: 'sqlserver://localhost;database=testdb;isolationLevel=REPEATABLE READ', expected: 3 },
  { input: 'sqlserver://localhost;database=testdb;isolationLevel=SERIALIZABLE', expected: 4 },
  { input: 'sqlserver://localhost;database=testdb;isolationLevel=SNAPSHOT', expected: 5 },
  { input: 'sqlserver://localhost;database=testdb;isolationLevel=READCOMMITTED', expected: 2 },
  { input: 'sqlserver://localhost;database=testdb;isolationLevel=read committed', expected: 2 },
];
for (const tc of testCases) {
  const config = parseConnectionString(tc.input);
  if (config.options?.isolationLevel !== tc.expected) {
    console.log('FAIL: For ' + tc.input + ' expected isolationLevel=' + tc.expected + ', got: ' + config.options?.isolationLevel);
    process.exit(1);
  }
}
console.log('ISOLATION_LEVEL_PARAMS_OK');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Isolation level params test failed:\n{r.stderr[-500:]}"
    assert "ISOLATION_LEVEL_PARAMS_OK" in r.stdout, f"Expected ISOLATION_LEVEL_PARAMS_OK, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_error_handling():
    """Repo CI - connection-string.ts throws appropriate errors for invalid input (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
const { parseConnectionString } = require('./src/connection-string.ts');
const errorCases = [
  { input: 'sqlserver://localhost:invalid;database=testdb', expected: 'Invalid port number' },
  { input: 'sqlserver://localhost;database=testdb;connectionLimit=invalid', expected: 'Invalid connection limit' },
  { input: 'sqlserver://localhost;database=testdb;connectTimeout=invalid', expected: 'Invalid connection timeout' },
  { input: 'sqlserver://;database=testdb', expected: 'Server host is required' },
  { input: 'sqlserver://', expected: 'Server host is required' },
];
for (const tc of errorCases) {
  try {
    parseConnectionString(tc.input);
    console.log('FAIL: Expected error for: ' + tc.input);
    process.exit(1);
  } catch (e) {
    if (!e.message.includes(tc.expected)) {
      console.log('FAIL: For ' + tc.input + ' expected error containing: ' + tc.expected + ', got: ' + e.message);
      process.exit(1);
    }
  }
}
console.log('ERROR_HANDLING_OK');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Error handling test failed:\n{r.stderr[-500:]}"
    assert "ERROR_HANDLING_OK" in r.stdout, f"Expected ERROR_HANDLING_OK, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_extract_schema_from_connection_string():
    """Repo CI - extractSchemaFromConnectionString works correctly (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsx", "-e", """
const { extractSchemaFromConnectionString } = require('./src/connection-string.ts');
const schema1 = extractSchemaFromConnectionString('sqlserver://localhost;database=testdb;schema=custom');
if (schema1 !== 'custom') {
  console.log('FAIL: Expected schema=custom, got: ' + schema1);
  process.exit(1);
}
const schema2 = extractSchemaFromConnectionString('sqlserver://localhost;schema=custom');
if (schema2 !== 'custom') {
  console.log('FAIL: Expected schema=custom without database, got: ' + schema2);
  process.exit(1);
}
const noSchema = extractSchemaFromConnectionString('sqlserver://localhost;database=testdb');
if (noSchema !== undefined) {
  console.log('FAIL: Expected undefined when no schema, got: ' + noSchema);
  process.exit(1);
}
const emptySchema = extractSchemaFromConnectionString('sqlserver://localhost;database=testdb;schema=');
if (emptySchema !== '') {
  console.log('FAIL: Expected empty string for schema=, got: ' + emptySchema);
  process.exit(1);
}
console.log('EXTRACT_SCHEMA_OK');
"""],
        capture_output=True, text=True, timeout=30, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Extract schema test failed:\n{r.stderr[-500:]}"
    assert "EXTRACT_SCHEMA_OK" in r.stdout, f"Expected EXTRACT_SCHEMA_OK, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_vitest_test_suite():
    """Repo CI - All vitest tests in connection-string.test.ts pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-lc", "npx vitest run src/connection-string.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=str(ADAPTER_DIR),
    )
    assert r.returncode == 0, f"Vitest test suite failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
    # Ensure all tests ran and passed
    assert "Tests" in r.stdout and "passed" in r.stdout, \
        f"Vitest output missing test summary:\n{r.stdout[-500:]}"
