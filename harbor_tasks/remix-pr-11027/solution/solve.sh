#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

python3 <<'PYEOF'
import sys

def fix_simple():
    f = "packages/route-pattern/bench/simple.bench.ts"
    with open(f) as fh:
        c = fh.read()

    # 1. Import TrieMatcher
    c = c.replace(
        "import { ArrayMatcher } from '@remix-run/route-pattern'",
        "import { ArrayMatcher, TrieMatcher } from '@remix-run/route-pattern'"
    )

    # 2. Remove matchers variable
    c = c.replace(
        "let matchers = [{ name: 'array', matcher: new ArrayMatcher<null>() }]\n\n", ""
    )

    # 3. Replace setup describe block
    old_setup = (
        "describe('setup', () => {\n"
        "  for (let { name, matcher } of matchers) {\n"
        "    bench(name, () => {\n"
        "      for (let route of routes) {\n"
        "        matcher.add(route, null)\n"
        "      }\n"
        "    })\n"
        "  }\n"
        "})"
    )
    new_setup = (
        "describe('setup', () => {\n"
        "  bench('array', () => {\n"
        "    let matcher = new ArrayMatcher<null>()\n"
        "    for (let route of routes) {\n"
        "      matcher.add(route, null)\n"
        "    }\n"
        "  })\n"
        "\n"
        "  bench('trie', () => {\n"
        "    let matcher = new TrieMatcher<null>()\n"
        "    for (let route of routes) {\n"
        "      matcher.add(route, null)\n"
        "    }\n"
        "  })\n"
        "})"
    )
    assert old_setup in c, f"old setup block not found in {f}"
    c = c.replace(old_setup, new_setup)

    # 4. Replace match describe block
    old_match = (
        "describe('match', () => {\n"
        "  for (let { name, matcher } of matchers) {\n"
        "    bench(name, () => {\n"
        "      urls.forEach((url) => matcher.match(url))\n"
        "    })\n"
        "  }\n"
        "})"
    )
    new_match = (
        "describe('match', () => {\n"
        "  let arrayMatcher = new ArrayMatcher<null>()\n"
        "  for (let route of routes) {\n"
        "    arrayMatcher.add(route, null)\n"
        "  }\n"
        "  bench('array', () => {\n"
        "    urls.forEach((url) => arrayMatcher.match(url))\n"
        "  })\n"
        "\n"
        "  let trieMatcher = new TrieMatcher<null>()\n"
        "  for (let route of routes) {\n"
        "    trieMatcher.add(route, null)\n"
        "  }\n"
        "  bench('trie', () => {\n"
        "    urls.forEach((url) => trieMatcher.match(url))\n"
        "  })\n"
        "})"
    )
    assert old_match in c, f"old match block not found in {f}"
    c = c.replace(old_match, new_match)

    with open(f, "w") as fh:
        fh.write(c)
    print(f"Fixed {f}")


def fix_pathological():
    f = "packages/route-pattern/bench/pathological.bench.ts"
    with open(f) as fh:
        c = fh.read()

    # 1. Import TrieMatcher
    c = c.replace(
        "import { ArrayMatcher } from '@remix-run/route-pattern'",
        "import { ArrayMatcher, TrieMatcher } from '@remix-run/route-pattern'"
    )

    # 2. Remove matchers variable
    c = c.replace(
        "let matchers = [{ name: 'array', matcher: new ArrayMatcher<null>() }]\n\n", ""
    )

    # 3. Replace setup describe block
    old_setup = (
        "describe('setup', () => {\n"
        "  for (let { name, matcher } of matchers) {\n"
        "    bench(name, () => {\n"
        "      routes.forEach((route) => matcher.add(route, null))\n"
        "    })\n"
        "  }\n"
        "})"
    )
    new_setup = (
        "describe('setup', () => {\n"
        "  bench('array', () => {\n"
        "    let matcher = new ArrayMatcher<null>()\n"
        "    routes.forEach((route) => matcher.add(route, null))\n"
        "  })\n"
        "\n"
        "  bench('trie', () => {\n"
        "    let matcher = new TrieMatcher<null>()\n"
        "    routes.forEach((route) => matcher.add(route, null))\n"
        "  })\n"
        "})"
    )
    assert old_setup in c, f"old setup block not found in {f}"
    c = c.replace(old_setup, new_setup)

    # 4. Replace match describe block
    old_match = (
        "describe('match', () => {\n"
        "  for (let { name, matcher } of matchers) {\n"
        "    bench(name, () => {\n"
        "      urls.forEach((url) => matcher.match(url))\n"
        "    })\n"
        "  }\n"
        "})"
    )
    new_match = (
        "describe('match', () => {\n"
        "  let arrayMatcher = new ArrayMatcher<null>()\n"
        "  routes.forEach((route) => arrayMatcher.add(route, null))\n"
        "  bench('array', () => {\n"
        "    urls.forEach((url) => arrayMatcher.match(url))\n"
        "  })\n"
        "\n"
        "  let trieMatcher = new TrieMatcher<null>()\n"
        "  routes.forEach((route) => trieMatcher.add(route, null))\n"
        "  bench('trie', () => {\n"
        "    urls.forEach((url) => trieMatcher.match(url))\n"
        "  })\n"
        "})"
    )
    assert old_match in c, f"old match block not found in {f}"
    c = c.replace(old_match, new_match)

    with open(f, "w") as fh:
        fh.write(c)
    print(f"Fixed {f}")


fix_simple()
fix_pathological()
print("All fixes applied successfully")
PYEOF

# Idempotency check
grep -q "import { ArrayMatcher, TrieMatcher }" packages/route-pattern/bench/pathological.bench.ts
echo "Verified: patch applied successfully"
