#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lavinmq

# Idempotency guard
if grep -qF "- **Performance** - Look for inefficient algorithms, unnecessary allocations, bl" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -69,3 +69,27 @@ LavinMQ is a high-performance message queue server implementing AMQP 0-9-1 and M
 ## Performance Considerations
 
 LavinMQ uses a disk-first approach where the OS handles caching. Message segments are memory-mapped files, and the server is designed for high throughput with minimal memory usage.
+
+## Code Review Guidelines
+
+When conducting code reviews, Claude should:
+
+### Review Style
+- Provide concise, to-the-point and actionable feedback
+- Focus on critical issues: bugs, security vulnerabilities, performance problems
+- Highlight Crystal-specific best practices and idioms
+- Check for proper error handling and resource cleanup
+- Verify thread safety in concurrent code
+
+### Key Areas to Review
+- **Memory Safety** - Check for potential memory leaks, especially with C bindings
+- **AMQP Compliance** - Ensure protocol implementations follow AMQP 0-9-1 specification
+- **Performance** - Look for inefficient algorithms, unnecessary allocations, blocking operations
+- **Testing** - Verify adequate test coverage for new functionality
+
+### Review Format
+- Use bullet points for multiple issues
+- Reference specific lines when possible, and always mention the file name
+- Suggest concrete improvements rather than just identifying problems
+- Keep feedback under 200 words per file unless critical issues require detailed explanation
+- Give a short summary of key points at the end of the review
PATCH

echo "Gold patch applied."
