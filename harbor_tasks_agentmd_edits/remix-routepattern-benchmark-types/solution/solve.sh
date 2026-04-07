#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'Type benchmarks' packages/route-pattern/bench/README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# 1. Move existing benchmark files into src/
mkdir -p packages/route-pattern/bench/src
git mv packages/route-pattern/bench/comparison.bench.ts packages/route-pattern/bench/src/comparison.bench.ts
git mv packages/route-pattern/bench/href.bench.ts packages/route-pattern/bench/src/href.bench.ts
git mv packages/route-pattern/bench/pathological.bench.ts packages/route-pattern/bench/src/pathological.bench.ts
git mv packages/route-pattern/bench/simple.bench.ts packages/route-pattern/bench/src/simple.bench.ts

# 2. Create type benchmark directory and files
mkdir -p packages/route-pattern/bench/types

cat > packages/route-pattern/bench/types/href.ts << 'EOF'
import { bench } from '@ark/attest'
import { RoutePattern, type HrefArgs } from '@remix-run/route-pattern'

bench('href', () => {
  let pattern = new RoutePattern('/posts/:id')
  pattern.href({ id: '123' })
}).types([1344, 'instantiations'])

bench('HrefArgs', () => {
  type _ = HrefArgs<'/posts/:id'>
}).types([1059, 'instantiations'])
EOF

cat > packages/route-pattern/bench/types/join.ts << 'EOF'
import { bench } from '@ark/attest'
import { RoutePattern, type Join } from '@remix-run/route-pattern'

bench('join', () => {
  let pattern = new RoutePattern('/posts/:id')
  pattern.join('/comments/:commentId')
}).types([2704, 'instantiations'])

bench('Join', () => {
  type _ = Join<'/posts/:id', '/comments/:commentId'>
}).types([2628, 'instantiations'])
EOF

cat > packages/route-pattern/bench/types/new.ts << 'EOF'
import { bench } from '@ark/attest'
import { RoutePattern } from '@remix-run/route-pattern'

bench('new RoutePattern', () => {
  new RoutePattern('/posts/:id')
}).types([3, 'instantiations'])
EOF

cat > packages/route-pattern/bench/types/params.ts << 'EOF'
import { bench } from '@ark/attest'
import { RoutePattern, type Params } from '@remix-run/route-pattern'

bench('params', () => {
  let pattern = new RoutePattern('/posts/:id')
  let match = pattern.match('https://example.com/posts/123')
  match?.params
}).types([1197, 'instantiations'])

bench('Params', () => {
  type _ = Params<'/posts/:id'>
}).types([1184, 'instantiations'])
EOF

# 3. Update bench/README.md
git apply --whitespace=fix - <<'PATCH'
--- a/packages/route-pattern/bench/README.md
+++ b/packages/route-pattern/bench/README.md
@@ -1,8 +1,10 @@
 # Benchmarks

-## Run benchmarks
+## Runtime benchmarks

-```bash
+Runtime benchmarks are in [src/](./src/) and use [Vitest benchmarking](https://vitest.dev/guide/features.html#benchmarking).
+
+```sh
 # All benchmarks
 pnpm bench

@@ -11,7 +13,7 @@ pnpm bench comparison.bench.json # full name
 pnpm bench comparison            # pattern match
 ```

-## Compare performance across branches
+### Compare performance across branches

 ```bash
 git checkout main
@@ -20,3 +22,12 @@ pnpm bench comparison.bench.ts --outputJson=main.json
 git checkout feature-branch
 pnpm bench comparison.bench.ts --compare=main.json
 ```
+
+## Type benchmarks
+
+Type benchmarks are in [types/](./types/) and use [ArkType Attest](https://github.com/arktypeio/arktype/blob/main/ark/attest/README.md).
+
+```sh
+# Run type benchmarks directly with Node
+node types/href.ts
+```
PATCH

# 4. Update bench/package.json — add bench:types script and @ark/attest devDep
git apply --whitespace=fix - <<'PATCH'
--- a/packages/route-pattern/bench/package.json
+++ b/packages/route-pattern/bench/package.json
@@ -3,7 +3,8 @@
   "private": true,
   "type": "module",
   "scripts": {
-    "bench": "vitest bench --run"
+    "bench": "vitest bench --run",
+    "bench:types": "node bench.types.ts"
   },
   "dependencies": {
     "@remix-run/route-pattern": "workspace:^",
@@ -11,6 +12,7 @@
     "path-to-regexp": "^8.2.0"
   },
   "devDependencies": {
+    "@ark/attest": "^0.56.0",
     "vitest": "4.0.15"
   }
 }
PATCH

# 5. Move @ark/attest from route-pattern to bench subpackage
git apply --whitespace=fix - <<'PATCH'
--- a/packages/route-pattern/package.json
+++ b/packages/route-pattern/package.json
@@ -41,7 +41,6 @@
     }
   },
   "devDependencies": {
-    "@ark/attest": "^0.49.0",
     "@types/node": "catalog:",
     "@typescript/native-preview": "catalog:",
     "dedent": "^1.7.1"
PATCH

echo "Patch applied successfully."
