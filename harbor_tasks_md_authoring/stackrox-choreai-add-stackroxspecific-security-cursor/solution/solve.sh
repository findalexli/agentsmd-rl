#!/usr/bin/env bash
set -euo pipefail

cd /workspace/stackrox

# Idempotency guard
if grep -qF "- The [security/product-security](security/product-security/) directory is a clo" ".cursor/rules/README.md" && grep -qF "- Never hardcode secrets, passwords, or API keys. Use secure configuration manag" ".cursor/rules/security/common.mdc" && grep -qF "- Use minimal, up-to-date base images from trusted sources (official registries)" ".cursor/rules/security/containers.mdc" && grep -qF "- Enable auditing and separate test from production databases." ".cursor/rules/security/databases.mdc" && grep -qF "- Use parameterized queries (Groovy Sql with parameters) to prevent SQL injectio" ".cursor/rules/security/groovy.mdc" && grep -qF "The directory \"image/templates/helm\" contains files that are used to generate th" ".cursor/rules/security/helm.mdc" && grep -qF "- Use parameterized queries (PreparedStatement) to prevent SQL injection. Never " ".cursor/rules/security/java.mdc" && grep -qF "- Prevent prototype pollution by validating object keys and using `Object.create" ".cursor/rules/security/javascript.mdc" && grep -qF "- **Authentication:** Use strong, standard authentication methods. Require authe" ".cursor/rules/security/product-security/security_rules.mdc" && grep -qF "- Run containers as non-root and use read-only filesystems when possible." ".cursor/rules/security/product-security/technology/containers.mdc" && grep -qF "- Enable auditing and separate test from production databases." ".cursor/rules/security/product-security/technology/databases.mdc" && grep -qF "- Log errors securely, avoiding leaks of sensitive data like credentials or toke" ".cursor/rules/security/product-security/technology/go.mdc" && grep -qF "- Check for vulnerable dependencies and validate chart provenance." ".cursor/rules/security/product-security/technology/helm.mdc" && grep -qF "description: Secure coding rules for Kafka and AMQ Streams \ud83d\udce8" ".cursor/rules/security/product-security/technology/kafka.mdc" && grep -qF "- Enforce strict input validation and privilege control for LLM plugins and APIs" ".cursor/rules/security/product-security/technology/llm.mdc" && grep -qF "- Authenticate and authorize actions using the privileges of the principal (for " ".cursor/rules/security/product-security/technology/mcp.mdc" && grep -qF "- Use the most restrictive Security Context Constraints (SCCs), such as restrict" ".cursor/rules/security/product-security/technology/operators.mdc" && grep -qF "- Avoid shell execution with untrusted input. Use `subprocess.run([...], check=T" ".cursor/rules/security/product-security/technology/python.mdc" && grep -qF "- Secure server-side rendering and avoid JSON injection." ".cursor/rules/security/product-security/technology/react.mdc" && grep -qF "- Prefer crates with broader community adoption, which have more downloads, more" ".cursor/rules/security/product-security/technology/rust.mdc" && grep -qF "- Validate and sanitize all external input (user input, command-line arguments, " ".cursor/rules/security/shell.mdc" && grep -qF "- Use parameterized queries or ORMs to prevent SQL injection. Never concatenate " ".cursor/rules/security/typescript.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/README.md b/.cursor/rules/README.md
@@ -2,4 +2,9 @@
 
 This directory contains a set of [Cursor project rules](https://docs.cursor.com/en/context/rules#project-rules), to steer Cursor's suggestions in ways that benefit the Stackrox development.
 
-The rules in [product-security](product-security/) are imported from [Product Security's Cursor rules](https://gitlab.cee.redhat.com/product-security/security-cursor-rules).
+## Security
+
+The rules in [security/](security/) provide security guidelines for Cursor to generate secure code/suggestions
+
+- The [security/product-security](security/product-security/) directory is a clone of [Product Security's Cursor rules](https://gitlab.cee.redhat.com/product-security/security-cursor-rules).
+- Rules directly in [security/](security/) are Stackrox-specific rules that aren't currently covered by ProdSec rules.
diff --git a/.cursor/rules/security/common.mdc b/.cursor/rules/security/common.mdc
@@ -0,0 +1,17 @@
+---
+description: Common secure coding rules for all languages
+alwaysApply: false
+---
+
+# Secure coding rules common to all languages
+
+- Validate and sanitize all input from external sources (user input, APIs, files).
+- Never hardcode secrets, passwords, or API keys. Use secure configuration management or vaults.
+- Use strong encryption (AES-256, RSA-2048+). Avoid deprecated algorithms (DES, MD5, SHA-1).
+- Implement proper authentication and authorization. Verify permissions before granting access.
+- Handle exceptions securely. Never expose stack traces or internal details to users.
+- Validate file paths to prevent traversal attacks. Check canonical paths before operations.
+- Use HTTPS/TLS for all network communications. Validate certificates.
+- Keep dependencies current. Pin specific versions and audit for vulnerabilities.
+- Apply least privilege. Grant minimal permissions.
+- Log security events but never log sensitive data (passwords, tokens, PII).
diff --git a/.cursor/rules/security/containers.mdc b/.cursor/rules/security/containers.mdc
@@ -0,0 +1,47 @@
+---
+description: Secure coding rules for Stackrox Containers
+globs:
+  - "**/Containerfile"
+  - "**/*Dockerfile*"
+alwaysApply: false
+---
+
+# Secure coding rules for Containers
+
+## Base Image Security
+
+- Use minimal, up-to-date base images from trusted sources (official registries).
+- Prefer distroless or minimal images (Alpine, scratch) to reduce attack surface.
+- Pin specific image versions using digest (sha256) rather than tags.
+- Remove non-essential software and keep essential packages updated.
+- Regularly scan base images for vulnerabilities and update promptly.
+
+## Runtime Security
+
+- Run containers as non-root user (USER directive with non-zero UID).
+- Use read-only root filesystems where possible.
+- Drop all Linux capabilities and add only those required.
+- Set resource limits (CPU, memory) to prevent resource exhaustion.
+- Avoid privileged containers unless absolutely necessary.
+
+## Secret Management
+
+- Never hardcode secrets, credentials, or API keys in Dockerfiles or images.
+- Never include secrets in environment variables visible in image layers.
+- Use build-time secrets with BuildKit's --secret flag for build-time needs.
+- Mount secrets as volumes at runtime rather than embedding in images.
+- Remove sensitive data and build artifacts in the same RUN layer.
+
+## Network Isolation
+
+- Minimize exposed ports and only expose what is necessary.
+- Use specific port numbers rather than ranges.
+- Implement network policies to restrict container communication.
+- Use internal networks for inter-container communication.
+
+## Image Integrity
+
+- Sign container images and verify signatures before deployment.
+- Use image scanning tools (Clair, Trivy, Grype) in CI/CD pipelines.
+- Implement admission controllers to enforce security policies.
+- Regularly audit images for vulnerabilities and compliance.
diff --git a/.cursor/rules/security/databases.mdc b/.cursor/rules/security/databases.mdc
@@ -0,0 +1,14 @@
+---
+description: Secure coding rules for Databases
+globs:
+  - "image/postgres/*"
+  - "pkg/postgres/*"
+alwaysApply: false
+---
+
+# Secure coding rules for databases
+
+- Encrypt communication and data at rest.
+- Enable auditing and separate test from production databases.
+- Use least privilege for application database access.
+- Store connection strings securely and encrypted.
diff --git a/.cursor/rules/security/groovy.mdc b/.cursor/rules/security/groovy.mdc
@@ -0,0 +1,18 @@
+---
+description: Secure coding rules for Groovy projects
+globs:
+  - "**/*.groovy"
+  - "**/*.gradle"
+  - "**/*.gvy"
+alwaysApply: false
+---
+
+# Secure coding rules for Groovy
+
+- Use parameterized queries (Groovy Sql with parameters) to prevent SQL injection. Never use GString interpolation in SQL.
+- Avoid `execute()` or `Process.start()` with untrusted input. Sanitize shell command arguments.
+- Avoid `Eval.me()` and `GroovyShell.evaluate()` with untrusted code.
+- Use `SecureRandom` for cryptographic operations, not `Random`.
+- Validate dynamic method calls when using ExpandoMetaClass, methodMissing, or other meta-programming.
+- Disable external entity processing in XML parsers (XmlSlurper/XmlParser) to prevent XXE.
+- Sanitize data before using in closures or meta-programming.
diff --git a/.cursor/rules/security/helm.mdc b/.cursor/rules/security/helm.mdc
@@ -0,0 +1,102 @@
+---
+description: Secure coding rules for Stackrox Helm charts
+globs:
+  - "image/templates/helm/**"
+alwaysApply: false
+---
+
+# Secure coding rules for Helm charts
+
+The directory "image/templates/helm" contains files that are used to generate the Stackrox helm charts. Many of them have the ".htpl" extension, which indicates they are templates from which helm charts will be rendered. When working with any files in that directory always follow these instructions:
+
+## General Security
+
+- Check for vulnerable dependencies and validate chart provenance.
+- Manage secrets outside of values.yaml. Use Kubernetes Secrets or external secret management solutions.
+- Use tools like checkov or kubesec for security scanning.
+- Never hardcode credentials, API keys, or sensitive data in chart templates or values files.
+
+## RBAC and Access Control
+
+- Define minimal RBAC permissions. Use Role/RoleBinding for namespace-scoped access.
+- Avoid ClusterRole/ClusterRoleBinding unless absolutely necessary.
+- Never grant wildcard permissions (`*`) on resources or verbs.
+- Create dedicated ServiceAccounts for each component rather than using default.
+
+## Pod Security
+
+- Set securityContext for all pods and containers.
+- Run containers as non-root user (runAsNonRoot: true).
+- Drop all capabilities and add only those required (drop: [ALL]).
+- Use read-only root filesystem where possible (readOnlyRootFilesystem: true).
+- Set allowPrivilegeEscalation: false.
+- Apply Pod Security Standards (restricted profile preferred).
+
+## Resource Management
+
+- Define resource requests and limits for all containers.
+- Set appropriate memory and CPU limits to prevent resource exhaustion.
+- Configure liveness and readiness probes for all deployments.
+- Use PodDisruptionBudgets for high-availability workloads.
+
+## Network Security
+
+- Define NetworkPolicies to restrict pod-to-pod communication.
+- Use least privilege network access (deny by default, allow specific).
+- Ensure services use ClusterIP unless external access is required.
+- Use TLS/mTLS for inter-service communication.
+
+## Meta-Templating Security (`.htpl` files)
+
+Stackrox uses a custom meta-templating system that processes `.htpl` files with build-time values (MetaValues) before standard Helm rendering. Meta-templates use `[<` and `>]` delimiters and Go text/template syntax.
+
+### Input Validation and Injection Prevention
+
+- **Validate all MetaValues**: Even though MetaValues come from the build process, validate image references, registry URLs, version strings, and other inputs before use.
+- **Use `required` function**: Always use `required` for critical MetaValues that must be present (e.g., `[< required "" .Versions.ChartVersion >]`).
+- **Sanitize string interpolation**: When injecting MetaValues into YAML/templates, ensure proper quoting and escaping to prevent injection attacks.
+- **Avoid dynamic code execution**: Never use meta-templating to generate executable code or shell commands from MetaValues without strict validation.
+
+### Feature Flag Security
+
+- **Validate feature flag behavior**: Feature flags (e.g., `.FeatureFlags.ROX_SCANNER_V4`) can dramatically alter chart behavior. Ensure all code paths (enabled/disabled) maintain security properties.
+- **Test all combinations**: Critical security features (RBAC, NetworkPolicies, Pod Security) must be tested with different feature flag combinations.
+- **Document security implications**: When using feature flags in meta-templates, document how they affect security posture.
+- **Never use feature flags for security controls**: Feature flags should control features, not bypass security mechanisms.
+
+### Image Reference Security
+
+- **Validate image references**: Image names, tags, and registries injected via MetaValues (.ImageRemote, .ImageTag, .MainRegistry, etc.) must be validated.
+- **Use immutable tags or digests**: Prefer image digests over mutable tags where possible for reproducible builds.
+- **Restrict image sources**: Only allow images from trusted registries. Never construct image references from untrusted input.
+- **Avoid latest tags**: Never use `latest` or other mutable tags in production configurations.
+
+### Secrets and Sensitive Data
+
+- **Never embed secrets in MetaValues**: MetaValues may be embedded in compiled binaries (roxctl, operator). Never include passwords, API keys, or certificates.
+- **No credentials in .htpl files**: Meta-templates should never contain hardcoded credentials or sensitive data.
+- **Validate secret references**: If meta-templates reference Kubernetes secrets, ensure the references (names, keys) are validated.
+
+### Template Function Safety
+
+- **Limit use of dangerous functions**: Avoid functions that can access filesystem, execute commands, or perform network operations in meta-templates.
+- **Validate sprig function usage**: When using sprig functions (like `randAlphaNum`, `b64enc`), ensure they don't introduce security issues.
+- **No arbitrary code execution**: Never use meta-templating to evaluate arbitrary expressions from external input.
+
+### Build-Time Security
+
+- **Audit meta-template changes**: Changes to `.htpl` files affect all chart instantiations. Require security review for these changes.
+- **Version compatibility**: Ensure meta-template changes maintain backward compatibility and don't weaken security in older versions.
+- **Reproducible builds**: Meta-templating should produce deterministic output for the same MetaValues to enable security auditing.
+
+### Conditional Logic Security
+
+- **Secure all branches**: When using conditionals (e.g., `[< if .FeatureFlags.X >]`), ensure both branches maintain security properties.
+- **Avoid security by obscurity**: Don't rely on feature flags or conditional logic to hide security issues.
+- **Test negative cases**: Test that disabled features don't leave security holes (e.g., disabled admission controller doesn't bypass policy enforcement).
+
+### File Inclusion and Templating
+
+- **Validate file paths**: If meta-templates load files (.helmtplignore.htpl, config files), validate paths to prevent directory traversal.
+- **Secure .helmtplignore.htpl**: This file can exclude resources based on meta-values. Ensure it doesn't exclude critical security resources.
+- **No arbitrary file inclusion**: Never include files based on untrusted MetaValues or user input.
diff --git a/.cursor/rules/security/java.mdc b/.cursor/rules/security/java.mdc
@@ -0,0 +1,19 @@
+---
+description: Secure coding rules for Java projects
+globs:
+  - "**/*.java"
+  - "**/pom.xml"
+  - "**/build.gradle"
+  - "**/build.gradle.kts"
+alwaysApply: false
+---
+
+# Secure coding rules for Java
+
+- Use parameterized queries (PreparedStatement) to prevent SQL injection. Never concatenate user input into SQL.
+- Avoid `Runtime.exec()` or `ProcessBuilder` with untrusted input. Sanitize command arguments.
+- Never deserialize untrusted data. Avoid `ObjectInputStream` with external sources.
+- Use `SecureRandom` for cryptographic operations, not `Random`.
+- Set secure HTTP headers (Content-Security-Policy, X-Frame-Options, etc.).
+- Disable DTD/external entity processing in XML parsers to prevent XXE.
+- Validate data before using in reflection or class loading.
diff --git a/.cursor/rules/security/javascript.mdc b/.cursor/rules/security/javascript.mdc
@@ -0,0 +1,26 @@
+---
+description: Secure coding rules for JavaScript projects
+globs:
+  - "**/*.js"
+  - "**/*.mjs"
+  - "**/*.cjs"
+  - "**/package.json"
+  - "**/package-lock.json"
+alwaysApply: false
+---
+
+# Secure coding rules for JavaScript
+
+- Use parameterized queries or ORMs to prevent SQL injection. Never concatenate user input into queries.
+- Avoid `eval()`, `Function()` constructor, or `setTimeout(string)` with untrusted data.
+- Sanitize HTML to prevent XSS. Use DOMPurify or similar for user-generated HTML.
+- Implement Content Security Policy (CSP) headers to mitigate XSS and injection attacks.
+- Validate and sanitize URLs before redirects to prevent open redirects.
+- Implement proper authentication and session management. Use secure, httpOnly cookies.
+- Use `crypto.randomBytes()` or Web Crypto API for secure random generation.
+- Use `npm audit` regularly to check for vulnerabilities.
+- Pin exact versions in package-lock.json. Avoid `^` or `~` for critical dependencies.
+- Implement rate limiting and input validation to prevent DoS.
+- Prevent prototype pollution by validating object keys and using `Object.create(null)` when appropriate.
+- Use strict mode (`'use strict'`) to catch common mistakes and unsafe actions.
+- Implement proper CORS policies. Never use wildcard (`*`) origins in production.
diff --git a/.cursor/rules/security/product-security/security_rules.mdc b/.cursor/rules/security/product-security/security_rules.mdc
@@ -0,0 +1,30 @@
+---
+description: Global security rules for all projects 🛡️
+globs:
+  - "**/*"
+alwaysApply: true
+---
+
+# Security Principles
+
+- **Complete Mediation:** Ensure every access request is validated and authorized. No bypasses allowed.
+- **Compromise Recording:** Implement mechanisms to detect, record, and respond to security breaches.
+- **Defense in Depth:** Use multiple, layered security controls to protect systems and data.
+- **Economy of Mechanism:** Keep designs simple and easy to understand. Avoid unnecessary complexity.
+- **Least Common Mechanism:** Minimize shared resources and isolate components to reduce risk.
+- **Least Privilege:** Grant only the minimum permissions necessary for users and systems.
+- **Open Design:** Favor transparency and well-understood mechanisms over security by obscurity.
+- **Psychological Acceptability:** Make security controls user-friendly and aligned with user expectations.
+- **Secure by Design, Default, Deployment (SD3):** Ship with secure defaults, deny by default, and avoid hardcoded credentials.
+
+# Security Controls
+
+- **Authentication:** Use strong, standard authentication methods. Require authentication for all non-public areas. Store credentials securely and enforce password policies. Use multi-factor authentication where possible.
+- **Authorization:** Enforce least privilege and explicit permissions. Use a single, trusted component for authorization checks. Deny by default and audit permissions regularly.
+- **Encryption:** Encrypt all network traffic and data at rest where applicable. Use approved certificates and protocols.
+- **Logging:** Log security events centrally. Do not log sensitive data. Restrict log access and monitor for suspicious activity.
+- **Networking:** Encrypt all communications. Do not expose unnecessary endpoints or ports. Restrict network access to only what is required.
+
+---
+
+Apply these rules to all code, infrastructure, and processes to maintain a strong security posture across your projects.
diff --git a/.cursor/rules/security/product-security/technology/containers.mdc b/.cursor/rules/security/product-security/technology/containers.mdc
@@ -0,0 +1,11 @@
+---
+description: Secure coding rules for Containers 🐳
+globs:
+  - "**/Containerfile"
+  - "**/Dockerfile"
+alwaysApply: false
+---
+
+- Use minimal, up-to-date base images from trusted sources.
+- Remove non-essential software and keep essential ones updated.
+- Run containers as non-root and use read-only filesystems when possible.
diff --git a/.cursor/rules/security/product-security/technology/databases.mdc b/.cursor/rules/security/product-security/technology/databases.mdc
@@ -0,0 +1,12 @@
+---
+description: Secure coding rules for Databases 🗄️
+globs:
+  - "**/database*"
+  - "**/*.sql"
+alwaysApply: false
+---
+
+- Encrypt communication and data at rest.
+- Enable auditing and separate test from production databases.
+- Use least privilege for application database access.
+- Store connection strings securely and encrypted.
diff --git a/.cursor/rules/security/product-security/technology/go.mdc b/.cursor/rules/security/product-security/technology/go.mdc
@@ -0,0 +1,16 @@
+---
+description: Secure coding rules for Go projects 🦫
+globs:
+  - "**/*.go"
+  - "**/go.mod"
+  - "**/go.sum"
+alwaysApply: false
+---
+
+- Use Go modules for dependency management.
+- Validate all input entries.
+- Use html/template for output to prevent XSS.
+- Use parameterized queries to prevent SQL injection.
+- Avoid using `fmt.Sprintf()` to build SQL or shell commands.
+- Encrypt sensitive information and enforce HTTPS.
+- Log errors securely, avoiding leaks of sensitive data like credentials or tokens.
diff --git a/.cursor/rules/security/product-security/technology/helm.mdc b/.cursor/rules/security/product-security/technology/helm.mdc
@@ -0,0 +1,11 @@
+---
+description: Secure coding rules for Helm charts ⎈
+globs:
+  - "**/Chart.yaml"
+  - "**/values.yaml"
+alwaysApply: false
+---
+
+- Check for vulnerable dependencies and validate chart provenance.
+- Secure configuration and manage secrets outside of values.yaml.
+- Use tools like checkov for security scanning.
diff --git a/.cursor/rules/security/product-security/technology/kafka.mdc b/.cursor/rules/security/product-security/technology/kafka.mdc
@@ -0,0 +1,12 @@
+---
+description: Secure coding rules for Kafka and AMQ Streams 📨
+globs:
+  - "**/kafka*"
+  - "**/amq*"
+alwaysApply: false
+---
+
+- Encrypt data in transit using TLS/SSL.
+- Use authentication (SSL/SASL) for all connections.
+- Apply access control lists (ACLs) to limit topic access.
+- Monitor and alert on abnormal access patterns.
diff --git a/.cursor/rules/security/product-security/technology/llm.mdc b/.cursor/rules/security/product-security/technology/llm.mdc
@@ -0,0 +1,11 @@
+---
+description: Secure coding rules for Large Language Models (LLM) 🤖
+globs:
+  - "**/llm*"
+alwaysApply: false
+---
+
+- Enforce strict input validation and privilege control for LLM plugins and APIs.
+- Prevent prompt injection and insecure output handling.
+- Limit LLM access to sensitive APIs and data sources.
+- Apply regularization and differential privacy to protect training data.
diff --git a/.cursor/rules/security/product-security/technology/mcp.mdc b/.cursor/rules/security/product-security/technology/mcp.mdc
@@ -0,0 +1,15 @@
+---
+description: Secure coding rules for Model Context Protocol (MCP) clients and servers
+globs:
+  - "**/*mcp*"
+alwaysApply: false
+---
+
+- Authenticate and authorize actions using the privileges of the principal (for example, the user) initiating the interaction, via standard authentication protocols (such as OAuth).
+- Don't let servers use their own credentials to perform actions on behalf of the user.
+- All actions executed by the MCP server must be traceable to the authenticated principal and conform to their permissions and scope.
+- Prevent prompt injection.
+- Prevent command injection.
+- Prevent API call injection.
+- Implement logging the tools and the parameters to be called as well as the outputs from the tools.
+- MCP clients must request the approval from the user before calling actions from an MCP server.
diff --git a/.cursor/rules/security/product-security/technology/operators.mdc b/.cursor/rules/security/product-security/technology/operators.mdc
@@ -0,0 +1,29 @@
+---
+description: Secure coding rules for Kubernetes Operators ⚙️
+globs:
+  - "**/operator*"
+alwaysApply: false
+---
+
+- Restrict access to sensitive resources (e.g., secrets) by using Role-Based Access Control (RBAC) and the Principle of Least Privilege.
+- To minimize cluster and namespace permissions, create dedicated roles for each workload with only the necessary permissions and avoid using wildcards. Never use service accounts with cluster-admin or similar broad privileges.
+- Isolate operator workloads by deploying them in dedicated namespaces. This prevents a compromise from spreading and affecting other workloads in the cluster.
+- Instead of using default service accounts, create dedicated ones with only the minimum necessary permissions for your workload.
+- Store all credentials and sensitive information in Secrets instead of hard-coding them in configuration files or environment variables.
+- Ensure all communications are encrypted with TLS 1.2 or 1.3 (recommended).
+- If using an older TLS version for compatibility, ensure all workloads have updated TLS configurations with weak cipher suites disabled.
+- Define CPU and memory resource requests and limits to prevent resource exhaustion.
+- Establish network policies with a "deny all" default for ingress and egress traffic. Explicitly define specific allow rules to control flow between pods, namespaces, and external services.
+- Use certificates issued by an Openshift trusted CA.
+- Avoid outdated dependencies. Replace deprecated and obsolete libraries with modern alternatives.
+- Avoid or redact sensitive information in logs and error messages.
+- Ensure the audit log captures enough detail for effective incident investigation.
+- If the workload exposes any endpoints (like metrics), add authentication unless they are intended for public access. This is a crucial security practice that protects against future data exposure, even if the endpoint isn't currently handling sensitive information.
+- Use the most restrictive Security Context Constraints (SCCs), such as restricted or restricted-v2, to enforce policies. This disallows privileged containers, prevents containers from running as root or escalating privileges, and denies host breakouts by disabling features like hostPID, hostIPC, hostNetwork, and allowedHostPath.
+- If an operator requires privileged permissions and cannot use restrictive SCCs, consider implementing the following controls as appropriate to mitigate the risk:
+  - Ensure operator containers are mounted as read-only by setting “readOnlyRootFilesystem: true”. This prevents the container from writing to the root filesystem, which is a powerful defense against attackers who try to install malicious code.
+  - Ensures the container process runs as a non-root user by setting “runAsNonRoot: true”.
+  - Configure pods with “allowPrivilegeEscalation: false” to prevent a container from gaining more privileges than its parent process.
+  - Drop all Linux capabilities by setting “capabilities: drop: [ALL]”. This ensures the container operates with the fewest possible permissions, and you can add specific capabilities back if needed.
+  - Use seccomp profiles to control system calls and enforce security policies.
+  - Ensure your workloads are not running privileged. Avoid setting “privileged: true” unless it's an absolute necessity. Instead, consider workloads that can run with lower, more fine-grained permissions.
diff --git a/.cursor/rules/security/product-security/technology/python.mdc b/.cursor/rules/security/product-security/technology/python.mdc
@@ -0,0 +1,16 @@
+---
+description: Secure coding rules for Python projects 🐍
+globs:
+  - "**/*.py"
+  - "**/requirements.txt"
+  - "**/Pipfile"
+  - "**/pyproject.toml"
+alwaysApply: false
+---
+
+- Validate and sanitize all input.
+- Avoid using `eval()`, `exec()` or `pickle` on untrusted data.
+- Do not hardcode secrets in code.
+- Pin exact versions in `requirements.txt` or `pyproject.toml`. Avoid using `*` or `latest`.
+- Avoid shell execution with untrusted input. Use `subprocess.run([...], check=True)` instead of `os.system()`.
+- Handle exceptions securely; avoid exposing debug traces or stack dumps to users.
diff --git a/.cursor/rules/security/product-security/technology/react.mdc b/.cursor/rules/security/product-security/technology/react.mdc
@@ -0,0 +1,12 @@
+---
+description: Secure coding rules for React projects ⚛️
+globs:
+  - "**/*.jsx"
+  - "**/*.tsx"
+alwaysApply: false
+---
+
+- Use default React data binding to prevent XSS.
+- Sanitize HTML before using dangerouslySetInnerHTML.
+- Validate URLs before using them in the DOM.
+- Secure server-side rendering and avoid JSON injection.
diff --git a/.cursor/rules/security/product-security/technology/rust.mdc b/.cursor/rules/security/product-security/technology/rust.mdc
@@ -0,0 +1,28 @@
+---
+description: Secure coding rules for Rust projects 🦀
+globs:
+  - "**/Cargo.toml"
+  - "**/*.rs"
+alwaysApply: false
+---
+
+- Avoid using unsafe code
+- Always handle `Result` and `Option` using `match`, do not use `unwrap`
+- Propagate errors using the `?` handle
+- Always display meaningful error messages, which the user can act upon
+- Prevent buffer overflows by using safe indexing methods (e.g., `get()`, `get_mut()`) and validating input sizes
+- Prevent SQL injection by using parameterized queries and escaping user input
+- Prevent XSS by escaping user input when rendering HTML
+- Prevent command injection by avoiding the use of `std::process::Command` with user-supplied arguments
+- Protect against DoS attacks by limiting resource usage (e.g., memory, CPU, network connections)
+- Use the `checked_add`, `checked_sub`, `checked_mul`, etc. methods on integers to prevent overflows
+- Avoid data races by using appropriate synchronization primitives (`Mutex`, `RwLock`, channels)
+- Be aware of integer overflow and use checked arithmetic methods to prevent it
+- Handle Unicode characters correctly to avoid unexpected behavior
+- Handle file paths correctly, especially when dealing with different operating systems
+- Be careful when writing concurrent code to avoid data races and deadlocks
+- Split code into smaller, reusable modules
+- Try to use as much the standard library as possible, only use crates if needed
+- Prefer using crates with less dependencies, utilize crate features, in order to limit indirect dependencies
+- Prefer crates with broader community adoption, which have more downloads, more github stars, are used in major projects
+- Prefer crates with more than one maintainers, with recent commits/changes
\ No newline at end of file
diff --git a/.cursor/rules/security/shell.mdc b/.cursor/rules/security/shell.mdc
@@ -0,0 +1,64 @@
+---
+description: Secure coding rules for Shell/Bash scripts
+globs:
+  - "**/*.sh"
+  - "**/*.bash"
+  - "**/bash/**"
+alwaysApply: false
+---
+
+# Secure coding rules for Shell/Bash
+
+## Input Validation and Sanitization
+
+- Always quote variables to prevent word splitting and globbing issues ("$var" not $var).
+- Validate and sanitize all external input (user input, command-line arguments, environment variables).
+- Use parameter expansion with defaults (${var:-default}) to handle unset variables safely.
+- Check if files exist and have proper permissions before operating on them.
+
+## Command Injection Prevention
+
+- Avoid eval with untrusted input. Never use eval on user-provided data.
+- Use arrays for command arguments instead of string concatenation.
+- Prefer built-in commands over external executables when possible.
+- Use `--` to separate options from arguments (e.g., `rm -- "$file`).
+- Sanitize input before passing to shell commands or system().
+
+## File Operations
+
+- Validate file paths to prevent directory traversal attacks.
+- Use absolute paths or canonicalize paths with `realpath` before operations.
+- Set proper file permissions (umask) and ownership.
+- Use mktemp for temporary files instead of predictable paths.
+- Clean up temporary files in trap handlers (trap cleanup EXIT).
+
+## Error Handling and Logging
+
+- Use `set -e` to exit on errors, `set -u` to error on undefined variables.
+- Use `set -o pipefail` to catch errors in pipelines.
+- Implement proper error handling with trap for cleanup.
+- Log security-relevant events but never log sensitive data (passwords, keys).
+- Validate command exit codes ($?) for critical operations.
+
+## Credentials and Secrets
+
+- Never hardcode passwords, API keys, or credentials in scripts.
+- Use environment variables or secure configuration files for secrets.
+- Restrict script permissions (chmod 700 or 750) for scripts handling sensitive data.
+- Avoid echoing or logging sensitive information.
+- Use secure methods for password input (read -s for silent input).
+
+## Privilege and Permissions
+
+- Run scripts with least privilege necessary. Avoid unnecessary sudo/root.
+- Validate effective UID/GID when privilege is required.
+- Drop privileges after privileged operations are complete.
+- Use sudo with specific commands rather than running entire script as root.
+
+## Code Quality and Security
+
+- Use ShellCheck to identify common bugs and security issues.
+- Disable dangerous options like `set +e` in production scripts.
+- Use `readonly` for constants to prevent modification.
+- Avoid using `source` or `.` with untrusted scripts.
+- Use specific interpreters in shebang (#!/bin/bash not #!/bin/sh if using bash features).
diff --git a/.cursor/rules/security/typescript.mdc b/.cursor/rules/security/typescript.mdc
@@ -0,0 +1,29 @@
+---
+description: Secure coding rules for TypeScript projects
+globs:
+  - "**/*.ts"
+  - "**/*.tsx"
+  - "**/*.mts"
+  - "**/*.cts"
+  - "**/tsconfig.json"
+alwaysApply: false
+---
+
+# Secure coding rules for TypeScript
+
+- Use type guards for runtime validation. Validate external data at runtime, not just compile time.
+- Use parameterized queries or ORMs to prevent SQL injection. Never concatenate user input into queries.
+- Avoid `eval()`, `Function()` constructor, or dynamic code execution with untrusted data.
+- Sanitize HTML to prevent XSS. Use DOMPurify or framework-specific sanitizers.
+- Implement Content Security Policy (CSP) headers to mitigate XSS and injection attacks.
+- Validate and sanitize URLs before redirects to prevent open redirects.
+- Implement proper authentication and session management. Use secure, httpOnly cookies.
+- Use `crypto.randomBytes()` or Web Crypto API for secure random generation.
+- Use `npm audit` regularly to check for vulnerabilities.
+- Pin exact versions in package-lock.json. Avoid `^` or `~` for critical dependencies.
+- Implement rate limiting and input validation to prevent DoS.
+- Implement proper CORS policies. Never use wildcard (`*`) origins in production.
+- Enable strict compiler options (`strict`, `noImplicitAny`, `strictNullChecks`).
+- Avoid `as any`. Use proper type guards and validation instead.
+- Prevent prototype pollution by validating object keys and using proper type definitions.
+- Use `readonly` and `const` to prevent unintended mutations.
PATCH

echo "Gold patch applied."
