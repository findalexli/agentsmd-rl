import { fileURLToPath } from 'node:url'
import { dirname, resolve as pathResolve } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))

export async function resolve(specifier, context, nextResolve) {
  if (specifier === 'vitest') {
    return {
      url: 'file://' + pathResolve(__dirname, 'vitest-stub.mjs'),
      shortCircuit: true,
      format: 'module',
    }
  }
  if (specifier === '@remix-run/route-pattern') {
    return {
      url: 'file://' + pathResolve(__dirname, 'route-pattern-stub.mjs'),
      shortCircuit: true,
      format: 'module',
    }
  }
  return nextResolve(specifier, context)
}
