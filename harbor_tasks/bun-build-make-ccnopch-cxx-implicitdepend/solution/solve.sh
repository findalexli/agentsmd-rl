#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'const codegenOrderOnly = codegen.cppAll' scripts/build/bun.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 << 'PYEOF'
from pathlib import Path

# ── Fix 1: scripts/build/bun.ts — depOutputs → implicitInputs for cc/no-PCH cxx ──
p = Path("scripts/build/bun.ts")
src = p.read_text()

# 1a. Update depOutputs comment
src = src.replace(
    'const depOutputs: string[] = []; // PCH order-only-deps on these',
    'const depOutputs: string[] = []; // implicit-dep signal for PCH/cc/no-PCH cxx',
)

# 1b. Replace the old comment block and depOrderOnly variable
src = src.replace(
    '  // All deps must be ready (headers extracted, libs built) before compile.\n'
    "  // ORDER-ONLY, not implicit: the compiler's .d depfile tracks ACTUAL header\n"
    '  // dependencies on subsequent builds. Order-only ensures first-build ordering;\n'
    "  // after that, touching libJavaScriptCore.a doesn't recompile every .c file\n"
    "  // (.c files don't include JSC headers — depfile knows this).\n"
    '  //\n'
    '  // PCH is different: it has IMPLICIT deps on depOutputs because root.h\n'
    '  // transitively includes WebKit headers, and the PCH encodes those. If\n'
    '  // WebKit headers change (lib rebuilt), PCH must invalidate. The depfile\n'
    "  // mechanism doesn't work for PCH-invalidation because the .cpp's depfile\n"
    '  // says "depends on root.h.pch", not on what root.h.pch was built from.\n'
    '  const depOrderOnly = [...depOutputs, ...codegen.cppAll];',

    '  // All deps must be ready (headers extracted, libs built) before compile.\n'
    '  //\n'
    "  // depOutputs are IMPLICIT inputs, not order-only. A locally-built dep's\n"
    '  // sub-build (e.g. WebKit) rewrites forwarding headers as an undeclared side\n'
    '  // effect of the edge whose declared outputs are only lib*.a. Depfiles record\n'
    '  // those headers, but ninja stats them BEFORE the sub-build runs — so with\n'
    '  // order-only, any compile that #includes a dep header lags one build behind\n'
    '  // a dep rebuild (observed: asan-config.c / uv-posix-*.c → wtf/Compiler.h).\n'
    '  // Implicit deps on the libs make "dep rebuilt" itself the invalidation\n'
    '  // signal. Cost is negligible: if the libs changed you\'re relinking anyway.\n'
    '  //\n'
    '  // codegen.cppAll stays order-only: those headers ARE declared ninja outputs\n'
    "  // with restat, so depfile tracking is exact and doesn't lag.\n"
    '  //\n'
    '  // PCH also has implicit deps on depOutputs (see above). When PCH is enabled,\n'
    '  // cxx inherits the dep transitively via its implicit dep on the PCH, so we\n'
    "  // don't add it again.\n"
    '  const codegenOrderOnly = codegen.cppAll;',
)

# 1c. Update PCH comment
src = src.replace(
    '      // Transitively: cxx waits for deps. No need for order-only here.',
    '      // Transitively: cxx waits for deps. No need to repeat them here.',
)

# 1d. Replace no-PCH else branch
src = src.replace(
    '    } else {\n'
    '      // No PCH (windows) — each cxx needs direct ordering on deps.\n'
    '      // Order-only: depfile tracks actual headers after first build.\n'
    '      opts.orderOnlyInputs = depOrderOnly;\n'
    '    }',
    '    } else {\n'
    '      // No PCH (windows) — each cxx needs the dep signal directly.\n'
    '      opts.implicitInputs = depOutputs;\n'
    '      opts.orderOnlyInputs = codegenOrderOnly;\n'
    '    }',
)

# 1e. Update cc compile comment
src = src.replace(
    '  // Compile all .c files. No PCH. Order-only on deps for first-build ordering.',
    '  // Compile all .c files. No PCH — dep signal applied directly.',
)

# 1f. Replace cc call in compileC
src = src.replace(
    '    const obj = cc(n, cfg, src, { flags: cFlagsFull, orderOnlyInputs: depOrderOnly });',
    '    const obj = cc(n, cfg, src, {\n'
    '      flags: cFlagsFull,\n'
    '      implicitInputs: depOutputs,\n'
    '      orderOnlyInputs: codegenOrderOnly,\n'
    '    });',
)

p.write_text(src)
print("Fixed scripts/build/bun.ts")

# ── Fix 2: scripts/build/compile.ts — update CompileOpts docs ──
p = Path("scripts/build/compile.ts")
src = p.read_text()

# 2a. Update implicitInputs JSDoc
src = src.replace(
    '   * Extra implicit deps. Use for generated headers this specific .cpp needs.\n'
    '   * E.g. ErrorCode.cpp depends on ErrorCode+List.h.',
    '   * Extra implicit deps. Use for generated headers this specific .cpp needs\n'
    '   * (e.g. ErrorCode.cpp depends on ErrorCode+List.h), and for dep outputs\n'
    "   * (lib*.a) — local sub-builds rewrite forwarding headers as undeclared\n"
    '   * side effects, so the lib is the invalidation signal; order-only would\n'
    '   * lag one build behind.',
)

# 2b. Update orderOnlyInputs JSDoc
src = src.replace(
    "   * subsequent builds — order-only is for \"dep libs/headers must be\n"
    "   * extracted before first compile attempts to #include them\".\n"
    '   *\n'
    "   * Prefer this over implicitInputs for dep outputs: if you touch\n"
    "   * libJavaScriptCore.a, you don't want every .c file to recompile\n"
    "   * (.c files don't include JSC headers). The depfile knows better.",
    '   * subsequent builds — order-only is for "header must be generated\n'
    '   * before first compile attempts to #include it".\n'
    '   *\n'
    '   * Use for codegen headers (declared ninja outputs with restat, so\n'
    '   * depfile tracking is exact). Dep outputs (lib*.a) go in\n'
    '   * implicitInputs instead — see above.',
)

p.write_text(src)
print("Fixed scripts/build/compile.ts")

# ── Fix 3: scripts/build/CLAUDE.md — update Ninja primer and Gotchas ──
p = Path("scripts/build/CLAUDE.md")
src = p.read_text()

# 3a. Update example build edge
src = src.replace(
    'build obj/src/foo.c.o: cc ../../src/foo.c | codegen/generated.h || ../../vendor/zstd/.ref',
    'build obj/src/foo.c.o: cc ../../src/foo.c | deps/zstd/libzstd.a || codegen/generated.h',
)

# 3b. Update implicit inputs definition
src = src.replace(
    "- **implicit inputs** (`| foo.h`) — tracked for rebuild but not in `$in`. Use for files the command reads that aren't on its command line (generated headers, PCH)",
    '- **implicit inputs** (`| foo`) — tracked for rebuild but not in `$in`. Use for the PCH, dep lib outputs (invalidation signal for their headers), or a per-file generated header this source is known to read',
)

# 3c. Update order-only definition
src = src.replace(
    '- **order-only inputs** (`|| stamp`) — must exist before this edge runs, but mtime doesn\'t trigger rebuild. Use for "X must be fetched/generated first, but the compiler\'s `.d` depfile will track which files I actually read"',
    '- **order-only inputs** (`|| stamp`) — must exist before this edge runs, but mtime doesn\'t trigger rebuild. Use for bulk codegen headers: "must be generated first, but the compiler\'s `.d` depfile will track which ones I actually read"',
)

# 3d. Update depfile explanation
src = src.replace(
    "**`depfile`** — compiler writes `foo.o.d` listing every `#include`d header. Ninja reads it on the next build to know which headers this `.o` depends on. This is why cxx uses order-only for dep outputs: the depfile gives exact per-file header deps on build 2+; order-only just ensures headers exist for build 1.",
    "**`depfile`** — compiler writes `foo.o.d` listing every `#include`d header. Ninja reads it on the next build to know which headers this `.o` depends on. Codegen headers are order-only for this reason: they're declared outputs with restat, the depfile gives exact per-file header deps on build 2+, and order-only just ensures they exist for build 1. Dep outputs (`lib*.a`) are a different story — PCH, cc, and no-PCH cxx use them as _implicit_ deps, because local sub-builds (e.g. WebKit) rewrite forwarding headers as undeclared side effects and order-only would lag one build behind (see Gotchas).",
)

# 3e. Replace Gotchas PCH + cxx paragraphs with unified paragraph
src = src.replace(
    "**PCH needs implicit dep on `depOutputs`**, not order-only. Local WebKit regenerates headers mid-build; order-only would let ninja think PCH is fresh while headers change under it → \"file modified since PCH was built\".\n"
    "\n"
    "**cxx needs order-only dep on `depOutputs`**, not implicit. Depfile tracks actual header deps. Implicit would recompile every `.c` when `libJavaScriptCore.a` changes — but `.c` files don't include JSC headers.",
    "**PCH, cc, and no-PCH cxx need implicit dep on `depOutputs`**, not order-only. Local WebKit's sub-build rewrites forwarding headers as an undeclared side effect (only `lib*.a` are declared outputs). Depfiles record those headers, but ninja stats them before the sub-build runs — order-only lags one build. The lib itself is the invalidation signal. Codegen headers stay order-only: they're declared outputs with restat, so depfile tracking is exact.",
)

p.write_text(src)
print("Fixed scripts/build/CLAUDE.md")

print("\nAll patches applied successfully.")
PYEOF
