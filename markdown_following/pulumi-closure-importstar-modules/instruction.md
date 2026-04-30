# Fix closure serialization for `__importStar`-wrapped modules

The `@pulumi/pulumi` Node.js SDK exposes `runtime.serializeFunction(fn, ...)`
which converts a JavaScript closure into a self-contained string of source
code that recreates the function. When the closure captures a Node module
(such as `require("crypto")`), the serializer is supposed to detect the
module and emit a single `require("<name>")` reference instead of trying
to inline every property of the module.

## The bug

When TypeScript compiles `import * as foo from "foo"` with
`module: "nodenext"`, it does **not** hand the original module to user
code. Instead it wraps it via TypeScript's `__importStar` helper, which
produces a brand-new plain object whose `default` property points to the
underlying module and whose other own properties are getter-defined
re-exports of the module's properties:

```js
function __importStar(mod) {
    if (mod && mod.__esModule) return mod;
    const result = {};
    if (mod != null) {
        for (const k of Object.getOwnPropertyNames(mod)) {
            if (k !== "default") {
                Object.defineProperty(result, k, {
                    enumerable: true,
                    get: () => mod[k],
                });
            }
        }
    }
    Object.defineProperty(result, "default", { enumerable: true, value: mod });
    return result;
}
```

Because this wrapper is a freshly allocated object — distinct from the
original module — the serializer's "is this a known module?" lookup misses
it and falls back to walking the wrapper's own properties one by one.

You can reproduce the broken behaviour today by running:

```js
const sdk = require("/workspace/pulumi/sdk/nodejs/bin");

function __importStar(mod) { /* identical to the helper above */ }
const wrapped = __importStar(require("crypto"));
const func = () => wrapped;

sdk.runtime.serializeFunction(func, {}).then(sf => console.log(sf.text));
```

On the unfixed code the printed output is several kilobytes long: it
expands `crypto` into many `Object.defineProperty(__wrapped, "<name>",
{ ... get: __fN });` lines plus synthetic `__fN` factory functions, one
per property of `crypto`. There is **no** `require("crypto")` reference
in the output at all.

## What "fixed" must look like

For the same reproduction script the serialised output must:

- Contain the substring `require("crypto")`.
- **Not** contain `Object.defineProperty(__wrapped` (or any other
  property-by-property expansion of the wrapper).
- Be roughly the same size as the output you get when you capture
  `require("crypto")` directly without the `__importStar` wrapper —
  i.e. a few hundred bytes, not many kilobytes.

The same must hold when the wrapped builtin is `os`: the output must
contain `require("os")` and no `Object.defineProperty(__wrapped` lines.
For `path` the output must contain one of `require("path")`,
`require("path/posix")`, or `require("path/win32")` (Node may resolve to
the platform-specific alias) and likewise no `Object.defineProperty`
expansion of the wrapper.

## What "fixed" must NOT regress

A naïve check ("any object with a `default` property is an `__importStar`
result") would be too aggressive and is not acceptable. Specifically, the
following input must continue to serialise as a plain object literal —
**not** be unwrapped:

```js
const obj = { default: require("crypto") };
const func = () => obj;
```

The expected output must contain the substring `{default: require("crypto")}`
verbatim (the serializer's existing object-literal formatting), because
`obj` has no re-exported keys and therefore cannot have come from
`__importStar`.

Likewise, capturing `require("crypto")` directly (no wrapper) must still
serialise to a single `const ... = require("crypto")` declaration, with no
`Object.defineProperty` calls.

## How `__importStar` results can be recognised

The shape of a value produced by `__importStar` is well-defined:

1. It is a non-null object whose prototype is `Object.prototype` (the
   helper builds it with `var result = {}`).
2. It has a `default` own property whose value is the underlying module.
3. Every other own property name (besides `default` and the optional
   `__esModule` marker) is also an own or inherited property of the
   underlying module — these are the getter-defined re-exports.
4. There is at least one such re-exported property; an object with only
   `default` and nothing else cannot be distinguished from a hand-rolled
   `{ default: ... }` and must therefore not be treated as `__importStar`.

When all four conditions hold, the captured value should be treated as
an alias for the wrapped module: the serializer's existing module-name
lookup should be retried against the underlying module (i.e. the value
of `default`), and if a name is found the serializer should emit a
`require("<name>")` reference for the wrapper just as it would for the
underlying module.

## Building and testing

The compiled SDK that the tests load from lives in
`/workspace/pulumi/sdk/nodejs/bin`. After editing TypeScript sources
under `/workspace/pulumi/sdk/nodejs/`, rebuild with:

```sh
cd /workspace/pulumi/sdk/nodejs
yarn run tsc
mkdir -p bin/proto && cp -R proto/. bin/proto/
cp package.json bin/package.json
mkdir -p bin/vendor && cp -R vendor/. bin/vendor/
```

(`yarn run tsc` is the one that actually picks up your code changes; the
other copies are non-TypeScript artefacts that the SDK's `runtime`
namespace expects to find under `bin/` and that are normally produced by
the repo's `make build_package` target.)

The existing closure-serializer unit tests in
`sdk/nodejs/tests/runtime/closure.spec.ts` must continue to pass, and
`yarn run tsc --noEmit` from `sdk/nodejs/` must compile cleanly.

## Repo conventions

The repository's `CLAUDE.md`, `AGENTS.md`, and `sdk/nodejs/AGENTS.md`
apply. Of particular relevance to this change:

- A changelog entry is required. Add a new YAML file under
  `changelog/pending/` with `type: fix`, `scope: sdk/nodejs`, and a
  one-line description of the change. The repo's existing files in that
  directory show the expected schema.
- Copyright headers on any new source files use the current year.
- Do not edit generated files by hand.

## Code style requirements

After your changes, the SDK's TypeScript must continue to compile under
`yarn run tsc` from `sdk/nodejs/` without errors.
