import re, sys
text = open("/workspace/bun/src/bun.js/test/expect.zig").read()
idx = text.find("pub fn extend")
if idx == -1:
    sys.exit(1)
brace = text.index("{", idx)
depth, i = 1, brace + 1
while i < len(text) and depth > 0:
    if text[i] == "{": depth += 1
    elif text[i] == "}": depth -= 1
    i += 1
body = text[brace+1:i-1]
body = re.sub(r"//[^\n]*", "", body)
body = re.sub(r'"(?:[^"\]|\.)*"', '""', body)
targets = ["expect_proto", "expect_constructor", "expect_static_proto"]
if re.search(r"\.initFast\s*\([^)]*\b(?:true|false)\b[^)]*\)", body):
    sys.exit(0)
if re.search(r"(?:isIndex|parseIndex)\s*\([^)]*\)\s*[^;]*(?:continue|break|return)", body):
    sys.exit(0)
for t in targets:
    if re.search(re.escape(t) + r"\.put\s*\(", body):
        print(f"FAIL: bare .put() on {t}", file=sys.stderr)
        sys.exit(1)
print("PASS")
