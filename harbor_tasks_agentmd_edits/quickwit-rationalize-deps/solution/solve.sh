#!/usr/bin/env bash
set -euo pipefail

cd /workspace/quickwit

# Idempotent: skip if already applied
if grep -q 'default-features = false' quickwit/Cargo.toml 2>/dev/null && [ -f .claude/skills/rationalize-deps/SKILL.md ]; then
    # Check a specific marker — dialoguer with default-features = false
    if grep -q 'dialoguer.*default-features = false' quickwit/Cargo.toml 2>/dev/null; then
        echo "Patch already applied."
        exit 0
    fi
fi

# --- Cargo.toml changes: disable unused default features from 6 deps ---

git apply - <<'PATCH'
diff --git a/quickwit/Cargo.toml b/quickwit/Cargo.toml
index 5a2b9ba606c..2ed23582f9b 100644
--- a/quickwit/Cargo.toml
+++ b/quickwit/Cargo.toml
@@ -102,11 +102,11 @@ colored = "3.0"
 console-subscriber = "0.5"
 criterion = { version = "0.8", features = ["async_tokio"] }
 cron = "0.15"
-dialoguer = "0.12"
+dialoguer = { version = "0.12", default-features = false }
 dotenvy = "0.15"
 dyn-clone = "1.0"
 enum-iterator = "2.3"
-env_logger = "0.11"
+env_logger = { version = "0.11", default-features = false, features = ["auto-color"] }
 fail = "0.5"
 flate2 = "1.1"
 flume = "0.12"
@@ -131,7 +131,13 @@ http-serde = "2.1"
 humantime = "2.3"
 hyper = { version = "1.8", features = ["client", "http1", "http2", "server"] }
 hyper-rustls = "0.27"
-hyper-util = { version = "0.1", features = ["full"] }
+hyper-util = { version = "0.1", default-features = false, features = [
+  "client-legacy",
+  "server-auto",
+  "server-graceful",
+  "service",
+  "tokio",
+] }
 indexmap = { version = "2.12", features = ["serde"] }
 indicatif = "0.18"
 itertools = "0.14"
@@ -176,7 +182,7 @@ pprof = { version = "0.15", features = ["flamegraph"] }
 predicates = "3"
 prettyplease = "0.2"
 proc-macro2 = "1.0"
-prometheus = { version = "0.14", features = ["process"] }
+prometheus = { version = "0.14", default-features = false, features = ["process"] }
 proptest = "1"
 prost = { version = "0.14", default-features = false, features = [
   "derive",
@@ -247,7 +253,10 @@ tokio = { version = "1.48", features = ["full"] }
 tokio-metrics = { version = "0.4", features = ["rt"] }
 tokio-rustls = { version = "0.26", default-features = false }
 tokio-stream = { version = "0.1", features = ["sync"] }
-tokio-util = { version = "0.7", features = ["full"] }
+tokio-util = { version = "0.7", default-features = false, features = [
+  "compat",
+  "io-util",
+] }
 toml = "0.9"
 tonic = { version = "0.14", features = [
   "_tls-any",
@@ -299,7 +308,7 @@ vrl = { version = "0.29", default-features = false, features = [
 warp = { version = "0.4", features = ["server", "test"] }
 whichlang = "0.1"
 wiremock = "0.6"
-zstd = "0.13"
+zstd = { version = "0.13", default-features = false }

 aws-config = "1.8"
 aws-credential-types = { version = "1.2", features = ["hardcoded-credentials"] }

PATCH

# --- Create the rationalize-deps skill ---

mkdir -p .claude/skills/rationalize-deps

cat > .claude/skills/rationalize-deps/SKILL.md <<'SKILLEOF'
---
name: rationalize-deps
description: Analyze Cargo.toml dependencies and attempt to remove unused features to reduce compile times and binary size
---

# Rationalize Dependencies

This skill analyzes Cargo.toml dependencies to identify and remove unused features.

## Overview

Many crates enable features by default that may not be needed. This skill:
1. Identifies dependencies with default features enabled
2. Tests if `default-features = false` works
3. Identifies which specific features are actually needed
4. Verifies compilation after changes

## Step 1: Identify the target

Ask the user which crate(s) to analyze:
- A specific crate name (e.g., "tokio", "serde")
- A specific workspace member (e.g., "quickwit-search")
- "all" to scan the entire workspace

## Step 2: Analyze current dependencies

For the workspace Cargo.toml (`quickwit/Cargo.toml`), list dependencies that:
- Do NOT have `default-features = false`
- Have default features that might be unnecessary

Run: `cargo tree -p <crate> -f "{p} {f}" --edges features` to see what features are actually used.

## Step 3: For each candidate dependency

### 3a: Check the crate's default features

Look up the crate on crates.io or check its Cargo.toml to understand:
- What features are enabled by default
- What each feature provides

Use: `cargo metadata --format-version=1 | jq '.packages[] | select(.name == "<crate>") | .features'`

### 3b: Try disabling default features

Modify the dependency in `quickwit/Cargo.toml`:

From:
```toml
some-crate = { version = "1.0" }
```

To:
```toml
some-crate = { version = "1.0", default-features = false }
```

### 3c: Run cargo check

Run: `cargo check --workspace` (or target specific packages for faster feedback)

If compilation fails:
1. Read the error messages to identify which features are needed
2. Add only the required features explicitly:
   ```toml
   some-crate = { version = "1.0", default-features = false, features = ["needed-feature"] }
   ```
3. Re-run cargo check

### 3d: Binary search for minimal features

If there are many default features, use binary search:
1. Start with no features
2. If it fails, add half the default features
3. Continue until you find the minimal set

## Step 4: Document findings

For each dependency analyzed, report:
- Original configuration
- New configuration (if changed)
- Features that were removed
- Any features that are required

## Step 5: Verify full build

After all changes, run:
```bash
cargo check --workspace --all-targets
cargo test --workspace --no-run
```

## Common Patterns

### Serde
Often only needs `derive`:
```toml
serde = { version = "1.0", default-features = false, features = ["derive", "std"] }
```

### Tokio
Identify which runtime features are actually used:
```toml
tokio = { version = "1.0", default-features = false, features = ["rt-multi-thread", "macros", "sync"] }
```

### Reqwest
Often doesn't need all TLS backends:
```toml
reqwest = { version = "0.11", default-features = false, features = ["rustls-tls", "json"] }
```

## Rollback

If changes cause issues:
```bash
git checkout quickwit/Cargo.toml
cargo check --workspace
```

## Tips

- Start with large crates that have many default features (tokio, reqwest, hyper)
- Use `cargo bloat --crates` to identify large dependencies
- Check `cargo tree -d` for duplicate dependencies that might indicate feature conflicts
- Some features are needed only for tests - consider using `[dev-dependencies]` features
SKILLEOF

echo "Patch applied successfully."
