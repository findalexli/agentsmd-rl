#!/usr/bin/env bash
set -euo pipefail

cd /workspace/waf-detector

# Idempotency guard
if grep -qF "1. **Dependency scan**: Run `cargo audit` (install with `cargo install cargo-aud" ".claude/skills/security-audit.md" && grep -qF "- [ ] **Detect tab**: Single URL scan \u2014 enter `https://cloudflare.com`, click Sc" ".claude/skills/test-dashboard.md" && grep -qF "Report pass/fail for each step with counts (e.g., \"298 tests passed\"). Do not tr" ".claude/skills/validate-build.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/security-audit.md b/.claude/skills/security-audit.md
@@ -0,0 +1,31 @@
+---
+name: security-audit
+description: Run a structured security audit on the WAF detector codebase
+user_invocable: true
+---
+
+# Security Audit Skill
+
+Run a systematic security audit of the WAF detector codebase.
+
+## Steps
+
+1. **Dependency scan**: Run `cargo audit` (install with `cargo install cargo-audit` if missing)
+2. **Code patterns**: Search for common security issues:
+   - Unwrapped user input reaching shell commands or file paths
+   - Missing input validation on API endpoints
+   - Hardcoded credentials or secrets
+   - Unsafe blocks without justification
+   - Missing CSRF/CORS protections
+3. **Configuration review**: Check for insecure defaults in:
+   - `src/web/mod.rs` (CORS, binding address, TLS)
+   - `src/http/mod.rs` (redirect policy, certificate validation)
+   - Consent enforcement in VA1/VA2 endpoints
+4. **Test coverage gaps**: Identify security-critical paths without test coverage
+5. **Report**: Output findings with severity (CRITICAL/HIGH/MEDIUM/LOW) and remediation steps
+
+## Rules
+
+- Run actual scans, report real results. Never predict or fabricate findings.
+- Check `cargo clippy` for any new warnings introduced.
+- Focus on OWASP Top 10 categories relevant to this Rust web application.
diff --git a/.claude/skills/test-dashboard.md b/.claude/skills/test-dashboard.md
@@ -0,0 +1,35 @@
+---
+name: test-dashboard
+description: Browser-test the WAF detector dashboard with Playwright
+user_invocable: true
+---
+
+# Dashboard Test Skill
+
+Launch the web server and validate the dashboard UI using Playwright browser automation.
+
+## Prerequisites
+
+- Build first: `cargo build --release`
+- Kill any existing server: `pkill -f 'waf-detect.*--web'`
+
+## Steps
+
+1. Start server: `./target/release/waf-detect --web --port 8080 &`
+2. Wait for healthy: `curl -s http://localhost:8080/api/status`
+3. Navigate to `http://localhost:8080`
+
+### Test checklist
+
+- [ ] **Detect tab**: Single URL scan — enter `https://cloudflare.com`, click Scan, verify CloudFlare detected
+- [ ] **Evidence**: Click "View Evidence" — verify items expand/collapse, no `Some(...)` or `None` in data
+- [ ] **Batch scan**: Enter 2 URLs, click Scan Batch, verify both results appear
+- [ ] **Test tab**: WAF Smoke Test, Virtual Adversary, Advanced Security Profiling sections visible
+- [ ] **Reports tab**: Quick Actions, Consent Status, VA History sections visible
+- [ ] **Export JSON**: Click Export JSON with results present — verify download triggers
+- [ ] **Console errors**: Check `browser_console_messages` — must be 0 errors
+- [ ] **Responsive**: Resize to 390px (mobile), 768px (tablet), 1440px (desktop) — verify layout adapts
+
+## Cleanup
+
+Kill the server after testing: `pkill -f 'waf-detect.*--web'`
diff --git a/.claude/skills/validate-build.md b/.claude/skills/validate-build.md
@@ -0,0 +1,27 @@
+---
+name: validate-build
+description: Full build validation — compile, test, lint, and verify
+user_invocable: true
+---
+
+# Build Validation Skill
+
+Run the complete build validation pipeline for the WAF detector.
+
+## Steps (run sequentially)
+
+1. `cargo fmt --check` — verify formatting
+2. `cargo clippy --all-targets --all-features -- -D warnings` — lint with strict warnings
+3. `cargo test -q` — run all tests
+4. `cargo build --release` — build optimized binary
+
+## On failure
+
+- If fmt fails: run `cargo fmt` and report what changed
+- If clippy fails: report the warnings with file locations
+- If tests fail: report failing test names and error messages
+- If build fails: report the compilation error
+
+## Output
+
+Report pass/fail for each step with counts (e.g., "298 tests passed"). Do not truncate test output if there are failures.
PATCH

echo "Gold patch applied."
