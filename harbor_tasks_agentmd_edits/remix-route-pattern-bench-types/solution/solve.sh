#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'Type benchmarks' packages/route-pattern/bench/README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# 1. Move runtime benchmarks to src/ subdirectory
mkdir -p packages/route-pattern/bench/src
git mv packages/route-pattern/bench/comparison.bench.ts packages/route-pattern/bench/src/comparison.bench.ts
git mv packages/route-pattern/bench/href.bench.ts packages/route-pattern/bench/src/href.bench.ts
git mv packages/route-pattern/bench/pathological.bench.ts packages/route-pattern/bench/src/pathological.bench.ts
git mv packages/route-pattern/bench/simple.bench.ts packages/route-pattern/bench/src/simple.bench.ts

# 2. Create type benchmark files
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

# 3. Update bench/package.json — add bench:types script and @ark/attest dependency
cat > packages/route-pattern/bench/package.json << 'BPKG'
{
  "name": "route-pattern-bench",
  "private": true,
  "type": "module",
  "scripts": {
    "bench": "vitest bench --run",
    "bench:types": "node bench.types.ts"
  },
  "dependencies": {
    "@remix-run/route-pattern": "workspace:^",
    "find-my-way": "^9.1.0",
    "path-to-regexp": "^8.2.0"
  },
  "devDependencies": {
    "@ark/attest": "^0.56.0",
    "vitest": "4.0.15"
  }
}
BPKG

# 4. Remove @ark/attest from route-pattern package.json
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('packages/route-pattern/package.json', 'utf8'));
delete pkg.devDependencies['@ark/attest'];
fs.writeFileSync('packages/route-pattern/package.json', JSON.stringify(pkg, null, 2) + '\n');
"

# 5. Update bench/README.md
cat > packages/route-pattern/bench/README.md << 'README'
# Benchmarks

## Runtime benchmarks

Runtime benchmarks are in [src/](./src/) and use [Vitest benchmarking](https://vitest.dev/guide/features.html#benchmarking).

```sh
# All benchmarks
pnpm bench

# Specific benchmark
pnpm bench comparison.bench.json # full name
pnpm bench comparison            # pattern match
```

### Compare performance across branches

```bash
git checkout main
pnpm bench comparison.bench.ts --outputJson=main.json

git checkout feature-branch
pnpm bench comparison.bench.ts --compare=main.json
```

## Type benchmarks

Type benchmarks are in [types/](./types/) and use [ArkType Attest](https://github.com/arktypeio/arktype/blob/main/ark/attest/README.md).

```sh
# Run type benchmarks directly with Node
node types/href.ts
```
README

echo "Patch applied successfully."
