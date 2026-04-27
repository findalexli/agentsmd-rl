#!/usr/bin/env bash
# Oracle solution for bun PR #28838: reject conflicting duplicate
# Content-Length headers in packages/bun-uws/src/HttpParser.h.

set -euo pipefail

cd /workspace/bun

# Idempotency guard: if the patched header already contains the bloom-filter
# guard for "content-length", we've been applied already.
if grep -q 'bf.mightHave("content-length")' packages/bun-uws/src/HttpParser.h; then
    echo "patch already applied, nothing to do"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/bun-uws/src/HttpParser.h b/packages/bun-uws/src/HttpParser.h
--- a/packages/bun-uws/src/HttpParser.h
+++ b/packages/bun-uws/src/HttpParser.h
@@ -870,7 +870,27 @@ namespace uWS
             * the Transfer-Encoding overrides the Content-Length. Such a message might indicate an attempt
             * to perform request smuggling (Section 11.2) or response splitting (Section 11.1) and
             * ought to be handled as an error. */
-            const std::string_view contentLengthString = req->getHeader("content-length");
+            /* RFC 9110 8.6 + RFC 9112 6.3: locate the Content-Length header and, in the
+             * same pass, verify every Content-Length header carries the same non-empty
+             * value. A single empty value or multiple differing values are ambiguous and
+             * must be rejected to prevent request smuggling. The bloom filter short-circuits
+             * the common "no Content-Length" case. */
+            std::string_view contentLengthString;
+            if (req->bf.mightHave("content-length")) {
+                for (HttpRequest::Header *h = req->headers; (++h)->key.length(); ) {
+                    if (h->key.length() == 14 && !strncmp(h->key.data(), "content-length", 14)) {
+                        if (contentLengthString.data() == nullptr) {
+                            if (h->value.length() == 0) {
+                                return HttpParserResult::error(HTTP_ERROR_400_BAD_REQUEST, HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH);
+                            }
+                            contentLengthString = h->value;
+                        } else if (h->value.length() != contentLengthString.length() ||
+                                   strncmp(h->value.data(), contentLengthString.data(), contentLengthString.length())) {
+                            return HttpParserResult::error(HTTP_ERROR_400_BAD_REQUEST, HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH);
+                        }
+                    }
+                }
+            }
             const auto contentLengthStringLen = contentLengthString.length();

             /* Check Transfer-Encoding header validity and conflicts */
PATCH

echo "patch applied successfully"
grep -q 'bf.mightHave("content-length")' packages/bun-uws/src/HttpParser.h
