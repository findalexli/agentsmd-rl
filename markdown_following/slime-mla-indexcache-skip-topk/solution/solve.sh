#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

PATCH="docker/patch/latest/sglang.patch"

# Idempotency: if unconditional skip_topk init already present, skip
if grep -q '^+        self\.skip_topk = False' "$PATCH" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

python3 << 'PYEOF'
import re
from pathlib import Path

patch = Path("docker/patch/latest/sglang.patch")
content = patch.read_text()

# 1. Insert unconditional self.skip_topk / self.next_skip_topk before "if self.use_nsa:"
#    In the base patch, the line "         if self.use_nsa:" appears in the deepseek_v2.py section
#    as a context line (space-prefixed). We insert two new added lines before it.
old_use_nsa = """\
             )
+            if is_nextn:
+                self.skip_topk = False
+                self.next_skip_topk = False
+            else:"""

new_use_nsa = """\
             )
+            if not is_nextn:"""

content = content.replace(old_use_nsa, new_use_nsa)

# 2. Before "         if self.use_nsa:", insert the unconditional init lines.
#    Find the context line that precedes "if self.use_nsa:" in the __init__ hunk.
#    The pattern in the base patch is:
#      +             )
#
#               if self.use_nsa:
#    We need to find "         if self.use_nsa:" preceded by a blank context line,
#    and insert the init before it.

# Find the hunk that contains the __init__ changes
# The base has: @@ -1174,6 +1175,34 @@
# We need to insert lines before the "if self.use_nsa:" line and adjust the hunk header

# Strategy: find the section between kv_a_proj_with_mqa and if self.use_nsa:
# In the base patch, the relevant area is:
#   ...
#   @@ -1174,6 +1175,34 @@ class DeepseekV2AttentionMLA(...):
#
# We need to add a new hunk before @@ -1174 that inserts the unconditional init.
# But actually, we can modify the existing hunks.

# Let's insert the two lines right before " \n         if self.use_nsa:"
# In the patch, that area looks like:
#              )
#  <blank>
#          if self.use_nsa:

# Find " \n         if self.use_nsa:" in the deepseek_v2 section
# Actually, let's look for a more specific pattern in the patch:
# The hunk header @@ -1174,6 +1175,34 @@ needs updating anyway.
# Let's replace it with a new hunk that includes the unconditional init.

# Approach: add a new hunk for the unconditional init insertion.
# First, replace the old hunk header to account for the removed lines (4->1, saves 3 lines)
old_hunk = "@@ -1174,6 +1175,34 @@"
# With our changes: we removed 3 added lines from the is_nextn block,
# so the new count is 34 - 3 = 31. But we also need to add a new hunk for the init.

# Simpler: do a two-step text replacement.
# Step A: already done above (is_nextn block -> if not is_nextn)
# Step B: insert the unconditional init before "         if self.use_nsa:"

# The deepseek_v2.py section has multiple occurrences of self.use_nsa.
# We need the one in the __init__ method. In the patch, this appears after
# the "self.layer_id = layer_id" line and before the indexer setup.

# The pattern in the base (after step A replacement above):
#     @@ -1174,6 +1175,34 @@ class DeepseekV2AttentionMLA
#                  layer_id=layer_id,
#                  alt_stream=alt_stream,
#              )
#     +            if not is_nextn:
# But we need to add lines BEFORE the if self.use_nsa: block.
# The if self.use_nsa: is a CONTEXT line (not added), somewhere earlier.

# Let me find the exact structure. In the base patch, the hunk @@ -1174,6 +1175,34 @@
# only shows context lines around line 1174. The "if self.use_nsa:" line
# must be earlier. Let me look for a hunk that contains both the
# kv_a_proj_with_mqa line and the if self.use_nsa: line.

# Actually, looking at the PR diff, the fix adds a NEW hunk at line 1154-1155
# that inserts the init BEFORE if self.use_nsa:. So we need to add this hunk.

# The PR diff adds:
# +@@ -1154,6 +1155,8 @@ class DeepseekV2AttentionMLA(nn.Module, DeepseekMHAForwardMixin):
# +                 prefix=add_prefix("kv_a_proj_with_mqa", prefix),
# +             )
# +
# ++        self.skip_topk = False
# ++        self.next_skip_topk = False
# +         if self.use_nsa:

# In the base patch, the hunk at @@ -1174 is the first hunk after __init__ params.
# We need to ADD a new hunk before it.

# Let's find the right insertion point: right before @@ -1174 (now with reduced count)
# The fix changes @@ -1174,6 +1175,34 @@ to @@ -1174,6 +1177,31 @@ (different offsets)
# But also adds a new hunk @@ -1154,6 +1155,8 @@

# Since this is getting complex, let me just replace the relevant section wholesale.
# Find the section from "@@ -1174" to the next @@ or section boundary.

# First, let's update the hunk header count: was +1175,34, removing 3 lines = +1177,31
# Actually the exact numbers depend on the new structure. Let me compute:
# Old added lines: 34 (from +1175,34)
# We removed 3 lines (if is_nextn, self.skip_topk, self.next_skip_topk removed; else -> if not)
# Actually we removed 4 lines and added 1 line: net -3 added lines
# New: 34 - 3 = 31. New start offset: +1177 (because the new preceding hunk adds 2 lines)

# Let me just splice in the new hunk and update the old one.

# Replace the old hunk header
content = content.replace(
    "@@ -1174,6 +1175,34 @@ class DeepseekV2AttentionMLA(nn.Module, DeepseekMHAForwardMixin):",
    """@@ -1154,6 +1155,8 @@ class DeepseekV2AttentionMLA(nn.Module, DeepseekMHAForwardMixin):
                 prefix=add_prefix("kv_a_proj_with_mqa", prefix),
             )

+        self.skip_topk = False
+        self.next_skip_topk = False
         if self.use_nsa:
             is_neox_style = not getattr(config, "indexer_rope_interleave", False)
             self.indexer = Indexer(
@@ -1174,6 +1177,31 @@ class DeepseekV2AttentionMLA(nn.Module, DeepseekMHAForwardMixin):"""
)

# Update remaining hunk line offsets that reference +1391, +1399, +1410, etc.
# These need adjusting by -3 (we removed 3 net lines from the added side)
# +1391 -> +1390, +1399 -> +1398, +1410 -> +1409
for old, new in [
    ("+1391,", "+1390,"),
    ("+1399,", "+1398,"),
    ("+1410,", "+1409,"),
    ("+1450,", "+1449,"),
    ("+1566,", "+1565,"),
    ("+1658,", "+1657,"),
    ("+1666,", "+1665,"),
    ("+1973,", "+1972,"),
    ("+2321,", "+2320,"),
    ("+2404,", "+2403,"),
    ("+2446,", "+2445,"),
    ("+2487,", "+2486,"),
    ("+2763,", "+2762,"),
    ("+2781,", "+2780,"),
    ("+2789,", "+2788,"),
]:
    # Only replace within @@ hunk headers in the deepseek_v2.py section
    content = content.replace(f"@@ {old}", f"@@ {new}")

# Update the index hash
content = content.replace(
    "index 1583dd788..432758732 100644",
    "index 1583dd788..08d59c883 100644"
)

patch.write_text(content)
print("Fix applied successfully.")
PYEOF
