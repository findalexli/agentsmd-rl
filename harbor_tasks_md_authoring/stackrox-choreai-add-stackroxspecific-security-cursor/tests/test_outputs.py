"""Behavioral checks for stackrox-choreai-add-stackroxspecific-security-cursor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stackrox")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/README.md')
    assert "- The [security/product-security](security/product-security/) directory is a clone of [Product Security's Cursor rules](https://gitlab.cee.redhat.com/product-security/security-cursor-rules)." in text, "expected to find: " + "- The [security/product-security](security/product-security/) directory is a clone of [Product Security's Cursor rules](https://gitlab.cee.redhat.com/product-security/security-cursor-rules)."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/README.md')
    assert "- Rules directly in [security/](security/) are Stackrox-specific rules that aren't currently covered by ProdSec rules." in text, "expected to find: " + "- Rules directly in [security/](security/) are Stackrox-specific rules that aren't currently covered by ProdSec rules."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/README.md')
    assert 'The rules in [security/](security/) provide security guidelines for Cursor to generate secure code/suggestions' in text, "expected to find: " + 'The rules in [security/](security/) provide security guidelines for Cursor to generate secure code/suggestions'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/common.mdc')
    assert '- Never hardcode secrets, passwords, or API keys. Use secure configuration management or vaults.' in text, "expected to find: " + '- Never hardcode secrets, passwords, or API keys. Use secure configuration management or vaults.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/common.mdc')
    assert '- Implement proper authentication and authorization. Verify permissions before granting access.' in text, "expected to find: " + '- Implement proper authentication and authorization. Verify permissions before granting access.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/common.mdc')
    assert '- Use strong encryption (AES-256, RSA-2048+). Avoid deprecated algorithms (DES, MD5, SHA-1).' in text, "expected to find: " + '- Use strong encryption (AES-256, RSA-2048+). Avoid deprecated algorithms (DES, MD5, SHA-1).'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/containers.mdc')
    assert '- Use minimal, up-to-date base images from trusted sources (official registries).' in text, "expected to find: " + '- Use minimal, up-to-date base images from trusted sources (official registries).'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/containers.mdc')
    assert '- Prefer distroless or minimal images (Alpine, scratch) to reduce attack surface.' in text, "expected to find: " + '- Prefer distroless or minimal images (Alpine, scratch) to reduce attack surface.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/containers.mdc')
    assert '- Never hardcode secrets, credentials, or API keys in Dockerfiles or images.' in text, "expected to find: " + '- Never hardcode secrets, credentials, or API keys in Dockerfiles or images.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/databases.mdc')
    assert '- Enable auditing and separate test from production databases.' in text, "expected to find: " + '- Enable auditing and separate test from production databases.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/databases.mdc')
    assert '- Use least privilege for application database access.' in text, "expected to find: " + '- Use least privilege for application database access.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/databases.mdc')
    assert '- Store connection strings securely and encrypted.' in text, "expected to find: " + '- Store connection strings securely and encrypted.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/groovy.mdc')
    assert '- Use parameterized queries (Groovy Sql with parameters) to prevent SQL injection. Never use GString interpolation in SQL.' in text, "expected to find: " + '- Use parameterized queries (Groovy Sql with parameters) to prevent SQL injection. Never use GString interpolation in SQL.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/groovy.mdc')
    assert '- Validate dynamic method calls when using ExpandoMetaClass, methodMissing, or other meta-programming.' in text, "expected to find: " + '- Validate dynamic method calls when using ExpandoMetaClass, methodMissing, or other meta-programming.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/groovy.mdc')
    assert '- Avoid `execute()` or `Process.start()` with untrusted input. Sanitize shell command arguments.' in text, "expected to find: " + '- Avoid `execute()` or `Process.start()` with untrusted input. Sanitize shell command arguments.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/helm.mdc')
    assert 'The directory "image/templates/helm" contains files that are used to generate the Stackrox helm charts. Many of them have the ".htpl" extension, which indicates they are templates from which helm char' in text, "expected to find: " + 'The directory "image/templates/helm" contains files that are used to generate the Stackrox helm charts. Many of them have the ".htpl" extension, which indicates they are templates from which helm char'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/helm.mdc')
    assert 'Stackrox uses a custom meta-templating system that processes `.htpl` files with build-time values (MetaValues) before standard Helm rendering. Meta-templates use `[<` and `>]` delimiters and Go text/t' in text, "expected to find: " + 'Stackrox uses a custom meta-templating system that processes `.htpl` files with build-time values (MetaValues) before standard Helm rendering. Meta-templates use `[<` and `>]` delimiters and Go text/t'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/helm.mdc')
    assert '- **Validate feature flag behavior**: Feature flags (e.g., `.FeatureFlags.ROX_SCANNER_V4`) can dramatically alter chart behavior. Ensure all code paths (enabled/disabled) maintain security properties.' in text, "expected to find: " + '- **Validate feature flag behavior**: Feature flags (e.g., `.FeatureFlags.ROX_SCANNER_V4`) can dramatically alter chart behavior. Ensure all code paths (enabled/disabled) maintain security properties.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/java.mdc')
    assert '- Use parameterized queries (PreparedStatement) to prevent SQL injection. Never concatenate user input into SQL.' in text, "expected to find: " + '- Use parameterized queries (PreparedStatement) to prevent SQL injection. Never concatenate user input into SQL.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/java.mdc')
    assert '- Avoid `Runtime.exec()` or `ProcessBuilder` with untrusted input. Sanitize command arguments.' in text, "expected to find: " + '- Avoid `Runtime.exec()` or `ProcessBuilder` with untrusted input. Sanitize command arguments.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/java.mdc')
    assert '- Never deserialize untrusted data. Avoid `ObjectInputStream` with external sources.' in text, "expected to find: " + '- Never deserialize untrusted data. Avoid `ObjectInputStream` with external sources.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/javascript.mdc')
    assert '- Prevent prototype pollution by validating object keys and using `Object.create(null)` when appropriate.' in text, "expected to find: " + '- Prevent prototype pollution by validating object keys and using `Object.create(null)` when appropriate.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/javascript.mdc')
    assert '- Use parameterized queries or ORMs to prevent SQL injection. Never concatenate user input into queries.' in text, "expected to find: " + '- Use parameterized queries or ORMs to prevent SQL injection. Never concatenate user input into queries.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/javascript.mdc')
    assert '- Avoid `eval()`, `Function()` constructor, or `setTimeout(string)` with untrusted data.' in text, "expected to find: " + '- Avoid `eval()`, `Function()` constructor, or `setTimeout(string)` with untrusted data.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/security_rules.mdc')
    assert '- **Authentication:** Use strong, standard authentication methods. Require authentication for all non-public areas. Store credentials securely and enforce password policies. Use multi-factor authentic' in text, "expected to find: " + '- **Authentication:** Use strong, standard authentication methods. Require authentication for all non-public areas. Store credentials securely and enforce password policies. Use multi-factor authentic'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/security_rules.mdc')
    assert '- **Authorization:** Enforce least privilege and explicit permissions. Use a single, trusted component for authorization checks. Deny by default and audit permissions regularly.' in text, "expected to find: " + '- **Authorization:** Enforce least privilege and explicit permissions. Use a single, trusted component for authorization checks. Deny by default and audit permissions regularly.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/security_rules.mdc')
    assert '- **Networking:** Encrypt all communications. Do not expose unnecessary endpoints or ports. Restrict network access to only what is required.' in text, "expected to find: " + '- **Networking:** Encrypt all communications. Do not expose unnecessary endpoints or ports. Restrict network access to only what is required.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/containers.mdc')
    assert '- Run containers as non-root and use read-only filesystems when possible.' in text, "expected to find: " + '- Run containers as non-root and use read-only filesystems when possible.'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/containers.mdc')
    assert '- Remove non-essential software and keep essential ones updated.' in text, "expected to find: " + '- Remove non-essential software and keep essential ones updated.'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/containers.mdc')
    assert '- Use minimal, up-to-date base images from trusted sources.' in text, "expected to find: " + '- Use minimal, up-to-date base images from trusted sources.'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/databases.mdc')
    assert '- Enable auditing and separate test from production databases.' in text, "expected to find: " + '- Enable auditing and separate test from production databases.'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/databases.mdc')
    assert '- Use least privilege for application database access.' in text, "expected to find: " + '- Use least privilege for application database access.'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/databases.mdc')
    assert '- Store connection strings securely and encrypted.' in text, "expected to find: " + '- Store connection strings securely and encrypted.'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/go.mdc')
    assert '- Log errors securely, avoiding leaks of sensitive data like credentials or tokens.' in text, "expected to find: " + '- Log errors securely, avoiding leaks of sensitive data like credentials or tokens.'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/go.mdc')
    assert '- Avoid using `fmt.Sprintf()` to build SQL or shell commands.' in text, "expected to find: " + '- Avoid using `fmt.Sprintf()` to build SQL or shell commands.'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/go.mdc')
    assert '- Use parameterized queries to prevent SQL injection.' in text, "expected to find: " + '- Use parameterized queries to prevent SQL injection.'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/helm.mdc')
    assert '- Check for vulnerable dependencies and validate chart provenance.' in text, "expected to find: " + '- Check for vulnerable dependencies and validate chart provenance.'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/helm.mdc')
    assert '- Secure configuration and manage secrets outside of values.yaml.' in text, "expected to find: " + '- Secure configuration and manage secrets outside of values.yaml.'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/helm.mdc')
    assert 'description: Secure coding rules for Helm charts ⎈' in text, "expected to find: " + 'description: Secure coding rules for Helm charts ⎈'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/kafka.mdc')
    assert 'description: Secure coding rules for Kafka and AMQ Streams 📨' in text, "expected to find: " + 'description: Secure coding rules for Kafka and AMQ Streams 📨'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/kafka.mdc')
    assert '- Apply access control lists (ACLs) to limit topic access.' in text, "expected to find: " + '- Apply access control lists (ACLs) to limit topic access.'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/kafka.mdc')
    assert '- Use authentication (SSL/SASL) for all connections.' in text, "expected to find: " + '- Use authentication (SSL/SASL) for all connections.'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/llm.mdc')
    assert '- Enforce strict input validation and privilege control for LLM plugins and APIs.' in text, "expected to find: " + '- Enforce strict input validation and privilege control for LLM plugins and APIs.'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/llm.mdc')
    assert '- Apply regularization and differential privacy to protect training data.' in text, "expected to find: " + '- Apply regularization and differential privacy to protect training data.'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/llm.mdc')
    assert 'description: Secure coding rules for Large Language Models (LLM) 🤖' in text, "expected to find: " + 'description: Secure coding rules for Large Language Models (LLM) 🤖'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/mcp.mdc')
    assert '- Authenticate and authorize actions using the privileges of the principal (for example, the user) initiating the interaction, via standard authentication protocols (such as OAuth).' in text, "expected to find: " + '- Authenticate and authorize actions using the privileges of the principal (for example, the user) initiating the interaction, via standard authentication protocols (such as OAuth).'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/mcp.mdc')
    assert '- All actions executed by the MCP server must be traceable to the authenticated principal and conform to their permissions and scope.' in text, "expected to find: " + '- All actions executed by the MCP server must be traceable to the authenticated principal and conform to their permissions and scope.'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/mcp.mdc')
    assert '- Implement logging the tools and the parameters to be called as well as the outputs from the tools.' in text, "expected to find: " + '- Implement logging the tools and the parameters to be called as well as the outputs from the tools.'[:80]


def test_signal_48():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/operators.mdc')
    assert '- Use the most restrictive Security Context Constraints (SCCs), such as restricted or restricted-v2, to enforce policies. This disallows privileged containers, prevents containers from running as root' in text, "expected to find: " + '- Use the most restrictive Security Context Constraints (SCCs), such as restricted or restricted-v2, to enforce policies. This disallows privileged containers, prevents containers from running as root'[:80]


def test_signal_49():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/operators.mdc')
    assert '- If the workload exposes any endpoints (like metrics), add authentication unless they are intended for public access. This is a crucial security practice that protects against future data exposure, e' in text, "expected to find: " + '- If the workload exposes any endpoints (like metrics), add authentication unless they are intended for public access. This is a crucial security practice that protects against future data exposure, e'[:80]


def test_signal_50():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/operators.mdc')
    assert '- Ensure operator containers are mounted as read-only by setting “readOnlyRootFilesystem: true”. This prevents the container from writing to the root filesystem, which is a powerful defense against at' in text, "expected to find: " + '- Ensure operator containers are mounted as read-only by setting “readOnlyRootFilesystem: true”. This prevents the container from writing to the root filesystem, which is a powerful defense against at'[:80]


def test_signal_51():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/python.mdc')
    assert '- Avoid shell execution with untrusted input. Use `subprocess.run([...], check=True)` instead of `os.system()`.' in text, "expected to find: " + '- Avoid shell execution with untrusted input. Use `subprocess.run([...], check=True)` instead of `os.system()`.'[:80]


def test_signal_52():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/python.mdc')
    assert '- Pin exact versions in `requirements.txt` or `pyproject.toml`. Avoid using `*` or `latest`.' in text, "expected to find: " + '- Pin exact versions in `requirements.txt` or `pyproject.toml`. Avoid using `*` or `latest`.'[:80]


def test_signal_53():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/python.mdc')
    assert '- Handle exceptions securely; avoid exposing debug traces or stack dumps to users.' in text, "expected to find: " + '- Handle exceptions securely; avoid exposing debug traces or stack dumps to users.'[:80]


def test_signal_54():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/react.mdc')
    assert '- Secure server-side rendering and avoid JSON injection.' in text, "expected to find: " + '- Secure server-side rendering and avoid JSON injection.'[:80]


def test_signal_55():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/react.mdc')
    assert 'description: Secure coding rules for React projects ⚛️' in text, "expected to find: " + 'description: Secure coding rules for React projects ⚛️'[:80]


def test_signal_56():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/react.mdc')
    assert '- Sanitize HTML before using dangerouslySetInnerHTML.' in text, "expected to find: " + '- Sanitize HTML before using dangerouslySetInnerHTML.'[:80]


def test_signal_57():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/rust.mdc')
    assert '- Prefer crates with broader community adoption, which have more downloads, more github stars, are used in major projects' in text, "expected to find: " + '- Prefer crates with broader community adoption, which have more downloads, more github stars, are used in major projects'[:80]


def test_signal_58():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/rust.mdc')
    assert '- Prevent buffer overflows by using safe indexing methods (e.g., `get()`, `get_mut()`) and validating input sizes' in text, "expected to find: " + '- Prevent buffer overflows by using safe indexing methods (e.g., `get()`, `get_mut()`) and validating input sizes'[:80]


def test_signal_59():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/product-security/technology/rust.mdc')
    assert '- Prefer using crates with less dependencies, utilize crate features, in order to limit indirect dependencies' in text, "expected to find: " + '- Prefer using crates with less dependencies, utilize crate features, in order to limit indirect dependencies'[:80]


def test_signal_60():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/shell.mdc')
    assert '- Validate and sanitize all external input (user input, command-line arguments, environment variables).' in text, "expected to find: " + '- Validate and sanitize all external input (user input, command-line arguments, environment variables).'[:80]


def test_signal_61():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/shell.mdc')
    assert '- Use parameter expansion with defaults (${var:-default}) to handle unset variables safely.' in text, "expected to find: " + '- Use parameter expansion with defaults (${var:-default}) to handle unset variables safely.'[:80]


def test_signal_62():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/shell.mdc')
    assert '- Use specific interpreters in shebang (#!/bin/bash not #!/bin/sh if using bash features).' in text, "expected to find: " + '- Use specific interpreters in shebang (#!/bin/bash not #!/bin/sh if using bash features).'[:80]


def test_signal_63():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/typescript.mdc')
    assert '- Use parameterized queries or ORMs to prevent SQL injection. Never concatenate user input into queries.' in text, "expected to find: " + '- Use parameterized queries or ORMs to prevent SQL injection. Never concatenate user input into queries.'[:80]


def test_signal_64():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/typescript.mdc')
    assert '- Use type guards for runtime validation. Validate external data at runtime, not just compile time.' in text, "expected to find: " + '- Use type guards for runtime validation. Validate external data at runtime, not just compile time.'[:80]


def test_signal_65():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/security/typescript.mdc')
    assert '- Avoid `eval()`, `Function()` constructor, or dynamic code execution with untrusted data.' in text, "expected to find: " + '- Avoid `eval()`, `Function()` constructor, or dynamic code execution with untrusted data.'[:80]

