#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if [ -f packages/route-pattern/src/lib/route-pattern/AGENTS.md ]; then
    if grep -q 'Organize by feature' packages/route-pattern/src/lib/route-pattern/AGENTS.md 2>/dev/null; then
        echo "Patch already applied."
        exit 0
    fi
fi

python3 << 'PYTHON_SCRIPT'
import os
import re

# Read the original part-pattern.ts
with open('packages/route-pattern/src/lib/route-pattern/part-pattern.ts', 'r') as f:
    pp_original = f.read()

# Extract type definitions (everything before "export class PartPattern")
types_section = re.search(r'^(.*?)(?=^export class PartPattern)', pp_original, re.MULTILINE | re.DOTALL)
types_content = types_section.group(1) if types_section else ''

# Add new imports if not present
if 'HrefError' not in types_content:
    types_content = types_content.replace(
        "import { ParseError } from './parse.ts'\n",
        "import { ParseError } from './parse.ts'\nimport { HrefError, type HrefParams } from './href.ts'\nimport type { RoutePattern } from '../route-pattern.ts'\n")

# Build new part-pattern.ts content completely
# We know the structure from the original file
new_pp = types_content + '''export class PartPattern {
  readonly tokens: Array<PartPatternToken>
  readonly optionals: Map<number, number>
  readonly type: 'hostname' | 'pathname'
  readonly ignoreCase: boolean

  // todo: params cache
  #regexp: RegExp | undefined

  constructor(
    args: {
      tokens: Array<PartPatternToken>
      optionals: Map<number, number>
    },
    options: { type: 'hostname' | 'pathname'; ignoreCase: boolean },
  ) {
    this.tokens = args.tokens
    this.optionals = args.optionals
    this.type = options.type
    this.ignoreCase = options.ignoreCase
  }

  get params(): Array<Extract<PartPatternToken, { type: ':' | '*' }>> {
    let result: Array<Extract<PartPatternToken, { type: ':' | '*' }>> = []
    for (let token of this.tokens) {
      if (token.type === ':' || token.type === '*') {
        result.push(token)
      }
    }
    return result
  }

  get separator(): '.' | '/' {
    return separatorForType(this.type)
  }

  static parse(
    source: string,
    options: { span?: Span; type: 'hostname' | 'pathname'; ignoreCase: boolean },
  ): PartPattern {
    let span = options.span ?? [0, source.length]
    let separator = separatorForType(options.type)

    let tokens: Array<PartPatternToken> = []
    let optionals: Map<number, number> = new Map()

    let appendText = (text: string) => {
      let currentToken = tokens.at(-1)
      if (currentToken?.type === 'text') {
        currentToken.text += text
      } else {
        tokens.push({ type: 'text', text })
      }
    }

    let i = span[0]
    let optionalStack: Array<number> = []
    while (i < span[1]) {
      let char = source[i]

      // optional begin
      if (char === '(') {
        optionalStack.push(tokens.length)
        tokens.push({ type: char })
        i += 1
        continue
      }

      // optional end
      if (char === ')') {
        let begin = optionalStack.pop()
        if (begin === undefined) {
          throw new ParseError('unmatched )', source, i)
        }
        optionals.set(begin, tokens.length)
        tokens.push({ type: char })
        i += 1
        continue
      }

      // variable
      if (char === ':') {
        i += 1
        let name = IDENTIFIER_RE.exec(source.slice(i, span[1]))?.[0]
        if (!name) {
          throw new ParseError('missing variable name', source, i - 1)
        }
        tokens.push({ type: ':', name })
        i += name.length
        continue
      }

      // wildcard
      if (char === '*') {
        i += 1
        let name = IDENTIFIER_RE.exec(source.slice(i, span[1]))?.[0]
        tokens.push({ type: '*', name: name ?? '*' })
        i += name?.length ?? 0
        continue
      }

      if (separator && char === separator) {
        tokens.push({ type: 'separator' })
        i += 1
        continue
      }

      // escaped char
      if (char === '\\\\') {
        if (i + 1 === span[1]) {
          throw new ParseError('dangling escape', source, i)
        }
        let text = source.slice(i, i + 2)
        appendText(text)
        i += text.length
        continue
      }

      // text
      appendText(char)
      i += 1
    }
    if (optionalStack.length > 0) {
      throw new ParseError('unmatched (', source, optionalStack.at(-1)!)
    }

    return new PartPattern(
      { tokens, optionals },
      { type: options.type, ignoreCase: options.ignoreCase },
    )
  }

  get source(): string {
    let result = ''
    for (let token of this.tokens) {
      if (token.type === '(' || token.type === ')') {
        result += token.type
        continue
      }

      if (token.type === 'text') {
        result += token.text
        continue
      }

      if (token.type === ':' || token.type === '*') {
        let name = token.name === '*' ? '' : token.name
        result += `${token.type}${name}`
        continue
      }

      if (token.type === 'separator') {
        result += this.separator
        continue
      }

      unreachable(token.type)
    }

    return result
  }

  /**
   * Generate a partial href from a part pattern and params.
   *
   * @param pattern The route pattern containing the part pattern.
   * @param params The parameters to substitute into the pattern.
   * @returns The partial href for the given params
   */
  href(pattern: RoutePattern, params: HrefParams): string {
    let missingParams: Array<string> = []

    let stack: Array<{ begin?: number; href: string }> = [{ href: '' }]
    let i = 0
    while (i < this.tokens.length) {
      let token = this.tokens[i]
      if (token.type === 'text') {
        stack[stack.length - 1].href += token.text
        i += 1
        continue
      }
      if (token.type === 'separator') {
        stack[stack.length - 1].href += this.separator
        i += 1
        continue
      }
      if (token.type === '(') {
        stack.push({ begin: i, href: '' })
        i += 1
        continue
      }
      if (token.type === ')') {
        let frame = stack.pop()!
        stack[stack.length - 1].href += frame.href
        i += 1
        continue
      }
      if (token.type === ':' || token.type === '*') {
        let value = params[token.name]
        if (value === undefined) {
          if (stack.length <= 1) {
            if (token.name === '*') {
              throw new HrefError({
                type: 'nameless-wildcard',
                pattern,
              })
            }
            missingParams.push(token.name)
          }
          let frame = stack.pop()!
          i = this.optionals.get(frame.begin!)! + 1
          continue
        }
        stack[stack.length - 1].href += typeof value === 'string' ? value : String(value)
        i += 1
        continue
      }
      unreachable(token.type)
    }
    if (missingParams.length > 0) {
      throw new HrefError({
        type: 'missing-params',
        pattern,
        partPattern: this,
        missingParams,
        params,
      })
    }
    if (stack.length !== 1) unreachable()
    return stack[0].href
  }

  match(part: string): PartPatternMatch | null {
    if (this.#regexp === undefined) {
      this.#regexp = this.#toRegExp()
    }
    let reMatch = this.#regexp.exec(part)
    if (reMatch === null) return null
    let match: PartPatternMatch = []
    let params = this.params
    for (let i = 0; i < params.length; i++) {
      let param = params[i]
      let captureIndex = i + 1
      let span = reMatch.indices?.[captureIndex]
      if (span === undefined) continue
      match.push({
        type: param.type,
        name: param.name,
        begin: span[0],
        end: span[1],
        value: reMatch[captureIndex],
      })
    }
    return match
  }

  #toRegExp(): RegExp {
    let result = ''
    for (let token of this.tokens) {
      if (token.type === 'text') {
        result += RE.escape(token.text)
        continue
      }

      if (token.type === ':') {
        result += this.separator ? `([^${this.separator}]+?)` : `(.+?)`
        continue
      }

      if (token.type === '*') {
        result += `(.*)`
        continue
      }

      if (token.type === '(') {
        result += '(?:'
        continue
      }

      if (token.type === ')') {
        result += ')?'
        continue
      }

      if (token.type === 'separator') {
        result += RE.escape(this.separator ?? '')
        continue
      }

      unreachable(token.type)
    }
    return new RegExp(`^${result}$`, this.ignoreCase ? 'di' : 'd')
  }
}

function separatorForType(type: 'hostname' | 'pathname'): '.' | '/' {
  if (type === 'hostname') return '.'
  return '/'
}
'''

with open('packages/route-pattern/src/lib/route-pattern/part-pattern.ts', 'w') as f:
    f.write(new_pp)

print("part-pattern.ts rebuilt successfully")
PYTHON_SCRIPT

# Continue with other transformations

# 1. Fix index.ts
sed -i "s/export { type Args as HrefArgs/export { type HrefArgs/" packages/route-pattern/src/index.ts

# 2. Fix route-pattern.test.ts
python3 << 'EOF'
with open('packages/route-pattern/src/lib/route-pattern.test.ts', 'r') as f:
    c = f.read()
c = c.replace('import * as Href from \'./route-pattern/href.ts\'\n', '')
c = c.replace('import * as Source from \'./route-pattern/source.ts\'\n', '')
if 'import { HrefError }' not in c:
    c = c.replace("import { RoutePattern } from './route-pattern.ts'\n",
                  "import { RoutePattern } from './route-pattern.ts'\nimport { HrefError } from './route-pattern/href.ts'\n")
c = c.replace('Href.HrefError', 'HrefError')
c = c.replace('Source.part(pattern.ast.hostname)', 'pattern.ast.hostname?.source ?? null')
c = c.replace('Source.part(pattern.ast.pathname)', 'pattern.ast.pathname.source')
c = c.replace('pattern.ast.port ?? null', 'pattern.ast.port')
c = c.replace('hostname: expected.hostname,', 'hostname: expected.hostname ?? null,')
with open('packages/route-pattern/src/lib/route-pattern.test.ts', 'w') as f:
    f.write(c)
EOF

# 3. Fix route-pattern.ts
python3 << 'EOF'
with open('packages/route-pattern/src/lib/route-pattern.ts', 'r') as f:
    c = f.read()
c = c.replace("import * as Search from './route-pattern/search.ts'\n", '')
c = c.replace('import type { Join as JoinResult, Params }', 'import type { Join, Params }')
c = c.replace("import * as Parse from './route-pattern/parse.ts'\n", '')
c = c.replace("import * as Source from './route-pattern/source.ts'\n", '')
c = c.replace("import * as Href from './route-pattern/href.ts'\n", '')
c = c.replace("import * as Join from './route-pattern/join.ts'\n", '')

new_imports = """import { parseHostname, parseProtocol, parseSearch } from './route-pattern/parse.ts'
import { serializeSearch } from './route-pattern/serialize.ts'
import { joinPathname, joinSearch } from './route-pattern/join.ts'
import { HrefError, hrefSearch, type HrefArgs } from './route-pattern/href.ts'
import { matchSearch } from './route-pattern/match.ts'
"""
if 'parseHostname' not in c:
    c = c.replace("import { split } from './route-pattern/split.ts'\n",
                  "import { split } from './route-pattern/split.ts'\n" + new_imports)

c = c.replace('search: Search.Constraints', 'search: Map<string, Set<string> | null>')
c = c.replace('Parse.protocol', 'parseProtocol')
c = c.replace('Parse.hostname', 'parseHostname')
c = c.replace('Parse.search', 'parseSearch')
c = c.replace("if (this.ast.hostname === null) return ''\n    return Source.part(this.ast.hostname)", 
              'return this.ast.hostname?.source ?? \'\'')
c = c.replace('Source.part(this.ast.pathname)', 'this.ast.pathname.source')
c = c.replace('Source.search(this.ast.search) ?? \'\'', 'serializeSearch(this.ast.search) ?? \'\'')
c = c.replace('JoinResult', 'Join')
c = c.replace('Join.pathname', 'joinPathname')
c = c.replace('Join.search', 'joinSearch')
c = c.replace('Href.Args', 'HrefArgs')
c = c.replace('Href.HrefError', 'HrefError')
c = c.replace('Href.part(this, this.ast.hostname, params)', 'this.ast.hostname.href(this, params)')
c = c.replace('Href.part(this, this.ast.pathname, params)', 'this.ast.pathname.href(this, params)')
c = c.replace('Href.search(this, searchParams)', 'hrefSearch(this, searchParams)')
c = c.replace('Search.test', 'matchSearch')
with open('packages/route-pattern/src/lib/route-pattern.ts', 'w') as f:
    f.write(c)
EOF

# 4. Create AGENTS.md
cat > packages/route-pattern/src/lib/route-pattern/AGENTS.md << 'AGENTSEOF'
# Route Pattern Helpers

This directory contains helpers for [`route-pattern.ts`](../route-pattern.ts).

## Organization

- **[`part-pattern.ts`](./part-pattern.ts)**: Logic that applies to any `PartPattern` (i.e. hostname _and_ pathname)
- **Other files**: Organize by feature (not by pattern part)
  - [`href.ts`](./href.ts): Href generation
  - [`join.ts`](./join.ts): Pattern joining
  - [`match.ts`](./match.ts): URL matching
  - [`parse.ts`](./parse.ts): Parsing patterns
  - [`serialize.ts`](./serialize.ts): Serializing to strings
  - [`split.ts`](./split.ts): Splitting source strings
AGENTSEOF

# 5. Fix join.ts
sed -i 's/export function pathname(/export function joinPathname(/' packages/route-pattern/src/lib/route-pattern/join.ts
sed -i 's/export function search(/export function joinSearch(/' packages/route-pattern/src/lib/route-pattern/join.ts

# 6. Create match.ts from search.ts
python3 << 'EOF'
with open('packages/route-pattern/src/lib/route-pattern/search.ts', 'r') as f:
    c = f.read()
c = c.replace('export type Constraints = Map<string, Set<string> | null>', 
              'import type { RoutePattern } from \'../route-pattern.ts\'')
c = c.replace('export function test(', 'export function matchSearch(')
c = c.replace('constraints: Constraints,', 'constraints: RoutePattern["ast"]["search"],')
with open('packages/route-pattern/src/lib/route-pattern/match.ts', 'w') as f:
    f.write(c)
EOF

# 7. Fix parse.ts
sed -i 's/export function protocol(/export function parseProtocol(/' packages/route-pattern/src/lib/route-pattern/parse.ts
sed -i 's/export function hostname(/export function parseHostname(/' packages/route-pattern/src/lib/route-pattern/parse.ts
sed -i 's/export function search(/export function parseSearch(/' packages/route-pattern/src/lib/route-pattern/parse.ts

# 8. Fix part-pattern.test.ts
sed -i "/import \* as Source from/d" packages/route-pattern/src/lib/route-pattern/part-pattern.test.ts
sed -i 's/Source.part(partPattern)/partPattern.source/g' packages/route-pattern/src/lib/route-pattern/part-pattern.test.ts

# 9. Fix trie-matcher.ts
python3 << 'EOF'
with open('packages/route-pattern/src/lib/trie-matcher.ts', 'r') as f:
    c = f.read()
c = c.replace("import * as Search from './route-pattern/search.ts'\n", '')
if 'matchSearch' not in c:
    c = c.replace("import * as Specificity from './specificity.ts'\n",
                  "import * as Specificity from './specificity.ts'\nimport { matchSearch } from './route-pattern/match.ts'\n")
c = c.replace('Search.test', 'matchSearch')
with open('packages/route-pattern/src/lib/trie-matcher.ts', 'w') as f:
    f.write(c)
EOF

# 10. Rebuild href.ts with TypeScript template literals
cat > packages/route-pattern/src/lib/route-pattern/href.ts << 'HREFEOF'
import { unreachable } from '../unreachable.ts'
import type { RoutePattern } from '../route-pattern.ts'
import type { OptionalParams, RequiredParams } from '../types/params.ts'
import type { PartPattern } from './part-pattern.ts'

type HrefParamValue = string | number
export type HrefParams = Record<string, HrefParamValue>

// prettier-ignore
export type HrefArgs<source extends string> =
  [RequiredParams<source>] extends [never] ?
    [] | [null | undefined | Record<string, any>] | [null | undefined | Record<string, any>, HrefSearchParams] :
    [HrefParamsArg<source>, HrefSearchParams] | [HrefParamsArg<source>]

// prettier-ignore
type HrefParamsArg<source extends string> =
  & Record<RequiredParams<source>, HrefParamValue>
  & Partial<Record<OptionalParams<source>, HrefParamValue | null | undefined>>
  & Record<string, unknown>

export type HrefSearchParams = Record<
  string,
  string | number | null | undefined | Array<string | number | null | undefined>
>

/**
 * Generate a search query string from a pattern and params.
 *
 * @param pattern the route pattern containing search constraints
 * @param searchParams the search params to include in the href
 * @returns the query string (without leading `?`), or undefined if empty
 */
export function hrefSearch(pattern: RoutePattern, searchParams: HrefSearchParams): string | undefined {
  let constraints = pattern.ast.search
  if (constraints.size === 0 && Object.keys(searchParams).length === 0) {
    return undefined
  }

  let urlSearchParams = new URLSearchParams()

  for (let [key, value] of Object.entries(searchParams)) {
    if (Array.isArray(value)) {
      for (let v of value) {
        if (v != null) {
          urlSearchParams.append(key, String(v))
        }
      }
    } else if (value != null) {
      urlSearchParams.append(key, String(value))
    }
  }

  let missingParams: Array<string> = []
  for (let [key, constraint] of constraints) {
    if (constraint === null) {
      if (key in searchParams) continue
      urlSearchParams.append(key, '')
    } else if (constraint.size === 0) {
      if (key in searchParams) continue
      missingParams.push(key)
    } else {
      for (let value of constraint) {
        if (urlSearchParams.getAll(key).includes(value)) continue
        urlSearchParams.append(key, value)
      }
    }
  }

  if (missingParams.length > 0) {
    throw new HrefError({
      type: 'missing-search-params',
      pattern,
      missingParams,
      searchParams: searchParams,
    })
  }

  let result = urlSearchParams.toString()
  return result || undefined
}

type HrefErrorDetails =
  | { type: 'missing-hostname'; pattern: RoutePattern }
  | { type: 'missing-params'; pattern: RoutePattern; partPattern: PartPattern; missingParams: Array<string>; params: HrefParams }
  | { type: 'missing-search-params'; pattern: RoutePattern; missingParams: Array<string>; searchParams: HrefSearchParams }
  | { type: 'nameless-wildcard'; pattern: RoutePattern }

export class HrefError extends Error {
  details: HrefErrorDetails
  constructor(details: HrefErrorDetails) {
    super(formatErrorMessage(details))
    this.details = details
    this.name = 'HrefError'
  }
}

function formatErrorMessage(details: HrefErrorDetails): string {
  switch (details.type) {
    case 'missing-hostname':
      return 'Cannot generate href for ' + details.pattern.source + ': missing hostname'
    case 'missing-params':
      return 'Cannot generate href for ' + details.pattern.source + ': missing required params ' + details.missingParams.join(', ')
    case 'missing-search-params':
      return 'Cannot generate href for ' + details.pattern.source + ': missing required search params ' + details.missingParams.join(', ')
    case 'nameless-wildcard':
      return 'Cannot generate href for ' + details.pattern.source + ': nameless wildcard not allowed'
    default:
      unreachable(details)
  }
}
HREFEOF

# 11. Create serialize.ts
cat > packages/route-pattern/src/lib/route-pattern/serialize.ts << 'SERIALEOF'
import type { RoutePattern } from '../route-pattern.ts'

/**
 * Serialize search constraints to a query string.
 *
 * @param constraints the search constraints to convert
 * @returns the query string (without leading `?`), or undefined if empty
 */
export function serializeSearch(constraints: RoutePattern['ast']['search']): string | undefined {
  if (constraints.size === 0) {
    return undefined
  }

  let parts: Array<string> = []

  for (let [key, constraint] of constraints) {
    if (constraint === null) {
      parts.push(encodeURIComponent(key))
    } else if (constraint.size === 0) {
      parts.push(`${encodeURIComponent(key)}=`)
    } else {
      for (let value of constraint) {
        parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
      }
    }
  }

  let result = parts.join('&')
  return result || undefined
}
SERIALEOF

# 12. Delete source.ts and search.ts
rm -f packages/route-pattern/src/lib/route-pattern/source.ts
rm -f packages/route-pattern/src/lib/route-pattern/search.ts

echo "Patch applied successfully."
