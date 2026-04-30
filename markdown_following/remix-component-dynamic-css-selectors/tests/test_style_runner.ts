// Test runner for the remix-run/remix dynamic CSS selectors fix.
// Tests the processStyle function for handling of undefined nested selectors and at-rules.

import { processStyle } from '/workspace/remix/packages/component/src/lib/style/lib/style.ts'

interface TestResult {
  name: string
  passed: boolean
  details: string
}

const results: TestResult[] = []

function record(name: string, fn: () => boolean, detail?: string): void {
  try {
    const passed = fn()
    results.push({ name, passed, details: detail || (passed ? 'ok' : 'assertion failed') })
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    results.push({ name, passed: false, details: msg })
  }
}

// Test 0 (p2p): Normal style processing works on basic properties
record('normal_style_processing', () => {
  const cache = new Map<string, { selector: string; css: string }>()
  const result = processStyle(
    { color: 'red', fontSize: 16 },
    cache,
  )
  return result.selector !== '' && result.css.includes('color: red') && result.css.includes('font-size: 16px')
}, 'Basic style processing should work on the base commit')

// Test 1: processStyle should not throw when a nested selector value is undefined
record('undefined_nested_selector_no_throw', () => {
  const cache = new Map<string, { selector: string; css: string }>()
  const result = processStyle(
    {
      color: 'red',
      '&:hover': undefined,
    },
    cache,
  )
  return result.selector !== '' && result.css.includes('color: red')
}, 'Nested selector with undefined value should be silently skipped, CSS should contain base declarations')

// Test 2: processStyle should not throw when an at-rule value is undefined
record('undefined_at_rule_no_throw', () => {
  const cache = new Map<string, { selector: string; css: string }>()
  const result = processStyle(
    {
      color: 'blue',
      '@media (min-width: 600px)': undefined,
    },
    cache,
  )
  return result.selector !== '' && result.css.includes('color: blue')
}, 'At-rule with undefined value should be silently skipped, CSS should contain base declarations')

// Test 3: Conditional nested selector - undefined removes the rule
record('conditional_nested_selector_skip', () => {
  const cache = new Map<string, { selector: string; css: string }>()
  const result = processStyle(
    {
      '& span': { color: 'rgb(0, 0, 255)' },
      '& span.special': undefined,
    },
    cache,
  )
  // The undefined selector should be absent from output
  return result.css.includes('& span') && !result.css.includes('span.special')
}, 'Undefined nested selector should be absent from CSS output, while defined selectors remain')

// Test 4: Conditional at-rule - undefined removes the rule
record('conditional_at_rule_skip', () => {
  const cache = new Map<string, { selector: string; css: string }>()
  const result = processStyle(
    {
      color: 'green',
      '@media (max-width: 768px)': undefined,
      '@media (min-width: 1024px)': {
        color: 'purple',
      },
    },
    cache,
  )
  return (
    !result.css.includes('max-width: 768px') &&
    result.css.includes('min-width: 1024px') &&
    result.css.includes('color: purple')
  )
}, 'Undefined at-rule should be absent from CSS, while defined at-rules remain')

// Test 5: Mixed undefined and defined nested selectors produce correct output
record('mixed_undefined_defined_nested', () => {
  const cache = new Map<string, { selector: string; css: string }>()
  const result = processStyle(
    {
      '&:hover': { color: 'yellow' },
      '&:focus': undefined,
      '&:active': { color: 'orange' },
      backgroundColor: 'black',
    },
    cache,
  )
  return (
    result.css.includes('&:hover') &&
    result.css.includes('color: yellow') &&
    result.css.includes('&:active') &&
    result.css.includes('color: orange') &&
    !result.css.includes('&:focus') &&
    result.css.includes('background-color: black')
  )
}, 'CSS output should contain only defined nested selectors and base declarations')

// Test 6: Arrays should not be treated as record objects
record('array_not_treated_as_record', () => {
  const cache = new Map<string, { selector: string; css: string }>()
  const result = processStyle(
    {
      color: 'red',
      '& span': ['not', 'a', 'record'] as unknown as Record<string, unknown>,
    },
    cache,
  )
  // Arrays should be skipped (not iterated as key-value pairs)
  return result.css.includes('color: red') && !result.css.includes('& span')
}, 'Array values for nested selectors should be skipped, not iterated as key-value pairs')

// Test 7: Null values for nested selectors are also skipped
record('null_nested_selector_skip', () => {
  const cache = new Map<string, { selector: string; css: string }>()
  const result = processStyle(
    {
      color: 'red',
      '&:hover': null as unknown as Record<string, unknown>,
    },
    cache,
  )
  return result.css.includes('color: red') && !result.css.includes('&:hover')
}, 'Null values for nested selectors should be silently skipped')

// Print results as JSON to stdout
console.log(JSON.stringify(results))
