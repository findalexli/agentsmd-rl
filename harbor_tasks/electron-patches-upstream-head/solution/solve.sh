#!/bin/bash
set -e

cd /workspace/electron

# Check if already patched
if grep -q "hashlib.md5(SCRIPT_DIR.encode()).hexdigest()" script/lib/git.py; then
    echo "Already patched, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/docs/development/patches.md b/docs/development/patches.md
index e32549e1fe7a7..8f03da90b25ef 100644
--- a/docs/development/patches.md
+++ b/docs/development/patches.md
@@ -79,7 +79,7 @@ $ ../../electron/script/git-import-patches ../../electron/patches/node
 $ ../../electron/script/git-export-patches -o ../../electron/patches/node
 ```

-Note that `git-import-patches` will mark the commit that was `HEAD` when it was run as `refs/patches/upstream-head`. This lets you keep track of which commits are from Electron patches (those that come after `refs/patches/upstream-head`) and which commits are in upstream (those before `refs/patches/upstream-head`).
+Note that `git-import-patches` will mark the commit that was `HEAD` when it was run as `refs/patches/upstream-head` (and a checkout-specific `refs/patches/upstream-head-<hash>` so that gclient worktrees sharing a `.git/refs` directory don't clobber each other). This lets you keep track of which commits are from Electron patches (those that come after `refs/patches/upstream-head`) and which commits are in upstream (those before `refs/patches/upstream-head`).

 #### Resolving conflicts

diff --git a/script/lib/git.py b/script/lib/git.py
index b23eddab39cc8..93f397f0bc490 100644
--- a/script/lib/git.py
+++ b/script/lib/git.py
@@ -6,6 +6,7 @@
 structure, or make assumptions about the passed arguments or calls' outcomes.
 """

+import hashlib
 import io
 import os
 import posixpath
@@ -18,7 +19,14 @@

 from patches import PATCH_FILENAME_PREFIX, is_patch_location_line

-UPSTREAM_HEAD='refs/patches/upstream-head'
+# In gclient-new-workdir worktrees, .git/refs is symlinked back to the source
+# checkout, so a single fixed ref name would be shared (and clobbered) across
+# worktrees. Derive a per-checkout suffix from this script's absolute path so
+# each worktree records its own upstream head in the shared refs directory.
+_LEGACY_UPSTREAM_HEAD = 'refs/patches/upstream-head'
+UPSTREAM_HEAD = (
+  _LEGACY_UPSTREAM_HEAD + '-' + hashlib.md5(SCRIPT_DIR.encode()).hexdigest()[:8]
+)

 def is_repo_root(path):
   path_exists = os.path.exists(path)
@@ -83,6 +91,8 @@ def import_patches(repo, ref=UPSTREAM_HEAD, **kwargs):
   """same as am(), but we save the upstream HEAD so we can refer to it when we
   later export patches"""
   update_ref(repo=repo, ref=ref, newvalue='HEAD')
+  if ref != _LEGACY_UPSTREAM_HEAD:
+    update_ref(repo=repo, ref=_LEGACY_UPSTREAM_HEAD, newvalue='HEAD')
   am(repo=repo, **kwargs)


@@ -102,19 +112,21 @@ def get_commit_count(repo, commit_range):

 def guess_base_commit(repo, ref):
   """Guess which commit the patches might be based on"""
-  try:
-    upstream_head = get_commit_for_ref(repo, ref)
-    num_commits = get_commit_count(repo, upstream_head + '..')
-    return [upstream_head, num_commits]
-  except subprocess.CalledProcessError:
-    args = [
-      'git',
-      '-C',
-      repo,
-      'describe',
-      '--tags',
-    ]
-    return subprocess.check_output(args).decode('utf-8').rsplit('-', 2)[0:2]
+  for candidate in (ref, _LEGACY_UPSTREAM_HEAD):
+    try:
+      upstream_head = get_commit_for_ref(repo, candidate)
+      num_commits = get_commit_count(repo, upstream_head + '..')
+      return [upstream_head, num_commits]
+    except subprocess.CalledProcessError:
+      continue
+  args = [
+    'git',
+    '-C',
+    repo,
+    'describe',
+    '--tags',
+  ]
+  return subprocess.check_output(args).decode('utf-8').rsplit('-', 2)[0:2]


 def format_patch(repo, since):
PATCH

echo "Patch applied successfully"
