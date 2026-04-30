#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cursor-security-rules

# Idempotency guard
if grep -qF "- **Rule:** Never hardcode secrets such as API Keys, private keys or credentials" "secure-dev-node.mdc" && grep -qF "- **Rule:** Logs must not contain passwords, tokens, API keys, private keys, or " "secure-dev-python.mdc" && grep -qF "- **Rule:** Secrets such as API keys, credentials, private keys, or tokens must " "secure-development-principles.mdc" && grep -qF "- **Examples of Sensitive Data:** Passwords, API keys, authentication tokens, em" "secure-mcp-usage.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/secure-dev-node.mdc b/secure-dev-node.mdc
@@ -20,7 +20,7 @@ Generated code must not violate these rules. If a rule is violated, a comment mu
 - **Rule:** Do not use `execSync`, `spawnSync`, or shell execution functions with untrusted input. Avoid them unless strictly necessary and audited.
 
 ## 4. Use Environment Variables for Secrets
-- **Rule:** Never hardcode secrets such as API keys or credentials. Use environment variables and secure configuration loading.
+- **Rule:** Never hardcode secrets such as API Keys, private keys or credentials. Use environment variables and secure configuration loading.
 
 ## 5. Sanitize and Validate All External Input
 - **Rule:** All inputs (query params, request bodies, headers) must be validated and sanitized before use in logic, queries, or file access.
diff --git a/secure-dev-python.mdc b/secure-dev-python.mdc
@@ -25,7 +25,7 @@ don't generate code that violates these rules.
 - **Rule:** Use `hmac.compare_digest()` for comparing secrets like tokens, passwords, or signatures to prevent timing attacks.
 
 ## 5. Do Not Log Sensitive Data
-- **Rule:** Logs must not contain passwords, tokens, API keys, or personally identifiable information (PII).
+- **Rule:** Logs must not contain passwords, tokens, API keys, private keys, or personally identifiable information (PII).
 
 ## 6. Avoid Subprocess Calls with User Input
 - **Rule:** Avoid using `os.system`, `subprocess.run`, or similar functions. Use parameterized APIs or sandboxed environments if needed.
diff --git a/secure-development-principles.mdc b/secure-development-principles.mdc
@@ -14,7 +14,7 @@ All violations must include a clear explanation of which rule was triggered and
 - **Rule:** Untrusted input must never be used directly in file access, command execution, database queries, or similar sensitive operations.
 
 ## 2. Do Not Expose Secrets in Public Code
-- **Rule:** Secrets such as API keys, credentials, or tokens must not appear in frontend code, public repositories, or client-distributed files.
+- **Rule:** Secrets such as API keys, credentials, private keys, or tokens must not appear in frontend code, public repositories, or client-distributed files.
 
 ## 3. Enforce Secure Communication Protocols
 - **Rule:** Only secure protocols (e.g., HTTPS, TLS) must be used for all external communications.
diff --git a/secure-mcp-usage.mdc b/secure-mcp-usage.mdc
@@ -13,7 +13,7 @@ These rules apply to all code and systems integrating with MCP (Model Context Pr
 ## 2. Do Not Send Sensitive Data or PII to MCP.
 - **Rule:** Do not transmit credentials, tokens, or personally identifiable information (PII) through MCP requests or responses. if it's sensitive information don't use it in parameters in any way.
 - **Clarification:** Treat all user-supplied input as potentially sensitive. If there is any doubt about the sensitivity of a value, do not use it as a parameter or transmit it in any way.
-- **Examples of Sensitive Data:** Passwords, API keys, authentication tokens, email addresses, phone numbers, government-issued IDs, or any data that could be used to identify or authenticate a user.
+- **Examples of Sensitive Data:** Passwords, API keys, authentication tokens, email addresses, phone numbers, government-issued IDs, private keys, or any data that could be used to identify or authenticate a user.
 - **Scope:** This rule applies to all tool calls, API requests, file operations, and any other form of data transmission within the MCP system.
 
 ## 3. Do Not Add or Edit Files Based on MCP Interactions
PATCH

echo "Gold patch applied."
